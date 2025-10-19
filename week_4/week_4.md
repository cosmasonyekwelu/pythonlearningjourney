# **Week 4 — Web Development & Data Systems**

## **Overview**

Week 4 focuses on mastering **backend frameworks (Flask & Django)**, **database integration**, and **data-driven web applications**. By the end of this week, you'll be able to design, build, and deploy **interactive web applications** that communicate with databases, visualize financial data, and provide real-time insights — a foundation for your upcoming **Trading Journal Web App**.

---

## **Learning Objectives**

By the end of Week 4, you should be able to:

- Build and configure Flask and Django web servers
- Create APIs and integrate with frontend templates
- Use databases (SQLite, PostgreSQL, MySQL, MongoDB) effectively
- Implement authentication and session management
- Build RESTful endpoints for trading or analytics systems
- Visualize data using charts and dashboards
- Implement real-time data updates using WebSockets or APIs

---

## **Detailed Table of Contents**

### **Day 22 — Flask Fundamentals & Routing**

**Focus:** Introduction to lightweight web frameworks and routing

**Topics:**

- Flask setup and environment configuration
- Creating routes and handling requests (GET, POST)
- Template rendering with Jinja2
- Static files management (CSS, JS, images)
- Request and response objects
- URL building and redirecting
- Debug mode and auto-reload

**Key Code Example:**

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='Trading Dashboard')

@app.route('/trades/<int:trade_id>')
def show_trade(trade_id):
    return f'Displaying Trade #{trade_id}'

if __name__ == '__main__':
    app.run(debug=True)
```

**Mini Project:** Build a Flask "Crypto Price Tracker" that fetches Bitcoin prices using an external API.

**Online Learning Resources:**

- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Real Python Flask Tutorials](https://realpython.com/tutorials/flask/)
- [GeeksforGeeks Flask Tutorial](https://www.geeksforgeeks.org/flask-tutorial/)
- [Tutorialspoint](https://www.tutorialspoint.com/flask/index.htm)
- [Flask Full Course](https://www.youtube.com/watch?v=45P3xQPaYxc)

---

### **Day 23 — Django Setup & ORM**

**Focus:** Understanding full-scale web frameworks and database modeling

**Topics:**

- Installing and setting up Django
- Understanding Django project structure
- Creating apps, views, and URLs
- Using Django ORM for models and migrations
- Connecting SQLite and PostgreSQL
- Django Admin and model registration
- QuerySets and CRUD operations
- Introduction to Django components
- Django project structure
- Adding the App to Your Project
- Understanding HttpRequest Objects
- Using QueryDict Objects
- Creating URLConf's
- Django URLs as routes
- Regular Expressions and URL patterns

**Key Code Example:**

```python
# models.py
from django.db import models

class Trade(models.Model):
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.quantity} shares"
```

**Mini Project:** Create a "Trade Records" app in Django that allows CRUD operations on trades.

**Online Learning Resources:**

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django for Beginners](https://djangoforbeginners.com/)
- [MDN Django Web Framework](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)
- [Simple is Better Than Complex Django Tutorials](https://simpleisbetterthancomplex.com/)

---

### **Day 24 — Database Design with SQLite, PostgreSQL, MySQL, and MongoDB**

**Focus:** Designing and connecting multi-database systems for scalability

**Topics:**

- Database fundamentals (tables, relations, indexes, keys)
- Designing schema for trading data
- Using SQLAlchemy ORM with Flask
- PostgreSQL setup and connection pooling
- Integrating MySQL and MongoDB for different use cases
- CRUD operations in SQL and NoSQL databases
- Backing up and restoring data
- About Database Models
- Configuring Django for Database Access
- Database migrations
- Understanding Django Models and Model Fields
- Table Naming Conventions
- Generating & Reviewing SQL
- Understanding QuerySets and applying filters
- Field lookups and slicing QuerySets
- Common QuerySet methods
- Managing related records

**Key Code Example:**

```python
# SQLAlchemy with Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
```

**Practice Task:** Design a relational schema for a "Portfolio Tracker" that includes users, transactions, and assets.

**Online Learning Resources:**

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [MongoDB University](https://university.mongodb.com/)
- [W3Schools SQL Tutorial](https://www.w3schools.com/sql/)
- [DB-Engines Database Knowledge Base](https://db-engines.com/en/learning_resources)

---

### **Day 25 — User Authentication & Sessions**

**Focus:** Implementing secure login and user management systems

**Topics:**

- Authentication vs Authorization
- Flask-Login and Django Authentication
- Password hashing (bcrypt, werkzeug.security)
- User sessions and cookies
- Access control and decorators
- Logout and session timeout handling
- Secure password reset and user validation
- The Django Session Framework
- Sessions in Views and Session Tuning
- Using Authentication in Views (CSRF Token)
- Login and Logout functionality
- Building custom Login/Logout Views
- Authentication Decorators
- Adding & Deactivating Users

**Key Code Example:**

```python
from flask_login import LoginManager, UserMixin, login_user, login_required

login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Mini Project:** Build a "User Login System" that protects portfolio data based on user sessions.

**Online Learning Resources:**

- [Django Authentication System](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Auth0 Python Web App Tutorial](https://auth0.com/docs/quickstart/webapp/python)

---

### **Day 26 — API Development (REST, etc.)**

**Focus:** Building RESTful APIs and backend endpoints

**Topics:**

- REST API principles and CRUD architecture
- Flask RESTful and Django REST Framework (DRF) setup
- Serializers and data validation
- Handling API authentication (JWT, TokenAuth)
- Pagination and filtering
- Testing API endpoints with Postman
- Versioning and documentation (Swagger, Postman Collections)
- Django and REST APIs
- JSON responses preparation
- Django REST framework setup
- Using the Django Admin Interface
- Creating an Admin User

**Key Code Example:**

```python
from flask_restful import Api, Resource

api = Api(app)

class TradeAPI(Resource):
    def get(self, trade_id=None):
        if trade_id:
            trade = Trade.query.get(trade_id)
            return trade.serialize()
        trades = Trade.query.all()
        return [t.serialize() for t in trades]

api.add_resource(TradeAPI, '/api/trades', '/api/trades/<int:trade_id>')
```

**Mini Project:** Create an API that returns market data and stores transactions for users.

**Online Learning Resources:**

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Flask-RESTful Documentation](https://flask-restful.readthedocs.io/)
- [Postman Learning Center](https://learning.postman.com/)
- [REST API Tutorial](https://restfulapi.net/)
- [Swagger/OpenAPI Documentation](https://swagger.io/docs/)

---

### **Day 27 — Frontend Integration & Templates**

**Focus:** Connecting backend logic with frontend presentation

**Topics:**

- Jinja2 templating (Flask) and Django Templates
- Template inheritance and layout design
- Integrating Bootstrap or Tailwind CSS
- Passing dynamic data from backend to templates
- Handling form submissions and validations
- Building user-friendly dashboard pages
- Introduction to Front-end development tools
- HTML & CSS fundamentals
- Basic JavaScript for interactivity
- Serving static and media files
- Template Fundamentals and Template Objects
- Template Tags and Filters
- Template Inheritance
- Django Form classes and validation
- Creating Forms from Models
- Advanced Forms processing techniques

**Key Code Example:**

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}Trading Journal{% endblock %}</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <!-- Navigation content -->
    </nav>
    <div class="container mt-4">{% block content %}{% endblock %}</div>
  </body>
</html>
```

**Mini Project:** Build a "Trading Activity Dashboard" that displays portfolio summaries.

**Online Learning Resources:**

- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)
- [Django Templates Documentation](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [W3Schools Frontend Tutorials](https://www.w3schools.com/)

---

### **Day 28 Weekly Project: Trading Journal Web App**

**Focus:** Bringing all concepts together into a complete web application

**Project Description:** Build a **Trading Journal Web App** that allows users to log trades, track performance, and visualize profits. Users can register, log in, and interact with a dashboard showing trade statistics and real-time data updates.

**Key Features:**

- Flask or Django backend
- Authentication and user management
- Database integration (PostgreSQL or MongoDB)
- REST API for trade entries
- Data visualization using Chart.js or Plotly
- Real-time updates for prices and trades
- Export functionality (CSV or PDF)

**Stretch Goals:**

- Integrate with Binance API for trade imports
- Add ML-based trade performance predictions
- Deploy the app to Render, Heroku, or AWS

**Project Resources:**

- [Full-Stack Python Guide](https://www.fullstackpython.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/stable/deploying/)
- [Heroku Python Deployment](https://devcenter.heroku.com/categories/python-support)

---

## **Tools & Libraries**

- **Backend Frameworks:** Flask, Django
- **Databases:** SQLite, PostgreSQL, MySQL, MongoDB
- **APIs & HTTP:** Requests, Flask-RESTful, Django REST Framework
- **Frontend:** HTML, CSS, Bootstrap, Tailwind CSS, Chart.js
- **Visualization:** Matplotlib, Plotly, Dash
- **Auth & Security:** Flask-Login, Django Auth, JWT
- **Deployment:** Gunicorn, Render, Heroku, Docker

---

## **Additional Learning Platforms**

### **Comprehensive Courses:**

- [Coursera: Web Applications for Everybody](https://www.coursera.org/specializations/web-applications)
- [edX: Django for Everybody](https://www.edx.org/professional-certificate/django-for-everybody)
- [FreeCodeCamp: Backend Development](https://www.freecodecamp.org/learn/back-end-development-and-apis/)

### **Community & Support:**

- [Stack Overflow - Flask](https://stackoverflow.com/questions/tagged/flask)
- [Stack Overflow - Django](https://stackoverflow.com/questions/tagged/django)
- [Reddit: r/flask](https://www.reddit.com/r/flask/)
- [Reddit: r/django](https://www.reddit.com/r/django/)
- [Python Discord Server](https://discord.gg/python)

### **Practice Platforms:**

- [Exercism Python Track](https://exercism.org/tracks/python)
- [HackerRank Python Domain](https://www.hackerrank.com/domains/python)
- [LeetCode Database Problems](https://leetcode.com/problemset/database/)

---

## **Expected Outcomes**

By the end of Week 4, you will:

- Build and deploy full-stack Python web applications
- Connect Python backends to multiple databases
- Create and consume REST APIs
- Implement authentication and secure user systems
- Visualize financial data in real time
- Prepare for advanced FinTech automation and trading projects in Week 5

---

**Next Week Preview:** Week 5 Financial Programming Essentials, where you'll apply these web development skills to build financial data pipelines and trading analytics systems.
