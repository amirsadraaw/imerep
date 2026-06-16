import requests

from datetime import datetime


from services.snapshot_service import (
    SnapshotService
)

URL = "https://dataapi.ime.co.ir/api/Option/LiveMarket"


def run():

    response = requests.get(
        URL,
        timeout=30
    )

    rows = response.json()

    for row in rows:

        call_id = row.get(
            "CallContractID"
        )

        if not call_id:
            continue

        trade_time = row.get(
            "CallLastTradedPriceTime"
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

            call_id,

            row.get(
                "CallContractCode"
            ),

            row.get(
                "CallContractDescription"
            ),

            "OPTION",

            row.get(
                "CallLastTradedPrice"
            ),

            row.get(
                "CallTradesVolume"
            ),

            None,

            row.get(
                "CallOpenInterests"
            ),

            snapshot_time
        )