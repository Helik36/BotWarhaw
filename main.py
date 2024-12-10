import configparser
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, \
    MessageHandler, filters

from Admin.KeyBoardButton.KeyButton_Main import button_menu

from Admin.BotBackend.Backend_channel import handler_add_channel, handler_delete_channel
from Admin.BotBackend.Backend_topic import select_channel, handler_create_topic

from Admin.BotHandler_Admin import HandlerForAdmin
from Admin.database.check_database import createbase_for_admin

config = configparser.ConfigParser()
config.read("config.ini")

TOKEN_BOT = config["api_token"]["api_TOKEN"]
ADMIN_ID = int(config['ADMIN_ID']["my_id"])


# logging.basicConfig(filename='logs/app.log',
#             format="\n[%(asctime)s]: %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
#             level=logging.INFO)

logging.basicConfig(
            format="\n[%(asctime)s]: %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
            level=logging.INFO)

(BUTTON, BACK,

 ACTION_WITH_CHANNEL,
 ADD_CHANNEL, DELETE_CHANNEL,

 ACTION_WITH_TOPIC,
 VIEW_TOPIC, CREATE_TOPIC, ADD_TOPIC, DELETE_TOPIC) = range(10)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    message_text = update.message.text

    # print(update)
    qq = await context.bot.get_chat(chat_id="-1001090194695")
    print(qq)

    # Создание топика с названием. ID передаётся основной канал
    # print(await context.bot.createForumTopic(chat_id=chat_id, name="mynewtopic"))
    get_id_topic = update.message.message_thread_id

    message_for_topic = f"{chat_id}_{get_id_topic}"
    # Логирование данных
    logging.info(f"Сообщение в группе {chat_id} от пользователя {user_id} ({user_name}): {message_text}")

    # Если нужно отправить ответ (опционально)
    # await context.bot.send_message(chat_id=chat_id, text=f"Ваш ID: {user_id}")

    # Отправка сообщения в конкретный топик
    await context.bot.send_message(chat_id=message_for_topic, text=f"Ваш ID: {user_id}", message_thread_id=get_id_topic)

# Входная точка
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):

    if update.message.chat.id != ADMIN_ID:
        await _.bot.send_message(chat_id=update.effective_chat.id, text="Access Denied")

    else:
        await update.message.reply_text(f'Приветствую, {update.effective_user.first_name}!')

        keyboard = button_menu()
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)

        return BUTTON


if __name__ == "__main__":

    admin_handler = HandlerForAdmin()
    createbase_for_admin()

    app = Application.builder().token(TOKEN_BOT).build()

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={

            # Кнопки и возврат
            BUTTON: [CallbackQueryHandler(admin_handler.button)],
            BACK: [CallbackQueryHandler(admin_handler.back)],

            # Админ. Действие с каналами
            ACTION_WITH_CHANNEL: [CallbackQueryHandler(admin_handler.action_with_channel)],
            ADD_CHANNEL: [MessageHandler(filters.TEXT, handler_add_channel)],
            DELETE_CHANNEL: [MessageHandler(filters.TEXT, handler_delete_channel)],

            ACTION_WITH_TOPIC: [CallbackQueryHandler(admin_handler.action_with_topic)],
            CREATE_TOPIC: [CallbackQueryHandler(select_channel), MessageHandler(filters.TEXT, handler_create_topic)],
            ADD_TOPIC: [],
            DELETE_TOPIC: []
        },
        fallbacks=[]
    ))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()