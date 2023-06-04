from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
#
import modules.chat_manager

'''
модуль реализует выбор языка, выводя пользователю список кнопок.
При выборе кнопки, сообщение меняется, а в БД юзера записывается значение выбранного языка (пока не реализовано)
'''

class LangSelector():
    def __init__(self, parent, limit: int) -> None:
        self.parent = parent        
        self.parent.dp.register_callback_query_handler(self.handle)
        self.limit = int(limit) # сколько кнопок на одной странице
        self.pages = None

    async def create_buttons(self, message, page=0, first_launch=True, edit_message_id=None) -> None:
        # переменная, отвечающая за текущую страницу
        current_page = page
        if self.pages == None:
            await self.get_pages_count()        
        # создаём список кнопок для выбора языка
        offset = current_page * self.limit
        result = await self.parent.db_manager.get_data(query=f"SELECT name, iso FROM langs LIMIT {self.limit} OFFSET {offset}")
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for r in result:
                callback_data = f"{r[0]}"
                button = InlineKeyboardButton(text=r[0], callback_data=callback_data)
                keyboard.add(button)

            # добавляем кнопки для переключения страниц
            buttons = []
            # мы записываем id предыдущей и последующей страницы в бинд кнопок
            buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page {current_page-1}"))
            current_page_button_text = f"[{current_page + 1}/{self.pages}]"
            buttons.append(InlineKeyboardButton(text=current_page_button_text, callback_data="current_page"))
            buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page {current_page+1}"))
            # создаём столько рядов в нихнем строке, сколько кнопок в списке buttons
            keyboard.row(*buttons)

            # отправляем юзеру меню выбора языка
            if edit_message_id is not None:
                # пытаемся обработать нажатие юзера по кнопке выбора языка (изменить список кнопок)
                try:
                    await self.parent.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=edit_message_id, reply_markup=keyboard)
                # если не получилось обработать, удаляем сообщение со списком кнопок выбора языка
                except:
                    await self.parent.bot.delete_message(chat_id=message.chat.id, message_id=edit_message_id)
            else:
                await message.answer(text=f"Choose language", reply_markup=keyboard)
        # проверяем, вызвана этот метод командой, или перелистыванием страницы
        if first_launch:
            # удаляем сообщение от юзера с командой
            await modules.chat_manager.delete_last_msg(self.parent.bot, message)

    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок выбора языка

        # если метод был вызван впервые, то отпределяю кол-во страниц
        if self.pages == None:
            await self.get_pages_count()

        # если была команда для перехода к другой странице, то
        if call.data.startswith("page"):
            # извлекаем номер страницы из callback_data
            current_page = int(call.data.split()[-1])
            # проверяем, не пытаемся-ли мы перейти на несуществующую страницу
            if current_page < 0:
                current_page = 0
                return
            elif current_page > self.pages-1:
                current_page = self.pages-1
                return
            
        # если была нажата кнопка смены страницы
        if call.data.startswith("page"):
            # создаём новый список кнопок для новой страницы
            await self.create_buttons(message=call.message, page=current_page, first_launch=False, edit_message_id=call.message.message_id)
        # Если была выбрана кнопка смены языка
        elif call.data != "current_page":
            lang = call.data
            # тут выводится инфо о том, какой язык был выбран (нужно, чтобы текст был на том языке, который выбран)
            await call.answer(f"{lang}")
            await self.parent.bot.edit_message_text(text=f"You selected language: {lang}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            await state.finish()

    async def get_pages_count(self) -> None:
        #метод задаёт кол-во страниц с языками
        self.pages = await self.parent.db_manager.get_data(query=f"SELECT COUNT(*) FROM langs")
        self.pages = (self.pages[0][0] // self.limit) + (1 if self.pages[0][0] % self.limit > 0 else 0)
