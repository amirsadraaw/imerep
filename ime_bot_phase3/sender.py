import requests

from config.settings import B_URL


def send_message(
        chat_id,
        text,
        reply_markup=None
):

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(
        f"{B_URL}/sendMessage",
        json=payload,
        timeout=30
    )