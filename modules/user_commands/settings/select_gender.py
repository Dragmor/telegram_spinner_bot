from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
#
import modules.chat_manager

'''
модуль реализует выбор пола, выводя пользователю список кнопок.
При выборе кнопки в БД юзера записывается значение выбранного пола
'''

class GenderSelector():
    def __init__(self, parent) -> None:
        self.parent = parent     
        self.title = "👨❓👱‍♀️" # заголовок сообщения с кнопками 
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("gender"))  

    async def create_buttons(self, message) -> None:
        # создаём список кнопок для выбора языка

        # извлекаем iso юзера
        iso = await self.parent.db_manager.get_data(query=f"SELECT iso FROM users WHERE ids = {message['chat']['id']}")
        # если язык ещё не был указан, то ставлю eng
        if iso == None or iso[0][0] == "0":
            iso = "eng"
        # если же были извлечены данные, то
        else:
            iso = iso[0][0]
        # извлекаем из БД название гендера на языке ISO
        result = await self.parent.db_manager.get_data(query=f"SELECT flag, name, gender FROM genders WHERE iso = '{iso}'")
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for flag, name, gender in result:
                callback_data = f"gender=={gender}"
                # присваиваем кнопке текст: флаг и название языка
                button = InlineKeyboardButton(text=f"{flag} {name}", callback_data=callback_data)
                keyboard.add(button)

            # отправляем юзеру меню выбора пола
            await message.answer(text=self.title, reply_markup=keyboard)

    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок выбора пола

        # если была нажата кнопка выбора пола
        gender = call.data.split("==")[-1]
        # вношу выбранный пол в БД
        await self.parent.db_manager.write_data(query=f"UPDATE users SET gender = '{gender}' WHERE ids = {call['from']['id']}")
        # удаляем меню выбора пола
        await self.parent.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await state.finish()
        
        # проверяем, какие поля ещё не заполнил юзер
        await modules.user_commands.settings.check_user.check_user_data(parent=self.parent, user_id=call['message']['chat']['id'], message=call.message)
