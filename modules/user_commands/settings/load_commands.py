from aiogram import types
'''
метод загружает в бота команды из БД (в кнопку МЕНЮ слева от поля ввода сообщения)
Команды имеют разные уровни допусков, и поэтому сначала получаем допуск данного юзера,
а потом заполняем кнопку МЕНЮ подходящими командами
'''

async def load_commands(parent, bot) -> None:
    # получаю из БД все команды
    data = await parent.db_manager.get_data(query=f"SELECT name, discription_ru FROM commands")
    # Список пользовательских команд
    commands = []
    for command in data:
        commands.append(types.BotCommand(command=f"{command[0]}", description=f"{command[1]}"))
    # присваиваю команды из списка в меню
    await bot.set_my_commands(commands)
