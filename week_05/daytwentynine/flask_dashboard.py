"""
Flask Live Dashboard for Real-time Crypto Prices
Web interface with JavaScript auto-refresh
"""

from flask import Flask, render_template, jsonify
import threading
import time
from datetime import datetime
from day_twentynine import BinanceWebSocket, PriceUpdate

app = Flask(__name__)

# Global variables for sharing data between threads
crypto_data = {}
ws_client = None


class DashboardData:
    """Manages data for the Flask dashboard"""

    def __init__(self):
        self.prices = {}
        self.price_history = {}
        self.connection_status = "disconnected"

    def update_price(self, price_update: PriceUpdate):
        """Update price data from WebSocket"""
        symbol = price_update.symbol
        self.prices[symbol] = {
            'price': price_update.price,
            'timestamp': price_update.timestamp,
            'volume': price_update.volume,
            'change': price_update.change,
            'change_percent': price_update.change_percent
        }

        # Initialize history if needed
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        # Add to history
        self.price_history[symbol].append({
            'price': price_update.price,
            'timestamp': price_update.timestamp,
            'time': datetime.fromtimestamp(price_update.timestamp).strftime('%H:%M:%S')
        })

        # Keep only last 50 records
        if len(self.price_history[symbol]) > 50:
            self.price_history[symbol].pop(0)

        # Calculate changes
        if len(self.price_history[symbol]) > 1:
            first_price = self.price_history[symbol][0]['price']
            current_price = price_update.price
            change = current_price - first_price
            change_percent = (change / first_price) * 100

            self.prices[symbol]['change'] = change
            self.prices[symbol]['change_percent'] = change_percent


# Create global data instance
dashboard_data = DashboardData()


def start_websocket():
    """Start WebSocket connection in a separate thread"""
    global ws_client

    symbols = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT",
        "LINKUSDT", "MATICUSDT", "SOLUSDT", "XRPUSDT"
    ]

    def on_price_update(price_update):
        dashboard_data.update_price(price_update)

    ws_client = BinanceWebSocket(symbols, on_price_update)
    ws_client.start()
    dashboard_data.connection_status = "connected"


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/prices')
def get_prices():
    """API endpoint to get current prices"""
    return jsonify({
        'prices': dashboard_data.prices,
        'connection_status': dashboard_data.connection_status,
        'last_update': datetime.now().isoformat()
    })


@app.route('/api/history/<symbol>')
def get_history(symbol):
    """API endpoint to get price history for a symbol"""
    if symbol in dashboard_data.price_history:
        return jsonify(dashboard_data.price_history[symbol])
    return jsonify([])


@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get connection statistics"""
    if ws_client:
        stats = ws_client.get_statistics()
        return jsonify(stats)
    return jsonify({'error': 'WebSocket not connected'})


def start_flask_app():
    """Start Flask application"""
    print("🚀 Starting Flask Live Dashboard...")
    print("📊 Open http://localhost:5000 in your browser")
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    # Start WebSocket in a separate thread
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    # Start Flask app
    start_flask_app()
