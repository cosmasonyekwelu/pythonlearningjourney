# Day 42: Secure Portfolio Tracker

A fully functional, security-hardened portfolio tracking application that integrates all security concepts from the week.

## Features

### Security Features

- **JWT Authentication** - Stateless token-based authentication
- **Password Hashing** - bcrypt with salt for secure password storage
- **Input Validation & Sanitization** - Comprehensive validation for all user inputs
- **Data Encryption** - Fernet encryption for sensitive API keys
- **Security Headers** - CSP, HSTS, XSS protection, and more
- **Audit Logging** - Track all security events and user actions
- **SQL Injection Prevention** - ORM-based queries with parameterization

### Portfolio Management

- Create and manage multiple portfolios
- Add stock holdings with symbols, quantities, and prices
- Track portfolio performance
- Secure API for all operations

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone and setup environment**:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Generate encryption key**:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

3. **Run the application**:

```bash
python day_fortytwo.py
```

The application will start on `http://localhost:5000`

### Environment Variables

Create a `.env` file with:

```bash
SECRET_KEY=your-flask-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key
DATABASE_URL=sqlite:///portfolio.db
```

## API Endpoints

### Authentication

- `POST /api/register` - Register new user
- `POST /api/login` - User login (returns JWT tokens)
- `POST /api/refresh` - Refresh access token

### Portfolios

- `GET /api/portfolios` - Get user portfolios (JWT required)
- `POST /api/portfolios` - Create new portfolio (JWT required)
- `POST /api/portfolios/<id>/holdings` - Add holding to portfolio (JWT required)

### Security

- `POST /api/user/api-key` - Set encrypted API key (JWT required)
- `GET /api/user/api-key` - Check API key status (JWT required)
- `GET /api/user/audit-logs` - Get user audit logs (JWT required)

### System

- `GET /api/health` - Health check

## Security Implementation

### 1. Secure Authentication

- **JWT Tokens**: Access tokens (1hr expiry) and refresh tokens (30 days)
- **Password Security**: bcrypt hashing with work factor 12
- **Token Refresh**: Secure token rotation mechanism

### 2. Hardened API

- **Input Validation**: Email format, password strength, stock symbols
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Input sanitization and CSP headers
- **CORS Configuration**: Restricted origins with credential support

### 3. Data Encryption

- **Encrypted Storage**: API keys encrypted using Fernet (symmetric encryption)
- **Key Management**: Environment variable configuration
- **Secure Transmission**: All data encrypted in transit

### 4. Security Headers

- **HSTS**: HTTP Strict Transport Security
- **CSP**: Content Security Policy
- **XSS Protection**: Browser XSS filtering
- **Frame Options**: Clickjacking protection
- **Content Type**: MIME sniffing prevention

### 5. Audit Logging

- **Authentication Events**: Successful/failed logins
- **User Actions**: Portfolio creation, trade additions
- **Large Trades**: Transactions over $10,000 threshold
- **Security Events**: API key updates, system access

## Example Usage

### 1. Register User

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

### 3. Create Portfolio (with JWT)

```bash
curl -X POST http://localhost:5000/api/portfolios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"name": "Tech Stocks", "description": "Technology sector investments"}'
```

### 4. Add Holding

```bash
curl -X POST http://localhost:5000/api/portfolios/1/holdings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"symbol": "AAPL", "quantity": 10, "average_price": 150.50}'
```

### 5. Set API Key

```bash
curl -X POST http://localhost:5000/api/user/api-key \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"api_key": "your-stock-data-api-key"}'
```

## Security Testing

### Input Validation Tests

- Try invalid email formats
- Test weak passwords
- Attempt SQL injection in inputs
- Test XSS payloads in string fields

### Authentication Tests

- Attempt access without JWT token
- Test token expiration
- Verify refresh token mechanism
- Check audit logging for failed attempts

### Encryption Verification

- Confirm API keys are encrypted in database
- Verify decryption only works with correct key
- Test data integrity after encryption/decryption

## Database Schema

- **users**: User accounts with hashed passwords
- **portfolios**: User portfolio containers
- **holdings**: Stock positions within portfolios
- **user_secrets**: Encrypted API keys
- **audit_logs**: Security and action tracking

## Monitoring

The application includes comprehensive logging:

- Application logs with timestamps and levels
- Security event tracking in database
- Error logging with stack traces
- Performance metrics for API endpoints

## Production Deployment

For production use:

1. Set strong secret keys in environment variables
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS with valid certificates
4. Set up reverse proxy (nginx)
5. Configure proper firewall rules
6. Implement rate limiting
7. Set up monitoring and alerting
8. Regular security updates and patches

## Security Best Practices Implemented

- Principle of Least Privilege
- Defense in Depth
- Fail Securely
- Security by Design
- Continuous Monitoring
- Input Validation
- Secure Defaults
- Comprehensive Logging

---

_This application demonstrates enterprise-grade security practices suitable for production financial applications._

```

## Key Security Features Demonstrated

This implementation includes:

1. **JWT Authentication** with secure token management
2. **bcrypt password hashing** with proper salt
3. **Comprehensive input validation** for all user inputs
4. **Fernet encryption** for sensitive API keys
5. **Security headers** including CSP and HSTS
6. **Audit logging** for all security events
7. **SQL injection prevention** through ORM usage
8. **XSS protection** via input sanitization and CSP
9. **Error handling** without information disclosure
10. **CORS configuration** for secure cross-origin requests

The application is production-ready and demonstrates all the required security concepts in a practical, functional portfolio tracker.
```
