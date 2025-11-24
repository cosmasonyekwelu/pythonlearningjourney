"""
CoinGecko API Example
Simple demonstration of the free CoinGecko API
"""

import time
from day_twentynine import CoinGeckoAPI, RealTimeData


def simple_price_handler(update):
    """Simple callback for price updates"""
    change = update.change_24h or 0
    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
    print(f"{update.symbol}: ${update.price:.2f} ({change_str})")


def main():
    print("CoinGecko API Example")
    print("Free cryptocurrency data with no API key required!")
    print("=" * 50)

    # Test basic API functionality
    api = CoinGeckoAPI()

    # Get BTC price
    print("\n📊 Testing single coin price:")
    btc_data = api.get_price(['bitcoin'])
    if btc_data:
        btc_price = btc_data['bitcoin']['usd']
        print(f"Bitcoin: ${btc_price:,.2f}")

    # Test real-time updates
    print("\n🔄 Starting real-time updates (30 seconds):")
    coin_ids = ['bitcoin', 'ethereum', 'cardano']

    data_provider = RealTimeData(
        coin_ids, simple_price_handler, update_interval=5)
    data_provider.start()

    try:
        # Run for 30 seconds
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        data_provider.stop()

    print("\n✅ CoinGecko API test completed!")


if __name__ == "__main__":
    main()
