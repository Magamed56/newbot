import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

# Данные для лекций и файлы к ним
LECTURE_TOPICS = {
    "Введение в Python": {
        "description": "📚 **Введение в Python**\nPython — это мощный, простой в изучении язык программирования.",
        "file": "./files/4.docx"
    },
    "Переменные и типы данных": {
        "description": "📚 **Переменные и типы данных**\nРассматриваем основные типы данных в Python.",
        "file": "./files/4.docx"
    },
}

# Данные для лабораторных и файлы к ним
LAB_TOPICS = {
    "Установка Python": {
        "description": "🛠 **Установка Python и настройка среды**\nГде скачать Python и как его установить.",
        "file": "./files/4.docx"
    },
    "Простые программы": {
        "description": "🛠 **Простые программы на Python**\nПишем первые программы с `print()` и `input()`.",
        "file": "./files/4.docx"
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
        lecture = LECTURE_TOPICS[text]
        keyboard = [[KeyboardButton(f"📂 Скачать {text}")], [KeyboardButton("⬅ Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(lecture["description"], reply_markup=reply_markup)

    elif text in LAB_TOPICS:
        lab = LAB_TOPICS[text]
        keyboard = [[KeyboardButton(f"📂 Скачать {text}")], [KeyboardButton("⬅ Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(lab["description"], reply_markup=reply_markup)

    elif text.startswith("📂 Скачать"):
        topic = text.replace("📂 Скачать ", "")
        if topic in LECTURE_TOPICS:
            file_path = LECTURE_TOPICS[topic]["file"]
        elif topic in LAB_TOPICS:
            file_path = LAB_TOPICS[topic]["file"]
        else:
            await update.message.reply_text("⚠ Файл не найден.")
            return

        if os.path.exists(file_path):
            await update.message.reply_document(InputFile(file_path))
        else:
            await update.message.reply_text("⚠ Файл не найден.")

    elif text == "⬅ Назад":
        await start(update, context)

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()


