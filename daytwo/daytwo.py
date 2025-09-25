"""
Python Learning Journey - Day Two
Date: September 23, 2025
Author: Cosmas Onyekwelu
Topic: Setting up a Linux Server for Hosting & Database Management
"""

# Key concepts reviewed:
from flask import Flask
linux_distros = ["Ubuntu", "Debian", "CentOS", "Fedora"]
web_servers = ["Apache", "Nginx"]
databases = ["MySQL/MariaDB", "PostgreSQL"]
firewall_ports = {"HTTP": 80, "HTTPS": 443,
                  "SSH": 22, "MySQL": 3306, "Postgres": 5432}


def recap():
    print("🔑 Day Two Recap")
    print("1. Installed and updated Linux server.")
    print("2. Learned web servers:", web_servers)
    print("3. Installed databases:", databases)
    print("4. Configured firewall for ports:", firewall_ports)
    print("5. Deployed a Flask app and enabled SSL with Certbot.")
    print("6. Orientation by Mr. Miracle: Backend Intro + Google Classroom setup.")


# Flask mini-demo
app = Flask(__name__)


@app.route('/')
def home():
    return "Hello from Flask! Day Two Learning Journey 🚀"


if __name__ == "__main__":
    recap()
    app.run(host="0.0.0.0", port=5000)
