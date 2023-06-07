import mysql.connector

'''
модуль для работы с БД (извлечение данных, внесение записей, редактирование и т.д.)
Класс реализует управление БД
'''
class DataBaseManager():
    def __init__(self, db_conf):
        # подключаюсь к БД
        self.connect = mysql.connector.connect(**db_conf)

    async def get_data(self, query: str) -> list[(tuple,)]:
        # метод подключается к БД, выполняет запрос, и возвращает кортеж извлечённых данных
        cursor = self.connect.cursor() 
        cursor.execute(query) # выполняем SQL-запрос в БД
        result = cursor.fetchall() # создаём отдельный курсор в каждом вызове метода
        cursor.close()
        return result
                
    def close(self):
        # метод закрывает соединение с БД
        self.connect.close()
