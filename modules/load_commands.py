from aiogram import types
'''
метод загружает в бота команды из файла
'''

async def load_commands(bot) -> None:
    with open("./settings/commands.txt", 'r') as f:
        data = f.read()
    data = data.split("\n")
    # Список пользовательских команд
    commands = []
    for command in data:
        commands.append(types.BotCommand(command=f"/{command.split(' - ')[0]}", description=f"{command.split(' - ')[1]}"))
    # присваиваю команды из списка в меню
    await bot.set_my_commands(commands)
