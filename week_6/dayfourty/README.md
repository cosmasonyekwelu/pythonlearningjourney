# Day 40: Web Security Best Practices & OWASP Top 10

## Overview

This module provides hands-on experience with web application security vulnerabilities and their remediation. You'll learn to identify, exploit, and fix common security issues following the OWASP Top 10 framework.

## Learning Objectives

- Understand and identify OWASP Top 10 web security risks
- Exploit SQL Injection and XSS vulnerabilities in controlled environments
- Implement proper input validation and output encoding
- Apply security headers and Content Security Policy (CSP)
- Conduct basic security testing and vulnerability assessment
- Implement proper authentication and authorization controls

## OWASP Top 10 Coverage

### A01: Broken Access Control

- Insecure Direct Object References (IDOR)
- Missing Function Level Access Control
- Privilege escalation vulnerabilities
- CORS misconfigurations

### A02: Cryptographic Failures

- Sensitive data exposure
- Weak encryption algorithms
- Insecure key management
- Missing TLS/SSL enforcement

### A03: Injection

- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Command Injection
- NoSQL Injection

### A04: Insecure Design

- Missing security controls
- Insecure workflows
- Lack of threat modeling

### A05: Security Misconfiguration

- Unnecessary features enabled
- Default credentials in use
- Verbose error messages
- Outdated software components

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Dependencies Installation

```bash
pip install -r requirements.txt
```

### Required Packages

```bash
pip install flask bcrypt cryptography email-validator
```

## Running the Application

### Start the Demo Server

```bash
python day40_web_security.py
```

### Access the Application

Open your web browser and navigate to: `http://localhost:5000`

## Application Features

### Vulnerable Endpoints

- `/vulnerable/login` - SQL Injection demonstration
- `/vulnerable/search` - XSS and SQL Injection vulnerabilities
- `/vulnerable/profile/<user_id>` - Broken Access Control (IDOR)
- `/vulnerable/transfer` - Missing CSRF protection

### Secure Endpoints

- `/secure/login` - Parameterized queries and password hashing
- `/secure/search` - Input validation and output encoding
- `/secure/profile/<user_id>` - Proper authorization checks
- `/secure/transfer` - CSRF token validation

### Demonstration Routes

- `/demo/sql-injection` - SQL Injection examples and fixes
- `/demo/xss` - XSS vulnerability demonstrations
- `/demo/access-control` - Broken access control examples

## Hands-On Exercises

### Exercise 1: SQL Injection Testing

```bash
# Test basic SQL injection
curl -X POST http://localhost:5000/vulnerable/login \
  -d "username=' OR '1'='1' --&password=anything"

# Test union-based SQL injection
curl "http://localhost:5000/vulnerable/search?q=' UNION SELECT 1,2,3 --"
```

### Exercise 2: XSS Testing

```bash
# Test reflected XSS
curl "http://localhost:5000/vulnerable/search?q=<script>alert('XSS')</script>"

# Test image-based XSS
curl "http://localhost:5000/vulnerable/search?q=<img src=x onerror=alert(1)>"
```

### Exercise 3: Broken Access Control Testing

```bash
# Test IDOR by changing user IDs
curl "http://localhost:5000/vulnerable/profile/1"
curl "http://localhost:5000/vulnerable/profile/2"
curl "http://localhost:5000/vulnerable/profile/999"
```

## Security Implementation Examples

### 1. SQL Injection Prevention

```python
# Vulnerable approach (DON'T USE)
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

# Secure approach (USE THIS)
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password_hash))
```

### 2. XSS Prevention

```python
# Vulnerable approach (DON'T USE)
return f"<div>Welcome {user_input}</div>"

# Secure approach - HTML escaping (USE THIS)
from flask import escape
return f"<div>Welcome {escape(user_input)}</div>"

# Secure approach - Template auto-escaping
return render_template('profile.html', username=username)
```

### 3. Access Control Implementation

```python
# Vulnerable approach (DON'T USE)
@app.route('/user/<user_id>')
def get_user(user_id):
    return User.query.get(user_id)  # No authorization check

# Secure approach (USE THIS)
@app.route('/user/<user_id>')
@login_required
def get_user(user_id):
    if current_user.id != int(user_id) and not current_user.is_admin:
        abort(403)  # Forbidden
    return User.query.get(user_id)
```

### 4. Input Validation

```python
import re

def validate_email(email):
    """Comprehensive email validation"""
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Invalid email format")

    if len(email) > 254:
        raise ValueError("Email address too long")

    return email.lower().strip()

def validate_password(password):
    """Strong password validation"""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])', password):
        raise ValueError("Password must contain uppercase, lowercase, number and special character")

    return password
```

### 5. Security Headers Implementation

```python
@app.after_request
def set_security_headers(response):
    """Apply security headers to all responses"""
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Security Testing Commands

### Manual Security Testing

```bash
# SQL Injection payloads to test
"' OR '1'='1' --"
"admin' --"
"'; DROP TABLE users --"
"' UNION SELECT username, password FROM users --"

# XSS payloads to test
"<script>alert('XSS')</script>"
"<img src=x onerror=alert('XSS')>"
"javascript:alert('XSS')"
"<svg onload=alert('XSS')>"

# IDOR testing techniques
# Change numeric IDs: /user/123 -> /user/124
# Change UUIDs: /file/abc-123 -> /file/def-456
# Test parameter manipulation
```

### Automated Security Headers Check

```python
import requests

def check_security_headers(url):
    response = requests.get(url)
    headers = response.headers

    security_headers = [
        'Content-Security-Policy',
        'Strict-Transport-Security',
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection'
    ]

    for header in security_headers:
        if header in headers:
            print(f"PASS: {header}: {headers[header]}")
        else:
            print(f"FAIL: {header} header missing")
```

## Security Best Practices Checklist

### Input Validation

- [ ] Validate all user inputs on server side
- [ ] Use whitelist validation where possible
- [ ] Implement proper data type checking
- [ ] Set reasonable length limits on all inputs
- [ ] Sanitize file uploads and check file types

### Authentication & Authorization

- [ ] Use strong password hashing (bcrypt, scrypt)
- [ ] Implement proper session management
- [ ] Use multi-factor authentication for sensitive operations
- [ ] Implement proper logout functionality
- [ ] Regular password rotation policies

### Data Protection

- [ ] Encrypt sensitive data at rest
- [ ] Use HTTPS for all communications
- [ ] Implement proper key management
- [ ] Secure database credentials
- [ ] Regular security patches and updates

### Security Headers

- [ ] Implement Content Security Policy (CSP)
- [ ] Enable HTTP Strict Transport Security (HSTS)
- [ ] Set X-Content-Type-Options header
- [ ] Configure X-Frame-Options header
- [ ] Use X-XSS-Protection header

## Common Vulnerabilities and Fixes

### SQL Injection

**Problem**: User input directly concatenated into SQL queries

```python
# Vulnerable
query = f"SELECT * FROM users WHERE email = '{email}'"
```

**Solution**: Use parameterized queries

```python
# Secure
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))
```

### Cross-Site Scripting (XSS)

**Problem**: User input rendered without escaping

```python
# Vulnerable
return f"<div>Hello {user_input}</div>"
```

**Solution**: Always escape user input

```python
# Secure
return f"<div>Hello {html.escape(user_input)}</div>"
```

### Insecure Direct Object References (IDOR)

**Problem**: No authorization checks on object access

```python
# Vulnerable
@app.route('/documents/<document_id>')
def get_document(document_id):
    return Document.query.get(document_id)
```

**Solution**: Implement proper authorization

```python
# Secure
@app.route('/documents/<document_id>')
@login_required
def get_document(document_id):
    document = Document.query.get(document_id)
    if document.owner_id != current_user.id:
        abort(403)
    return document
```

## Learning Outcomes

After completing this module, you should be able to:

1. Identify common web application vulnerabilities
2. Implement proper input validation and sanitization
3. Apply security headers and Content Security Policy
4. Use parameterized queries to prevent SQL injection
5. Implement proper authentication and authorization
6. Conduct basic security testing and assessment
7. Understand and apply OWASP security guidelines

## Next Steps

Continue your security learning journey with:

- **Day 41**: Network Scanning & Monitoring
- **Advanced Web Security**: CSRF protection, session security
- **Security Testing**: OWASP ZAP, Burp Suite usage
- **Secure Development Lifecycle**: Integrating security into development processes

## Important Notes

- This application is for educational purposes only
- Never test security vulnerabilities on systems without explicit permission
- Always follow responsible disclosure practices
- Keep security dependencies updated regularly
- Implement proper logging and monitoring in production

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in the application or stop other services using port 5000
2. **Database errors**: Delete the vulnerable_app.db file to reset the database
3. **Import errors**: Ensure all dependencies are installed correctly
4. **Permission errors**: Run with appropriate permissions for your operating system

### Getting Help

- Check the application logs for detailed error messages
- Verify all dependencies are installed and up to date
- Ensure you're using a supported Python version (3.8+)
- Consult the OWASP documentation for additional guidance

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- Flask Security Documentation: https://flask.palletsprojects.com/en/security/
- Python Security Best Practices: https://docs.python.org/3/library/security.html

This module provides practical experience with web application security fundamentals. Remember that security is an ongoing process requiring continuous learning and vigilance.

```

```
