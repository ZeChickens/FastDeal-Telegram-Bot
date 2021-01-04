import configparser

from telebot import logging, TeleBot, logger

from data import Data
from system import System

from sections.main import Main
from sections.tag import Tag
from sections.channel import Channel
from sections.order import Order
from sections.redaction import Redaction

import error_logging

from time import sleep

logger.setLevel(logging.INFO)

config = configparser.ConfigParser()
config.read('Settings.ini')
API_TOKEN = config['TG']['token']

bot = TeleBot(API_TOKEN)
bot.remove_webhook()

data = Data(bot=bot)
system = System(data=data)

main_menu = Main(data=data)
tag = Tag(data=data)
channel = Channel(data=data)
order = Order(data=data)
redaction = Redaction(data=data, order=order)


@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.chat.id == data.REDACTION_CHAT_ID:
        redaction.command_in_group_error()
        return
    system.add_client(message)
    main_menu.send_start_message(chat_id=message.chat.id)
    
    system.clear(message=message)
    system.update_client_interaction_time(message)
    
@bot.message_handler(commands=['orders'])
def orders_list(message):
    chat_id=message.chat.id

    system.clear(message=message)
    system.update_client_interaction_time(message)

    order.send_order_list(chat_id=chat_id)

@bot.callback_query_handler(func=lambda call: "Main" in call.data.split(";")[0])
def handle_main_menu_query(call):
    system.update_client_interaction_time(call.message)

    try:
        main_menu.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())
    
@bot.callback_query_handler(func=lambda call: "Tag" in call.data)
def handle_tag_query(call):
    system.update_client_interaction_time(call.message)
    
    try:
        tag.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Channel" in call.data)
def handle_channel_query(call):
    system.update_client_interaction_time(call.message)
    
    try:
        channel.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Order" in call.data)
def handle_order_query(call):
    system.clear(message=call.message)
    system.update_client_interaction_time(call.message)

    try:
        order.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Redaction" in call.data)
def handle_redaction_query(call):
    system.clear(message=call.message)
    
    try:
        redaction.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Payment" in call.data)
def handle_payment_query(call):
    system.clear(message=call.message)
    
    try:
        order.payment.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.message_handler(func=lambda message: message.chat.id == data.REDACTION_CHAT_ID, content_types=['text'])
def redaction_message_handler(message):
    redaction.process_text(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_etc_query(call):
    
    if call.data == "DELETE":
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, text=data.message.delete_error)
    elif call.data == "IGNORE":
        bot.answer_callback_query(call.id)
    else:
        oops(call, current_frame=error_logging.currentframe())

def oops(call, current_frame, additional_info=None):
    oops_text = data.message.oops
    bot.answer_callback_query(call.id, text=oops_text)

    if additional_info is None:
        additional_info = call.data

    error_logging.send_error_info_message(bot, current_frame, additional_info=additional_info)

if __name__ == "__main__":
    # logger = logging.Logger("Polling")
    bot.polling(none_stop=True)



#start = time.time()
#
#end = time.time()
#print(end - start)