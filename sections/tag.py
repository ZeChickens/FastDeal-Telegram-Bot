from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section
from inspect import currentframe

class Tag(Section):
    def __init__(self, data):
        super().__init__(data=data)

        self.START_STRUCTURE = [1, 2, 2, 2, 2]#, 1]
        self.CONTENT_SIZE = 5
        self.MAX_CHANNEL_LENGTH = 20
        self.TAG_ALL = 1
        self.TAG_POPULAR = 10

    def process_callback(self, call):
        #Tag;{action};{tag_id};{direction}
        action = call.data.split(";")[1]

        if action == "Start":
            self.send_start_content(call=call)

        elif action == "Select":
            tag_id = call.data.split(";")[2]
            self.send_tag_content(call=call , tag_id=int(tag_id))

        elif action == "Scroll":
            tag_id, direction = call.data.split(";")[2:4]
            self.scroll_tag_content(call=call , direction=direction, tag_id=int(tag_id))

        elif action == "Back":
            self.send_start_content(call=call)

        elif action == "Empty":
            empty_text = self.data.message.tag_empty
            self.bot.answer_callback_query(call.id, text=empty_text)
            return
            
        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)


    def send_start_content(self, call):
        text = self.data.message.tag_choose

        markup = InlineKeyboardMarkup()

        tags = self.data.get_tag()
        tag_index = 0
        for row in self.START_STRUCTURE:
            btn_row = list()
            for _ in range(row):
                tag_id = tags[tag_index].TagID
                tag_sign = tags[tag_index].Sign
                callback = self.form_tag_callback(action="Select", tag_id=tag_id, prev_msg_action="Edit")
                tag_button = InlineKeyboardButton(text=tag_sign, callback_data=callback)
                btn_row += [tag_button]
                tag_index += 1
            markup.add(*btn_row)

        # Back Button
        back_button_callback = self.form_main_callback(action="Start", prev_msg_action="Edit")
        back_button = self.create_back_button(callback_data=back_button_callback)
        markup.add(back_button)

        self.send_message(call=call, text=text, reply_markup=markup)
        
    def send_tag_content(self, call, tag_id, page=1):
        def cut_channel_name(name):
            if len(name) > self.MAX_CHANNEL_LENGTH:
                cut_name = name[:self.MAX_CHANNEL_LENGTH] + "..."
                return cut_name
            return name

        # get channels by current tag
        where, signs = self.get_tag_filter(tag_id=tag_id)
        channels_by_tag = self.data.get_channel(where=where, signs=signs)
        channel_number = len(channels_by_tag)

        # get channels list of current page
        page_number = int(channel_number / self.CONTENT_SIZE) if channel_number % self.CONTENT_SIZE == 0 else int(channel_number / self.CONTENT_SIZE) + 1
        if page_number == 0:
            page_number = 1
        
        last_channel_index = page * self.CONTENT_SIZE
        first_channel_index = last_channel_index - self.CONTENT_SIZE
        if last_channel_index > channel_number:
            last_channel_index -= last_channel_index - channel_number
        
        current_page_channels = channels_by_tag[first_channel_index:last_channel_index]
        markup = InlineKeyboardMarkup()

        # head button (back)
        tag = self.data.get_tag(where={"TagID":tag_id})[0]
        head_button_callback = "IGNORE"
        head_button = InlineKeyboardButton(text=f"{tag.Sign}", callback_data=head_button_callback)
        markup.add(head_button)

        # channel buttons
        for channel in current_page_channels:
            callback = self.form_channel_callback(action="Select", channel_id=channel.ChannelID, 
                                                  current_section_tag_id=tag_id, prev_msg_action="Delete")
            
            # button design
            channel_subscribers = channel.Subscribers
            channel_name = cut_channel_name(name=channel.Name.strip())
            button_text = f"{channel_name} 🔸{channel_subscribers}" ##############
            channel_button = InlineKeyboardButton(text=button_text, callback_data=callback)
            markup.add(channel_button)
        if len(current_page_channels) == 0:
            text = self.data.message.button_tag_empty
            callback = self.form_tag_callback(action="Empty")
            markup.add(InlineKeyboardButton(text, callback_data=callback))

        # Counter Button
        callback = "IGNORE"
        page_counter_button = InlineKeyboardButton(text=f"{page}/{page_number}", callback_data=callback)
        markup.add(page_counter_button)

        # Footer
        if page == 1:
            callback = self.form_tag_callback(action="Scroll", tag_id=tag_id, direction="FirstPage")
            scroll_left_button = InlineKeyboardButton(text="✖️", callback_data=callback)
        else:
            callback = self.form_tag_callback(action="Scroll", tag_id=tag_id, direction="Left", page=page, prev_msg_action="Edit")
            scroll_left_button = InlineKeyboardButton(text="⬅️", callback_data=callback)
            
        back_button_callback = self.form_tag_callback(action="Start", prev_msg_action="Edit")
        back_button = self.create_back_button(callback_data=back_button_callback)

        if page == page_number:
            callback = self.form_tag_callback(action="Scroll", tag_id=tag_id, direction="LastPage")
            scroll_right_button = InlineKeyboardButton(text="✖️", callback_data=callback)
        else:
            callback = self.form_tag_callback(action="Scroll", tag_id=tag_id, direction="Right", page=page, prev_msg_action="Edit")
            scroll_right_button = InlineKeyboardButton(text="➡️", callback_data=callback)

        markup.add(scroll_left_button, back_button, scroll_right_button)

        text = self.data.message.channel_choose
        self.send_message(call=call, text=text, reply_markup=markup)
        
    def scroll_tag_content(self, call, direction, tag_id):
        if direction == "FirstPage":
            first_page_text = self.data.message.tag_first_page
            self.bot.answer_callback_query(call.id, text=first_page_text)
            return
        if direction == "LastPage":
            last_page_text = self.data.message.tag_last_page
            self.bot.answer_callback_query(call.id, text=last_page_text)
            return

        current_page = int(call.data.split(";")[4])
        if direction == "Right":
            current_page += 1
        if direction == "Left":
            current_page -= 1
        self.send_tag_content(call=call, tag_id=tag_id, page=current_page)

    def get_tag_filter(self, tag_id):
        if tag_id == self.TAG_POPULAR:
            return {"Status":2}, ["="]
        if tag_id == self.TAG_ALL:
            return {"Status":0}, [">"]
        return {"TagID":tag_id, "Status":0}, ["=", ">"]