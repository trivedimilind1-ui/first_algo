# first_algo 📈 (INR ₹ Edition)

A modular, risk-first quantitative algorithmic trading framework built in Python for backtesting, paper trading, and strategy research on the Indian Stock Market (NSE/BSE) and global assets.

---

## ⚠️ The Truth About "Making ₹1,000/Day with Minimum Capital"

When beginning algorithmic trading, many aspire to achieve high daily profits (such as **₹1,000/day**) with a **minimal deposit** (such as ₹5,000, ₹10,000, or ₹25,000). Before deploying any capital, understanding the mathematical reality of financial markets is essential.

### 1. The Math of Returns & The Risk of Ruin
* If your capital is **₹5,000** and your target is **₹1,000/day**, your required daily return is:
  $$\text{Daily Return} = \frac{₹1,000}{₹5,000} \times 100\% = 20.0\% \text{ per day}$$
* To generate 20% in a single day, an intraday trader must employ **extreme leverage (20x to 50x)**.
* With 20x to 50x intraday MIS leverage, a **1% to 2% adverse market move triggers broker auto-square-off and wipes out 100% of your account**.
* Mathematically, under normal market volatility, attempting a fixed 20% daily return leads to a **near 100% probability of total account wipeout within weeks**.
* **SEBI Reality Disclosure**: Official SEBI research confirms that **93% of individual retail intraday traders incur net losses** due to excessive leverage, overtrading, and lack of strict stop-loss rules.

### 2. How Professional Quantitative Traders Operate
* The Nifty 50 long-term daily average return is **~0.05% per trading day**.
* A professional retail algorithmic trading strategy with a proven statistical edge typically targets **0.3% to 0.5% average return per trading day** with strict drawdowns.
* To sustainably generate **₹1,000/day** without risking catastrophic liquidation:
  $$\text{Required Capital} = \frac{₹1,000}{0.004} = \mathbf{₹250,000}$$
* **Capital Preservation > Profit Target**: Professional algos never trade to hit an arbitrary rupee figure. They trade to exploit statistical edges while strictly keeping risk per trade capped at **1% to 2%** of portfolio equity.

`first_algo` is built around these institutional risk management principles.

---

## 🌟 Key Features

1. **Risk Management & Circuit Breakers**:
   - **Fixed Fractional Sizing (1% Rule)**: Dynamic position sizing based on stop-loss distance and total equity.
   - **Daily Circuit Breaker**: Halts automated trading immediately if daily loss reaches threshold (e.g., -2.5%) to prevent emotional drawdown spirals.
   - **Mathematical Feasibility Calculator**: Instantly calculates required capital, leverage multipliers, and risk of ruin for any target profit in Rupees (₹).

2. **Modular Strategy Engine**:
   - **`MomentumRSIStrategy`**: Combines Dual Exponential Moving Averages (EMA 9/21) trend confirmation with RSI (14) momentum filters.
   - **`MeanReversionStrategy`**: Bollinger Bands mean-reversion algorithm designed for range-bound assets.
   - Easily extensible via abstract base class `BaseStrategy`.

3. **Event-Driven Backtester**:
   - Intraday high/low stop-loss & take-profit simulation.
   - Market frictions: Models **slippage (0.05%)** and **brokerage/exchange turnover taxes (0.03%)**.
   - Performance analytics: Total Return, Benchmark Buy & Hold, Sharpe Ratio, Maximum Drawdown, Win Rate, and Profit Factor.

4. **Dual Data Feeds**:
   - Live/Historical market data via **Yahoo Finance (`yfinance`)** for Indian stocks (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `^NSEI`).
   - Realistic synthetic market simulation (Geometric Brownian Motion with volatility clustering) for offline research and instant testing.

---

## 📁 Project Architecture

```
first_algo/
├── config.py                   # Indian market parameters (INR ₹), fees, & risk controls
├── main.py                     # CLI entrypoint (backtester & feasibility analyzer)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & Quantitative Guide
├── engine/
│   ├── __init__.py
│   ├── data_feed.py            # Historical & synthetic data provider
│   ├── risk_manager.py         # 1% sizing, circuit breakers & capital math in ₹
│   ├── order_manager.py        # Portfolio state, slippage & trade log
│   └── backtester.py           # Simulation engine & performance metrics
├── strategies/
│   ├── __init__.py
│   ├── base.py                 # Abstract strategy interface & signal types
│   ├── momentum_rsi.py         # EMA Trend + RSI Momentum strategy
│   └── mean_reversion.py       # Bollinger Bands Mean Reversion
└── tests/
    ├── __init__.py
    └── test_risk_and_strategies.py # Unit tests
```

---

## 💻 Usage

### 1. Run the Reality Check & Capital Feasibility Calculator
Analyze what capital is actually required to target ₹1,000/day:
```bash
python main.py --target 1000 --capital 10000 --check-feasibility-only
```

### 2. Run a Strategy Backtest on Indian Stocks (NSE)
Backtest the Momentum EMA + RSI strategy on Reliance Industries (`RELIANCE.NS`) with ₹50,000 starting capital:
```bash
python main.py --symbol RELIANCE.NS --capital 50000 --strategy momentum --timeframe 1h --days 180
```

Backtest on Tata Consultancy Services (`TCS.NS`):
```bash
python main.py --symbol TCS.NS --capital 50000 --strategy mean_reversion --timeframe 1h --days 180
```

### 3. Run Automated Tests
```bash
python -m unittest tests/test_risk_and_strategies.py
```

---

## ⚖️ Disclaimer

*This software is created for educational, research, and simulation purposes only. Algorithmic trading involves substantial risk of loss. Past performance in backtests is never a guarantee of future returns. Never trade with money you cannot afford to lose.*
