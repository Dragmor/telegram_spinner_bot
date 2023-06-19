from modules import logger # для логирования
from aiogram import types

'''
метод загружает в бота команды из БД (в кнопку МЕНЮ слева от поля ввода сообщения)
Команды имеют разные уровни допусков, и поэтому сначала получаем допуск данного юзера,
а потом заполняем кнопку МЕНЮ подходящими командами
'''

async def load_commands(parent, user_id) -> None:
    # получаю из БД все команды (фильтруя по ISO и ROLE юзера)
    # тут применяю моржовый оператор, чтобы не делать конструкцию if-else
    if (data := await parent.db_manager.get_data(query=f'''SELECT c.command, c.description 
                                                     FROM commands AS c 
                                                     JOIN users AS u ON c.role >= u.role
                                                     AND c.iso = u.iso 
                                                     WHERE u.ids = {user_id}''')) == None:
        # если юзера ещё нет в БД, то добавляем кнопки в меню на английском
        data = await parent.db_manager.get_data(query=f'''SELECT command, description 
                                                     FROM commands 
                                                     WHERE iso = "eng" and role = 5''')
        
    # Список пользовательских команд
    commands = []
    for command in data:
        commands.append(types.BotCommand(command=f"{command[0]}", description=f"{command[1]}"))
    # присваиваю команды из списка в меню
    await parent.bot.set_my_commands(commands)
