import datetime # для работы с текущей датой (например, для записи даты регистрации юзера)


'''
модуль проверяет, есть-ли данный юзер в БД. Если нет, то добавляет новую
запись в таблицу users с дефолтнами значениями (кроме ids, tg)
'''

async def check_user(db_manager, message:dict) -> bool:
	username = message['chat']['username']
	user_id = message['chat']['id']

	# # FOR DEBUG
	# print(f"USERNAME={username}, ID={user_id}")

	# если юзера нет в БД, то регистрируем (создаём запись в таблице users)
	if await is_user_exists(db_manager, user_id) == False:
		# получаем текущую дату, и формируем строку для записи её в БД в поле (дата регистрации юзера)
		reg_date = datetime.datetime.now().strftime("%Y%m%d")

		# если нет такого юзера, то добавляем его (с дефолтными параметрами)
		await db_manager.write_data(query=f'''INSERT INTO users 
											(
											ids, 
											tg, 
											lang_iso, 
											role, 
											year_of_birth, 
											gender, 
											user_lang, 
											country, 
											ca, 
											cl, 
											cr, 
											cc, 
											reg_date) 
											VALUES (
											{user_id}, 
											'{username}', 
											'1', 
											'5', 
											'0', 
											'0', 
											'0', 
											'0', 
											'0', 
											'0', 
											'0', 
											'0', 
											{reg_date})''')
		return False
	return True

async def check_user_data(parent, message) -> bool:
	# метод проверяет, какие параметры юзера ещё не были указаны (если "0" то не указаны)
	# язык мы не проверяем, т.к. при регистрации по дефолту выставляется eng
	user_id = message['chat']['id']
	# проверяем, есть-ли данный юзер в БД. Если нет - добавляем
	if await check_user(db_manager=parent.db_manager, message=message) == False:
		# выводим кнопки для выбора языка
		await parent.lang_selector.create_buttons(message=message, command_launch=False)
		return False
		
	# проверяем, выбран-ли пол юзера
	if await parent.db_manager.get_data(query=f"SELECT gender FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.gender_selector.create_buttons(message=message, command_launch=False)
		return False

	# проверяем, выбран-ли возраст юзера
	if await parent.db_manager.get_data(query=f"SELECT year_of_birth FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.age_selector.create_buttons(message=message, command_launch=False)
		return False

	# проверяем, выбрана ли локация
	if await parent.db_manager.get_data(query=f"SELECT cl FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.location_selector.create_buttons(message=message, command_launch=False)
		return False

	# проверяем, выбран ли регион
	if await parent.db_manager.get_data(query=f"SELECT cr FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.region_selector.create_buttons(message=message, command_launch=False)
		return False

	# проверяем, выбрана ли страна
	if await parent.db_manager.get_data(query=f"SELECT cc FROM users WHERE ids = {user_id}") == ((0,),):
		await parent.country_selector.create_buttons(message=message, command_launch=False)
		return False

	# если все поля заполнены, то возвращает True
	return True

async def is_user_exists(db_manager, user_id) -> bool:
	# возвращает True если юзер есть в БД, и False в противном случае
	if await db_manager.get_data(query=f"SELECT id FROM users WHERE ids = {user_id}") != None:
		# если такой юзер уже есть в БД
		return True
	else:
		return False
