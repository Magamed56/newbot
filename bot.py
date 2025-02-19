import os
import pandas as pd
import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# ID твоей Google Таблицы
SPREADSHEET_ID = "1s1F-DONBzaYH8n1JmQmuWS5Z1HW4lH4cz1Vl5wXSqyw"

# Функция загрузки данных из Google Sheets
def get_tasks(task_type):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(url)  # Загружаем таблицу

    today = datetime.date.today()
    tasks = []

    for _, row in df.iterrows():
        if row["Тип"] == task_type:
            unlock_date = datetime.datetime.strptime(row["Дата разблокировки"], "%Y-%m-%d").date()
            days_left = (unlock_date - today).days

            if days_left > 0:
                tasks.append(f"⏳ {row['Название']} будет доступно через {days_left} дней.")
            else:
                tasks.append(f"📌 *{row['Название']}*\n{row['Описание']}\n[Ссылка]({row['Ссылка']})")

    return "\n\n".join(tasks) if tasks else "Нет доступных тем."

# Функция старта
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📚 Лекционные темы")],
        [KeyboardButton("🛠 Лабораторные работы")],
        [KeyboardButton("⬅ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Функция отправки лекций
async def send_lectures(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(get_tasks("Лекция"), parse_mode="Markdown")

# Функция отправки лабораторных
async def send_labs(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(get_tasks("Лабораторная"), parse_mode="Markdown")

# Запуск бота
app = Application.builder().token(os.getenv("TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📚 Лекционные темы"), send_lectures))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛠 Лабораторные работы"), send_labs))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()



