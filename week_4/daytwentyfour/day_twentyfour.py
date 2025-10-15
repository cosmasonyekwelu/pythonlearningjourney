"""
Day 24 — Database Design with SQLite, PostgreSQL, MySQL, and MongoDB
Focus: Designing and connecting multi-database systems for scalability
Date: October 15, 2025
"""

# --------------------------------------------------------
# 🧱 IMPORTS AND CONFIGURATION
# --------------------------------------------------------
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# --------------------------------------------------------
# 🎛️ DATABASE CONNECTIONS
# --------------------------------------------------------
# SQLAlchemy - connect to PostgreSQL (replace credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/portfolio_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MongoDB for logging (NoSQL)
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client['portfolio_tracker']
activity_logs = mongo_db['activity_logs']


# --------------------------------------------------------
# 🧩 MODELS (SQLAlchemy ORM)
# --------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)


class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        'Transaction', backref='portfolio', lazy=True)


class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey(
        'portfolios.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey(
        'assets.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # buy or sell
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref='transactions')


# --------------------------------------------------------
# 🔧 ROUTES — CRUD API EXAMPLES
# --------------------------------------------------------

@app.route('/')
def home():
    return jsonify({
        "message": "Day 24 — Portfolio Tracker API",
        "endpoints": ["/users", "/portfolios", "/transactions", "/assets"]
    })


# -------- USERS --------
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    log_action("create_user", f"User {data['username']} created.")
    return jsonify({"message": "User created successfully"}), 201


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])


# -------- ASSETS --------
@app.route('/assets', methods=['POST'])
def create_asset():
    data = request.json
    asset = Asset(name=data['name'], symbol=data['symbol'], type=data['type'])
    db.session.add(asset)
    db.session.commit()

    log_action("create_asset", f"Asset {data['symbol']} added.")
    return jsonify({"message": "Asset added successfully"}), 201


@app.route('/assets', methods=['GET'])
def get_assets():
    assets = Asset.query.all()
    return jsonify([{"id": a.id, "name": a.name, "symbol": a.symbol, "type": a.type} for a in assets])


# -------- PORTFOLIOS --------
@app.route('/portfolios', methods=['POST'])
def create_portfolio():
    data = request.json
    portfolio = Portfolio(
        user_id=data['user_id'], balance=data.get('balance', 0.0))
    db.session.add(portfolio)
    db.session.commit()

    log_action("create_portfolio",
               f"Portfolio created for user {data['user_id']}.")
    return jsonify({"message": "Portfolio created"}), 201


@app.route('/portfolios', methods=['GET'])
def get_portfolios():
    portfolios = Portfolio.query.all()
    return jsonify([
        {"id": p.id, "user_id": p.user_id,
            "balance": p.balance, "created_at": p.created_at}
        for p in portfolios
    ])


# -------- TRANSACTIONS --------
@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.json
    txn = Transaction(
        portfolio_id=data['portfolio_id'],
        asset_id=data['asset_id'],
        type=data['type'],
        amount=data['amount'],
        price=data['price']
    )
    db.session.add(txn)
    db.session.commit()

    log_action("create_transaction",
               f"Transaction {data['type']} recorded for portfolio {data['portfolio_id']}.")
    return jsonify({"message": "Transaction recorded"}), 201


@app.route('/transactions', methods=['GET'])
def get_transactions():
    txns = Transaction.query.all()
    return jsonify([
        {
            "id": t.id,
            "portfolio_id": t.portfolio_id,
            "asset_id": t.asset_id,
            "type": t.type,
            "amount": t.amount,
            "price": t.price,
            "timestamp": t.timestamp
        } for t in txns
    ])


# --------------------------------------------------------
# 🧠 HELPER FUNCTION — MongoDB Logging
# --------------------------------------------------------
def log_action(action, message):
    log_entry = {
        "action": action,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    activity_logs.insert_one(log_entry)
    print(f"[LOG] {action}: {message}")


# --------------------------------------------------------
# 🚀 RUN SERVER
# --------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
