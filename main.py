"""
first_algo - Quantitative Trading & Risk Management Engine.
CLI entrypoint for backtesting, strategy simulation, and target feasibility analysis (in INR ₹).
"""

import sys
import argparse
from typing import Dict, Any

# Ensure Windows terminal can print unicode characters (₹)
try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import TradingConfig, DEFAULT_CONFIG
from engine.risk_manager import RiskManager


def print_banner():
    banner = r"""
================================================================================
   ______ _             _              _                  
  / ____/(_)____ _____ / /_   ____ _  | | ____ _  ____    
 / /_   / // ___// ___// __ \ / __ `/  / // __ `/ / __ \   
/ __/  / // /   (__  )/ / / // /_/ /  / // /_/ / / /_/ /   
/_/    /_//_/   /____//_/ /_/ \__,_/  /_/ \__, /  \____/    
                                         /____/            
     Quantitative Algorithmic Trading Framework (INR ₹ Edition)
================================================================================
    """
    print(banner)


def run_feasibility_check(
    daily_target: float = 1000.0,
    capital: float = 25000.0,
    currency_symbol: str = "₹",
):
    """
    Runs an institutional mathematical reality check on the target
    (e.g., ₹1,000/day profit with minimal capital).
    """
    sym = currency_symbol
    print("\n" + "=" * 72)
    print(f"  [QUANTITATIVE FEASIBILITY & RISK OF RUIN ANALYSIS ({sym} INR)]")
    print("=" * 72)

    analysis = RiskManager.calculate_capital_feasibility(
        daily_target_profit=daily_target,
        available_capital=capital,
        currency_symbol=sym,
    )

    print(f" Target Daily Profit      : {sym}{analysis['daily_target_profit']:,.2f}")
    print(f" Starting Invested Capital: {sym}{analysis['available_capital']:,.2f}")
    print(f" Required Daily Return    : {analysis['required_daily_return_pct']:.2f}% PER DAY")
    print(f" Benchmark Realistic Return: {analysis['realistic_daily_return_pct']:.2f}% per day (0.2-0.5% pro avg)")
    print(f" Excess Leverage Factor   : {analysis['leverage_multiplier_needed']:.1f}x")
    print(f" Risk Assessment          : >>> {analysis['risk_assessment']} <<<")
    print("-" * 72)
    print(" MATHEMATICAL REALITY EXPLANATION:")
    print(analysis["analysis_notes"])
    print("-" * 72)
    print(f" Recommended Capital to safely generate {sym}{daily_target:,.0f}/day (at 1% trade risk):")
    print(f" >>> {sym}{analysis['sustainable_capital_needed']:,.2f} <<<")
    print("=" * 72 + "\n")


def print_backtest_report(metrics: Dict[str, Any]):
    """Pretty prints backtest metrics and trade summary with INR (₹)."""
    sym = metrics.get("currency_symbol", "₹")
    print("\n" + "=" * 65)
    print("             BACKTEST PERFORMANCE REPORT (INR)")
    print("=" * 65)
    print(f" Symbol                   : {metrics['symbol']}")
    print(f" Strategy                 : {metrics['strategy']}")
    print(f" Initial Capital          : {sym}{metrics['initial_capital']:,.2f}")
    print(f" Final Portfolio Equity   : {sym}{metrics['final_equity']:,.2f}")
    print(f" Net Profit / Loss        : {sym}{metrics['net_profit']:+,.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f" Benchmark Buy & Hold     : {metrics['buy_and_hold_return_pct']:+.2f}%")
    print("-" * 65)
    print(f" Maximum Drawdown (Risk)  : {metrics['max_drawdown_pct']:.2f}%")
    print(f" Sharpe Ratio (Risk-Adj)  : {metrics['sharpe_ratio']:.2f}")
    print(f" Total Closed Trades      : {metrics['total_trades']}")
    print(f" Win Rate                 : {metrics['win_rate_pct']:.1f}%")
    print(f" Profit Factor            : {metrics['profit_factor']:.2f}")
    print(f" Average Winning Trade    : {sym}{metrics['avg_win']:,.2f}")
    print(f" Average Losing Trade     : {sym}{metrics['avg_loss']:,.2f}")
    print(f" Average Daily P&L        : {sym}{metrics['avg_daily_pnl']:+,.2f}/day")
    print("=" * 65)

    trades = metrics["trades"]
    if trades:
        print(f"\n Recent Trades (Last {min(5, len(trades))}):")
        print(f" {'ID':<4} {'Type':<6} {'Entry':<12} {'Exit':<12} {'PnL (₹)':<12} {'PnL (%)':<8} {'Reason':<12}")
        print("-" * 70)
        for t in trades[-5:]:
            print(
                f" {t.id:<4} {t.direction:<6} {sym}{t.entry_price:<11.2f} {sym}{t.exit_price:<11.2f} "
                f"{sym}{t.pnl:<11.2f} {t.pnl_pct:<+7.2f}% {t.exit_reason:<12}"
            )
        print("-" * 70)


def run_backtest_pipeline(
    symbol: str = "RELIANCE.NS",
    strategy_name: str = "momentum",
    capital: float = 50000.0,
    timeframe: str = "1h",
    days: int = 180,
    currency_symbol: str = "₹",
):
    sym = currency_symbol
    try:
        from engine import DataFeed, Backtester
        from strategies import (
            MomentumRSIStrategy,
            MeanReversionStrategy,
            MicroScalperStrategy,
        )
    except ImportError as e:
        print("\n" + "!" * 70)
        print("  NOTICE: Live NSE data and backtesting require 'pandas' and 'yfinance'.")
        print(f"  Missing module: {e.name}")
        print("  To install, please run in your terminal:")
        print("     pip install pandas yfinance")
        print("!" * 70 + "\n")
        return None

    print(f"\n[*] Initializing Backtest for {symbol} with {sym}{capital:,.2f} capital...")
    data = DataFeed.fetch_data(symbol=symbol, interval=timeframe, lookback_days=days)

    config = TradingConfig(
        initial_capital=capital,
        currency="INR",
        currency_symbol=sym,
        default_symbol=symbol,
        timeframe=timeframe,
        lookback_days=days,
    )

    if strategy_name.lower() == "mean_reversion":
        strategy = MeanReversionStrategy()
    elif strategy_name.lower() in ("scalper", "micro_scalper"):
        print("\n[!] RUNNING MICRO-SCALPER (MICRO-PROFIT TARGETING)")
        print("    Target: +0.4% quick take-profit per trade.")
        print("    Safety: -0.6% stop-loss enforced to prevent total steamroller wipeouts.")
        strategy = MicroScalperStrategy()
    else:
        strategy = MomentumRSIStrategy()

    backtester = Backtester(strategy=strategy, data=data, symbol=symbol, config=config)
    metrics = backtester.run()
    print_backtest_report(metrics)
    return metrics


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="first_algo - Quantitative Trading Engine (INR ₹)")
    parser.add_argument(
        "--symbol",
        type=str,
        default=DEFAULT_CONFIG.default_symbol,
        help="Trading ticker symbol (e.g. RELIANCE.NS, TCS.NS, INFY.NS, ^NSEI)",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=DEFAULT_CONFIG.initial_capital,
        help="Starting investment capital in Rupees (default: ₹50,000)",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=DEFAULT_CONFIG.daily_profit_target,
        help="Daily profit target in Rupees (default: ₹1,000)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="momentum",
        choices=["momentum", "mean_reversion", "scalper"],
        help="Strategy (momentum, mean_reversion, or scalper)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default=DEFAULT_CONFIG.timeframe,
        help="Data timeframe (e.g. 5m, 15m, 1h, 1d)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_CONFIG.lookback_days,
        help="Historical lookback days",
    )
    parser.add_argument(
        "--check-feasibility-only",
        action="store_true",
        help="Run only the capital/feasibility check",
    )

    args = parser.parse_args()

    # Always show feasibility & risk analysis first to educate and protect the user
    run_feasibility_check(
        daily_target=args.target,
        capital=args.capital,
        currency_symbol=DEFAULT_CONFIG.currency_symbol,
    )

    if not args.check_feasibility_only:
        run_backtest_pipeline(
            symbol=args.symbol,
            strategy_name=args.strategy,
            capital=args.capital,
            timeframe=args.timeframe,
            days=args.days,
            currency_symbol=DEFAULT_CONFIG.currency_symbol,
        )


if __name__ == "__main__":
    main()
