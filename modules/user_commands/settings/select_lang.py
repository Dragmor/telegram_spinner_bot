from modules.imports import *

'''
модуль реализует выбор языка, выводя пользователю список кнопок.
При выборе кнопки, сообщение меняется, а в БД юзера записывается значение выбранного языка
'''

class LangSelector():
    def __init__(self, parent, limit: int) -> None:
        self.parent = parent     
        self.title = "💬❔" # заголовок сообщения с кнопками выбора
        # привязываю вызов обработчика 
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("lang"))   
        self.limit = int(limit) # сколько кнопок на одной странице
        self.pages = None

    async def create_buttons(self, message, page=0, command_launch=True, edit_message_id=None) -> None:
        # проверяем, вызвана этот метод командой /, или перелистыванием страницы
        if command_launch:
            # удаляем сообщение от юзера с командой
            await message.delete()
            
        # переменная, отвечающая за текущую страницу
        current_page = page
        if self.pages == None:
            await self.get_pages_count()        
        # создаём список кнопок для выбора языка
        offset = current_page * self.limit
        # извлекаем из БД флаг, название языка и ISO
        result = await self.parent.db_manager.get_data(query=f"SELECT flag, name, iso FROM langs LIMIT {self.limit} OFFSET {offset}")
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for flag, name, iso in result:
                callback_data = f"lang=={iso}"
                # присваиваем кнопке текст: флаг и название языка
                button = InlineKeyboardButton(text=f"{flag} {name}", callback_data=callback_data)
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
                await message.answer(text=self.title, reply_markup=keyboard)


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
            lang = call.data.split("==")[-1]
            # тут выводится инфо о том, какой язык был выбран (нужно, чтобы текст был на том языке, который выбран)
            # отправляем уведомление о выбранном языке
            # await call.answer(f"{lang}")
            # меняем текст сообщения
            # await self.parent.bot.edit_message_text(text=f"You selected language: {lang}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            # вношу iso выбранного языка в БД юзеру
            await self.parent.db_manager.write_data(query=f"UPDATE users SET iso = '{lang}' WHERE ids = {call['from']['id']}")
            # удаляем сообщение с кнопками после выбора языка
            await call.message.delete()
            await state.finish()

            # загружаю команды в меню бота из БД на выбранном языке
            await modules.user_commands.settings.load_commands.load_commands(parent=self.parent, user_id=call['message']['chat']['id'])
            
            # проверяем, какие поля ещё не заполнил юзер
            await modules.user_commands.settings.check_user.check_user_data(parent=self.parent, user_id=call['message']['chat']['id'], message=call.message)
            

    async def get_pages_count(self) -> None:
        # метод задаёт кол-во страниц с языками
        self.pages = await self.parent.db_manager.get_data(query=f"SELECT COUNT(*) FROM langs")
        # определяем, сколько языков есть в БД, и определяем, сколько страниц должно быть (для перелистывания)
        self.pages = (self.pages[0][0] // self.limit) + (1 if self.pages[0][0] % self.limit > 0 else 0)
