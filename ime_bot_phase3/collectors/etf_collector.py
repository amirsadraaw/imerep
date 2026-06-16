import requests

from services.snapshot_service import (
    SnapshotService
)

ETF_LIST = [

    {
        "symbol": "کهربا",
        "description": "صندوق س. کالای کهربا",
        "ins_code": "25559236668122210"
    },

    {
        "symbol": "طلا",
        "description": "صندوق س. کالای پارسیان",
        "ins_code": "46700660505281786"
    },

    {
        "symbol": "درخشان",
        "description": "صندوق س.کالای آبان",
        "ins_code": "61805666737517582"
    },

    {
        "symbol": "جواهر",
        "description": "صندوق س.کالای دنای زاگرس",
        "ins_code": "38544104313215500"
    }
]


def run():

    for item in ETF_LIST:

        try:

            url = (
                "https://cdn.tsetmc.com/api/"
                "ClosingPrice/GetClosingPriceInfo/"
                f"{item['ins_code']}"
            )

            response = requests.get(
                url,
                timeout=30
            )

            data = response.json()

            info = data.get(
                "closingPriceInfo",
                {}
            )

            last_price = info.get(
                "pDrCotVal"
            )

            volume = info.get(
                "qTotTran5J"
            )

            trade_date = str(
                info.get("dEven")
            )

            trade_time = str(
                info.get("hEven")
            ).zfill(6)

            snapshot_time = None

            if trade_date and trade_time:

                snapshot_time = (

                    f"{trade_date[0:4]}-"
                    f"{trade_date[4:6]}-"
                    f"{trade_date[6:8]}T"
                    f"{trade_time[0:2]}:"
                    f"{trade_time[2:4]}:"
                    f"{trade_time[4:6]}"
                )

            SnapshotService.save_if_changed(

                item["ins_code"],

                item["symbol"],

                item["description"],

                "ETF",

                last_price,

                volume,

                None,

                snapshot_time
            )

        except Exception as ex:

            print(ex)