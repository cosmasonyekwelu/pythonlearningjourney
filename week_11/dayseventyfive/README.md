# Day 75: Backtesting Framework Setup and Strategy Evaluation

## Objective
Build a robust backtesting foundation supporting both fast vectorized simulation and realistic event-driven execution.

## Concepts Covered
- **Vectorized Backtesting**: Using `numpy`/`pandas` for high-performance exploratory testing.
- **Event-Driven Backtesting**: Simulating market microstructure (slippage, spreads, commissions).
- **Performance Analytics**: Calculating Sharpe, Sortino, max drawdown, and VaR.
- **Benchmarking**: Comparing strategy performance against Buy-and-Hold and indices.

## Code Explanation
The `day_seventyfive.py` script provides:
- A `VectorizedBacktester` for rapid strategy iteration.
- An `EventDrivenBacktester` for high-fidelity execution simulation.
- A comprehensive metrics engine that calculates 15+ key performance indicators.
- Example SMA Crossover and Mean Reversion strategies.

## How to Run
Run the backtesting demonstration:
```bash
python day_seventyfive.py
```
