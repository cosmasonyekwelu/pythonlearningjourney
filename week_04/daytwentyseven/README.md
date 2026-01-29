# Day 27: Frontend Integration & Templates

**Date:** October 18, 2025

## Learning Objective
To understand how to integrate a Flask backend with a dynamic HTML frontend using the Jinja2 template engine.

## Concepts Covered
- **Jinja2 Inheritance**: Using base layouts to maintain a consistent UI across different pages.
- **Data Rendering**: Passing complex Python dictionaries and lists to HTML templates.
- **Form Handling**: Capturing user input from HTML forms and processing it on the server.
- **Dynamic CSS/JS**: Linking static assets to rendered HTML pages.
- **Flash Messaging**: Providing visual feedback to users after actions (e.g., "Trade recorded").

## Code Explanation
The `day_twentyseven.py` script focuses on the interaction between data and display:
- **`portfolio_data`**: A mock data structure representing a user's holdings.
- **`home()` route**: Renders `dashboard.html`, passing the portfolio data for display in tables and charts.
- **`trade()` route**: Demonstrates handling both GET (to show the form) and POST (to process the trade) in a single function.
- **`templates/`**: Contains the HTML files that use Jinja2 syntax (e.g., `{% for holding in data.holdings %}`).

## How to Run
1. Ensure Flask is installed.
2. Run the application:
```bash
python week_04/daytwentyseven/day_twentyseven.py
```
3. Visit `http://localhost:5000` to interact with the dashboard and trade forms.

## Reflection
A backend is only as good as its interface. Mastering templates allows you to transform raw database data into a user-friendly experience, making the application accessible to non-technical users.
