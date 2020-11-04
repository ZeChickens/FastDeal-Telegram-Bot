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
        action, order_id = call.data.split(";")[1:3]

        if action == "Neworder":
            self.send_new_order(call=call, order_id=order_id)

        elif action == "Confirm":
            self.confirm_order(call, order_id=order_id)

        elif action == "Reject":
            self.reject_order(call, order_id=order_id)
        
        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def process_text(self, message):
        text = message.text

        if "FINISHED" in text:
            order_id = int(text.split("_")[1].split("@")[0])
            self.send_completed_order(chat_id=message.chat.id, order_id=order_id)

    def send_new_order(self, call, order_id):
        #in redaction
        markup = InlineKeyboardMarkup()
        text_to_redaction = self.data.message.redaction_new_order_notification
        btn_text = self.data.message.button_redaction_new_order
        btn_callback = self.form_order_callback(action="Description", order_id=order_id, prev_msg_action="Delete")
        btn = InlineKeyboardButton(text=btn_text, callback_data=btn_callback)
        markup.add(btn)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text_to_redaction, reply_markup=markup, parse_mode="HTML")

        #in client
        text_to_client = self.data.message.order_sent_to_redaction
        self.send_message(call, text=text_to_client)

    def send_completed_order(self, chat_id, order_id):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        # redaction
        text = self.data.message.redaction_results_sent_to_client
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text)

        # client
        self.order.send_order_status_notification(chat_id=client_chat_id, order_id=order_id)

    def confirm_order(self, call, order_id):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        #redaction
        self.send_message(call, text=call.message.text, reply_markup=None)
        notify_another_bot_text = self.data.message.form_redaction_confirm_order(order_id)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=notify_another_bot_text)

        #client
        self.data.update_order(set_={"Status":1}, where={"OrderID":order_id})
        self.order.send_order_status_notification(chat_id=client_chat_id, order_id=order_id)

    def reject_order(self, call, order_id):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        client_chat_id = client.ChatID

        self.send_message(call, text=call.message.text, reply_markup=None)
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