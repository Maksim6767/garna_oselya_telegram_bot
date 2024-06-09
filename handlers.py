import telebot
import sqlite3

from decouple import config
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Contact

from database import (
    get_num_registered_users,
    get_user_ids,
    get_all_users_info,
    get_last_registered_users,
    get_column_names,
)


TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")
DB_CONNECTION_URL = config("DB_CONNECTION_URL")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Функция Обработки получения количества зарегистрированных пользователей
def handle_get_registered_users(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        num_users = get_num_registered_users()
        bot.send_message(user_id, f"Кількість зареєстрованих користувачів: {num_users}")
    else:
        bot.send_message(user_id, "У Вас немає доступа до цієї команди.")


# Функция обработки получения информации о всех пользователях
def handle_get_all_users(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        all_users_info = get_all_users_info()

        if all_users_info:

            for user_info in all_users_info:
                (
                    user_id,
                    first_name,
                    last_name,
                    age,
                    city,
                    district,
                    address,
                    user_contact,
                    registration_time,
                    _,
                ) = user_info

                user_info_text = (
                    f"User ID: {user_id}\n"
                    f"Name: {first_name} {last_name}\n"
                    f"Age: {age}\n"
                    f"City: {city}\n"
                    f"District: {district}\n"
                    f"Address: {address}\n"
                    f"User Contact: {user_contact}\n"
                    "------------------------"
                )
                bot.send_message(ADMIN_MY_ID, user_info_text)
        else:
            bot.send_message(user_id, "Немає зареєстрованих користувачів.")
    else:
        bot.send_message(user_id, "У Вас немає доступу до цієї команди.")


# Функция обработки получения информации о последних зарегистрированных пользователях
def handle_get_last_registered_users(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        last_registered_users = get_last_registered_users()
        if last_registered_users:
            for user_info in last_registered_users:
                (
                    user_id,
                    first_name,
                    last_name,
                    age,
                    city,
                    district,
                    address,
                    user_contact,
                    registration_time,
                    _,
                ) = user_info

                user_info_text = (
                    f"User ID: {user_id}\n"
                    f"Name: {first_name} {last_name}\n"
                    f"Age: {age}\n"
                    f"City: {city}\n"
                    f"District: {district}\n"
                    f"Address: {address}\n"
                    f"User Contact: {user_contact}\n"
                    f"Date Created User Contact: {registration_time}\n"
                    "------------------------"
                )
                bot.send_message(ADMIN_MY_ID, user_info_text)
        else:
            bot.send_message(user_id, "Немає зареєстрованих користувачів.")
    else:
        bot.send_message(user_id, "У Вас немає доступу до цієї команди.")


# Функция обработки отправки сообщения пользователям
def handle_send_message_to_users(bot, user_id):
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


# Функция обработки отправки сообщения
def process_send_message(message, admin_user_id):
    message_text = message.text

    user_ids = get_user_ids()

    for target_user_id in user_ids:
        bot.send_message(
            target_user_id, "Повідомлення від адміністратора:\n " + message_text
        )

    bot.send_message(admin_user_id, f"Розсилка успішно завершена!")


# Функция обработки добавления пользователя в черный список
def handle_blacklist_user(message):
    admin_id = message.chat.id
    try:
        # Создаем объект клавиатуры
        markup = types.ForceReply(selective=False)
        # Отправляем сообщение с просьбой ввести ID пользователя
        bot.send_message(
            admin_id,
            "Введіть ID користувача для додавання в чорний список:",
            reply_markup=markup,
        )
    except Exception as e:
        bot.send_message(admin_id, f"Ошибка: {e}")


# Функцмя обработки удаления пользователя из черного списка
def handle_unblacklist_user(message):
    admin_id = message.chat.id
    try:
        # Создаем объект клавиатуры
        markup = types.ForceReply(selective=False)
        # Отправляем сообщение с просьбой ввести ID пользователя
        bot.send_message(
            admin_id,
            "Введіть ID користувача для видалення з чорного списка:",
            reply_markup=markup,
        )
    except Exception as e:
        bot.send_message(admin_id, f"Помилка: {e}")


# Функция обработки получения списка пользователей из черного списка
def handle_get_blacklisted_users(message):
    admin_id = message.chat.id
    try:
        conn = sqlite3.connect(DB_CONNECTION_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM blacklist")

        blacklisted_users = cursor.fetchall()
        conn.close()

        if blacklisted_users:
            users_list = "\n".join(str(user[0]) for user in blacklisted_users)
            bot.send_message(
                admin_id, f"Список користувачів в чорному списку:\n{users_list}"
            )
        else:
            bot.send_message(admin_id, "Чорний список пустий.")
    except sqlite3.Error as e:
        bot.send_message(
            admin_id, f"Помилка при отриманні списка користувачів чорного списка: {e}"
        )


# Функция обработчика команды help
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
        help_text += "/get_last_registered_users - Получити останніх зареєстрованих користувачів\n"
        help_text += "/blacklist_user - Додати користувача в чорний список\n"
        help_text += "/unblacklist_user - Видалити користувача з чорного списка\n"
        help_text += (
            "/blacklisted_users - Отримати всіх користувачів з чорного списка\n"
        )
        help_text += "/help - Вивести цей список команд"

        bot.send_message(user_id, help_text)
    else:
        bot.send_message(user_id, "У Вас немає доступа до цієї команди.")


# Функция обработки команды start
def handle_start(message):
    try:
        conn = sqlite3.connect(DB_CONNECTION_URL)
        cursor = conn.cursor()

        user_id = message.chat.id
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(existing_user)
            if (
                existing_user.first_name
                and existing_user.last_name
                and existing_user.age
                and existing_user.city
                and existing_user.district
                and existing_user.address
            ):
                send_message_with_keyboard(user_id)
            else:
                bot.send_message(
                    message.chat.id,
                    "Спочатку потрібно зареєструватися. Натисніть кнопку 'Зареєструватися' для продовження.",
                )
                return
        else:
            inline_keyboard = types.InlineKeyboardMarkup()
            registration_button = types.InlineKeyboardButton(
                "Зареєструватися", callback_data="registration"
            )
            inline_keyboard.add(registration_button)

            bot.send_message(
                message.chat.id,
                "Привіт!\nЯ Тelegram бот Garna Oselya і я допоможу Вам отримати інформацію з питань відключення, ремонту, технічного обслуговування інженерних мереж опалення, холодного та гарячого водопостачання, водовідведення, електропостачання тощо.\nЩоб отримати консультацію від фахівців, натисніть нижче кнопку 'Зареєструватися'.",
                reply_markup=inline_keyboard,
            )
    except Exception as e:
        print(f"Помилка при обробці команди /start: {e}")