# модули для телеги
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# импортируем пакет с командами настроек профиля юзера
import modules.user_commands.settings as user_settings
from modules import logger # для логирования

'''
модуль реализует выбор пола, выводя пользователю список кнопок.
При выборе кнопки в БД юзера записывается значение выбранного пола
'''

class GenderSelector():
    def __init__(self, parent) -> None:
        self.parent = parent     
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("gender"))  

    async def create_buttons(self, message, command_launch=True) -> None:
        # создаём список кнопок для выбора языка (если command_launch=True, то вызов был по команде юзера)

        #если этот метод вызван командой /, то удаляем сообщение с этой командой
        if command_launch:
            # удаляем сообщение от юзера с командой
            await message.delete()
        
        # получаем lang_iso юзера и извлекаем название гендера на этом языке
        result = await self.parent.db_manager.get_data(query=f'''SELECT g.flag, g.name, g.gender 
                                                                 FROM genders AS g 
                                                                 JOIN users AS u ON g.lang_iso = u.lang_iso 
                                                                 WHERE u.ids = {message['chat']['id']}''')
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for flag, name, gender in result:
                callback_data = f"gender=={gender}"
                # присваиваем кнопке текст: флаг и название языка
                button = InlineKeyboardButton(text=f"{flag} {name}", callback_data=callback_data)
                keyboard.add(button)

            # заголовок сообщения с кнопками
            title = await self.parent.db_manager.get_data(query=f'''SELECT t.text FROM texts AS t
                                                                    JOIN users AS u ON t.lang_iso = u.lang_iso
                                                                    WHERE t.place = "gender"''')
            # отправляем юзеру меню выбора пола
            await message.answer(text=title[0][0], reply_markup=keyboard)

            

    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок выбора пола

        # если была нажата кнопка выбора пола
        gender = call.data.split("==")[-1]
        # вношу выбранный пол в БД
        await self.parent.db_manager.write_data(query=f"UPDATE users SET gender = '{gender}' WHERE ids = {call['from']['id']}")
        # удаляем меню выбора пола
        await call.message.delete()
        await state.finish()
        
        # проверяем, какие поля ещё не заполнил юзер
        await user_settings.check_user_data(parent=self.parent, user_id=call['message']['chat']['id'], message=call.message)
