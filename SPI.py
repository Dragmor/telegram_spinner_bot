import telebot
import sqlite3

# Создание объекта бота и указание токена
bot = telebot.TeleBot('6148264041:AAEi_qQRI-oHOZHE3ktV4yZ7vlF5CMMcPI4')

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание подключения к базе данных
    conn = sqlite3.connect('F:/GREOR/prod/py/chat/spinner.db')
    
    # Получение списка языков из таблицы langs в базе данн
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM langs")
    result = cursor.fetchall()
    
    if result:
        # Создание клавиатуры с кнопками выбора языка (InlineKeyboardMarkup)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        
        # Добавление кнопок на клавиатуру
        for r in result:
            callback_data = f"select_language:{r[0]}"
            button = telebot.types.InlineKeyboardButton(text=r[0], callback_data=callback_data)
            keyboard.add(button)
        
        # Отправка сообщения с клавиатурой
        bot.send_message(chat_id=message.chat.id, text="Choose language:", reply_markup=keyboard)
    
    # Закрытие подключения к базе данных
    conn.close()
        
@bot.message_handler(commands=['ping'])
def handle_ping(message):
    bot.reply_to(message, "Pong")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
