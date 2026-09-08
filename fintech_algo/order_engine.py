import time
import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class OrderIntent(BaseModel):
    symbol: str
    action: str  # BUY / SELL
    volume: float = Field(gt=0)
    target_price: float
    max_slippage_pips: float = 1.5
    stop_loss: float
    take_profit: float

class RiskGovernor:
    """
    Automated risk governor enforcing strict daily drawdown and position sizing.
    Directly addresses FTMO / prop firm / quantitative trading requirements.
    """
    def __init__(self, starting_balance: float = 100000.0, max_daily_drawdown_pct: float = 5.0):
        self.starting_balance = starting_balance
        self.current_equity = starting_balance
        self.daily_high_equity = starting_balance
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.is_halted = False

    def check_execution_risk(self, order: OrderIntent) -> Dict[str, Any]:
        drawdown_pct = ((self.daily_high_equity - self.current_equity) / self.daily_high_equity) * 100.0
        
        if drawdown_pct >= self.max_daily_drawdown_pct:
            self.is_halted = True
            return {
                "allowed": False,
                "reason": f"CRITICAL_HALT: Maximum daily drawdown reached ({drawdown_pct:.2f}% >= {self.max_daily_drawdown_pct}%)",
                "action": "EMERGENCY_STOP"
            }
            
        risk_per_trade = abs(order.target_price - order.stop_loss) * order.volume * 100000
        risk_pct = (risk_per_trade / self.current_equity) * 100.0
        
        if risk_pct > 2.0:
            return {
                "allowed": False,
                "reason": f"OVERLEVERAGED: Trade risk exceeds 2% account equity ({risk_pct:.2f}%)",
                "action": "REJECT"
            }
            
        return {
            "allowed": True,
            "current_drawdown_pct": round(drawdown_pct, 2),
            "trade_risk_pct": round(risk_pct, 2),
            "status": "APPROVED_FOR_ROUTING"
        }

    def simulate_execution(self, order: OrderIntent, fill_price: float) -> Dict[str, Any]:
        risk_check = self.check_execution_risk(order)
        if not risk_check["allowed"]:
            return risk_check
            
        slippage = abs(fill_price - order.target_price) * 10000
        if slippage > order.max_slippage_pips:
            return {
                "allowed": False,
                "reason": f"SLIPPAGE_BREACH: Slippage {slippage:.2f} exceeds limit {order.max_slippage_pips} pips",
                "action": "CANCEL_ORDER"
            }
            
        return {
            "status": "FILLED",
            "order_id": f"ORD_{int(time.time_ns())}",
            "symbol": order.symbol,
            "volume": order.volume,
            "fill_price": fill_price,
            "slippage_pips": round(slippage, 2),
            "latency_ms": 1.2
        }

if __name__ == "__main__":
    gov = RiskGovernor(starting_balance=200000.0)
    order = OrderIntent(
        symbol="EURUSD",
        action="BUY",
        volume=2.0,
        target_price=1.0850,
        stop_loss=1.0830,
        take_profit=1.0910
    )
    res = gov.simulate_execution(order, fill_price=1.08505)
    print("Execution Result:", res)
