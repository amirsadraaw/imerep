import requests

from datetime import datetime

from config.settings import CDC_URL

from services.snapshot_service import (
    SnapshotService
)


def run():

    rows = requests.get(
        CDC_URL,
        timeout=30
    ).json()

    for row in rows:

        contract_id = row.get(
            "ContractID"
        )

        if not contract_id:
            continue

        trade_time = row.get(
            "LastTradedPriceTime"
        )

        snapshot_time = None

        if trade_time:

            today = datetime.now().strftime(
                "%Y-%m-%d"
            )

            snapshot_time = (
                f"{today}T{trade_time}"
            )

        SnapshotService.save_if_changed(

            contract_id,

            row.get(
                "ContractCode"
            ),

            row.get(
                "ContractDescription"
            ),

            "CDC",

            row.get(
                "LastTradedPrice"
            ),

            row.get(
                "TradesVolume"
            ),

            None,

            snapshot_time
        )