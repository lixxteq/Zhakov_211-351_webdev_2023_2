from dotenv import load_dotenv
load_dotenv()
from os import getenv

SECRET_KEY = '018b681f-8947-7f04-8cc7-b2cf1ba230ef'
MYSQL_PASSWORD = getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = 'std_2220_lab4'
MYSQL_USER = getenv('MYSQL_USER')
MYSQL_HOST = 'std-mysql.ist.mospolytech.ru'
