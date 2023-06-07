import json
'''
модуль для парсинга .json-файлов
принимает на вход название json-файла, и имя (или список имён), по которому будет извлечено значение.
Если в data передана строка, то вернёт извлеченное значение.
Если в data передан список, то вернёт словарь {ключ: значение}
'''
def get_data(fname: str, data: str) -> str:
    # Открываем файл token.json и читаем его содержимое в переменную
    with open(fname, 'r') as f:
        file_data = f.read()
    # Распарсиваем содержимое файла, чтобы получить объект Python
    json_data = json.loads(file_data)
    # если передана 1 строка, то извлекаю по ней данные и возвращаю их
    if type(data) == str:
        # Извлекаем строку из объекта Python
        extracted_data = json_data[data]
    # если передан список параметров, то возвращаем словарь значений
    elif type(data) == list:
        extracted_data = {}
        for key in data:
            extracted_data[key] = json_data[key]
    # Возвращаем извлечённые данные
    return extracted_data
    