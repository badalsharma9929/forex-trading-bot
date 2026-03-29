"""
Technical Indicators Library
Calculates RSI, MACD, Bollinger Bands, EMA, and more
"""
import pandas as pd
import numpy as np


class TechnicalIndicators:
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> dict:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "bandwidth": upper - lower,
            "position": (prices - lower) / (upper - lower)
        }
    
    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> dict:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=3).mean()
        
        return {"k": k, "d": d}
    
    @staticmethod
    def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators and add to DataFrame"""
        result = df.copy()
        
        result["rsi_14"] = TechnicalIndicators.calculate_rsi(df["close"], 14)
        
        macd = TechnicalIndicators.calculate_macd(df["close"])
        result["macd_line"] = macd["macd_line"]
        result["macd_signal"] = macd["signal_line"]
        result["macd_histogram"] = macd["histogram"]
        
        bb = TechnicalIndicators.calculate_bollinger_bands(df["close"])
        result["bb_upper"] = bb["upper"]
        result["bb_middle"] = bb["middle"]
        result["bb_lower"] = bb["lower"]
        result["bb_position"] = bb["position"]
        
        result["ema_12"] = TechnicalIndicators.calculate_ema(df["close"], 12)
        result["ema_26"] = TechnicalIndicators.calculate_ema(df["close"], 26)
        result["sma_20"] = TechnicalIndicators.calculate_sma(df["close"], 20)
        result["sma_50"] = TechnicalIndicators.calculate_sma(df["close"], 50)
        result["sma_200"] = TechnicalIndicators.calculate_sma(df["close"], 200)
        
        result["adx"] = TechnicalIndicators.calculate_adx(df["high"], df["low"], df["close"])
        
        stoch = TechnicalIndicators.calculate_stochastic(df["high"], df["low"], df["close"])
        result["stoch_k"] = stoch["k"]
        result["stoch_d"] = stoch["d"]
        
        result["cci"] = TechnicalIndicators.calculate_cci(df["high"], df["low"], df["close"])
        result["atr"] = TechnicalIndicators.calculate_atr(df["high"], df["low"], df["close"])
        
        if "volume" in df.columns:
            result["obv"] = TechnicalIndicators.calculate_obv(df["close"], df["volume"])
            result["vwap"] = TechnicalIndicators.calculate_vwap(df["high"], df["low"], df["close"], df["volume"])
        
        result["returns"] = df["close"].pct_change()
        result["volatility"] = result["returns"].rolling(window=14).std()
        
        return result


if __name__ == "__main__":
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
    
    print("=== Technical Indicators Calculated ===\n")
    print(f"RSI (14): {df_with_indicators['rsi_14'].iloc[-1]:.2f}")
    print(f"MACD Line: {df_with_indicators['macd_line'].iloc[-1]:.4f}")
    print(f"MACD Signal: {df_with_indicators['macd_signal'].iloc[-1]:.4f}")
    print(f"BB Upper: {df_with_indicators['bb_upper'].iloc[-1]:.4f}")
    print(f"BB Lower: {df_with_indicators['bb_lower'].iloc[-1]:.4f}")
    print(f"EMA 12: {df_with_indicators['ema_12'].iloc[-1]:.4f}")
    print(f"EMA 26: {df_with_indicators['ema_26'].iloc[-1]:.4f}")
    print(f"ATR: {df_with_indicators['atr'].iloc[-1]:.4f}")
    print(f"Stoch K: {df_with_indicators['stoch_k'].iloc[-1]:.2f}")
    print(f"Stoch D: {df_with_indicators['stoch_d'].iloc[-1]:.2f}")
