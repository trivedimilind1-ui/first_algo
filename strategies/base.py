"""
Base Strategy Interface for first_algo.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd


class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BaseStrategy(ABC):
    """
    Abstract Base Class for all trading strategies.
    Strategies process market data bars and generate buy/sell signals with stop-loss / take-profit.
    """

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute technical indicators required for the strategy on the historical dataframe.
        """
        pass

    @abstractmethod
    def get_signal(self, current_bar: pd.Series, previous_bar: pd.Series) -> str:
        """
        Evaluate the latest bar against previous bar and return Signal.BUY, Signal.SELL, or Signal.HOLD.
        """
        pass

    def __repr__(self) -> str:
        return f"<Strategy: {self.name} (params={self.params})>"
