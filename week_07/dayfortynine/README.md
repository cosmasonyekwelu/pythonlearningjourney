# Day 49: Weekly Project – Trading Bot Architecture

**Date:** November 9, 2025

## Learning Objective
To integrate all concepts from the "FinTech Architecture" week into a fully-functional, automated trading bot that handles data, strategy, risk, and execution.

## Concepts Covered
- **Modular Bot Architecture**: Decoupling the Data Feed, Strategy, Risk Manager, and OMS.
- **Strategy Implementation**: Building "Moving Average Crossover" and "Mean Reversion" signals.
- **Graceful Shutdown**: Using the `signal` module to handle `Ctrl+C` correctly and save data before exiting.
- **Event-Loop Design**: Implementing a continuous polling loop that runs the bot's logic at regular intervals.
- **Reporting & Persistence**: Automatically saving equity curves, trades, and orders to CSV files.

## Code Explanation
The `day_fortynine.py` script is the orchestrator for the entire trading system:
- **`DataFeed`**: Fetches price data either via a live exchange (using CCXT) or from a local CSV file.
- **`Strategy`**: Analyzes the historical data to generate "buy" or "sell" signals.
- **`PaperBroker`**: A simulated environment that fills orders with realistic slippage.
- **`TradingBot`**: The main class that runs the `run_once()` loop, checking rules and triggering actions.
- **`RiskManager`**: Ensures every trade is appropriately sized and stops trading if drawdown gets too high.

## How to Run
1. Install requirements: `pip install pandas numpy ccxt` (ccxt is optional).
2. Ensure `sample_data.csv` is present in the directory.
3. Start the bot:
```bash
python week_07/dayfortynine/day_fortynine.py
```
4. Watch the `logs/` directory for real-time activity and the root directory for generated CSV reports.

## Reflection
This project brings together everything from web scraping and database management to risk engineering and multi-threading. It demonstrates the complexity and rigor required to build a system that can operate autonomously in the financial markets.
