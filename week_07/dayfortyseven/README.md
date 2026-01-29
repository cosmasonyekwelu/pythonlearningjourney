# Day 47: Risk Management Engine

**Date:** November 7, 2025

## Learning Objective
To implement a proactive risk management system that enforces trading limits and provides real-time protection for a portfolio.

## Concepts Covered
- **Pre-trade Risk Checks**: Validating orders against limits before they are even sent to the broker.
- **Position Sizing**: Calculating the "correct" number of shares based on a target risk per trade.
- **Exposure Limits**: Enforcing maximum concentration levels for individual symbols and entire sectors.
- **Automatic Stop-Losses**: Generating protective orders based on current price action (Fixed stops vs. Trailing stops).
- **Drawdown Protection**: Implementing a "circuit breaker" that halts trading if losses exceed a certain percentage.

## Code Explanation
The `day_fortyseven.py` script implements the `RiskManager`:
- **`pre_trade_risk_check()`**: Checks if a proposed trade violates any limits like max position size or daily loss.
- **`calculate_position_size()`**: Uses a volatility-based approach to determine how many shares to buy given a specific stop-loss.
- **`generate_stop_loss_orders()`**: Scans the portfolio and creates a list of sell orders to protect against downside.
- **`check_sector_exposure()`**: Ensures the portfolio is diversified and not overly concentrated in one area (e.g., Technology).

## How to Run
1. Ensure `trading_system.db` exists (created by Day 46).
2. Run the risk manager demo:
```bash
python week_07/dayfortyseven/day_fortyseven.py
```

## Reflection
Profit is important, but survival is more important. A robust risk management engine ensures that no single bad decision can destroy the entire portfolio.
