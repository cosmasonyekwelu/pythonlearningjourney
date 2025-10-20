# Flask Quick Reference Cheatsheet

## Flask Project Structure

```
flask_app/
├── app.py                    # Main application file
├── requirements.txt          # Dependencies
├── config.py                # Configuration (optional)
├── .env                     # Environment variables
├── static/                  # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
└── templates/               # Jinja2 templates
    ├── base.html
    ├── index.html
    ├── partials/
    │   └── _navbar.html
    └── errors/
        └── 404.html
```

## Basic Flask Application

### Minimal App

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

### Enhanced App Structure

```python
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for sessions, flash messages
app.config['DEBUG'] = True  # Development only!

# Basic routes
@app.route('/')
def index():
    return render_template('index.html', title='Home Page')

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## Routing & URL Handling

### Basic Routes

```python
@app.route('/')
def home():
    return 'Home Page'

@app.route('/hello')
def hello():
    return 'Hello World!'

@app.route('/user/dashboard')
def user_dashboard():
    return 'User Dashboard'
```

### Dynamic Routes with Converters

```python
# String converter (default)
@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'

# Integer converter
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post #{post_id}'

# Float converter
@app.route('/price/<float:price>')
def show_price(price):
    return f'Price: ${price:.2f}'

# Path converter (includes slashes)
@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f'Subpath: {subpath}'

# UUID converter
@app.route('/item/<uuid:item_id>')
def show_item(item_id):
    return f'Item ID: {item_id}'
```

### HTTP Methods

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        username = request.form['username']
        password = request.form['password']
        return f'Logged in as {username}'
    else:
        # Show login form
        return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <input type="submit" value="Login">
        </form>
        '''

# Specific methods only
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'data': 'some data'})

@app.route('/api/data', methods=['POST'])
def create_data():
    return jsonify({'status': 'created'}), 201
```

### URL Building

```python
from flask import url_for

@app.route('/')
def index():
    return 'Index Page'

@app.route('/user/<username>')
def profile(username):
    return f'{username}\'s profile'

# Using url_for in routes
@app.route('/urls')
def show_urls():
    return f'''
    Index URL: {url_for('index')}
    Profile URL: {url_for('profile', username='john')}
    '''
```

## Request Handling

### Accessing Request Data

```python
from flask import request

@app.route('/submit', methods=['POST'])
def submit():
    # Form data
    name = request.form.get('name', 'Anonymous')
    email = request.form['email']  # Raises KeyError if missing

    # URL parameters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')

    # JSON data
    if request.is_json:
        data = request.get_json()

    # Files
    file = request.files.get('file')
    if file:
        file.save(f'uploads/{file.filename}')

    # Headers
    user_agent = request.headers.get('User-Agent')

    return f'Received: {name}, {email}'

# Request object properties
print(request.method)      # HTTP method
print(request.path)        # Request path
print(request.full_path)   # Full path with query string
print(request.url)         # Full URL
print(request.remote_addr) # Client IP address
```

### Request Validation

```python
from flask import abort

@app.route('/user/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        abort(400, description="Invalid user ID")

    user = find_user(user_id)
    if not user:
        abort(404, description="User not found")

    return jsonify(user)

# Custom error handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
```

## Template System (Jinja2)

### Basic Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}My App{% endblock %}</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/style.css') }}"
    />
  </head>
  <body>
    <nav>{% include 'partials/_navbar.html' %}</nav>

    <main>
      {% with messages = get_flashed_messages() %} {% if messages %}
      <div class="flash-messages">
        {% for message in messages %}
        <div class="alert">{{ message }}</div>
        {% endfor %}
      </div>
      {% endif %} {% endwith %} {% block content %}{% endblock %}
    </main>

    <footer>{% include 'partials/_footer.html' %}</footer>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
  </body>
</html>
```

### Template Inheritance

```html
<!-- templates/index.html -->
{% extends "base.html" %} {% block title %}Home - My App{% endblock %} {% block
content %}
<div class="container">
  <h1>Welcome to My App</h1>
  <p>Current time: {{ current_time.strftime('%Y-%m-%d %H:%M') }}</p>

  {% if user %}
  <p>Hello, {{ user.username }}!</p>
  {% else %}
  <p>Please <a href="{{ url_for('login') }}">log in</a>.</p>
  {% endif %}

  <ul>
    {% for item in items %}
    <li
      class="{% if loop.first %}first{% endif %} {% if loop.last %}last{% endif %}"
    >
      {{ loop.index }}. {{ item.name }}
    </li>
    {% else %}
    <li>No items found.</li>
    {% endfor %}
  </ul>
</div>
{% endblock %}
```

### Jinja2 Filters

```html
<!-- String filters -->
<p>{{ name|upper }}</p>
<p>{{ title|lower }}</p>
<p>{{ description|title }}</p>
<p>{{ text|truncate(100) }}</p>

<!-- Number filters -->
<p>{{ price|round(2) }}</p>
<p>{{ count|abs }}</p>

<!-- Date filters -->
<p>{{ created_at|datetime }}</p>
<p>{{ updated_at|dateformat }}</p>

<!-- List filters -->
<p>{{ items|length }} items</p>
<p>{{ list|first }}</p>
<p>{{ list|last }}</p>
<p>{{ list|sort }}</p>

<!-- Custom filters -->
<p>{{ value|currency }}</p>
<p>{{ html_content|safe }}</p>
```

### Custom Filters

```python
from flask import Flask
import datetime

app = Flask(__name__)

@app.template_filter('datetime')
def format_datetime(value, format='medium'):
    if format == 'full':
        format = "%Y-%m-%d %H:%M:%S"
    elif format == 'medium':
        format = "%Y-%m-%d %H:%M"
    return value.strftime(format)

@app.template_filter('currency')
def format_currency(value):
    return f"${value:,.2f}"

# Using in templates
# {{ product.price|currency }}
# {{ created_at|datetime('full') }}
```

## Response Handling

### Different Response Types

```python
from flask import make_response, redirect, url_for, jsonify, render_template

@app.route('/text')
def text_response():
    return "Plain text response"

@app.route('/html')
def html_response():
    return "<h1>HTML response</h1>"

@app.route('/template')
def template_response():
    return render_template('page.html', title='Page Title')

@app.route('/json')
def json_response():
    return jsonify({'status': 'success', 'data': [1, 2, 3]})

@app.route('/redirect')
def redirect_example():
    return redirect(url_for('home'))

@app.route('/custom-response')
def custom_response():
    response = make_response('Custom response')
    response.headers['X-Custom-Header'] = 'Value'
    response.status_code = 201
    return response

@app.route('/download')
def download_file():
    return send_file('file.pdf', as_attachment=True)
```

### Setting Cookies & Sessions

```python
from flask import session, make_response

@app.route('/set-cookie')
def set_cookie():
    resp = make_response('Cookie set!')
    resp.set_cookie('username', 'john', max_age=60*60*24)  # 1 day
    return resp

@app.route('/get-cookie')
def get_cookie():
    username = request.cookies.get('username')
    return f'Hello {username}'

@app.route('/set-session')
def set_session():
    session['user_id'] = 123
    session['username'] = 'john'
    return 'Session set!'

@app.route('/get-session')
def get_session():
    user_id = session.get('user_id')
    username = session.get('username')
    return f'User: {username} (ID: {user_id})'

@app.route('/clear-session')
def clear_session():
    session.clear()
    return 'Session cleared!'
```

## Authentication & Security

### Basic Authentication

```python
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Password hashing
password_hash = generate_password_hash('mypassword')
is_valid = check_password_hash(password_hash, 'mypassword')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

# Authentication decorator
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

### CSRF Protection

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process form data
        pass
    return render_template('login.html', form=form)
```

```html
<!-- In template -->
<form method="post">
  {{ form.hidden_tag() }} {{ form.username.label }} {{ form.username() }} {{
  form.password.label }} {{ form.password() }}
  <input type="submit" value="Login" />
</form>
```

## Database Integration

### SQLAlchemy Setup

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
```

### Database Operations

```python
# Create
user = User(username='john', email='john@example.com')
db.session.add(user)
db.session.commit()

# Read
users = User.query.all()
user = User.query.get(1)
user = User.query.filter_by(username='john').first()
users = User.query.filter(User.email.like('%@example.com')).all()

# Update
user = User.query.get(1)
user.email = 'new@example.com'
db.session.commit()

# Delete
user = User.query.get(1)
db.session.delete(user)
db.session.commit()

# Complex queries
from sqlalchemy import desc, and_, or_

recent_users = User.query.order_by(desc(User.created_at)).limit(10)
active_users = User.query.filter(
    and_(
        User.email.isnot(None),
        or_(User.active == True, User.last_login >= datetime.utcnow() - timedelta(days=30))
    )
).all()
```

## API Development

### RESTful API Routes

```python
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})
```

### Error Handling for APIs

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400
```

## Configuration & Environment

### Configuration Management

```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Usage
app.config.from_object(DevelopmentConfig)  # or ProductionConfig, TestingConfig
```

### Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
```

## Common Patterns & Utilities

### Flash Messages

```python
from flask import flash

@app.route('/action', methods=['POST'])
def perform_action():
    try:
        # Perform some action
        flash('Action completed successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('index'))
```

```html
<!-- Display flash messages -->
{% with messages = get_flashed_messages(with_categories=true) %} {% if messages
%}
<div class="flash-messages">
  {% for category, message in messages %}
  <div class="alert alert-{{ category }}">{{ message }}</div>
  {% endfor %}
</div>
{% endif %} {% endwith %}
```

### File Upload

```python
import os
from werkzeug.utils import secure_filename

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type', 'error')
        return redirect(request.url)
```

### Pagination

```python
@app.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('posts.html', posts=posts)
```

```html
<!-- Pagination in template -->
<div class="pagination">
  {% if posts.has_prev %}
  <a href="{{ url_for('posts', page=posts.prev_num) }}">Previous</a>
  {% endif %}

  <span>Page {{ posts.page }} of {{ posts.pages }}</span>

  {% if posts.has_next %}
  <a href="{{ url_for('posts', page=posts.next_num) }}">Next</a>
  {% endif %}
</div>
```

## Common Flask Extensions

### Popular Extensions

```python
# Database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

# Authentication
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

# API
from flask_restful import Api, Resource

# Mail
from flask_mail import Mail, Message

# Caching
from flask_caching import Cache

# Admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
```

### Extension Setup Examples

```python
# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flask-Mail
mail = Mail(app)

@app.route('/send-email')
def send_email():
    msg = Message('Hello', sender='from@example.com', recipients=['to@example.com'])
    msg.body = "This is a test email"
    mail.send(msg)
    return 'Email sent!'

# Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/expensive-operation')
@cache.cached(timeout=300)  # Cache for 5 minutes
def expensive_operation():
    # Some expensive computation
    return 'Result'
```

## Deployment Configuration

### Production WSGI

```python
# wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

### Production Configuration

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Logging
    LOG_LEVEL = 'WARNING'
```

### Requirements File

```txt
# requirements.txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.1.1
Flask-Login==0.6.3
Flask-Mail==0.9.1
python-dotenv==1.0.0
Werkzeug==2.3.7
Jinja2==3.1.2
```

## Quick Reference Commands

### Development Commands

```bash
# Run development server
python app.py
flask run
flask run --host=0.0.0.0 --port=5000

# Shell context
flask shell

# Database commands (with Flask-Migrate)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask db downgrade

# Environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Debugging

```python
# Debug mode
app.run(debug=True)

# Print debugging
print(variable)
print(request.form)
print(session)

# Logging
import logging
app.logger.debug('Debug message')
app.logger.info('Info message')
app.logger.warning('Warning message')
app.logger.error('Error message')
```

This comprehensive Flask cheatsheet covers everything from basic routing to advanced patterns. Keep this handy as you build your Flask applications!
