from sender import send_message

from services.cover_call_service import (
    calculate_covered_call
)


def handle_cover_call(chat_id):

    positions = calculate_covered_call()

    if not positions:

        send_message(
            chat_id,
            "موقعیتی پیدا نشد"
        )

        return

    for item in positions[:10]:

        message = f"""

🔄 {item['description']}

📅 آخرین روز معاملاتی:
{item['expiry']}

⏳ روز مانده تا سررسید:
{item['days']}

💰 قیمت اختیار:
{item['option_price']:,}

🏷️ قیمت دارایی پایه:
{item['base_price']:,}

💼 سرمایه اولیه:
{int(item['initial_capital']):,}

💳 دریافتی پایان دوره:
{int(item['final_value']):,}

📈 سود ناخالص:
{int(item['gross_profit']):,}

📊 بازده:
{item['return']:.2f}%

📆 نرخ YTM:
{item['ytm']:.2f}%

🏦 هزینه فرصت:
{int(item['opportunity_cost']):,}

✅ سود خالص:
{int(item['net_profit']):,}

📊 بازده تعدیل شده:
{item['adjusted_return']:.2f}%

📆 YTM تعدیل شده:
{item['adjusted_ytm']:.2f}%

📦 OI:
{item['oi']}
"""

        send_message(
            chat_id,
            message
        )