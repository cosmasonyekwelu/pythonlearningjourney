# Day 25: User Authentication & Sessions

**Date:** October 16, 2025

## Learning Objective
To implement a secure user authentication system in Flask, including password hashing, session management, and protected routes.

## Concepts Covered
- **Password Security**: Hashing passwords with `werkzeug.security` to ensure they are never stored in plain text.
- **Session Management**: Using `Flask-Login` and `Flask-Session` to maintain user state.
- **Protected Routes**: Using the `@login_required` decorator to restrict access to authenticated users.
- **User Lifecycles**: Handling registration, login, logout, and account deactivation.
- **Database Integration**: Using SQLite with SQLAlchemy for local user storage.

## Code Explanation
The `day_twentyfive.py` script provides a complete authentication workflow:
- **`User` Model**: Implements `UserMixin` for compatibility with Flask-Login and includes helper methods `set_password` and `check_password`.
- **`login_manager.user_loader`**: A callback function used to reload the user object from the user ID stored in the session.
- **Routes**:
    - `/register`: Validates input, hashes the password, and saves the user.
    - `/login`: Verifies credentials and starts a "remember me" session.
    - `/profile`: A protected route that displays the current user's details.

## How to Run
1. Install requirements: `pip install flask-sqlalchemy flask-login`
2. Run the application:
```bash
python week_04/daytwentyfive/day_twentyfive.py
```
3. Use a tool like Postman or `curl` to send POST requests to `/register` and `/login`.

## Reflection
Authentication is the gatekeeper of any application. Beyond just checking passwords, managing session lifetimes and securely hashing data are fundamental responsibilities for a backend developer.
