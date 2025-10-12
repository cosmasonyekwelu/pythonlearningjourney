"""
Day 22 - Flask Fundamentals & Routing
Date: October 13, 2025

COMPREHENSIVE LEARNING SUMMARY
Resources Studied:
- Flask Official Documentation
- Flask Mega-Tutorial by Miguel Grinberg
- Real Python Flask Tutorials
- GeeksforGeeks Flask Tutorial
- Tutorialspoint Flask Guide
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-2025'


def create_learning_summary():
    """Structured summary of concepts learned from Flask tutorials."""
    return {
        "flask_basics": {
            "title": "Flask Fundamentals",
            "points": [
                "Flask is a micro web framework — lightweight and extensible.",
                "Built-in development server with auto-reload.",
                "Jinja2 templating engine for dynamic HTML rendering.",
                "Werkzeug toolkit for WSGI interface handling."
            ]
        },
        "routing_concepts": {
            "title": "Routing & URL Handling",
            "points": [
                "@app.route() maps URLs to view functions.",
                "Dynamic routes support URL variables using <variable> syntax.",
                "Support for multiple HTTP methods (GET, POST).",
                "Use url_for() for URL generation and maintenance."
            ]
        },
        "request_response": {
            "title": "Request & Response Handling",
            "points": [
                "The request object provides incoming request data.",
                "Access form data using request.form['name'].",
                "Access query parameters using request.args.get().",
                "Use jsonify() to send JSON responses."
            ]
        },
        "templates_jinja2": {
            "title": "Templates & Jinja2",
            "points": [
                "Template inheritance using {% extends %} and {% block %}.",
                "Render variables with {{ variable }} syntax.",
                "Use control structures: {% for %}, {% if %}, etc."
            ]
        },
        "static_files": {
            "title": "Static Files Management",
            "points": [
                "Static files live in the 'static' folder.",
                "Use url_for('static', filename='file.css') for linking assets."
            ]
        }
    }


@app.route('/')
def home():
    """Home page displaying summary metrics."""
    data = create_learning_summary()
    total_concepts = sum(len(section['points']) for section in data.values())
    return render_template(
        'index.html',
        title='Flask Learning Dashboard',
        current_time=datetime.now(),
        total_concepts=total_concepts,
        data=data
    )


@app.route('/learning-summary')
def learning_summary():
    """Detailed learning summary page."""
    summary = create_learning_summary()
    return render_template('learning_summary.html', title='Comprehensive Learning Summary', summary=summary)


@app.route('/api/concepts')
def api_concepts():
    """Example REST endpoint."""
    concepts = {
        "framework": "Flask",
        "type": "Micro web framework",
        "features": [
            "Lightweight and modular",
            "Built-in development server",
            "Jinja2 templates",
            "RESTful routing"
        ],
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(concepts)


@app.errorhandler(404)
def not_found(error):
    """Custom 404 error page."""
    return "<h1>404 - Page Not Found</h1><p>The requested page could not be found.</p>", 404


def print_learning_cheatsheet():
    """Displays a concise summary in terminal."""
    print("\n" + "="*60)
    print("FLASK LEARNING CHEATSHEET - DAY 22")
    print("="*60)
    print("1. Flask is lightweight but powerful.")
    print("2. Use url_for() for dynamic URLs.")
    print("3. Template inheritance improves maintainability.")
    print("4. The request object contains all client data.")
    print("5. Use jsonify() for structured API responses.")
    print("="*60)


if __name__ == '__main__':
    print_learning_cheatsheet()
    print("\nStarting Flask Development Server...")
    print("Access the learning dashboard at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
