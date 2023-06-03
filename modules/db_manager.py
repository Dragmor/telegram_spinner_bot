import sqlite3

'''
модуль для работы с БД (извлечение данных, внесение записей, редактирование и т.д.)
'''

async def db_query(db_name, query):
    # метод подключается к БД, выполняет запрос, и возвращает кортеж извлечённых данных
    # делаем очередь для обращения к БД из потоков
    while True:
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            # выполняем SQL-запрос в БД
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except sqlite3.OperationalError:
            # ждём, пока БД станет доступной
            await asyncio.sleep(0.1)
            