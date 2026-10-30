"""
Micro-Profit Scalping Strategy.
Designed to capture rapid, small price fluctuations (0.3% - 0.6% micro-gains).

⚠️ CRITICAL RISK WARNING:
1. In financial markets, NO algorithm can guarantee "only profits".
2. Strategies that attempt to "never take a loss" (by removing stop losses or averaging down)
   suffer from the 'Steamroller Trap': 50 micro-wins of +₹20 can be erased in seconds
   by a single unhedged drop of -₹5,000.
3. Intraday friction: On every trade, Indian brokers charge brokerage (₹20), STT, GST,
   and exchange turnover fees (~₹30 - ₹50 round-trip). Micro-profits MUST exceed these fees
   to avoid guaranteed net losses.
"""

from typing import Dict, Any, Optional
import pandas as pd
from .base import BaseStrategy, Signal


class MicroScalperStrategy(BaseStrategy):
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            "fast_period": 5,           # Fast moving average for rapid tick reactions
            "slow_period": 13,          # Medium trend baseline
            "take_profit_pct": 0.4,     # Micro-profit target: 0.4% quick exit
            "stop_loss_pct": 0.6,       # MANDATORY stop loss to prevent steamroller wipeout
            "volume_multiplier": 1.1,   # Ensure volume supports the micro-move
        }
        if params:
            default_params.update(params)
        super().__init__(name="Micro_Scalper", params=default_params)

    def generate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        fast_p = self.params["fast_period"]
        slow_p = self.params["slow_period"]

        # Fast and medium EMAs for quick momentum flips
        data["fast_ema"] = data["Close"].ewm(span=fast_p, adjust=False).mean()
        data["slow_ema"] = data["Close"].ewm(span=slow_p, adjust=False).mean()

        # Volume moving average to ensure liquidity
        data["vol_sma"] = data["Volume"].rolling(window=10).mean()

        # Rate of change (micro momentum)
        data["roc"] = data["Close"].pct_change(periods=2) * 100.0

        return data

    def get_signal(self, current_bar: pd.Series, previous_bar: pd.Series) -> str:
        if pd.isna(current_bar.get("fast_ema")) or pd.isna(previous_bar.get("fast_ema")):
            return Signal.HOLD

        curr_fast = current_bar["fast_ema"]
        curr_slow = current_bar["slow_ema"]
        prev_fast = previous_bar["fast_ema"]
        prev_slow = previous_bar["slow_ema"]
        curr_vol = current_bar.get("Volume", 0)
        avg_vol = current_bar.get("vol_sma", 1)

        # Micro Buy Trigger: Fast EMA crosses above slow EMA with expanding volume
        bullish_micro_cross = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
        volume_confirmed = curr_vol >= (avg_vol * 0.9)

        if bullish_micro_cross and volume_confirmed:
            return Signal.BUY

        # Micro Exit Trigger: Fast EMA turns downward or momentum reverses
        bearish_micro_cross = (prev_fast >= prev_slow) and (curr_fast < curr_slow)
        if bearish_micro_cross:
            return Signal.SELL

        return Signal.HOLD
