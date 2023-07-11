# модули для телеги
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

#
import modules.user_commands.settings as user_settings
from modules import logger # для логирования

'''
модуль реализует выбор региона юзера, выводя пользователю список кнопок.
При выборе кнопки, сообщение меняется, а в БД юзера записывается значение выбранного региона
'''

class RegionSelector():
    def __init__(self, parent: int) -> None:
        self.parent = parent     
        # привязываю вызов обработчика 
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("region"))   
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("region_page"))
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("region_current_page"))
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("goto_locations"))

        self.limit = 8 # сколько кнопок на одной странице (значение присваивается в классе ChatBot в on_startup)

    async def create_buttons(self, message, page=0, command_launch=True, edit_message_id=None) -> None:
        # проверяем, вызвана этот метод командой /, или перелистыванием страницы
        if command_launch:
            # удаляем сообщение от юзера с командой
            await message.delete()
            
        # переменная, отвечающая за текущую страницу
        current_page = page
        pages = await self.get_pages_count(user_id=message['chat']['id'])        
        # создаём список кнопок для выбора языка
        offset = current_page * self.limit
        # извлекаем из БД
        result = await self.parent.db_manager.get_data(query=f'''SELECT r.id, r.name 
                                                         FROM regions AS r 
                                                         JOIN users AS u ON r.lang_iso = u.lang_iso AND r.cl = u.cl 
                                                         WHERE u.ids = {message['chat']['id']} AND r.cl = (SELECT cl FROM users WHERE ids = {message['chat']['id']})
                                                         LIMIT {self.limit} OFFSET {offset}''')
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for region_id, name in result:
                callback_data = f"region=={region_id}"
                # присваиваем кнопке текст
                button = InlineKeyboardButton(text=f"{name}", callback_data=callback_data)
                keyboard.add(button)

            if pages > 1:
                # добавляем кнопки для переключения страниц
                buttons = []
                # мы записываем id предыдущей и последующей страницы в бинд кнопок
                buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"region_page {current_page-1}"))
                current_page_button_text = f"[{current_page + 1}/{pages}]"
                buttons.append(InlineKeyboardButton(text=current_page_button_text, callback_data="region_current_page"))
                buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"region_page {current_page+1}"))
                # создаём столько рядов в нихнем строке, сколько кнопок в списке buttons
                keyboard.row(*buttons)

            button_text = await self.parent.db_manager.get_data(query=f'''SELECT text FROM texts
                                                                        WHERE place = "back_button" AND lang_iso = 
                                                                        (SELECT lang_iso FROM users WHERE ids = {message['chat']['id']})''')

            keyboard.add(InlineKeyboardButton(text=button_text[0][0], callback_data="goto_locations"))

            # отправляем юзеру меню
            if edit_message_id is not None:
                # пытаемся обработать нажатие юзера по кнопке (изменить список кнопок)
                try:
                    await self.parent.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=edit_message_id, reply_markup=keyboard)
                # если не получилось обработать, удаляем сообщение со списком кнопок
                except:
                    await self.parent.bot.delete_message(chat_id=message.chat.id, message_id=edit_message_id)
            else:
                # заголовок сообщения с кнопками
                title = await self.parent.db_manager.get_data(query=f'''SELECT text FROM texts
                                                                    WHERE place = "region" AND lang_iso = 
                                                                    (SELECT lang_iso FROM users WHERE ids = {message['chat']['id']})''')
                # отправляем юзеру сообщение с кнопками
                await message.answer(text=title[0][0], reply_markup=keyboard)


    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок выбора языка

        # если метод был вызван впервые, то отпределяю кол-во страниц
        pages =  await self.get_pages_count(user_id=call['from']['id'])

        # если была команда для перехода к другой странице, то
        if call.data.startswith("region_page"):
            # извлекаем номер страницы из callback_data
            current_page = int(call.data.split()[-1])
            # проверяем, не пытаемся-ли мы перейти на несуществующую страницу
            if current_page < 0:
                current_page = 0
                await call.answer()
                return
            elif current_page > pages-1:
                current_page = pages-1
                await call.answer()
                return

        elif call.data.startswith("goto_locations"):
            await self.parent.db_manager.write_data(query=f'''UPDATE users 
                                                            SET cl = 0
                                                            WHERE ids = {call['from']['id']}''')
            await call.message.delete()
            await state.finish()
            await user_settings.check_user_data(parent=self.parent, message=call.message)
            return
            
        # если была нажата кнопка смены страницы
        if call.data.startswith("region_page"):
            # создаём новый список кнопок для новой страницы
            await self.create_buttons(message=call.message, page=current_page, command_launch=False, edit_message_id=call.message.message_id)
        # Если была выбрана кнопка выбора области
        elif call.data != "region_current_page":
            region_id = call.data.split("==")[-1]
            # тут выводится инфо о том, какой язык был выбран (нужно, чтобы текст был на том языке, который выбран)
            # отправляем уведомление о выбранном языке
            # await call.answer(f"{lang}")
            # меняем текст сообщения
            # await self.parent.bot.edit_message_text(text=f"You selected language: {region_id}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            # вношу id выбранного области в БД юзеру
            await self.parent.db_manager.write_data(query=f'''UPDATE users 
                                                            SET cr = (SELECT cr FROM regions WHERE id = {region_id})
                                                            WHERE ids = {call['from']['id']}''')

            # удаляем сообщение с кнопками после выбора языка
            await call.message.delete()
            await state.finish()
            
            # проверяем, какие поля ещё не заполнил юзер
            await user_settings.check_user_data(parent=self.parent, message=call.message)
        # убираем значок таймера с нажатой кнопки
        await call.answer()

    async def get_pages_count(self, user_id) -> None:
        # метод задаёт кол-во страниц
        pages = await self.parent.db_manager.get_data(query=f'''SELECT COUNT(*) FROM regions AS r
                                                                    JOIN langs AS l ON r.lang_iso = l.id 
                                                                    WHERE l.id = (SELECT lang_iso FROM users WHERE ids = {user_id}) 
                                                                    and r.cl = (SELECT cl FROM users WHERE ids = {user_id})''')

                

        # определяем, сколько страниц должно быть (для перелистывания)
        return (pages[0][0] // self.limit) + (1 if pages[0][0] % self.limit > 0 else 0)
