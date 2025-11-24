"""
Day 40: Web Security Best Practices & OWASP Top 10
Demonstration app: intentionally vulnerable and secure implementations
"""

import sqlite3
import html
import re
import secrets
import bcrypt
from typing import Dict, List
from cryptography.fernet import Fernet
from flask import Flask, request, session, render_template_string
import logging

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------- APP CLASS ----------------
class VulnerableApp:
    """Flask app with vulnerable and secure routes demonstrating OWASP Top 10 issues"""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "demo-secret-key-change-in-prod"
        self.conn = sqlite3.connect(
            "vulnerable_app.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Encryption setup
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

        self.setup_database()
        self.setup_routes()

    # ---------- DATABASE SETUP ----------
    def setup_database(self):
        """Initialize both vulnerable and secure tables."""
        try:
            # Vulnerable tables
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT,
                role TEXT DEFAULT 'user'
            )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                author TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS sensitive_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                credit_card TEXT,
                ssn TEXT,
                data TEXT
            )''')

            # Secure tables
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users_secure (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                role TEXT DEFAULT 'user'
            )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS sensitive_data_secure (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                credit_card_encrypted TEXT,
                ssn_encrypted TEXT,
                data TEXT
            )''')

            # Insert test data if not exists
            self.cursor.execute(
                "INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 'admin')")
            self.cursor.execute(
                "INSERT OR IGNORE INTO users VALUES (2, 'user1', 'password123', 'user1@example.com', 'user')")
            self.cursor.execute(
                "INSERT OR IGNORE INTO sensitive_data VALUES (1, 1, '4111111111111111', '123-45-6789', 'Confidential info')"
            )

            # Secure entries
            admin_pw = bcrypt.hashpw(
                b"SecureAdmin123!", bcrypt.gensalt()).decode()
            user_pw = bcrypt.hashpw(
                b"SecureUser123!", bcrypt.gensalt()).decode()

            self.cursor.execute("INSERT OR IGNORE INTO users_secure VALUES (1, 'admin_secure', ?, 'admin@secure.com', 'admin')",
                                (admin_pw,))
            self.cursor.execute("INSERT OR IGNORE INTO users_secure VALUES (2, 'user_secure', ?, 'user@secure.com', 'user')",
                                (user_pw,))

            enc_cc = self.fernet.encrypt(b"4111111111111111").decode()
            enc_ssn = self.fernet.encrypt(b"123-45-6789").decode()

            self.cursor.execute("INSERT OR IGNORE INTO sensitive_data_secure VALUES (1, 1, ?, ?, 'Confidential info')",
                                (enc_cc, enc_ssn))

            self.conn.commit()
        except Exception as e:
            logger.error(f"Database setup failed: {e}")

    # ---------- ROUTES ----------
    def setup_routes(self):
        app = self.app

        # ---------------- Vulnerable routes ----------------
        @app.route("/vulnerable/login", methods=["GET", "POST"])
        def vulnerable_login():
            """Vulnerable login: SQL injection"""
            if request.method == "POST":
                username = request.form.get("username", "")
                password = request.form.get("password", "")

                query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
                logger.warning(f"VULNERABLE QUERY: {query}")
                try:
                    self.cursor.execute(query)
                    user = self.cursor.fetchone()
                    if user:
                        session["user_id"] = user[0]
                        session["username"] = user[1]
                        session["role"] = user[4]
                        return f"Welcome {user[1]}! Role: {user[4]}"
                    return "Invalid credentials"
                except Exception as e:
                    return f"DB Error: {e}"

            return render_template_string("""
                <h3>Vulnerable Login</h3>
                <form method="POST">
                  <input name="username" placeholder="Username">
                  <input name="password" placeholder="Password" type="password">
                  <button>Login</button>
                </form>
                <p>Try SQL Injection: <code>' OR '1'='1' --</code></p>
            """)

        @app.route("/vulnerable/search")
        def vulnerable_search():
            """Vulnerable search: XSS + SQLi"""
            q = request.args.get("q", "")
            result_html = f"<h3>Search results for: {q}</h3>"
            if q:
                sql = f"SELECT * FROM posts WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'"
                self.cursor.execute(sql)
                posts = self.cursor.fetchall()
                for p in posts:
                    result_html += f"<div><h4>{p[1]}</h4><p>{p[2]}</p></div>"

            return f"""
                <h2>Vulnerable Search</h2>
                <form><input name='q' value='{q}'><button>Search</button></form>
                {result_html}
                <p>Try XSS: &lt;script&gt;alert('XSS')&lt;/script&gt;</p>
            """

        @app.route("/vulnerable/profile/<user_id>")
        def vulnerable_profile(user_id):
            """Vulnerable profile: IDOR"""
            try:
                self.cursor.execute(f"SELECT * FROM users WHERE id={user_id}")
                user = self.cursor.fetchone()
                if not user:
                    return "User not found"
                self.cursor.execute(
                    f"SELECT * FROM sensitive_data WHERE user_id={user_id}")
                sensitive = self.cursor.fetchone()
                return f"""
                <h3>Profile of {user[1]}</h3>
                <p>Email: {user[3]}</p>
                <p>Credit Card: {sensitive[2] if sensitive else 'None'}</p>
                <p>SSN: {sensitive[3] if sensitive else 'None'}</p>
                """
            except Exception as e:
                return f"Error: {e}"

        # ---------------- Secure routes ----------------
        @app.route("/secure/login", methods=["GET", "POST"])
        def secure_login():
            if request.method == "POST":
                username = request.form.get("username", "")
                password = request.form.get("password", "")
                query = "SELECT * FROM users_secure WHERE username=?"
                self.cursor.execute(query, (username,))
                user = self.cursor.fetchone()

                if user and bcrypt.checkpw(password.encode(), user[2].encode()):
                    session["user_id"] = user[0]
                    session["username"] = user[1]
                    session["role"] = user[4]
                    session["csrf_token"] = secrets.token_urlsafe(32)
                    return f"Welcome {html.escape(user[1])}! Role: {user[4]}"
                return "Invalid credentials"

            return render_template_string("""
                <h3>Secure Login</h3>
                <form method="POST">
                  <input name="username" required placeholder="Username">
                  <input name="password" type="password" required placeholder="Password">
                  <button>Login</button>
                </form>
            """)

        @app.route("/secure/search")
        def secure_search():
            q = request.args.get("q", "")
            if not re.match(r"^[\w\s]{0,50}$", q):
                return "Invalid input"
            safe_q = html.escape(q)
            result_html = f"<h3>Results for: {safe_q}</h3>"
            sql = "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?"
            self.cursor.execute(sql, (f"%{q}%", f"%{q}%"))
            for post in self.cursor.fetchall():
                result_html += f"<div><h4>{html.escape(post[1])}</h4><p>{html.escape(post[2])}</p></div>"
            return result_html

        @app.route("/secure/profile/<int:user_id>")
        def secure_profile(user_id):
            if "user_id" not in session:
                return "Please login"
            if session["user_id"] != user_id and session["role"] != "admin":
                return "Access denied"

            self.cursor.execute(
                "SELECT * FROM sensitive_data_secure WHERE user_id=?", (user_id,))
            row = self.cursor.fetchone()
            if not row:
                return "No secure data found"

            dec_cc = self.fernet.decrypt(row[2].encode()).decode()
            dec_ssn = self.fernet.decrypt(row[3].encode()).decode()

            return f"""
            <h3>Secure Profile #{user_id}</h3>
            <p>Decrypted Credit Card: {dec_cc}</p>
            <p>Decrypted SSN: {dec_ssn}</p>
            """

        @app.route("/")
        def index():
            return render_template_string("""
            <h1>Web Security Demo</h1>
            <p>Demonstrating OWASP Top 10 Vulnerabilities & Fixes</p>
            <ul>
              <li><a href="/vulnerable/login">Vulnerable Login (SQLi)</a></li>
              <li><a href="/vulnerable/search">Vulnerable Search (XSS)</a></li>
              <li><a href="/vulnerable/profile/1">Vulnerable Profile (IDOR)</a></li>
              <li><a href="/secure/login">Secure Login</a></li>
              <li><a href="/secure/search">Secure Search</a></li>
              <li><a href="/secure/profile/1">Secure Profile</a></li>
            </ul>
            """)


# ---------------- SECURITY SCANNER ----------------
class SecurityScanner:
    """Mock scanner to demonstrate vulnerabilities programmatically"""

    def __init__(self, target: str):
        self.target = target

    def generate_security_report(self) -> Dict:
        vulns: List[Dict] = [
            {"vulnerability": "SQL Injection",
                "endpoint": "/vulnerable/login", "risk": "High"},
            {"vulnerability": "Cross-Site Scripting (XSS)",
             "endpoint": "/vulnerable/search", "risk": "Medium"},
            {"vulnerability": "Broken Access Control (IDOR)",
             "endpoint": "/vulnerable/profile/1", "risk": "High"},
        ]
        summary = {"high_risk": sum(1 for v in vulns if v["risk"] == "High"),
                   "medium_risk": sum(1 for v in vulns if v["risk"] == "Medium"),
                   "total": len(vulns)}
        return {"target": self.target, "vulnerabilities": vulns, "summary": summary}


# ---------------- MAIN DEMO ----------------
def demonstrate_web_security():
    print("Initializing Secure Tables & Data...")
    conn = sqlite3.connect("vulnerable_app.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users_secure")
    print("✔ Secure tables ready.")
    conn.close()

    scanner = SecurityScanner("http://localhost:5000")
    report = scanner.generate_security_report()
    print("\nSecurity Scan Summary:")
    print(report["summary"])
    print("\nSample vulnerabilities:")
    for v in report["vulnerabilities"]:
        print(f"- {v['vulnerability']} ({v['risk']}) at {v['endpoint']}")


if __name__ == "__main__":
    demonstrate_web_security()

    app_instance = VulnerableApp()
    print("\n Starting Web Security Demo at http://localhost:5000")
    print("For educational use only — not production safe.")
    app_instance.app.run(host="0.0.0.0", port=5000, debug=False)
