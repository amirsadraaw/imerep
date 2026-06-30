import asyncio

# ایمپورت کالکتورهای لایو شما
from collectors.cdc_collector import run as fetch_cdc
from collectors.option_collector import run as fetch_option
from collectors.etf_collector import run as fetch_etf

async def cdc_loop():
    print("Live CDC Loop Started...")
    while True:
        try:
            # ارسال تابع مسدودکننده به ترد مجزا جهت جلوگیری از فریز شدن لوپ
            await asyncio.to_thread(fetch_cdc)
        except Exception as ex:
            print(f"Error in Live CDC: {ex}")
        await asyncio.sleep(1)

async def option_loop():
    print("Live Option Loop Started...")
    while True:
        try:
            # ارسال تابع مسدودکننده به ترد مجزا جهت جلوگیری از فریز شدن لوپ
            await asyncio.to_thread(fetch_option)
        except Exception as ex:
            print(f"Error in Live Option: {ex}")
        await asyncio.sleep(1)

async def etf_loop():
    print("Live ETF Loop Started...")
    while True:
        try:
            # ارسال تابع مسدودکننده به ترد مجزا جهت جلوگیری از فریز شدن لوپ
            await asyncio.to_thread(fetch_etf)
        except Exception as ex:
            print(f"Error in Live ETF: {ex}")
        await asyncio.sleep(1)

# این همان تابعی است که در main.py صدا زده می‌شود
async def start_engine():
    print("Live Engine Started (All Real-time Streams Activating)...")
    # اجرای موازی تمام چرخه‌های دریافت لحظه‌ای تیک بورس کالا
    await asyncio.gather(
        cdc_loop(),
        option_loop(),
        etf_loop()
    )

if __name__ == "__main__":
    # اجرای مستقل برای تست شخصی
    asyncio.run(start_engine())