"""
Live Cryptocurrency Price Tracker
Mini Project for Day 29 - Updates every 5 seconds
"""

import time
import threading
from datetime import datetime
from typing import Dict, List
import pandas as pd
from day_twentynine import BinanceWebSocket, PriceUpdate


class CryptoTracker:
    """
    Live cryptocurrency price tracker that updates every 5 seconds
    with additional features like price alerts and data logging
    """

    def __init__(self, symbols: List[str], update_interval: int = 5):
        self.symbols = symbols
        self.update_interval = update_interval
        self.price_data: Dict[str, List] = {symbol: [] for symbol in symbols}
        self.alerts: Dict[str, float] = {}
        self.is_running = False

        # Create WebSocket client
        self.ws_client = BinanceWebSocket(symbols, self._on_price_update)

    def _on_price_update(self, price_update: PriceUpdate):
        """Handle price updates from WebSocket"""
        symbol = price_update.symbol
        price = price_update.price
        timestamp = datetime.now()

        # Store price data
        self.price_data[symbol].append({
            'timestamp': timestamp,
            'price': price
        })

        # Keep only last 100 records per symbol
        if len(self.price_data[symbol]) > 100:
            self.price_data[symbol].pop(0)

        # Check alerts
        self._check_alerts(symbol, price)

    def _check_alerts(self, symbol: str, price: float):
        """Check if price triggers any alerts"""
        if symbol in self.alerts:
            target_price = self.alerts[symbol]
            if price >= target_price:
                print(f"🚨 ALERT: {symbol} reached target price: ${price:.4f}")
                # Remove alert after triggering
                del self.alerts[symbol]

    def set_alert(self, symbol: str, target_price: float):
        """Set price alert for a symbol"""
        self.alerts[symbol] = target_price
        print(f"Alert set: {symbol} at ${target_price:.4f}")

    def display_prices(self):
        """Display current prices in a formatted table"""
        print("\n" + "="*60)
        print(
            f"CRYPTO PRICE TRACKER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        headers = ["Symbol", "Price (USDT)", "Change (5m)", "Volume", "Status"]
        print(
            f"{headers[0]:<10} {headers[1]:<15} {headers[2]:<12} {headers[3]:<12} {headers[4]}")
        print("-" * 60)

        for symbol in self.symbols:
            prices = self.price_data.get(symbol, [])
            if len(prices) >= 2:
                current_price = prices[-1]['price']
                # Calculate 5-minute change if we have enough data
                if len(prices) >= 6:  # Assuming ~1 update per second
                    old_price = prices[-6]['price']
                    change = ((current_price - old_price) / old_price) * 100
                    change_str = f"{change:+.2f}%"
                    status = "📈" if change >= 0 else "📉"
                else:
                    change_str = "N/A"
                    status = "➡️"

                # Get approximate volume (from recent trades)
                volume = "N/A"  # Would need additional WebSocket for proper volume

                # Color coding for changes
                if change_str != "N/A":
                    change_val = float(change_str.strip('%+'))
                    if change_val > 0:
                        change_str = f"\033[92m{change_str}\033[0m"
                    elif change_val < 0:
                        change_str = f"\033[91m{change_str}\033[0m"

                print(
                    f"{symbol:<10} ${current_price:<14.4f} {change_str:<12} {volume:<12} {status}")
            else:
                print(f"{symbol:<10} {'Loading...':<15} {'N/A':<12} {'N/A':<12} ⏳")

    def start_tracking(self):
        """Start the price tracker"""
        print("🚀 Starting Live Cryptocurrency Price Tracker")
        print(f"📊 Tracking: {', '.join(self.symbols)}")
        print(f"⏰ Update interval: {self.update_interval} seconds")
        print("Press Ctrl+C to stop\n")

        self.is_running = True
        self.ws_client.start()

        try:
            # Main display loop
            while self.is_running:
                time.sleep(self.update_interval)
                self.display_prices()

        except KeyboardInterrupt:
            self.stop_tracking()

    def stop_tracking(self):
        """Stop the price tracker"""
        print("\n🛑 Stopping price tracker...")
        self.is_running = False
        self.ws_client.stop()

    def get_price_history(self, symbol: str) -> pd.DataFrame:
        """Get price history as DataFrame for analysis"""
        if symbol in self.price_data:
            return pd.DataFrame(self.price_data[symbol])
        return pd.DataFrame()


def main():
    """Main function for cryptocurrency price tracker"""

    # Popular cryptocurrency pairs
    symbols = [
        "BTCUSDT",  # Bitcoin
        "ETHUSDT",  # Ethereum
        "ADAUSDT",  # Cardano
        "DOTUSDT",  # Polkadot
        "LINKUSDT",  # Chainlink
        "MATICUSDT",  # Polygon
        "SOLUSDT",  # Solana
        "XRPUSDT",  # Ripple
    ]

    # Create and start tracker
    tracker = CryptoTracker(symbols, update_interval=5)

    # Set some example alerts (you can modify these)
    tracker.set_alert("BTCUSDT", 45000.00)  # Alert if BTC reaches $45,000
    tracker.set_alert("ETHUSDT", 3000.00)   # Alert if ETH reaches $3,000

    # Start tracking
    tracker.start_tracking()


if __name__ == "__main__":
    main()
