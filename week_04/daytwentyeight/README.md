# Day 28: Weekly Project – Web Frameworks & Backend Summary

**Date:** October 19, 2025

## Learning Objective
To consolidate all backend development skills acquired during the week—Flask, SQLAlchemy, authentication, and external APIs—into a single, production-ready Portfolio Tracker.

## Concepts Covered
- **Comprehensive Integration**: Combining database models, user auth, and API calls.
- **Relational Mapping**: Linking Users, Trades, and Portfolios in a cohesive SQL schema.
- **Custom Template Filters**: Creating reusable Jinja2 filters for currency and date formatting.
- **Third-Party APIs**: Fetching live cryptocurrency prices from the CoinGecko API.
- **Error Handling**: Implementing custom 404 and 500 error pages.

## Code Explanation
The `day_twentyeight.py` script serves as the "grand finale" of the web framework week:
- **`User`, `Trade`, `Portfolio` Models**: A complete normalized database schema.
- **`@app.template_filter`**: Custom filters like `format_currency` make the frontend code cleaner.
- **`get_crypto_prices()`**: An API endpoint that acts as a proxy to CoinGecko, bringing real-time data into the dashboard.
- **`init_db()`**: Automatically seeds the database with a test user and sample trades upon first run.

## How to Run
1. Install dependencies: `pip install flask flask-sqlalchemy flask-login requests`
2. Run the application:
```bash
python week_04/daytwentyeight/day_twentyeight.py
```
3. Register a new account at `http://localhost:5000/register` to start tracking your simulated trades.

## Reflection
Building a full-stack application from scratch reveals how all the individual pieces—databases, routing, security, and external data—fit together. This project serves as a solid foundation for any commercial web application.
