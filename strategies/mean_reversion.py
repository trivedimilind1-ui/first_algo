"""
Bollinger Bands Mean Reversion Strategy.
Capitalizes on temporary price overextensions by buying near the lower band
and exiting near the midline or upper band.
"""

from typing import Dict, Any, Optional
import pandas as pd
from .base import BaseStrategy, Signal


class MeanReversionStrategy(BaseStrategy):
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            "period": 20,
            "std_dev": 2.0,
            "stop_loss_pct": 1.5,
            "take_profit_pct": 2.5,
        }
        if params:
            default_params.update(params)
        super().__init__(name="Mean_Reversion_BB", params=default_params)

    def generate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        period = self.params["period"]
        std_dev = self.params["std_dev"]

        data["bb_mid"] = data["Close"].rolling(window=period).mean()
        rolling_std = data["Close"].rolling(window=period).std()
        data["bb_upper"] = data["bb_mid"] + (rolling_std * std_dev)
        data["bb_lower"] = data["bb_mid"] - (rolling_std * std_dev)

        return data

    def get_signal(self, current_bar: pd.Series, previous_bar: pd.Series) -> str:
        if pd.isna(current_bar.get("bb_lower")) or pd.isna(previous_bar.get("bb_lower")):
            return Signal.HOLD

        curr_close = current_bar["Close"]
        prev_close = previous_bar["Close"]
        curr_lower = current_bar["bb_lower"]
        curr_upper = current_bar["bb_upper"]
        curr_mid = current_bar["bb_mid"]

        # Buy Signal: Previous bar was below or near lower band, and current bar rebounds above it
        if prev_close <= previous_bar["bb_lower"] and curr_close > curr_lower:
            return Signal.BUY

        # Exit Signal: Price reaches upper band or reverts
        if curr_close >= curr_upper or (prev_close > curr_mid and curr_close < curr_mid):
            return Signal.SELL

        return Signal.HOLD
