"""
Database queries and utilities
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class DatabaseQueries:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_price_data(self, pair: str, limit: int = 100) -> pd.DataFrame:
        """Get recent price data"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            f"SELECT * FROM price_data WHERE pair = ? ORDER BY timestamp DESC LIMIT ?",
            conn,
            params=(pair, limit)
        )
        conn.close()
        return df
    
    def get_trades(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Get trade history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                f"SELECT * FROM trades WHERE status = ? ORDER BY entry_time DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                f"SELECT * FROM trades ORDER BY entry_time DESC LIMIT ?",
                (limit,)
            )
        
        columns = [desc[0] for desc in cursor.description]
        trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return trades
    
    def get_account_summary(self) -> Dict:
        """Get account summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM account WHERE id = 1")
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        
        if row:
            summary = dict(zip(columns, row))
        else:
            summary = {}
        
        conn.close()
        return summary
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        return self.get_trades(status='open')
    
    def get_closed_trades(self, days: int = 30) -> List[Dict]:
        """Get closed trades for last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute(
            "SELECT * FROM trades WHERE status = 'closed' AND exit_time > ? ORDER BY exit_time DESC",
            (cutoff,)
        )
        
        columns = [desc[0] for desc in cursor.description]
        trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return trades
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        trades = self.get_closed_trades(days=365)
        
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_win": 0,
                "avg_loss": 0
            }
        
        df = pd.DataFrame(trades)
        
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] <= 0]
        
        return {
            "total_trades": len(df),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(len(wins) / len(df) * 100, 2) if len(df) > 0 else 0,
            "total_pnl": round(df['pnl'].sum(), 2),
            "avg_win": round(wins['pnl'].mean(), 2) if len(wins) > 0 else 0,
            "avg_loss": round(losses['pnl'].mean(), 2) if len(losses) > 0 else 0,
            "max_win": round(df['pnl'].max(), 2),
            "max_loss": round(df['pnl'].min(), 2),
            "profit_factor": round(abs(wins['pnl'].sum() / losses['pnl'].sum()), 2) if len(losses) > 0 and losses['pnl'].sum() != 0 else 0
        }
