# Day 69: Crypto Trading Strategies

**Date:** November 29, 2025

## Learning Objective
To implement specialized cryptocurrency trading strategies that leverage both technical indicators and unique on-chain metrics.

## Concepts Covered
- **Momentum Strategies**: Using moving average crossovers optimized for 24/7 crypto markets.
- **Statistical Arbitrage**: Finding cointegrated pairs (e.g., BTC and ETH) to trade the spread.
- **Whale Accumulation**: Generating signals from large-wallet transaction data.
- **Network Health**: Using NVT and MVRV ratios to identify "fair value" for a network.
- **Risk Management**: Implementing volatility-adjusted stop losses and position sizing.

## Code Explanation
The `day_sixtynine.py` script provides a quantitative strategy toolbox:
- **`TechnicalStrategy`**: Implements classic RSI and Bollinger Band signals using the `talib` library.
- **`StatisticalArbitrage`**: Uses the Engle-Granger test to identify pairs suitable for mean reversion.
- **`OnChainStrategy`**: Converts raw transaction flows into directional signals.
- **`BacktestEngine`**: A vectorized evaluator that calculates Sharpe Ratio, Max Drawdown, and Profit Factor for each strategy.

## How to Run
1. Install requirements: `pip install ccxt vectorbt TA-Lib scipy`
2. Run the strategy comparison:
```bash
python week_10/daysixtynine/day_sixtynine.py --strategy all
```

## Reflection
Crypto is a highly inefficient market, which provides opportunities for statistical arbitrage and mean reversion. However, the extreme volatility means that risk management (like the volatility-adjusted stops implemented today) is not optional—it's survival.
