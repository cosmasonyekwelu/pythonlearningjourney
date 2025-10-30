"""
Day 37: Building Secure APIs
This module demonstrates secure API development practices including:
- Input validation and sanitization
- Rate limiting
- SQL injection prevention
- CORS configuration
- Security headers
"""

import re
import sqlite3
from contextlib import contextmanager
from flask import Flask, request, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Rate limiting setup
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# CORS configuration
CORS(app, origins=['https://trusted-domain.com'])

# Database setup


def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@contextmanager
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Input validation functions


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username (alphanumeric, 3-20 characters)"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


def sanitize_input(input_string):
    """Sanitize input to prevent XSS"""
    return html.escape(input_string.strip())

# Secure API endpoints


@app.route('/api/register', methods=['POST'])
@limiter.limit("10 per minute")
def register_user():
    """Secure user registration endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Input validation
        username = sanitize_input(data.get('username', ''))
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        if not validate_username(username):
            return jsonify({'error': 'Invalid username format'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        # Secure database operation (parameterized query)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    # In real app, use proper hashing
                    (username, email, f"hash_{password}")
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return jsonify({'error': 'Username or email already exists'}), 409

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/users/<int:user_id>')
@limiter.limit("100 per hour")
def get_user(user_id):
    """Secure user retrieval endpoint"""
    # Input validation for user_id
    if user_id <= 0:
        return jsonify({'error': 'Invalid user ID'}), 400

    # Secure database query
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(dict(user))

# Security headers middleware


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Error handling


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    init_db()
    # In production, use HTTPS and disable debug mode
    app.run(debug=False, host='0.0.0.0', port=5000)
