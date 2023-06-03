from imports import *

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token, db_name):
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_name = db_name # название БД
        # объект кнопок выбора языка
        self.lang_selector = modules.select_lang.LangSelector(parent=self, limit=modules.get_json_data.get_data(fname="settings.json", data="limit"))
        self.register_handlers() # биндим команды

    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_message_handler(self.lang_selector.create_buttons, commands=['set_lang'])
        
    async def handle_start(self, message: types.Message):       
        # обработка команды /start
             
        # выводим кнопки для выбора языка
        await self.lang_selector.create_buttons(message=message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # выводит некоторые логи в консоль
    SpinnerBot = ChatBot(token=modules.get_json_data.get_data(fname="token.json", data="telegram_bot_token"), db_name="./database/spinner.db")
    asyncio.run(SpinnerBot.dp.start_polling())
