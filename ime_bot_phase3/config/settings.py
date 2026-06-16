from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

BALE_BOT_TOKEN = "1234750349:N69R_YgR_97QuGsQcpVOuxP_lTUqnz3xI7A"

B_URL = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}"

CDC_URL = "https://dataapi.ime.co.ir/api/CDC/CDCLiveMarket"
OPTION_URL = "https://dataapi.ime.co.ir/api/Option/LiveMarket"
FUTURE_URL = "https://dataapi.ime.co.ir/api/Future/LiveMarket"

DB_PATH = "data/market.db"

POLLING_INTERVAL = 2
SNAPSHOT_INTERVAL = 5
POLLING_TIMEOUT = 30