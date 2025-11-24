"""
Python Learning Journey - Day Twenty Two
Topic: Flask Fundamentals & Routing
Date: October 14, 2025
Author: Cosmas Onyekwelu

"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, session
import os
from datetime import datetime
import json

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask-fundamentals-day-22-secret-key'
# Enable debug mode for auto-reload and detailed errors
app.config['DEBUG'] = True

# Sample data for our application
users = [
    {'id': 1, 'username': 'alice', 'email': 'alice@example.com'},
    {'id': 2, 'username': 'bob', 'email': 'bob@example.com'},
    {'id': 3, 'username': 'charlie', 'email': 'charlie@example.com'}
]

products = [
    {'id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'electronics'},
    {'id': 2, 'name': 'Book', 'price': 29.99, 'category': 'education'},
    {'id': 3, 'name': 'Coffee Mug', 'price': 12.99, 'category': 'home'},
    {'id': 4, 'name': 'Headphones', 'price': 149.99, 'category': 'electronics'}
]

trades = [
    {'id': 1, 'asset': 'BTC', 'type': 'buy', 'amount': 0.5,
        'price': 45000, 'timestamp': '2024-01-15 10:30:00'},
    {'id': 2, 'asset': 'ETH', 'type': 'buy', 'amount': 2.0,
        'price': 3000, 'timestamp': '2024-01-16 14:45:00'},
    {'id': 3, 'asset': 'BTC', 'type': 'sell', 'amount': 0.1,
        'price': 46000, 'timestamp': '2024-01-17 09:15:00'},
]

# =============================================================================
# BASIC ROUTING EXAMPLES
# =============================================================================


@app.route('/')
def home():
    """Home page - demonstrates basic routing and template rendering"""
    return render_template('index.html',
                           title='Flask Fundamentals Dashboard',
                           current_time=datetime.now(),
                           user_count=len(users),
                           product_count=len(products))


@app.route('/hello')
def hello_world():
    """Simple route returning plain text"""
    return "Hello, World! Welcome to Flask Fundamentals!"


@app.route('/greet/<name>')
def greet_user(name):
    """Dynamic route with URL parameter"""
    return f"Hello, {name}! Welcome to our Flask application!"

# =============================================================================
# REQUEST HANDLING EXAMPLES
# =============================================================================


@app.route('/methods-demo', methods=['GET', 'POST', 'PUT', 'DELETE'])
def methods_demo():
    """Demonstrates different HTTP methods"""
    if request.method == 'GET':
        return """
        <h1>HTTP Methods Demo</h1>
        <p>This is a GET request</p>
        <form method="POST">
            <button type="submit">Send POST Request</button>
        </form>
        """
    elif request.method == 'POST':
        return "<h1>POST Request Received!</h1><p>Form submitted successfully.</p>"
    elif request.method == 'PUT':
        return jsonify({'message': 'PUT request handled', 'status': 'success'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'DELETE request handled', 'status': 'success'})


@app.route('/form-demo', methods=['GET', 'POST'])
def form_demo():
    """Handles form submissions"""
    if request.method == 'POST':
        # Access form data
        username = request.form.get('username')
        email = request.form.get('email')
        newsletter = 'newsletter' in request.form  # Checkbox

        flash(f'User {username} registered successfully!', 'success')
        return redirect(url_for('form_demo'))

    return render_template('form_demo.html', title='Form Demonstration')


@app.route('/query-demo')
def query_demo():
    """Handles URL query parameters"""
    name = request.args.get('name', 'Guest')
    page = request.args.get('page', '1')
    sort = request.args.get('sort', 'asc')

    return f"""
    <h1>Query Parameters Demo</h1>
    <p>Name: {name}</p>
    <p>Page: {page}</p>
    <p>Sort: {sort}</p>
    <p>Try adding ?name=YourName&page=2&sort=desc to the URL</p>
    """

# =============================================================================
# DYNAMIC ROUTES WITH CONVERTERS
# =============================================================================


@app.route('/user/<int:user_id>')
def show_user(user_id):
    """Integer converter - shows user by ID"""
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return render_template('user_profile.html', user=user, title=f"User {user['username']}")
    else:
        return render_template('404.html', title="User Not Found"), 404


@app.route('/product/<string:product_name>')
def show_product(product_name):
    """String converter - shows product by name"""
    product = next(
        (p for p in products if p['name'].lower() == product_name.lower()), None)
    if product:
        return f"Product: {product['name']} - ${product['price']}"
    else:
        return "Product not found", 404


@app.route('/trade/<int:trade_id>')
def show_trade(trade_id):
    """Shows individual trade details"""
    trade = next((t for t in trades if t['id'] == trade_id), None)
    if trade:
        return jsonify({
            'trade': trade,
            'total_value': trade['amount'] * trade['price']
        })
    else:
        return jsonify({'error': 'Trade not found'}), 404


@app.route('/price/<float:price>')
def show_price(price):
    """Float converter - demonstrates float in URLs"""
    return f"The price is: ${price:.2f}"


@app.route('/path-demo/<path:subpath>')
def path_demo(subpath):
    """Path converter - captures entire path"""
    return f"Subpath captured: {subpath}"

# =============================================================================
# URL BUILDING AND REDIRECTION
# =============================================================================


@app.route('/url-building-demo')
def url_building_demo():
    """Demonstrates URL building with url_for"""
    routes = {
        'Home': url_for('home'),
        'User Profile (ID 1)': url_for('show_user', user_id=1),
        'Product Page': url_for('show_product', product_name='Laptop'),
        'Form Demo': url_for('form_demo')
    }

    return render_template('url_building.html', routes=routes, title="URL Building Demo")


@app.route('/redirect-demo')
def redirect_demo():
    """Demonstrates different redirect methods"""
    target = request.args.get('target', 'home')

    if target == 'home':
        return redirect(url_for('home'))
    elif target == 'google':
        return redirect('https://www.google.com')
    elif target == 'user':
        return redirect(url_for('show_user', user_id=2))
    else:
        return "Invalid redirect target"

# =============================================================================
# RESPONSE OBJECTS AND CUSTOM RESPONSES
# =============================================================================


@app.route('/custom-response')
def custom_response():
    """Creates a custom response with headers"""
    response = make_response(render_template(
        'custom_response.html', title="Custom Response"))
    response.headers['X-Custom-Header'] = 'Flask-Demo'
    response.headers['Content-Language'] = 'en-US'
    response.set_cookie('visited', 'true', max_age=60*60*24)  # 1 day
    return response


@app.route('/json-api/users')
def json_users():
    """JSON API endpoint"""
    return jsonify({
        'users': users,
        'count': len(users),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/json-api/users/<int:user_id>')
def json_user_detail(user_id):
    """JSON API endpoint for specific user"""
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify({'user': user})
    else:
        return jsonify({'error': 'User not found'}), 404

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================


@app.route('/session-demo')
def session_demo():
    """Demonstrates session usage"""
    visit_count = session.get('visit_count', 0) + 1
    session['visit_count'] = visit_count
    session['last_visit'] = datetime.now().isoformat()

    return f"""
    <h1>Session Demo</h1>
    <p>Visit count: {visit_count}</p>
    <p>Last visit: {session.get('last_visit', 'Never')}</p>
    <form method="POST" action="/clear-session">
        <button type="submit">Clear Session</button>
    </form>
    """


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clears session data"""
    session.clear()
    flash('Session cleared successfully!', 'info')
    return redirect(url_for('session_demo'))

# =============================================================================
# ERROR HANDLING
# =============================================================================


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error handler"""
    return render_template('404.html',
                           title="Page Not Found",
                           error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Custom 500 error handler"""
    return render_template('500.html',
                           title="Server Error",
                           error=error), 500


@app.route('/trigger-error')
def trigger_error():
    """Route that intentionally triggers an error for demonstration"""
    raise ValueError("This is a demonstration error!")

# =============================================================================
# DATA FILTERING AND SEARCH
# =============================================================================


@app.route('/products')
def products_list():
    """Lists products with filtering capabilities"""
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    filtered_products = products

    if category:
        filtered_products = [
            p for p in filtered_products if p['category'] == category]

    if min_price is not None:
        filtered_products = [
            p for p in filtered_products if p['price'] >= min_price]

    if max_price is not None:
        filtered_products = [
            p for p in filtered_products if p['price'] <= max_price]

    return render_template('products.html',
                           products=filtered_products,
                           title="Products List",
                           category=category,
                           min_price=min_price,
                           max_price=max_price)


@app.route('/search')
def search():
    """Search functionality across users and products"""
    query = request.args.get('q', '').lower()

    if not query:
        return render_template('search.html',
                               title="Search",
                               query=query,
                               results=[])

    # Search in users
    user_results = [u for u in users if query in u['username'].lower(
    ) or query in u['email'].lower()]

    # Search in products
    product_results = [p for p in products if query in p['name'].lower(
    ) or query in p['category'].lower()]

    results = {
        'users': user_results,
        'products': product_results
    }

    return render_template('search.html',
                           title=f"Search: {query}",
                           query=query,
                           results=results)

# =============================================================================
# ADVANCED ROUTING PATTERNS
# =============================================================================


@app.route('/api/v1/')
def api_v1_root():
    """API version 1 root endpoint"""
    return jsonify({
        'version': '1.0',
        'endpoints': {
            'users': '/api/v1/users',
            'products': '/api/v1/products',
            'trades': '/api/v1/trades'
        }
    })


@app.route('/api/v1/users')
def api_v1_users():
    """API v1 users endpoint"""
    return jsonify({'users': users})


@app.route('/api/v1/products')
def api_v1_products():
    """API v1 products endpoint"""
    return jsonify({'products': products})


@app.route('/api/v1/trades')
def api_v1_trades():
    """API v1 trades endpoint"""
    return jsonify({'trades': trades})

# =============================================================================
# REQUEST OBJECT DEMONSTRATION
# =============================================================================


@app.route('/request-info')
def request_info():
    """Displays comprehensive request information"""
    info = {
        'method': request.method,
        'url': request.url,
        'base_url': request.base_url,
        'path': request.path,
        'full_path': request.full_path,
        'args': dict(request.args),
        'form': dict(request.form),
        'headers': dict(request.headers),
        'cookies': dict(request.cookies),
        'remote_addr': request.remote_addr,
        'user_agent': str(request.user_agent)
    }

    return jsonify(info)

# =============================================================================
# STATIC FILES DEMONSTRATION
# =============================================================================


@app.route('/static-demo')
def static_demo():
    """Demonstrates static file usage"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static Files Demo</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1>Static Files Demonstration</h1>
        <p>This page demonstrates static file serving.</p>
        <img src="/static/images/logo.png" alt="Logo" width="100">
        <script src="/static/js/script.js"></script>
    </body>
    </html>
    """

# =============================================================================
# APPLICATION CONFIGURATION AND UTILITIES
# =============================================================================


@app.route('/app-config')
def app_config():
    """Displays application configuration"""
    config_info = {
        'debug': app.config.get('DEBUG'),
        'secret_key_set': bool(app.config.get('SECRET_KEY')),
        'static_folder': app.static_folder,
        'template_folder': app.template_folder
    }

    return jsonify(config_info)


@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================


def create_template_files():
    """Create basic template files if they don't exist"""
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)

    # Create basic templates
    templates = {
        'index.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .nav { background: #333; padding: 10px; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; }
        .flash { background: #d4edda; padding: 10px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/form-demo">Form Demo</a>
        <a href="/products">Products</a>
        <a href="/search">Search</a>
        <a href="/session-demo">Session</a>
        <a href="/api/v1/">API</a>
    </div>
    
    <h1>{{ title }}</h1>
    <div class="card">
        <p>Current Time: {{ current_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        <p>Users: {{ user_count }} | Products: {{ product_count }}</p>
    </div>
    
    <div class="card">
        <h3>Quick Links:</h3>
        <ul>
            <li><a href="/user/1">User Profile Example</a></li>
            <li><a href="/greet/John">Dynamic Greeting</a></li>
            <li><a href="/methods-demo">HTTP Methods Demo</a></li>
            <li><a href="/query-demo?name=Alice&page=2">Query Parameters</a></li>
            <li><a href="/custom-response">Custom Response</a></li>
        </ul>
    </div>
</body>
</html>
        ''',

        'form_demo.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/form-demo">Form Demo</a>
    </div>
    
    <h1>{{ title }}</h1>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="flash">
                {% for message in messages %}
                    <p>{{ message }}</p>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <form method="POST">
        <div>
            <label>Username:</label>
            <input type="text" name="username" required>
        </div>
        <div>
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>
        <div>
            <label>
                <input type="checkbox" name="newsletter">
                Subscribe to newsletter
            </label>
        </div>
        <button type="submit">Register</button>
    </form>
</body>
</html>
        '''
    }

    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)


if __name__ == '__main__':
    # Create template files
    create_template_files()

    # Create static directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)

    print("Starting Flask Development Server...")
    print("Access the application at: http://localhost:5000")
    print("Debug mode: ON (Auto-reload enabled)")
    print("Available routes:")
    print("   - /                 : Home page")
    print("   - /form-demo        : Form handling demo")
    print("   - /user/<id>        : User profiles")
    print("   - /products         : Product listing with filters")
    print("   - /api/v1/*         : REST API endpoints")
    print("   - /session-demo     : Session management")
    print("   - /request-info     : Request object inspection")

    # Run the application with debug mode enabled
    app.run(
        debug=True,              # Enable debug mode
        host='0.0.0.0',         # Accessible from any interface
        port=5000,              # Default Flask port
        use_reloader=True       # Auto-reload on code changes
    )
