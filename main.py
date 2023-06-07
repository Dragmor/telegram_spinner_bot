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
    # извлекаем из json-файла данные для подключения к БД mysql
    db_conf = modules.get_json_data.get_data(fname="./settings/mysql_access_data.json", data=["user","password","host","port","database"])
    # создаём объект бота
    SpinnerBot = ChatBot(token=modules.get_json_data.get_data(fname="./settings/token.json", data="telegram_bot_token"), db_conf=db_conf)
    asyncio.run(SpinnerBot.dp.start_polling())
