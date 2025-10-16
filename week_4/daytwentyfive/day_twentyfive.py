"""
Day 25 — User Authentication & Sessions
Focus: Implementing secure login and user management systems
Date: October 16, 2025
"""

# --------------------------------------------------------
# 🧱 IMPORTS
# --------------------------------------------------------
from flask import Flask, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

# --------------------------------------------------------
# ⚙️ APP CONFIGURATION
# --------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///day25_auth.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --------------------------------------------------------
# 👤 USER MODEL
# --------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify hashed password"""
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------------------------------------
# 🧠 HELPER FUNCTIONS
# --------------------------------------------------------
def validate_user_input(data, required_fields):
    """Ensure all required fields are provided"""
    for field in required_fields:
        if field not in data:
            return False
    return True


# --------------------------------------------------------
# 🧱 AUTH ROUTES
# --------------------------------------------------------

@app.route('/')
def home():
    if current_user.is_authenticated:
        return jsonify({
            "message": f"Welcome back, {current_user.username}!",
            "user": current_user.username
        })
    return jsonify({"message": "Welcome to Day 25 Authentication System!"})


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not validate_user_input(data, ['email', 'username', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(email=data['email'], username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not validate_user_input(data, ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        login_user(user, remember=True)
        session.permanent = True  # session timeout controlled by app config
        return jsonify({"message": "Login successful", "user": user.username})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    """Protected route only for authenticated users"""
    return jsonify({
        "username": current_user.username,
        "email": current_user.email,
        "active": current_user.is_active,
        "created_at": current_user.created_at
    })


@app.route('/deactivate', methods=['POST'])
@login_required
def deactivate_user():
    """Deactivate current user account"""
    current_user.is_active = False
    db.session.commit()
    logout_user()
    return jsonify({"message": "Account deactivated"})


# --------------------------------------------------------
# 🚀 RUN APP
# --------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
