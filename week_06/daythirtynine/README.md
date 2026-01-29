# Day 39: Authentication Protocols

**Date:** October 30, 2025

## Learning Objective
To understand and implement various industry-standard authentication protocols, ranging from traditional sessions to modern JWT and OAuth 2.0 flows.

## Concepts Covered
- **JWT (JSON Web Tokens)**: Building stateless authentication with access and refresh tokens.
- **Session-Based Auth**: Managing user state on the server using unique session IDs.
- **API Key Authentication**: Creating and validating hashed secret keys for third-party integrations.
- **MFA (Multi-Factor Authentication)**: Implementing Time-based One-Time Passwords (TOTP).
- **OAuth 2.0 Client**: Understanding the authorization code grant flow.

## Code Explanation
The `day_thirtynine.py` script contains specialized managers for each protocol:
- **`JWTAuthManager`**: Uses the `PyJWT` library to sign and verify payloads with expiration times.
- **`APIKeyAuthManager`**: Demonstrates the "sk_..." prefix pattern and stores keys as hashes to prevent leaks from database dumps.
- **`MFAManager`**: Shows how to generate secrets and verify TOTP codes (simplified version).
- **`SecureAPIAuthenticator`**: A "multiplexer" class that can authenticate a single request using JWT, API Key, or Session headers.

## How to Run
1. Install dependencies: `pip install PyJWT cryptography bcrypt`
2. Run the authentication protocol demos:
```bash
python week_06/daythirtynine/day_thirtynine.py
```

## Reflection
Authentication is about trust. While sessions are great for simple web apps, JWTs offer better scalability for microservices, and API keys are the standard for developer interfaces. Implementing MFA is the single best way to protect users from credential theft.
