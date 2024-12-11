import logging

import telegram
from telegram import Update
from telegram.ext import Application, ContextTypes

from Admin.Scheduler.message_sheduler import scheduler_message


class Scheduler:

    def __init__(self, update, context):
        self.update = update
        self.context = context

    def create_new_cheduler(self):

        chat_id =  self.update.message.from_user.id
        logging.info("create scheduler message")

        self.context.job_queue.run_repeating(callback=scheduler_message, interval=5, chat_id=chat_id)

