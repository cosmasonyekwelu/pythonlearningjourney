# Day 61: Reward System Design for RL

**Date:** November 21, 2025

## Learning Objective
To design sophisticated reward functions that go beyond simple returns, incorporating risk management and market volatility into the agent's learning process.

## Concepts Covered
- **Reward Shaping**: Designing the "objective function" to guide the agent toward desired behaviors.
- **Risk-Adjusted Rewards**: Incorporating the Sharpe and Sortino Ratios into the reward signal.
- **Drawdown Penalties**: Explicitly punishing large percentage drops in the portfolio value.
- **Adaptive Rewards**: Adjusting the agent's risk aversion based on real-time market volatility.
- **Transaction Cost Awareness**: Ensuring the reward accounts for the negative impact of over-trading.

## Code Explanation
The `day_sixtyone.py` script implements a `RewardSystem` factory:
- **`sharpe_ratio_reward()`**: Rewards the agent for high returns relative to the standard deviation of those returns.
- **`calmar_ratio_reward()`**: Focuses on maximizing returns while minimizing the maximum drawdown.
- **`risk_adjusted_reward()`**: A multi-factor signal that combines volatility penalties with raw performance.
- **`RewardComparator`**: A backtesting tool that runs the same strategy across 6 different reward functions to visualize how they influence agent behavior.

## How to Run
1. Run the comparator:
```bash
python week_09/daysixtyone/day_sixtyone.py --symbol AAPL
```

## Reflection
The reward function is the "personality" of the AI. A simple return reward produces an aggressive, high-risk agent, while a Sharpe-based reward produces a more conservative, consistent agent.
