from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

from inspect import currentframe

class Redaction(Section):

    def __init__(self, data, order):
        super().__init__(data=data)
        self.order = order

        self.REDACTION_CHAT_ID = self.data.REDACTION_CHAT_ID#-1001153596317

    def process_callback(self, call):
        #Redaction;{action};{order_id}
        action, order_id = call.data.split(";")[1:]
        chat_id = call.message.chat.id

        if action == "Neworder":
            message = call.message
            self.send_new_order(message, order_id=order_id)

        elif action == "Description":
            self.send_order_description(call, order_id=order_id)

        elif action == "Confirm":
            self.confirm_order(call, order_id=order_id)

        elif action == "Reject":
            self.reject_order(call, order_id=order_id)
        
        else:
            self.oops(call)
            return

        self.bot.answer_callback_query(call.id)

    def process_text(self, message):
        text = message.text

        if "FINISHED" in text:
            order_id = int(text.split("_")[1].split("@")[0])
            self.send_completed_order(chat_id=message.chat.id, order_id=order_id)

    def send_new_order(self, message, order_id):
        client_chat_id = message.chat.id
        message_id = message.message_id
        
        #in redaction
        markup = InlineKeyboardMarkup()
        text_to_redaction = self.data.message.redaction_new_order_notification
        btn_text = self.data.message.button_redaction_new_order
        btn_callback = self.form_redaction_callback(action="Description", order_id=order_id)
        btn = InlineKeyboardButton(text=btn_text, callback_data=btn_callback)
        markup.add(btn)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text_to_redaction, reply_markup=markup, parse_mode="HTML")

        #in client
        text_to_client = self.data.message.order_sent_to_redaction
        self.bot.edit_message_text(chat_id=client_chat_id, message_id=message_id, text=text_to_client, reply_markup=None, parse_mode="HTML")

    def send_completed_order(self, chat_id, order_id):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        #redaction
        text = self.data.message.redaction_results_sent_to_client
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text)

        #client
        self.order.send_order_status_notification(chat_id=client_chat_id, order_id=order_id)

    def send_order_description(self, call, order_id):
        chat_id = self.REDACTION_CHAT_ID
        self.bot.delete_message(chat_id, call.message.message_id)

        text, photo = self.order.form_order_description(order_id=order_id)
        markup = InlineKeyboardMarkup()
        
        confirm_button_text = "✅"
        confirm_button_callback = self.form_redaction_callback(action="Confirm", order_id=order_id)
        confirm_button = InlineKeyboardButton(text=confirm_button_text, callback_data=confirm_button_callback)

        reject_button_text = "❌"
        reject_button_callback = self.form_redaction_callback(action="Reject", order_id=order_id)
        reject_button = InlineKeyboardButton(text=reject_button_text, callback_data=reject_button_callback)
        
        markup.add(confirm_button, reject_button)

        if photo is not None:
            self.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    def confirm_order(self, call, order_id):
        self.bot.edit_message_reply_markup(chat_id=self.REDACTION_CHAT_ID, message_id=call.message.message_id, reply_markup=None)
        
        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        #redaction
        notify_another_bot_text = self.data.message.form_redaction_confirm_order(order_id)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=notify_another_bot_text)

        #client
        self.data.update_order(set_={"Status":1}, where={"OrderID":order_id})
        self.order.send_order_status_notification(chat_id=client_chat_id, order_id=order_id)

    def reject_order(self, call, order_id):
        self.bot.edit_message_reply_markup(chat_id=self.REDACTION_CHAT_ID, message_id=call.message.message_id, reply_markup=None)

        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        input_reject_reason_text = self.data.message.redaction_reject_reason
        message = self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=input_reject_reason_text)
        
        self.bot.register_next_step_handler(message, self.complete_rejection, client_chat_id=client_chat_id, order_id=order_id)
    
    def complete_rejection(self, message, **kwargs):
        client_chat_id = kwargs["client_chat_id"]
        order_id = kwargs["order_id"]

        redaction_comment = message.text

        self.data.update_order(set_={"RedactionComment":redaction_comment}, where={"OrderId":order_id})
        self.data.update_order(set_={"Status":-1}, where={"OrderId":order_id})

        #redaction
        order_rejected_text = self.data.message.redaction_reject_order
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=order_rejected_text)

        #client
        self.order.send_order_status_notification(chat_id=client_chat_id, order_id=order_id)

    def command_in_group_error(self):
        text = self.data.message.redaction_command_error

        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text)