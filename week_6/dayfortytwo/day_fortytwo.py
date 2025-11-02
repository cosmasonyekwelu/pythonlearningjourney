"""
Python Learning Journey - Day Forty Two
Week 6 Summary - Networking & Security.
Date: November 2, 2025
Author: Cosmas Onyekwelu
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import re
import logging
from cryptography.fernet import Fernet
from functools import wraps
import json

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///portfolio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()


class InputValidator:
    """Input validation and sanitization utilities"""

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit"
        return True, "Password is strong"

    @staticmethod
    def sanitize_string(input_string, max_length=255):
        if not input_string:
            return None
        sanitized = re.sub(r'[<>"\']', '', input_string.strip())
        return sanitized[:max_length]

    @staticmethod
    def validate_symbol(symbol):
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, symbol))

    @staticmethod
    def validate_quantity(quantity):
        try:
            qty = float(quantity)
            return qty > 0
        except (ValueError, TypeError):
            return False


class DataEncryptor:
    """Handle encryption/decryption of sensitive data"""

    def __init__(self, encryption_key):
        self.fernet = Fernet(encryption_key)

    def encrypt_data(self, data):
        if not data:
            return None
        return self.fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        if not encrypted_data:
            return None
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return None


class SecurityHeaders:
    """Manage security headers"""

    @staticmethod
    def set_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp

        return response

# Database Models


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    secrets = db.relationship(
        'UserSecret', backref='user', lazy=True, uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    holdings = db.relationship(
        'Holding', backref='portfolio', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'holdings_count': len(self.holdings)
        }


class Holding(db.Model):
    __tablename__ = 'holdings'

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey(
        'portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_price': self.average_price,
            'current_value': self.quantity * self.average_price,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class UserSecret(db.Model):
    __tablename__ = 'user_secrets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, unique=True)
    encrypted_api_key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }

# JWT Configuration


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)


def audit_log(action, user_id=None, details=None):
    """Log security events"""
    try:
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None

        details_str = json.dumps(details) if details else None

        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details_str
        )

        db.session.add(log_entry)
        db.session.commit()

        logging.info(
            f"Audit Event - Action: {action}, User: {user_id}, IP: {ip_address}")

    except Exception as e:
        logging.error(f"Failed to log audit event: {e}")
        db.session.rollback()


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # Initialize encryptor
    encryptor = DataEncryptor(app.config['ENCRYPTION_KEY'])

    # Security headers
    @app.after_request
    def after_request(response):
        return SecurityHeaders.set_headers(response)

    # Authentication routes
    @app.route('/api/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            email = InputValidator.sanitize_string(data.get('email'))
            password = data.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            if not InputValidator.validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400

            is_valid_pw, pw_message = InputValidator.validate_password(
                password)
            if not is_valid_pw:
                return jsonify({'error': pw_message}), 400

            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'User already exists'}), 409

            user = User(email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            audit_log('registration_success', user.id, {'email': email})

            return jsonify({
                'message': 'User created successfully',
                'user': user.to_dict()
            }), 201

        except Exception as e:
            logging.error(f"Registration error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            email = InputValidator.sanitize_string(data.get('email'))
            password = data.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            user = User.query.filter_by(email=email).first()

            if not user:
                audit_log('login_failed', None, {
                          'reason': 'user_not_found', 'email': email})
                return jsonify({'error': 'Invalid credentials'}), 401

            if not user.check_password(password):
                audit_log('login_failed', user.id, {
                          'reason': 'invalid_password', 'email': email})
                return jsonify({'error': 'Invalid credentials'}), 401

            if not user.is_active:
                audit_log('login_failed', user.id, {
                          'reason': 'account_inactive', 'email': email})
                return jsonify({'error': 'Account is inactive'}), 401

            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            audit_log('login_success', user.id)

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200

        except Exception as e:
            logging.error(f"Login error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.is_active:
                return jsonify({'error': 'Invalid token'}), 401

            new_token = create_access_token(identity=user)

            return jsonify({
                'access_token': new_token
            }), 200

        except Exception as e:
            logging.error(f"Token refresh error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    # Portfolio routes
    @app.route('/api/portfolios', methods=['GET'])
    @jwt_required()
    def get_portfolios():
        try:
            current_user_id = get_jwt_identity()
            portfolios = Portfolio.query.filter_by(
                user_id=current_user_id).all()

            return jsonify({
                'portfolios': [p.to_dict() for p in portfolios]
            }), 200

        except Exception as e:
            logging.error(f"Get portfolios error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/portfolios', methods=['POST'])
    @jwt_required()
    def create_portfolio():
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            name = InputValidator.sanitize_string(data.get('name'))
            description = InputValidator.sanitize_string(
                data.get('description'))

            if not name:
                return jsonify({'error': 'Portfolio name is required'}), 400

            existing = Portfolio.query.filter_by(
                user_id=current_user_id, name=name).first()
            if existing:
                return jsonify({'error': 'Portfolio with this name already exists'}), 409

            portfolio = Portfolio(
                user_id=current_user_id,
                name=name,
                description=description
            )

            db.session.add(portfolio)
            db.session.commit()

            audit_log('portfolio_created', current_user_id, {
                'portfolio_id': portfolio.id,
                'portfolio_name': name
            })

            return jsonify({
                'message': 'Portfolio created successfully',
                'portfolio': portfolio.to_dict()
            }), 201

        except Exception as e:
            logging.error(f"Create portfolio error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/portfolios/<int:portfolio_id>/holdings', methods=['POST'])
    @jwt_required()
    def add_holding(portfolio_id):
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            portfolio = Portfolio.query.filter_by(
                id=portfolio_id, user_id=current_user_id).first()
            if not portfolio:
                return jsonify({'error': 'Portfolio not found'}), 404

            symbol = InputValidator.sanitize_string(data.get('symbol'))
            quantity = data.get('quantity')
            price = data.get('average_price')
            notes = InputValidator.sanitize_string(data.get('notes'))

            if not symbol or not quantity or not price:
                return jsonify({'error': 'Symbol, quantity, and average price are required'}), 400

            if not InputValidator.validate_symbol(symbol):
                return jsonify({'error': 'Invalid symbol format'}), 400

            if not InputValidator.validate_quantity(quantity):
                return jsonify({'error': 'Quantity must be a positive number'}), 400

            if not InputValidator.validate_quantity(price):
                return jsonify({'error': 'Price must be a positive number'}), 400

            trade_value = float(quantity) * float(price)
            is_large_trade = trade_value > 10000

            holding = Holding(
                portfolio_id=portfolio_id,
                symbol=symbol.upper(),
                quantity=float(quantity),
                average_price=float(price),
                notes=notes
            )

            db.session.add(holding)
            db.session.commit()

            action = 'large_trade_added' if is_large_trade else 'trade_added'
            audit_log(action, current_user_id, {
                'portfolio_id': portfolio_id,
                'holding_id': holding.id,
                'symbol': symbol,
                'quantity': quantity,
                'average_price': price,
                'trade_value': trade_value
            })

            return jsonify({
                'message': 'Holding added successfully',
                'holding': holding.to_dict()
            }), 201

        except Exception as e:
            logging.error(f"Add holding error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    # API Key management (encrypted)
    @app.route('/api/user/api-key', methods=['POST'])
    @jwt_required()
    def set_api_key():
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            api_key = data.get('api_key')
            if not api_key:
                return jsonify({'error': 'API key is required'}), 400

            encrypted_key = encryptor.encrypt_data(api_key)

            user_secret = UserSecret.query.filter_by(
                user_id=current_user_id).first()
            if user_secret:
                user_secret.encrypted_api_key = encrypted_key
            else:
                user_secret = UserSecret(
                    user_id=current_user_id,
                    encrypted_api_key=encrypted_key
                )
                db.session.add(user_secret)

            db.session.commit()

            audit_log('api_key_updated', current_user_id)

            return jsonify({'message': 'API key stored successfully'}), 200

        except Exception as e:
            logging.error(f"Set API key error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/user/api-key', methods=['GET'])
    @jwt_required()
    def get_api_key_status():
        try:
            current_user_id = get_jwt_identity()
            user_secret = UserSecret.query.filter_by(
                user_id=current_user_id).first()

            return jsonify({
                'has_api_key': user_secret is not None
            }), 200

        except Exception as e:
            logging.error(f"Get API key status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    # Audit logs
    @app.route('/api/user/audit-logs', methods=['GET'])
    @jwt_required()
    def get_audit_logs():
        try:
            current_user_id = get_jwt_identity()
            logs = AuditLog.query.filter_by(user_id=current_user_id).order_by(
                AuditLog.created_at.desc()).limit(50).all()

            return jsonify({
                'audit_logs': [log.to_dict() for log in logs]
            }), 200

        except Exception as e:
            logging.error(f"Get audit logs error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Secure Portfolio Tracker API is running'})

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


def init_db(app):
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    app = create_app()

    # Initialize database
    with app.app_context():
        db.create_all()

    print("Secure Portfolio Tracker starting...")
    print("Available endpoints:")
    print("  POST /api/register - Register new user")
    print("  POST /api/login - User login")
    print("  POST /api/refresh - Refresh JWT token")
    print("  GET  /api/portfolios - Get user portfolios")
    print("  POST /api/portfolios - Create portfolio")
    print("  POST /api/portfolios/<id>/holdings - Add holding")
    print("  POST /api/user/api-key - Set encrypted API key")
    print("  GET  /api/user/api-key - Check API key status")
    print("  GET  /api/user/audit-logs - Get audit logs")
    print("  GET  /api/health - Health check")

    app.run(debug=True, host='0.0.0.0', port=5000)
