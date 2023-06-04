import json
'''
модуль для парсинга .json-файлов
принимает на вход название json-файла, и имя , по которому будет извлечено значение
'''
def get_data(fname: str, data: str) -> str:
    # Открываем файл token.json и читаем его содержимое в переменную
    with open(fname, 'r') as f:
        file_data = f.read()
    # Распарсиваем содержимое файла, чтобы получить объект Python
    json_data = json.loads(file_data)
    # Извлекаем строку из объекта Python
    extracted_data = json_data[data]
    # Возвращаем извлечённые данные
    return extracted_data
    