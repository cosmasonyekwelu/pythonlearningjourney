"""
Python Learning Journey - Day Forty Two
Week 6 Summary - Networking & Security
Date: November 2, 2025
Author: Cosmas Onyekwelu
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///portfolio.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    _raw_key = os.environ.get("ENCRYPTION_KEY")
    if not _raw_key:
        _raw_key = Fernet.generate_key().decode()
    ENCRYPTION_KEY = _raw_key.encode()  # ensure bytes


# -------------------------------------------------------
# Utilities
# -------------------------------------------------------
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
        return bool(re.match(r'^[A-Z]{1,5}$', symbol))

    @staticmethod
    def validate_quantity(quantity):
        try:
            return float(quantity) > 0
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
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; connect-src 'self';"
        )
        return response


# -------------------------------------------------------
# Database Models
# -------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    secrets = db.relationship('UserSecret', backref='user', uselist=False)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey(
        'portfolio.id'), nullable=False)
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
            'current_value': round(self.quantity * self.average_price, 2),
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class UserSecret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False, unique=True)
    encrypted_api_key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------------------------------------
# JWT Configuration
# -------------------------------------------------------
@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id


# -------------------------------------------------------
# Helper: Audit Logging
# -------------------------------------------------------
def audit_log(action, user_id=None, details=None):
    try:
        ip = request.remote_addr if request else None
        ua = request.headers.get('User-Agent') if request else None
        details_str = json.dumps(details) if details else None

        entry = AuditLog(user_id=user_id, action=action,
                         ip_address=ip, user_agent=ua, details=details_str)
        db.session.add(entry)
        db.session.commit()
        logging.info(f"Audit: {action} - User {user_id}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Audit log failed: {e}")


# -------------------------------------------------------
# App Factory
# -------------------------------------------------------
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=["https://trusted-domain.com"])

    encryptor = DataEncryptor(app.config["ENCRYPTION_KEY"])

    @app.after_request
    def after_request(response):
        return SecurityHeaders.set_headers(response)

    # ---- Authentication Routes ----
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        email = InputValidator.sanitize_string(data.get("email"))
        password = data.get("password")

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        if not InputValidator.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        valid_pw, msg = InputValidator.validate_password(password)
        if not valid_pw:
            return jsonify({'error': msg}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 409

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        audit_log('register', user.id, {'email': email})
        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        email = InputValidator.sanitize_string(data.get("email"))
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            audit_log('login_failed', None, {'email': email})
            return jsonify({'error': 'Invalid credentials'}), 401

        access = create_access_token(identity=user.id)
        refresh = create_refresh_token(identity=user.id)
        audit_log('login_success', user.id)
        return jsonify({'access_token': access, 'refresh_token': refresh, 'user': user.to_dict()}), 200

    # ---- Health Check ----
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'time': datetime.utcnow().isoformat()})

    return app


# -------------------------------------------------------
# Entry Point
# -------------------------------------------------------
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    app = create_app()
    with app.app_context():
        db.create_all()
    print("Secure Portfolio Tracker API running on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
