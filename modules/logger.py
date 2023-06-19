import aioconsole
import aiofiles
import datetime

"""
для асинхронного ведения логов.
чтобы писать логи в файл, нужно перенаправить поток вывода в ОС
в файл
"""

async def write_to_log(logging: bool =True, module_name: str ="", func_name: str ="", level: str ="INFO", log_text: str =""):
    '''
    функция асинхронного логирования. Для записи логов в файл, нужно запускать бота
    с перенаправлением вывода в файл. Принимает параметры:

    logging - флаг, отвечающий, будет-ли вестить логирование или нет
    module_name - имя модуля, в котором было вызвано логирование
    func_name - функция, из которой было вызвано логирование
    level - уровень лога (INFO, ERROR, DEBUG, WARNING, CRITICAL)
    log_text - текст, который будет записан в строке лога
    '''

    # если флаг не активирован, то не логируем
    if not logging:
        return None

    # формируем строку уровня определённой длины
    level = level+" "*(8-len(level))

    # получаем форматированную дату-время
    now = datetime.datetime.now()
    now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # формируем строку лога
    log_text = f"{now_date_time} | {level} | {module_name}:{func_name} - {log_text}"

    # асинхронная функция вывода лога в консоль
    await aioconsole.aprint(log_text)

    # асинхронная запись лога в файл
    await write_to_file(filename="log.txt", text=log_text)


async def write_to_file(filename, text):
    # асинхронная запись текста в файл

    async with aiofiles.open(filename, 'a') as f:
        await f.write(text + '\n')
