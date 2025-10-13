"""
Day 22 - Flask Fundamentals & Routing
Complete Trading Journal with Crypto Tracker
Date: October 13, 2025
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-2025'

# Sample trading data
SAMPLE_TRADES = [
    {
        'id': 1,
        'symbol': 'AAPL',
        'quantity': 100,
        'entry_price': 150.75,
        'current_price': 155.20,
        'profit_loss': 445.00,
        'entry_date': '2025-10-10',
        'status': 'Active'
    },
    {
        'id': 2,
        'symbol': 'GOOGL',
        'quantity': 50,
        'entry_price': 2750.00,
        'current_price': 2800.50,
        'profit_loss': 2525.00,
        'entry_date': '2025-10-08',
        'status': 'Active'
    },
    {
        'id': 3,
        'symbol': 'MSFT',
        'quantity': 75,
        'entry_price': 330.25,
        'current_price': 325.80,
        'profit_loss': -333.75,
        'entry_date': '2025-10-05',
        'status': 'Active'
    }
]


def get_crypto_prices():
    """Fetch current cryptocurrency prices from CoinGecko API"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum,cardano,solana,ripple',
            'order': 'market_cap_desc',
            'per_page': 5,
            'page': 1,
            'sparkline': False
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        crypto_data = response.json()
        formatted_data = []
        for crypto in crypto_data:
            formatted_data.append({
                'name': crypto['name'],
                'symbol': crypto['symbol'].upper(),
                'current_price': crypto['current_price'],
                'price_change_24h': crypto['price_change_24h'],
                'price_change_percentage_24h': crypto['price_change_percentage_24h'],
                'market_cap': crypto['market_cap']
            })

        return formatted_data

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return get_sample_crypto_data()


def get_sample_crypto_data():
    """Return sample data when API is unavailable"""
    return [
        {
            'name': 'Bitcoin',
            'symbol': 'BTC',
            'current_price': 34567.89,
            'price_change_24h': 1234.56,
            'price_change_percentage_24h': 3.45,
            'market_cap': 675000000000
        },
        {
            'name': 'Ethereum',
            'symbol': 'ETH',
            'current_price': 2345.67,
            'price_change_24h': 89.12,
            'price_change_percentage_24h': 2.15,
            'market_cap': 282000000000
        },
        {
            'name': 'Cardano',
            'symbol': 'ADA',
            'current_price': 0.45,
            'price_change_24h': 0.02,
            'price_change_percentage_24h': 4.65,
            'market_cap': 16000000000
        }
    ]


def calculate_portfolio_stats():
    """Calculate portfolio statistics from sample trades"""
    total_value = sum(trade['quantity'] * trade['current_price']
                      for trade in SAMPLE_TRADES)
    total_profit_loss = sum(trade['profit_loss'] for trade in SAMPLE_TRADES)
    active_trades = len(SAMPLE_TRADES)

    return {
        'total_value': total_value,
        'total_profit_loss': total_profit_loss,
        'active_trades': active_trades
    }

# =============================================================================
# MAIN ROUTES
# =============================================================================


@app.route('/')
def home():
    """Home page"""
    return render_template('index.html',
                           title='Trading Dashboard',
                           current_time=datetime.now())


@app.route('/dashboard')
def dashboard():
    """Trading dashboard with portfolio overview"""
    portfolio_stats = calculate_portfolio_stats()

    return render_template('index.html',
                           title='Trading Dashboard',
                           portfolio_value=portfolio_stats['total_value'],
                           daily_change=portfolio_stats['total_profit_loss'],
                           active_trades=portfolio_stats['active_trades'],
                           trades=SAMPLE_TRADES,
                           current_time=datetime.now())


@app.route('/trades')
def trades_list():
    """List all trades"""
    return render_template('trade_details.html',
                           trades=SAMPLE_TRADES,
                           title='All Trades')


@app.route('/trade/<int:trade_id>')
def trade_detail(trade_id):
    """Show individual trade details"""
    trade = next((t for t in SAMPLE_TRADES if t['id'] == trade_id), None)
    if trade:
        return render_template('trade_details.html',
                               trade=trade,
                               title=f'Trade #{trade_id}')
    else:
        flash('Trade not found!', 'danger')
        return redirect(url_for('trades_list'))

# =============================================================================
# CRYPTO ROUTES
# =============================================================================


@app.route('/crypto')
def crypto_home():
    """Crypto tracker home page"""
    return render_template('crypto_prices.html',
                           title='Crypto Tracker',
                           crypto_data=[],
                           show_welcome=True)


@app.route('/crypto/prices')
def crypto_prices():
    """Display current cryptocurrency prices"""
    crypto_data = get_crypto_prices()
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template('crypto_prices.html',
                           crypto_data=crypto_data,
                           last_updated=last_updated,
                           title='Cryptocurrency Prices')


@app.route('/crypto/api/prices')
def crypto_api_prices():
    """JSON API endpoint for crypto prices"""
    crypto_data = get_crypto_prices()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'cryptocurrencies': crypto_data
    })


@app.route('/crypto/<symbol>')
def crypto_detail(symbol):
    """Detail page for a specific cryptocurrency"""
    crypto_data = get_crypto_prices()
    crypto = next(
        (c for c in crypto_data if c['symbol'].lower() == symbol.lower()), None)

    if crypto:
        return render_template('crypto_prices.html',
                               crypto_detail=crypto,
                               title=f'{crypto["name"]} Details')
    else:
        flash(f'Cryptocurrency {symbol.upper()} not found!', 'danger')
        return redirect(url_for('crypto_prices'))

# =============================================================================
# UTILITY ROUTES
# =============================================================================


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form"""
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        email = request.form.get('email', 'Not provided')
        message = request.form.get('message', 'No message')

        # In a real app, you'd save this to a database
        flash(f'Thank you {name}! Your message has been received.', 'success')

        return redirect(url_for('contact'))

    return '''
    <div class="container">
        <h1>Contact Us</h1>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Name:</label>
                <input type="text" name="name" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Email:</label>
                <input type="email" name="email" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Message:</label>
                <textarea name="message" class="form-control" rows="5" required></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Send Message</button>
            <a href="/" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
    '''


@app.route('/api/portfolio')
def api_portfolio():
    """JSON API for portfolio data"""
    portfolio_stats = calculate_portfolio_stats()
    return jsonify({
        'portfolio_value': portfolio_stats['total_value'],
        'total_profit_loss': portfolio_stats['total_profit_loss'],
        'active_trades': portfolio_stats['active_trades'],
        'timestamp': datetime.now().isoformat()
    })

# =============================================================================
# ERROR HANDLERS
# =============================================================================


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html',
                           error_code=404,
                           error_message="The page you're looking for doesn't exist."), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                           error_code=500,
                           error_message="Something went wrong on our end."), 500

# =============================================================================
# APPLICATION START
# =============================================================================


if __name__ == '__main__':
    print("🚀 Starting Flask Trading Journal...")
    print("📊 Dashboard: http://localhost:5000")
    print("💰 Crypto Prices: http://localhost:5000/crypto/prices")
    print("🔧 Debug mode: ON")
    print("⏰ Started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    app.run(debug=True, host='0.0.0.0', port=5000)
