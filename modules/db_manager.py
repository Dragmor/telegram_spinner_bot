"""
модуль для работы с БД MySQL
реализует асинхронную работу с БД. Запись и извлечение данных.
Методы получают SQL-запрос для передачи его в БД.
Записи из БД вохвразаются кортежом кортежей ((,),)
"""
import aiomysql

class DataBaseManager():
    # класс для асинхронного управления БД MySQL
    def __init__(self, db_conf: dict):
        # записываю в переменную логин/пароль и т.д. для подключения к БД
        self.db_conf = db_conf

    async def connect(self):
        # подключаюсь к БД (создаю соединение)
        self.pool = await aiomysql.create_pool(**self.db_conf)

    async def get_data(self, query: str) ->  tuple:
        # метод выполняет запрос, и возвращает кортеж кортежей извлечённых данных
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                result = await cur.fetchall()
                # проверяем, были ли извлечены какие-либо данные (если нет, то возвращает None)
                if len(result) == 0:
                    return None
        # если же были извлечены данные, отдаём их
        return result
        

    async def write_data(self, query: str):
        # метод записывает в БД данные, переданные запросом SQL
        # используем менеджер контекста, чтобы не забыть закрыть курсор
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
            await conn.commit()

    async def close(self):
        # метод закрывает соединение с БД
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
