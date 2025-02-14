import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

# Данные для лекций с файлами
LECTURE_TOPICS = {
    "Введение в Python": {
        "text": "📚 **Введение в Python**\nPython — это мощный, простой в изучении язык программирования.",
        "file": "files/3.docx",
    },
    "Переменные и типы данных": {
        "text": "📚 **Переменные и типы данных**\nРассматриваем основные типы данных в Python.",
        "file": "files/4.docx",
    },
  
}

# Данные для лабораторных
LAB_TOPICS = {
    "Установка Python": {
        "text": "🛠 **Установка Python и настройка среды**\nГде скачать Python и как его установить.",
        "file": "files/2.docx",
    },
    "Простые программы": {
        "text": "🛠 **Простые программы на Python**\nПишем первые программы с `print()` и `input()`.",
        "file": "files/3.pptx",
    },
    
}

# Главное меню с кнопками
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📚 Лекционные темы"), KeyboardButton("🛠 Лабораторные темы")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Обработчик выбора раздела
async def menu_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "📚 Лекционные темы":
        keyboard = [[KeyboardButton(topic)] for topic in LECTURE_TOPICS.keys()]
        keyboard.append([KeyboardButton("⬅ Назад")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📚 Выберите лекционную тему:", reply_markup=reply_markup)

    elif text == "🛠 Лабораторные темы":
        keyboard = [[KeyboardButton(topic)] for topic in LAB_TOPICS.keys()]
        keyboard.append([KeyboardButton("⬅ Назад")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🛠 Выберите лабораторную тему:", reply_markup=reply_markup)

    elif text in LECTURE_TOPICS:
        topic = LECTURE_TOPICS[text]
        file_path = topic["file"]

        keyboard = [[InlineKeyboardButton("📂 Скачать материал", callback_data=f"download:{file_path}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(topic["text"], reply_markup=reply_markup)

    elif text in LAB_TOPICS:
        topic = LAB_TOPICS[text]
        file_path = topic["file"]

        keyboard = [[InlineKeyboardButton("📂 Скачать материал", callback_data=f"download:{file_path}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(topic["text"], reply_markup=reply_markup)

    elif text == "⬅ Назад":
        await start(update, context)

# Обработчик скачивания файлов
async def download_file(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    file_path = query.data.split(":")[1]

    if os.path.exists(file_path):
        await query.message.reply_document(InputFile(file_path))
    else:
        await query.message.reply_text("⚠ Файл не найден.")

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
app.add_handler(CallbackQueryHandler(download_file))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()


