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


def send_photo(
        chat_id,
        photo_bytes,
        caption=None,
        reply_markup=None
):
    """
    ارسال تصویر به کاربر
    
    Args:
        chat_id: شناسه چت
        photo_bytes: bytes تصویر (از io.BytesIO)
        caption: متن توضیح تصویر
        reply_markup: کیبورد (اختیاری)
    """
    
    files = {
        'photo': ('chart.png', photo_bytes, 'image/png')
    }
    
    data = {
        "chat_id": chat_id
    }
    
    if caption:
        data["caption"] = caption
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    try:
        response = requests.post(
            f"{B_URL}/sendPhoto",
            files=files,
            data=data,
            timeout=30
        )
        return response.json()
    except Exception as e:
        print(f"خطا در ارسال تصویر: {e}")
        return None


def send_chart(
        chat_id,
        contract_code,
        timeframe_minutes=5
):
    """
    ساخت و ارسال چارت برای کاربر
    
    Args:
        chat_id: شناسه چت
        contract_code: کد نماد
        timeframe_minutes: طول هر شمع
    """
    from services.candle_service import CandleService
    
    try:
        # ساخت چارت
        image, caption = CandleService.create_chart_image(
            contract_code,
            timeframe_minutes
        )
        
        if not image:
            send_message(chat_id, caption)
            return
        
        # ارسال تصویر
        send_photo(chat_id, image, caption)
    
    except Exception as e:
        send_message(
            chat_id,
            f"❌ خطایی در ساخت چارت رخ داد: {str(e)}"
        )
