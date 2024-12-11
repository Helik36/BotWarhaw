import logging

from langchain_core.runnables import chain
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.BotBackend_scheduler.message_sheduler import scheduler_message

(BUTTON, BACK,
 SCHEDULER_MESSAGE)= range(3)

class Scheduler:

    async def back(self, update, _):
        query = update.callback_query
        await query.answer()

        keyboard = button_menu()

        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await query.answer()

        await query.edit_message_text('Пожалуйста, выберите:', reply_markup=reply_markup)

        return BUTTON


    async def setting_scheduler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        # query = update.callback_query
        # choice = query.data
        #
        # await query.answer()
        #
        # match choice:
        #
        #     case "SCHEDULER_MESSAGE":
        chat_id = update.message.from_user.id
        target_text = update.message.text
        print(target_text)
        # Тут должно быть сохранение в БД

        keyboard = [[InlineKeyboardButton("> Каждый день", callback_data='EVERY_DAY')],
                    [InlineKeyboardButton("> Конкретные дни", callback_data='SPECIFIC_DAY')],
                    [InlineKeyboardButton("> Раз в неделю", callback_data='ONCE_AT_WEEK')],
                    [InlineKeyboardButton("< В меню", callback_data='BACK')]]
        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=chat_id, text="Выберете как часто будет отправляться: ", reply_markup=menu_markup)


    async def setting_scheduler_select_repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        type_callback_query = update.callback_query.data

        from_user = query.from_user.id
        get_sent_channel = query.message.reply_markup.inline_keyboard[0][0].text
        context.user_data["select_channel"] = get_sent_channel

        match type_callback_query:

            case "EVERY_DAY":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)

            case "SPECIFIC_DAY":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)

            case "ONCE_AT_WEEK":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)



    def create_new_cheduler(self, update, context):

        chat_id =  update.message.from_user.id
        logging.info("create scheduler message")

        context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)

