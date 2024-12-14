import configparser
import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, \
    MessageHandler, filters

from Admin.KeyBoardButton.KeyButton_Main import button_menu

from Admin.BotBackend.BotBackend_channel import handler_add_channel, handler_delete_channel
from Admin.BotBackend.BotBackend_topic import select_channel, handler_create_topic, handler_add_topic, handler_delete_topic

from Admin.BotBackend.HandlerMessageInChannel.HandlerMessage import handler_add_channel_from_message_in_channel

from Admin.BotHandler_Admin import HandlerForAdmin
from Admin.BotBackend.BotBackend_scheduler.BotBackend_scheduler import Scheduler

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

(BUTTON, BACK) = range(2)

(ACTION_WITH_CHANNEL,
 ADD_CHANNEL, DELETE_CHANNEL) = range(2, 5)

(ACTION_WITH_TOPIC,
CREATE_TOPIC, ADD_TOPIC, DELETE_TOPIC) = range(5, 9)

# SCHEDULER
(SCHEDULER,
 SCHEDULER_MESSAGE, SCHEDULER_CONFIG_DAY, CONFIG_SCHEDULER,
 EXIT_SCHEDULER) = range(9, 14)


async def mess(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """
    Реализация:
    По команде можно выбирается создать планировщик сообщений или опросов

    Планирововщик сообщений:
    1) Выбрать канал
    1.1) Выбрать топик
    2) Указать текст
    3) Выбрать как часто

    """

    chat_id = update.message.from_user.id

    context.bot.send_message(chat_id=chat_id, text="Напиши текст, который нужно отправлять")


    #
    # scheduler = Scheduler(update, context)
    # logging.info("create scheduler message")
    #
    # scheduler.create_new_cheduler()
    # context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # chat_id = update.effective_chat.id
    # user_id = update.effective_user.id
    # user_name = update.effective_user.first_name
    message_text = update.message.text

    # print(update)
    # await context.bot.createForumTopic(chat_id=main_channel, name="mynewtopic")

    # добавить отдельно ручки для работы с командами в самом канале/топике
    # print(update.message.chat.id)

    # message_for_topic = f"{chat_id}_{get_id_topic}"
    # Логирование данных
    # logging.info(f"Сообщение в группе {chat_id} от пользователя {user_id} ({user_name}): {message_text}")

    # Если нужно отправить ответ (опционально)
    # await context.bot.send_message(chat_id=chat_id, text=f"Ваш ID: {user_id}")

    # Отправка сообщения в конкретный топик
    # await context.bot.send_message(chat_id=message_for_topic, text=f"Ваш ID: {user_id}", message_thread_id=get_id_topic)


# Входная точка
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    print(__name__)

    if update.message.from_user.id != ADMIN_ID:
        await _.bot.send_message(chat_id=update.effective_chat.id, text="Access Denied")

    else:
        await update.message.reply_text(f'Приветствую, {update.effective_user.first_name}!')

        keyboard = button_menu()
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)

        return BUTTON


if __name__ == "__main__":

    admin_handler = HandlerForAdmin()
    scheduler = Scheduler()

    createbase_for_admin()

    app = Application.builder().token(TOKEN_BOT).build()

    # second_level =(ConversationHandler(
    #     entry_points=[MessageHandler(filters.TEXT, scheduler.setting_scheduler)],
    #     states={
    #         CHOICE: [CallbackQueryHandler(scheduler.setting_scheduler_select_repeat)],
    #         HOUR: [CallbackQueryHandler(scheduler.create_new_cheduler)]
    #     },
    #     fallbacks=[]
    # ))

    # selection_handler = [second_level]

    app.add_handler(CommandHandler("mess", mess))
    app.add_handler(ConversationHandler(
        # Админ
        entry_points=[CommandHandler("start", start),

                      # Добавить канал через сообщение в канале
                      CommandHandler("add_channel", handler_add_channel_from_message_in_channel)],
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
            ADD_TOPIC: [CallbackQueryHandler(select_channel), MessageHandler(filters.TEXT, handler_add_topic)],
            DELETE_TOPIC: [CallbackQueryHandler(select_channel), MessageHandler(filters.TEXT, handler_delete_topic)],


            SCHEDULER: [ConversationHandler(
                entry_points=[CallbackQueryHandler(admin_handler.create_sheduler_entity)],
                states={
                    SCHEDULER_MESSAGE: [MessageHandler(filters.TEXT, scheduler.setting_scheduler)],
                    SCHEDULER_CONFIG_DAY: [CallbackQueryHandler(scheduler.setting_scheduler_select_repeat)],
                    CONFIG_SCHEDULER: [CallbackQueryHandler(scheduler.create_new_cheduler)]
                },
                fallbacks=[],
                map_to_parent={
                    EXIT_SCHEDULER: ConversationHandler.END
                })
            ],
        },
        fallbacks=[]
    ))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()