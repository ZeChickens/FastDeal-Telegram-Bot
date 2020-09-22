from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Main(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def send_start_message(self, message):
        text = self.data.message.start_bot

        markup = InlineKeyboardMarkup()

        start_btn = InlineKeyboardButton(text=self.data.message.button_start_work, callback_data="Tag;Start")
        markup.add(start_btn)
        
        # Feedback button
        #reviews_btn = InlineKeyboardButton(text=self.data.message.button_service_reviews, callback_data="IGNORE")
        #markup.add(reviews_btn)
        
        # Info button
        #info_btn = InlineKeyboardButton(text=self.data.message.button_service_info, callback_data="IGNORE")
        #markup.add(info_btn)
        
        # What is special button
        what_special_btn = InlineKeyboardButton(text=self.data.message.button_service_what_special,
                                                callback_data=self.form_main_callback(action="Special"))
        markup.add(what_special_btn)

        # How to use button
        how_to_use_button = InlineKeyboardButton(text=self.data.message.button_service_how_to_use,
                                                 callback_data=self.form_main_callback(action="HowToUse"))
        markup.add(how_to_use_button)

        self.bot.send_message(message.chat.id, text=text, reply_markup=markup)
