"""
first_algo - Quantitative Trading & Risk Management Engine.
CLI entrypoint for backtesting, strategy simulation, and target feasibility analysis.
"""

import sys
import argparse
from typing import Dict, Any

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
          Quantitative Algorithmic Trading Framework
================================================================================
    """
    print(banner)


def run_feasibility_check(daily_target: float = 1000.0, capital: float = 500.0):
    """
    Runs an institutional mathematical reality check on the target
    (e.g., $1,000/day profit with minimal capital).
    """
    print("\n" + "=" * 70)
    print("  [QUANTITATIVE FEASIBILITY & RISK OF RUIN ANALYSIS]")
    print("=" * 70)

    analysis = RiskManager.calculate_capital_feasibility(
        daily_target_profit=daily_target, available_capital=capital
    )

    print(f" Target Daily Profit      : ${analysis['daily_target_profit']:,.2f}")
    print(f" Starting Invested Capital: ${analysis['available_capital']:,.2f}")
    print(f" Required Daily Return    : {analysis['required_daily_return_pct']:.2f}% PER DAY")
    print(f" Benchmark Realistic Return: {analysis['realistic_daily_return_pct']:.2f}% per day (0.2-0.5% pro avg)")
    print(f" Excess Leverage Factor   : {analysis['leverage_multiplier_needed']:.1f}x")
    print(f" Risk Assessment          : >>> {analysis['risk_assessment']} <<<")
    print("-" * 70)
    print(" MATHEMATICAL REALITY EXPLANATION:")
    print(analysis["analysis_notes"])
    print("-" * 70)
    print(f" Recommended Capital to safely generate ${daily_target:,.0f}/day (at 1% trade risk):")
    print(f" >>> ${analysis['sustainable_capital_needed']:,.2f} <<<")
    print("=" * 70 + "\n")


def print_backtest_report(metrics: Dict[str, Any]):
    """Pretty prints backtest metrics and trade summary."""
    print("\n" + "=" * 60)
    print("             BACKTEST PERFORMANCE REPORT")
    print("=" * 60)
    print(f" Symbol                   : {metrics['symbol']}")
    print(f" Strategy                 : {metrics['strategy']}")
    print(f" Initial Capital          : ${metrics['initial_capital']:,.2f}")
    print(f" Final Portfolio Equity   : ${metrics['final_equity']:,.2f}")
    print(f" Net Profit / Loss        : ${metrics['net_profit']:+,.2f} ({metrics['total_return_pct']:+.2f}%)")
    print(f" Benchmark Buy & Hold     : {metrics['buy_and_hold_return_pct']:+.2f}%")
    print("-" * 60)
    print(f" Maximum Drawdown (Risk)  : {metrics['max_drawdown_pct']:.2f}%")
    print(f" Sharpe Ratio (Risk-Adj)  : {metrics['sharpe_ratio']:.2f}")
    print(f" Total Closed Trades      : {metrics['total_trades']}")
    print(f" Win Rate                 : {metrics['win_rate_pct']:.1f}%")
    print(f" Profit Factor            : {metrics['profit_factor']:.2f}")
    print(f" Average Winning Trade    : ${metrics['avg_win']:,.2f}")
    print(f" Average Losing Trade     : ${metrics['avg_loss']:,.2f}")
    print(f" Average Daily P&L        : ${metrics['avg_daily_pnl']:+,.2f}/day")
    print("=" * 60)

    trades = metrics["trades"]
    if trades:
        print(f"\n Recent Trades (Last {min(5, len(trades))}):")
        print(f" {'ID':<4} {'Type':<6} {'Entry':<10} {'Exit':<10} {'PnL ($)':<10} {'PnL (%)':<8} {'Reason':<12}")
        print("-" * 65)
        for t in trades[-5:]:
            print(
                f" {t.id:<4} {t.direction:<6} ${t.entry_price:<9.2f} ${t.exit_price:<9.2f} "
                f"${t.pnl:<9.2f} {t.pnl_pct:<+7.2f}% {t.exit_reason:<12}"
            )
        print("-" * 65)


def run_backtest_pipeline(
    symbol: str = "SPY",
    strategy_name: str = "momentum",
    capital: float = 10000.0,
    timeframe: str = "1h",
    days: int = 180,
):
    try:
        from engine import DataFeed, Backtester
        from strategies import MomentumRSIStrategy, MeanReversionStrategy
    except ImportError as e:
        print("\n" + "!" * 70)
        print("  NOTICE: Backtesting and charting require 'pandas' and 'yfinance'.")
        print(f"  Missing module: {e.name}")
        print("  To install, please run in your terminal:")
        print("     pip install -r requirements.txt")
        print("!" * 70 + "\n")
        return None

    print(f"\n[*] Initializing Backtest for {symbol} with ${capital:,.2f} capital...")
    data = DataFeed.fetch_data(symbol=symbol, interval=timeframe, lookback_days=days)

    config = TradingConfig(
        initial_capital=capital,
        default_symbol=symbol,
        timeframe=timeframe,
        lookback_days=days,
    )

    if strategy_name.lower() == "mean_reversion":
        strategy = MeanReversionStrategy()
    else:
        strategy = MomentumRSIStrategy()

    backtester = Backtester(strategy=strategy, data=data, symbol=symbol, config=config)
    metrics = backtester.run()
    print_backtest_report(metrics)
    return metrics


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="first_algo - Quantitative Trading Engine")
    parser.add_argument("--symbol", type=str, default="SPY", help="Trading ticker symbol (e.g. SPY, AAPL, BTC-USD)")
    parser.add_argument("--capital", type=float, default=10000.0, help="Starting investment capital (USD/INR)")
    parser.add_argument("--target", type=float, default=1000.0, help="Daily profit target to evaluate")
    parser.add_argument("--strategy", type=str, default="momentum", choices=["momentum", "mean_reversion"], help="Strategy")
    parser.add_argument("--timeframe", type=str, default="1h", help="Data timeframe (e.g. 5m, 15m, 1h, 1d)")
    parser.add_argument("--days", type=int, default=180, help="Historical lookback days")
    parser.add_argument("--check-feasibility-only", action="store_true", help="Run only the capital/feasibility check")

    args = parser.parse_args()

    # Always show feasibility & risk analysis first to educate and protect the user
    run_feasibility_check(daily_target=args.target, capital=args.capital)

    if not args.check_feasibility_only:
        run_backtest_pipeline(
            symbol=args.symbol,
            strategy_name=args.strategy,
            capital=args.capital,
            timeframe=args.timeframe,
            days=args.days,
        )


if __name__ == "__main__":
    main()
