"""
Paper Trading Simulator
Executes virtual trades without real money
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from config.settings import PAPER_TRADING_INITIAL_BALANCE, DATABASE_PATH


class PaperTradingSimulator:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.open_position = None
    
    def get_connection(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def get_current_price(self, pair: str) -> float:
        """Get current market price (simulated)"""
        from data.collectors.price_collector import FreePriceCollector
        collector = FreePriceCollector()
        result = collector.get_latest_price(pair.replace("/", ""))
        return result.get("rate", 83.50)
    
    def open_position(self, pair: str, direction: str, position_size: float,
                     entry_price: float = None, stop_loss: float = None,
                     take_profit: float = None, signal_source: str = "rule_based") -> Dict:
        """Open a new position"""
        if self.has_open_position():
            return {"success": False, "error": "Position already open"}
        
        if entry_price is None:
            entry_price = self.get_current_price(pair)
        
        if stop_loss is None:
            sl_percentage = 0.02
            stop_loss = entry_price * (1 - sl_percentage) if direction == "BUY" else entry_price * (1 + sl_percentage)
        
        if take_profit is None:
            tp_percentage = 0.03
            take_profit = entry_price * (1 + tp_percentage) if direction == "BUY" else entry_price * (1 - tp_percentage)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (pair, direction, entry_price, position_size, 
                              entry_time, status, signal_source)
            VALUES (?, ?, ?, ?, ?, 'open', ?)
        """, (pair, direction.upper(), entry_price, position_size, datetime.now().isoformat(), signal_source))
        
        trade_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        self.open_position = {
            "id": trade_id,
            "pair": pair,
            "direction": direction.upper(),
            "entry_price": entry_price,
            "position_size": position_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": datetime.now().isoformat(),
            "signal_source": signal_source
        }
        
        return {
            "success": True,
            "trade_id": trade_id,
            "message": f"{direction.upper()} position opened",
            "position": self.open_position
        }
    
    def check_position(self, current_price: float = None) -> Dict:
        """Check if open position should be closed"""
        if not self.has_open_position():
            return {"should_close": False, "reason": "No open position"}
        
        position = self.open_position
        
        if current_price is None:
            current_price = self.get_current_price(position["pair"])
        
        pnl_pips = (current_price - position["entry_price"]) * position["position_size"]
        if position["direction"] == "SELL":
            pnl_pips = -pnl_pips
        
        pnl_percentage = (current_price - position["entry_price"]) / position["entry_price"] * 100
        if position["direction"] == "SELL":
            pnl_percentage = -pnl_percentage
        
        should_close = False
        close_reason = ""
        
        if position["direction"] == "BUY":
            if current_price <= position["stop_loss"]:
                should_close = True
                close_reason = "Stop loss hit"
            elif current_price >= position["take_profit"]:
                should_close = True
                close_reason = "Take profit hit"
        else:
            if current_price >= position["stop_loss"]:
                should_close = True
                close_reason = "Stop loss hit"
            elif current_price <= position["take_profit"]:
                should_close = True
                close_reason = "Take profit hit"
        
        return {
            "should_close": should_close,
            "close_reason": close_reason,
            "current_price": current_price,
            "pnl": round(pnl_pips, 2),
            "pnl_percentage": round(pnl_percentage, 2),
            "position": position
        }
    
    def close_position(self, exit_price: float = None, reason: str = "manual") -> Dict:
        """Close the open position"""
        if not self.has_open_position():
            return {"success": False, "error": "No open position to close"}
        
        position = self.open_position
        
        if exit_price is None:
            exit_price = self.get_current_price(position["pair"])
        
        if position["direction"] == "BUY":
            pnl = (exit_price - position["entry_price"]) * position["position_size"]
        else:
            pnl = (position["entry_price"] - exit_price) * position["position_size"]
        
        pnl_percentage = pnl / (position["entry_price"] * position["position_size"]) * 100
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trades 
            SET exit_price = ?,
                exit_time = ?,
                pnl = ?,
                pnl_percentage = ?,
                status = 'closed'
            WHERE id = ? AND status = 'open'
        """, (exit_price, datetime.now().isoformat(), round(pnl, 2), round(pnl_percentage, 2), position["id"]))
        
        conn.commit()
        conn.close()
        
        closed_position = {
            **position,
            "exit_price": exit_price,
            "exit_time": datetime.now().isoformat(),
            "pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_percentage, 2),
            "close_reason": reason
        }
        
        self.open_position = None
        
        return {
            "success": True,
            "message": f"Position closed: {reason}",
            "trade_result": closed_position
        }
    
    def has_open_position(self) -> bool:
        """Check if there's an open position"""
        if self.open_position is not None:
            return True
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'open'")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count > 0
    
    def get_open_position(self) -> Optional[Dict]:
        """Get current open position details"""
        if self.open_position:
            return self.open_position
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pair, direction, entry_price, position_size, 
                   entry_time, signal_source
            FROM trades 
            WHERE status = 'open'
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            self.open_position = {
                "id": row[0],
                "pair": row[1],
                "direction": row[2],
                "entry_price": row[3],
                "position_size": row[4],
                "entry_time": row[5],
                "signal_source": row[6]
            }
            return self.open_position
        
        return None
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trade history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pair, direction, entry_price, exit_price, 
                   position_size, entry_time, exit_time, pnl, 
                   pnl_percentage, status, signal_source
            FROM trades 
            ORDER BY entry_time DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trades = []
        for row in rows:
            trades.append({
                "id": row[0],
                "pair": row[1],
                "direction": row[2],
                "entry_price": row[3],
                "exit_price": row[4],
                "position_size": row[5],
                "entry_time": row[6],
                "exit_time": row[7],
                "pnl": row[8],
                "pnl_percentage": row[9],
                "status": row[10],
                "signal_source": row[11]
            })
        
        return trades
    
    def get_statistics(self) -> Dict:
        """Get trading statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                AVG(CASE WHEN pnl <= 0 THEN pnl END) as avg_loss
            FROM trades 
            WHERE status = 'closed'
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        total = row[0] or 0
        wins = row[1] or 0
        losses = row[2] or 0
        
        return {
            "total_trades": total,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round((wins / total * 100) if total > 0 else 0, 2),
            "total_pnl": round(row[3] or 0, 2),
            "average_pnl": round(row[4] or 0, 2),
            "average_win": round(row[5] or 0, 2),
            "average_loss": round(row[6] or 0, 2),
            "profit_factor": round(abs(row[5] / row[6]) if row[6] and row[5] else 0, 2)
        }


if __name__ == "__main__":
    simulator = PaperTradingSimulator()
    
    print("=== Paper Trading Simulator Test ===\n")
    
    print("Opening BUY position...")
    result = simulator.open_position(
        pair="USD/INR",
        direction="BUY",
        position_size=1000,
        signal_source="rule_based"
    )
    print(f"Result: {result}")
    
    position = simulator.get_open_position()
    print(f"\nOpen Position: {position}")
    
    check = simulator.check_position(current_price=83.70)
    print(f"\nPosition Check: {check}")
    
    if check["should_close"]:
        close_result = simulator.close_position(reason=check["close_reason"])
        print(f"\nClosed Position: {close_result}")
    
    stats = simulator.get_statistics()
    print(f"\nStatistics: {stats}")
