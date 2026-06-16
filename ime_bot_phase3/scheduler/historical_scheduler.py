from apscheduler.schedulers.blocking import (
    BlockingScheduler
)

from collectors.historical_cdc_collector import (
    run
)


def start():

    print("historical scheduler started")

    run()

    scheduler = BlockingScheduler()

    scheduler.add_job(
        run,
        "interval",
        minutes=10,
        max_instances=1
    )

    scheduler.start()