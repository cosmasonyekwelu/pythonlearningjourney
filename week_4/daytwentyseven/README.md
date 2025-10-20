# Day 27  Frontend Integration & Templates

## **Focus**

Connecting backend logic with frontend presentation using templating systems in Flask (Jinja2) and Django.

---

## **Topics Covered**

- Jinja2 templating (Flask) and Django Templates
- Template inheritance and layout design
- Integrating Bootstrap or Tailwind CSS
- Passing dynamic data from backend to templates
- Handling form submissions and validations
- Building user-friendly dashboard pages
- HTML, CSS & Basic JavaScript fundamentals
- Serving static and media files
- Template Tags, Filters, and Inheritance
- Django Form classes and validation
- Creating Forms from Models
- Advanced Form Processing Techniques

---

## **Mini Project:**

**Trading Activity Dashboard**

Build a simple dashboard that displays:

- Portfolio summary and balance
- List of holdings
- Recent trades
- A form to record new trades

Uses Jinja2 templates to render dynamic data and Bootstrap for styling.

---

## **Key Code Example**

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
