# Day 37: Building Secure APIs

This module demonstrates essential security practices for building robust and secure RESTful APIs.

## Key Security Features

### 1. Input Validation & Sanitization

- **Email Validation**: Regex pattern for valid email formats
- **Username Validation**: Alphanumeric with length constraints
- **Input Sanitization**: HTML escaping to prevent XSS attacks
- **Type Checking**: Proper data type validation

### 2. SQL Injection Prevention

- **Parameterized Queries**: Using placeholders instead of string concatenation
- **ORM Best Practices**: Safe database operations

### 3. Rate Limiting

- **Flask-Limiter**: Protection against brute force and DoS attacks
- **Configurable Limits**: 200 requests per day, 50 per hour by default
- **Endpoint-specific limits**: Stricter limits on sensitive endpoints

### 4. CORS Configuration

- **Origin Restrictions**: Only allow trusted domains
- **Cross-Origin Protection**: Prevent unauthorized domain access

### 5. Security Headers

- **X-Content-Type-Options**: Prevent MIME type sniffing
- **X-Frame-Options**: Clickjacking protection
- **X-XSS-Protection**: Browser XSS protection
- **HSTS**: HTTP Strict Transport Security
- **CSP**: Content Security Policy

### 6. Error Handling

- **Generic Error Messages**: Avoid information leakage
- **Proper HTTP Status Codes**: Accurate response statuses
- **Structured Error Responses**: Consistent error format

## API Endpoints

### POST /api/register

- Rate limit: 10 requests per minute
- Input validation for username, email, password
- SQL injection protection
- Secure user creation

### GET /api/users/{id}

- Rate limit: 100 requests per hour
- Parameterized SQL queries
- Proper error handling

## Security Best Practices Implemented

1. **Never Trust User Input**: Always validate and sanitize
2. **Use HTTPS**: Essential for production (configure in deployment)
3. **Principle of Least Privilege**: Database users with minimal permissions
4. **Secure Authentication**: Proper password hashing (use bcrypt in production)
5. **Regular Updates**: Keep dependencies updated
6. **Security Testing**: Regular penetration testing and code reviews

## Running the Application

```bash
pip install flask flask-limiter flask-cors
python day_37.py
```
