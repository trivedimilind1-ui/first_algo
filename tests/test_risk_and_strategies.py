"""
Unit tests for first_algo trading framework.
Verifies risk management, position sizing, circuit breakers, and strategy indicators.
"""

import unittest

from config import TradingConfig
from engine.risk_manager import RiskManager
from engine.order_manager import OrderManager

try:
    import pandas as pd
    import numpy as np
    from engine.data_feed import DataFeed
    from strategies.momentum_rsi import MomentumRSIStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.risk_mgr = RiskManager(
            max_risk_per_trade_pct=1.0,
            max_daily_loss_pct=2.5,
            default_stop_loss_pct=1.5,
            default_take_profit_pct=3.0,
        )

    def test_position_sizing_1_percent_rule(self):
        equity = 10000.0
        cash = 10000.0
        entry_price = 100.0
        # 1% of 10000 is 100 risk
        # Stop loss is 1.5% -> $1.50 per share risk
        # 100 / 1.50 = 66 shares
        res = self.risk_mgr.calculate_position_size(equity, cash, entry_price)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.shares, 66)
        self.assertAlmostEqual(res.stop_loss_price, 98.5, places=2)
        self.assertAlmostEqual(res.take_profit_price, 103.0, places=2)
        self.assertLessEqual(res.risk_amount, 100.0)

    def test_circuit_breaker_trips_on_loss(self):
        self.risk_mgr.reset_daily_circuit_breaker(10000.0)
        # Drops by 3% (exceeds 2.5% max limit)
        is_tripped, msg = self.risk_mgr.check_circuit_breaker(9700.0)
        self.assertTrue(is_tripped)
        self.assertTrue(self.risk_mgr.is_circuit_breaker_tripped)

        # After trip, new trades should be rejected
        res = self.risk_mgr.calculate_position_size(9700.0, 9700.0, 100.0)
        self.assertFalse(res.is_valid)

    def test_capital_feasibility_calculator(self):
        feasibility = RiskManager.calculate_capital_feasibility(daily_target_profit=1000.0, available_capital=500.0)
        self.assertEqual(feasibility["required_daily_return_pct"], 200.0)
        self.assertGreater(feasibility["sustainable_capital_needed"], 100000.0)
        self.assertIn("Wipeout", feasibility["risk_assessment"])


class TestOrderManager(unittest.TestCase):
    def setUp(self):
        self.order_mgr = OrderManager(initial_capital=10000.0, slippage_pct=0.05, commission_pct=0.03)

    def test_open_and_close_trade_with_pnl(self):
        success = self.order_mgr.open_position(
            symbol="TEST",
            timestamp="2026-01-01 10:00",
            price=100.0,
            shares=50,
            stop_loss=98.5,
            take_profit=103.0,
        )
        self.assertTrue(success)
        self.assertIn("TEST", self.order_mgr.positions)

        # Close position with profit at $105
        trade = self.order_mgr.close_position("TEST", "2026-01-01 15:00", 105.0, reason="TAKE_PROFIT")
        self.assertIsNotNone(trade)
        self.assertNotIn("TEST", self.order_mgr.positions)
        self.assertGreater(trade.pnl, 0)
        self.assertEqual(len(self.order_mgr.trades), 1)


@unittest.skipUnless(HAS_PANDAS, "pandas/numpy dependencies not installed")
class TestStrategies(unittest.TestCase):
    def setUp(self):
        self.data = DataFeed.generate_synthetic_data(days=60)

    def test_momentum_rsi_indicators(self):
        strat = MomentumRSIStrategy()
        df = strat.generate_indicators(self.data)
        self.assertIn("fast_ema", df.columns)
        self.assertIn("slow_ema", df.columns)
        self.assertIn("rsi", df.columns)

    def test_mean_reversion_indicators(self):
        strat = MeanReversionStrategy()
        df = strat.generate_indicators(self.data)
        self.assertIn("bb_mid", df.columns)
        self.assertIn("bb_upper", df.columns)
        self.assertIn("bb_lower", df.columns)


if __name__ == "__main__":
    unittest.main()
