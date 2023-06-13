"""
модуль реализует класс для асинхронного ведения логов.
чтобы писать логи в файл, нужно перенаправить поток вывода в ОС
в файл
"""

import datetime
import aioconsole # асинхронный вывод текста в консоль

class Logger():
    def __init__(self, logging: bool = True):
        # logging - флаг, отвечающий, будет-ли вестить логирование или нет
        self.logging = logging

    async def write_to_log(self, module_name=__name__, func_name="", level: str ="INFO", log_text: str =""):
        '''
        функция асинхронного логирования. Для записи логов в файл, нужно запускать бота
        с перенаправлением вывода в файл. Принимает параметры:
        module_name - имя модуля, в котором было вызвано логирование
        func_name - функция, из которой было вызвано логирование
        level - уровень лога (INFO, ERROR, DEBUG, WARNING, CRITICAL)
        log_text - текст, который будет записан в строке лога
        '''

        # если флаг не активирован, то не логируем
        if not self.logging:
            return None

        # формируем строку уровня определённой длины
        level = level+" "*(8-len(level))

        # получаем форматированную дату-время
        now = datetime.datetime.now()
        now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # асинхронная функция вывода лога
        await aioconsole.aprint(f"{now_date_time} | {level} | {module_name}:{func_name} | {log_text}")