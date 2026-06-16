
from threading import Thread

from scheduler.live_engine import start_engine

from polling import start_polling

from database.db import (
    init_market_db,
    init_historical_db
)


if __name__ == "__main__":

    init_market_db()

    init_historical_db()

    Thread(
        target=start_engine,
        daemon=True
    ).start()

    start_polling()
