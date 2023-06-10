from aiogram import types
'''
метод загружает в бота команды из БД (в кнопку МЕНЮ слева от поля ввода сообщения)
Команды имеют разные уровни допусков, и поэтому сначала получаем допуск данного юзера,
а потом заполняем кнопку МЕНЮ подходящими командами
'''

async def load_commands(parent, user_id) -> None:
    temp = await parent.db_manager.get_data(query=f"SELECT iso, role FROM users WHERE ids = {user_id}")
    lang = temp[0][0]
    role = temp[0][1]
    # если язык не был выбран юзером, то выводим описание на английском
    if lang == "0":
        lang = "eng"
    # получаю из БД все команды
    data = await parent.db_manager.get_data(query=f"SELECT command, {lang} FROM commands WHERE role >= {role}")
    # Список пользовательских команд
    commands = []
    for command in data:
        commands.append(types.BotCommand(command=f"{command[0]}", description=f"{command[1]}"))
    # присваиваю команды из списка в меню
    await parent.bot.set_my_commands(commands)
