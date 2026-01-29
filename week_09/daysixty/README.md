# Day 60: Reinforcement Learning (RL) Basics

**Date:** November 20, 2025

## Learning Objective
To understand the fundamentals of Reinforcement Learning and build a custom OpenAI Gym environment for an agent to learn how to trade.

## Concepts Covered
- **The RL Framework**: Agent, Environment, States, Actions, and Rewards.
- **Gym Environments**: Implementing the `reset()` and `step()` API for time-series data.
- **Q-Learning**: Understanding the Bellman equation and Tabular Q-tables.
- **Deep Q-Networks (DQN)**: Using neural networks to approximate the Q-function for high-dimensional state spaces.
- **Experience Replay**: Storing past transitions to break correlation in training data.

## Code Explanation
The `day_sixty.py` script features a complete RL implementation:
- **`TradingEnvironment`**: A custom class where the agent can choose to BUY (2), SELL (0), or HOLD (1). It handles transaction costs and tracks portfolio value.
- **`DQNAgent`**: A PyTorch-based agent that uses epsilon-greedy exploration to discover profitable strategies.
- **`TabularQLearningAgent`**: A baseline agent that discretizes the market into bins to learn a simple lookup table.
- **Evaluation**: Compares the trained agent against a simple "Buy and Hold" benchmark.

## How to Run
1. Install requirements: `pip install torch gym numpy pandas yfinance matplotlib stable-baselines3`
2. Run the RL training:
```bash
python week_09/daysixty/day_sixty.py --symbol AAPL --episodes 500
```

## Reflection
Reinforcement Learning is unique because the agent doesn't just predict the future; it learns how its own actions (buying/selling) impact its long-term reward. This mimics the actual challenge of a live trader.
