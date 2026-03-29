"""
Rule-Based Trading Strategy
Entry/Exit logic using technical indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime


class TradingStrategy:
    def __init__(self):
        self.buy_conditions = []
        self.sell_conditions = []
        
    def check_buy_conditions(self, df: pd.DataFrame, last_row: int = -1) -> Dict:
        """Check if BUY conditions are met"""
        row = df.iloc[last_row]
        signals = {}
        
        signals["rsi_oversold"] = row.get("rsi_14", 50) < 30
        signals["bb_lower_touch"] = row.get("close", 0) <= row.get("bb_lower", float('inf'))
        signals["macd_bullish"] = row.get("macd_histogram", 0) > 0
        signals["price_above_sma200"] = row.get("close", 0) > row.get("sma_200", 0)
        signals["stoch_oversold"] = row.get("stoch_k", 50) < 20
        signals["cci_oversold"] = row.get("cci", 0) < -100
        
        signals["ema_bullish_cross"] = row.get("ema_12", 0) > row.get("ema_26", 0)
        signals["adx_strong_trend"] = row.get("adx", 0) > 25
        
        required = ["rsi_oversold", "bb_lower_touch"]
        optional = ["macd_bullish", "price_above_sma200", "stoch_oversold", "cci_oversold", "adx_strong_trend"]
        
        required_met = all(signals.get(cond, False) for cond in required)
        optional_count = sum(1 for cond in optional if signals.get(cond, False))
        
        if required_met and optional_count >= 2:
            strength = self._calculate_signal_strength(signals, required + optional, len(required + optional))
            return {"triggered": True, "strength": strength, "signals": signals}
        
        return {"triggered": False, "strength": 0, "signals": signals}
    
    def check_sell_conditions(self, df: pd.DataFrame, last_row: int = -1) -> Dict:
        """Check if SELL conditions are met"""
        row = df.iloc[last_row]
        signals = {}
        
        signals["rsi_overbought"] = row.get("rsi_14", 50) > 70
        signals["bb_upper_touch"] = row.get("close", 0) >= row.get("bb_upper", 0)
        signals["macd_bearish"] = row.get("macd_histogram", 0) < 0
        signals["price_below_sma200"] = row.get("close", 0) < row.get("sma_200", float('inf'))
        signals["stoch_overbought"] = row.get("stoch_k", 50) > 80
        signals["cci_overbought"] = row.get("cci", 0) > 100
        
        signals["ema_bearish_cross"] = row.get("ema_12", 0) < row.get("ema_26", 0)
        
        required = ["rsi_overbought", "bb_upper_touch"]
        optional = ["macd_bearish", "price_below_sma200", "stoch_overbought", "cci_overbought"]
        
        required_met = all(signals.get(cond, False) for cond in required)
        optional_count = sum(1 for cond in optional if signals.get(cond, False))
        
        if required_met and optional_count >= 2:
            strength = self._calculate_signal_strength(signals, required + optional, len(required + optional))
            return {"triggered": True, "strength": strength, "signals": signals}
        
        return {"triggered": False, "strength": 0, "signals": signals}
    
    def _calculate_signal_strength(self, signals: Dict, conditions: list, total: int) -> float:
        """Calculate signal strength as percentage"""
        met = sum(1 for cond in conditions if signals.get(cond, False))
        return round(met / total, 2)
    
    def get_signal(self, df: pd.DataFrame, last_row: int = -1) -> Dict:
        """Get overall trading signal"""
        buy_check = self.check_buy_conditions(df, last_row)
        sell_check = self.check_sell_conditions(df, last_row)
        
        if buy_check["triggered"] and not sell_check["triggered"]:
            return {
                "action": "BUY",
                "strength": buy_check["strength"],
                "reason": "Technical indicators suggest oversold bounce",
                "signals": buy_check["signals"]
            }
        elif sell_check["triggered"] and not buy_check["triggered"]:
            return {
                "action": "SELL",
                "strength": sell_check["strength"],
                "reason": "Technical indicators suggest overbought reversal",
                "signals": sell_check["signals"]
            }
        elif buy_check["triggered"] and sell_check["triggered"]:
            return {
                "action": "HOLD",
                "strength": 0,
                "reason": "Conflicting signals - hold position",
                "signals": {"buy": buy_check["signals"], "sell": sell_check["signals"]}
            }
        else:
            return {
                "action": "HOLD",
                "strength": 0,
                "reason": "No clear signals from technical indicators",
                "signals": {}
            }
    
    def calculate_stop_loss(self, entry_price: float, direction: str, atr: float = None, percentage: float = 0.02) -> float:
        """Calculate stop loss price"""
        if direction.upper() == "BUY":
            return entry_price * (1 - percentage)
        else:
            return entry_price * (1 + percentage)
    
    def calculate_take_profit(self, entry_price: float, direction: str, atr: float = None, percentage: float = 0.03) -> float:
        """Calculate take profit price"""
        if direction.upper() == "BUY":
            return entry_price * (1 + percentage)
        else:
            return entry_price * (1 - percentage)


if __name__ == "__main__":
    from strategies.indicators import TechnicalIndicators
    import random
    from datetime import datetime, timedelta
    
    dates = [(datetime.now() - timedelta(hours=i)) for i in range(100, 0, -1)]
    base_price = 83.50
    
    data = {
        "timestamp": dates,
        "open": [base_price + random.uniform(-0.1, 0.1) for _ in range(100)],
        "high": [base_price + random.uniform(0, 0.2) for _ in range(100)],
        "low": [base_price - random.uniform(0, 0.2) for _ in range(100)],
        "close": [base_price + random.uniform(-0.15, 0.15) for _ in range(100)],
        "volume": [random.randint(1000, 10000) for _ in range(100)]
    }
    
    df = pd.DataFrame(data)
    df_with_indicators = TechnicalIndicators.calculate_all(df)
    
    strategy = TradingStrategy()
    signal = strategy.get_signal(df_with_indicators)
    
    print("=== Rule-Based Strategy Test ===\n")
    print(f"Signal: {signal['action']}")
    print(f"Strength: {signal['strength']}")
    print(f"Reason: {signal['reason']}")
