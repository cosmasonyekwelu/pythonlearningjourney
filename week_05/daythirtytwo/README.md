# Day 32: Market Data APIs & Performance Metrics

**Date:** October 23, 2025

## Learning Objective
To integrate external market data APIs into a portfolio management workflow and calculate professional-grade performance metrics.

## Concepts Covered
- **API Integration**: Using `yfinance` to download historical data for a custom portfolio.
- **Portfolio Weighting**: Calculating returns based on asset allocation percentages.
- **Benchmark Comparison**: Measuring portfolio performance against a market index (e.g., SPY).
- **Risk-Adjusted Returns**: Implementing Alpha and Beta calculations to evaluate manager skill vs. market risk.
- **Drawdown Analysis**: Visualizing the peak-to-trough decline of an investment.

## Code Explanation
The `day_thirtytwo.py` script focuses on the `PortfolioAnalyzer` class:
- **`get_portfolio_returns()`**: Takes a dictionary of weights and aggregates their historical performance into a single series.
- **`calculate_metrics()`**: Computes:
    - **Volatility**: Annualized standard deviation of returns.
    - **Sharpe Ratio**: Reward per unit of risk.
    - **Alpha**: Excess return over the benchmark.
    - **Beta**: Sensitivity to market movements.
- **Visualization**: Plots the cumulative growth of $1 in the portfolio versus the benchmark.

## How to Run
1. Ensure `yfinance` and `pandas` are installed.
2. Run the demonstration:
```bash
python week_05/daythirtytwo/day_thirtytwo.py
```

## Reflection
Calculating raw returns is easy, but understanding "Alpha" (skill) versus "Beta" (market exposure) is what separates professional portfolio management from simple indexing.
