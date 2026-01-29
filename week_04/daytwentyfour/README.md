# Day 24: Database Design (SQL & NoSQL)

**Date:** October 15, 2025

## Learning Objective
To understand the differences between relational (SQL) and non-relational (NoSQL) databases and implement a hybrid data architecture using Flask.

## Concepts Covered
- **Relational Databases (SQL)**: Using PostgreSQL with SQLAlchemy to manage structured data (Users, Portfolios, Transactions).
- **NoSQL Databases**: Using MongoDB (via `pymongo`) for unstructured logging and activity tracking.
- **ORM (Object-Relational Mapping)**: Defining relationships like `ForeignKey` and `backref` in SQLAlchemy.
- **Hybrid Architectures**: Knowing when to use SQL for consistency and NoSQL for scalability/flexibility.
- **RESTful API CRUD**: Implementing Create and Read operations for multiple database resources.

## Code Explanation
The `day_twentyfour.py` script implements a Portfolio Tracker API:
- **`SQLAlchemy Models`**: Defines the relational schema with `User`, `Portfolio`, `Asset`, and `Transaction` tables.
- **`MongoDB Logging`**: The `log_action()` helper function sends record of every API call to a MongoDB collection.
- **`Flask Routes`**:
    - `POST /users`: Creates a new user in the SQL database.
    - `POST /transactions`: Records a trade and links it to a portfolio and asset.
    - `GET /assets`: Retrieves all available assets.

## How to Run
*Note: This script requires active PostgreSQL and MongoDB instances.*
1. Install dependencies: `pip install flask-sqlalchemy psycopg2-binary pymongo`
2. Update the connection strings in the script with your credentials.
3. Run the application:
```bash
python week_04/daytwentyfour/day_twentyfour.py
```

## Reflection
Modern applications often use multiple types of databases. Using SQL for financial transactions ensures data integrity, while using NoSQL for logs allows the system to handle high volumes of activity data without slowing down core business logic.
