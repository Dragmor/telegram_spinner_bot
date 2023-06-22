# модуль для получения значений настроек из БД

async def get_value(db_manager, option):
	# возвращает значение option из таблицы settings
	if (value:= await db_manager.get_data(query=f'''SELECT value FROM settings WHERE name="{option}"''')) != None:
		return value[0][0]
	return None
