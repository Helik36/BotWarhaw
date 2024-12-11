import logging

import telegram
from telegram.ext import ConversationHandler

from Admin.database.actionWithDB.actionWithChannelDB import append_in_db_channel

# Добавление канала через выозова бота в канале
async def handler_add_channel_from_message_in_channel(update, context):

    nameg_group = update.message.chat.title
    super_grupId = update.message.chat.id

    channel = {super_grupId: nameg_group}

    try:
        await context.bot.get_chat(chat_id=super_grupId)

    except telegram.error.BadRequest:

        await update.message.reply_text("Ошибка при добавлении канала.")

        logging.info(update)
        raise telegram.error.BadRequest

    try:
        await append_in_db_channel(channel)

        await update.message.reply_text(f"Канал `{nameg_group}` добавлен.")
        return ConversationHandler.END

    except:
        await update.message.reply_text("Возникла проблема при добавлении названия в БД. Обратитесть к админу Бота")