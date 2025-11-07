# Day 48: Portfolio Rebalancing Scripts

## Objective

Automate the rebalancing of your portfolio to maintain optimal diversification and target asset weights, implementing disciplined buy-low/sell-high strategies.

## Features

- **Threshold-Based Rebalancing**: Automatic rebalancing when allocations drift beyond set thresholds
- **Time-Based Rebalancing**: Periodic rebalancing (monthly/quarterly) regardless of drift
- **Trade Calculation**: Precise calculation of buy/sell quantities needed for rebalancing
- **Cost-Aware Optimization**: Commission cost estimation and trade optimization
- **Simulation Mode**: Preview rebalance impact before execution
- **Performance Metrics**: Improvement scoring and allocation deviation analysis

## Core Concepts Demonstrated

- **Target vs Current Allocation**: Calculating portfolio drift and rebalance needs
- **Rebalance Triggers**: Threshold and time-based rebalancing conditions
- **Trade Optimization**: Minimizing transaction costs and market impact
- **Portfolio Analytics**: Allocation analysis and improvement metrics
- **Execution Planning**: Generating actionable, optimized trade lists

## Installation Requirements

```bash
pip install pandas numpy sqlite3
```

## Rebalancing Strategies

- **Threshold-Based**: Rebalance when any holding deviates >5% from target
- **Time-Based**: Rebalance every 30 days regardless of drift
- **Hybrid Approach**: Combine both strategies for optimal results

## Usage

```bash
python day_fortyeight.py
```

## Configuration

- Set target allocations in `target_allocations` dictionary
- Adjust `rebalance_threshold` for sensitivity (default: 5%)
- Modify rebalance frequency in `check_rebalance_conditions()`

## Key Methods

- `generate_rebalance_plan()`: Comprehensive rebalance analysis and planning
- `calculate_rebalance_trades()`: Precise trade quantity calculations
- `simulate_rebalance()`: Preview rebalance impact and costs
- `execute_rebalance()`: Execute the rebalance plan (simulation/real)

## Output Analysis

- Current vs target allocation comparison
- Required trades with quantities and values
- Commission cost estimation
- Expected improvement in allocation accuracy
- Portfolio statistics and metrics
