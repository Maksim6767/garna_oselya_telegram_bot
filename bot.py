import telebot
import sqlite3
import base64
import re

from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Contact
from decouple import config
from database import (
    create_tables,
    get_num_registered_users,
    get_all_users_info,
    get_column_names,
)
from handlers import (
    # start,
    help_command,
    # handle_text,
    handle_get_registered_users,
    send_message_to_users,
)

# Загрузка переменных окружения из файла .env
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
print(bot)

create_tables()


@bot.message_handler(commands=["help"])
def handle_help_command(message):
    help_command(message)


# Определение обработчика команды get_registered_users
@bot.message_handler(commands=["get_registered_users"])
def get_registered_users(message):
    handle_get_registered_users(message)


@bot.message_handler(commands=["send_message"])
def send_message_to_users(message):
    user_id = message.chat.id

    if str(user_id) == ADMIN_MY_ID:
        bot.send_message(
            user_id,
            "Введіть повідомлення для розсилки:",
        )

        bot.register_next_step_handler(message, process_send_message)
    else:
        bot.send_message(user_id, "У Вас немає доступу до цієї команди.")


def process_send_message(message):
    admin_user_id = message.chat.id
    message_text = message.text

    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    for user_id in user_ids:
        bot.send_message(user_id[0], "Повідомлення від адміністратора: " + message_text)

    conn.close()

    bot.send_message(admin_user_id, f"Розсилка успішно завершена!")


@bot.message_handler(commands=["send_message"])
def get_send_message_command(message):
    send_message_to_users(bot, message.chat.id)


@bot.message_handler(commands=["start"])
def start(message):
    try:
        conn = sqlite3.connect("user_data.db")
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
                markup = types.InlineKeyboardMarkup()
                consultation_button = types.InlineKeyboardButton(
                    "Консультація", callback_data="consultation"
                )
                markup.add(consultation_button)
                bot.send_message(
                    user_id,
                    "Для отримання консультації натисніть кнопку 'Консультація'.",
                    reply_markup=markup,
                )
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


def get_name(message):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    if message.text.isalpha() and len(message.text) >= 2:
        name = message.text.lower().capitalize().strip()
        # Проверка, зарегистрирован ли пользователь
        user_id = message.chat.id
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            bot.send_message(user_id, "Чудово! Ви вже зареєстровані.")

            markup = types.InlineKeyboardMarkup()
            consultation_button = types.InlineKeyboardButton(
                "Консультація", callback_data="consultation"
            )
            markup.add(consultation_button)
            bot.send_message(
                user_id,
                "Для отримання консультації натисніть кнопку 'Консультація'.",
                reply_markup=markup,
            )
            return
        elif existing_user is None:
            cursor.execute(
                "INSERT INTO users (first_name, user_id) VALUES (?, ?)",
                (name, user_id),
            )
            conn.commit()
            conn.close()

        bot.send_message(
            message.chat.id, f"{name}, введіть Ваше прізвище. Наприклад: Маск."
        )
        bot.register_next_step_handler(message, lambda msg: get_surname(msg, name))
    else:
        bot.send_message(
            message.chat.id,
            "Введіть коректне ім'я (мінімум 2 літери, тільки букви).",
        )
        bot.register_next_step_handler(message, get_name)


def get_surname(message, name):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    if message.text.isalpha() and len(message.text) >= 2:
        surname = message.text.lower().capitalize().strip()

        # Обновление фамилии пользователя в базе данных
        user_id = message.chat.id
        cursor.execute(
            "UPDATE users SET last_name=? WHERE user_id=?", (surname, user_id)
        )
        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id, f"{name} {surname}, введіть цифрами скільки Вам років?"
        )
        bot.register_next_step_handler(message, lambda msg: get_age(msg, name, surname))
    else:
        bot.send_message(
            message.chat.id,
            "Введіть правильне прізвище (мінімум 2 букви, тільки букви).",
        )
        bot.register_next_step_handler(message, get_surname, name)


def declination_of_years(age):
    if 5 <= age <= 19:
        return "років"

    last_digit = age % 10
    if last_digit == 1:
        return "рік"
    elif 2 <= last_digit <= 4:
        return "роки"
    else:
        return "років"


def get_age(message, name, surname):
    try:
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        age = int(message.text)

        if 5 <= age <= 100:
            user_id = message.chat.id
            cursor.execute("UPDATE users SET age=? WHERE user_id=?", (age, user_id))
            conn.commit()
            conn.close()

            bot.send_message(
                message.chat.id, "Введіть місто, де Ви мешкаєте. Наприклад: Київ."
            )
            bot.register_next_step_handler(
                message, lambda msg: get_city(msg, name, surname, age)
            )
        else:
            bot.send_message(
                message.chat.id, "Будь ласка, введіть коректний вік від 6 до 100."
            )
            bot.register_next_step_handler(message, get_age, name, surname)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть вік цифрами.")
        bot.register_next_step_handler(message, get_age, name, surname)


def get_city(message, name, surname, age):
    global city

    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    city = " ".join(message.text.strip().title().split())

    if city.replace(" ", "").isalpha() and len(city.split()) >= 1:
        user_id = message.chat.id
        cursor.execute("UPDATE users SET city=? WHERE user_id=?", (city, user_id))
        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id,
            "Введіть район, в якому Ви мешкаєте. Наприклад: Дарницький.",
        )
        bot.register_next_step_handler(
            message, lambda msg: get_district(msg, name, surname, age, city)
        )
    else:
        bot.send_message(
            message.chat.id,
            "Будь ласка, введіть корректну назву міста. Наприклад: Київ.",
        )
        bot.register_next_step_handler(message, get_city, name, surname, age)


def get_district(message, name, surname, age, city):
    global district

    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    district = " ".join(message.text.strip().title().split())

    if district.replace(" ", "").isalpha() and len(district.split()) >= 1:
        user_id = message.chat.id
        cursor.execute(
            "UPDATE users SET district=? WHERE user_id=?", (district, user_id)
        )
        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id,
            "Введіть адресу, за якою Ви проживаєте. Наприклад: вул. Тростянецька 121.",
        )
        bot.register_next_step_handler(
            message, get_address, name, surname, age, city, district
        )
    else:
        bot.send_message(
            message.chat.id,
            "Будь ласка, введіть корректну назву району.",
        )
        bot.register_next_step_handler(message, get_district, name, surname, age, city)


def get_address(
    message, name, surname, age, city, district, awaiting_confirmation=False
):
    if message is not None:
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        user_id = message.chat.id

        if awaiting_confirmation:
            if message.text.strip().lower() == "так":
                # Пользователь подтвердил адрес, сохраняем его в базу
                cursor.execute(
                    "UPDATE users SET address=? WHERE user_id=?",
                    (awaiting_confirmation, user_id),
                )
                conn.commit()
                conn.close()

                bot.send_message(message.chat.id, "Адресу успішно збережено.")
                # Деактивируем кнопку "Ні"
                bot.edit_message_reply_markup(message.chat.id, message.message_id)
            else:
                # Пользователь отказался от адреса, запрашиваем его снова
                bot.send_message(message.chat.id, "Будь ласка, введіть адресу знову.")
                bot.register_next_step_handler(
                    message,
                    lambda msg: get_address(msg, name, surname, age, city, district),
                )
            return

        address = " ".join(message.text.strip().title().split())

        if address.strip() and len(address.split()) >= 1:
            markup = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton("Так", callback_data="yes")
            no_button = types.InlineKeyboardButton(
                "Ні", callback_data="no", callback_game=awaiting_confirmation
            )
            markup.row(yes_button, no_button)

            question = f"Вам {age} {declination_of_years(age)}, Вас звати {name} {surname} і Ви проживаєте за адресою: місто {city}, {district} район, {address}?"

            cursor.execute(
                "UPDATE users SET address=? WHERE user_id=?", (address, user_id)
            )
            conn.commit()
            conn.close()

            bot.send_message(message.chat.id, text=question, reply_markup=markup)
            return

    # Если что-то пошло не так, запрашиваем адрес заново
    bot.send_message(
        message.chat.id,
        "Будь ласка, введіть адресу, щоб продовжити.",
    )
    bot.register_next_step_handler(
        message,
        lambda msg: get_address(msg, name, surname, age, city, district),
    )


registration_status = {}  # Словарь для отслеживания статуса регистрации пользователей


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.message.chat.id
    global registration_status

    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT first_name, last_name, age, city, district, address FROM users WHERE user_id=?",
        (user_id,),
    )
    user_data = cursor.fetchone()

    if user_data:
        name, surname, age, city, district, address = user_data
        if call.data == "yes":
            bot.send_message(
                call.message.chat.id, "✅ Чудово! Ви успішно зареєстровані!"
            )
            get_num_registered_users()

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("Консультація", callback_data="consultation")
            )

            bot.send_message(
                user_id,
                "Для отримання консультації натисніть кнопку 'Консультація'.",
                reply_markup=markup,
            )
            registration_status[user_id] = (
                True  # Установка статуса регистрации пользователя
            )
        elif call.data == "no" and not registration_status.get(user_id, False):
            conn = sqlite3.connect("user_data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()

            bot.send_message(
                user_id,
                "Пройдіть повторну реєстрацію. Натисніть кнопку Зареєструватися",
            )
            start(call.message)
        elif call.data == "consultation":
            bot.send_message(
                user_id,
                "Тепер відправте свій контактний номер телефона, натиснув нижче кнопку 'Відправити мій контакт'.",
                reply_markup=ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ).add(
                    KeyboardButton(
                        text="📞   Відправити мій контакт",
                        request_contact=True,
                    )
                ),
            )
            bot.register_next_step_handler(call.message, get_contact)
    elif call.data == "registration":
        bot.send_message(
            user_id,
            "Введіть Ваше ім'я. Наприклад, Ілон.",
            reply_markup=types.ReplyKeyboardRemove(),  # Удаление клавиатуры
        )

        bot.register_next_step_handler(call.message, get_name)


def get_contact(message):
    user_id = message.from_user.id

    if message.contact is not None and message.contact.phone_number:
        user_contact = base64.b64encode(message.contact.phone_number.encode()).decode()

        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET user_contact=? WHERE user_id=?",
            (user_contact, user_id),
        )
        conn.commit()
        conn.close()

        contact_button_active = True

        markup = types.ReplyKeyboardRemove(selective=False)

        bot.send_message(
            user_id,
            "Тепер введіть Ваше повідомлення для консультації:",
            reply_markup=markup,
        )

        bot.register_next_step_handler(message, start_consultation)
    else:
        bot.send_message(
            user_id,
            "Будь ласка, відправте свій контактний номер. Скористайтеся кнопкою 'Відправити мій контакт'.",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
            ).add(
                KeyboardButton(
                    text="📞   Відправити мій контакт",
                    request_contact=True,
                )
            ),
        )


def start_consultation(message):
    user_id = message.from_user.id

    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT first_name, last_name, age, city, district, address, user_contact FROM users WHERE user_id=?",
        (user_id,),
    )

    user_data = cursor.fetchone()

    if user_data is None:
        return

    name, surname, age, city, district, address, encoded_contact = user_data

    if encoded_contact is not None:
        decoded_contact = base64.b64decode(encoded_contact.encode()).decode()
        print(f"User Contact: {decoded_contact}")

        consultation_message = message.text
        chat_id = int(ADMIN_USER_ID)

        bot.send_message(
            chat_id,
            f"Користувач {name} {surname} запрошує консультацію. Його контактний номер: {decoded_contact}\n\nПовідомлення:\n\n{consultation_message}",
        )
        bot.send_message(user_id, "✅ Ваше повідомлення відправлено на консультацію.")

        bot.send_message(
            user_id,
            "Натисніть кнопку 'Консультація' для продовження спілкування.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Консультація", callback_data="consultation")
            ),
        )
    else:
        bot.send_message(
            user_id, "Ваш контакт відсутній. Будь ласка, відправте свій контакт ще раз."
        )


# Функция для получения информации о всех пользователях
def get_all_users_info():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    all_users_info = cursor.fetchall()

    conn.close()

    return all_users_info


@bot.message_handler(commands=["get_all_users"])
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


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
