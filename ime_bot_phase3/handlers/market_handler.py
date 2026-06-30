"""
هندلرهای مربوط به بخش رصد بازار
"""
from sender import send_message, send_chart
from services.contract_service import ContractService
from keyboard import TIMEFRAME_KEYBOARD
from utils.keyboard_builder import build_dynamic_keyboard


def handle_market_timeframe(chat_id, timeframe, market_type, market_type_fa):
    """
    هندلر انتخاب بازه زمانی و نمایش نمادهای دیتابیسی
    
    Args:
        chat_id: شناسه چت
        timeframe: بازه زمانی انتخاب شده (تایم بازار، روزانه، هفتگی، ماهانه)
        market_type: کد نوع بازار (cdc, option, future)
        market_type_fa: نام فارسی بازار
    """
    # ذخیره timeframe و market_type برای استفاده بعدی
    from polling import user_states
    user_states[chat_id] = "awaiting_commodity"
    user_states[f"{chat_id}_timeframe"] = timeframe
    user_states[f"{chat_id}_market_type"] = market_type
    user_states[f"{chat_id}_market_type_fa"] = market_type_fa
    
    # دریافت نمادهای بازار از دیتابیس
    try:
        contracts = ContractService.get_contracts_by_market_type(market_type)
        
        if not contracts:
            send_message(
                chat_id,
                f"❌ نمادی برای {market_type_fa} {timeframe} یافت نشد"
            )
            return
        
        # ساخت کیبورد دینامیک از نمادهای دیتابیس
        keyboard = build_dynamic_keyboard(contracts)
        
        send_message(
            chat_id,
            f"📊 نمادهای {market_type_fa} ({timeframe})\n\nنماد مورد نظر را انتخاب کنید:",
            keyboard
        )
    
    except Exception as e:
        send_message(
            chat_id,
            f"❌ خطایی در دریافت نمادها رخ داد: {str(e)}"
        )


def handle_commodity_selection(chat_id, contract_code, market_type, timeframe, market_type_fa):
    """
    هندلر انتخاب نماد و نمایش داده‌های آن + چارت شمعی
    
    Args:
        chat_id: شناسه چت
        contract_code: کد نماد انتخاب شده
        market_type: کد نوع بازار (cdc, option, future)
        timeframe: بازه زمانی
        market_type_fa: نام فارسی بازار
    """
    try:
        # دریافت داده‌های نماد
        data = ContractService.get_latest_data_by_contract(contract_code)
        
        if not data:
            send_message(
                chat_id,
                f"❌ داده‌ای برای {contract_code} یافت نشد"
            )
            return
        
        # ساخت پیام نمایش داده‌ها
        message = f"""
📊 **{data['description']} ({data['code']})**

🏷️ **بازار:** {market_type_fa}
⏱️ **بازه زمانی:** {timeframe}

💰 **آخرین قیمت:** {data['last_price']:,} تومان
📈 **حجم:** {int(data['volume']) if data['volume'] else 0:,}
📍 **تغییر حجم:** {int(data['volume_delta']) if data['volume_delta'] else 0:,}
🔓 **تعداد پوزیشن باز:** {int(data['open_interest']) if data['open_interest'] else 0:,}

⏰ **زمان:** {data['snapshot_time']}
📅 **تاریخ معاملات:** {data['trade_date']}
"""
        send_message(chat_id, message)
        
        # تعیین تعداد دقیقه‌های شمع براساس timeframe
        timeframe_minutes = {
            'تایم بازار': 5,
            'روزانه': 1440,
            'هفتگی': 10080,
            'ماهانه': 43200
        }.get(timeframe, 5)
        
        # ارسال چارت شمعی
        send_chart(chat_id, contract_code, timeframe_minutes)
    
    except Exception as e:
        send_message(
            chat_id,
            f"❌ خطایی در دریافت داده‌ها رخ داد: {str(e)}"
        )
