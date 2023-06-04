'''
содержит функции для управления отображения чата (удаление сообщений)
'''

async def delete_last_msg(bot, message) -> None:
    # удаляем последнее сообщение
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)