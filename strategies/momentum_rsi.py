"""
Momentum EMA Crossover + RSI Strategy.
Combines trend direction (EMA 9/21) with momentum confirmation (RSI 14)
to filter false breakouts and trade high-probability swings.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from .base import BaseStrategy, Signal


class MomentumRSIStrategy(BaseStrategy):
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            "fast_ema": 9,
            "slow_ema": 21,
            "rsi_period": 14,
            "rsi_oversold": 40.0,
            "rsi_overbought": 70.0,
            "stop_loss_pct": 1.5,
            "take_profit_pct": 3.0,  # 1:2 Risk/Reward
        }
        if params:
            default_params.update(params)
        super().__init__(name="Momentum_EMA_RSI", params=default_params)

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        # Exponential moving averages for smoother Wilder's RSI
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        fast_period = self.params["fast_ema"]
        slow_period = self.params["slow_ema"]
        rsi_period = self.params["rsi_period"]

        # Exponential Moving Averages
        data["fast_ema"] = data["Close"].ewm(span=fast_period, adjust=False).mean()
        data["slow_ema"] = data["Close"].ewm(span=slow_period, adjust=False).mean()

        # Relative Strength Index
        data["rsi"] = self._calculate_rsi(data["Close"], period=rsi_period)

        # Average True Range (ATR) for volatility tracking
        high_low = data["High"] - data["Low"]
        high_close = (data["High"] - data["Close"].shift(1)).abs()
        low_close = (data["Low"] - data["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data["atr"] = true_range.ewm(span=14, adjust=False).mean()

        return data

    def get_signal(self, current_bar: pd.Series, previous_bar: pd.Series) -> str:
        # Check if indicators are valid
        if pd.isna(current_bar.get("fast_ema")) or pd.isna(current_bar.get("rsi")):
            return Signal.HOLD

        curr_fast = current_bar["fast_ema"]
        curr_slow = current_bar["slow_ema"]
        prev_fast = previous_bar["fast_ema"]
        prev_slow = previous_bar["slow_ema"]
        curr_rsi = current_bar["rsi"]

        # Bullish Crossover: Fast crosses above slow & RSI is bullish (> 50 and < 70)
        bullish_cross = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
        rsi_bullish = 50.0 < curr_rsi < self.params["rsi_overbought"]

        if bullish_cross and rsi_bullish:
            return Signal.BUY

        # Bearish Crossover or Overbought Exhaustion
        bearish_cross = (prev_fast >= prev_slow) and (curr_fast < curr_slow)
        rsi_exhausted = curr_rsi >= self.params["rsi_overbought"] + 5.0  # extreme overbought
        rsi_breakdown = curr_rsi < self.params["rsi_oversold"]

        if bearish_cross or rsi_exhausted or rsi_breakdown:
            return Signal.SELL

        return Signal.HOLD
