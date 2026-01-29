# Day 73: Unit Testing Trading Strategies

## Objective
Apply comprehensive unit testing to complex trading strategy components and risk management logic.

## Concepts Covered
- **Strategy Logic Validation**: Testing indicator crossovers, signal generation rules, and thresholds.
- **Risk Management Tests**: Verifying position sizing, drawdown limits, and stop-loss calculations.
- **Edge Case Handling**: Testing with NaN values, flat price series, and extreme market moves.
- **Property-Based Testing**: Using `hypothesis` to verify mathematical invariants.

## Code Explanation
The `day_seventythree.py` script includes:
- A `MomentumStrategy` with RSI and MACD logic, fully covered by unit tests.
- A `RiskManager` implementing Kelly Criterion and volatility-based sizing.
- Extensive test cases covering successful execution, invalid inputs, and boundary conditions.

## How to Run
Run the tests using:
```bash
pytest day_seventythree.py -v
```
