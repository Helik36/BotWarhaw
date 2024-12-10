from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from Admin.KeyBoardButton.KeyButton_Main import button_menu
from Admin.BotBackend.Backend_channel import handler_view_channel
from Admin.database.actionWithDB.config_for_DB import get_from_db_data

command_button = (BUTTON, BACK,

 ACTION_WITH_CHANNEL,
 ADD_CHANNEL, DELETE_CHANNEL,

 ACTION_WITH_TOPIC,
 VIEW_TOPIC, CREATE_TOPIC, ADD_TOPIC, DELETE_TOPIC) = range(10)


class HandlerForAdmin:

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


    async def action_with_channel(self, update, _):

        query = update.callback_query
        choice = query.data
        await query.answer()

        match choice:

            case "VIEW_CHANNEL":
                await handler_view_channel(update, _)
                return BACK

            case "ADD_CHANNEL":
                await query.edit_message_text("Напишите название канала: ")
                return ADD_CHANNEL

            case "DELETE_CHANNEL":
                await query.edit_message_text("Напишите название канала (не ID), которое нужно удалить")
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
                await handler_view_channel(update, context)
                return BACK

            case "CREATE_TOPIC":

                keyboard = []

                channels = await get_from_db_data("channels")

                for id, name in channels.items():

                    keyboard.append([InlineKeyboardButton(f"{name}", callback_data="CREATE_TOPIC")])
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text("Для какого канала нужно создать топик?", reply_markup=reply_markup)

                return CREATE_TOPIC

            case "ADD_TOPIC":
                await query.edit_message_text("Напишите название канала: ")
                return ADD_TOPIC

            case "DELETE_TOPIC":
                await query.edit_message_text("Напишите название канала (не ID), которое нужно удалить")
                return DELETE_TOPIC

            case _:
                query = update.callback_query
                await query.answer()

                keyboard = button_menu()

                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text('Пожалуйста, выберите:', reply_markup=reply_markup)
                return BUTTON