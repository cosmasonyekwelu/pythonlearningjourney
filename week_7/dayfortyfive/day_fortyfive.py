import requests
import json
import hmac
import hashlib
import time
import pandas as pd
from datetime import datetime
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PaperTradingAPI:
    def __init__(self, base_url, api_key, secret_key):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.headers.update({
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key
        })

        # Initialize database
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for trade logging"""
        self.conn = sqlite3.connect('trading_log.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                order_type TEXT NOT NULL,
                price REAL,
                status TEXT NOT NULL,
                order_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_account_info(self):
        """Get account information"""
        try:
            response = self.session.get(f"{self.base_url}/v2/account")
            response.raise_for_status()
            account_data = response.json()

            logging.info(
                f"Account equity: ${float(account_data['equity']):.2f}")
            return account_data

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching account info: {str(e)}")
            return None

    def get_market_data(self, symbol):
        """Get latest market data for a symbol"""
        try:
            # For Alpaca, you might use different endpoints for real-time data
            # This is a simplified version
            response = self.session.get(f"{self.base_url}/v2/assets/{symbol}")
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Could not fetch data for {symbol}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching market data: {str(e)}")
            return None

    def place_order(self, symbol, qty, side, order_type, limit_price=None):
        """Place a new order"""
        try:
            order_data = {
                'symbol': symbol,
                'qty': str(qty),
                'side': side,  # 'buy' or 'sell'
                'type': order_type,  # 'market', 'limit', etc.
                'time_in_force': 'day'
            }

            if order_type == 'limit' and limit_price:
                order_data['limit_price'] = str(limit_price)

            response = self.session.post(
                f"{self.base_url}/v2/orders", json=order_data)
            response.raise_for_status()
            order_result = response.json()

            # Log trade to database
            self.log_trade(
                symbol=symbol,
                side=side,
                quantity=qty,
                order_type=order_type,
                price=limit_price,
                status=order_result['status'],
                order_id=order_result['id']
            )

            logging.info(
                f"Order placed: {side} {qty} {symbol} at ${limit_price if limit_price else 'market'}")
            return order_result

        except requests.exceptions.RequestException as e:
            logging.error(f"Error placing order: {str(e)}")
            return None

    def get_order_status(self, order_id):
        """Check order status"""
        try:
            response = self.session.get(
                f"{self.base_url}/v2/orders/{order_id}")
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching order status: {str(e)}")
            return None

    def cancel_order(self, order_id):
        """Cancel an open order"""
        try:
            response = self.session.delete(
                f"{self.base_url}/v2/orders/{order_id}")
            if response.status_code == 204:
                logging.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                logging.warning(f"Could not cancel order {order_id}")
                return False

        except requests.exceptions.RequestException as e:
            logging.error(f"Error cancelling order: {str(e)}")
            return False

    def get_positions(self):
        """Get current positions"""
        try:
            response = self.session.get(f"{self.base_url}/v2/positions")
            response.raise_for_status()
            positions = response.json()

            logging.info(f"Found {len(positions)} open positions")
            return positions

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching positions: {str(e)}")
            return []

    def log_trade(self, symbol, side, quantity, order_type, price, status, order_id):
        """Log trade to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, order_type, price, status, order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, side, quantity, order_type, price, status, order_id))
        self.conn.commit()

    def get_trade_history(self):
        """Retrieve trade history from database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10
        ''')
        return cursor.fetchall()


class BinanceTestnetAPI:
    """Alternative implementation for Binance Testnet"""

    def __init__(self, api_key, secret_key):
        self.base_url = "https://testnet.binance.vision/api"
        self.api_key = api_key
        self.secret_key = secret_key

    def _sign_request(self, data):
        """Sign request for Binance API"""
        query_string = '&'.join(
            [f"{key}={value}" for key, value in data.items()])
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()


def main():
    # Configuration - Replace with your actual paper trading credentials
    # Alpaca Paper Trading (recommended for stocks)
    ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
    ALPACA_API_KEY = "your_alpaca_api_key_here"
    ALPACA_SECRET_KEY = "your_alpaca_secret_key_here"

    # Initialize trading API
    trader = PaperTradingAPI(
        ALPACA_BASE_URL, ALPACA_API_KEY, ALPACA_SECRET_KEY)

    print("🔍 Fetching Account Information...")
    account_info = trader.get_account_info()
    if account_info:
        print(f"Account Number: {account_info.get('account_number', 'N/A')}")
        print(f"Equity: ${float(account_info.get('equity', 0)):.2f}")
        print(
            f"Buying Power: ${float(account_info.get('buying_power', 0)):.2f}")

    print("\n📊 Checking Open Positions...")
    positions = trader.get_positions()
    if positions:
        for position in positions[:3]:  # Show first 3 positions
            print(
                f"Symbol: {position['symbol']}, Qty: {position['qty']}, Market Value: ${position['market_value']}")
    else:
        print("No open positions found")

    # Example: Place a paper trade (commented out for safety)
    # Uncomment and modify to actually place trades
    """
    print("\n🔄 Placing Paper Trade...")
    order_result = trader.place_order(
        symbol="AAPL",
        qty=1,
        side="buy",
        order_type="market"
    )
    
    if order_result:
        print(f"Order ID: {order_result['id']}")
        print(f"Status: {order_result['status']}")
        
        # Check order status after a delay
        time.sleep(2)
        order_status = trader.get_order_status(order_result['id'])
        print(f"Updated Status: {order_status['status'] if order_status else 'Unknown'}")
    """

    print("\n📋 Recent Trade History:")
    trade_history = trader.get_trade_history()
    if trade_history:
        for trade in trade_history:
            print(
                f"ID: {trade[0]}, Symbol: {trade[1]}, Side: {trade[2]}, Qty: {trade[3]}, Status: {trade[6]}")
    else:
        print("No trade history found")

    # Close database connection
    trader.conn.close()


if __name__ == "__main__":
    main()
