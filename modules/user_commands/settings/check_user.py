from modules.imports import *

'''
модуль проверяет, есть-ли данный юзер в БД. Если нет, то добавляет новую
запись в таблицу users с дефолтнами значениями (кроме ids, tg)
'''

async def check_user(db_manager, username:str, user_id:int) -> bool:
	# если юзера нет в БД, то регистрируем (создаём запись в таблице users)
	if not await is_user_exists(db_manager, user_id):
		# получаем текущую дату, и формируем строку для записи её в БД в поле (дата регистрации юзера)
		reg_date = datetime.datetime.now().strftime("%Y%m%d")

		# если нет такого юзера, то добавляем его (с дефолтными параметрами)
		await db_manager.write_data(query=f'''INSERT INTO users 
											(ids, tg, iso, role, age, gender, lang, country, ca, cl, cr, cc, reg_date) 
											VALUES ({user_id}, '{username}', 'eng', '5', '0', '0', '0', '0', '0', '0', '0', '0', {reg_date})''')
		return False
	return True

async def check_user_data(parent, user_id:int, message) -> bool:
	# метод проверяет, какие параметры юзера ещё не были указаны (если "0" то не указаны)
	# язык мы не проверяем, т.к. при регистрации по дефолту выставляется eng

	# проверяем, есть-ли данный юзер в БД. Если нет - добавляем
	if await modules.user_commands.settings.check_user.check_user(db_manager=parent.db_manager, username=message['from']['username'], user_id=user_id) == False:
		# выводим кнопки для выбора языка
		await parent.lang_selector.create_buttons(message=message, command_launch=False)
		return False
		
	# проверяем, выбран-ли пол юзера
	if await parent.db_manager.get_data(query=f"SELECT gender FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.gender_selector.create_buttons(message=message, command_launch=False)
		return False

	# если все поля заполнены, то возвращает True
	return True

async def is_user_exists(db_manager, user_id:int =0) -> bool:
	# возвращает True если юзер есть в БД, и False в противном случае
	if await db_manager.get_data(query=f"SELECT id FROM users WHERE ids = {user_id}") != None:
		# если такой юзер уже есть в БД
		return True
	else:
		return False
