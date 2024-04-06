import telebot
import sqlite3
from decouple import config
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Contact

from database import (
    get_num_registered_users,
    get_user_ids,
    get_all_users_info,
    get_column_names,
)


TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Определение обработчика команды get_registered_users
def handle_get_registered_users(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        num_users = get_num_registered_users()
        bot.send_message(user_id, f"Кількість зареєстрованих користувачів: {num_users}")
    else:
        bot.send_message(user_id, "У Вас немає доступа до цієї команди.")


def send_message_to_users(bot, user_id):
    if str(user_id) == ADMIN_MY_ID:
        bot.send_message(
            user_id,
            "Введіть повідомлення для розсилки:",
        )

        bot.register_next_step_handler_by_chat_id(
            user_id, process_send_message, user_id
        )
    else:
        bot.send_message(user_id, "У Вас немає доступу до цієї команди.")


def process_send_message(message, admin_user_id):
    message_text = message.text

    user_ids = get_user_ids()

    for target_user_id in user_ids:
        bot.send_message(
            target_user_id, "Повідомлення від адміністратора:\n " + message_text
        )

    bot.send_message(admin_user_id, f"Розсилка успішно завершена!")


# Определение обработчика команды help
def help_command(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        help_text = "Доступні команди:\n"
        help_text += "/start - Початок реєстрації та отримання інформації\n"
        help_text += "/get_registered_users - Кількість зареєстрованих користувачів\n"
        help_text += (
            "/send_message - Розсилка повідомлення зареєстрованим користувачам\n"
        )
        help_text += "/get_all_users - Получити всіх зареєстрованих користувачів\n"
        help_text += "/blacklist_user - Додати користувача в чорний список\n"
        help_text += "/unblacklist_user - Видалити користувача з чорного списка\n"
        help_text += "/help - Вивести цей список команд"

        bot.send_message(user_id, help_text)
    else:
        bot.send_message(user_id, "У Вас немає доступа до цієї команди.")
