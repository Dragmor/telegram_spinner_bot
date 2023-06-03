import json

def get_token():
    # Открываем файл token.json и читаем его содержимое в переменную
    with open('token.json', 'r') as f:
        data = f.read()
    # Распарсиваем содержимое файла, чтобы получить объект Python
    token = json.loads(data)
    # Извлекаем строку из объекта Python
    token_str = token["telegram_bot_token"]
    # Возвращаем извлечённый токен
    return token_str