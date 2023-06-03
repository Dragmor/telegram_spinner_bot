import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import sqlite3

class LangStates(StatesGroup):
    lang = State()

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token, db_name):
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_name = db_name
        self.register_handlers()

    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_callback_query_handler(self.handle_set_lang, state=LangStates.lang)

    async def handle_start(self, message: types.Message):
        # запускаем обработку команды /start
        result = await self.db_query(query="SELECT name, iso FROM langs")  # Add 'await' here
        # проверяем, есть ли извлечённые данные из БД
        if result:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for r in result:
                callback_data = f"{r[0]}"
                button = InlineKeyboardButton(text=r[0], callback_data=callback_data)
                keyboard.add(button)
            # отправляем юзеру меню выбора языка
            await message.answer(text="Choose language:", reply_markup=keyboard)
            await LangStates.lang.set()

    async def handle_set_lang(self, call: CallbackQuery, state: FSMContext):
        # обработчик для кнопок выбора языка
        # выводим сообщение, какой язык выбран
        lang = call.data
        # тут выводится инфо о том, какой язык был выбран (нужно, чтобы текст был на том языке, который выбран)
        await call.answer(f"You selected {lang}")
        await self.bot.edit_message_text(text=f"You selected language: {lang}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        await state.finish()

    async def db_query(self, query):
        # метод подключается к БД, выполняет запрос, и возвращает кортеж извлечённых данных
        # делаем очередь для обращения к БД из потоков
        while True:
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result
            except sqlite3.OperationalError:
                # ждём, пока БД станет доступной
                await asyncio.sleep(0.1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    SpinnerBot = ChatBot(token='6108544466:AAF012RlMXPAXTUc_EKm05FSqBekLigLNnw', db_name="./spinner.db")
    asyncio.run(SpinnerBot.dp.start_polling())