import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.BotBackend_scheduler.message_sheduler import scheduler_message
from Admin.another_def import get_previous_message

# Button
(BUTTON, BACK) = range(2)

#SCHEDULER
(SCHEDULER,
 SCHEDULER_MESSAGE, SCHEDULER_CONFIG_DAY,CONFIG_SCHEDULER,
 EXIT_SCHEDULER) = range(10, 15)


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

                    keyboard.append([InlineKeyboardButton(text=text, callback_data=f'SET_TIME_{i}')])

                else:
                    text = f"{i}:00"

                    keyboard.append([InlineKeyboardButton(text=text, callback_data=f'SET_TIME_{i}')])

            keyboard.append([InlineKeyboardButton(text="> Дальше", callback_data='BUTTOM_NEXT')])
            return InlineKeyboardMarkup(keyboard)

        if query == "BUTTOM_NEXT":

            for i in range(13, 24):

                    text = f"{i}:00"

                    keyboard.append([InlineKeyboardButton(text=text, callback_data=f'SET_TIME_{i}')])

            keyboard.append([InlineKeyboardButton(text="<Назад", callback_data='BUTTOM_BACK')])
            return InlineKeyboardMarkup(keyboard)

    async def __setting_time(self, get_hour):

        get_select_hour = int(next(j for j in get_hour.split("_") if j.isdigit())) - 3

        # timedelta - Пока кажется, что он засекает ЧЕРЕЗ сколько будет запущен, но скорее всего там нужно указывать всё данные
        # Также дату нужно указывать не с 1 по 28/30/31 а с 1 по 365 (неудобно)

        # datetime - засекает, и запускает в УСТАНОВЛЕННОЕ время

        current_hour = datetime.now().hour - 3
        if current_hour > get_select_hour:
            print("pinc")
            setting = datetime(year=datetime.now().year,
                               month=datetime.now().month,
                               day=datetime.now().day + 1,
                               hour=get_select_hour,
                               minute=0)

        else:
            print("pong")
            setting = datetime(year=datetime.now().year,
                               month=datetime.now().month,
                               day=datetime.now().day,
                               hour=get_select_hour,
                               minute=0)

        return setting


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


    async def create_new_cheduler(self, update, context: ContextTypes.DEFAULT_TYPE):


        query = update.callback_query
        chat_id = query.message.chat.id
        await query.answer()

        type_callback_query = update.callback_query.data

        for i in range(24):

            if type_callback_query == f"SET_TIME_{i}":

                logging.info("create scheduler message")

                time_interval = timedelta(seconds=5)
                first_run = await self.__setting_time(type_callback_query)

                # await context.bot.send_message(chat_id=chat_id, text=type_callback_query)

                message_id = await get_previous_message(update, context)
                await context.bot.edit_message_text(
                    text=f"Сообщение запланировано", chat_id=chat_id, message_id=message_id)

                context.job_queue.run_repeating(callback=scheduler_message, interval=time_interval, first=first_run, chat_id=chat_id)

                ##############################
                # тут нужно сделать сохранение данных в БД
                ##############################
                return EXIT_SCHEDULER

        match type_callback_query:

            # case "SET_TIME_NEXT":
            #
            #     logging.info("create scheduler message")
            #
            #     await context.bot.send_message(chat_id=chat_id, text=type_callback_query)
            #     # context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)
            #
            #     return ConversationHandler.END

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
