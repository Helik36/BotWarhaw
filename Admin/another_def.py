
async def get_previous_message(update, context):

    message_id = update.callback_query.message.message_id

    return message_id