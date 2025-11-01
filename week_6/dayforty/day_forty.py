"""
Day 40: Web Security Best Practices & OWASP Top 10
Comprehensive web security vulnerability demonstration and protection implementation.
"""

import sqlite3
import html
import re
import json
import secrets
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from cryptography.fernet import Fernet
import bcrypt
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VulnerableApp:
    """
    Deliberately vulnerable application to demonstrate OWASP Top 10 vulnerabilities
    and their fixes.
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'insecure-secret-key-change-in-production'
        self.setup_database()
        self.setup_routes()

        # Encryption key for demonstration
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def setup_database(self):
        """Initialize vulnerable database"""
        self.conn = sqlite3.connect(
            'vulnerable_app.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Create tables with insecure design
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,  -- Stored in plain text (vulnerable)
                email TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                author TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensitive_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                credit_card TEXT,  -- Stored unencrypted (vulnerable)
                ssn TEXT,
                data TEXT
            )
        ''')

        # Add some test data
        self.cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 'admin')")
        self.cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (2, 'user1', 'password123', 'user1@example.com', 'user')")
        self.cursor.execute(
            "INSERT OR IGNORE INTO sensitive_data VALUES (1, 1, '4111111111111111', '123-45-6789', 'Confidential info')")

        self.conn.commit()

    def setup_routes(self):
        """Setup vulnerable and secure routes for comparison"""

        # VULNERABLE ROUTES

        @self.app.route('/vulnerable/login', methods=['GET', 'POST'])
        def vulnerable_login():
            """Vulnerable login - SQL Injection and weak authentication"""
            if request.method == 'POST':
                username = request.form.get('username', '')
                password = request.form.get('password', '')

                # VULNERABLE: SQL Injection
                query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
                logger.warning(f"VULNERABLE SQL QUERY: {query}")

                try:
                    self.cursor.execute(query)
                    user = self.cursor.fetchone()

                    if user:
                        session['user_id'] = user[0]
                        session['username'] = user[1]
                        session['role'] = user[4]
                        return f"Welcome {user[1]}! Role: {user[4]}"
                    else:
                        return "Invalid credentials"
                except Exception as e:
                    return f"Error: {str(e)}"

            return '''
            <form method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p>Try SQL Injection: <code>' OR '1'='1' --</code></p>
            '''

        @self.app.route('/vulnerable/search')
        def vulnerable_search():
            """Vulnerable search - XSS and SQL Injection"""
            query = request.args.get('q', '')

            # VULNERABLE: Reflected XSS
            results_html = f"<h3>Search results for: {query}</h3>"

            # VULNERABLE: SQL Injection
            if query:
                sql = f"SELECT * FROM posts WHERE title LIKE '%{query}%' OR content LIKE '%{query}%'"
                self.cursor.execute(sql)
                posts = self.cursor.fetchall()

                for post in posts:
                    results_html += f"<div><h4>{post[1]}</h4><p>{post[2]}</p></div>"

            return f'''
            <h2>Vulnerable Search</h2>
            <form>
                <input type="text" name="q" value="{query}">
                <button type="submit">Search</button>
            </form>
            {results_html}
            <p>Try XSS: <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></p>
            '''

        @self.app.route('/vulnerable/profile/<user_id>')
        def vulnerable_profile(user_id):
            """Vulnerable profile - Broken Access Control"""
            # VULNERABLE: Insecure Direct Object Reference (IDOR)
            self.cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
            user = self.cursor.fetchone()

            if user:
                # VULNERABLE: No authorization check
                self.cursor.execute(
                    f"SELECT * FROM sensitive_data WHERE user_id = {user_id}")
                sensitive_data = self.cursor.fetchone()

                return f'''
                <h2>Profile: {user[1]}</h2>
                <p>Email: {user[3]}</p>
                <p>Role: {user[4]}</p>
                <h3>Sensitive Data:</h3>
                <p>Credit Card: {sensitive_data[2] if sensitive_data else 'None'}</p>
                <p>SSN: {sensitive_data[3] if sensitive_data else 'None'}</p>
                '''
            return "User not found"

        @self.app.route('/vulnerable/transfer', methods=['POST'])
        def vulnerable_transfer():
            """Vulnerable CSRF example"""
            if 'user_id' not in session:
                return "Not logged in"

            # VULNERABLE: No CSRF protection
            amount = request.form.get('amount')
            to_user = request.form.get('to_user')

            return f"Transferred ${amount} to {to_user}"

        # SECURE ROUTES

        @self.app.route('/secure/login', methods=['GET', 'POST'])
        def secure_login():
            """Secure login with parameterized queries and password hashing"""
            if request.method == 'POST':
                username = request.form.get('username', '')
                password = request.form.get('password', '')

                # SECURE: Parameterized query
                query = "SELECT * FROM users_secure WHERE username = ?"
                self.cursor.execute(query, (username,))
                user = self.cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[4]
                    session['csrf_token'] = secrets.token_urlsafe(32)
                    return f"Welcome {user[1]}! Role: {user[4]}"
                else:
                    return "Invalid credentials"

            return '''
            <form method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            '''

        @self.app.route('/secure/search')
        def secure_search():
            """Secure search with input validation and output encoding"""
            query = request.args.get('q', '')

            # SECURE: Input validation
            if not re.match(r'^[a-zA-Z0-9\s]{1,50}$', query):
                return "Invalid search query"

            # SECURE: Output encoding
            safe_query = html.escape(query)
            results_html = f"<h3>Search results for: {safe_query}</h3>"

            # SECURE: Parameterized query
            if query:
                sql = "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?"
                self.cursor.execute(sql, (f'%{query}%', f'%{query}%'))
                posts = self.cursor.fetchall()

                for post in posts:
                    safe_title = html.escape(post[1])
                    safe_content = html.escape(post[2])
                    results_html += f"<div><h4>{safe_title}</h4><p>{safe_content}</p></div>"

            return f'''
            <h2>Secure Search</h2>
            <form>
                <input type="text" name="q" value="{safe_query}">
                <button type="submit">Search</button>
            </form>
            {results_html}
            '''

        @self.app.route('/secure/profile/<int:user_id>')
        def secure_profile(user_id):
            """Secure profile with proper authorization"""
            if 'user_id' not in session:
                return "Please login"

            # SECURE: Authorization check
            if session['user_id'] != user_id and session['role'] != 'admin':
                return "Access denied"

            # SECURE: Parameterized query
            self.cursor.execute(
                "SELECT * FROM users_secure WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()

            if user:
                # SECURE: Encrypted sensitive data
                self.cursor.execute(
                    "SELECT * FROM sensitive_data_secure WHERE user_id = ?", (user_id,))
                sensitive_data = self.cursor.fetchone()

                decrypted_cc = self.fernet.decrypt(
                    sensitive_data[2].encode()).decode() if sensitive_data else "N/A"
                decrypted_ssn = self.fernet.decrypt(
                    sensitive_data[3].encode()).decode() if sensitive_data else "N/A"

                return f'''
                <h2>Profile: {html.escape(user[1])}</h2>
                <p>Email: {html.escape(user[3])}</p>
                <p>Role: {html.escape(user[4])}</p>
                <h3>Sensitive Data:</h3>
                <p>Credit Card: {decrypted_cc}</p>
                <p>SSN: {decrypted_ssn}</p>
                '''
            return "User not found"

        @self.app.route('/secure/transfer', methods=['POST'])
        def secure_transfer():
            """Secure transfer with CSRF protection"""
            if 'user_id' not in session:
                return "Not logged in"

            # SECURE: CSRF token validation
            if request.form.get('csrf_token') != session.get('csrf_token'):
                return "Invalid CSRF token"

            amount = request.form.get('amount')
            to_user = request.form.get('to_user')

            # SECURE: Input validation
            if not re.match(r'^\d+$', amount) or not re.match(r'^[a-zA-Z0-9]+$', to_user):
                return "Invalid input"

            return f"Transferred ${amount} to {to_user}"

        # SECURITY DEMONSTRATION ROUTES

        @self.app.route('/demo/sql-injection')
        def demo_sql_injection():
            """Demonstrate SQL Injection vulnerabilities and protections"""
            return '''
            <h2>SQL Injection Demo</h2>
            <h3>Vulnerable Examples:</h3>
            <ul>
                <li><a href="/vulnerable/login">Vulnerable Login</a> - Try: <code>' OR '1'='1' --</code></li>
                <li><a href="/vulnerable/search?q=test">Vulnerable Search</a> - Try: <code>' UNION SELECT * FROM users --</code></li>
            </ul>
            <h3>Secure Examples:</h3>
            <ul>
                <li><a href="/secure/login">Secure Login</a> - Uses parameterized queries</li>
                <li><a href="/secure/search?q=test">Secure Search</a> - Uses input validation</li>
            </ul>
            '''

        @self.app.route('/demo/xss')
        def demo_xss():
            """Demonstrate XSS vulnerabilities and protections"""
            return '''
            <h2>XSS Demo</h2>
            <h3>Vulnerable Examples:</h3>
            <ul>
                <li><a href="/vulnerable/search?q=">Vulnerable Search</a> - Try: <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></li>
            </ul>
            <h3>Secure Examples:</h3>
            <ul>
                <li><a href="/secure/search?q=">Secure Search</a> - Uses HTML escaping</li>
            </ul>
            '''

        @self.app.route('/demo/access-control')
        def demo_access_control():
            """Demonstrate Broken Access Control vulnerabilities"""
            return '''
            <h2>Broken Access Control Demo</h2>
            <h3>Vulnerable Examples:</h3>
            <ul>
                <li><a href="/vulnerable/profile/1">Admin Profile (IDOR)</a> - Try changing user ID</li>
            </ul>
            <h3>Secure Examples:</h3>
            <ul>
                <li><a href="/secure/profile/1">Secure Profile</a> - Proper authorization checks</li>
            </ul>
            '''

        @self.app.route('/')
        def index():
            return '''
            <h1>Web Security Demo</h1>
            <p>This application demonstrates common web security vulnerabilities and their fixes.</p>
            <h2>OWASP Top 10 Demonstrations:</h2>
            <ul>
                <li><a href="/demo/sql-injection">A03: Injection</a></li>
                <li><a href="/demo/xss">A03: XSS</a></li>
                <li><a href="/demo/access-control">A01: Broken Access Control</a></li>
            </ul>
            <h3>Security Best Practices Implemented:</h3>
            <ul>
                <li>Parameterized Queries (SQL Injection Prevention)</li>
                <li>Input Validation & Sanitization</li>
                <li>Output Encoding (XSS Prevention)</li>
                <li>Proper Authentication & Authorization</li>
                <li>CSRF Protection</li>
                <li>Data Encryption</li>
                <li>Secure Password Hashing</li>
            </ul>
            '''


class SecurityScanner:
    """Basic web vulnerability scanner for educational purposes"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.vulnerabilities = []

    def test_sql_injection(self, endpoint: str, method: str = 'GET') -> List[Dict]:
        """Test for SQL injection vulnerabilities"""
        tests = [
            {"payload": "' OR '1'='1' --", "description": "Basic SQL Injection"},
            {"payload": "' UNION SELECT 1,2,3 --",
                "description": "Union-based SQLi"},
            {"payload": "'; DROP TABLE users --",
                "description": "Destructive SQLi"},
        ]

        results = []
        for test in tests:
            try:
                # This would be implemented with actual HTTP requests
                # For demo purposes, we'll simulate
                result = {
                    "vulnerability": "SQL Injection",
                    "payload": test["payload"],
                    "description": test["description"],
                    "risk": "High",
                    "remediation": "Use parameterized queries"
                }
                results.append(result)
            except Exception as e:
                logger.error(f"SQLi test failed: {e}")

        return results

    def test_xss(self, endpoint: str) -> List[Dict]:
        """Test for XSS vulnerabilities"""
        tests = [
            {"payload": "<script>alert('XSS')</script>",
             "description": "Basic XSS"},
            {"payload": "<img src=x onerror=alert('XSS')>",
             "description": "Image XSS"},
            {"payload": "javascript:alert('XSS')",
             "description": "JavaScript URI"},
        ]

        results = []
        for test in tests:
            result = {
                "vulnerability": "Cross-Site Scripting (XSS)",
                "payload": test["payload"],
                "description": test["description"],
                "risk": "Medium",
                "remediation": "Implement output encoding and Content Security Policy"
            }
            results.append(result)

        return results

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security assessment report"""
        report = {
            "scan_date": "2024-01-01",
            "target": self.base_url,
            "vulnerabilities": [],
            "summary": {
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "total": 0
            }
        }

        # Test various endpoints
        endpoints = ['/vulnerable/login',
                     '/vulnerable/search', '/vulnerable/profile/1']

        for endpoint in endpoints:
            report['vulnerabilities'].extend(self.test_sql_injection(endpoint))
            report['vulnerabilities'].extend(self.test_xss(endpoint))

        # Calculate summary
        for vuln in report['vulnerabilities']:
            if vuln['risk'] == 'High':
                report['summary']['high_risk'] += 1
            elif vuln['risk'] == 'Medium':
                report['summary']['medium_risk'] += 1
            else:
                report['summary']['low_risk'] += 1

        report['summary']['total'] = len(report['vulnerabilities'])

        return report


def demonstrate_web_security():
    """Demonstrate web security concepts"""
    print("Web Security Best Practices Demo")
    print("=" * 50)

    # Create secure database tables
    conn = sqlite3.connect('vulnerable_app.db', check_same_thread=False)
    cursor = conn.cursor()

    # Create secure users table with hashed passwords
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_secure (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensitive_data_secure (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            credit_card_encrypted TEXT,
            ssn_encrypted TEXT,
            data TEXT
        )
    ''')

    # Add secure test users
    admin_hash = bcrypt.hashpw(
        'SecureAdmin123!'.encode('utf-8'), bcrypt.gensalt())
    user_hash = bcrypt.hashpw(
        'SecureUser123!'.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("INSERT OR IGNORE INTO users_secure VALUES (1, 'admin_secure', ?, 'admin@secure.com', 'admin')",
                   (admin_hash.decode('utf-8'),))
    cursor.execute("INSERT OR IGNORE INTO users_secure VALUES (2, 'user_secure', ?, 'user@secure.com', 'user')",
                   (user_hash.decode('utf-8'),))

    # Encrypt sensitive data
    fernet = Fernet(Fernet.generate_key())
    encrypted_cc = fernet.encrypt('4111111111111111'.encode()).decode()
    encrypted_ssn = fernet.encrypt('123-45-6789'.encode()).decode()

    cursor.execute("INSERT OR IGNORE INTO sensitive_data_secure VALUES (1, 1, ?, ?, 'Confidential info')",
                   (encrypted_cc, encrypted_ssn))

    conn.commit()
    conn.close()

    print("Secure database tables created")
    print("Sample users with hashed passwords added")
    print("Encrypted sensitive data stored")

    # Demonstrate security scanner
    scanner = SecurityScanner('http://localhost:5000')
    report = scanner.generate_security_report()

    print(f"\nSecurity Scan Report:")
    print(f"Target: {report['target']}")
    print(f"High Risk Vulnerabilities: {report['summary']['high_risk']}")
    print(f"Medium Risk Vulnerabilities: {report['summary']['medium_risk']}")
    print(f"Total Vulnerabilities Found: {report['summary']['total']}")

    print(f"\nSample Vulnerabilities Found:")
    for i, vuln in enumerate(report['vulnerabilities'][:3], 1):
        print(f"{i}. {vuln['vulnerability']} - Risk: {vuln['risk']}")
        print(f"   Payload: {vuln['payload']}")
        print(f"   Remediation: {vuln['remediation']}\n")


if __name__ == '__main__':
    demonstrate_web_security()

    # Start the vulnerable/secure demo application
    app = VulnerableApp()
    print("\nStarting Web Security Demo Application...")
    print("Access the application at: http://localhost:5000")
    print("Note: This is for educational purposes only - do not use in production!")
    app.app.run(host='0.0.0.0', port=5000, debug=False)
