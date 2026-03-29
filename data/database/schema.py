import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "forex_bot.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pair, timestamp)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT,
            title TEXT,
            description TEXT,
            source TEXT,
            url TEXT,
            published_at TEXT,
            sentiment_score REAL DEFAULT 0,
            sentiment_label TEXT DEFAULT 'neutral',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL,
            position_size REAL NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            pnl REAL DEFAULT 0,
            pnl_percentage REAL DEFAULT 0,
            status TEXT DEFAULT 'open',
            signal_source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            balance REAL DEFAULT 100000.0,
            equity REAL DEFAULT 100000.0,
            max_drawdown REAL DEFAULT 0.0,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            daily_pnl REAL DEFAULT 0,
            consecutive_losses INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            rsi_14 REAL,
            macd_line REAL,
            macd_signal REAL,
            macd_histogram REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            ema_12 REAL,
            ema_26 REAL,
            sma_20 REAL,
            adx REAL,
            stochastic_k REAL,
            stochastic_d REAL,
            cci REAL,
            atr REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pair, timestamp)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction INTEGER,
            probability_bullish REAL,
            probability_bearish REAL,
            confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT,
            timestamp TEXT NOT NULL,
            avg_sentiment_score REAL DEFAULT 0,
            bullish_articles INTEGER DEFAULT 0,
            bearish_articles INTEGER DEFAULT 0,
            neutral_articles INTEGER DEFAULT 0,
            overall_label TEXT DEFAULT 'neutral',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_pair_time ON price_data(pair, timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_pair_time ON news_data(pair, published_at)
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO account (id, balance, equity) VALUES (1, 100000.0, 100000.0)
    """)
    
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully")

if __name__ == "__main__":
    init_database()
