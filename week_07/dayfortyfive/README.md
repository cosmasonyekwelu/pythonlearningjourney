# Day 45: Paper Trading API Integration

**Date:** November 5, 2025

## Learning Objective
To integrate with a real-world brokerage API (Alpaca) for paper trading and implement a local trade logging system for auditing.

## Concepts Covered
- **Brokerage APIs**: Authenticating and interacting with the Alpaca Paper Trading environment.
- **Order Execution**: Placing market and limit orders programmatically.
- **Account Management**: Fetching equity, buying power, and current positions.
- **Trade Logging**: Using `sqlite3` to maintain a local record of all trade attempts and fills.
- **Error Handling**: Managing network issues and API rejection codes.

## Code Explanation
The `day_fortyfive.py` script features the `PaperTradingAPI` class:
- **`place_order()`**: Sends a POST request to Alpaca and logs the resulting order ID to the database.
- **`get_trade_history()`**: Queries the local SQLite database to show recent activities.
- **`init_database()`**: Ensures the local `trading_log.db` is set up with the correct schema.
- **`BinanceTestnetAPI`**: A skeleton class showing how the logic would differ for a crypto exchange.

## How to Run
1. Install dependencies: `pip install requests pandas`
2. Obtain an API Key from [Alpaca](https://alpaca.markets/).
3. Update the constants in the script.
4. Run the trading system:
```bash
python week_07/dayfortyfive/day_fortyfive.py
```

## Reflection
Paper trading is the safest way to develop algorithms. By integrating a local database with a remote API, we create a robust system where we can audit our bot's behavior against actual market data without financial risk.
