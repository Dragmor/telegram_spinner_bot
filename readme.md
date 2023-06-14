Установка зависимостей

Для установки всех необходимых зависимостей из файла requirements.txt используйте команду: 
pip install -r requirements.txt


Запуск бота

Для запуска бота необходимо передать значения следующих переменных окружения: TOKEN, USER, PASSWORD, HOST, PORT, DATABASE.

Пример настройки переменных окружения для Windows bat-файла, через который можно запустить скрипт:

    @echo off

    cd project_files

    set TOKEN=your_bot_token

    set USER=MySQL_username

    set PASSWORD=MySQL_password

    set HOST=MySQL_host

    set PORT=MySQL_port

    set DATABASE=MySQL_database_name

    %~dp0\project_files\main.py -logging

    pause

Этот скрипт запустит бота, передав ему в переменных окружения нужные значения.

В командной строке можно указывать параметры запуска:

    -logging -> включает режим логирования (выводятся логи в файл и в консоль)
