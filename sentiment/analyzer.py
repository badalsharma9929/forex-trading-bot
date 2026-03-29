"""
Sentiment Analysis Engine
Uses VADER for lightweight sentiment analysis (Streamlit Cloud compatible)
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')


class SentimentAnalyzer:
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        self.vader_analyzer = None
        
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            import nltk
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            self.vader_analyzer = SentimentIntensityAnalyzer()
            print("[Sentiment] VADER loaded successfully")
        except Exception as e:
            print(f"[Sentiment] VADER failed: {e}")
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of a single text using VADER"""
        if self.vader_analyzer:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                "label": "positive" if scores["compound"] > 0.05 else "negative" if scores["compound"] < -0.05 else "neutral",
                "score": scores["compound"],
                "confidence": abs(scores["compound"]),
                "source": "vader"
            }
        
        return {
            "label": "neutral",
            "score": 0.0,
            "confidence": 0.0,
            "source": "none"
        }
    
    def analyze_news(self, news_list: List[Dict]) -> Dict:
        """Analyze sentiment for a list of news articles"""
        if not news_list:
            return self._empty_sentiment()
        
        sentiments = []
        articles_analyzed = 0
        
        for news in news_list:
            text = f"{news.get('title', '')} {news.get('description', '')}"
            if text.strip():
                sentiment = self.analyze_text(text)
                sentiment["title"] = news.get("title", "")
                sentiment["source"] = news.get("source", "")
                sentiment["published_at"] = news.get("published_at", "")
                sentiments.append(sentiment)
                articles_analyzed += 1
        
        if not sentiments:
            return self._empty_sentiment()
        
        avg_score = np.mean([s["score"] for s in sentiments])
        avg_confidence = np.mean([s["confidence"] for s in sentiments])
        
        bullish_count = sum(1 for s in sentiments if s["label"] in ["positive", "bullish"])
        bearish_count = sum(1 for s in sentiments if s["label"] in ["negative", "bearish"])
        neutral_count = sum(1 for s in sentiments if s["label"] == "neutral")
        
        if avg_score > 0.1:
            overall_label = "bullish"
        elif avg_score < -0.1:
            overall_label = "bearish"
        else:
            overall_label = "neutral"
        
        return {
            "avg_sentiment_score": round(avg_score, 4),
            "avg_confidence": round(avg_confidence, 4),
            "overall_label": overall_label,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "total_articles": articles_analyzed,
            "articles": sentiments,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_trading_signal(self, sentiment_data: Dict) -> Dict:
        """Convert sentiment data to trading signal"""
        score = sentiment_data.get("avg_sentiment_score", 0)
        confidence = sentiment_data.get("avg_confidence", 0)
        
        bullish_threshold = 0.2
        bearish_threshold = -0.2
        strong_threshold = 0.4
        
        if score > strong_threshold and confidence > 0.6:
            signal = "strong_buy"
            strength = min(score * 2, 1.0)
        elif score > bullish_threshold:
            signal = "buy"
            strength = min(score * 1.5, 0.8)
        elif score < -strong_threshold and confidence > 0.6:
            signal = "strong_sell"
            strength = min(abs(score) * 2, 1.0)
        elif score < bearish_threshold:
            signal = "sell"
            strength = min(abs(score) * 1.5, 0.8)
        else:
            signal = "hold"
            strength = 0.5
        
        return {
            "signal": signal,
            "strength": round(strength, 2),
            "sentiment_score": score,
            "confidence": confidence,
            "label": sentiment_data.get("overall_label", "neutral"),
            "recommendation": self._get_recommendation(signal, strength)
        }
    
    def _get_recommendation(self, signal: str, strength: float) -> str:
        """Get human-readable recommendation"""
        if signal == "strong_buy":
            return f"STRONG BUY - High confidence bullish sentiment ({strength:.0%})"
        elif signal == "buy":
            return f"BUY - Moderate bullish sentiment ({strength:.0%})"
        elif signal == "strong_sell":
            return f"STRONG SELL - High confidence bearish sentiment ({strength:.0%})"
        elif signal == "sell":
            return f"SELL - Moderate bearish sentiment ({strength:.0%})"
        else:
            return "HOLD - Neutral or mixed sentiment"
    
    def _empty_sentiment(self) -> Dict:
        return {
            "avg_sentiment_score": 0,
            "avg_confidence": 0,
            "overall_label": "neutral",
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "total_articles": 0,
            "articles": [],
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    test_headlines = [
        {
            "title": "RBI keeps interest rates steady, rupee weakens",
            "description": "Reserve Bank of India maintains status quo on rates, causing currency pressure",
            "source": "Economic Times"
        },
        {
            "title": "Dollar strengthens on positive jobs data",
            "description": "US employment numbers beat expectations, boosting USD",
            "source": "Reuters"
        },
        {
            "title": "Oil prices stabilize after OPEC meeting",
            "description": "Crude oil prices hold steady, supporting emerging market currencies",
            "source": "Bloomberg"
        }
    ]
    
    print("=== Sentiment Analysis Test ===\n")
    
    sentiment = analyzer.analyze_news(test_headlines)
    print(f"Average Sentiment Score: {sentiment['avg_sentiment_score']:.4f}")
    print(f"Overall Label: {sentiment['overall_label']}")
    print(f"Bullish: {sentiment['bullish_count']}, Bearish: {sentiment['bearish_count']}, Neutral: {sentiment['neutral_count']}")
    
    signal = analyzer.get_trading_signal(sentiment)
    print(f"\nTrading Signal: {signal['signal']}")
    print(f"Recommendation: {signal['recommendation']}")
