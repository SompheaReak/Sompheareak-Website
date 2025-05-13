from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Function to handle /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    await update.message.reply_text(f"Hello {name}! Welcome to Somphea Reak Shop.")

# Start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
