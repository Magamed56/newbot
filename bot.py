import os
import pandas as pd
import asyncpg
import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# ID Google Таблицы
SPREADSHEET_ID = "1s1F-DONBzaYH8n1JmQmuWS5Z1HW4lH4cz1Vl5wXSqyw"

# Список тем для СРС
srs_topics = [
    "Блог с возможностью комментариев", "Онлайн-магазин", "Система бронирования", "Веб-сайт для портфолио",
    "Сайт для обмена книгами", "Система управления задачами", "Платформа для опросов", "Форум", "Чат-приложение",
    "Система учёта расходов", "Сайт для отслеживания привычек", "Веб-приложение для планирования путешествий",
    "Сайт для аренды жилья", "Онлайн-курсы с видеоуроками", "Личный дневник", "Социальная сеть",
    "Платформа для фрилансеров", "Система оповещений", "Репозиторий с кодами", "Онлайн-галерея",
    "Сайт для бронирования мероприятий", "Калькулятор кальорий", "Платформа для обмена фотографиями",
    "Веб-сайт для планирования меню", "Система отслеживания здоровья", "Приложение для изучения языков",
    "Сайт для составления резюме", "Онлайн-магазин с персонализированными товарами", "Веб-приложение для организации благотворительных акций",
    "Система автоматического анализа текста", "Сайт для проведения викторин", "Платформа для анализа финансов",
    "Приложение для мониторинга социальных медиа", "Веб-сайт для обсуждения фильмов", "Сайт для организации волонтёрских мероприятий",
    "Платформа для поиска партнёров для стартапов", "Онлайн-курсы по программированию", "Веб-приложение для публикации статей",
    "Приложение для отслеживания привычек в спорте", "Система для отслеживания проектов", "Веб-сайт для обмена рецептами",
    "Платформа для обмена опытом в бизнесе", "Система для бронирования транспортных средств", "Приложение для планирования встреч",
    "Веб-сайт для аналитики продаж", "Онлайн-агрегатор вакансий", "Система для управления библиотекой",
    "Платформа для проверки знаний", "Веб-приложение для учета коллекций", "Сайт для продажи билетов",
    "Приложение для планирования тренировки", "Система рекомендаций для фильмов", "Платформа для подписки на новости",
    "Веб-сайт для обмена навыками", "Приложение для поиска ресторанов", "Веб-приложение для создания заметок",
    "Платформа для доставки еды", "Система мониторинга доставки", "Сайт для создания мероприятий",
    "Приложение для планирования расходов", "Веб-сайт для организации спортивных турниров", "Система для поиска скидок",
    "Платформа для обмена аудиокнигами", "Онлайн-магазин для продажи сувениров", "Сайт для отслеживания новостей",
    "Платформа для организации совместных покупок", "Веб-приложение для фоторедактирования", "Система для выбора подарков",
    "Приложение для записи аудио", "Сайт для оценки качества товаров", "Платформа для обмена видеоконтентом",
    "Веб-приложение для прогнозов погоды", "Система для создания интерактивных карт", "Сайт для проведения видеоконференций",
    "Онлайн-агрегатор предложений услуг", "Платформа для автоматического создания резюме", "Веб-сайт для публикации стихов",
    "Приложение для анализа текстов", "Система для обмена домашними заданиями", "Веб-сайт для организации фотоконкурсов",
    "Платформа для создания опросников", "Приложение для подсчёта голосов", "Система для расчёта налога на имущество",
    "Сайт для получения информации о здоровье", "Платформа для организации онлайн-курсов по кулинарии"
]

# Подключение к базе данных PostgreSQL
async def create_db():
    conn = await asyncpg.connect(
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        database=os.getenv('PGDATABASE'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS srs_topics (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            user TEXT
        )
    ''')
    await conn.close()

# Функция для добавления/обновления выбранной темы
async def select_topic(topic, user):
    conn = await asyncpg.connect(
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        database=os.getenv('PGDATABASE'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )

    result = await conn.fetch("SELECT * FROM srs_topics WHERE name = $1", topic)
    
    if result:
        # Обновляем выбранного пользователя для этой темы
        await conn.execute("UPDATE srs_topics SET user = $1 WHERE name = $2", user, topic)
    else:
        # Если тема не была выбрана ранее, добавляем её
        await conn.execute("INSERT INTO srs_topics (name, user) VALUES ($1, $2)", topic, user)

    await conn.close()

# Функция для получения всех выбранных тем
async def get_selected_topics():
    conn = await asyncpg.connect(
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        database=os.getenv('PGDATABASE'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )
    
    rows = await conn.fetch("SELECT name, user FROM srs_topics")
    await conn.close()
    return rows

# Функция отображения тем СРС
async def show_srs_topics(update: Update, context: CallbackContext) -> None:
    keyboard = []
    
    for topic in srs_topics:
        # Проверим, есть ли уже кто-то, кто выбрал эту тему
        selected_topics = await get_selected_topics()
        selected_by = next((item['user'] for item in selected_topics if item['name'] == topic), "Свободно")
        
        if selected_by == "Свободно":
            keyboard.append([KeyboardButton(f"{topic} (Свободно)")])
        else:
            keyboard.append([KeyboardButton(f"{topic} (Выбрано: {selected_by})")])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите тему СРС:", reply_markup=reply_markup)

# Функция для обработки выбора темы СРС
async def select_srs_topic(update: Update, context: CallbackContext) -> None:
    topic = update.message.text.replace(" (Свободно)", "").replace(" (Выбрано: ", "").replace(")", "")
    
    # Проверяем, свободна ли тема
    selected_topics = await get_selected_topics()
    selected_by = next((item['user'] for item in selected_topics if item['name'] == topic), None)
    
    if selected_by is None:
        # Если тема свободна, сохраняем её как выбранную для текущего пользователя
        await select_topic(topic, update.message.from_user.username)
        await update.message.reply_text(f"Вы выбрали тему: {topic}")
    else:
        # Если уже выбран другой пользователь
        await update.message.reply_text(f"Эта тема уже выбрана пользователем: {selected_by}. Вы можете выбрать другую.")

# Главное меню
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📚 Лекционные темы"), KeyboardButton("🛠 Лабораторные работы")],
        [KeyboardButton("📚 СРС")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Показывает список тем для лекций и лабораторных
async def show_topics(update: Update, context: CallbackContext) -> None:
    task_type = "Лекция" if update.message.text == "📚 Лекционные темы" else "Лабораторная"
    tasks = get_tasks(task_type)

    if not tasks:
        await update.message.reply_text("Нет доступных тем.")
        return

    keyboard = []
    for name, details in tasks.items():
        text = f"{name} (⏳ {details['days_left']} дн.)" if details["days_left"] > 0 else name
        keyboard.append([KeyboardButton(text)])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"📜 {task_type}:", reply_markup=reply_markup)

# Показывает выбранную тему
async def show_task(update: Update, context: CallbackContext) -> None:
    if update.message.text == "⬅ Назад":
        await start(update, context)
        return

    task_name = update.message.text.replace(" (⏳", "").split(" дн.)")[0]  # Убираем таймер из кнопки
    tasks = get_tasks("Лекция") | get_tasks("Лабораторная")  # Объединяем лекции и лабораторные
    task = tasks.get(task_name)

    if not task:
        await update.message.reply_text("Тема не найдена.")
        return

    if task["days_left"] > 0:
        await update.message.reply_text(
            f"⛔ Тема \"{task_name}\" пока недоступна.\n"
            f"📅 Она откроется {task['unlock_date']} (через {task['days_left']} дней)."
        )
    else:
        text = f"📌 *{task_name}*\n{task['description']}\n[Ссылка]({task['link']})"
        await update.message.reply_text(text, parse_mode="Markdown")

# Настройка бота
app = Application.builder().token(os.getenv("TOKEN")).build()

# Создаем базу данных, если она не существует
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📚 Лекционные темы|🛠 Лабораторные работы"), show_topics))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📚 СРС"), show_srs_topics))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅ Назад"), start))
app.add_handler(MessageHandler(filters.TEXT, show_task))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(".*"), select_srs_topic))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()


