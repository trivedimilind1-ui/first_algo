"""
Backtester Module.
Simulates strategy performance bar-by-bar, accounting for:
- Stop-loss and Take-profit limit orders within high-low range
- Signal generation on bar completion
- Friction (slippage + commissions)
- Risk-adjusted quantitative metrics (Sharpe ratio, Max Drawdown, Profit Factor)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from config import TradingConfig
from strategies.base import BaseStrategy, Signal
from .risk_manager import RiskManager
from .order_manager import OrderManager, Trade


class Backtester:
    def __init__(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        symbol: str = "SPY",
        config: Optional[TradingConfig] = None,
    ):
        self.strategy = strategy
        self.data = data.copy()
        self.symbol = symbol
        self.config = config or TradingConfig()

        self.risk_manager = RiskManager(
            max_risk_per_trade_pct=self.config.max_risk_per_trade_pct,
            max_daily_loss_pct=self.config.max_daily_loss_pct,
            default_stop_loss_pct=self.config.stop_loss_pct,
            default_take_profit_pct=self.config.take_profit_pct,
        )
        self.order_manager = OrderManager(
            initial_capital=self.config.initial_capital,
            slippage_pct=self.config.slippage_pct,
            commission_pct=self.config.commission_pct,
        )

        self.equity_curve: List[Dict[str, Any]] = []

    def run(self) -> Dict[str, Any]:
        """Executes the backtest simulation bar by bar."""
        # 1. Compute indicators
        df = self.strategy.generate_indicators(self.data)

        if len(df) < 25:
            raise ValueError("Insufficient data points to run backtest.")

        current_day = None

        for i in range(1, len(df)):
            curr_bar = df.iloc[i]
            prev_bar = df.iloc[i - 1]
            timestamp = df.index[i]

            # Daily circuit breaker reset if new calendar day
            bar_date = getattr(timestamp, "date", lambda: timestamp)()
            if current_day != bar_date:
                current_day = bar_date
                # Reset circuit breaker for the new trading day
                curr_eq = self.order_manager.get_equity(curr_bar["Close"], self.symbol)
                self.risk_manager.reset_daily_circuit_breaker(curr_eq)

            current_price = curr_bar["Close"]
            high_price = curr_bar["High"]
            low_price = curr_bar["Low"]

            # 2. Check open positions for Stop Loss or Take Profit triggers
            if self.symbol in self.order_manager.positions:
                pos = self.order_manager.positions[self.symbol]

                # Stop loss triggered?
                if low_price <= pos.stop_loss:
                    self.order_manager.close_position(
                        self.symbol, timestamp, pos.stop_loss, reason="STOP_LOSS"
                    )
                # Take profit triggered?
                elif high_price >= pos.take_profit:
                    self.order_manager.close_position(
                        self.symbol, timestamp, pos.take_profit, reason="TAKE_PROFIT"
                    )

            # 3. Check circuit breaker status
            curr_equity = self.order_manager.get_equity(current_price, self.symbol)
            is_halted, _ = self.risk_manager.check_circuit_breaker(curr_equity)

            # 4. Generate Strategy Signal
            signal = self.strategy.get_signal(curr_bar, prev_bar)

            # 5. Process Signal if not halted
            if not is_halted:
                if signal == Signal.BUY and self.symbol not in self.order_manager.positions:
                    # Calculate position size via risk manager
                    sizing = self.risk_manager.calculate_position_size(
                        equity=curr_equity,
                        cash=self.order_manager.cash,
                        entry_price=current_price,
                        stop_loss_pct=self.strategy.params.get("stop_loss_pct", self.config.stop_loss_pct),
                        take_profit_pct=self.strategy.params.get("take_profit_pct", self.config.take_profit_pct),
                    )

                    if sizing.is_valid and sizing.shares > 0:
                        self.order_manager.open_position(
                            symbol=self.symbol,
                            timestamp=timestamp,
                            price=current_price,
                            shares=sizing.shares,
                            stop_loss=sizing.stop_loss_price,
                            take_profit=sizing.take_profit_price,
                        )

                elif signal == Signal.SELL and self.symbol in self.order_manager.positions:
                    self.order_manager.close_position(
                        self.symbol, timestamp, current_price, reason="SIGNAL_EXIT"
                    )

            # Record portfolio equity
            end_bar_equity = self.order_manager.get_equity(current_price, self.symbol)
            self.equity_curve.append(
                {
                    "timestamp": timestamp,
                    "equity": end_bar_equity,
                    "cash": self.order_manager.cash,
                    "close": current_price,
                }
            )

        # Close any remaining open position at end of backtest
        if self.symbol in self.order_manager.positions:
            last_bar = df.iloc[-1]
            self.order_manager.close_position(
                self.symbol, df.index[-1], last_bar["Close"], reason="BACKTEST_END"
            )

        return self._calculate_metrics()

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculates performance statistics and quant metrics."""
        eq_df = pd.DataFrame(self.equity_curve)
        if eq_df.empty:
            return {}

        eq_series = eq_df["equity"]
        initial_cap = self.config.initial_capital
        final_cap = eq_series.iloc[-1]
        total_return_pct = ((final_cap - initial_cap) / initial_cap) * 100.0

        # Benchmark Buy & Hold Return
        initial_price = self.data["Close"].iloc[0]
        final_price = self.data["Close"].iloc[-1]
        buy_and_hold_return_pct = ((final_price - initial_price) / initial_price) * 100.0

        # Maximum Drawdown
        running_max = eq_series.cummax()
        drawdowns = (eq_series - running_max) / running_max
        max_drawdown_pct = drawdowns.min() * 100.0

        # Trade metrics
        trades = self.order_manager.trades
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]

        win_rate_pct = (len(winning_trades) / total_trades * 100.0) if total_trades > 0 else 0.0

        total_gain = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (total_gain / total_loss) if total_loss > 0 else (999.0 if total_gain > 0 else 0.0)

        avg_win = (total_gain / len(winning_trades)) if winning_trades else 0.0
        avg_loss = (total_loss / len(losing_trades)) if losing_trades else 0.0

        # Daily Sharpe Ratio
        eq_df["date"] = pd.to_datetime(eq_df["timestamp"]).dt.date
        daily_equity = eq_df.groupby("date")["equity"].last()
        daily_returns = daily_equity.pct_change().dropna()

        if len(daily_returns) > 1 and daily_returns.std() > 0:
            sharpe_ratio = np.sqrt(252) * (daily_returns.mean() / daily_returns.std())
            avg_daily_pnl = (daily_equity.iloc[-1] - daily_equity.iloc[0]) / len(daily_equity)
        else:
            sharpe_ratio = 0.0
            avg_daily_pnl = 0.0

        return {
            "symbol": self.symbol,
            "strategy": self.strategy.name,
            "initial_capital": initial_cap,
            "final_equity": final_cap,
            "net_profit": final_cap - initial_cap,
            "total_return_pct": total_return_pct,
            "buy_and_hold_return_pct": buy_and_hold_return_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": total_trades,
            "win_rate_pct": win_rate_pct,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "avg_daily_pnl": avg_daily_pnl,
            "trades": trades,
        }
