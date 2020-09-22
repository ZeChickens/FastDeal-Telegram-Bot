from telebot.types import InlineKeyboardButton

class Section:

    def __init__(self, data):
        self.data = data
        self.bot = self.data.bot

    def process_callback(self, call):
        pass

    def form_main_callback(self, action):
        return f"Main;{action}"

    def form_tag_callback(self, action, tag_id=None, direction=None, page=None):
        return f"Tag;{action};{tag_id};{direction};{page}"

    def form_channel_callback(self, action, channel_id, current_section_tag_id, direction=None):
        return f"Channel;{action};{channel_id};{current_section_tag_id};{direction}"

    def form_order_callback(self, action, order_id, prev_msg_action=None):
        return f"Order;{action};{order_id};{prev_msg_action}"

    def form_calendar_callback(self, action, channel_id, day, month, year, direction=None):
        return f"Order;Calendar;{action};{channel_id};{day};{month};{year};{direction}"

    def form_payment_callback(self, action, payment_id):
        return f"Payment;{action};{payment_id}"

    def form_redaction_callback(self, action, order_id):
        return f"Redaction;{action};{order_id}"

    def create_delete_button(self):
        return InlineKeyboardButton(text="❌", callback_data="DELETE")

    def oops(self, call):
        oops_text = self.data.message.oops
        self.bot.answer_callback_query(call.id, text=oops_text)