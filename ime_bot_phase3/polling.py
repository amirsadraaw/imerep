import requests
import time
from handlers.cover_call_handler import (
    handle_cover_call
)

user_states = {}
FILTER_MAP = {
    "شمش طلا": 2,
    "شمش نقره": 4,
    "سکه طلا": 14,
    "کاتد مس": 21,
    "شمش روی": 26,
    "میلگرد": 27,
    "خودرو": 28,
    "گندله": 29,
    "قیر": 30
}

from keyboard import (
    MAIN_KEYBOARD,
    MARKET_KEYBOARD,
    TIMEFRAME_KEYBOARD,
    COMMODITY_KEYBOARD
)

from sender import (
    send_message
)

from config.settings import (
    B_URL,
    POLLING_TIMEOUT
)

from handlers.start_handler import (
    handle_start
)

offset = 0
def get_updates():

    global offset

    response = requests.get(
        f"{B_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": POLLING_TIMEOUT
        }
    )

    data = response.json()

    if not data["ok"]:
        return []

    updates = data["result"]

    if updates:

        offset = (
            updates[-1]["update_id"] + 1
        )

    return updates
def process_update(update):

    message = update.get("message")

    if not message:
        return

    chat_id = (
        message["chat"]["id"]
    )

    text = (
        message.get("text", "")
    )

    if text == "/start":
        user_states[chat_id] = "main"

        handle_start(chat_id)

    if text == "موقعیت کاوردکال":
        handle_cover_call(chat_id)

    if text == "بازگشت":

        current_state = user_states.get(chat_id)

        if current_state == "commodity":

            user_states[chat_id] = "timeframe"

            send_message(
                chat_id,
                "بازه زمانی را انتخاب کنید",
                TIMEFRAME_KEYBOARD
            )

        elif current_state == "timeframe":

            user_states[chat_id] = "market"

            send_message(
                chat_id,
                "بازار مورد نظر را انتخاب کنید",
                MARKET_KEYBOARD
            )

        elif current_state == "market":

            user_states[chat_id] = "main"

            send_message(
                chat_id,
                "منوی اصلی",
                MAIN_KEYBOARD
            )

        return

    elif text == "رصد بازار":

        user_states[chat_id] = "market"

        send_message(

            chat_id,

            "بازار مورد نظر را انتخاب کنید",

            MARKET_KEYBOARD

        )

    elif text == "گواهی سپرده":

        user_states[chat_id] = "timeframe"

        send_message(
            chat_id,
            "بازه زمانی را انتخاب کنید",
            TIMEFRAME_KEYBOARD
        )

    elif text in [
        "تایم بازار",
        "روزانه",
        "هفتگی",
        "ماهانه"
    ]:

        user_states[chat_id] = "commodity"

        send_message(
            chat_id,
            "کالای مورد نظر را انتخاب کنید",
            COMMODITY_KEYBOARD
        )

    elif text in FILTER_MAP:

        filter_id = FILTER_MAP[text]

        send_message(
            chat_id,
            f"فیلتر انتخاب شده: {filter_id}"
        )
def start_polling():

    while True:

        try:

            updates = get_updates()

            for update in updates:

                process_update(update)

        except Exception as ex:

            print(ex)

        time.sleep(1)