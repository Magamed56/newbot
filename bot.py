import os
import pandas as pd
import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# ID Google Таблицы
SPREADSHEET_ID = "1s1F-DONBzaYH8n1JmQmuWS5Z1HW4lH4cz1Vl5wXSqyw"

# Хранение выборов тем СРС
selected_srs = {}

# Функция загрузки данных из таблицы
def get_tasks(task_type):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    
    try:
        df = pd.read_csv(url)  # Загружаем таблицу
    except Exception as e:
        print(f"Ошибка загрузки таблицы: {e}")
        return {}

    today = datetime.date.today()
    tasks = {}

    for _, row in df.iterrows():
        if str(row.get("Тип", "")).strip() == task_type:
            unlock_date_str = str(row.get("Дата разблокировки", "")).strip()

            try:
                unlock_date = datetime.datetime.strptime(unlock_date_str, "%Y-%m-%d").date()
                days_left = (unlock_date - today).days
            except ValueError:
                continue  # Пропустить, если дата неправильная

            tasks[row["Название"]] = {
                "description": row.get("Описание", "Нет описания"),
                "link": row.get("Ссылка", "#"),
                "unlock_date": unlock_date,
                "days_left": days_left
            }

    return tasks

# Главное меню
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📚 Лекционные темы"), KeyboardButton("🛠 Лабораторные работы")],
        [KeyboardButton("СРС (Django проекты)")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Показывает список тем
async def show_topics(update: Update, context: CallbackContext) -> None:
    task_type = "Лекция" if update.message.text == "📚 Лекционные темы" else "Лабораторная" if update.message.text == "🛠 Лабораторные работы" else "СРС"
    if task_type == "СРС":
        tasks = get_srs_tasks()
        await show_srs_topics(update, tasks)
        return
    
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

# Получить список тем для СРС
def get_srs_tasks():
    srs_tasks = {
        f"Тема {i+1} Django": "" for i in range(85)
    }
    return srs_tasks

# Показывает темы для СРС
async def show_srs_topics(update: Update, tasks: dict) -> None:
    keyboard = []
    for name, selected_by in tasks.items():
        text = f"{name} - (Выбрано: {selected_by})" if selected_by else name
        keyboard.append([KeyboardButton(text)])

    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите тему для СРС:", reply_markup=reply_markup)

# Выбор темы для СРС
async def select_srs_topic(update: Update, context: CallbackContext) -> None:
    if update.message.text == "⬅ Назад":
        await start(update, context)
        return

    selected_topic = update.message.text
    user_name = update.message.from_user.first_name

    # Проверяем, была ли тема уже выбрана
    if selected_topic in selected_srs and selected_srs[selected_topic]:
        await update.message.reply_text(f"Тема \"{selected_topic}\" уже выбрана пользователем {selected_srs[selected_topic]}.")
    else:
        # Если тема не выбрана, то записываем пользователя
        selected_srs[selected_topic] = user_name
        await update.message.reply_text(f"Вы выбрали тему: \"{selected_topic}\". Вы можете теперь продолжить работу.")

    # Показываем обновленный список
    await show_srs_topics(update, selected_srs)

# Настройка бота
app = Application.builder().token(os.getenv("TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📚 Лекционные темы|🛠 Лабораторные работы|СРС (Django проекты)"), show_topics))
app.add_handler(MessageHandler(filters.TEXT, select_srs_topic))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
