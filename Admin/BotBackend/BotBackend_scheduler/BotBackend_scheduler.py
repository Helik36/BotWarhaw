import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.BotBackend_scheduler.message_sheduler import scheduler_message
from Admin.database.actionWithDB.actionWithTopicDB import get_topic_from_channel
from Admin.database.actionWithDB.general_query import get_from_db_data

# Button
(BUTTON, BACK) = range(2)

#SCHEDULER
(SCHEDULER, SELECT_TOPIC_FROM_CHANNEL, CREATE_SCHEDULER_ENTITY,
 SCHEDULER_MESSAGE, SCHEDULER_CONFIG_DAY, CONFIG_SCHEDULER,
 EXIT_SCHEDULER) = range(9, 16)


class Scheduler:

    async def __get_previous_message(self, update, context):

        message_id = update.callback_query.message.message_id

        return message_id

    async def __query_from_user(self, update, context):

        query_from_user_id = update.callback_query.from_user.id

        return query_from_user_id


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


    async def select_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        context.user_data["type_scheduler"] = query.data

        from_user = await self.__query_from_user(update, context)
        message_id = await self.__get_previous_message(update, context)

        channels = await get_from_db_data("channels")

        keyboard = []

        for id_channel, name in channels.items():
            keyboard.append([InlineKeyboardButton(f"{name}", callback_data=name)])

        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(chat_id=from_user, text="Выберете канал: ", reply_markup=menu_markup, message_id=message_id)

        return SELECT_TOPIC_FROM_CHANNEL


    async def select_topic_from_channel(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        selected_channel = query.data
        context.user_data["selected_channel"] = selected_channel

        from_user = await self.__query_from_user(update, context)
        message_id = await self.__get_previous_message(update, context)

        topics = await get_topic_from_channel(selected_channel)

        keyboard = []
        for topic in topics:
            keyboard.append([InlineKeyboardButton(f"{topic}", callback_data=topic)])

        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(chat_id=from_user, text="Выберете топик: ", reply_markup=menu_markup,
                                            message_id=message_id)

        return CREATE_SCHEDULER_ENTITY


    async def create_scheduler_entity(self, update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.callback_query.from_user.id
        query = update.callback_query
        topic = query.data

        context.user_data["selected_topic"] = topic

        await query.answer()

        match context.user_data["type_scheduler"]:

            case "SCHEDULER_MESSAGE":

                message_id = await self.__get_previous_message(update, context)

                await context.bot.edit_message_text(chat_id=chat_id, text="Напиши текст, который нужно запланировать", message_id=message_id)

                return SCHEDULER_MESSAGE

            case "SCHEDULER_POLL":
                pass


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
        get_sent_channel = query.message.reply_markup.inline_keyboard[0][0].text # Нужно передлать
        context.user_data["select_channel"] = get_sent_channel

        match type_callback_query:

            case "EVERY_DAY":

                menu_markup = await self.__create_time(type_callback_query)

                await update.callback_query.edit_message_text(text="Выбери время",  reply_markup=menu_markup)

                return CONFIG_SCHEDULER


            case "SPECIFIC_DAY":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)

            case "ONCE_AT_WEEK":

                await context.bot.send_message(chat_id=from_user, text=type_callback_query)


    async def create_new_scheduler(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        chat_id = query.message.chat.id
        await query.answer()

        type_callback_query = update.callback_query.data

        if "SET_TIME" in type_callback_query:
            logging.info("create scheduler message")

            time_interval = timedelta(days=1)
            first_run = await self.__setting_time(type_callback_query)

            # await context.bot.send_message(chat_id=chat_id, text=type_callback_query)

            message_id = await self.__get_previous_message(update, context)

            keyboard = [[InlineKeyboardButton("< В меню", callback_data='BACK')]]
            menu_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.edit_message_text(
                text=f"Сообщение запланировано", chat_id=chat_id, message_id=message_id, reply_markup=menu_markup)

            context.job_queue.run_repeating(callback=scheduler_message, interval=time_interval, first=first_run,
                                            chat_id=chat_id)
            print(context.job_queue.jobs())

            ##############################
            # тут нужно сделать сохранение данных в БД
            ##############################

            context.user_data.clear()
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
