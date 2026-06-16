import requests
import time
from datetime import date, timedelta
import time

from database.db import get_historical_conn


API_URL = "https://dataapi.ime.co.ir/api/CDC/CDCTrades"

PAGE_SIZE = 25

CHUNK_DAYS = 90


CUSTOM_FILTERS = [
    2,
    4,
    14,
    21,
    26,
    27,
    28,
    29,
    30
]


START_DATE = date(2023, 3, 9)

END_DATE = date.today()


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


def date_chunks(start, end, days):

    cur = start

    while cur <= end:

        yield cur, min(
            cur + timedelta(days=days - 1),
            end
        )

        cur += timedelta(days=days)


def build_payload(
    from_date,
    to_date,
    page,
    custom_filter
):

    return {

        "fromDate":
        from_date.strftime("%Y-%m-%d"),

        "toDate":
        to_date.strftime("%Y-%m-%d"),

        "pageNumber":
        page,

        "pageSize":
        PAGE_SIZE,

        "marketId": None,
        "mainGroupId": None,
        "groupId": None,
        "subGroupId": None,

        "commodityId": None,

        "customFilter":
        str(custom_filter),

        "sortField": None,

        "sortOrder": "asc"
    }


def save_rows(rows, custom_filter):

    conn = get_historical_conn()

    for item in rows:

        conn.execute("""
        INSERT OR IGNORE INTO cdc_trades (

            commodity_id,

            contract_code,

            contract_description,

            dt,

            persian_date,

            first_price,

            last_price,

            max_price,

            min_price,

            trades_volume,

            trades_value,

            open_interest,

            custom_filter

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


def run():
    print("historical sync started")
    init_table()

    session = requests.Session()

    for from_d, to_d in date_chunks(
        START_DATE,
        END_DATE,
        CHUNK_DAYS
    ):

        for custom_filter in CUSTOM_FILTERS:

            page = 1

            while True:

                payload = build_payload(
                    from_d,
                    to_d,
                    page,
                    custom_filter
                )

                response = session.post(
                    API_URL,
                    json=payload,
                    timeout=30
                )

                data = response.json()

                rows = data.get("Data", [])

                if not rows:
                    break

                save_rows(
                    rows,
                    custom_filter
                )

                print(
                    f"saved => "
                    f"{from_d} "
                    f"filter={custom_filter} "
                    f"page={page}"
                )

                if not data.get(
                    "HasNextPage",
                    False
                ):
                    break

                page += 1

                time.sleep(0.5)
    print("historical sync finished")