"""
Python Learning Journey - Day Two
Date: September 23, 2025
Author: Cosmas Onyekwelu
Topic: Setting up a Linux Server for Hosting & Database Management
"""

from flask import Flask

# Common Linux distributions for servers
linux_distros = ["Ubuntu", "Debian", "CentOS", "Fedora"]

# Popular web servers for hosting applications
web_servers = ["Apache", "Nginx"]

# Database management systems commonly used in backend development
databases = ["MySQL/MariaDB", "PostgreSQL"]

# Standard firewall ports for common services
firewall_ports = {
    "HTTP": 80,
    "HTTPS": 443,
    "SSH": 22,
    "MySQL": 3306,
    "Postgres": 5432
}


def recap_day_two():
    """Summarize the key learning points from Day Two"""
    print("=== Day Two Learning Recap ===")
    print("Today we covered server setup and backend fundamentals:")
    print()
    print("1. Installed and updated a Linux server environment")
    print("2. Explored web server options:", ", ".join(web_servers))
    print("3. Set up database systems:", ", ".join(databases))
    print("4. Configured firewall rules for essential ports:")

    for service, port in firewall_ports.items():
        print(f"   - {service}: port {port}")

    print("5. Deployed a Flask web application with SSL security")
    print("6. Attended orientation on backend development and Google Classroom setup")
    print()
    print("Ready to start the Flask demo server...")


# Create a simple Flask web application
app = Flask(__name__)


@app.route('/')
def home():
    """Main route that returns a welcome message"""
    return "Hello from our Flask application! Day Two of Python Learning Journey"


@app.route('/server-info')
def server_info():
    """Route showing server configuration details"""
    return {
        "web_servers": web_servers,
        "databases": databases,
        "firewall_ports": firewall_ports
    }


if __name__ == "__main__":
    # Display the day's learning summary
    recap_day_two()

    # Start the Flask development server
    print("\nStarting Flask development server...")
    print("Access the application at: http://localhost:5000")
    print("Server info available at: http://localhost:5000/server-info")
    print("Press Ctrl+C to stop the server")

    app.run(host="0.0.0.0", port=5000, debug=True)
