from sender import send_message
from keyboard import MAIN_KEYBOARD, MARKET_KEYBOARD


def handle_start(chat_id):

    send_message(
        chat_id,
        "به سامانه تحلیل بازار خوش آمدید",
        MAIN_KEYBOARD
    )