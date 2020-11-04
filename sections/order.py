from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import date, datetime, timezone
import calendar
import json
import requests
from threading import Thread
from time import sleep
import hmac

from sections.section import Section

import error_logging

class Order(Section):
    def __init__(self, data):
        super().__init__(data=data)
        self.calendar = Calendar(data)
        self.payment = Payment(data)

    def process_callback(self, call):
        #Order;{action};{order_id}
        #Order;Confirm;{channel_id};{day};{month};{year}
        #Order;Calendar;{action};{channel_id};{day};{month};{year};{direction}
        action = call.data.split(";")[1]

        if action == "Start":
            channel_id = int(call.data.split(";")[2])
            self.start_order(call, channel_id)

        elif action == "Calendar":
            self.calendar.process_callback(call=call)
        
        elif action == "Confirm":
            channel_id = int(call.data.split(";")[2])
            day, month, year = call.data.split(";")[3:6]
            date_ = date(int(year), int(month), int(day))
            self.confirm_order_date(call, channel_id=channel_id, date=date_)

        elif action == "Description":
            order_id = int(call.data.split(";")[2])
            self.send_order_description(call, order_id=order_id)

        elif action == "List":
            self.send_order_list(call=call)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_order_list(self, chat_id=None, call=None): 
        """Send start message with introduction to bot.\n
        Specify chat_id if it called through command, otherwise
        specify call if it called after button pressed.
        """     
        if call is not None:
            chat_id = call.message.chat.id

        if chat_id == self.data.REDACTION_CHAT_ID:
            where_clause = None #get all orders
        else:
            client = self.data.get_client(where={"ChatID":chat_id})[0]
            where_clause = {"ClientID":client.ClientID}
        orders = self.data.get_order(where=where_clause)
        
        markup = InlineKeyboardMarkup()
        for order in orders:
            button = self.create_order_description_button(order=order)
            markup.add(button)

        # if list is called from main menu than send "Back" button
        if call is not None and chat_id != self.data.REDACTION_CHAT_ID:
            back_button_callback = self.form_main_callback(action="Start", prev_msg_action="Edit")
            back_button = self.create_back_button(callback_data=back_button_callback)
            markup.add(back_button)
        else:
            markup.add(self.create_delete_button())

        text = self.data.message.order_list
        if call is None:
            self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        else:
            self.send_message(call=call, text=text, reply_markup=markup)

    def send_order_description(self, call, order_id):
        chat_id = call.message.chat.id
        text, photo = self.form_order_description(order_id=order_id)
        markup = InlineKeyboardMarkup()

        # If called in Redaction then display special buttons
        if chat_id == self.data.REDACTION_CHAT_ID:
            order = self.data.get_order(where={"OrderID":order_id})[0]
            redaction_buttons = self.create_redaction_buttons(order=order)
            for button in redaction_buttons:
                # if few button in a row
                if isinstance(button, list):
                    markup.add(*button)
                else:
                    markup.add(button)

        # Back button
        back_button_callback = self.form_order_callback(action="List", order_id=None, prev_msg_action="Delete")
        back_button = self.create_back_button(callback_data=back_button_callback)
        markup.add(back_button)

        self.send_message(call=call, text=text, photo=photo, reply_markup=markup)

    def send_order_status_notification(self, chat_id, order_id):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        text = self.data.get_order_status(where={"StatusID":order.Status})[0].Notification

        button = self.create_order_description_button(order)
        markup = InlineKeyboardMarkup()
        markup.add(button)

        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    def start_order(self, call, channel_id):
        self.calendar.send_calendar(call, channel_id)

    def confirm_order_date(self, call, channel_id, date):
        self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

        self.process_order_forming(call.message, step=1, date=date, channel_id=channel_id)

    def process_order_forming(self, message, **kwargs):
        step = kwargs["step"]
        date = kwargs["date"]
        channel_id = kwargs["channel_id"]
        
        # Keyboard button to cancel order
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        reply_markup.add(KeyboardButton(text=self.data.message.button_order_cancel))

        if message.text == self.data.message.button_order_cancel:
            canceled_order_text = self.data.message.order_canceled
            self.bot.send_message(chat_id=message.chat.id, text=canceled_order_text, reply_markup=ReplyKeyboardRemove())
            return

        if step == 1:
            step += 1
            text = self.data.message.order_wait_photo
            button_text = self.data.message.button_order_no_photo
            reply_markup.add(KeyboardButton(text=button_text))

            self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="HTML")
            
            self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.process_order_forming, step=step, date=date, channel_id=channel_id)
            return
        if step == 2:
            if message.text == self.data.message.button_order_no_photo:
                step += 1
                ad_photo = None
                text = self.data.message.order_wait_text
                message = self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="HTML")
            elif message.content_type == "photo":
                step += 1
                ad_photo = message.json['photo'][0]['file_id']
                text = self.data.message.order_wait_text
                message = self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="HTML")
            else:#INCORRECT
                step -= 1
                self.process_order_forming(message, step=step, date=date, channel_id=channel_id)#INCORRECT
                return

            self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.process_order_forming, step=step, date=date, photo=ad_photo, channel_id=channel_id)
            return
        if step == 3:
            ad_photo = kwargs["photo"]
            if message.content_type == "text":
                step += 1
                ad_text = message.text
                text = self.data.message.order_wait_comment
            else:
                ad_text = None
                text = self.data.message.order_wait_text

            message = self.bot.send_message(chat_id=message.chat.id, text=text, parse_mode="HTML")
            self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.process_order_forming, step=step, date=date, photo=ad_photo, text=ad_text, channel_id=channel_id)
            return
        if step == 4:
            ad_photo = kwargs["photo"]
            ad_text = kwargs["text"]
            if message.content_type == "text":
                step += 1
                ad_comment = message.text
            else:
                ad_comment = "-" 

            content = {
                "Photo":ad_photo,
                "Text":ad_text,
                "Comment":ad_comment,
                "PostDate":date
            }

            # Remove keyboard
            temp_msg = self.bot.send_message(chat_id=message.chat.id, text="temp", reply_markup=ReplyKeyboardRemove())
            self.bot.delete_message(chat_id=temp_msg.chat.id, message_id=temp_msg.message_id)
            
            # Start Payment Thread
            payment_thread = Thread(target=self.payment.process_payment,
                                    kwargs={"message":message, "channel_id":channel_id, 
                                    "order_forming":self.complete_order_forming, "content":content})
            payment_thread.start()
            return

            #self.complete_order_forming(bot, message, channel_id=channel_id, photo=ad_photo, text=ad_text, comment=ad_comment, post_date=date)

    def complete_order_forming(self, message, channel_id, photo, text, comment, post_date):
        client_chat_id = message.chat.id
        client_id = self.data.get_client(where={"ChatID":client_chat_id})[0].ClientID
        order_date = datetime.now()

        self.data.add_order(client_id=client_id, channel_id=channel_id, 
                            text=text, photo=photo, comment=comment, 
                            post_date=post_date, order_date=order_date)

        order_id = self.data.get_order(where={"ClientID":client_id})[-1].OrderID

        text = self.data.message.order_formed
        markup = InlineKeyboardMarkup()

        send_to_redaction_btn_text = self.data.message.button_order_send_to_redaction
        send_to_redaction_btn_callback = self.form_redaction_callback(action="Neworder", order_id=order_id, prev_msg_action="Edit")
        send_to_redaction_btn = InlineKeyboardButton(text=send_to_redaction_btn_text, callback_data=send_to_redaction_btn_callback)
        markup.add(send_to_redaction_btn)

        self.bot.send_message(chat_id=client_chat_id, text=text, reply_markup=markup)

        return order_id

    def form_order_description(self, order_id):
        def get_delimiter(length=10):
            return "➖" * length + "\n"
        def get_status(status):
            if status == -1:
                return self.data.message.order_status_redaction_rejected
            if status == 0:
                pass
            if status == 1:
                pass
        order = self.data.get_order(where={"OrderID":order_id})[0]
        
        text = str()

        ad_text = order.Text.strip()
        ad_photo = order.Photo
        ad_client_comment = order.Comment.strip()
        #ad_redaction_comment = order.RedactionComment.strip()
        ad_post_date = order.PostDate
        ad_order_date = order.OrderDate
        order_status = self.data.get_order_status(where={"StatusID":order.Status})[0].Description

        text += f"<b>{self.data.message.order_description_text}</b>\n"
        text += f"{order.Text}\n"
        text += get_delimiter()

        text += f"<b>{self.data.message.order_description_client_comment}</b>\n"
        text += f"{order.Comment}\n"
        text += get_delimiter()

        if order.Status >= 2:
            post_statistic = self.data.get_post_statistic(where={"PostStatisticID":order.PostStatisticID})[0]
            post_statistic_link = post_statistic.PostLink
            text += f"<b>{self.data.message.order_description_post_link}</b> - {post_statistic_link}\n"

        text += f"<b>{self.data.message.order_description_status}</b>{order_status}\n"

        return text, order.Photo

    def create_redaction_buttons(self, order):
        order_id = order.OrderID
        buttons = list()

        # REFUND Button
        payment = self.data.get_payment(where={"OrderID":order_id})
        if len(payment) > 0:
            payment = payment[0]
            payment_transaction_status = payment.TransactionStatus
            if payment_transaction_status == "Approved":
                payment_id = payment.PaymentID
                refund_button_text = self.data.message.button_payment_refund
                refund_button_callback = self.form_payment_callback(action="Refund", payment_id=payment_id)
                refund_button = InlineKeyboardButton(text=refund_button_text, callback_data=refund_button_callback)
                buttons += [refund_button]

        
        # Confirm and reject order
        if order.Status == 0:
            confirm_button_text = "✅"
            confirm_button_callback = self.form_redaction_callback(action="Confirm", order_id=order_id, prev_msg_action="Edit")
            confirm_button = InlineKeyboardButton(text=confirm_button_text, callback_data=confirm_button_callback)

            reject_button_text = "❌"
            reject_button_callback = self.form_redaction_callback(action="Reject", order_id=order_id, prev_msg_action="Edit")
            reject_button = InlineKeyboardButton(text=reject_button_text, callback_data=reject_button_callback)
            buttons += [[confirm_button, reject_button]]

        return buttons

    def create_order_description_button(self, order):
        def get_status_emoji(order_status):
            if order_status <= -1:
                return "✖️"
            if order_status < 2:
                return "🕐"
            if order_status == 2:
                return "📝"
            if order_status == 3:
                return "✅"
        def cut_channel_name(name, length=25):
            if len(name) > length:
                cut_name = name[:length] + "..."
                return cut_name
            return name
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]

        ch_name = cut_channel_name(name=channel.Name.strip())
        emoji = get_status_emoji(order_status=order.Status)
        btn_text = f"{ch_name} {emoji}"

        callback = self.form_order_callback(action="Description", order_id=order.OrderID, prev_msg_action="Delete")

        return InlineKeyboardButton(text=btn_text, callback_data=callback)

class Calendar(Section):

    def __init__(self, data):
        super().__init__(data=data)

    def process_callback(self, call):
        #Order;Calendar;{action};{channel_id};{day};{month};{year};{direction};
        info = call.data.split(";")
        action = info[2]
        channel_id = info[3]

        if action == "Select":
            self.send_date_confirmation(call, channel_id=channel_id)

        elif action == "Scroll":
            direction = info[7]
            self.scroll_calendar(call, channel_id=channel_id, direction=direction)

        else:
            self.in_development(call)
            return
        
        self.bot.answer_callback_query(call.id)

    def send_calendar(self, call, channel_id, month=None, year=None):
        now = datetime.now()
        year = now.year if year is None else year
        month = now.month if month is None else month

        data_ignore = "IGNORE"
        markup = {"inline_keyboard": []}

        # First row - Month and Year
        row = [{"text": calendar.month_name[month] + " " + str(year), "callback_data": data_ignore}]
        markup["inline_keyboard"].append(row)

        # Second row - Week Days
        row = []
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            row.append({"text": day, "callback_data": data_ignore})
        markup["inline_keyboard"].append(row)

        # Next rows - Each Day
        my_calendar = calendar.monthcalendar(year, month)
        for week in my_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append({"text": " ", "callback_data": data_ignore})
                else:
                    is_available = self.check_order_date_availability(channel_id=channel_id, day=day, month=month, year=year)
                    if is_available is True:
                        callback = self.form_calendar_callback(action="Select", channel_id=channel_id,
                                                               day=day, month=month, year=year,
                                                               prev_msg_action="Edit")
                        row.append({"text": f"{day}", "callback_data": callback})
                    else:
                        row.append({"text": "✖️", "callback_data": data_ignore})
            markup["inline_keyboard"].append(row)

        # Last row - Buttons
        left_callback = self.form_calendar_callback(action="Scroll", channel_id=channel_id,
                                                    day=day, month=month, year=year, direction="Left",
                                                    prev_msg_action="Edit")
        right_callback = self.form_calendar_callback(action="Scroll", channel_id=channel_id,
                                                    day=day, month=month, year=year, direction="Right",
                                                    prev_msg_action="Edit")
        row = [{"text": "<", "callback_data": left_callback},
               {"text": "❌", "callback_data": "DELETE"},
               {"text": ">", "callback_data": right_callback}]
        markup["inline_keyboard"].append(row)


        markup = json.dumps(markup, ensure_ascii=False)
        text = self.data.message.calendar_choose_date
        self.send_message(call=call, text=text, reply_markup=markup)

    def scroll_calendar(self, call, channel_id, direction):
        month = int(call.data.split(";")[5])
        year = int(call.data.split(";")[6])

        if direction == "Right":
            month += 1
        if direction == "Left":
            month -= 1

        if month < 1:
            month = 12
            year -= 1
        if month > 12:
            month = 1
            year += 1

        self.send_calendar(call, channel_id=channel_id, month=month, year=year)

    def send_date_confirmation(self, call, channel_id):
        day = int(call.data.split(";")[4])
        month = int(call.data.split(";")[5])
        year = int(call.data.split(";")[6])
        date_ = date(year, month, day)

        text = self.data.message.form_calendar_confirm_date(date=date_)
        markup = InlineKeyboardMarkup()

        confirm_callback = self.form_order_callback(action="Confirm", channel_id=channel_id, day=day, month=month, year=year)
        confirm_button = InlineKeyboardButton(text="✅", callback_data=confirm_callback)
        decline_callback = self.form_order_callback(action="Start", channel_id=channel_id, prev_msg_action="Delete")
        decline_button = InlineKeyboardButton(text="❌", callback_data=decline_callback)
        markup.add(confirm_button, decline_button)

        self.send_message(call=call, text=text, reply_markup=markup)

    # Overwrite for Calendar
    def form_order_callback(self, action, channel_id, day=None, month=None, year=None, prev_msg_action=None):
        return f"Order;{action};{channel_id};{day};{month};{year};{prev_msg_action}"

    def check_order_date_availability(self, channel_id, day, month, year):
        current_date = datetime.now()
        if year <= current_date.year and month < current_date.month:
            return False
        elif day < current_date.day and month == current_date.month:
            return False

        date_ = date(year, month, day)
        order = self.data.get_order(where={"ChannelID":channel_id, "PostDate":date_, "Status":0}, signs=["=", "=", ">="])
        if len(order) > 0:
            return False

        return True

class Payment:

    API_ENDPOINT = "https://api.wayforpay.com/api"	
    merchant_account = "t_me88"
    merchant_domain_name = "https://t.me/poopyduster_bot"
    merchant_transaction_type = "AUTO"
    api_version = "1" 
    secret_key = "9b8ccf714a845bd2867421173be71920457aee94"
    currency = "UAH" 
    payment_destination_text = "Telegram channel"

    PRICE_COEF = 1#.025

    pay_check_time = 10     #30
    pay_check_number = 40   #30

    refund_check_time = 30 # Delay after each check for cost refund

    def __init__(self, data):
        self.data = data
        self.bot = self.data.bot
    
    def process_callback(self, call):
        #Payment;{action};{payment_id}
        action = call.data.split(";")[1]

        if action == "Refund":
            payment_id = call.data.split(";")[2]
            refund_thread = Thread(target=self.process_refund,
                                   kwargs={"message":call.message, "payment_id":payment_id})
            refund_thread.start()

        else:
            in_development_text = self.data.message.under_development
            self.bot.answer_callback_query(call.id, text=in_development_text)
            return

        self.bot.answer_callback_query(call.id)

    def process_payment(self, message, channel_id, order_forming, content):
        chat_id = message.chat.id
        ad_photo = content["Photo"]
        ad_text = content["Text"]
        ad_comment = content["Comment"]
        ad_post_date = content["PostDate"]

        channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        
        # create invoice and check it's status
        invoice_data, order_reference = self.api_create_invoice(price=channel.Price, channel_name=channel.Name)
        invoice_link = invoice_data["invoiceUrl"]
        payment_status_response = self.api_check_status(order_reference)

        # add new paymnet to DB
        self.add_new_payment(order_id=None, payment_status_response=payment_status_response)

        # form receipt and send it to client
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="Оплатити", url=invoice_link)
        markup.add(button)
        receipt_text = self.data.message.form_order_receipt(channel.Name.strip(), ad_post_date, channel.Price)
        try:
            message = self.bot.send_message(chat_id=message.chat.id, text=receipt_text, reply_markup=markup, parse_mode="HTML")
        except:
            self.bot.send_message(chat_id=chat_id, text=self.data.message.order_payment_error)
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(), additional_info="Вірогідно OrderReference")
            return

        # check payment status
        succesful_payment, payment_status_response = self.check_pay(message=message,
                                                                    order_reference=order_reference)

        # form order if payment was succesful (add it to DB)
        if succesful_payment:
            order_id = order_forming(message, channel_id, ad_photo, ad_text, ad_comment, ad_post_date)
        else:
            order_id = None
            message_id = message.message_id
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None, text=self.data.message.order_payment_time_is_up)

        # update payment status
        self.add_new_payment(order_id=order_id, payment_status_response=payment_status_response,
                             update=True)     

    def process_refund(self, message, payment_id):
        """
            process costs refund to client
            1) refund costs
            2) check refund
            3) update payment instance in DB
            4) send message to Redaction about succesful refund
            5) send message to Client about succesful refund specifying amount in message
        """

        payment = self.data.get_payment(where={"PaymentID":payment_id})[0]
        order = self.data.get_order(where={"OrderID":payment.OrderID})[0]
        client = self.data.get_client(where={"ClientID":order.ClientID})[0]
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]

        order_reference = payment.OrderReference
        amount = payment.Amount

        # Refund costs
        self.api_refund(order_reference=order_reference, amount=amount)

        # Check for refund
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        message = self.bot.send_message(chat_id=message.chat.id, text=self.data.message.order_payment_refund_wait)
        self.check_refund(order_reference=order_reference)

        # Update payment in Database
        payment_status_response = self.api_check_status(order_reference=order_reference)
        self.add_new_payment(order_id=order.OrderID, payment_status_response=payment_status_response,
                             update=True)

        # Send message to Redaction
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_message(chat_id=message.chat.id, text=self.data.message.order_payment_refund_completed)

        # Send message to Client about succesful refund with additional info about order
        client_chat_id = client.ChatID
        payment = self.data.get_payment(where={"PaymentID":payment_id})[0]
        message_text = self.data.message.form_order_refund_info(channel_name=channel.Name,
                                                                order_id=order.OrderID, 
                                                                refund_amount=payment.RefundAmount)
        self.bot.send_message(chat_id=client_chat_id, text=message_text, parse_mode="HTML")

    def check_pay(self, message, order_reference):
        """Main method for approving pay 
		connect with API and try to approve CURRENT order (orderReference)!"""

        payment_status_response = self.api_check_status(order_reference=order_reference)
        transaction_status = payment_status_response['transactionStatus']
        succesful_payment = False

        check = 0
        edit = False
        while check < self.pay_check_number+1:
            if transaction_status == "Approved":
                succesful_payment = True
                self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                break

            elif transaction_status == "Pending":
                check=1
                if edit is False:
                    self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                          text=self.data.message.order_payment_confirmation_wait, reply_markup=None)
                    edit = True

            sleep(self.pay_check_time)
            payment_status_response = self.api_check_status(order_reference=order_reference)
            transaction_status = payment_status_response['transactionStatus']

            self.add_new_payment(order_id=None, payment_status_response=payment_status_response,
                                 update=True)
            
            check += 1
        
        return succesful_payment, payment_status_response

    def check_refund(self, order_reference):

        payment_status_response = self.api_check_status(order_reference=order_reference)
        transaction_status = payment_status_response['transactionStatus']

        while transaction_status != "Refunded":

            sleep(self.refund_check_time)

            payment_status_response = self.api_check_status(order_reference=order_reference)
            transaction_status = payment_status_response['transactionStatus']

    def update_order_reference(self):
        """method for increasing and updating order reference 
        	would be better to take order reference from outside"""
        

        last_payment = self.data.get_payment(order_by={"OrderReference":"ASC"})[-1]
        code = last_payment.OrderReference

        letters = code[:2]
        digits = code[2:]
        new_number = str(int(digits)+1)
        zeros = '0' * (len(digits)-len(new_number))
        new_order_reference = letters + zeros + new_number

        return new_order_reference

    def add_new_payment(self, order_id, payment_status_response, update=False):
        """
            Function can also update existed payment.
            If update is True then payment_id must be given
        """
        order_reference = payment_status_response["orderReference"]
        reason = payment_status_response["reason"]
        amount = payment_status_response["amount"]
        currency = payment_status_response["currency"]
        card_pan = payment_status_response["cardPan"]
        card_type = payment_status_response["cardType"]
        issuer_bank_country  = payment_status_response["issuerBankCountry"]
        issuer_bank_name = payment_status_response["issuerBankName"]
        transaction_status = payment_status_response["transactionStatus"]
        refund_amount = payment_status_response["refundAmount"]
        fee = payment_status_response["fee"]
        merchant_signature = payment_status_response["merchantSignature"]

        if isinstance(payment_status_response["createdDate"], int):
            created_date = datetime.utcfromtimestamp(payment_status_response["createdDate"])
            processing_date = datetime.utcfromtimestamp(payment_status_response["processingDate"])
        else:
            created_date = datetime.now()
            processing_date = None
        
        if update is True:
            self.data.update_payment(set_={"OrderID":order_id, "CreatedDate":created_date, "ProcessingDate":processing_date,
                                     "Amount":amount, "Fee":fee, "Reason":reason, "CardPan":card_pan, "CardType":card_type,
                                     "Currency":currency, "IssuerBankCountry":issuer_bank_country, "IssuerBankName":issuer_bank_name,
                                     "TransactionStatus":transaction_status, "RefundAmount":refund_amount}, 
                                     where={"OrderReference":order_reference})
        else:
            self.data.add_payment(order_id, order_reference, reason, 
                        amount, currency, created_date, processing_date, 
                        card_pan, card_type, issuer_bank_country, 
                        issuer_bank_name, transaction_status, refund_amount,
                        fee, merchant_signature)
        
    def generate_secret_key(self, secret_key_array):	#збір даних для хешування
        """method for generating secret Key and returning his 16-NS value"""

        secret_key_data = str(";".join(secret_key_array))

        hmac_object = hmac.new(self.secret_key.encode(), secret_key_data.encode(), "md5")

        return hmac_object.hexdigest()

    def api_check_status(self, order_reference:str):
        secret_key_array = [self.merchant_account, order_reference]
        merchant_signature = self.generate_secret_key(secret_key_array)
        
        transaction_type = "CHECK_STATUS"

        data = {
   			"transactionType":transaction_type, 
   			"merchantAccount": self.merchant_account,
	  	 	"orderReference": order_reference,  
  	 		"merchantSignature": merchant_signature,
 		  	"apiVersion": self.api_version
        }

        data = json.dumps(data)

        result = requests.post(url=self.API_ENDPOINT, data=data).json()

        return result

    def api_create_invoice(self, price:int, channel_name:str):
        product_name = [f"{self.payment_destination_text} {channel_name}"] #creating sentence with the name of channel
        product_count = [1]
        amount = round(self.PRICE_COEF*price, 2)
        product_price = [amount]		#taking price of product
        order_reference = self.update_order_reference()		#forming orderReference
        transaction_type = "CREATE_INVOICE"
        order_date = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())

        secret_key_array = [self.merchant_account, self.merchant_domain_name, 
                            str(order_reference), str(order_date),
		            	    str(amount), str(self.currency), product_name[0], 
                            str(product_count[0]), str(product_price[0])]
        merchant_signature= self.generate_secret_key(secret_key_array) 	#generating signature

        data={
			'transactionType':transaction_type,
			'merchantAccount':self.merchant_account,
			'merchantDomainName':self.merchant_domain_name,
			'merchantSignature':merchant_signature,
			'apiVersion':self.api_version,
			'orderReference': order_reference,
			'orderDate':order_date,
			'amount':amount,
			'currency':self.currency,
			'productName':product_name,
			'productPrice':product_price,
			'productCount':product_count
        }

        data = json.dumps(data)

        result = requests.post(url=self.API_ENDPOINT, data=data).json()

        return result, order_reference

    def api_refund(self, order_reference, amount):
        secret_key_array = [self.merchant_account, order_reference, str(int(amount)), self.currency]
        merchant_signature = self.generate_secret_key(secret_key_array)
        
        transaction_type = "REFUND"

        data = {
   			"transactionType": transaction_type, 
   			"merchantAccount": self.merchant_account,
	  	 	"orderReference": order_reference,  
            "amount": amount,
            "currency": self.currency,   
            "comment": "None",
  	 		"merchantSignature": merchant_signature,
 		  	"apiVersion": self.api_version
        }

        data = json.dumps(data)

        result = requests.post(url=self.API_ENDPOINT, data=data).json()

        return result

    def api_verify(self):
        #order_reference = self.update_order_reference()
        orderReference = "GC0000121"

        secret_key_array = [self.merchant_account, self.merchant_domain_name, orderReference, '1', self.currency]
        merchant_signature = self.generate_secret_key(secret_key_array)
        
        transaction_type = "P2P_CREDIT"

        data = {
   			"merchantAccount": self.merchant_account,
            "merchantDomainName": self.merchant_domain_name,
  	 		"merchantSignature": merchant_signature,
 		  	"apiVersion": self.api_version,
	  	 	"orderReference": orderReference,  
            "amount": 1,
            "currency": self.currency,   
        }

        data = json.dumps(data)

        result = requests.post(url="https://secure.wayforpay.com/verify", data=data)
        result = result.json()

        return result

    #Not working - need to get rec_token
    def api_top_up(self, card_number, amount):
        order_reference = "top_up_test_2"

        secret_key_array = [self.merchant_account, order_reference, str(amount), self.currency, card_number, ""]
        merchant_signature = self.generate_secret_key(secret_key_array)
        
        transaction_type = "P2P_CREDIT"

        data = {
   			"transactionType": transaction_type, 
   			"merchantAccount": self.merchant_account,
  	 		"merchantSignature": merchant_signature,
 		  	"apiVersion": self.api_version,
	  	 	"orderReference": order_reference,  
            "amount": amount,
            "currency": self.currency,   
            "cardBeneficiary": card_number,
            "rec2Token": ""
        }

        data = json.dumps(data)

        result = requests.post(url=self.API_ENDPOINT, data=data).json()

        return result