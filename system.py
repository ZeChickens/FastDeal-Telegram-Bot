from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime

import error_logging

class System:

    def __init__(self, data):
        self.data = data
        self.bot = self.data.bot

        self.REDACTION_CHAT_ID = self.data.REDACTION_CHAT_ID

    def add_client(self, message):
        username = message.chat.username if message.chat.username is not None else "Безіменний"
        name = message.chat.first_name if message.chat.first_name is not None else "Безіменний"
        surname = message.chat.last_name if message.chat.last_name is not None else "0"
        register_date = datetime.now()
        last_interaction = register_date
        chat_id = message.chat.id

        try:
            client_registered = len(self.data.get_client(where={"ChatID":chat_id})) == 1
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(), additional_info=None)
            return

        if chat_id == self.REDACTION_CHAT_ID:
            return
        if not client_registered:
            self.data.add_client(chat_id=chat_id, username=username, name=name,
                                 surname=surname, register_date=register_date, 
                                 last_interaction_time=last_interaction)

    def update_client_interaction_time(self, message):
        date = datetime.now()
        client_chat_id = message.chat.id

        if client_chat_id == self.REDACTION_CHAT_ID:
            return

        self.data.update_client(set_={"LastInteractionTime":date}, where={"ChatID":client_chat_id})

    def clear(self, message):
        chat_id = message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id=chat_id)