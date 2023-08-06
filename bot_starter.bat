@echo off
cd project_files
rem тут мы объявляем переменные, которые передаются в скрипт
set TOKEN=<ТОКЕН_ТГ_БОТА>
set USER=<ИМЯ_ПОЛЬЗОВАТЕЛЯ_БД_MYSQL>
set PASSWORD=<ПАРОЛЬ_ПОЛЬЗОВАТЕЛЯ_БД_MYSQL>
set HOST=<IP_АДРЕС_БД_MYSQL>
set PORT=<ПОРТ_БД_MYSQL>
set DATABASE=<ИМЯ_БД_MYSQL_(по_дефолту_"spinner")>
rem запуск скрипта
%~dp0\main.py
pause