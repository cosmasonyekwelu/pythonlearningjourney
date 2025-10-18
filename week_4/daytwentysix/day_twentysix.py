"""
Day 26 - API Development (REST, etc.)
Trading API with Flask and SQLAlchemy
Date: October 17, 2025
"""

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app)
CORS(app)  # Enable CORS for all routes

# Database Models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trades = db.relationship('Trade', backref='user',
                             lazy=True, cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    trade_type = db.Column(db.String(4), nullable=False)  # BUY/SELL
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'trade_type': self.trade_type,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id
        }

# Authentication Resources


class RegisterAPI(Resource):
    def post(self):
        try:
            data = request.get_json()

            # Validation
            required_fields = ['username', 'email', 'password']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields: username, email, password'}, 400

            # Check if user already exists
            if User.query.filter_by(username=data['username']).first():
                return {'error': 'Username already exists'}, 400

            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already exists'}, 400

            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password']  # In production, hash this password!
            )

            db.session.add(user)
            db.session.commit()

            # Create access token
            access_token = create_access_token(identity=user.id)

            return {
                'message': 'User created successfully',
                'user': user.serialize(),
                'access_token': access_token
            }, 201

        except Exception as e:
            return {'error': str(e)}, 500


class LoginAPI(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data or 'username' not in data or 'password' not in data:
                return {'error': 'Username and password required'}, 400

            user = User.query.filter_by(username=data['username']).first()

            # In production, use proper password hashing!
            if user and user.password == data['password']:
                access_token = create_access_token(identity=user.id)
                return {
                    'message': 'Login successful',
                    'user': user.serialize(),
                    'access_token': access_token
                }, 200

            return {'error': 'Invalid username or password'}, 401

        except Exception as e:
            return {'error': str(e)}, 500

# Trade API with CRUD operations, pagination, and filtering


class TradeAPI(Resource):
    @jwt_required()
    def get(self, trade_id=None):
        try:
            current_user_id = get_jwt_identity()

            if trade_id:
                # Get single trade
                trade = Trade.query.filter_by(
                    id=trade_id, user_id=current_user_id).first()
                if trade:
                    return trade.serialize()
                return {'error': 'Trade not found'}, 404

            # Get all trades with pagination and filtering
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            symbol = request.args.get('symbol')
            trade_type = request.args.get('trade_type')

            # Build query
            query = Trade.query.filter_by(user_id=current_user_id)

            if symbol:
                query = query.filter(Trade.symbol.ilike(f'%{symbol}%'))
            if trade_type:
                query = query.filter(Trade.trade_type == trade_type.upper())

            # Pagination
            trades = query.order_by(Trade.timestamp.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return {
                'trades': [t.serialize() for t in trades.items],
                'total': trades.total,
                'pages': trades.pages,
                'current_page': page,
                'per_page': per_page
            }

        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # Data validation
            required_fields = ['symbol', 'quantity', 'price', 'trade_type']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields: symbol, quantity, price, trade_type'}, 400

            if data['trade_type'].upper() not in ['BUY', 'SELL']:
                return {'error': 'Trade type must be BUY or SELL'}, 400

            if data['quantity'] <= 0:
                return {'error': 'Quantity must be positive'}, 400

            if data['price'] <= 0:
                return {'error': 'Price must be positive'}, 400

            # Create trade
            trade = Trade(
                symbol=data['symbol'].upper(),
                quantity=data['quantity'],
                price=data['price'],
                trade_type=data['trade_type'].upper(),
                user_id=current_user_id
            )

            db.session.add(trade)
            db.session.commit()

            return trade.serialize(), 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    def put(self, trade_id):
        try:
            current_user_id = get_jwt_identity()
            trade = Trade.query.filter_by(
                id=trade_id, user_id=current_user_id).first()

            if not trade:
                return {'error': 'Trade not found'}, 404

            data = request.get_json()

            # Update allowed fields
            allowed_fields = ['symbol', 'quantity', 'price', 'trade_type']
            for field in allowed_fields:
                if field in data:
                    if field == 'trade_type' and data[field].upper() not in ['BUY', 'SELL']:
                        return {'error': 'Trade type must be BUY or SELL'}, 400
                    if field in ['quantity', 'price'] and data[field] <= 0:
                        return {'error': f'{field} must be positive'}, 400

                    setattr(trade, field, data[field].upper() if field in [
                            'symbol', 'trade_type'] else data[field])

            db.session.commit()
            return trade.serialize()

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    def delete(self, trade_id):
        try:
            current_user_id = get_jwt_identity()
            trade = Trade.query.filter_by(
                id=trade_id, user_id=current_user_id).first()

            if not trade:
                return {'error': 'Trade not found'}, 404

            db.session.delete(trade)
            db.session.commit()

            return {'message': 'Trade deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

# Portfolio API


class PortfolioAPI(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            trades = Trade.query.filter_by(user_id=current_user_id).all()

            portfolio = {}
            total_value = 0
            total_invested = 0

            for trade in trades:
                if trade.symbol not in portfolio:
                    portfolio[trade.symbol] = {
                        'quantity': 0,
                        'total_invested': 0,
                        'average_price': 0,
                        'current_value': 0
                    }

                if trade.trade_type == 'BUY':
                    portfolio[trade.symbol]['quantity'] += trade.quantity
                    portfolio[trade.symbol]['total_invested'] += trade.quantity * trade.price
                else:  # SELL
                    portfolio[trade.symbol]['quantity'] -= trade.quantity
                    portfolio[trade.symbol]['total_invested'] -= trade.quantity * trade.price

            # Calculate averages and current values (using mock current prices)
            for symbol, data in portfolio.items():
                if data['quantity'] > 0:
                    data['average_price'] = data['total_invested'] / \
                        data['quantity']
                    # Mock current price (in real app, fetch from market data API)
                    current_price = data['average_price'] * \
                        (1 + (hash(symbol) % 20 - 10) / 100)
                    data['current_price'] = round(current_price, 2)
                    data['current_value'] = data['quantity'] * \
                        data['current_price']
                    data['pnl'] = data['current_value'] - \
                        data['total_invested']
                    data['pnl_percent'] = (
                        data['pnl'] / data['total_invested']) * 100 if data['total_invested'] > 0 else 0

                    total_value += data['current_value']
                    total_invested += data['total_invested']
                else:
                    # Remove symbols with zero quantity
                    portfolio[symbol] = None

            # Clean up portfolio
            portfolio = {k: v for k, v in portfolio.items() if v is not None}

            return {
                'portfolio': portfolio,
                'summary': {
                    'total_value': round(total_value, 2),
                    'total_invested': round(total_invested, 2),
                    'total_pnl': round(total_value - total_invested, 2),
                    'total_pnl_percent': round(((total_value - total_invested) / total_invested * 100), 2) if total_invested > 0 else 0
                }
            }

        except Exception as e:
            return {'error': str(e)}, 500

# Market Data API


class MarketDataAPI(Resource):
    def get(self):
        try:
            symbols = request.args.get(
                'symbols', 'AAPL,GOOGL,MSFT,TSLA,AMZN').split(',')

            market_data = {}
            for symbol in symbols:
                symbol = symbol.strip().upper()
                if symbol:
                    # Generate mock market data
                    base_price = 50 + (hash(symbol) % 500)
                    change = (hash(symbol + str(datetime.now().hour)) %
                              40 - 20) / 2
                    change_percent = (change / base_price) * 100

                    market_data[symbol] = {
                        'symbol': symbol,
                        'price': round(base_price + change, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'volume': (hash(symbol) % 10000000) + 1000000,
                        'last_updated': datetime.utcnow().isoformat()
                    }

            return market_data

        except Exception as e:
            return {'error': str(e)}, 500

# Health Check


class HealthAPI(Resource):
    def get(self):
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db.engine.connect() else 'disconnected'
        }


# Register API routes
api.add_resource(RegisterAPI, '/api/register')
api.add_resource(LoginAPI, '/api/login')
api.add_resource(TradeAPI, '/api/trades', '/api/trades/<int:trade_id>')
api.add_resource(PortfolioAPI, '/api/portfolio')
api.add_resource(MarketDataAPI, '/api/market-data')
api.add_resource(HealthAPI, '/api/health')

# CLI commands for setup


@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
    print('Database initialized successfully!')


@app.cli.command('create-sample-data')
def create_sample_data():
    """Create sample data for testing."""
    with app.app_context():
        # Create sample user
        user = User.query.filter_by(username='demo').first()
        if not user:
            user = User(username='demo', email='demo@example.com',
                        password='password')
            db.session.add(user)
            db.session.commit()
            print('Created demo user: demo/password')

        # Create sample trades
        sample_trades = [
            {'symbol': 'AAPL', 'quantity': 10, 'price': 150.50, 'trade_type': 'BUY'},
            {'symbol': 'GOOGL', 'quantity': 5,
                'price': 2750.00, 'trade_type': 'BUY'},
            {'symbol': 'MSFT', 'quantity': 15, 'price': 305.75, 'trade_type': 'BUY'},
            {'symbol': 'TSLA', 'quantity': 8, 'price': 220.00, 'trade_type': 'BUY'},
            {'symbol': 'AAPL', 'quantity': 3, 'price': 155.00, 'trade_type': 'SELL'},
        ]

        for trade_data in sample_trades:
            trade = Trade(**trade_data, user_id=user.id)
            db.session.add(trade)

        db.session.commit()
        print('Created sample trades')


if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()

    print("Trading API Server Starting...")
    print("Available endpoints:")
    print("  GET    /api/health")
    print("  POST   /api/register")
    print("  POST   /api/login")
    print("  GET    /api/market-data")
    print("  GET    /api/trades")
    print("  POST   /api/trades")
    print("  GET    /api/trades/<id>")
    print("  PUT    /api/trades/<id>")
    print("  DELETE /api/trades/<id>")
    print("  GET    /api/portfolio")
    print("\nRun with: flask --app day_twentysix run --port 5000 --debug")

    app.run(debug=True, port=5000)
