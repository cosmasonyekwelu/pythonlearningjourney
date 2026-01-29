# Day 44: Portfolio Reporting Engine

**Date:** November 4, 2025

## Learning Objective
To build a comprehensive reporting system that calculates portfolio performance and generates both visual and HTML reports for end-users.

## Concepts Covered
- **Data Analysis**: Calculating unrealized P&L, percentage changes, and weighted allocations.
- **Data Visualization**: Using `Matplotlib` to create pie charts and bar graphs.
- **HTML Templating**: Using `Jinja2` to generate dynamic HTML reports.
- **Email Automation**: Sending reports as attachments using `smtplib` and MIME messages.
- **Logging**: Tracking the report generation lifecycle.

## Code Explanation
The `day_fortyfour.py` script implements the `PortfolioReporter`:
- **`calculate_metrics()`**: Takes a list of holdings and produces a summary including total value and P&L percentage.
- **`create_visualizations()`**: Generates a 2x2 dashboard image showing allocation and performance.
- **`generate_html_report()`**: Uses an embedded Jinja2 template to produce a professional-looking summary.
- **`send_email_report()`**: (Optional) Interfaces with an SMTP server to deliver the report to the user's inbox.

## How to Run
1. Install dependencies: `pip install pandas matplotlib jinja2`
2. Run the reporter:
```bash
python week_07/dayfortyfour/day_fortyfour.py
```
3. Open `portfolio_report.html` to view the generated dashboard.

## Reflection
A system is only as good as the information it provides. Automating the generation and delivery of performance reports allows investors to make data-driven decisions without manual calculations.
