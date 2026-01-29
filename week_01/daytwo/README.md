# Day 02: Backend Fundamentals & Server Setup

**Date:** September 23, 2025

## Learning Objective
To understand the basics of backend development, including Linux server environments, web servers, and database management systems.

## Concepts Covered
- Linux distributions for servers (Ubuntu, Debian, CentOS, Fedora).
- Web server options (Nginx, Apache).
- Database systems (MySQL, PostgreSQL).
- Network security and firewall ports (HTTP: 80, HTTPS: 443, SSH: 22).
- Introduction to the Flask web framework.

## Code Explanation
The `day_two.py` script introduces a simple Flask application and demonstrates basic server configuration concepts.
- `linux_distros`, `web_servers`, `databases`: Lists of common technologies used in backend stacks.
- `firewall_ports`: A dictionary mapping services to their standard network ports.
- `recap_day_two()`: A function that prints a summary of the concepts learned.
- `app = Flask(__name__)`: Initializes a Flask application.
- `@app.route('/')`: A basic route that returns a welcome string.
- `@app.route('/server-info')`: A JSON route that returns the server configuration data.

## How to Run
1. Install Flask: `pip install flask`
2. Run the application:
```bash
python week_01/daytwo/day_two.py
```
3. Open your browser and visit `http://localhost:5000` or `http://localhost:5000/server-info`.

## Reflection
Setting up the backend environment and writing my first Flask app was eye-opening. Understanding how servers and databases communicate is crucial for full-stack development.
