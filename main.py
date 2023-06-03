from imports import *

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token, db_name):
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_name = db_name
        self.register_handlers()

    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.dp.register_message_handler(self.handle_start, commands=['star'])
        

    async def handle_start(self, message: types.Message):
        # запускаем обработку команды /start
        
        limit = 5 # кол-во языков, отображаемых на одной странице
        # количество страниц с языками
        pages = await modules.db_manager.db_query(db_name=self.db_name, query=f"SELECT COUNT(*) FROM langs")
        pages = (pages[0][0] // limit) + (1 if pages[0][0] % limit > 0 else 0)
        # выводим кнопки для выбора языка
        await modules.select_lang.LangSelector(parent=self, pages=pages, limit=limit).create_buttons(message=message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # выводит некоторые логи в консоль
    SpinnerBot = ChatBot(token=modules.get_token.get_token(), db_name="./database/spinner.db")
    asyncio.run(SpinnerBot.dp.start_polling())
