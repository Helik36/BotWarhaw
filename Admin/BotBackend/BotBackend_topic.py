import logging

import telegram.error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from Admin.BotBackend.BotBackend_channel import get_channel
from Admin.database.actionWithDB.actionWithChannelDB import append_in_db_channel
from Admin.database.actionWithDB.actionWithTopicDB import append_in_db_topic, del_from_db_topic
from Admin.database.actionWithDB.general_query import get_from_db_data

BUTTON, BACK = range(2)

async def get_topics():

    topics = "topics"

    channels = await get_from_db_data(topics)
    tempalte = ""

    count = 1
    for i, j in channels.items():
        tempalte += f"{count}) {j}\n"
        count += 1

    return tempalte

# Просмотр топиков
# Тут нужно будет сделать, чтобы выводились топики, привязанные к группе
async def handler_view_topics(update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = await get_topics()

    await query.edit_message_text(f"Текущие топики/темы:\n\n{text}", reply_markup=reply_markup)


async def select_channel(update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    type_callback_query = update.callback_query.data

    from_user = query.from_user.id
    get_sent_channel = query.message.reply_markup.inline_keyboard[0][0].text
    context.user_data["select_channel"] = get_sent_channel

    match type_callback_query:

        case "CREATE_TOPIC":

            await context.bot.send_message(from_user, "Напиши название нового топика")

        case "ADD_TOPIC":

            await context.bot.send_message(from_user, "Напишите ID и название существующего топика через пробел")

        case "DELETE_TOPIC":

            await context.bot.send_message(from_user, f"Напиши название топика на удаление\nТекущие топики: {await get_topics()}")


async def handler_create_topic(update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text
    channel = context.user_data["select_channel"]

    data_channels = await get_from_db_data("channels")
    id_channel = next(key for key, name in data_channels.items() if name == channel)

    try:
        data_topic = await context.bot.createForumTopic(chat_id=id_channel, name=user_input)
        thread_id = data_topic.message_thread_id
        name_topic = data_topic.name

    except telegram.error.BadRequest:

        await update.message.reply_text("Не удалось создать топик")
        logging.error(user_input, id_channel)
        raise telegram.error.BadRequest

    topic = {thread_id: name_topic}

    try:
        await append_in_db_topic(topic)

        current_topic_at_channel = await get_topics()

        await update.message.reply_text(f"Топик '{user_input}' создан. Текущие топики для канала '{channel}':\n\n{current_topic_at_channel}")
        context.user_data.clear()

        return ConversationHandler.END

    except:
        await update.message.reply_text("Возникла проблема при добавления топика в БД. Обратитесть к админу бота")

        return BACK


# Добавление
async def handler_add_topic(update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    channel = context.user_data["select_channel"]

    user_input = update.message.text
    id_thread, name_topic = user_input.split(" ")

    topic = {id_thread: name_topic}

    data_channels = await get_from_db_data("channels")
    id_channel = next(key for key, name in data_channels.items() if name == channel)

    try:
        await context.bot.get_chat(chat_id=f"{id_channel}_{id_thread}")

    except telegram.error.TelegramError:

        await update.message.reply_text("Канал не найден. Некоректное имя",
                                        reply_markup=reply_markup)

        raise telegram.error.TelegramError

    try:
        await append_in_db_topic(topic)

        current_topic_at_channel = await get_topics()

        await update.message.reply_text(f"Топик '{user_input}' создан. Текущие топики для канала '{channel}':\n\n{current_topic_at_channel}")
        context.user_data.clear()

        return ConversationHandler.END

    except:

        await update.message.reply_text("Возникла проблема при добавления топика в БД. Обратитесть к админу бота")

        return BACK

# Удаление
async def handler_delete_topic(update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text

    keyboard = [[InlineKeyboardButton("<< В меню", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    channel = context.user_data["select_channel"]

    data_channel = await get_from_db_data("channels")
    data_topic = await get_from_db_data("topics")

    id_channel = next(key for key, name in data_channel.items() if name == channel)
    id_topic = next(key for key, name in data_topic.items() if name == user_input)

    try:
        await context.bot.delete_forum_topic(chat_id=id_channel, message_thread_id=id_topic)

    except telegram.error.TelegramError:

        await update.message.reply_text("Не удалось удалить топик")
        logging.error(user_input, id_channel, id_topic)
        raise telegram.error.TelegramError

    try:
        await del_from_db_topic(user_input)

        current_topic_at_channel = await get_topics()


        await update.message.reply_text(f"Топик `{user_input}` удалён. Текущие топики:\n\n{current_topic_at_channel}")

        context.user_data.clear()
        return ConversationHandler.END

    except:
        await update.message.reply_text("Такой канал отсутствует", reply_markup=reply_markup)

    return BACK
