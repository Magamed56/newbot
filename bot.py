import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

# Данные для лекций
LECTURE_TOPICS = {
    "Введение в Python": "📚 **Введение в Python**\nPython — это мощный, простой в изучении язык программирования.",
    "Переменные и типы данных": "📚 **Переменные и типы данных**\nРассматриваем основные типы данных в Python.",
    "Условные конструкции": "📚 **Условные конструкции**\nКак использовать `if`, `elif`, `else` в Python.",
}

# Данные для лабораторных
LAB_TOPICS = {
    "Установка Python": "🛠 **Установка Python и настройка среды**\nГде скачать Python и как его установить.",
    "Простые программы": "🛠 **Простые программы на Python**\nПишем первые программы с `print()` и `input()`.",
    "Работа со строками": "🛠 **Работа со строками и списками**\nУчимся манипулировать данными в Python.",
}
CRC_TOPICS = {
    "Ljas": "🛠 **Установка Python и настройка среды**\nГде скачать Python и как его установить.",
    "Простые программы": "🛠 **Простые программы на Python**\nПишем первые программы с `print()` и `input()`.",
    "Работа со строками": "🛠 **Работа со строками и списками**\nУчимся манипулировать данными в Python.",
}
# Главное меню с кнопками
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("📚 Лекционные темы"), KeyboardButton("🛠 Лабораторные темы"),KeyboardButton("🛠 СРС темы")]
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
    
    elif text == "🛠 СРС Темы":
        keyboard = [[KeyboardButton(topic)] for topic in CRC_TOPICS.keys()]
        keyboard.append([KeyboardButton("⬅ Назад")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🛠 Выберите СРС тему:", reply_markup=reply_markup)

    elif text in LECTURE_TOPICS:
        await update.message.reply_text(LECTURE_TOPICS[text])

    elif text in LAB_TOPICS:
        await update.message.reply_text(LAB_TOPICS[text])
    elif text in CRC_TOPICS:
        await update.message.reply_text(CRC_TOPICS[text])

    elif text == "⬅ Назад":
        await start(update, context)

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()


