"""
Main Forex Trading Bot
Orchestrates all components for automated trading
"""
import time
import logging
from datetime import datetime
from typing import Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.database.schema import init_database
from data.collectors.price_collector import FreePriceCollector
from data.collectors.news_collector import FreeNewsCollector
from strategies.indicators import TechnicalIndicators
from strategies.rule_based import TradingStrategy
from strategies.ml_model import MLTradingModel
from sentiment.analyzer import SentimentAnalyzer
from risk.manager import RiskManager
from paper_trading.simulator import PaperTradingSimulator
from config.settings import UPDATE_INTERVAL_SECONDS, DEFAULT_PAIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ForexTradingBot:
    def __init__(self, pair: str = DEFAULT_PAIR):
        self.pair = pair
        self.pair_code = pair.replace("/", "")
        
        logger.info(f"Initializing Forex Trading Bot for {pair}")
        
        self.price_collector = FreePriceCollector()
        self.news_collector = FreeNewsCollector()
        self.indicators = TechnicalIndicators()
        self.strategy = TradingStrategy()
        self.ml_model = MLTradingModel()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.risk_manager = RiskManager()
        self.simulator = PaperTradingSimulator()
        
        self.is_running = False
        self.iteration_count = 0
        
        logger.info("Bot initialized successfully")
    
    def fetch_data(self) -> Dict:
        """Fetch latest price and news data"""
        logger.info("Fetching market data...")
        
        price_data = self.price_collector.get_latest_price(self.pair_code)
        
        if price_data.get("success"):
            logger.info(f"Price fetched: {price_data['rate']}")
        else:
            logger.warning("Failed to fetch price data")
        
        ohlcv = self.price_collector.get_ohlcv(self.pair_code, periods=100)
        
        news = self.news_collector.fetch_forex_news()
        logger.info(f"Fetched {len(news)} news articles")
        
        return {
            "price": price_data,
            "ohlcv": ohlcv,
            "news": news
        }
    
    def analyze_technical(self, df) -> Dict:
        """Calculate technical indicators and generate signals"""
        if df.empty:
            return {"signal": "HOLD", "reason": "No data"}
        
        df_with_indicators = self.indicators.calculate_all(df)
        
        signal = self.strategy.get_signal(df_with_indicators)
        
        latest = df_with_indicators.iloc[-1]
        
        return {
            "signal": signal["action"],
            "strength": signal["strength"],
            "reason": signal["reason"],
            "indicators": {
                "rsi": latest.get("rsi_14"),
                "macd_histogram": latest.get("macd_histogram"),
                "bb_position": latest.get("bb_position"),
                "adx": latest.get("adx"),
                "atr": latest.get("atr")
            }
        }
    
    def analyze_sentiment(self, news: list) -> Dict:
        """Analyze news sentiment"""
        if not news:
            return {"signal": "HOLD", "label": "neutral"}
        
        sentiment_data = self.sentiment_analyzer.analyze_news(news)
        trading_signal = self.sentiment_analyzer.get_trading_signal(sentiment_data)
        
        return {
            "signal": trading_signal["signal"],
            "strength": trading_signal["strength"],
            "score": sentiment_data["avg_sentiment_score"],
            "label": sentiment_data["overall_label"],
            "confidence": sentiment_data["avg_confidence"],
            "bullish_count": sentiment_data["bullish_count"],
            "bearish_count": sentiment_data["bearish_count"]
        }
    
    def get_ml_prediction(self, df) -> Dict:
        """Get ML model prediction"""
        if df.empty:
            return {"prediction": "HOLD", "confidence": 0}
        
        prediction = self.ml_model.get_ensemble_prediction(df)
        
        return {
            "prediction": prediction["label"],
            "confidence": prediction["confidence"],
            "probability_bullish": prediction["probability_bullish"],
            "probability_bearish": prediction["probability_bearish"]
        }
    
    def make_decision(self, technical: Dict, sentiment: Dict, ml: Dict) -> Dict:
        """Combine all signals and make trading decision"""
        logger.info("Making trading decision...")
        
        signals = {
            "technical": technical["signal"],
            "sentiment": sentiment["signal"],
            "ml": ml["prediction"]
        }
        
        buy_signals = sum(1 for s in signals.values() if "BUY" in s or "buy" in s)
        sell_signals = sum(1 for s in signals.values() if "SELL" in s or "sell" in s)
        
        avg_strength = (technical.get("strength", 0) + sentiment.get("strength", 0) + ml.get("confidence", 0)) / 3
        
        if buy_signals >= 2 and buy_signals > sell_signals:
            decision = "BUY"
            confidence = min(avg_strength * buy_signals / 3, 1.0)
        elif sell_signals >= 2 and sell_signals > buy_signals:
            decision = "SELL"
            confidence = min(avg_strength * sell_signals / 3, 1.0)
        else:
            decision = "HOLD"
            confidence = 0.5
        
        return {
            "decision": decision,
            "confidence": round(confidence, 2),
            "signals": signals,
            "technical_strength": technical.get("strength", 0),
            "sentiment_strength": sentiment.get("strength", 0),
            "ml_confidence": ml.get("confidence", 0)
        }
    
    def execute_trade(self, decision: Dict, current_price: float) -> Dict:
        """Execute paper trade based on decision"""
        risk_check = self.risk_manager.check_risk_limits()
        
        if not risk_check["can_trade"]:
            logger.warning(f"Risk limits breached: {risk_check['reasons']}")
            return {"executed": False, "reason": "risk_limit", "details": risk_check["reasons"]}
        
        if self.simulator.has_open_position():
            position = self.simulator.get_open_position()
            
            position_check = self.simulator.check_position(current_price)
            
            if position_check["should_close"]:
                result = self.simulator.close_position(reason=position_check["close_reason"])
                
                if result.get("success"):
                    trade_result = result["trade_result"]
                    self.risk_manager.update_after_trade(trade_result)
                    logger.info(f"Position closed: {trade_result['pnl']}")
                    return {"executed": True, "action": "CLOSE", "pnl": trade_result["pnl"]}
            
            if decision["decision"] in ["BUY", "SELL"] and decision["decision"] != position["direction"]:
                result = self.simulator.close_position(reason="Reversing position")
                
                if result.get("success"):
                    trade_result = result["trade_result"]
                    self.risk_manager.update_after_trade(trade_result)
            
            return {"executed": False, "reason": "position_open"}
        
        if decision["decision"] in ["BUY", "SELL"] and decision["confidence"] > 0.6:
            account = self.risk_manager.get_account_info()
            
            position_size_calc = self.risk_manager.calculate_position_size(
                entry_price=current_price,
                stop_loss=current_price * (1 - 0.02 if decision["decision"] == "BUY" else 1 + 0.02),
                balance=account["balance"]
            )
            
            result = self.simulator.open_position(
                pair=self.pair,
                direction=decision["decision"],
                position_size=position_size_calc["position_size"],
                entry_price=current_price,
                signal_source="combined_ai"
            )
            
            if result.get("success"):
                logger.info(f"Trade executed: {decision['decision']} at {current_price}")
                return {
                    "executed": True,
                    "action": decision["decision"],
                    "price": current_price,
                    "position_size": position_size_calc["position_size"],
                    "risk": position_size_calc["risk_percentage"]
                }
        
        return {"executed": False, "reason": "no_signal", "confidence": decision["confidence"]}
    
    def run_iteration(self) -> Dict:
        """Run one iteration of the trading loop"""
        self.iteration_count += 1
        logger.info(f"\n{'='*50}")
        logger.info(f"Iteration #{self.iteration_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data = self.fetch_data()
        
        technical = self.analyze_technical(data["ohlcv"])
        logger.info(f"Technical Signal: {technical['signal']} (strength: {technical['strength']})")
        
        sentiment = self.analyze_sentiment(data["news"])
        logger.info(f"Sentiment Signal: {sentiment['signal']} (score: {sentiment['score']:.2f})")
        
        ml = self.get_ml_prediction(data["ohlcv"])
        logger.info(f"ML Prediction: {ml['prediction']} (confidence: {ml['confidence']:.2%})")
        
        decision = self.make_decision(technical, sentiment, ml)
        logger.info(f"Final Decision: {decision['decision']} (confidence: {decision['confidence']:.2%})")
        
        current_price = data["price"].get("rate", 0)
        
        trade_result = self.execute_trade(decision, current_price)
        
        if trade_result.get("executed"):
            logger.info(f"Trade Result: {trade_result}")
        
        metrics = self.risk_manager.get_performance_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "iteration": self.iteration_count,
            "price": current_price,
            "technical": technical,
            "sentiment": sentiment,
            "ml": ml,
            "decision": decision,
            "trade": trade_result,
            "metrics": metrics
        }
    
    def start(self, iterations: int = None):
        """Start the trading bot"""
        logger.info("="*50)
        logger.info("FOREX TRADING BOT STARTED")
        logger.info("="*50)
        
        self.is_running = True
        
        try:
            while self.is_running:
                result = self.run_iteration()
                
                if iterations and self.iteration_count >= iterations:
                    logger.info(f"Completed {iterations} iterations")
                    break
                
                logger.info(f"Next iteration in {UPDATE_INTERVAL_SECONDS} seconds...")
                time.sleep(UPDATE_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping bot...")
        self.is_running = False
        
        if self.simulator.has_open_position():
            logger.info("Closing open position...")
            close_result = self.simulator.close_position(reason="Bot stopped")
            if close_result.get("success"):
                self.risk_manager.update_after_trade(close_result["trade_result"])
        
        logger.info("Bot stopped")


def main():
    print("""
    +==================================================+
    |         FOREX TRADING BOT - PAPER TRADING        |
    |                                                  |
    |  * Technical Analysis (RSI, MACD, Bollinger)    |
    |  * News Sentiment Analysis (FinBERT)             |
    |  * ML Predictions (Random Forest, XGBoost)       |
    |  * Risk Management                                |
    |  * Paper Trading Simulation                       |
    +==================================================+
    """)
    
    init_database()
    
    pair = input("Enter currency pair (default: USD/INR): ").strip() or "USD/INR"
    
    bot = ForexTradingBot(pair=pair)
    
    print(f"\nStarting bot for {pair}...")
    print("Press Ctrl+C to stop\n")
    
    bot.start(iterations=3)


if __name__ == "__main__":
    main()
