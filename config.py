"""
Configuration module for first_algo quantitative trading framework.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class TradingConfig:
    # Portfolio & Capital Settings (in Indian Rupees - INR)
    initial_capital: float = 50000.0     # Starting capital in INR (e.g. ₹50,000)
    currency: str = "INR"                # Currency code
    currency_symbol: str = "₹"           # Currency symbol
    
    # Target & Risk Limits
    daily_profit_target: float = 1000.0  # Target: ₹1,000 profit per day
    max_risk_per_trade_pct: float = 1.0  # Max 1.0% of portfolio at risk per trade
    max_daily_loss_pct: float = 2.5      # Circuit breaker: stop trading if losing 2.5% in a day
    stop_loss_pct: float = 1.5          # Default stop loss percentage
    take_profit_pct: float = 3.0        # Default take profit percentage (1:2 Risk/Reward)
    
    # Execution & Indian Market Frictions (STT, brokerage, exchange turnover)
    slippage_pct: float = 0.05          # 0.05% slippage simulation
    commission_pct: float = 0.03        # 0.03% brokerage / exchange charges
    
    # Asset & Timeframe Defaults (NSE India symbols use .NS suffix in yfinance)
    default_symbol: str = "RELIANCE.NS" # e.g. RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ^NSEI
    timeframe: str = "1h"               # 5m, 15m, 1h, 1d
    lookback_days: int = 180            # Historical window for backtesting
    
    # Safety Controls
    max_open_positions: int = 2
    allow_shorting: bool = False
    enforce_daily_circuit_breaker: bool = True


# Global default configuration instance
DEFAULT_CONFIG = TradingConfig()
