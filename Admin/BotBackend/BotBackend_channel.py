import telegram.error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from Admin.database.actionWithDB.actionWithChannelDB import append_in_db_channel, del_from_db_channel
from Admin.database.actionWithDB.general_query import get_from_db_data

BUTTON, BACK = range(2)

async def get_channel():

    channel = "channels"

    channels = await get_from_db_data(channel)
    tempalte = ""

    count = 1
    for i, j in channels.items():
        tempalte += f"{count}) {j}\n"
        count += 1

    return tempalte

# Просмотр каналов
async def handler_view_channel(update, context):

    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    current_channel = await get_channel()

    await query.edit_message_text(f"Текущие каналы:\n\n{current_channel}", reply_markup=reply_markup)

# Добавление каналов
async def handler_add_channel(update, context):

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user_input = int("-100" + update.message.text)

    try:
        data_channel = await context.bot.get_chat(chat_id=user_input)
        nameGroup = data_channel.title

        channel = {user_input: nameGroup}

    except telegram.error.BadRequest:

        await update.message.reply_text("Возникла проблема, группа не найден", reply_markup=reply_markup)
        raise telegram.error.BadRequest


    try:
        await append_in_db_channel(channel)

        current_channel = await get_channel()

        await update.message.reply_text(f"Канал `{nameGroup}` добавлен. Текущие каналы:\n\n{current_channel}")
        return ConversationHandler.END

    except:
        await update.message.reply_text("Возникла проблема при добавлении названия в БД. Обратитесть к админу бота")

    return BACK


# Удаление каналов
async def handler_delete_channel(update, context):

    user_input = update.message.text

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await del_from_db_channel(user_input)

        current_channel = await get_channel()

        await update.message.reply_text(f"Канал `{user_input}` удалён. Текущие каналы:\n\n{current_channel}",
                                        reply_markup=reply_markup)
    except:
        await update.message.reply_text("Такой канал отсутствует", reply_markup=reply_markup)

    return BACK
