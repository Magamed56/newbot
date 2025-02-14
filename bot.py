import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

# Данные для лекций
LECTURE_TOPICS = {
    "lec1": "📚 **Введение в Python**\nPython — это мощный, простой в изучении язык программирования.",
    "lec2": "📚 **Переменные и типы данных**\nРассматриваем основные типы данных в Python.",
    "lec3": "📚 **Условные конструкции**\nКак использовать `if`, `elif`, `else` в Python.",
}

# Данные для лабораторных
LAB_TOPICS = {
    "lab1": "🛠 **Установка Python и настройка среды**\nГде скачать Python и как его установить.",
    "lab2": "🛠 **Простые программы на Python**\nПишем первые программы с `print()` и `input()`.",
    "lab3": "🛠 **Работа со строками и списками**\nУчимся манипулировать данными в Python.",
}

# Главное меню
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("📚 Лекционные темы", callback_data="lectures")],
        [InlineKeyboardButton("🛠 Лабораторные темы", callback_data="labs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# Обработчик кнопок
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Если выбраны лекции
    if query.data == "lectures":
        keyboard = [[InlineKeyboardButton(topic, callback_data=key)] for key, topic in {
            "lec1": "Введение в Python",
            "lec2": "Переменные и типы данных",
            "lec3": "Условные конструкции",
        }.items()]
        keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📚 Выберите лекционную тему:", reply_markup=reply_markup)

    # Если выбраны лабораторные
    elif query.data == "labs":
        keyboard = [[InlineKeyboardButton(topic, callback_data=key)] for key, topic in {
            "lab1": "Установка Python",
            "lab2": "Простые программы",
            "lab3": "Работа со строками",
        }.items()]
        keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🛠 Выберите лабораторную тему:", reply_markup=reply_markup)

    # Если выбрана конкретная тема
    elif query.data in LECTURE_TOPICS:
        await query.edit_message_text(LECTURE_TOPICS[query.data])

    elif query.data in LAB_TOPICS:
        await query.edit_message_text(LAB_TOPICS[query.data])

    # Назад в главное меню
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("📚 Лекционные темы", callback_data="lectures")],
            [InlineKeyboardButton("🛠 Лабораторные темы", callback_data="labs")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите раздел:", reply_markup=reply_markup)

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()

