# Day 65: Crypto APIs & Data Feeds

**Date:** November 25, 2025

## Learning Objective
To master real-time cryptocurrency data acquisition using REST APIs, WebSockets, and on-chain analysis techniques.

## Concepts Covered
- **Multi-Exchange Aggregation**: Using the `ccxt` library to fetch unified data from Binance, Coinbase, and Kraken.
- **WebSocket Streaming**: Implementing asynchronous listeners for live ticker updates.
- **Arbitrage Detection**: Identifying price discrepancies between different exchanges in real-time.
- **On-Chain Analysis**: Calculating network metrics like "Whale Movements" and exchange flows.
- **Order Book Analysis**: Evaluating market depth and bid-ask spreads.

## Code Explanation
The `day_sixtyfive.py` script provides a toolkit for market data:
- **`ExchangeDataManager`**: Fetches OHLCV and order book data across multiple venues.
- **`WebSocketManager`**: Uses `websockets` and `asyncio` to maintain persistent connections to live price streams.
- **`OnChainAnalyzer`**: A conceptual class showing how to detect large transactions on the Ethereum network.
- **`DataVisualizer`**: Uses Matplotlib to compare prices and volatility across different exchanges.

## How to Run
1. Install requirements: `pip install ccxt websockets pandas matplotlib`
2. Run the historical analysis:
```bash
python week_10/daysixtyfive/day_sixtyfive.py --fetch_historical
```
3. Run the live ticker stream (requires internet):
```bash
python week_10/daysixtyfive/day_sixtyfive.py --real_time
```

## Reflection
Crypto markets never sleep. Relying only on REST APIs is insufficient for high-frequency trading; WebSockets are essential for capturing the micro-movements that occur between poll intervals.
