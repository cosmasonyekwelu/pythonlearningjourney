
## Day 24 — Database Design with SQLite, PostgreSQL, MySQL, and MongoDB

### 🎯 Focus
Designing and connecting **multi-database systems** using SQL (PostgreSQL, MySQL, SQLite) and NoSQL (MongoDB) to create scalable and data-rich applications.

---

## 🧩 Key Concepts

### 1. **Database Fundamentals**
- **Tables** — store structured data in rows and columns.  
- **Relations** — define links between tables: one-to-one, one-to-many, many-to-many.  
- **Indexes** — speed up data lookup.  
- **Primary Key** — unique record identifier.  
- **Foreign Key** — references another table’s key.

---

### 2. **Portfolio Tracker Schema**
| Table | Purpose | Key Fields |
|--------|----------|------------|
| Users | Store user data | id, username, email |
| Portfolios | Track user balance | id, user_id, balance |
| Assets | Define tradable items | id, name, symbol, type |
| Transactions | Record buy/sell operations | id, portfolio_id, asset_id, type, amount, price |

---

### 3. **SQLAlchemy + Flask Integration**
- ORM maps Python classes to database tables.
- `db.create_all()` auto-generates schema.
- CRUD routes for interacting with the database.

Example:
```python
portfolio = Portfolio(user_id=1, balance=1500.0)
db.session.add(portfolio)
db.session.commit()
````

---

### 4. **MongoDB Integration**

MongoDB is used for logging or unstructured data (via `pymongo`):

```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client['portfolio_tracker']
db['activity_logs'].insert_one({"action": "BUY", "asset": "BTC"})
```

---

### 5. **Backup & Restore**

**PostgreSQL**

```bash
pg_dump portfolio_db > backup.sql
psql portfolio_db < backup.sql
```

**MongoDB**

```bash
mongodump --db portfolio_tracker --out ./backup
mongorestore --db portfolio_tracker ./backup/portfolio_tracker
```

---

### 6. **Connecting Multiple Databases (Django Example)**

```python
DATABASES = {
  'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'main_db'},
  'mysql_db': {'ENGINE': 'django.db.backends.mysql', 'NAME': 'analytics_db'},
}
```

Query from specific database:

```python
MyModel.objects.using('mysql_db').all()
```

---

## 🧠 Important ORM Concepts

| Term                | Description                                          |
| ------------------- | ---------------------------------------------------- |
| **Model**           | Python class representing a table                    |
| **Migration**       | Converts model changes into database schema          |
| **QuerySet**        | Lazy-evaluated collection of records                 |
| **Field lookups**   | Filter expressions like `.filter(balance__gte=1000)` |
| **Related records** | Access linked data via foreign keys                  |

---

## 🧰 Tools Used

* **Flask** — micro web framework
* **SQLAlchemy** — ORM for SQL databases
* **PostgreSQL / MySQL / SQLite** — relational databases
* **MongoDB** — NoSQL database for logs
* **PyMongo** — MongoDB driver for Python

---

## 📚 Learning Resources

* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
* [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
* [MongoDB University](https://university.mongodb.com/)
* [W3Schools SQL Tutorial](https://www.w3schools.com/sql/)
* [DB-Engines Knowledge Base](https://db-engines.com/en/learning_resources)

---


