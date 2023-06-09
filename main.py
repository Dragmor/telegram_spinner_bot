from modules.imports import *

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token: str, db_conf: str) -> None:
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_manager = modules.db_manager.DataBaseManager(db_conf)
        
        # объект кнопок выбора языка
        self.lang_selector = modules.user_commands.settings.select_lang.LangSelector(parent=self, limit=modules.get_json_data.get_data(fname="./settings/settings.json", data="lang_buttons_in_page"))
        self.register_handlers() # биндим команды

    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_message_handler(self.lang_selector.create_buttons, commands=['set_lang'])
        
    async def handle_start(self, message: types.Message) -> None:       
        # обработка команды /start
        
        # загружаю команды в меню бота из файла
        await modules.user_commands.settings.load_commands.load_commands(parent=self, bot=self.bot)
        # удаляем сообщение /start от юзера в чате
        await modules.chat_manager.delete_last_msg(self.bot, message)
        # выводим кнопки для выбора языка
        await self.lang_selector.create_buttons(message=message, first_launch=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # выводит некоторые логи в консоль
    # извлекаем из переменных окружения значения для коннеката к БД
    db_conf = {"user": os.getenv('USER'),
        "password": os.getenv('PASSWORD'),
        "host": os.getenv('HOST'),
        "port": os.getenv('PORT'),
        "database": os.getenv('DATABASE')}
    # создаём объект бота
    SpinnerBot = ChatBot(token=os.getenv('TOKEN'), db_conf=db_conf)
    asyncio.run(SpinnerBot.dp.start_polling())



"""
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
"""