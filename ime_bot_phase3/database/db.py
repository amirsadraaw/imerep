import sqlite3
import os
from pathlib import Path

Path("data").mkdir(exist_ok=True)

MARKET_DB_PATH = "data/market.db"

HISTORICAL_DB_PATH = "data/historical.db"


def get_market_conn():

    return sqlite3.connect(
        MARKET_DB_PATH
    )


def get_historical_conn():

    return sqlite3.connect(
        HISTORICAL_DB_PATH
    )


def init_market_db():

    conn = get_market_conn()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    contract_id TEXT,

    contract_code TEXT,

    contract_description TEXT,

    market_type TEXT,

    last_price REAL,

    volume REAL,

    volume_delta REAL,

    open_interest REAL,

    snapshot_time TEXT,

    trade_date TEXT
    )
    """)

    conn.commit()

    conn.close()


def init_historical_db():

    conn = get_historical_conn()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS cdc_daily (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        contract_id TEXT,

        filter_id INTEGER,

        trade_date TEXT,

        open_price REAL,

        high_price REAL,

        low_price REAL,

        close_price REAL,

        volume REAL,

        open_interest REAL
    )
    """)

    conn.commit()

    conn.close()