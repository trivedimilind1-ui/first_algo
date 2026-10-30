"""
Configuration module for first_algo quantitative trading framework.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class TradingConfig:
    # Portfolio & Capital Settings
    initial_capital: float = 10000.0  # Starting capital in account currency
    currency: str = "USD"            # e.g., "USD" or "INR"
    
    # Target & Risk Limits
    daily_profit_target: float = 1000.0   # Desired daily profit benchmark
    max_risk_per_trade_pct: float = 1.0   # Max 1.0% of portfolio at risk per trade
    max_daily_loss_pct: float = 2.5       # Circuit breaker: stop trading if losing 2.5% in a day
    stop_loss_pct: float = 1.5           # Default stop loss percentage
    take_profit_pct: float = 3.0         # Default take profit percentage (1:2 Risk/Reward)
    
    # Execution & Frictions
    slippage_pct: float = 0.05           # 0.05% slippage simulation
    commission_pct: float = 0.03         # 0.03% brokerage / exchange fees
    
    # Asset & Timeframe Defaults
    default_symbol: str = "SPY"          # Benchmark ETF / Equity (e.g. SPY, AAPL, BTC-USD, RELIANCE.NS)
    timeframe: str = "1h"                # 1m, 5m, 15m, 1h, 1d
    lookback_days: int = 180             # Historical window for backtesting
    
    # Safety Controls
    max_open_positions: int = 2
    allow_shorting: bool = False
    enforce_daily_circuit_breaker: bool = True


# Global default configuration instance
DEFAULT_CONFIG = TradingConfig()
