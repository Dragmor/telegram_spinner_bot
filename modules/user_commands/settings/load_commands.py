from aiogram import types
'''
метод загружает в бота команды из БД
'''

async def load_commands(parent, bot) -> None:

    data = await parent.db_manager.get_data(query=f"SELECT name, discription_ru FROM commands")
    # Список пользовательских команд
    commands = []
    for command in data:
        commands.append(types.BotCommand(command=f"{command[0]}", description=f"{command[1]}"))
    # присваиваю команды из списка в меню
    await bot.set_my_commands(commands)
