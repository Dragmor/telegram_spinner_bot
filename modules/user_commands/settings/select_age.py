# модули для телеги
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# для определения года рождения
import datetime

# самописные модули
from modules.user_commands.settings import check_user_data

'''
модуль реализует выбор возраста юзера, выводя пользователю список кнопок.
При выборе кнопки в БД юзера записывается значение год рождения (текущий год - указанный возраст)
'''

class AgeSelector():
    def __init__(self, parent) -> None:
        self.parent = parent
        # минимальный возраст, максимальный(+шаг), шаг 
        # присваиваем дефолтные значения. После запуска они будут перезаписаны значениями из БД
        # (присваиваем сюда значения настроек из БД при создании объекта в классе ChatBot)
        self.min_age = 6
        self.max_age = 65
        self.age_step = 10
        #
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("diapason"))
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("age"))
        self.parent.dp.register_callback_query_handler(self.handle, lambda c: c.data.startswith("back"))

    async def create_buttons(self, message, command_launch: bool=True, back_button: bool=False) -> None:
        # создаём список кнопок (если command_launch=True, то вызов был по команде юзера)
        # back_button означает, что метод вызван нажатием кнопки НАЗАД, для перерисовки сообщения без его удаления

        #если этот метод вызван командой /, то удаляем сообщение с этой командой
        if command_launch:
            # удаляем сообщение от юзера с командой
            await message.delete()
        
        # создаём для начала клавиши выбора диапазона для возраста
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        # создаём кнопки возрастов
        for diapason in range(self.min_age, self.max_age, self.age_step):
            callback_data = f"diapason=={diapason}"
            # присваиваем кнопке текст
            button = InlineKeyboardButton(text=f"{diapason}-{diapason+9}", callback_data=callback_data)
            keyboard.add(button)

        if back_button:
            await self.parent.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
        else:
            # заголовок сообщения с кнопками
            title = await self.parent.db_manager.get_data(query=f'''SELECT text FROM texts
                                                                    WHERE place = "age" AND lang_iso = 
                                                                    (SELECT lang_iso FROM users WHERE ids = {message['chat']['id']})''')
            # отправляем юзеру меню выбора диапазона возраста
            await message.answer(text=title[0][0], reply_markup=keyboard)

            

    async def handle(self, call: CallbackQuery, state: FSMContext) -> None:
        # обработчик для кнопок

        # если был выбран диапазон возраста
        if call.data.startswith("diapason"):
            # если была нажата кнопка выбора диапазона, то
            # меняю клавиатуру диапазонов на клавиатуру возраста
            
            diapason = int(call.data.split("==")[-1]) # получаю указанный диапазон возраста
            # меняю клавиатуру
            keyboard = InlineKeyboardMarkup(row_width=1)
            # создаю кнопки для выбора возраста
            for age in range(diapason, int(diapason+self.age_step)):
                callback_data = f"age=={age}"
                # присваиваем кнопке конкретный возраст для выбора
                button = InlineKeyboardButton(text=f"{age}", callback_data=callback_data)
                keyboard.add(button)
            # создаём кнопку "назад"
            # заголовок сообщения с кнопками
            button_text = await self.parent.db_manager.get_data(query=f'''SELECT text FROM texts
                                                        WHERE place = "back_button" AND lang_iso = 
                                                        (SELECT lang_iso FROM users WHERE ids = {call['from']['id']})''')

            keyboard.row(InlineKeyboardButton(text=button_text[0][0], callback_data=f"back"))
            await self.parent.bot.edit_message_reply_markup(chat_id=call['from']['id'], message_id=call.message.message_id, reply_markup=keyboard)
        
        # если была нажата кнопка назад
        elif call.data=="back":
            await self.create_buttons(message=call.message, command_launch=False, back_button=True)
        
        # если был выбран возраст
        elif call.data.startswith("age"):
            # определяю год рождения

            # получаем выбранный возраст (в int)
            selected_age = int(call.data.split("==")[1])
            # высчитываем год рождения
            year_of_birth = datetime.datetime.now().year - selected_age
            # вношу год рождения в БД
            await self.parent.db_manager.write_data(query=f"UPDATE users SET year_of_birth = '{year_of_birth}' WHERE ids = {call['from']['id']}")
            # удаляем меню выбора 
            await call.message.delete()
            await state.finish()

            # убираем значок таймера с нажатой кнопки
            await call.answer()

            # проверяем, какие поля ещё не заполнил юзер
            await check_user_data(parent=self.parent, message=call.message)
