import telebot
import sqlite3
import threading
import time

class ChatBot:
    def __init__(self, token, db_name):
        self.bot = telebot.TeleBot(token)
        self.db_name = db_name
        self.register_handlers()
        self.run()

    def register_handlers(self):
        # создаём бинды обработчиков команд
        self.bot.message_handler(commands=['start'])(lambda msg: threading.Thread(target=self.handle_start, args=(msg,)).start())


    def handle_start(self, message):
        # запускаем обработку команды /start
        result = self.db_query(query="SELECT name, tag FROM langs")

        if result:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            for r in result:
                callback_data = f"{r[0]}"
                button = telebot.types.InlineKeyboardButton(text=r[0], callback_data=callback_data)
                # регистрируем обработчик для каждой кнопки
                self.bot.callback_query_handler(func=lambda call, selected_lang=r[0]: call.data == f"{selected_lang}")(lambda call, selected_lang=r[1]: self.handle_set_lang(call, selected_lang))
                keyboard.add(button)
            # отправляем юзеру меню выбора языка
            self.bot.send_message(chat_id=message.chat.id, text="Choose language:", reply_markup=keyboard)

    def handle_set_lang(self, call, data):
        # обработчик для кнопок выбора языка
        # выводим сообщение, какой язык выбран
        self.bot.answer_callback_query(callback_query_id=call.id, text=f"You selected {call.data}")
            
    def run(self):
        # запускаем вечный цикл обработки сообщений
        self.bot.polling(none_stop=True)

    def db_query(self, query):
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
                time.sleep(0.1)


if __name__ == '__main__':
    SpinnerBot = ChatBot(token='6108544466:AAF012RlMXPAXTUc_EKm05FSqBekLigLNnw', db_name="./spinner.db")
    SpinnerBot.run()