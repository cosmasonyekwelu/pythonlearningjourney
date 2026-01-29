# Day 71: Testing Frameworks Overview

## Objective
Establish a foundational testing architecture for algorithmic trading systems, including unit testing, parameterized testing, and fixtures.

## Concepts Covered
- **Unit Tests**: Validating isolated logic (indicators, signals, sizing).
- **Parameterized Tests**: Improving coverage across multiple scenarios and edge cases.
- **Fixtures**: Creating reusable, reproducible datasets for tests.
- **Mocking**: Simulating exchange APIs and external dependencies without network calls.

## Code Explanation
The `day_seventyone.py` script implements a modular testing suite using `pytest`. It covers:
- Calculation validation for Simple Moving Average (SMA).
- Robustness checks for `TradeSignal` objects.
- Risk validation for position sizing models.
- A mock exchange integration to test order execution logic in isolation.

## How to Run
Run the tests using:
```bash
pytest day_seventyone.py -v
```
