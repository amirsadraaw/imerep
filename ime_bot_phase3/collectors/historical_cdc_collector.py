import asyncio
import httpx
from datetime import date, timedelta, datetime

from database.db import get_historical_conn

API_URL = "https://dataapi.ime.co.ir/api/CDC/CDCTrades"
PAGE_SIZE = 25
CHUNK_DAYS = 90

CUSTOM_FILTERS = [
    2, 4, 14, 21, 26, 27, 28, 29, 30
]

# تاریخ پیش‌فرض در صورتی که دیتابیس کاملاً خالی باشد
DEFAULT_START_DATE = date(2023, 3, 9)


def init_table():
    conn = get_historical_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cdc_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        commodity_id INTEGER,
        contract_code TEXT,
        contract_description TEXT,
        dt TEXT,
        persian_date TEXT,
        first_price REAL,
        last_price REAL,
        max_price REAL,
        min_price REAL,
        trades_volume REAL,
        trades_value REAL,
        open_interest REAL,
        custom_filter INTEGER,
        UNIQUE(contract_code, dt)
    )
    """)
    conn.commit()
    conn.close()


def get_last_available_date():
    """یافتن آخرین تاریخ ثبت شده در دیتابیس برای بهینه‌سازی فرآیند"""
    conn = get_historical_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(dt) FROM cdc_trades")
        row = cursor.fetchone()
        if row and row[0]:
            date_str = row[0][:10]
            last_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return max(DEFAULT_START_DATE, last_date - timedelta(days=3))
    except Exception as e:
        print(f"Error fetching last date: {e}")
    finally:
        conn.close()
    return DEFAULT_START_DATE


def date_chunks(start, end, days):
    cur = start
    while cur <= end:
        yield cur, min(
            cur + timedelta(days=days - 1),
            end
        )
        cur += timedelta(days=days)


def build_payload(from_date, to_date, page, custom_filter):
    return {
        "fromDate": from_date.strftime("%Y-%m-%d"),
        "toDate": to_date.strftime("%Y-%m-%d"),
        "pageNumber": page,
        "pageSize": PAGE_SIZE,
        "marketId": None,
        "mainGroupId": None,
        "groupId": None,
        "subGroupId": None,
        "commodityId": None,
        "customFilter": str(custom_filter),
        "sortField": None,
        "sortOrder": "asc"
    }


def save_rows(rows, custom_filter):
    conn = get_historical_conn()
    for item in rows:
        conn.execute("""
        INSERT OR IGNORE INTO cdc_trades (
            commodity_id, contract_code, contract_description, dt, persian_date,
            first_price, last_price, max_price, min_price, trades_volume,
            trades_value, open_interest, custom_filter
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            item.get("CommodityID"),
            item.get("ContractCode"),
            item.get("ContractDescription"),
            item.get("DT"),
            item.get("PersianDate"),
            item.get("FirstPrice"),
            item.get("LastPrice"),
            item.get("MaxPrice"),
            item.get("MinPrice"),
            item.get("TradesVolume"),
            item.get("TradesValue"),
            item.get("OpenInterest"),
            custom_filter
        ))
    conn.commit()
    conn.close()


async def run():
    print("historical sync started (Async Mode)")
    
    # اجرای عملیاتهای دیتابیسی سنگین یا مسدودکننده در ترد مجزا برای روان ماندن اِونت‌لوپ
    await asyncio.to_thread(init_table)
    start_date = await asyncio.to_thread(get_last_available_date)
    end_date = date.today()

    print(f"Syncing data from {start_date} to {end_date}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # استفاده از AsyncClient برای درخواست‌های کاملاً غیرمسدودکننده شبکه
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        for from_d, to_d in date_chunks(start_date, end_date, CHUNK_DAYS):
            for custom_filter in CUSTOM_FILTERS:
                page = 1
                while True:
                    payload = build_payload(from_d, to_d, page, custom_filter)
                    try:
                        response = await client.post(API_URL, json=payload)

                        if response.status_code != 200:
                            print(f"API Error {response.status_code} for filter {custom_filter} page {page}")
                            break

                        data = response.json()
                    except Exception as e:
                        print(f"Connection or JSON parse error: {e}")
                        await asyncio.sleep(5)
                        break

                    rows = data.get("Data", [])
                    if not rows:
                        break

                    # ذخیره‌سازی داده‌ها بدون قفل کردن لوپ اصلی
                    await asyncio.to_thread(save_rows, rows, custom_filter)
                    print(f"saved => {from_d} to {to_d} | filter={custom_filter} | page={page}")

                    if not data.get("HasNextPage", False):
                        break

                    page += 1
                    await asyncio.sleep(0.5)  # استفاده از sleep غیرمسدودکننده ناهمگام

    print("historical sync finished")


async def historical_loop():
    """حلقه بی‌نهایت جهت اجرا و به‌روزرسانی مداوم هر ۱۰ دقیقه یک‌بار"""
    while True:
        try:
            await run()
        except Exception as e:
            print(f"Error in historical loop execution: {e}")
        
        print("Historical loop waiting for 10 minutes...")
        await asyncio.sleep(10 * 60)