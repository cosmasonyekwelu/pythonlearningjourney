# Day 62: Strategy Optimization with Advanced RL

**Date:** November 22, 2025

## Learning Objective
To implement state-of-the-art RL algorithms (PPO and SAC) to optimize a multi-asset trading strategy across a portfolio of stocks.

## Concepts Covered
- **Proximal Policy Optimization (PPO)**: A robust on-policy algorithm that balances exploration and exploitation.
- **Soft Actor-Critic (SAC)**: An off-policy algorithm that uses entropy to maximize diversity in explored strategies.
- **Multi-Asset Environments**: Building an environment that manages multiple symbols simultaneously.
- **Continuous Action Spaces**: Allowing the agent to decide exactly *what percentage* of the portfolio to allocate, rather than just Buy/Sell.
- **Vectorized Environments**: Using `stable-baselines3` to train on multiple environment instances at once.

## Code Explanation
The `day_sixtytwo.py` script implement an `AdvancedRLTrader`:
- **`MultiAssetTradingEnvironment`**: Manages a shared cash pool and individual position limits for a basket of stocks.
- **`TrainingProgressCallback`**: A custom monitoring tool that tracks the "Mean Reward" during long training runs.
- **`evaluate_agent()`**: Runs a deterministic backtest using the trained weights to compare performance against an "Equal Weight" benchmark.
- **TensorBoard Integration**: Automatically logs metrics for visualization in the TensorBoard dashboard.

## How to Run
1. Install dependencies: `pip install stable-baselines3 shimmy gym yfinance`
2. Run the optimization:
```bash
python week_09/daysixtytwo/day_sixtytwo.py --symbols AAPL MSFT GOOGL --timesteps 50000
```

## Reflection
Moving from single-stock discrete actions to multi-asset continuous allocation is a significant step up in complexity. Algorithms like PPO are much more stable for financial tasks because they prevent the policy from changing too drastically in a single update.
