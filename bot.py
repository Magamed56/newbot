import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

# Данные для кнопок
LECTURE_TOPICS = [
    "1. Введение в Python",
    "2. Переменные и типы данных",
    "3. Условные конструкции",
    "4. Циклы",
    "5. Функции",
    "6. Работа с файлами",
]

LAB_TOPICS = [
    "1. Установка Python и настройка среды",
    "2. Простые программы на Python",
    "3. Работа со строками и списками",
    "4. Написание функций",
    "5. Основы ООП",
    "6. Работа с БД (SQLite)",
]

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

    if query.data == "lectures":
        text = "📚 **Лекционные темы:**\n\n" + "\n".join(LECTURE_TOPICS)
    elif query.data == "labs":
        text = "🛠 **Лабораторные работы:**\n\n" + "\n".join(LAB_TOPICS)
    else:
        text = "Ошибка: неизвестная команда."

    await query.edit_message_text(text=text)

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
