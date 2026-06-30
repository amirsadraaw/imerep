import requests
import time
from handlers.cover_call_handler import (
    handle_cover_call
)
from handlers.market_handler import (
    handle_market_timeframe,
    handle_commodity_selection
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

        user_states[chat_id] = "awaiting_timeframe"
        # ذخیره نوع بازار برای استفاده بعدی
        user_states[f"{chat_id}_market_type"] = "گواهی سپرده"

        send_message(
            chat_id,
            "بازه زمانی را انتخاب کنید",
            TIMEFRAME_KEYBOARD
        )

    elif text == "اختیار معامله":

        user_states[chat_id] = "awaiting_timeframe"
        user_states[f"{chat_id}_market_type"] = "اختیار معامله"

        send_message(
            chat_id,
            "بازه زمانی را انتخاب کنید",
            TIMEFRAME_KEYBOARD
        )

    elif text == "آتی":

        user_states[chat_id] = "awaiting_timeframe"
        user_states[f"{chat_id}_market_type"] = "آتی"

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
        current_state = user_states.get(chat_id)
        
        # اگر از بخش بازار آمده‌ایم
        if current_state == "awaiting_timeframe":
            market_type = user_states.get(f"{chat_id}_market_type")
            handle_market_timeframe(chat_id, text, market_type)
        else:
            user_states[chat_id] = "commodity"
            send_message(
                chat_id,
                "کالای مورد نظر را انتخاب کنید",
                COMMODITY_KEYBOARD
            )

    elif text in FILTER_MAP:
        current_state = user_states.get(chat_id)
        
        # اگر از تایم فریم آمده‌ایم (بخش بازار)
        if current_state == "awaiting_commodity":
            market_type = user_states.get(f"{chat_id}_market_type")
            timeframe = user_states.get(f"{chat_id}_timeframe")
            handle_commodity_selection(chat_id, text, market_type, timeframe)
        else:
            # رفتار قدیمی برای سازگاری
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
