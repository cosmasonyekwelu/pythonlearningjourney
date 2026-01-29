# Day 37: Building Secure APIs

**Date:** October 28, 2025

## Learning Objective
To implement essential security patterns in Flask-based REST APIs, protecting against common web vulnerabilities like XSS and SQL injection.

## Concepts Covered
- **Input Sanitization**: Using `html.escape` to prevent Cross-Site Scripting (XSS).
- **Parameterized Queries**: Using SQLite's placeholder syntax to prevent SQL Injection.
- **Rate Limiting**: Using `flask-limiter` to protect against Brute Force and DoS attacks.
- **CORS (Cross-Origin Resource Sharing)**: Configuring trusted origins to prevent unauthorized cross-site requests.
- **Security Headers**: Setting HSTS, CSP, and X-Frame-Options to harden the application.

## Code Explanation
The `day_thirtyseven.py` script implements a "Security-First" User API:
- **`validate_email` & `validate_username`**: Strict regex checks ensure inputs meet expected formats before processing.
- **`limiter`**: Configured with both default and route-specific limits (e.g., only 10 registrations per minute).
- **`set_security_headers`**: A decorator that automatically adds 5+ defensive HTTP headers to every response.
- **`sqlite3` context manager**: Demonstrates safe database handling using parameterized values `(?, ?, ?)`.

## How to Run
1. Install dependencies: `pip install flask-limiter flask-cors`
2. Run the secure API:
```bash
python week_06/daythirtyseven/day_thirtyseven.py
```
3. Test the rate limiting by making multiple requests to `/api/register`.

## Reflection
Security is not a feature; it's a foundation. Building an API with security from day one—like implementing rate limits and CSP headers—is much more effective than trying to patch vulnerabilities after deployment.
