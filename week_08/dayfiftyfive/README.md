# Day 55: Strategy Backtesting with VectorBT

**Date:** November 15, 2025

## Learning Objective
To build a high-performance backtesting engine that converts model predictions into trading signals and evaluates their real-world profitability.

## Concepts Covered
- **Vectorized Backtesting**: Using `vectorbt` for lightning-fast performance evaluation on large datasets.
- **Signal Generation**: Transforming probabilities into "Buy," "Sell," and "Hold" decisions using thresholding.
- **Transaction Costs**: Factoring in slippage and commissions to understand the net profitability of a strategy.
- **Performance Metrics**: Calculating Sortino Ratio (downside risk), Calmar Ratio, and Profit Factor.
- **Equity Curves**: Visualizing the growth of capital over time compared to a Buy & Hold benchmark.

## Code Explanation
The `day_fiftyfive.py` script implements the `TradingStrategyBacktester`:
- **`vectorbt_backtest()`**: Wraps the `from_signals` method to compute an entire trading history in one pass.
- **`manual_backtest()`**: A loop-based implementation used to verify the logic and handle custom order rules.
- **`add_transaction_costs()`**: Adjusts the equity curve based on a fixed percentage commission per trade.
- **`benchmark_comparison()`**: Directly compares the strategy against the underlying asset's performance.

## How to Run
1. Install dependencies: `pip install pandas numpy matplotlib yfinance vectorbt`
2. Run the backtester:
```bash
python week_08/dayfiftyfive/day_fiftyfive.py
```

## Reflection
A model that is 60% accurate can still lose money if the average loss is larger than the average win, or if commissions eat the profits. Backtesting is the ultimate "reality check" for any machine learning strategy.
