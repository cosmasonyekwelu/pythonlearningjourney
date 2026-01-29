# Day 26: RESTful API Development

**Date:** October 17, 2025

## Learning Objective
To build a professional-grade RESTful API using Flask-RESTful, featuring JWT authentication, pagination, and CORS support.

## Concepts Covered
- **Flask-RESTful**: Using the `Resource` class to structure API endpoints.
- **JWT (JSON Web Tokens)**: implementing stateless authentication with `flask-jwt-extended`.
- **CORS (Cross-Origin Resource Sharing)**: Enabling the API to be called from different frontend domains.
- **Pagination & Filtering**: Implementing efficient data retrieval for large datasets.
- **API Versioning**: Organizing routes under `/api/v1/`.
- **Mock Data Generation**: Simulating live market data for testing.

## Code Explanation
The `day_twentysix.py` script implements a comprehensive Trading API:
- **`RegisterAPI` & `LoginAPI`**: Handle user lifecycle and issue JWT access tokens.
- **`TradeAPI`**: A robust endpoint that handles GET (with pagination), POST, PUT, and DELETE operations.
- **`PortfolioAPI`**: Performs real-time calculations to summarize a user's holdings and P&L.
- **`MarketDataAPI`**: Generates randomized stock prices to demonstrate API responses without requiring an external subscription.
- **`CLI Commands`**: Custom Flask commands (`init-db`, `create-sample-data`) for easy environment setup.

## How to Run
1. Install dependencies: `pip install flask-restful flask-sqlalchemy flask-jwt-extended flask-cors`
2. Initialize the database: `flask --app day_twentysix init-db`
3. Run the server:
```bash
python week_04/daytwentysix/day_twentysix.py
```
4. Access the health check at `http://localhost:5000/api/health`.

## Reflection
Building a clean API requires more than just returning JSON. It involves careful consideration of security (JWT), ease of use (clear status codes), and performance (pagination).
