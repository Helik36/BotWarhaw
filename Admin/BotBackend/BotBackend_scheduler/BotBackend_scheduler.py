import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.BotBackend_scheduler.message_sheduler import scheduler_message

# Button
(BUTTON, BACK)= range(2)

#SCHEDULER
(SCHEDULER,
 SCHEDULER_MESSAGE, SCHEDULER_CONFIG_DAY, SCHEDULER_POLL) = range(10, 14)

(CHOICE, CONFIG_SCHEDULER, CREATE_NEW_CCHEDULER) = 15, 16, 17

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

    async def __create_time(self, query):

        keyboard = [[]]

        if query != "BUTTOM_NEXT" or query == "BUTTOM_BACK":

            for i in range(13):
                if i <= 9:
                    text = f"0{i}:00"

                    keyboard.append([InlineKeyboardButton(text=text, callback_data='SET_TIME_NEXT')])

                else:
                    text = f"{i}:00"

                    keyboard.append([InlineKeyboardButton(text=text, callback_data='SET_TIME_NEXT')])

            keyboard.append([InlineKeyboardButton(text="> Дальше", callback_data='BUTTOM_NEXT')])
            return InlineKeyboardMarkup(keyboard)

        if query == "BUTTOM_NEXT":

            for i in range(13, 24):

                    text = f"{i}:00"

                    keyboard.append([InlineKeyboardButton(text=text, callback_data='SET_TIME_NEXT')])

            keyboard.append([InlineKeyboardButton(text="<Назад", callback_data='BUTTOM_BACK')])
            return InlineKeyboardMarkup(keyboard)

    # async def check_time(self, update, context):
    #
    #     query = update.callback_query
    #     await query.answer()
    #
    #     type_callback_query = update.callback_query.data
    #
    #     match type_callback_query:
    #
    #         case "NEXT":
    #             keyboard = [[]]
    #             for i in range(13):
    #                 if i <= 9:
    #                     text = f"0{i}:00"
    #
    #                     keyboard.append([InlineKeyboardButton(text=text, callback_data='SET_TIME')])
    #
    #                 else:
    #                     text = f"{i}:00"
    #
    #                     keyboard.append([InlineKeyboardButton(text=text, callback_data='SET_TIME')])
    #
    #             keyboard.append([InlineKeyboardButton(text="<Назад", callback_data='BACK')])
    #             return InlineKeyboardMarkup(keyboard)


    async def setting_scheduler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.message.from_user.id

        ##################################
        target_text = update.message.text
        # Тут должно быть сохранение в БД
        ##################################

        keyboard = [[InlineKeyboardButton("> Каждый день", callback_data='EVERY_DAY')],
                    [InlineKeyboardButton("> Конкретные дни", callback_data='SPECIFIC_DAY')],
                    [InlineKeyboardButton("> Раз в неделю", callback_data='ONCE_AT_WEEK')],
                    [InlineKeyboardButton("< В меню", callback_data='BACK')]]
        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=chat_id, text="Выберете как часто будет отправляться: ", reply_markup=menu_markup)

        return SCHEDULER_CONFIG_DAY


    async def setting_scheduler_select_repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        type_callback_query = update.callback_query.data

        from_user = query.from_user.id
        get_sent_channel = query.message.reply_markup.inline_keyboard[0][0].text
        context.user_data["select_channel"] = get_sent_channel

        match type_callback_query:

            case "EVERY_DAY":

                menu_markup = await self.__create_time(type_callback_query)

                await update.callback_query.edit_message_text(text=type_callback_query,  reply_markup=menu_markup)

                return CONFIG_SCHEDULER


            case "SPECIFIC_DAY":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)

            case "ONCE_AT_WEEK":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)


    async def config_scheduler(self, update, context):

        query = update.callback_query

        query = update.callback_query
        await query.answer()

        type_callback_query = update.callback_query.data

        match type_callback_query:

            case "SET_TIME_NEXT":

                return CREATE_NEW_CCHEDULER

    async def create_new_cheduler(self, update, context):

        print(update)
        query = update.callback_query
        chat_id = query.message.chat.id
        await query.answer()

        type_callback_query = update.callback_query.data

        match type_callback_query:

            case "SET_TIME_NEXT":

                logging.info("create scheduler message")

                await context.bot.send_message(chat_id=chat_id, text=type_callback_query)
                # context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)

                return ConversationHandler.END

            case "BUTTOM_NEXT":

                print(type_callback_query)

                menu_markup = await self.__create_time(type_callback_query)
                await update.callback_query.edit_message_text(text=type_callback_query,  reply_markup=menu_markup)

                return CONFIG_SCHEDULER

            case "BUTTOM_BACK":

                print(type_callback_query)

                menu_markup = await self.__create_time(type_callback_query)
                await update.callback_query.edit_message_text(text=type_callback_query, reply_markup=menu_markup)

                return CONFIG_SCHEDULER
