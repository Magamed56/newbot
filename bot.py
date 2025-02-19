import os
import pandas as pd
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, filters

# ID таблицы
SPREADSHEET_ID = "1AbCDEfgHIjKlMNO-PQrsTUVWXYZ"

# Функция загрузки данных
def get_tasks(task_type):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(url)  # Загружаем таблицу

    today = datetime.date.today()
    tasks = {}

    for _, row in df.iterrows():
        if row["Тип"] == task_type:
            unlock_date = datetime.datetime.strptime(row["Дата разблокировки"], "%Y-%m-%d").date()
            days_left = (unlock_date - today).days

            tasks[row["Название"]] = {
                "description": row["Описание"],
                "link": row["Ссылка"],
                "unlock_date": unlock_date,
                "days_left": days_left
            }

    return tasks

# Стартовое меню
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("📚 Лекционные темы", callback_data="lectures")],
        [InlineKeyboardButton("🛠 Лабораторные работы", callback_data="labs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Показывает список тем
async def show_topics(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task_type = "Лекция" if query.data == "lectures" else "Лабораторная"
    tasks = get_tasks(task_type)

    if not tasks:
        await query.message.edit_text("Нет доступных тем.")
        return

    keyboard = []
    for name, details in tasks.items():
        text = f"{name} (⏳ {details['days_left']} дней)" if details["days_left"] > 0 else name
        keyboard.append([InlineKeyboardButton(text, callback_data=f"task_{name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"📜 {task_type}:", reply_markup=reply_markup)

# Показывает выбранную тему
async def show_task(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task_name = query.data.replace("task_", "")
    
    tasks = get_tasks("Лекция") | get_tasks("Лабораторная")  # Объединяем лекции и лабораторные
    task = tasks.get(task_name)

    if not task:
        await query.answer("Тема не найдена.")
        return

    if task["days_left"] > 0:
        await query.answer(f"⏳ Доступно через {task['days_left']} дней.")
    else:
        text = f"📌 *{task_name}*\n{task['description']}\n[Ссылка]({task['link']})"
        await query.message.edit_text(text, parse_mode="Markdown")

# Настройка бота
app = Application.builder().token(os.getenv("TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(show_topics, pattern="^(lectures|labs)$"))
app.add_handler(CallbackQueryHandler(show_task, pattern="^task_"))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()




