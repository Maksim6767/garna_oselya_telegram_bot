import telebot
import sqlite3
import base64
import re

from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Contact
from decouple import config
from database import (
    create_tables,
    create_blacklist_table,
    get_num_registered_users,
    get_all_users_info,
    get_last_registered_users,
    get_column_names,
)
from handlers import (
    handle_get_registered_users,
    handle_get_all_users,
    handle_get_last_registered_users,
    handle_send_message_to_users,
    process_send_message,
    handle_blacklist_user,
    handle_unblacklist_user,
    handle_get_blacklisted_users,
    help_command,
    handle_start,
)


# Загрузка переменных окружения из файла .env
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_MY_ID = config("ADMIN_MY_ID")
ADMIN_USER_ID = config("ADMIN_USER_ID")
DB_CONNECTION_URL = config("DB_CONNECTION_URL")


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
print(bot)

create_tables()
create_blacklist_table()


# Функция для получения информации о всех пользователях
def get_all_users_info():
    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    all_users_info = cursor.fetchall()

    conn.commit()
    conn.close()

    return all_users_info


# Функция отправки сообщения с клавиатурой
def send_message_with_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=False
    )
    consultation_button = types.KeyboardButton("🔍 Консультація")
    markup.add(consultation_button)
    bot.send_message(
        user_id,
        "Для отримання консультації натисніть, будь ласка, кнопку 'Консультація':",
        reply_markup=markup,
    )
    return markup


# Обработчик ответа на запрос ID пользователя
@bot.message_handler(
    func=lambda message: message.reply_to_message is not None
    and message.reply_to_message.text
    == "Введіть ID користувача для додавання в чорний список:",
    content_types=["text"],
)
def process_user_id(message):
    admin_id = message.chat.id
    try:
        user_id_to_blacklist = message.text  # Получаем ID пользователя из ответа
        # Проверяем, был ли передан user_id
        if user_id_to_blacklist:
            conn = sqlite3.connect(DB_CONNECTION_URL)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO blacklist (user_id) VALUES (?)", (user_id_to_blacklist,)
            )

            conn.commit()
            conn.close()

            bot.send_message(
                admin_id,
                f"Користувача з ID {user_id_to_blacklist} додано в чорний список!",
            )
        else:
            bot.send_message(
                admin_id, "Не вказано ID користувача для додавання в чорний список."
            )
    except Exception as e:
        bot.send_message(
            admin_id,
            f"Користувач з ID {user_id_to_blacklist} вже існує в чорному списку: {e}",
        )


# Обработчик ответа на запрос ID пользователя для удаления из черного списка
@bot.message_handler(
    func=lambda message: message.reply_to_message is not None
    and message.reply_to_message.text
    == "Введіть ID користувача для видалення з чорного списка:",
    content_types=["text"],
)
def process_unblacklist_user(message):
    admin_id = message.chat.id
    try:
        user_id_to_unblacklist = message.text  # Получаем ID пользователя из ответа
        # Удаляем пользователя из черного списка
        conn = sqlite3.connect(DB_CONNECTION_URL)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM blacklist WHERE user_id=?", (user_id_to_unblacklist,)
        )

        conn.commit()
        conn.close()

        bot.send_message(
            admin_id,
            f"Користувача з ID {user_id_to_unblacklist} видалено з чорного списка.",
        )
    except Exception as e:
        bot.send_message(
            admin_id, f"Помилка при видаленні користувача з чорного списка: {e}"
        )


# Функция для проверки, находится ли пользователь в черном списке
def is_user_blacklisted(user_id):
    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM blacklist WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


# Определение обработчика команды get_registered_users
@bot.message_handler(commands=["get_registered_users"])
def get_registered_users(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_get_registered_users(message)


# Определение обработчика команды send_message
@bot.message_handler(commands=["send_message"])
def get_send_message_command(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_send_message_to_users(bot, message.chat.id)


# Определение обработчика команды get_all_users
@bot.message_handler(commands=["get_all_users"])
def get_all_users(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_get_all_users(message)


# Определение обработчика команды get_last_registered_users
@bot.message_handler(commands=["get_last_registered_users"])
def get_last_registered_users(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_get_last_registered_users(message)


# Определение обработчика команды blacklist_user
@bot.message_handler(commands=["blacklist_user"])
def blacklist_user(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_blacklist_user(message)


# Определение обработчика команды unblacklist_user
@bot.message_handler(commands=["unblacklist_user"])
def unblacklist_user(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_unblacklist_user(message)


# Определение обработчика команды blacklisted_users
@bot.message_handler(commands=["blacklisted_users"])
def get_blacklisted_users(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    handle_get_blacklisted_users(message)


# Определение обработчика команды help
@bot.message_handler(commands=["help"])
def handle_help_command(message):
    user_id = message.chat.id
    send_message_with_keyboard(user_id)
    help_command(message)


# Определение обработчика команды start
@bot.message_handler(commands=["start"])
def start(message):
    handle_start(message)


# Функция получения имени
def get_name(message):
    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    if message.text.isalpha() and 2 <= len(message.text) <= 64:
        name = message.text.lower().capitalize().strip()
        # Проверка, зарегистрирован ли пользователь
        user_id = message.chat.id
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            bot.send_message(user_id, "Чудово! Ви вже зареєстровані.")
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
            "Введіть ім'я тільки буквами та довжиною від 2 до 64 літер.",
        )
        bot.register_next_step_handler(message, get_name)


# Функция получения фамилии
def get_surname(message, name):
    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    if message.text.isalpha() and 2 <= len(message.text) <= 64:
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
            "Введіть прізвище тільки буквами та довжиною від 2 до 64 літер.",
        )
        bot.register_next_step_handler(message, get_surname, name)


# Функция склонения лет
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


# Функция получения возраста
def get_age(message, name, surname):
    try:
        conn = sqlite3.connect(DB_CONNECTION_URL)
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


# Функция получения города
def get_city(message, name, surname, age):
    global city

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    city = " ".join(message.text.strip().title().split())

    if city.replace(" ", "").isalpha() and 2 <= len(city) <= 64:
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
            "Будь ласка, введіть назву міста (селища) тільки буквами та довжиною від 2 до 64 літер. Наприклад: Київ.",
        )
        bot.register_next_step_handler(message, get_city, name, surname, age)


# Функция получения района
def get_district(message, name, surname, age, city):
    global district

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    district = " ".join(message.text.strip().title().split())

    if (
        district.replace(" ", "").isalpha()
        and len(district.split()) >= 1
        and 2 <= len(district) <= 64
    ):
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
            "Будь ласка, введіть назву району тільки буквами та довжиною від 2 до 64 літер.",
        )
        bot.register_next_step_handler(message, get_district, name, surname, age, city)


# Функция получения адреса
def get_address(
    message, name, surname, age, city, district, awaiting_confirmation=False
):
    if message is not None:
        conn = sqlite3.connect(DB_CONNECTION_URL)
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

        if address.strip() and len(address.split()) >= 1 and len(address) <= 64:
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
        "Будь ласка, введіть адресу довжиною не більше 64 символів.",
    )
    bot.register_next_step_handler(
        message,
        lambda msg: get_address(msg, name, surname, age, city, district),
    )


# Обработчик нажатия на кнопку "Консультация"
@bot.message_handler(func=lambda message: message.text == "🔍 Консультація")
def consultation(message):
    user_id = message.chat.id

    if is_user_blacklisted(
        user_id
    ):  # Проверяем, не находится ли пользователь в черном списке
        bot.send_message(
            user_id,
            "Ви не можете отримати консультацію.",
        )
        return
    bot.send_message(
        user_id,
        "Тепер відправте свій контактний номер телефона, натиснув нижче кнопку 'Відправити мій контакт'.",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=False,
        ).add(
            KeyboardButton(
                text="📞   Відправити мій контакт",
                request_contact=True,
            )
        ),
    )
    bot.register_next_step_handler(message, get_contact)


registration_status = {}  # Словарь для отслеживания статуса регистрации пользователей


# Обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        conn = sqlite3.connect(DB_CONNECTION_URL)
        cursor = conn.cursor()

        user_id = message.chat.id
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        existing_user = cursor.fetchone()

        # Если сообщение пустое, игнорируем его
        if not message.text:
            return

        # Если пользователь существует
        if existing_user:
            # Если пользователь не подтвердил регистрацию, отправляем сообщение о необходимости подтвердить регистрацию кнопкой "Так"
            if message.text.strip() and not registration_status.get(user_id, False):
                bot.send_message(
                    user_id,
                    "Будь ласка, підтвердіть реєстрацію, натиснувши кнопку 'Так'.",
                    reply_markup=types.ReplyKeyboardMarkup(
                        one_time_keyboard=True,
                        resize_keyboard=True,
                    ).add(types.KeyboardButton("")),
                )
                return

            # Если пользователь не нажал кнопку "Консультация", но отправил текст, отправляем сообщение о необходимости нажать "Консультация"
            if message.text.strip() and not message.text == "🔍 Консультація":
                markup = types.ReplyKeyboardMarkup(
                    row_width=1, resize_keyboard=True, one_time_keyboard=False
                )
                consultation_button = types.KeyboardButton("🔍 Консультація")
                markup.add(consultation_button)
                bot.send_message(
                    user_id,
                    "Спочатку натисніть кнопку 'Консультація', щоб продовжити.",
                    reply_markup=markup,
                )
                return

        # Если пользователь не существует или не подтвердил регистрацию, отправляем сообщение о необходимости регистрации
        if not existing_user or (
            existing_user and not registration_status.get(user_id, False)
        ):
            bot.send_message(
                user_id,
                "Спочатку потрібно зареєструватися. Натисніть кнопку 'Зареєструватися' для продовження.",
            )
            markup = types.ReplyKeyboardMarkup(
                row_width=1, resize_keyboard=True, one_time_keyboard=False
            )
            registration_button = types.KeyboardButton("Зареєструватися")
            markup.add(registration_button)
            bot.send_message(
                user_id,
                "",
                reply_markup=markup,
            )
            return

    except Exception as e:
        print(f"Помилка при обробці текстового повідомлення: {e}")


# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.message.chat.id
    global registration_status

    conn = sqlite3.connect(DB_CONNECTION_URL)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT first_name, last_name, age, city, district, address FROM users WHERE user_id=?",
        (user_id,),
    )
    user_data = cursor.fetchone()

    if user_data:
        name, surname, age, city, district, address = user_data
        if registration_status.get(user_id, False):
            bot.send_message(user_id, "Ви вже зареєстровані!")
            return

        if call.data == "yes":
            bot.send_message(
                call.message.chat.id, "✅ Чудово! Ви успішно зареєстровані!"
            )
            # Добавление кнопки "Консультация" после успешной регистрации
            send_message_with_keyboard(user_id)

            get_num_registered_users()

            registration_status[user_id] = (
                True  # Установка статуса регистрации пользователя
            )
        elif call.data == "no" and not registration_status.get(user_id, False):
            conn = sqlite3.connect(DB_CONNECTION_URL)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))

            conn.commit()
            conn.close()

            bot.send_message(
                user_id,
                "Пройдіть повторну реєстрацію. Натисніть кнопку Зареєструватися",
            )
            start(call.message)
    elif call.data == "registration":
        bot.send_message(
            user_id,
            "Введіть Ваше ім'я. Наприклад, Ілон.",
            reply_markup=types.ReplyKeyboardRemove(),  # Удаление клавиатуры
        )
        bot.register_next_step_handler(call.message, get_name)


# Функция обработки получения контактной информации пользователя
def get_contact(message):
    user_id = message.from_user.id

    if message.contact is not None and message.contact.phone_number:
        user_contact = base64.b64encode(message.contact.phone_number.encode()).decode()

        conn = sqlite3.connect(DB_CONNECTION_URL)
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
        bot.register_next_step_handler(message, get_contact)


# Функция обработки начала консультации
def start_consultation(message):
    user_id = message.from_user.id

    conn = sqlite3.connect(DB_CONNECTION_URL)
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
            f"Користувач {name} {surname} за адресою {address} з ID {user_id} запрошує консультацію. Його контактний номер: {decoded_contact}\n\nПовідомлення:\n\n{consultation_message}",
        )
        bot.send_message(
            user_id,
            "✅ Ваше повідомлення відправлено на консультацію.\nНаш адміністратор зв'яжеться з Вами.",
        )

        send_message_with_keyboard(user_id)
    else:
        bot.send_message(
            user_id, "Ваш контакт відсутній. Будь ласка, відправте свій контакт ще раз."
        )


if __name__ == "__main__":
    print("BOT STARTED")
    bot.polling(non_stop=True, interval=0)
