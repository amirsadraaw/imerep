import asyncio
import logging
from threading import Thread

from database.db import init_market_db, init_historical_db
from scheduler.live_engine import start_engine
from polling import start_polling
from collectors.historical_cdc_collector import run as run_historical

# تنظیمات لاگینج
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def historical_thread_worker():
    """کارگر ترد اختصاصی برای بخش تاریخی"""
    logger.info("Historical Thread Worker Started.")
    while True:
        try:
            asyncio.run(run_historical())
        except Exception as e:
            logger.error(f"Error in historical sync execution: {e}")
        
        logger.info("Historical sync finished. Thread sleeping for 10 minutes...")
        import time
        time.sleep(10 * 60)


def bot_polling_thread_worker():
    """کارگر ترد اختصاصی برای ربات بله"""
    logger.info("Bot Polling Thread Worker Started.")
    while True:
        try:
            # اجرای تابع پولینگ همگام شما در یک ترد کاملاً ایزوله
            start_polling()
        except Exception as e:
            logger.error(f"Error in bot polling: {e}")
            import time
            time.sleep(5)


async def main():
    logger.info("Starting IME Bot Application...")

    # ۱. مقداردهی اولیه دیتابیس‌ها
    init_market_db()
    init_historical_db()

    # ۲. راه‌اندازی بخش تاریخی در ترد مجزا
    historical_thread = Thread(target=historical_thread_worker, daemon=True)
    historical_thread.start()

    # ۳. راه‌اندازی ربات بله در ترد مجزا (این تغییر مشکل قفل شدن لایو را حل میکند)
    bot_thread = Thread(target=bot_polling_thread_worker, daemon=True)
    bot_thread.start()

    # ۴. حالا اِونت‌لوپ اصلی کاملاً آزاد است و ۱۰۰٪ توان خود را به موتور استریم لحظه‌ای می‌دهد
    logger.info("Main Event Loop is now dedicated to Live Engine Streaming.")
    await start_engine()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.error(f"Critical error in application: {e}", exc_info=True)