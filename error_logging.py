from inspect import getframeinfo, currentframe 

ERRORS_CHAT_ID = -459712183

def send_error_info_message(bot, current_frame, additional_info=None):
    frame_info = getframeinfo(current_frame)
    
    error_info_message = (f"<b>File Name</b>\n{frame_info.filename}\n\n"
                          f"<b>Function Name</b>\n{frame_info.function}\n\n"
                          f"<b>Line</b>\n{frame_info.lineno}\n\n"
                          f"<b>Additional Info</b>\n{additional_info}\n\n"
    )

    bot.send_message(chat_id=ERRORS_CHAT_ID, text=error_info_message, parse_mode="HTML")