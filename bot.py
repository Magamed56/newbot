import gspread
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import psycopg2
import os

# Подключение к базе данных PostgreSQL (из Railway)
DATABASE_URL = os.getenv('DATABASE_URL')

# Функция для подключения к Google Sheets
def authenticate_google_sheets():
    # Убедитесь, что у вас есть общедоступная ссылка на Google Sheets
    gc = gspread.service_account(filename='credentials.json')
    sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1s1F-DONBzaYH8n1JmQmuWS5Z1HW4lH4cz1Vl5wXSqyw/edit?usp=sharing')
    return sheet

# Функция для получения данных лекций
def get_lecture_data():
    sheet = authenticate_google_sheets()
    worksheet = sheet.get_worksheet(0)  # Первый лист с лекциями
    return worksheet.get_all_records()

# Функция для получения данных лабораторных
def get_lab_data():
    sheet = authenticate_google_sheets()
    worksheet = sheet.get_worksheet(1)  # Второй лист с лабораторными заданиями
    return worksheet.get_all_records()

# Функция для создания таблицы и базы данных на Railway
def create_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Создаем таблицу для хранения выбранных тем СРС
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS srs_topics (
            id SERIAL PRIMARY KEY,
            topic_name TEXT NOT NULL,
            user_name TEXT,
            is_taken BOOLEAN NOT NULL DEFAULT FALSE
        )
    ''')

    conn.commit()
    conn.close()

# Функция для добавления темы СРС в базу данных
def add_srs_topic(topic_name):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO srs_topics (topic_name, is_taken) VALUES (%s, %s)", (topic_name, False))
    conn.commit()
    conn.close()

# Функция для получения всех доступных СРС тем
def get_srs_topics():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic_name, user_name, is_taken FROM srs_topics")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Команда /start для бота
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("Лекции")],
        [KeyboardButton("Лабораторные")],
        [KeyboardButton("СРС (Django проекты)")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Показать лекции
async def show_lectures(update: Update, context: CallbackContext) -> None:
    lectures = get_lecture_data()
    keyboard = []
    for lecture in lectures:
        topic_name = lecture['Тема']
        available_at = lecture['Дата']
        link = lecture['Ссылка']
        text = f"{topic_name} - Доступна с {available_at} \nСсылка: {link}"
        keyboard.append([KeyboardButton(text)])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите лекцию:", reply_markup=reply_markup)

# Показать лабораторные задания
async def show_labs(update: Update, context: CallbackContext) -> None:
    labs = get_lab_data()
    keyboard = []
    for lab in labs:
        topic_name = lab['Тема']
        available_at = lab['Дата']
        link = lab['Ссылка']
        text = f"{topic_name} - Доступно с {available_at} \nСсылка: {link}"
        keyboard.append([KeyboardButton(text)])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите лабораторное задание:", reply_markup=reply_markup)

# Показать темы СРС
async def show_srs_topics(update: Update, context: CallbackContext) -> None:
    topics = get_srs_topics()
    keyboard = []
    for topic in topics:
        topic_name = topic[1]
        user_name = topic[2] if topic[2] else "Не выбрана"
        text = f"{topic_name} - {user_name}"
        keyboard.append([KeyboardButton(text)])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите тему для СРС:", reply_markup=reply_markup)

# Выбор темы для СРС
async def select_srs_topic(update: Update, context: CallbackContext) -> None:
    selected_topic = update.message.text
    user_name = update.message.from_user.first_name

    # Проверка, была ли тема выбрана
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM srs_topics WHERE topic_name = %s", (selected_topic,))
    row = cursor.fetchone()

    if row and row[3]:  # Проверяем, была ли тема выбрана
        await update.message.reply_text(f"Тема \"{selected_topic}\" уже выбрана пользователем {row[2]}.")
    else:
        cursor.execute("UPDATE srs_topics SET user_name = %s, is_taken = TRUE WHERE topic_name = %s", (user_name, selected_topic))
        conn.commit()
        await update.message.reply_text(f"Вы выбрали тему: \"{selected_topic}\".")
    conn.close()

# Настройка бота
app = Application.builder().token("TOKEN").build()

# Создаем базу данных и таблицы при запуске
create_db()

# Регистрируем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Лекции"), show_lectures))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Лабораторные"), show_labs))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("СРС (Django проекты)"), show_srs_topics))
app.add_handler(MessageHandler(filters.TEXT, select_srs_topic))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
