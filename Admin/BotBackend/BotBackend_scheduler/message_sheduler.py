from telegram import Update
from telegram.ext import Application, ContextTypes


async def scheduler_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""

    chat_id = context.job.chat_id
    text = context.job.data.get("target_text")
    id_thread = context.job.data.get("topic_id")

    await context.bot.send_message(chat_id=chat_id, text=text, message_thread_id=id_thread)
