"""Deterministic integrity checks of the ORIGINAL first_algo engine on hand-built bars.
These are engine-behaviour tests, NOT market results."""
import sys
sys.path.insert(0, "/home/claude/trivedimilind1-ui/first_algo")
import pandas as pd, numpy as np
from config import TradingConfig
from engine.backtester import Backtester
from strategies.base import BaseStrategy, Signal

class Scripted(BaseStrategy):
    """Buys on bar BUY_AT, never sells (stop/TP/end only)."""
    def __init__(self, buy_at):
        super().__init__("scripted", {"stop_loss_pct": 1.5, "take_profit_pct": 3.0})
        self.buy_at = buy_at
    def generate_indicators(self, df):
        d = df.copy(); d["n"] = range(len(d)); return d
    def get_signal(self, cur, prev):
        return Signal.BUY if cur["n"] == self.buy_at else Signal.HOLD

def bars(n=40, price=1000.0):
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    return pd.DataFrame({"Open": price, "High": price, "Low": price, "Close": price, "Volume": 1e6}, index=idx)

cfg = TradingConfig(initial_capital=50000.0)

# 1) Signal timing / next-bar execution
d = bars(); d.iloc[31, :4] = 1050.0   # bar after signal gaps +5% and stays there
t = Backtester(Scripted(30), d, "X", cfg); m = t.run()
tr = m["trades"][0]
print(f"[1] signal bar close=1000, next bar open=1050. Entry fill={tr.entry_price:.2f} (bar {d.index.get_loc(tr.entry_time)})")
print("    -> fills at SIGNAL-BAR CLOSE (same bar), not next open: look-ahead", "CONFIRMED" if abs(tr.entry_price-1000.5)<0.01 else "not confirmed")

# 2) Gap-through-stop
d = bars(); d.iloc[32:, :4] = 950.0  # opens 5% below the ~985 stop
t = Backtester(Scripted(30), d, "X", cfg); m = t.run()
tr = m["trades"][0]
print(f"[2] stop=985.0, bar opens/trades at 950. Exit reason={tr.exit_reason}, exit price={tr.exit_price:.2f}")
print("    -> fills at stop price, not the gap open: gap loss understated by", f"{(985*(1-.0005)-950)*tr.shares:,.0f} INR on this trade" if tr.exit_reason=="STOP_LOSS" else "n/a")

# 3) Costs on a flat round trip
d = bars(); t = Backtester(Scripted(30), d, "X", cfg); m = t.run(); tr = m["trades"][0]
print(f"[3] flat price round trip: pnl={tr.pnl:,.2f} on cost basis {tr.entry_price*tr.shares:,.0f} => cost {-tr.pnl/(tr.entry_price*tr.shares)*100:.3f}% (slippage 0.05%x2 + brokerage 0.03%x2). No STT/stamp/GST/exchange/DP charges.")

# 4) Position size concentration
print(f"[4] shares={tr.shares}, notional={tr.entry_price*tr.shares:,.0f} = {tr.entry_price*tr.shares/50000*100:.0f}% of equity from a '1% risk' rule with 1.5% stop")

# 5) Config knobs never read by the engine
import inspect, engine.backtester as b, engine.risk_manager as r, engine.order_manager as o
src = inspect.getsource(b)+inspect.getsource(r)+inspect.getsource(o)
for k in ["max_open_positions","allow_shorting","enforce_daily_circuit_breaker","daily_profit_target","MARKET_CLOSE"]:
    print(f"[5] '{k}' referenced in engine code:", k in src)

# 6) Silent synthetic fallback
from engine.data_feed import DataFeed
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    df = DataFeed.fetch_data("RELIANCE.NS", "1d", 900)
print("[6] fetch_data with Yahoo unreachable returned", len(df), "rows without raising; start price", round(df['Close'].iloc[0],2), "(GBM seed 42, initial 450)")
