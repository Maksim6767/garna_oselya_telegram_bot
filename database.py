import telebot
import sqlite3
import base64

from decouple import config

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")
DB_CONNECTION_URL = config("DB_CONNECTION_URL")

print(DB_CONNECTION_URL)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Cоздание в БД таблицы "users"
def create_tables():
    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            city TEXT,
            district TEXT,
            address TEXT,
            user_id INTEGER,
            user_contact TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def check_db_connection_url():
    if DB_CONNECTION_URL:
        print("Переменная DB_CONNECTION_URL содержит данные:", DB_CONNECTION_URL)
    else:
        print("Переменная DB_CONNECTION_URL не содержит данных или не была найдена в файле.")


# Проверяем наличие данных в переменной DB_CONNECTION_URL
check_db_connection_url()


# Функция добавления в БД новой таблицы для черного списка
def create_blacklist_table():

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS blacklist (
                        user_id INTEGER PRIMARY KEY
                    )"""
    )

    conn.commit()
    conn.close()


# Функция получения_количества_зарегистрированных_пользователей
def get_num_registered_users():

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()

    num_users = len(user_ids)

    conn.close()

    return num_users


# Функция получения_идентификаторов_пользователей
def get_user_ids():

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    conn.close()

    return [user_id[0] for user_id in user_ids]


# Функция получения_всей_информации о пользователях
def get_all_users_info():

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    all_users_info = cursor.fetchall()

    conn.close()

    return all_users_info


#  Функция получения имен столбцов из таблицы "users"
def get_column_names():

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    conn.close()

    return column_names
