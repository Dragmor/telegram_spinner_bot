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
        with self.connect.cursor() as cursor:
            cursor.execute(query) # выполняем SQL-запрос в БД
            result = cursor.fetchall() # создаём отдельный курсор в каждом вызове метода
            
        # проверяем, были ли извлечены какие-либо данные
        if len(result) == 0: # если нет, то возвращаем None
            return None
        return result

    async def write_data(self, query: str):
        # метод записывает в БД данные, переданные запросом SQL
        # используем менеджер контекста, чтобы не забыть закрыть курсор
        with self.connect.cursor() as cursor:
            cursor.execute(query) # выполняем SQL-запрос в БД
        self.connect.commit() # сохраняем изменения в БД
                
    def close(self):
        # метод закрывает соединение с БД
        self.connect.close()
