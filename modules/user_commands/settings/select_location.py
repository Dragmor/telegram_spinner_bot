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

class LocationSelector():
    def __init__(self, parent: int) -> None:
        self.parent = parent     
        # привязываю вызов обработчика 
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("location"))   

    async def create_buttons(self, message, command_launch=True, edit_message_id=None) -> None:
        # проверяем, вызвана этот метод командой /, или перелистыванием страницы
        if command_launch:
            # удаляем сообщение от юзера с командой
            await message.delete()
            
        # извлекаем из БД
        # тут мы берём все cl кроме cl = 1, так как первый cl это Global
        result = await self.parent.db_manager.get_data(query=f'''SELECT r.id, r.name 
                                                         FROM locations AS r 
                                                         JOIN users AS u ON r.lang_iso = u.lang_iso 
                                                         WHERE u.ids = {message['chat']['id']} AND r.cl != 1
                                                         ''')
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for region_id, name in result:
                callback_data = f"location=={region_id}"
                # присваиваем кнопке текст
                button = InlineKeyboardButton(text=f"{name}", callback_data=callback_data)
                keyboard.add(button)

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
                title = await self.parent.db_manager.get_data(query=f'''SELECT t.text FROM texts AS t
                                                                    WHERE t.place = "location" AND t.lang_iso = 
                                                                    (SELECT lang_iso FROM users WHERE ids = {message['chat']['id']})''')
                # отправляем юзеру сообщение с кнопками
                await message.answer(text=title[0][0], reply_markup=keyboard)


    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок выбора языка

        # Если была выбрана кнопка выбора области
        if call.data != "location_current_page":
            location_id = call.data.split("==")[-1]

            await self.parent.db_manager.write_data(query=f'''UPDATE users 
                                                            SET cl = (SELECT cl FROM locations WHERE id = {location_id})
                                                            WHERE ids = {call['from']['id']}''')

            # удаляем сообщение с кнопками после выбора языка
            await call.message.delete()
            await state.finish()
            
            # проверяем, какие поля ещё не заполнил юзер
            await user_settings.check_user_data(parent=self.parent, message=call.message)
        # убираем значок таймера с нажатой кнопки
        await call.answer()


