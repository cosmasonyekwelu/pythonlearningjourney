"""
Python Learning Journey - Day Twenty Eight
Week 4 Summary - Web Frameworks & Backend Development
Date: October 19, 2025
Author: Cosmas Onyekwelu
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with trades
    trades = db.relationship('Trade', backref='user', lazy=True)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    trade_type = db.Column(db.String(4), nullable=False)  # BUY or SELL
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat()
        }


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Flask-Login user loader


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes


@app.route('/')
def index():
    """Home page with market data"""
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with portfolio summary"""
    user_trades = Trade.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', trades=user_trades)


@app.route('/api/crypto-prices')
def get_crypto_prices():
    """API endpoint to fetch cryptocurrency prices"""
    try:
        # Example using CoinGecko API
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd')
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades', methods=['GET', 'POST'])
@login_required
def handle_trades():
    """API endpoint for trade operations"""
    if request.method == 'GET':
        trades = Trade.query.filter_by(user_id=current_user.id).all()
        return jsonify([trade.to_dict() for trade in trades])

    elif request.method == 'POST':
        data = request.get_json()
        new_trade = Trade(
            user_id=current_user.id,
            symbol=data['symbol'],
            trade_type=data['trade_type'],
            quantity=data['quantity'],
            price=data['price']
        )
        db.session.add(new_trade)
        db.session.commit()
        return jsonify(new_trade.to_dict()), 201


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login functionality"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout functionality"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration functionality"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))

    return render_template('register.html')

# Template filters


@app.template_filter('format_currency')
def format_currency(value):
    """Format currency values"""
    return f"${value:,.2f}"


@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime objects"""
    return value.strftime('%Y-%m-%d %H:%M:%S')

# Error handlers


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Initialize database


def init_db():
    """Initialize database with sample data"""
    db.create_all()

    # Create sample user if none exists
    if not User.query.first():
        sample_user = User(username='trader1', email='trader@example.com')
        sample_user.set_password('password123')
        db.session.add(sample_user)
        db.session.commit()

        # Add sample trades
        sample_trades = [
            Trade(user_id=sample_user.id, symbol='BTC',
                  trade_type='BUY', quantity=0.5, price=45000),
            Trade(user_id=sample_user.id, symbol='ETH',
                  trade_type='BUY', quantity=2, price=3000),
            Trade(user_id=sample_user.id, symbol='BTC',
                  trade_type='SELL', quantity=0.1, price=48000)
        ]
        db.session.add_all(sample_trades)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

"""
This comprehensive example demonstrates:
1. Flask application setup and configuration
2. Database modeling with SQLAlchemy
3. User authentication with Flask-Login
4. RESTful API endpoints
5. Template rendering and filters
6. Error handling
7. External API integration
8. Session management

The application provides:
- User registration and login
- Cryptocurrency price tracking
- Trade management
- Portfolio dashboard
- REST API for frontend integration
"""
