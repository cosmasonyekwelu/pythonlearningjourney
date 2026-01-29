# Day 42: Weekly Project – Secure Portfolio Tracker API

**Date:** November 2, 2025

## Learning Objective
To integrate all networking and security concepts learned in Week 6—Secure APIs, Encryption, Authentication, and Auditing—into a production-ready Portfolio Management API.

## Concepts Covered
- **Defense in Depth**: Layering multiple security controls (JWT, Input Validation, Encryption, Audit Logs).
- **Application Factory Pattern**: Organizing Flask apps for better testability and scalability.
- **Data Privacy**: Encrypting sensitive user secrets (like API keys) using Fernet symmetric encryption.
- **Security Auditing**: Implementing a comprehensive `AuditLog` model to track all high-risk user actions.
- **Modern JWT Flow**: Implementing both access and refresh tokens for a better user experience.

## Code Explanation
The `day_fortytwo.py` script is a high-level API implementation:
- **`InputValidator`**: A centralized class for sanitizing strings and validating financial data (symbols, quantities).
- **`DataEncryptor`**: Handles the AES encryption of third-party API keys stored in the database.
- **`Audit System`**: The `audit_log()` helper captures the IP address and User-Agent for every registration and login attempt.
- **Secure Routes**:
    - `POST /api/register`: Validates password strength and hashes it with bcrypt.
    - `POST /api/user/api-key`: Stores an encrypted string that only the user's sessions can decrypt.
    - `GET /api/user/audit-logs`: Allows users to review their own security history.

## How to Run
1. Install requirements: `pip install flask-sqlalchemy flask-bcrypt flask-jwt-extended flask-cors cryptography`
2. Start the API server:
```bash
python week_06/dayfortytwo/day_fortytwo.py
```
3. Use a tool like Postman to interact with the endpoints.

## Reflection
Building a secure API is about more than just a login page. It's about ensuring that data is safe at rest (encryption), safe in transit (HTTPS/Headers), and that every action is accountable (auditing). This project demonstrates the level of care required for financial applications.
