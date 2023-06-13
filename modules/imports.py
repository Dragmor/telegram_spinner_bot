'''
это список для импортирования модулей в основной скрипт
при старте main.py подгружает все модули
'''

import sys # для полученния переданных параметров при запуске скрипта
import asyncio # многопоточность
from loguru import logger # модуль для реализации асинхронного логирования
import os # для извлечения из переменных окружения токена и других переменных
import datetime # для работы с текущей датой (например, для записи даты регистрации юзера)

# модули для телеги
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

# самописные модули
import modules.db_manager
import modules.get_json_data
import modules.user_commands.settings.check_user
import modules.user_commands.settings.select_lang
import modules.user_commands.settings.select_gender
import modules.user_commands.settings.load_commands
