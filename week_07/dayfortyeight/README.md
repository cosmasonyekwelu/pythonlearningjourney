# Day 48: Portfolio Rebalancing System

**Date:** November 8, 2025

## Learning Objective
To build a system that maintains a target asset allocation by automatically identifying and planning rebalance trades.

## Concepts Covered
- **Asset Allocation**: Defining target weights for various stocks and cash.
- **Drift Detection**: Identifying when market movements have pushed a portfolio away from its intended target.
- **Rebalance Planning**: Calculating the precise number of shares to buy or sell to restore the balance.
- **Threshold-based Execution**: Only triggering trades if the deviation exceeds a certain limit (e.g., 5%).
- **Simulation**: Modeling the effects of a rebalance (including commissions) before executing the trades.

## Code Explanation
The `day_fortyeight.py` script implements the `PortfolioRebalancer`:
- **`calculate_current_allocations()`**: Computes the percentage of the portfolio currently held in each asset.
- **`calculate_rebalance_trades()`**: Generates a list of suggested trades to bring the portfolio back to target weights.
- **`simulate_rebalance()`**: Estimates the "improvement score" (how much closer the portfolio gets to the target) and the cost of commissions.
- **`check_rebalance_conditions()`**: Decides if a rebalance is actually necessary based on time or deviation thresholds.

## How to Run
1. Run the rebalancer:
```bash
python week_07/dayfortyeight/day_fortyeight.py
```

## Reflection
Portfolios naturally drift over time as some assets outperform others. Regular rebalancing forces you to "buy low and sell high," maintaining your desired risk profile without constant manual intervention.
