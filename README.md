# first_algo 📈

A modular, risk-first quantitative algorithmic trading framework built in Python for backtesting, paper trading, and strategy research.

---

## ⚠️ The Truth About "Making \$1,000/Day with Minimum Capital"

When beginning algorithmic trading, many aspire to achieve high daily profits (such as **\$1,000/day**) with a **minimal deposit** (such as \$100, \$500, or \$1,000). Before deploying any capital, understanding the mathematical reality of financial markets is essential.

### 1. The Math of Returns & The Risk of Ruin
* If your capital is **\$500** and your target is **\$1,000/day**, your required daily return is:
  $$\text{Daily Return} = \frac{\$1,000}{\$500} \times 100\% = 200\% \text{ per day}$$
* To generate 200% in a single day, a trader must employ **50x to 100x leverage**.
* With 50x leverage, a **1% to 2% market fluctuation against your trade results in 100% loss of your entire account**.
* Mathematically, under random or volatile market conditions, attempting a fixed 200% daily return leads to a **near 100% probability of total account wipeout within days**.

### 2. How Professional Quantitative Firms Trade
* Top quantitative hedge funds (e.g., Renaissance Technologies, Citadel, Two Sigma) target **30% to 50% net annualized returns** (~0.12% to 0.18% average per trading day).
* A professional retail algorithmic trading strategy with a proven statistical edge typically targets **0.2% to 0.5% average return per trading day** with strict drawdowns.
* To sustainably generate **\$1,000/day** without excessive risk, institutional math dictates:
  $$\text{Required Capital} = \frac{\$1,000}{0.004} = \mathbf{\$250,000}$$
* **Capital Preservation > Profit Target**: Professional algos never trade to hit an arbitrary dollar figure. They trade to exploit statistical edges while strictly keeping risk per trade capped at **1% to 2%** of portfolio equity.

`first_algo` is built around these institutional risk management principles.

---

## 🌟 Key Features

1. **Risk Management & Circuit Breakers**:
   - **Fixed Fractional Sizing (1% Rule)**: Dynamic position sizing based on stop-loss distance and total equity.
   - **Daily Circuit Breaker**: Halts automated trading immediately if daily loss reaches threshold (e.g., -2.5%) to prevent emotional drawdown spirals.
   - **Mathematical Feasibility Calculator**: Instantly calculates required capital, leverage multipliers, and risk of ruin for any target profit.

2. **Modular Strategy Engine**:
   - **`MomentumRSIStrategy`**: Combines Dual Exponential Moving Averages (EMA 9/21) trend confirmation with RSI (14) momentum filters.
   - **`MeanReversionStrategy`**: Bollinger Bands mean-reversion algorithm designed for range-bound assets.
   - Easily extensible via abstract base class `BaseStrategy`.

3. **Event-Driven Backtester**:
   - Intraday high/low stop-loss & take-profit simulation.
   - Market frictions: Models **slippage (0.05%)** and **brokerage/exchange commissions (0.03%)**.
   - Performance analytics: Total Return, Benchmark Buy & Hold, Sharpe Ratio, Maximum Drawdown, Win Rate, and Profit Factor.

4. **Dual Data Feeds**:
   - Live/Historical market data via **Yahoo Finance (`yfinance`)** for global stocks, ETFs, indices, and crypto.
   - Realistic synthetic market simulation (Geometric Brownian Motion with volatility clustering) for offline research and instant testing.

---

## 📁 Project Architecture

```
first_algo/
├── config.py                   # Global configuration & safety controls
├── main.py                     # CLI entrypoint (backtester & feasibility analyzer)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & Quantitative Guide
├── engine/
│   ├── __init__.py
│   ├── data_feed.py            # Historical & synthetic data provider
│   ├── risk_manager.py         # 1% sizing, circuit breakers & capital math
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

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/trivedimilind1-ui/first_algo.git
cd first_algo
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## 💻 Usage

### 1. Run the Reality Check & Capital Feasibility Calculator
Analyze what capital is actually required to target \$1,000/day:
```bash
python main.py --target 1000 --capital 500 --check-feasibility-only
```

### 2. Run a Strategy Backtest
Backtest the Momentum EMA + RSI strategy on SPY ETF with \$10,000 starting capital:
```bash
python main.py --symbol SPY --capital 10000 --strategy momentum --timeframe 1h --days 180
```

Backtest the Bollinger Bands Mean Reversion strategy:
```bash
python main.py --symbol AAPL --capital 15000 --strategy mean_reversion --timeframe 1h --days 180
```

### 3. Run Automated Tests
```bash
python -m unittest discover tests
```

---

## 📊 Sample Output

```
============================================================
             BACKTEST PERFORMANCE REPORT
============================================================
 Symbol                   : SPY
 Strategy                 : Momentum_EMA_RSI
 Initial Capital          : $10,000.00
 Final Portfolio Equity   : $11,240.50
 Net Profit / Loss        : +$1,240.50 (+12.41%)
 Benchmark Buy & Hold     : +8.15%
------------------------------------------------------------
 Maximum Drawdown (Risk)  : -3.85%
 Sharpe Ratio (Risk-Adj)  : 1.82
 Total Closed Trades      : 28
 Win Rate                 : 64.3%
 Profit Factor            : 2.14
 Average Winning Trade    : $112.50
 Average Losing Trade     : -$54.20
 Average Daily P&L        : +$9.84/day
============================================================
```

---

## ⚖️ Disclaimer

*This software is created for educational, research, and simulation purposes only. Algorithmic trading involves substantial risk of loss. Past performance in backtests is never a guarantee of future returns. Never trade with money you cannot afford to lose.*
