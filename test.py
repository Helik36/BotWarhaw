from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import configparser
import logging

config = configparser.ConfigParser()
config.read("config.ini")

logging.basicConfig(
            format="\n[%(asctime)s]: %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
            level=logging.INFO)


TOKEN_BOT = config["api_token"]["api_TOKEN"]
ADMIN_ID = config['ADMIN_ID']["my_id"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


app = ApplicationBuilder().token(TOKEN_BOT).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()