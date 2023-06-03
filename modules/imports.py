'''
это список для импортирования модулей в основной скрипт
при старте main.py подгружает все модули
'''

import asyncio # многопоточность
import logging # модуль для отображения логов в консоли

# модули для телеги
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# самописные модули
import modules.db_manager
import modules.select_lang
import modules.get_json_data
import modules.chat_manager
import modules.load_commands
