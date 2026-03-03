import os
from dotenv import load_dotenv

load_dotenv()

BYBIT_WS_URL = "wss://stream-testnet.bybit.com/v5/public/linear"
SYMBOL = "BTCUSDT"

DB_PATH = "sqlite:///./iceberg.db"

MIN_TOUCHES = 2
PRICE_TOLERANCE = 0.005

LARGE_ORDER_THRESHOLD_BTC = 10
DYNAMIC_THRESHOLD_ENABLED = True