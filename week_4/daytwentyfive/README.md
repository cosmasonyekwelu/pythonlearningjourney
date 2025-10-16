## Day 25 — User Authentication & Sessions

### 🎯 Focus

Implementing **secure login and user management systems** using Flask-Login and Django Authentication.

---

## 🧩 Key Concepts

### 🔐 1. Authentication vs Authorization

- **Authentication** — verifies _who_ the user is (login, password, identity).
- **Authorization** — defines _what_ actions they can perform (admin access, restricted pages).

---

### ⚙️ 2. Flask Authentication Workflow

1. **User Registration**
   - Accept email, username, and password.
   - Hash passwords using `werkzeug.security.generate_password_hash()`.
2. **Login**
   - Verify password using `check_password_hash()`.
   - Create a session via Flask-Login’s `login_user()`.
3. **Session**
   - Stored in browser cookies.
   - Can be made permanent (`session.permanent = True`) and auto-expire.
4. **Logout**
   - `logout_user()` clears the session.
5. **Access Control**
   - Use `@login_required` to protect private routes.

---

### 🧠 3. Secure Password Handling

```python
from werkzeug.security import generate_password_hash, check_password_hash

hashed = generate_password_hash("password123")
check_password_hash(hashed, "password123")  # ✅ True
```

Hashing ensures raw passwords are **never stored** in the database.

### 🔄 4. Flask-Login Essentials

````
| Function           | Description                                   |
| ------------------ | --------------------------------------------- |
| `LoginManager()`   | Initializes login system                      |
| `UserMixin`        | Adds authentication methods to the User model |
| `login_user(user)` | Logs in the user                              |
| `logout_user()`    | Logs out current session                      |
| `current_user`     | Returns logged-in user instance               |
| `@login_required`  | Protects private routes                       |

---

### 🧩 5. Django Authentication Overview

Django provides authentication out of the box:

#### Configure in `settings.py`

```python
INSTALLED_APPS = [
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
]
````

#### Example: Login View

```python
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')
```

#### Example: Logout View

```python
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')
```

---

### 🧾 6. Session Management

| Framework  | Mechanism         | Storage                  |
| ---------- | ----------------- | ------------------------ |
| **Flask**  | `session` dict    | Signed cookies           |
| **Django** | Session framework | DB, cache, or file-based |

**Set timeout (Flask):**

```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
```

**Set timeout (Django):**

```python
SESSION_COOKIE_AGE = 1800  # 30 minutes
```

---

### ⚙️ 7. Security Best Practices (OWASP)

- Use **bcrypt** or **PBKDF2** for hashing.
- Implement **CSRF protection** (`@csrf_protect` in Django, Flask-WTF in Flask).
- Enforce **strong passwords** (length, symbols, numbers).
- Limit login attempts to prevent brute-force.
- Use HTTPS to protect cookies and tokens.

---

### 🔧 8. Common Flask Routes in `day_twentyfive.py`

| Route         | Method | Description                   |
| ------------- | ------ | ----------------------------- |
| `/register`   | POST   | Create a new user             |
| `/login`      | POST   | Authenticate user             |
| `/logout`     | POST   | End session                   |
| `/profile`    | GET    | View user details (protected) |
| `/deactivate` | POST   | Deactivate account            |

---

## 🧰 Tools Used

- **Flask** — lightweight Python web framework
- **Flask-Login** — session-based authentication
- **Werkzeug Security** — password hashing utilities
- **SQLite** — test database
- **Django Auth System** — for comparative learning

---

## 📚 Learning Resources

- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Django Authentication System](https://docs.djangoproject.com/en/stable/topics/auth/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Auth0 Python Web App Tutorial](https://auth0.com/docs/quickstart/webapp/python)

---
