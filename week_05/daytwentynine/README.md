# Day 29: Real-time Data & API Comparison

**Date:** October 20, 2025

## Learning Objective
To understand how to fetch real-time financial data from multiple sources (Yahoo Finance and CoinGecko), handle rate limits, and compare data consistency across different APIs.

## Concepts Covered
- **Multi-API Integration**: Using both `yfinance` and RESTful APIs (`CoinGecko`) in a single application.
- **Rate Limiting**: Implementing logic to respect API provider constraints and avoid 429 errors.
- **Data Comparison**: Analyzing price discrepancies between different market data providers.
- **Multi-threading**: Using `threading` to run a non-blocking background data poller.
- **Enumerations & Dataclasses**: Using `Enum` and `dataclass` for cleaner, type-safe code.

## Code Explanation
The `day_twentynine.py` script implements a robust price tracker:
- **`DualAPIProvider`**: Encapsulates the logic for fetching from both sources. It maps ticker symbols (like BTC) to CoinGecko IDs (like bitcoin).
- **`RealTimeData`**: Manages a background thread that periodically polls for updates and stores a short history of prices.
- **`PriceMonitor`**: A callback-based system to handle data as it arrives.
- **Comparison Table**: Generates a CLI report showing the percentage difference between Yahoo and CoinGecko prices.

## How to Run
1. Install dependencies: `pip install requests yfinance`
2. Run the tracker:
```bash
python week_05/daytwentynine/day_twentynine.py
```

## Reflection
No single API is perfect. Real-time systems often require data redundancy. Building a comparison tool helps identify which source is more reliable or faster for specific assets.
