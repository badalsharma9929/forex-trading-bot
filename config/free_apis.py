"""
FREE API Configuration - No API Keys Required
"""

EXCHANGE_RATE_APIS = {
    "frankfurter": "https://api.frankfurter.app/latest",
    "er_api": "https://open.er-api.com/v6/latest",
    "exchangerate": "https://api.exchangerate-api.com/v4/latest",
}

NEWS_APIS = {
    "gnews": "https://gnews.io/api/v4/search",
    "freenewsapi": "https://freenewsapi.com/api/post/list",
}

FOREX_NEWS_FREE = "https://newsdata.io/api/1/news"

SUPPORTED_PAIRS = {
    "USD/INR": {"from": "USD", "to": "INR", "code": "USDINR"},
    "EUR/INR": {"from": "EUR", "to": "INR", "code": "EURINR"},
    "GBP/INR": {"from": "GBP", "to": "INR", "code": "GBPINR"},
    "JPY/INR": {"from": "JPY", "to": "INR", "code": "JPYINR"},
    "EUR/USD": {"from": "EUR", "to": "USD", "code": "EURUSD"},
}

DEFAULT_PAIR = "USD/INR"
