from modules.imports import *

class ChatBot:
    '''класс чат-бота'''
    def __init__(self, token: str, db_conf: str) -> None:
        self.bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db_manager = modules.db_manager.DataBaseManager(db_conf)
        
        # объект кнопок выбора языка
        self.lang_selector = modules.user_commands.settings.select_lang.LangSelector(parent=self, limit=modules.get_json_data.get_data(fname="./settings/settings.json", data="lang_buttons_in_page"))
        # объект кнопок выбора пола
        self.gender_selector = modules.user_commands.settings.select_gender.GenderSelector(parent=self)
        self.register_handlers() # биндим команды

    async def on_startup(self, dp):
        '''
        метод запускается при старте бота. Тут прописываем важные для работы бота
        события (подключение к БД и т.д.), которые должны произойти сразу после старта
        '''
        # подключаемся к БД
        await self.db_manager.connect()


    def register_handlers(self):
        # создаём бинды обработчиков команд
        
        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_message_handler(self.lang_selector.create_buttons, commands=['lang'])
        self.dp.register_message_handler(self.gender_selector.create_buttons, commands=['gender'])
        self.dp.register_message_handler(self.echo)
        
    async def handle_start(self, message: types.Message) -> None:
        # обработка команды /start
        
        # удаляем сообщение /start от юзера в чате
        # тут мы используем create_task() чтобы handle_start() не блокировался на выполнении каждой задачи (асинхронность)
        await message.delete()
        # проверяем, какие данные о юзере ещё не заполнены, и выводим ему сообщения для их выбора
        await modules.user_commands.settings.check_user.check_user_data(parent=self, user_id=message['from']['id'], message=message)
        # загружаю команды в меню бота из БД на выбранном юзером языке
        await modules.user_commands.settings.load_commands.load_commands(parent=self, user_id=message['from']['id'])
        

    async def echo(self, message: types.Message):
        # тестовый метод, который обрабатывает все сообщения, которые не были обработаны другими хендлерами

        # отвечаю на сообщение юзера эхо-сообщением
        await message.reply(text=message.text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)# выводит некоторые логи в консоль
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
    # запускаем диспетчер
    executor.start_polling(SpinnerBot.dp, skip_updates=False, on_startup=SpinnerBot.on_startup)



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


# await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id) # удаляет любое сообщение по его id и id чата
# await message.delete() # удаляет сообщение message
"""