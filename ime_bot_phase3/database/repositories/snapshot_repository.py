from datetime import datetime

from database.db import get_market_conn


class SnapshotRepository:

    @staticmethod
    def save(
            contract_id,
            contract_code,
            contract_description,
            market_type,
            last_price,
            volume,
            volume_delta,
            oi,
            created_at
    ):

        conn = get_market_conn()

        trade_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        conn.execute("""
        INSERT INTO snapshots (

            contract_id,

            contract_code,

            contract_description,

            market_type,

            last_price,

            volume,

            volume_delta,

            open_interest,

            snapshot_time,

            trade_date

        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            contract_id,
            contract_code,
            contract_description,
            market_type,
            last_price,
            volume,
            volume_delta,
            oi,
            created_at,
            trade_date
        ))

        conn.commit()

        conn.close()
