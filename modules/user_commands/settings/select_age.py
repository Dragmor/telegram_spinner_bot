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
        self.title = "AD3reqr3dq@!df" # заголовок сообщения с кнопками
        self.diapason_step = 10 # шаг для цикла диапазона возрастов
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
        # минимальный возраст, максимальный(+шаг), шаг
        for diapason in range(6, 57, self.diapason_step):
            callback_data = f"diapason=={diapason}"
            # присваиваем кнопке текст
            button = InlineKeyboardButton(text=f"{diapason}-{diapason+9}", callback_data=callback_data)
            keyboard.add(button)

        if back_button:
            await self.parent.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
        else:
            # отправляем юзеру меню выбора диапазона возраста
            await message.answer(text=self.title, reply_markup=keyboard)

            

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
            for age in range(diapason, int(diapason+self.diapason_step)):
                callback_data = f"age=={age}"
                # присваиваем кнопке конкретный возраст для выбора
                button = InlineKeyboardButton(text=f"{age}", callback_data=callback_data)
                keyboard.add(button)
            # создаём кнопку "назад"
            keyboard.row(InlineKeyboardButton(text="⬅️", callback_data=f"back"))
            await self.parent.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        
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

            # проверяем, какие поля ещё не заполнил юзер
            await check_user_data(parent=self.parent, user_id=call['message']['chat']['id'], message=call.message)
