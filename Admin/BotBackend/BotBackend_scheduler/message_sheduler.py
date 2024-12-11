
from telegram import Update
from telegram.ext import Application, ContextTypes



async def scheduler_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""

    job = context.job

    await context.bot.send_message(job.chat_id, text="Отложенное сообщение")

