import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Try loading .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Function to handle /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    await update.message.reply_text(f"Hello {name}! Welcome to Somphea Reak Shop.")

# Start the bot
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Warning: TELEGRAM_BOT_TOKEN is not set in environment or .env file.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
