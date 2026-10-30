"""
Order and Portfolio Manager.
Tracks portfolio state, simulates executions with market friction (slippage, fees),
and manages open positions and trade logs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any


@dataclass
class Trade:
    id: int
    symbol: str
    entry_time: Any
    exit_time: Optional[Any]
    entry_price: float
    exit_price: float
    shares: int
    direction: str  # "LONG"
    pnl: float
    pnl_pct: float
    commission_paid: float
    exit_reason: str  # "TAKE_PROFIT", "STOP_LOSS", "SIGNAL_EXIT", "MARKET_CLOSE"


@dataclass
class Position:
    symbol: str
    entry_time: Any
    entry_price: float
    shares: int
    stop_loss: float
    take_profit: float
    direction: str = "LONG"


class OrderManager:
    def __init__(
        self,
        initial_capital: float = 10000.0,
        slippage_pct: float = 0.05,
        commission_pct: float = 0.03,
    ):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct

        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self._trade_counter = 0

    @property
    def total_equity(self) -> float:
        # Note: In backtesting, current price is updated per bar
        return self.cash + sum(pos.shares * pos.entry_price for pos in self.positions.values())

    def get_equity(self, current_price: float, symbol: str) -> float:
        pos_val = 0.0
        if symbol in self.positions:
            pos_val = self.positions[symbol].shares * current_price
        return self.cash + pos_val

    def open_position(
        self,
        symbol: str,
        timestamp: Any,
        price: float,
        shares: int,
        stop_loss: float,
        take_profit: float,
    ) -> bool:
        if shares <= 0:
            return False

        # Apply slippage on entry (buy at slightly higher ask)
        exec_price = price * (1.0 + (self.slippage_pct / 100.0))
        cost = exec_price * shares
        commission = cost * (self.commission_pct / 100.0)
        total_required = cost + commission

        if total_required > self.cash:
            # Adjust shares to fit cash
            shares = int((self.cash / (exec_price * (1.0 + self.commission_pct / 100.0))))
            if shares <= 0:
                return False
            cost = exec_price * shares
            commission = cost * (self.commission_pct / 100.0)
            total_required = cost + commission

        self.cash -= total_required
        self.positions[symbol] = Position(
            symbol=symbol,
            entry_time=timestamp,
            entry_price=exec_price,
            shares=shares,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        return True

    def close_position(
        self,
        symbol: str,
        timestamp: Any,
        price: float,
        reason: str = "SIGNAL_EXIT",
    ) -> Optional[Trade]:
        if symbol not in self.positions:
            return None

        pos = self.positions.pop(symbol)

        # Apply slippage on exit (sell at slightly lower bid)
        exec_price = price * (1.0 - (self.slippage_pct / 100.0))
        gross_proceeds = exec_price * pos.shares
        commission = gross_proceeds * (self.commission_pct / 100.0)
        net_proceeds = gross_proceeds - commission

        self.cash += net_proceeds

        cost_basis = pos.entry_price * pos.shares
        pnl = net_proceeds - cost_basis
        pnl_pct = (pnl / cost_basis) * 100.0

        self._trade_counter += 1
        trade = Trade(
            id=self._trade_counter,
            symbol=symbol,
            entry_time=pos.entry_time,
            exit_time=timestamp,
            entry_price=pos.entry_price,
            exit_price=exec_price,
            shares=pos.shares,
            direction=pos.direction,
            pnl=pnl,
            pnl_pct=pnl_pct,
            commission_paid=commission,
            exit_reason=reason,
        )
        self.trades.append(trade)
        return trade
