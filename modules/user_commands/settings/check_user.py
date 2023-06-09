'''
модуль проверяет, есть-ли данный юзер в БД. Если нет, то добавляет новую
запись в таблицу users с дефолтнами значениями (кроме ids, tg)
'''
async def check(db_manager, username ,user_id):
	if await db_manager.get_data(query=f"SELECT id FROM users WHERE ids = {user_id}") != None:
		# если такой юзер уже есть в БД
		return True
	else:
		# если нет такого юзера, то добавляем его (с дефолтными параметрами)
		await db_manager.write_data(query=f'''INSERT INTO users 
											(ids, tg, iso, role, age, gender, lang, country, ca, cl, cr, cc) 
											VALUES ({user_id}, '{username}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0')''')
		return False