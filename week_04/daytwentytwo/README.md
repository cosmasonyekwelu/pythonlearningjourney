# Day 22: Flask Fundamentals & Routing

**Date:** October 14, 2025

## Learning Objective
To master the basics of the Flask web framework, including application setup, routing, request handling, and template rendering.

## Concepts Covered
- **Basic Routing**: Using `@app.route` to map URLs to Python functions.
- **Dynamic Routes**: Using variable rules and converters (`<int:id>`, `<string:name>`).
- **HTTP Methods**: Handling GET, POST, PUT, and DELETE requests.
- **Request Handling**: Accessing form data (`request.form`), query parameters (`request.args`), and JSON payloads.
- **Jinja2 Templates**: Rendering HTML with dynamic content and using `url_for` for path building.
- **Session Management**: Storing user-specific data across requests.

## Code Explanation
The `day_twentytwo.py` script is a comprehensive Flask toolkit:
- **`home()`**: Demonstrates passing multiple variables to a template.
- **`methods_demo()`**: Shows how a single route can behave differently based on the HTTP method used.
- **`show_user(user_id)`**: Illustrates integer converters and dynamic error pages (404).
- **`custom_response()`**: Shows how to set custom headers and cookies manually.
- **`json_api/users`**: A basic example of building a JSON API using `jsonify`.

## How to Run
1. Install Flask: `pip install flask`
2. Run the application:
```bash
python week_04/daytwentytwo/day_twentytwo.py
```
3. Visit `http://localhost:5000` to see the dashboard.

## Reflection
Flask is beautifully simple but extremely extensible. Its "micro" nature makes it easy to understand the fundamental lifecycle of a web request before moving on to more complex frameworks like Django.
