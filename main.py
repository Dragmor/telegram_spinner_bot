# модули для телеги
from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

#
import asyncio # асинхронность
import os # для извлечения из переменных окружения токена и других переменных
import sys # для полученния переданных параметров при запуске скрипта

# самописные модули
import modules.user_commands.settings as user_settings
from modules import db_manager, write_to_log, currentframe, settings_loader

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token: str, db_conf: str) -> None:
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_manager = db_manager.DataBaseManager(db_conf)

        # объект кнопок выбора языка
        self.lang_selector = user_settings.LangSelector(parent=self)
        # объект кнопок выбора пола
        self.gender_selector = user_settings.GenderSelector(parent=self)
        #объект выбора возраста
        self.age_selector = user_settings.AgeSelector(parent=self)

        self.register_handlers() # биндим команды


    async def on_startup(self, dp):
        '''
        метод запускается при старте бота. Тут прописываем важные для работы бота
        события (подключение к БД, включение логирования и т.д.), которые должны произойти сразу после старта
        '''
        # подключаемся к БД (и ждём, пока приконнектимся!)
        await self.db_manager.connect()

        # извлекаем настройки из БД для объектов
        # кол-во языков на 1 странице
        if (temp:=await settings_loader.get_value(self.db_manager, "langs_on_page")) != None: self.lang_selector.limit = temp
        # минимальный возраст, максимальный(+шаг), шаг (для объекта выбора возраста)
        if (temp:=await settings_loader.get_value(self.db_manager, "min_age")) != None: self.age_selector.min_age = temp
        if (temp:=await settings_loader.get_value(self.db_manager, "max_age")) != None: self.age_selector.max_age = temp
        if (temp:=await settings_loader.get_value(self.db_manager, "age_step")) != None: self.age_selector.age_step = temp

        # если был передан параметр -logging, то включаем логирование
        if "-logging" in sys.argv:
            # записываю лог, и не дожидаясь отработки функции, продолжаю выполнение бота
            asyncio.get_event_loop().create_task(write_to_log(logging=True, level="SUCCESS", log_text="Bot started!", module_name=__name__, func_name=currentframe().f_code.co_name))

            # # эта конструкция ожидает, пока запишется лог, и только тогда продолжает работу бота
            # await modules.logger.write_to_log(logging=True, level="SUCCESS", log_text="Bot started!", module_name=__name__, func_name=inspect.currentframe().f_code.co_name)


    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_message_handler(self.lang_selector.create_buttons, commands=['lang'])
        self.dp.register_message_handler(self.gender_selector.create_buttons, commands=['gender'])
        self.dp.register_message_handler(self.age_selector.create_buttons, commands=['age'])
        self.dp.register_message_handler(self.echo) # получает ВСЕ сообщения, не уловленные предыдущими хендлерами
        
    async def handle_start(self, message: types.Message) -> None:
        # обработка команды /start
        
        # удаляем сообщение /start от юзера в чате
        # тут мы используем create_task() чтобы handle_start() не блокировался на выполнении каждой задачи (асинхронность)
        asyncio.get_event_loop().create_task(message.delete())
        # проверяем, какие данные о юзере ещё не заполнены, и выводим ему сообщения для их выбора
        await user_settings.check_user_data(parent=self, user_id=message['from']['id'], message=message)
        # загружаю команды в меню бота из БД на выбранном юзером языке
        asyncio.get_event_loop().create_task(user_settings.load_commands(parent=self, user_id=message['from']['id']))
        

    async def echo(self, message: types.Message):
        # тестовый метод, который обрабатывает все сообщения, которые не были обработаны другими хендлерами

        # отвечаю на сообщение юзера эхо-сообщением
        asyncio.get_event_loop().create_task(message.reply(text=message.text))


if __name__ == "__main__":

    # извлекаем из переменных окружения значения для коннеката к БД
    db_conf = {
        "user": os.getenv('USER'),
        "password": os.getenv('PASSWORD'),
        "host": os.getenv('HOST'),
        "port": int(os.getenv('PORT')),
        "db": os.getenv('DATABASE')
    }
    # создаём объект бота
    SpinnerBot = ChatBot(token=os.getenv('TOKEN'), db_conf=db_conf)

    # # запускаем диспетчер (раньше использовал этот вариант вместо loop)
    # executor.start_polling(SpinnerBot.dp, skip_updates=False, on_startup=SpinnerBot.on_startup)

    # запускаем цикл для обработки событий бота
    loop = asyncio.get_event_loop()
    loop.create_task(executor.start_polling(SpinnerBot.dp, skip_updates=False, on_startup=SpinnerBot.on_startup, on_shutdown=loop.close))
    loop.run_forever()



"""
Logger method
logger.trace()
logger.debug()
logger.info()
logger.success()
logger.warning()
logger.error()
logger.critical()

# Изменение аватарки бота
with open('new_avatar.jpg', 'rb') as f:
    await bot.set_avatar(photo=f)

# Изменение описания бота
await bot.set_my_commands(commands=[
    types.BotCommand(command='start', description='Start the bot'),
    types.BotCommand(command='help', description='Get help')
])

# Изменение логотипа бота
with open('new_logo.jpg', 'rb') as f:
    await bot.set_photo(photo=f)

# Изменение имени бота
await bot.set_name(name='New Bot Name')

# изменяет описание профиля бота.
set_chat_description(chat_id: Union[int, str], description: str)


# await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id) # удаляет любое сообщение по его id и id чата
# await message.delete() # удаляет сообщение message
"""