import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем объект бота
app = Application.builder().token(TOKEN).build()

keyboard = [["Лекционная тема"]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Я твой Telegram-бот.", reply_markup=reply_markup)
  
# Команда /tema  
async def tema(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('1-Тема')
# Эхо-ответ на сообщения
async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.message.text)


# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("Лекционная тема", tema))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
