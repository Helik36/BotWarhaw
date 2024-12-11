from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from Admin.BotBackend.BotBackend_topic import handler_view_topics
from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.BotBackend_channel import handler_view_channel
from Admin.database.actionWithDB.general_query import get_from_db_data

(BUTTON, BACK,

 ACTION_WITH_CHANNEL,
 ADD_CHANNEL, DELETE_CHANNEL,

 ACTION_WITH_TOPIC,
 VIEW_TOPIC, CREATE_TOPIC, ADD_TOPIC, DELETE_TOPIC,

 SCHEDULER,
 SCHEDULER_MESSAGE, SCHEDULER_POLL) = range(13)


class HandlerForAdmin:

    async def check_callback_query(self, case):

        keyboard = []

        channels = await get_from_db_data("channels")

        for id_channel, name in channels.items():
            keyboard.append([InlineKeyboardButton(f"{name}", callback_data=case)])

        return InlineKeyboardMarkup(keyboard)


    # Вызывается когда нажимается кнопка Назад
    async def back(self, update, _):
        query = update.callback_query
        await query.answer()

        keyboard = button_menu()

        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await query.answer()

        await query.edit_message_text('Пожалуйста, выберите:', reply_markup=reply_markup)

        return BUTTON


    async def button(self, update, _):
        query = update.callback_query
        choice = query.data

        await query.answer()

        match choice:

            case "ACTION_WITH_CHANNEL":
                keyboard = [[InlineKeyboardButton("> Посмотреть текущие каналы", callback_data='VIEW_CHANNEL')],
                            [InlineKeyboardButton("> Добавить канал", callback_data='ADD_CHANNEL')],
                            [InlineKeyboardButton("> Удалить канал", callback_data='DELETE_CHANNEL')],
                            [InlineKeyboardButton("< В меню", callback_data='BACK')]]
                menu_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text("Выберете действие: ", reply_markup=menu_markup)
                return ACTION_WITH_CHANNEL

            case "ACTION_WITH_TOPIC":
                keyboard = [[InlineKeyboardButton("> Посмотреть текущие топики", callback_data='VIEW_TOPIC')],
                            [InlineKeyboardButton("> Создать топик для канала", callback_data='CREATE_TOPIC')],
                            [InlineKeyboardButton("> Добавить боту существующий топик в канале", callback_data='ADD_TOPIC')],
                            [InlineKeyboardButton("> Удалить топик из канала", callback_data='DELETE_TOPIC')],
                            [InlineKeyboardButton("< В меню", callback_data='BACK')]]
                menu_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text("Выберете действие: ", reply_markup=menu_markup)
                return ACTION_WITH_TOPIC

            case "SCHEDULER":

                keyboard = [[InlineKeyboardButton("> Запланировать пост сообщения", callback_data='SCHEDULER_MESSAGE')],
                            [InlineKeyboardButton("> Запланирировать опрос", callback_data='SCHEDULER_POLL')]]
                menu_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text("Выберете действие: ", reply_markup=menu_markup)
                return SCHEDULER


    async def action_with_channel(self, update, _):

        query = update.callback_query
        choice = query.data
        await query.answer()

        match choice:

            case "VIEW_CHANNEL":
                await handler_view_channel(update, _)
                return BACK

            case "ADD_CHANNEL":
                await query.edit_message_text("Вставьте ID группы: ")
                return ADD_CHANNEL

            case "DELETE_CHANNEL":
                await query.edit_message_text("Напишите название группы, которое нужно удалить")
                return DELETE_CHANNEL

            case _ :
                query = update.callback_query
                await query.answer()

                keyboard = button_menu()
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text('Пожалуйста, выберите:', reply_markup=reply_markup)
                return BUTTON


    async def action_with_topic(self, update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        choice = query.data
        await query.answer()


        match choice:

            case "VIEW_TOPIC":
                await handler_view_topics(update, context)
                return BACK

            case "CREATE_TOPIC":

                reply_markup = await self.check_callback_query("CREATE_TOPIC")

                await query.edit_message_text("Для какого канала нужно создать топик?", reply_markup=reply_markup)

                return CREATE_TOPIC

            case "ADD_TOPIC":

                reply_markup = await self.check_callback_query("ADD_TOPIC")

                await query.edit_message_text("Для какого канала нужно добавить топик?", reply_markup=reply_markup)

                return ADD_TOPIC

            case "DELETE_TOPIC":

                reply_markup = await self.check_callback_query("DELETE_TOPIC")

                await query.edit_message_text("Из какого канала нужно удалить топик?", reply_markup=reply_markup)

                return DELETE_TOPIC

            case _:
                query = update.callback_query
                await query.answer()

                keyboard = button_menu()

                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text('Пожалуйста, выберите:', reply_markup=reply_markup)
                return BUTTON


    async def create_sheduler_entity(self, update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.callback_query.from_user.id
        query = update.callback_query
        choice = query.data

        await query.answer()

        match choice:

            case "SCHEDULER_MESSAGE":

                await context.bot.send_message(chat_id=chat_id, text="Напиши текст, который нужно запланировать")

                return SCHEDULER_MESSAGE

            case "SCHEDULER_POLL":
                pass

