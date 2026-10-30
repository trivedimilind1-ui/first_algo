"""
Risk Manager module.
Enforces institutional capital preservation principles:
1. Fixed fractional position sizing (1-2% risk rule).
2. Daily loss circuit breaker to prevent emotional revenge trading and blow-ups.
3. Realistic Capital & Feasibility Analysis for daily profit expectations.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class PositionSizeResult:
    shares: int
    capital_allocated: float
    risk_amount: float
    stop_loss_price: float
    take_profit_price: float
    is_valid: bool
    reason: str = ""


class RiskManager:
    def __init__(
        self,
        max_risk_per_trade_pct: float = 1.0,
        max_daily_loss_pct: float = 2.5,
        default_stop_loss_pct: float = 1.5,
        default_take_profit_pct: float = 3.0,
    ):
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.default_stop_loss_pct = default_stop_loss_pct
        self.default_take_profit_pct = default_take_profit_pct
        self.daily_start_equity: float = 0.0
        self.is_circuit_breaker_tripped: bool = False

    def reset_daily_circuit_breaker(self, current_equity: float):
        """Called at the beginning of each trading day."""
        self.daily_start_equity = current_equity
        self.is_circuit_breaker_tripped = False

    def check_circuit_breaker(self, current_equity: float) -> Tuple[bool, str]:
        """
        Circuit breaker stops trading immediately if losses exceed the daily limit.
        """
        if self.daily_start_equity <= 0:
            self.daily_start_equity = current_equity

        daily_change_pct = ((current_equity - self.daily_start_equity) / self.daily_start_equity) * 100.0

        if daily_change_pct <= -abs(self.max_daily_loss_pct):
            self.is_circuit_breaker_tripped = True
            return True, f"DAILY CIRCUIT BREAKER TRIPPED! Down {daily_change_pct:.2f}% (Limit: -{self.max_daily_loss_pct}%). Trading halted for the day."

        return False, "Normal"

    def calculate_position_size(
        self,
        equity: float,
        cash: float,
        entry_price: float,
        stop_loss_pct: float = 0.0,
        take_profit_pct: float = 0.0,
    ) -> PositionSizeResult:
        """
        Calculates position size using the 1% Risk Rule:
        Risk Amount = Equity * Max_Risk_Pct
        Shares = Risk_Amount / (Entry_Price - Stop_Loss_Price)
        """
        if self.is_circuit_breaker_tripped:
            return PositionSizeResult(0, 0.0, 0.0, 0.0, 0.0, False, "Daily circuit breaker active.")

        sl_pct = stop_loss_pct if stop_loss_pct > 0 else self.default_stop_loss_pct
        tp_pct = take_profit_pct if take_profit_pct > 0 else self.default_take_profit_pct

        stop_loss_price = entry_price * (1.0 - (sl_pct / 100.0))
        take_profit_price = entry_price * (1.0 + (tp_pct / 100.0))
        per_share_risk = entry_price - stop_loss_price

        if per_share_risk <= 0:
            return PositionSizeResult(0, 0.0, 0.0, 0.0, 0.0, False, "Invalid stop loss level.")

        # Total capital allowed to risk on this single trade
        max_risk_capital = equity * (self.max_risk_per_trade_pct / 100.0)

        # Number of shares we can buy without risking more than max_risk_capital if stop is hit
        shares = int(max_risk_capital / per_share_risk)

        # Ensure we don't spend more cash than available
        max_affordable_shares = int(cash / entry_price)
        shares = min(shares, max_affordable_shares)

        if shares <= 0:
            return PositionSizeResult(
                0, 0.0, 0.0, 0.0, 0.0, False, f"Insufficient capital (Cash: ${cash:.2f}, Price: ${entry_price:.2f})."
            )

        capital_allocated = shares * entry_price
        actual_risk_amount = shares * per_share_risk

        return PositionSizeResult(
            shares=shares,
            capital_allocated=capital_allocated,
            risk_amount=actual_risk_amount,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            is_valid=True,
            reason="Approved",
        )

    @staticmethod
    def calculate_capital_feasibility(daily_target_profit: float = 1000.0, available_capital: float = 500.0) -> Dict[str, Any]:
        """
        Analyzes the mathematical feasibility of making $1,000/day with minimal capital.
        Provides realistic institutional estimates.
        """
        required_daily_return_pct = (daily_target_profit / available_capital) * 100.0

        # Benchmarks:
        # Top quantitative hedge funds (e.g. Renaissance Medallion) average ~40-60% annualized (~0.15% - 0.2% daily).
        # S&P 500 long-term daily average return is ~0.04% per trading day.
        # Professional retail day traders aim for 0.2% - 0.5% daily average net of commissions.

        realistic_daily_return_pct = 0.4  # Realistic high-performing target: 0.4% per trading day
        sustainable_capital_needed = daily_target_profit / (realistic_daily_return_pct / 100.0)

        # Leverage required to hit target on low capital:
        leverage_required = required_daily_return_pct / realistic_daily_return_pct

        risk_category = "Extremely High (Certain Account Wipeout)" if required_daily_return_pct > 20 else (
            "High (High Drawdown Risk)" if required_daily_return_pct > 3 else "Realistic / Professional"
        )

        return {
            "daily_target_profit": daily_target_profit,
            "available_capital": available_capital,
            "required_daily_return_pct": required_daily_return_pct,
            "realistic_daily_return_pct": realistic_daily_return_pct,
            "sustainable_capital_needed": sustainable_capital_needed,
            "leverage_multiplier_needed": leverage_required,
            "risk_assessment": risk_category,
            "analysis_notes": (
                f"Attempting to make ${daily_target_profit:.0f}/day on ${available_capital:.0f} requires a "
                f"{required_daily_return_pct:.1f}% daily return ({leverage_required:.1f}x normal leverage).\n"
                f"In real financial markets, trading with this level of leverage means a single adverse price movement "
                f"of ~1% to 2% causes 100% liquidation (total capital loss).\n"
                f"To sustainably target ${daily_target_profit:.0f}/day with sound 1% risk management, a capital base of "
                f"approximately ${sustainable_capital_needed:,.0f} is mathematically required."
            ),
        }
