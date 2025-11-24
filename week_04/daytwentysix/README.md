# Day 26: API Development

A complete RESTful API implementation for a trading platform with user authentication, trade management, portfolio tracking, and market data.

## Features

- User Authentication: JWT-based registration and login
- Trade Management: Full CRUD operations for trades
- Portfolio Tracking: Real-time portfolio summary with P&L
- Market Data: Real-time (mock) market data
- Pagination and Filtering: Efficient data retrieval
- Error Handling: Comprehensive error responses
- CORS Support: Cross-origin resource sharing

## Tech Stack

- Backend: Flask, Flask-RESTful, SQLAlchemy
- Authentication: JWT (JSON Web Tokens)
- Database: SQLite (with SQLAlchemy ORM)
- Security: Password hashing, JWT tokens
- Documentation: OpenAPI/Swagger compatible

## Installation and Setup

1. Install dependencies:

```bash
pip install flask flask-restful flask-sqlalchemy flask-jwt-extended flask-cors
```

2. Initialize the database:

```bash
python day_twentysix.py
```

This will automatically create the database tables.

3. Run the application:

```bash
python day_twentysix.py
```

Or using Flask CLI:

```bash
flask --app day_twentysix run --port 5000 --debug
```

## API Endpoints

### Authentication

- POST /api/register – Register new user
- POST /api/login – User login

### Trades (Require JWT Authentication)

- GET /api/trades – Get all trades (with pagination/filtering)
- POST /api/trades – Create new trade
- GET /api/trades/<id> – Get specific trade
- PUT /api/trades/<id> – Update trade
- DELETE /api/trades/<id> – Delete trade

### Portfolio and Market Data

- GET /api/portfolio – Get user portfolio summary
- GET /api/market-data – Get market data
- GET /api/health – Health check

## Usage Examples

### 1. User Registration

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword"
  }'
```

### 3. Create Trade (with JWT)

```bash
curl -X POST http://localhost:5000/api/trades \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "symbol": "AAPL",
    "quantity": 10,
    "price": 150.50,
    "trade_type": "BUY"
  }'
```

### 4. Get Trades with Pagination

```bash
curl -X GET "http://localhost:5000/api/trades?page=1&per_page=5&symbol=AAPL" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Get Portfolio Summary

```bash
curl -X GET http://localhost:5000/api/portfolio \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 6. Get Market Data

```bash
curl -X GET "http://localhost:5000/api/market-data?symbols=AAPL,GOOGL,MSFT"
```

## Database Models

### User Model

- id: Primary key
- username: Unique username
- email: Unique email
- password: Hashed password
- created_at: Account creation timestamp

### Trade Model

- id: Primary key
- symbol: Stock symbol (e.g., AAPL)
- quantity: Number of shares
- price: Trade price per share
- trade_type: BUY or SELL
- timestamp: Trade timestamp
- user_id: Foreign key to User

## Query Parameters

### Trades Endpoint

- page: Page number (default: 1)
- per_page: Items per page (default: 10)
- symbol: Filter by symbol
- trade_type: Filter by trade type (BUY/SELL)

### Market Data Endpoint

- symbols: Comma-separated list of symbols

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized (authentication required)
- 404: Not Found
- 500: Internal Server Error

## Security Notes

Important Security Considerations:

1. Passwords: Currently stored in plain text. In production, use proper hashing (bcrypt, Argon2).
2. JWT Secret: Change the JWT secret key in production.
3. HTTPS: Always use HTTPS in production.
4. Input Validation: Implement comprehensive input validation.
5. Rate Limiting: Add rate limiting to prevent abuse.

## Sample Data

Create sample data using the CLI command:

```bash
flask --app day_twentysix create-sample-data
```

This creates:

- Demo user: demo / password
- Sample trades for popular stocks

## Testing with Postman

Import the following collection:

```json
{
  "info": {
    "name": "Trading API",
    "description": "Day 26 Trading API Collection"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/health"
      }
    },
    {
      "name": "Register User",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/register",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"email\": \"test@example.com\",\n  \"password\": \"password\"\n}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/login",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"password\": \"password\"\n}"
        }
      }
    }
  ]
}
```

## Learning Objectives Covered

- REST API principles and CRUD architecture
- Flask RESTful setup and configuration
- Serializers and data validation
- JWT authentication implementation
- Pagination and filtering
- API testing preparation
- Database models and relationships
- Error handling and response formatting

## Next Steps

1. Add proper password hashing
2. Implement unit tests
3. Add API documentation with Swagger
4. Implement real market data integration
5. Add WebSocket support for real-time updates
6. Implement rate limiting
7. Add database migrations

## Common Issues and Solutions

1. Port already in use: Change port with `--port 5001`
2. Database errors: Delete `trading.db` and reinitialize
3. Import errors: Ensure all dependencies are installed
4. JWT errors: Check token expiration and secret key

## Contributing

You can extend this API with additional features such as:

- Real market data integration
- Advanced portfolio analytics
- Order types (limit, stop-loss)
- Multi-currency support
- WebSocket real-time updates

## How to Run

1. Save both files in the same directory.
2. Install dependencies:

```bash
pip install flask flask-restful flask-sqlalchemy flask-jwt-extended flask-cors
```

3. Run the application:

```bash
python day_twentysix.py
```

4. Access the API at [http://localhost:5000](http://localhost:5000)
5. Test endpoints using the provided curl commands or Postman.

The API provides a complete trading platform with user management, trade operations, portfolio tracking, and market data. It is an excellent foundation for learning REST API development.
