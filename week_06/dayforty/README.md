# Day 40: Web Security & OWASP Top 10

**Date:** October 31, 2025

## Learning Objective
To recognize and mitigate the most common web security risks identified by the OWASP Top 10 project.

## Concepts Covered
- **SQL Injection (SQLi)**: Understanding how unparameterized queries allow database takeovers.
- **Cross-Site Scripting (XSS)**: Seeing how raw user input in HTML can lead to malicious script execution.
- **IDOR (Insecure Direct Object Reference)**: Exploiting access to resources by changing IDs in the URL.
- **Broken Access Control**: Implementing role-based checks (e.g., admin vs. user).
- **Sensitive Data Exposure**: Learning to encrypt data at rest using `cryptography`.

## Code Explanation
The `day_forty.py` script is an educational laboratory containing:
- **`VulnerableApp`**: A Flask server with two parallel sets of routes:
    - `/vulnerable/...`: Demonstrates easy-to-exploit flaws (SQLi in login, XSS in search, IDOR in profile).
    - `/secure/...`: Shows the fixed versions using best practices (bcrypt hashing, parameterized SQL, HTML escaping).
- **`SecurityScanner`**: A mock utility that programmatically identifies high-risk endpoints.
- **Encryption Lab**: Uses `Fernet` (AES-based) to encrypt credit card and SSN data before storage.

## How to Run
1. Install dependencies: `pip install flask bcrypt cryptography`
2. Start the lab:
```bash
python week_06/dayforty/day_forty.py
```
3. Visit `http://localhost:5000` to interactively compare the vulnerable and secure routes.

## Reflection
The best way to defend an application is to understand how it can be attacked. Seeing an SQL injection succeed in the "Vulnerable Login" makes the importance of parameterized queries immediately obvious.
