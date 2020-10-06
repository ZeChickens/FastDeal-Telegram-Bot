from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Main(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def process_callback(self, call):
        action = call.data.split(";")[1]

        if action == "Start":
            self.send_start_message(call=call)

        elif action == "Special":
            self.in_development(call)

        elif action == "HowToUse":
            self.in_development(call)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_start_message(self, chat_id=None, call=None):
        """Send start message with introduction to bot.\n
        Specify chat_id if it called through command, otherwise
        specify call if it called after button pressed.
        """
        text = self.data.message.start_bot

        markup = InlineKeyboardMarkup()

        start_btn_text = self.data.message.button_start_work
        start_btn_callback = self.form_tag_callback(action="Start", prev_msg_action="Edit")
        start_btn = InlineKeyboardButton(text=start_btn_text, callback_data=start_btn_callback)
        markup.add(start_btn)
        
        # Feedback button
        #reviews_btn = InlineKeyboardButton(text=self.data.message.button_service_reviews, callback_data="IGNORE")
        #markup.add(reviews_btn)
        
        # Info button
        #info_btn = InlineKeyboardButton(text=self.data.message.button_service_info, callback_data="IGNORE")
        #markup.add(info_btn)

        # Orders button
        orders_btn_text = self.data.message.button_order_my
        orders_btn_callback = self.form_order_callback(action="List", order_id=None, prev_msg_action="Edit")
        orders_btn = InlineKeyboardButton(text=orders_btn_text, callback_data=orders_btn_callback)
        markup.add(orders_btn)        
        
        # What is special button
        what_special_btn_text = self.data.message.button_service_what_special
        what_special_btn_callback = self.form_main_callback(action="Special", prev_msg_action="Edit")
        what_special_btn = InlineKeyboardButton(text=what_special_btn_text,
                                                callback_data=what_special_btn_callback)
        markup.add(what_special_btn)

        # How to use button
        how_to_use_btn_text = self.data.message.button_service_how_to_use
        how_to_use_btn_callback = self.form_main_callback(action="HowToUse", prev_msg_action="Edit")
        how_to_use_btn = InlineKeyboardButton(text=how_to_use_btn_text,
                                                 callback_data=how_to_use_btn_callback)
        markup.add(how_to_use_btn)

        if chat_id is not None:
            self.bot.send_message(chat_id, text=text, reply_markup=markup)
        else:
            self.send_message(call, text=text, reply_markup=markup)
