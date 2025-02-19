import gspread
import psycopg2
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import os

# Получаем URL подключения к базе данных из переменных окружения (Railway предоставляет это)
DATABASE_URL = os.getenv('postgresql://postgres:LEcsPYdsrVvQaYhsEoNyupPWzsxNkEKd@crossover.proxy.rlwy.net:30056/railway')

# Авторизация для работы с Google Sheets
def authenticate_google_sheets():
    client = gspread.service_account(filename='credentials.json')
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1s1F-DONBzaYH8n1JmQmuWS5Z1HW4lH4cz1Vl5wXSqyw')
    return sheet

# Получаем данные из Google Sheets для Лекций и Лабораторных
def get_lecture_data():
    sheet = authenticate_google_sheets()
    worksheet = sheet.get_worksheet(0)  # Получаем первый лист (можно изменить)
    return worksheet.get_all_records()  # Все записи

def get_lab_data():
    sheet = authenticate_google_sheets()
    worksheet = sheet.get_worksheet(1)  # Получаем второй лист (можно изменить)
    return worksheet.get_all_records()

# Настройка базы данных и таблиц на Railway (PostgreSQL)
def create_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

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

# Добавление темы в базу данных (для СРС)
def add_srs_topic(topic_name):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO srs_topics (topic_name, is_taken) VALUES (%s, %s)", (topic_name, False))
    conn.commit()
    conn.close()

# Получение всех доступных СРС тем
def get_srs_topics():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic_name, user_name, is_taken FROM srs_topics")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("Лекции")],
        [KeyboardButton("Лабораторные")],
        [KeyboardButton("СРС (Django проекты)")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Функция для отображения лекций
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

# Функция для отображения лабораторных заданий
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

# Функция для отображения выбора СРС тем
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

# Функция для выбора СРС темы
async def select_srs_topic(update: Update, context: CallbackContext) -> None:
    selected_topic = update.message.text
    user_name = update.message.from_user.first_name

    # Проверяем, была ли тема уже выбрана
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
app = Application.builder().token("8088305768:AAEOB7f893L-57dADMyAh32gTApX8iPgFY8").build()

# Создание базы данных и таблиц при запуске
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
