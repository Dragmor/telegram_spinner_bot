��������� ������������
��� ��������� ���� ����������� ������������ �� ����� requirements.txt ����������� �������:
pip install -r requirements.txt

������ ����
��� ������� ���� ���������� �������� �������� ��������� ���������� ���������: TOKEN, USER, PASSWORD, HOST, PORT, DATABASE.

������ ��������� ���������� ��������� ��� Windows bat-�����, ����� ������� ����� ��������� ������:

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

���� ������ �������� ����, ������� ��� � ���������� ��������� ������ ��������.

� ��������� ������ ����� ��������� ��������� �������:
    -logging -> �������� ����� ����������� (��������� ���� � ���� � � �������)