from database.db import (
    get_historical_conn
)


class HistoricalRepository:

    @staticmethod
    def save_daily_candle(
        contract_id,
        filter_id,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        open_interest
    ):

        conn = get_historical_conn()

        conn.execute("""
        INSERT INTO cdc_daily (

            contract_id,
            filter_id,
            trade_date,

            open_price,
            high_price,
            low_price,
            close_price,

            volume,
            open_interest

        )
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            contract_id,
            filter_id,
            trade_date,

            open_price,
            high_price,
            low_price,
            close_price,

            volume,
            open_interest
        ))

        conn.commit()

        conn.close()