# Day 76: Technical Indicators and Signal Logic

## Objective
Implement a professional-grade technical indicator library and a flexible signal generation framework.

## Concepts Covered
- **Indicator Library**: Implementing SMA, EMA, RSI, MACD, and Bollinger Bands from scratch.
- **Signal Generation Framework**: Creating conditional logic using AND/OR operators.
- **Confirmation Filters**: Using volume and volatility to validate trading signals.
- **Position Sizing Models**: Implementing Kelly Criterion and dynamic drawdown-based sizing.

## Code Explanation
The `day_seventysix.py` script features:
- A `TechnicalIndicatorLibrary` with 10+ indicator types.
- A `SignalGenerator` that applies configurable rules and confirmation filters.
- A `MultiIndicatorStrategy` demonstrating how to integrate indicators, signals, and risk management into a single pipeline.

## How to Run
Run the indicator and signal demonstration:
```bash
python day_seventysix.py
```
