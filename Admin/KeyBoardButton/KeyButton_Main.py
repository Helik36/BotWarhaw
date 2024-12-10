from telegram import InlineKeyboardButton


def button_menu():

    keyboard = [
        [InlineKeyboardButton("Действие с каналами", callback_data='ACTION_WITH_CHANNEL')],
        [InlineKeyboardButton("Действие с топиками", callback_data='ACTION_WITH_TOPIC')]
    ]

    return keyboard