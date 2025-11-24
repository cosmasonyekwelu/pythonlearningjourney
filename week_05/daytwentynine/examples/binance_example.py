"""
Binance WebSocket Example
Simple implementation for cryptocurrency price streaming
"""

import time
from day_twentynine import BinanceWebSocket


def simple_price_handler(price_update):
    """Simple callback function for price updates"""
    print(f"{price_update.symbol}: ${price_update.price:.4f}")


def main():
    print("Binance WebSocket Example")
    print("Streaming live cryptocurrency prices...")

    # Cryptocurrency pairs to track
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]

    # Create WebSocket client
    ws_client = BinanceWebSocket(symbols, simple_price_handler)

    try:
        # Start connection
        ws_client.start()

        # Let it run for 30 seconds
        print("Streaming for 30 seconds...")
        time.sleep(30)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ws_client.stop()
        print("Disconnected")


if __name__ == "__main__":
    main()
