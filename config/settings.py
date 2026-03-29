import os

from .api_keys import (
    ALPHA_VANTAGE_API_KEY,
    OANDA_API_KEY,
    OANDA_ACCOUNT_ID,
    FOREX_NEWS_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    MARKETAUX_API_KEY,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.path.join(BASE_DIR, "data", "database", "forex_bot.db")
CACHE_PATH = os.path.join(BASE_DIR, "data", "cache")

CURRENCY_PAIRS = {
    "USDINR": {"from_currency": "USD", "to_currency": "INR"},
    "EURINR": {"from_currency": "EUR", "to_currency": "INR"},
    "GBPINR": {"from_currency": "GBP", "to_currency": "INR"},
    "JPYINR": {"from_currency": "JPY", "to_currency": "INR"},
}
DEFAULT_PAIR = "USDINR"

UPDATE_INTERVAL_SECONDS = 300  # 5 minutes

PAPER_TRADING_INITIAL_BALANCE = 100000.0  # ₹1 Lakh

RISK_MANAGEMENT = {
    "max_risk_per_trade": 0.02,  # 2%
    "max_position_size": 0.10,  # 10%
    "max_drawdown": 0.20,  # 20%
    "daily_loss_limit": 0.05,  # 5%
    "max_consecutive_losses": 5,
}

ML_CONFIG = {
    "confidence_threshold": 0.70,
    "lookback_periods": [1, 2, 3, 5, 10],
}

SENTIMENT_CONFIG = {
    "bullish_threshold": 0.2,
    "bearish_threshold": -0.2,
    "news_limit": 10,
}

INDICATOR_PERIODS = {
    "rsi": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb": 20,
    "bb_std": 2,
    "ema_fast": 12,
    "ema_slow": 26,
    "sma_long": 200,
    "adx": 14,
    "stochastic": 14,
    "cci": 20,
    "atr": 14,
}
