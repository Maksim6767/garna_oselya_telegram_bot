import telebot
import sqlite3
import base64

from decouple import config

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def create_tables():
    conn = sqlite3.connect("user_data.db")
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


# Добавление новой таблицы для черного списка в базу данных
def create_blacklist_table():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS blacklist (
                        user_id INTEGER PRIMARY KEY
                    )"""
    )

    conn.commit()
    conn.close()


def get_num_registered_users():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()

    num_users = len(user_ids)

    conn.close()

    return num_users


def get_user_ids():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    conn.close()

    return [user_id[0] for user_id in user_ids]


def get_all_users_info():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    all_users_info = cursor.fetchall()

    conn.close()

    return all_users_info


def get_column_names():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    conn.close()

    return column_names
