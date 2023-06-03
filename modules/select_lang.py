from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
#
import modules.db_manager

'''
модуль реализует выбор языка, выводя пользователю список кнопок.
При выборе кнопки, сообщение меняется, а в БД юзера записывается значение выбранного языка (пока не реализовано)
'''

class LangSelector():
    def __init__(self, parent, pages, limit):
        self.parent = parent
        self.current_page = 0
        self.parent.dp.register_callback_query_handler(self.handle)
        self.pages = pages # сколько всего страниц
        self.limit = limit # сколько кнопок на одной странице

    async def create_buttons(self, message, edit_message_id=None):
        # создаём список кнопок для выбора языка
        offset = self.current_page * self.limit
        result = await modules.db_manager.db_query(db_name=self.parent.db_name, query=f"SELECT name, iso FROM langs LIMIT {self.limit} OFFSET {offset}")
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for r in result:
                callback_data = f"{r[0]}"
                button = InlineKeyboardButton(text=r[0], callback_data=callback_data)
                keyboard.add(button)
            # добавляем кнопки для переключения страниц
            buttons = []
            buttons.append(InlineKeyboardButton(text="⬅️", callback_data="prev_page"))
            current_page_button_text = f"[{self.current_page + 1}/{self.pages}]"
            buttons.append(InlineKeyboardButton(text=current_page_button_text, callback_data="current_page"))
            buttons.append(InlineKeyboardButton(text="➡️", callback_data="next_page"))
            # создаём столько рядов в нихнем строке, сколько кнопок в списке buttons
            keyboard.row(*buttons)
            # отправляем юзеру меню выбора языка
            if edit_message_id is not None:
                await self.parent.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=edit_message_id, reply_markup=keyboard)
            else:
                await message.answer(text=f"Choose language", reply_markup=keyboard)

    async def handle(self, call: CallbackQuery, state: FSMContext):
        # обработчик для кнопок выбора языка

        # если была нажата кнопка ВПЕРЁД/НАЗАД
        if call.data == "prev_page" or call.data == "next_page":
            # обработчик для кнопок переключения страниц
            if call.data == "prev_page":
                if self.current_page > 0:
                    self.current_page -= 1
                else:
                    return
            elif call.data == "next_page":
                if self.current_page < self.pages-1:
                    self.current_page += 1
                else:
                    return
            # создаём новый список кнопок для новой страницы
            await self.create_buttons(call.message, edit_message_id=call.message.message_id)
        # Если была выбрана кнопка смены языка
        elif call.data != "current_page":
            lang = call.data
            # тут выводится инфо о том, какой язык был выбран (нужно, чтобы текст был на том языке, который выбран)
            await call.answer(f"You selected {lang}")
            await self.parent.bot.edit_message_text(text=f"You selected language: {lang}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            await state.finish()
