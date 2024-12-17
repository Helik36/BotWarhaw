import calendar
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.database.actionWithDB.actionWithTopicDB import get_topic_from_channel
from Admin.database.actionWithDB.general_query import get_from_db_data, select_id_channel

# Button
(BUTTON, BACK) = range(2)

# SCHEDULER
(SCHEDULER, SELECT_TOPIC_FROM_CHANNEL, CREATE_SCHEDULER_ENTITY,
 SCHEDULER_MESSAGE, SCHEDULER_CONFIG_FREQUENCY, SCHEDULER_CONFIG_TIME, CONFIG_SCHEDULER,
 EXIT_SCHEDULER) = range(9, 17)


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


    async def __create_days_week(self, query):

        keyboard = [[]]

        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

        match query:

            case "ONCE_AT_WEEK":

                for i in range(len(days_of_week)):
                    keyboard.append([InlineKeyboardButton(text=days_of_week[i], callback_data=f'DAY_OF_WEEK_{i}')])

        return InlineKeyboardMarkup(keyboard)


    async def __setting_time(self, get_hour, selected_day_week=None):

        async def get_day_week(target_weekday):
            year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
            current_day = day

            current_weekday = calendar.weekday(year, month, current_day)
            target_weekday = int(next(i for i in target_weekday.split("_") if i.isdigit()))

            if target_weekday < current_weekday:
                while calendar.weekday(year, month, day) != target_weekday:
                    if target_weekday != current_weekday:
                        day += 1
                    else:
                        break

            elif target_weekday > current_weekday:
                while calendar.weekday(year, month, day) != target_weekday:
                    if target_weekday != current_weekday:
                        day += 1
                    else:
                        break

            return day

        get_select_hour = int(next(j for j in get_hour.split("_") if j.isdigit())) - 3

        day = datetime.now().day


        if selected_day_week is not None:
            day = await get_day_week(selected_day_week)

        current_hour = datetime.now().hour - 3
        if datetime.now().day == day:
            if current_hour > get_select_hour:
                logging.info("+day")
                day += 1

        # timedelta - Пока кажется, что он засекает ЧЕРЕЗ сколько будет запущен, но скорее всего там нужно указывать всё данные
        # Также дату нужно указывать не с 1 по 28/30/31 а с 1 по 365 (неудобно)

        # datetime - засекает, и запускает в УСТАНОВЛЕННОЕ время
        setting = datetime(year=datetime.now().year,
                           month=datetime.now().month,
                           day=day,
                           hour=get_select_hour,
                           minute=0)

        tar_week = calendar.weekday(datetime.now().year, datetime.now().month, day)
        logging.info("tar_week - ", tar_week)
        logging.info("tar_week - ", calendar.day_name[tar_week])

        print(setting)
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

        await context.bot.edit_message_text(chat_id=from_user, text="Выберете канал: ", reply_markup=menu_markup,
                                            message_id=message_id)

        return SELECT_TOPIC_FROM_CHANNEL


    async def select_topic_from_channel(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        selected_channel = query.data

        context.user_data["selected_channel"] = await select_id_channel("channels", selected_channel)

        from_user = await self.__query_from_user(update, context)
        message_id = await self.__get_previous_message(update, context)

        topics = await get_topic_from_channel(selected_channel)

        keyboard = []
        for id_data, topic in topics.items():
            keyboard.append([InlineKeyboardButton(f"{topic}", callback_data=id_data)])

        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(chat_id=from_user, text="Выберете топик: ", reply_markup=menu_markup,
                                            message_id=message_id)

        return CREATE_SCHEDULER_ENTITY


    async def create_scheduler_entity(self, update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.callback_query.from_user.id
        query = update.callback_query
        topic_id = query.data

        context.user_data["selected_topic"] = topic_id

        await query.answer()

        match context.user_data["type_scheduler"]:

            case "SCHEDULER_MESSAGE":

                message_id = await self.__get_previous_message(update, context)

                await context.bot.edit_message_text(chat_id=chat_id, text="Напиши текст, который нужно запланировать",
                                                    message_id=message_id)

                return SCHEDULER_MESSAGE

            case "SCHEDULER_POLL":
                pass


    async def setting_scheduler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.message.from_user.id

        target_text = update.message.text
        context.user_data["target_text"] = target_text

        keyboard = [[InlineKeyboardButton("> Каждый день", callback_data='EVERY_DAY')],
                    [InlineKeyboardButton("> Конкретные дни", callback_data='SPECIFIC_DAY')],
                    [InlineKeyboardButton("> Раз в неделю", callback_data='ONCE_AT_WEEK')],
                    [InlineKeyboardButton("< В меню", callback_data='BACK')]]
        menu_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=chat_id, text="Выберете как часто будет отправляться: ",
                                       reply_markup=menu_markup)

        return SCHEDULER_CONFIG_FREQUENCY


    async def setting_scheduler_select_repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        type_callback_query = update.callback_query.data

        context.user_data["selected_frequency"] = type_callback_query

        from_user = query.from_user.id

        match type_callback_query:

            case "EVERY_DAY":

                menu_markup = await self.__create_time(type_callback_query)

                await update.callback_query.edit_message_text(text="Выбери время", reply_markup=menu_markup)

                return CONFIG_SCHEDULER

            case "SPECIFIC_DAY":

                await context.bot.send_message(chat_id=from_user, text="Данная функция ещё не реализоваана")

            case "ONCE_AT_WEEK":

                menu_markup = await self.__create_days_week(type_callback_query)

                await update.callback_query.edit_message_text(text="Выбери день недели", reply_markup=menu_markup)

                return SCHEDULER_CONFIG_TIME


    async def config_scheduler_time(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        type_callback_query = update.callback_query.data
        context.user_data["day_of_week"] = type_callback_query

        menu_markup = await self.__create_time(type_callback_query)

        await update.callback_query.edit_message_text(text="Выбери время", reply_markup=menu_markup)

        return CONFIG_SCHEDULER


    async def create_new_scheduler(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        chat_id = query.message.chat.id
        await query.answer()

        type_callback_query = update.callback_query.data

        match type_callback_query:

            case "BUTTOM_NEXT":

                menu_markup = await self.__create_time(type_callback_query)
                await update.callback_query.edit_message_text(text=type_callback_query, reply_markup=menu_markup)

                return CONFIG_SCHEDULER

            case "BUTTOM_BACK":

                menu_markup = await self.__create_time(type_callback_query)
                await update.callback_query.edit_message_text(text=type_callback_query, reply_markup=menu_markup)

                return CONFIG_SCHEDULER

            case _ :

                message_id = await self.__get_previous_message(update, context)

                id_channel = context.user_data["selected_channel"]
                topic_id = context.user_data["selected_topic"]
                target_text = context.user_data["target_text"]
                selected_frequency = context.user_data["selected_frequency"]

                keyboard = [[InlineKeyboardButton("< В меню", callback_data='BACK')]]
                menu_markup = InlineKeyboardMarkup(keyboard)

                match selected_frequency:

                    case "EVERY_DAY":

                        logging.info("create scheduler message")

                        time_interval = timedelta(days=1)

                        first_run = await self.__setting_time(get_hour=type_callback_query)

                        context.job_queue.run_repeating(callback=self.__scheduler_message, interval=time_interval,
                                                        first=first_run,
                                                        chat_id=id_channel,
                                                        data={"target_text": target_text, "topic_id": topic_id})

                        print(context.job_queue.jobs())

                        ##############################
                        """
                        тут нужно сделать сохранение данных в БД, чтобы они при перезапуске бота автоматически создавались
                        1) Канал
                        2) Топик
                        3) Частота и время
                        4) Текст
                        """
                        ##############################

                        await context.bot.edit_message_text(
                            text=f"Сообщение запланировано", chat_id=chat_id, message_id=message_id, reply_markup=menu_markup)

                        context.user_data.clear()
                        return EXIT_SCHEDULER

                        # case "SET_TIME_NEXT":
                        #
                        #     logging.info("create scheduler message")
                        #
                        #     await context.bot.send_message(chat_id=chat_id, text=type_callback_query)
                        #     # context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)
                        #
                        #     return ConversationHandler.END

                    case "ONCE_AT_WEEK":

                        logging.info("create scheduler message")

                        day_week = context.user_data["day_of_week"]
                        time_interval = timedelta(days=7)

                        first_run = await self.__setting_time(get_hour=type_callback_query, selected_day_week=day_week)

                        context.job_queue.run_repeating(callback=self.__scheduler_message, interval=time_interval,
                                                        first=first_run,
                                                        chat_id=id_channel,
                                                        data={"target_text": target_text, "topic_id": topic_id})

                        day_week = int(next(i for i in day_week.split("_") if i.isdigit()))
                        week = calendar.day_name[day_week]
                        text_message = f"Сообщение запланировано на каждый {week} в {type_callback_query} часов"

                        await context.bot.edit_message_text(
                            text=text_message, chat_id=chat_id, message_id=message_id, reply_markup=menu_markup)
                        print(context.job_queue.jobs())

                        context.user_data.clear()
                        return EXIT_SCHEDULER


    async def __scheduler_message(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send the alarm message."""

        chat_id = context.job.chat_id
        text = context.job.data.get("target_text")
        id_thread = context.job.data.get("topic_id")

        await context.bot.send_message(chat_id=chat_id, text=text, message_thread_id=id_thread)



