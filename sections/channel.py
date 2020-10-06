from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section
import textwrap

class Channel(Section):
    
    def __init__(self, data):
        super().__init__(data=data)
        self.TAG_ALL = 1
        self.TAG_POPULAR = 10

    def process_callback(self, call):
        #Channel;{action};{channel_id};{current_section_tag_id}{direction}
        action = call.data.split(";")[1]
        channel_id = int(call.data.split(";")[2])
        current_section_tag_id = int(call.data.split(";")[3])

        if action == "Select":
            self.send_channel_content(call=call, channel_id=channel_id, current_section_tag_id=current_section_tag_id)

        elif action == "ForbiddenTopics":
            self.send_channel_forbidden_topics(call=call, channel_id=channel_id)

        elif action == "Stats":
            self.send_channel_stats(call=call, channel_id=channel_id)

        elif action == "Reviews":
            self.send_channel_reviews(call=call, channel_id=channel_id)

        elif action == "Scroll":
            direction = call.data.split(";")[4]
            self.scroll_channel_content(call=call, channel_id=channel_id, direction=direction, current_section_tag_id=current_section_tag_id)

        else:
            self.in_development(call)
            return
        
        self.bot.answer_callback_query(call.id)

    def send_channel_content(self, call, channel_id, current_section_tag_id):
        markup = InlineKeyboardMarkup()

        # Get current channel and ID of neighbors channels
        current_channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        all_channels_in_section = self.data.get_channel(where=self.get_tag_filter(tag_id=current_section_tag_id), 
                                                        signs=["=", ">"])
        first_channel_id = all_channels_in_section[0].ChannelID
        last_channel_id = all_channels_in_section[-1].ChannelID

        # Заборонені теми
        forbiden_topics_callback = self.form_channel_callback(action="ForbiddenTopics", channel_id=channel_id, 
                                                              current_section_tag_id=current_section_tag_id,
                                                              prev_msg_action="Delete")
        forbiden_topics_text = self.data.message.button_channel_forbidden_topics
        forbiden_topics_btn = InlineKeyboardButton(text=forbiden_topics_text, callback_data=forbiden_topics_callback)
        markup.add(forbiden_topics_btn)

        #статистика & відгуки
        #statistic_url = self.data.get_channel(where={"ChannelID":channel_id})[0].Stats
        #statistic_text = self.data.message.button_channel_statistic
        #if statistic_url != None:
        #    statistic_btn = InlineKeyboardButton(text=statistic_text, url=statistic_url.strip())
        #    markup.add(statistic_btn)

        #reviews_callback = self.form_channel_callback(action="Reviews", channel_id=channel_id, current_section_tag_id=current_section_tag_id)
        #reviews_text = self.data.message.button_channel_reviews
        #reviews_button = InlineKeyboardButton(text=reviews_text, callback_data=reviews_callback)
        #markup.add(reviews_button)
        
        # Замовити
        order_callback = self.form_order_callback(action="Start", channel_id=channel_id)
        order_text = self.data.message.button_channel_order
        order_button = InlineKeyboardButton(text=order_text, callback_data=order_callback)
        markup.add(order_button)

        # Footer (⬅️ Назад ➡️)
        if current_channel.ChannelID == first_channel_id:
            left_arrow_callback = self.form_channel_callback(action="Scroll", channel_id=channel_id, 
                                                             current_section_tag_id=current_section_tag_id, 
                                                             direction="FirstPage")
            left_arrow_text = "✖️"
            left_arrow_btn = InlineKeyboardButton(text=left_arrow_text, callback_data=left_arrow_callback)
        else:
            left_arrow_callback = self.form_channel_callback(action="Scroll", channel_id=channel_id, 
                                                             current_section_tag_id=current_section_tag_id, 
                                                             direction="Left", prev_msg_action="Delete")
            left_arrow_text = "⬅️"
            left_arrow_btn = InlineKeyboardButton(text=left_arrow_text, callback_data=left_arrow_callback)
        
        back_btn_callback = self.form_tag_callback(action="Select", tag_id=current_section_tag_id,
                                                   prev_msg_action="Delete")
        back_btn = self.create_back_button(callback_data=back_btn_callback)

        if current_channel.ChannelID == last_channel_id:
            right_arrow_callback = self.form_channel_callback(action="Scroll", channel_id=channel_id, 
                                                              current_section_tag_id=current_section_tag_id, 
                                                              direction="LastPage")
            right_arrow_text = "✖️"
            right_arrow_btn = InlineKeyboardButton(text=right_arrow_text, callback_data=right_arrow_callback)
        else:
            right_arrow_callback = self.form_channel_callback(action="Scroll", channel_id=channel_id, 
                                                              current_section_tag_id=current_section_tag_id, 
                                                              direction="Right", prev_msg_action="Delete")
            right_arrow_text = "➡️"
            right_arrow_btn = InlineKeyboardButton(text=right_arrow_text, callback_data=right_arrow_callback)
        
        markup.add(left_arrow_btn, back_btn, right_arrow_btn)

        # Send message
        text, photo = self.create_channel_description(channel=current_channel)
        self.send_message(call=call, text=text, photo=photo, reply_markup=markup)

    def scroll_channel_content(self, call, channel_id, current_section_tag_id, direction):
        if direction == "FirstPage":
            first_page_text = self.data.message.tag_first_page
            self.bot.answer_callback_query(call.id, text=first_page_text)
            return
        if direction == "LastPage":
            last_page_text = self.data.message.tag_last_page
            self.bot.answer_callback_query(call.id, text=last_page_text)
            return

        current_channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        all_channels_in_section = self.data.get_channel(where=self.get_tag_filter(tag_id=current_section_tag_id), 
                                                        signs=["=", ">"])
        current_channel_index = all_channels_in_section.index(current_channel)

        if direction == "Right":
            next_channel_index = current_channel_index + 1
        if direction == "Left":
            next_channel_index = current_channel_index - 1
        
        next_channel_id = all_channels_in_section[next_channel_index].ChannelID

        self.send_channel_content(call=call, channel_id=next_channel_id, current_section_tag_id=current_section_tag_id)

    def send_channel_forbidden_topics(self, call, channel_id):
        self.in_development(call)

    def send_channel_stats(self, call, channel_id):
        self.in_development(call)

    def send_channel_reviews(self, call, channel_id):
        self.in_development(call)

    def get_tag_filter(self, tag_id):
        if tag_id == self.TAG_POPULAR:
            return {"Status":2}
        if tag_id == self.TAG_ALL:
            return None
        return {"TagID":tag_id, "Status":0}

    def create_channel_description(self, channel):
        def compress_string(string):
            return "\n".join(textwrap.wrap(string, 40, break_long_words=False))
        def get_delimiter(length=10):
            return " " * length + "\n"

        name = channel.Name.strip()
        link = channel.Link.strip()
        description = channel.Description.strip()
        price = channel.Price
        subscribers = channel.Subscribers
        photo = channel.Photo

        statistic = self.data.get_channel_stats(where={"StatisticID":channel.StatisticID})
        if len(statistic) > 0:
            statistic = statistic[0]
            stat_one_post = statistic.OnePost
            stat_one_post_last_day = statistic.OnePostLastDay
            stat_er = statistic.ER
            stat_er_last_day = statistic.ERLastDay
        else:
            statistic = None

        text = str()

        text += f"<b>{name}</b>\n"
        text += f"{link}\n"
        text += get_delimiter()

        
        text += f"{self.data.message.channel_description_description}:\n{compress_string(description)}\n"
        text += get_delimiter()

        text += f"{self.data.message.channel_description_subs} - {subscribers}\n"
        text += f"{self.data.message.channel_description_price} - {price} грн\n"

        if statistic:
            text += f"\n{self.data.message.channel_description_post_views}:\n"
            text += f"{self.data.message.channel_description_post_views_last_seven_days} - <b>{stat_one_post}</b>\n"
            text += f"{self.data.message.channel_description_post_views_last_day} - <b>{stat_one_post_last_day}</b>\n"
            
            text += f"\n{self.data.message.channel_description_er}:\n"
            text += f"{self.data.message.channel_description_er_last_seven_days} - <b>{stat_er}%</b>\n"
            text += f"{self.data.message.channel_description_er_last_day} - <b>{stat_er_last_day}%</b>\n"

        return text, photo

    # Overwrite for channel
    def form_order_callback(self, action, channel_id, prev_msg_action=None):
        return f"Order;{action};{channel_id};{prev_msg_action}"