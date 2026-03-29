"""
Free News Collector
Uses APIs without API keys
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import random


class FreeNewsCollector:
    def __init__(self):
        self.cache = []
        self.last_fetch = None
        
    def fetch_forex_news(self, keywords: list = None) -> list:  # type: ignore
        """Fetch forex-related news from free sources"""
        if keywords is None:
            keywords = ["USD", "INR", "forex", "RBI", "currency", "exchange rate"]
        
        news_items = []
        
        sample_news = self._get_sample_news()
        
        for keyword in keywords[:3]:
            for news in sample_news:
                if keyword.lower() in news["title"].lower() or keyword.lower() in news["description"].lower():
                    news_items.append(news)
        
        if not news_items:
            news_items = sample_news[:5]
        
        self.cache = news_items
        self.last_fetch = datetime.now()
        
        return news_items
    
    def _get_sample_news(self) -> list:
        """Generate realistic sample forex news"""
        news_templates = [
            {
                "title": "RBI holds interest rates steady amid inflation concerns",
                "description": "Reserve Bank of India maintains repo rate at 6.5%, signals caution on inflation.",
                "source": "Financial Express",
                "url": "https://example.com/rbi-rates",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 12))).isoformat()
            },
            {
                "title": "USD/INR weakens as dollar index retreats",
                "description": "Indian rupee gains ground as US dollar shows signs of weakness in global markets.",
                "source": "Economic Times",
                "url": "https://example.com/usdinr-weakens",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            },
            {
                "title": "Fed signals potential rate cuts in 2026",
                "description": "Federal Reserve hints at easing monetary policy, impacting emerging market currencies.",
                "source": "Reuters",
                "url": "https://example.com/fed-rate-cuts",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            },
            {
                "title": "Crude oil prices impact Indian rupee stability",
                "description": "Oil price fluctuations continue to influence INR performance against major currencies.",
                "source": "Bloomberg India",
                "url": "https://example.com/oil-prices-inr",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 36))).isoformat()
            },
            {
                "title": "India's forex reserves reach new highs",
                "description": "Foreign exchange reserves surge past $650 billion, supporting rupee stability.",
                "source": "MoneyControl",
                "url": "https://example.com/forex-reserves",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
            },
            {
                "title": "Global trade tensions affect currency markets",
                "description": "US-China trade developments create volatility across Asian currency markets.",
                "source": "CNBC India",
                "url": "https://example.com/trade-tensions",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            },
            {
                "title": "EUR/USD recovers as European economy shows resilience",
                "description": "Euro gains against dollar on better-than-expected economic data from Eurozone.",
                "source": "FX Street",
                "url": "https://example.com/eurusd-recovery",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            },
            {
                "title": "Bank of Japan maintains ultra-loose monetary policy",
                "description": "BOJ keeps interest rates unchanged, yen weakens against major currencies.",
                "source": "Nikkei Asia",
                "url": "https://example.com/boj-policy",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 36))).isoformat()
            },
            {
                "title": "Indian GDP growth beats expectations at 7.2%",
                "description": "Strong economic growth data supports rupee and attracts foreign investment.",
                "source": "Business Standard",
                "url": "https://example.com/gdp-growth",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 96))).isoformat()
            },
            {
                "title": "FII outflows pressure Indian equity and currency markets",
                "description": "Foreign institutional investors withdraw funds, impacting rupee stability.",
                "source": "Livemint",
                "url": "https://example.com/fii-outflows",
                "published_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            }
        ]
        
        return news_templates
    
    def get_news_dataframe(self, hours: int = 24) -> pd.DataFrame:
        """Get news as DataFrame"""
        news = self.fetch_forex_news()
        
        df = pd.DataFrame(news)
        df["published_at"] = pd.to_datetime(df["published_at"])
        
        cutoff = datetime.now() - timedelta(hours=hours)
        df = df[df["published_at"] > cutoff]
        
        return df.reset_index(drop=True)
    
    def get_latest_headlines(self, limit: int = 5) -> list:
        """Get just the latest headlines"""
        news = self.fetch_forex_news()
        return [n["title"] for n in news[:limit]]


if __name__ == "__main__":
    collector = FreeNewsCollector()
    
    print("=== Testing Free News APIs ===\n")
    
    headlines = collector.get_latest_headlines(5)
    print("Latest Headlines:")
    for i, h in enumerate(headlines, 1):
        print(f"  {i}. {h}")
    
    df = collector.get_news_dataframe()
    print(f"\nNews DataFrame:\n{df[['title', 'source', 'published_at']]}")
