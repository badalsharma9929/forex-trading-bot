"""
Risk Management Module
Position sizing, kill switch, drawdown limits
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from config.settings import RISK_MANAGEMENT, PAPER_TRADING_INITIAL_BALANCE


class RiskManager:
    def __init__(self, db_path: str = "data/database/forex_bot.db"):
        self.db_path = db_path
        self.config = RISK_MANAGEMENT
        
        self.max_risk_per_trade = self.config["max_risk_per_trade"]
        self.max_position_size = self.config["max_position_size"]
        self.max_drawdown = self.config["max_drawdown"]
        self.daily_loss_limit = self.config["daily_loss_limit"]
        self.max_consecutive_losses = self.config["max_consecutive_losses"]
        
        self.trading_halted = False
        self.halt_reason = ""
    
    def get_account_info(self) -> Dict:
        """Get current account information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM account WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            account = {
                "balance": row[1],
                "equity": row[2],
                "max_drawdown": row[3],
                "total_trades": row[4],
                "winning_trades": row[5],
                "losing_trades": row[6],
                "daily_pnl": row[7],
                "consecutive_losses": row[8]
            }
        else:
            account = {
                "balance": PAPER_TRADING_INITIAL_BALANCE,
                "equity": PAPER_TRADING_INITIAL_BALANCE,
                "max_drawdown": 0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "daily_pnl": 0,
                "consecutive_losses": 0
            }
        
        conn.close()
        return account
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, balance: float = None) -> Dict:
        """Calculate optimal position size based on risk management rules"""
        if balance is None:
            balance = self.get_account_info()["balance"]
        
        risk_amount = balance * self.max_risk_per_trade
        
        price_diff = abs(entry_price - stop_loss)
        if price_diff == 0:
            price_diff = entry_price * 0.02
        
        position_size = risk_amount / price_diff
        
        max_position_value = balance * self.max_position_size
        max_units = max_position_value / entry_price
        
        final_position_size = min(position_size, max_units)
        
        actual_risk = final_position_size * price_diff
        actual_risk_percentage = (actual_risk / balance) * 100 if balance > 0 else 0
        
        return {
            "position_size": round(final_position_size, 2),
            "risk_amount": round(actual_risk, 2),
            "risk_percentage": round(actual_risk_percentage, 2),
            "max_position_value": round(final_position_size * entry_price, 2),
            "stop_loss_distance": round(price_diff, 4)
        }
    
    def check_risk_limits(self, proposed_trade: Dict = None) -> Dict:
        """Check if trading should proceed based on risk limits"""
        account = self.get_account_info()
        
        checks = {
            "can_trade": True,
            "reasons": [],
            "warnings": []
        }
        
        if self.trading_halted:
            checks["can_trade"] = False
            checks["reasons"].append(f"Trading halted: {self.halt_reason}")
            return checks
        
        if account["total_trades"] == 0:
            return checks
        
        current_drawdown = (PAPER_TRADING_INITIAL_BALANCE - account["equity"]) / PAPER_TRADING_INITIAL_BALANCE
        
        if current_drawdown >= self.max_drawdown:
            self.trading_halted = True
            self.halt_reason = f"Max drawdown exceeded: {current_drawdown:.1%}"
            checks["can_trade"] = False
            checks["reasons"].append(self.halt_reason)
            return checks
        
        daily_loss_pct = abs(account["daily_pnl"]) / PAPER_TRADING_INITIAL_BALANCE
        if daily_loss_pct >= self.daily_loss_limit:
            checks["can_trade"] = False
            checks["reasons"].append(f"Daily loss limit reached: {daily_loss_pct:.1%}")
        
        if account["consecutive_losses"] >= self.max_consecutive_losses:
            checks["can_trade"] = False
            checks["reasons"].append(f"Max consecutive losses: {account['consecutive_losses']}")
        
        if current_drawdown > self.max_drawdown * 0.7:
            checks["warnings"].append(f"Approaching max drawdown: {current_drawdown:.1%}")
        
        if daily_loss_pct > self.daily_loss_limit * 0.8:
            checks["warnings"].append(f"Approaching daily loss limit: {daily_loss_pct:.1%}")
        
        return checks
    
    def update_after_trade(self, trade_result: Dict):
        """Update account after trade closes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE account 
            SET equity = equity + ?,
                daily_pnl = daily_pnl + ?,
                total_trades = total_trades + 1,
                winning_trades = winning_trades + ?,
                losing_trades = losing_trades + ?,
                consecutive_losses = CASE 
                    WHEN ? > 0 THEN 0 
                    ELSE consecutive_losses + 1 
                END,
                max_drawdown = MAX(max_drawdown, ?),
                updated_at = ?
            WHERE id = 1
        """, (
            trade_result["pnl"],
            trade_result["pnl"],
            1 if trade_result["pnl"] > 0 else 0,
            1 if trade_result["pnl"] <= 0 else 0,
            trade_result["pnl"],
            (PAPER_TRADING_INITIAL_BALANCE - (self.get_account_info()["equity"] + trade_result["pnl"])) / PAPER_TRADING_INITIAL_BALANCE,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.check_risk_limits()
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of trading day)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE account 
            SET daily_pnl = 0,
                consecutive_losses = 0
            WHERE id = 1
        """)
        
        conn.commit()
        conn.close()
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        account = self.get_account_info()
        
        total_trades = account["total_trades"]
        winning = account["winning_trades"]
        losing = account["losing_trades"]
        
        win_rate = (winning / total_trades * 100) if total_trades > 0 else 0
        
        current_drawdown = (PAPER_TRADING_INITIAL_BALANCE - account["equity"]) / PAPER_TRADING_INITIAL_BALANCE
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning,
            "losing_trades": losing,
            "win_rate": round(win_rate, 2),
            "current_equity": round(account["equity"], 2),
            "total_pnl": round(account["equity"] - PAPER_TRADING_INITIAL_BALANCE, 2),
            "total_pnl_percentage": round((account["equity"] - PAPER_TRADING_INITIAL_BALANCE) / PAPER_TRADING_INITIAL_BALANCE * 100, 2),
            "current_drawdown": round(current_drawdown * 100, 2),
            "max_drawdown": round(account["max_drawdown"] * 100, 2),
            "daily_pnl": round(account["daily_pnl"], 2),
            "is_halted": self.trading_halted,
            "halt_reason": self.halt_reason
        }
    
    def emergency_stop(self):
        """Emergency stop - halt all trading"""
        self.trading_halted = True
        self.halt_reason = "Manual emergency stop triggered"
        print("[RISK] EMERGENCY STOP ACTIVATED")
    
    def resume_trading(self):
        """Resume trading after stop"""
        self.trading_halted = False
        self.halt_reason = ""
        print("[RISK] Trading resumed")


if __name__ == "__main__":
    risk_manager = RiskManager()
    
    print("=== Risk Management Test ===\n")
    
    account = risk_manager.get_account_info()
    print(f"Account Balance: ₹{account['balance']:,.2f}")
    print(f"Account Equity: ₹{account['equity']:,.2f}")
    
    position = risk_manager.calculate_position_size(
        entry_price=83.50,
        stop_loss=83.00,
        balance=account["balance"]
    )
    print(f"\nPosition Sizing (Entry: 83.50, SL: 83.00):")
    print(f"  Position Size: {position['position_size']:,.2f} units")
    print(f"  Risk Amount: ₹{position['risk_amount']:,.2f}")
    print(f"  Risk %: {position['risk_percentage']:.2f}%")
    
    risk_check = risk_manager.check_risk_limits()
    print(f"\nRisk Check: {'PASSED' if risk_check['can_trade'] else 'FAILED'}")
    if risk_check['reasons']:
        print(f"  Reasons: {risk_check['reasons']}")
    
    metrics = risk_manager.get_performance_metrics()
    print(f"\nPerformance Metrics:")
    print(f"  Win Rate: {metrics['win_rate']:.1f}%")
    print(f"  Total P&L: ₹{metrics['total_pnl']:,.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
