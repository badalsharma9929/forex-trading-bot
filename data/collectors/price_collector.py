"""
Free Price Data Collector
Uses APIs without API keys
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import random
from config.free_apis import EXCHANGE_RATE_APIS, SUPPORTED_PAIRS


class FreePriceCollector:
    def __init__(self):
        self.cache = {}
        self.last_fetch = {}
        
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        """Fetch real-time exchange rate from free API"""
        pair = f"{from_currency}/{to_currency}"
        
        try:
            url = f"{EXCHANGE_RATE_APIS['er_api']}/{from_currency}-{to_currency}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "success":
                    rate = data["rates"][to_currency]
                    self.cache[pair] = {
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                        "source": "er-api"
                    }
                    return {
                        "pair": pair,
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
        except Exception as e:
            print(f"[Price] Primary API failed: {e}")
        
        return self._fallback_rate(from_currency, to_currency)
    
    def _fallback_rate(self, from_currency: str, to_currency: str) -> dict:
        """Fallback to another free API"""
        pair = f"{from_currency}/{to_currency}"
        
        try:
            url = f"{EXCHANGE_RATE_APIS['frankfurter']}?from={from_currency}&to={to_currency}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "rates" in data and to_currency in data["rates"]:
                    rate = data["rates"][to_currency]
                    self.cache[pair] = {
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                        "source": "frankfurter"
                    }
                    return {
                        "pair": pair,
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
        except Exception as e:
            print(f"[Price] Fallback API failed: {e}")
        
        if pair in self.cache:
            return {
                "pair": pair,
                "rate": self.cache[pair]["rate"],
                "timestamp": self.cache[pair]["timestamp"],
                "success": True,
                "cached": True
            }
        
        return {"pair": pair, "success": False, "error": "All APIs failed"}
    
    def get_ohlcv(self, pair: str, periods: int = 100) -> pd.DataFrame:
        """Generate OHLCV data with realistic variations"""
        pair_info = None
        for name, info in SUPPORTED_PAIRS.items():
            if info["code"] == pair or name == pair:
                pair_info = info
                break
        
        if not pair_info:
            pair_info = {"from": "USD", "to": "INR", "code": "USDINR"}
        
        current_rate = self.get_exchange_rate(pair_info["from"], pair_info["to"])
        if not current_rate.get("success"):
            return pd.DataFrame()
        
        base_rate = current_rate["rate"]
        
        data = []
        current_time = datetime.now()
        
        for i in range(periods, 0, -1):
            timestamp = current_time - timedelta(minutes=i * 5)
            
            variation = random.uniform(-0.003, 0.003)
            open_price = base_rate * (1 + variation)
            
            high_extra = random.uniform(0, 0.002)
            low_extra = random.uniform(0, 0.002)
            
            high_price = open_price * (1 + high_extra)
            low_price = open_price * (1 - low_extra)
            
            close_variation = random.uniform(-0.002, 0.002)
            close_price = open_price * (1 + close_variation)
            
            high_price = max(open_price, close_price, high_price)
            low_price = min(open_price, close_price, low_price)
            
            volume = random.randint(1000, 10000)
            
            data.append({
                "timestamp": timestamp,
                "open": round(open_price, 4),
                "high": round(high_price, 4),
                "low": round(low_price, 4),
                "close": round(close_price, 4),
                "volume": volume
            })
            
            base_rate = close_price
        
        return pd.DataFrame(data)
    
    def get_latest_price(self, pair: str) -> dict:
        """Get just the latest price"""
        pair_info = None
        for name, info in SUPPORTED_PAIRS.items():
            if info["code"] == pair or name == pair:
                pair_info = info
                break
        
        if not pair_info:
            pair_info = {"from": "USD", "to": "INR"}
        
        return self.get_exchange_rate(pair_info["from"], pair_info["to"])
    
    def get_all_rates(self) -> dict:
        """Get all supported exchange rates"""
        rates = {}
        for pair_name, info in SUPPORTED_PAIRS.items():
            rate_data = self.get_exchange_rate(info["from"], info["to"])
            if rate_data.get("success"):
                rates[pair_name] = rate_data["rate"]
            time.sleep(0.5)
        return rates


if __name__ == "__main__":
    collector = FreePriceCollector()
    
    print("=== Testing Free Price APIs ===\n")
    
    result = collector.get_latest_price("USDINR")
    print(f"USD/INR: {result}")
    
    rates = collector.get_all_rates()
    print(f"\nAll Rates: {rates}")
    
    ohlcv = collector.get_ohlcv("USDINR", periods=20)
    print(f"\nOHLCV Sample:\n{ohlcv.tail()}")
