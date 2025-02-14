import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

TOKEN = "8088305768:AAEOB7f893L-57dADMyAh32gTApX8iPgFY8"

# Подключение к базе данных
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT)")
conn.commit()

# Состояния для диалога
ADDING = 1

# Клавиатура
keyboard = [["Лекционная тема", "Показать темы"]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def add_data(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите данные для сохранения:")
    return ADDING

async def save_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    cursor.execute("INSERT INTO messages (user_id, text) VALUES (?, ?)", (user_id, text))
    conn.commit()

    await update.message.reply_text("Данные сохранены!", reply_markup=reply_markup)
    return ConversationHandler.END

async def get_messages(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    cursor.execute("SELECT text FROM messages WHERE user_id=?", (user_id,))
    messages = cursor.fetchall()

    if messages:
        response = "\n".join([msg[0] for msg in messages])
    else:
        response = "У вас нет сохранённых данных."

    await update.message.reply_text(response, reply_markup=reply_markup)

app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Лекционная тема$"), add_data)],
    states={ADDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_data)]},
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("^Показать темы$"), get_messages))
app.add_handler(conv_handler)

app.run_polling()
