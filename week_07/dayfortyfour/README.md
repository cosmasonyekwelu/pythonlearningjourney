# Day 44: Automated Report Generation

## Objective
Automate the creation and delivery of daily portfolio summaries and market analysis, converting raw data into actionable, visualized insights.

## Features
- **Portfolio Analytics**: Calculate key metrics like P&L, allocation, and performance
- **Professional Visualizations**: Generate pie charts, bar charts, and performance graphs
- **HTML & PDF Reports**: Create formatted reports using Jinja2 templating
- **Email Automation**: Send reports via SMTP with attachment support
- **Modular Design**: Easy to extend with new metrics and visualizations

## Core Concepts Demonstrated
- **Data Analysis**: Portfolio metrics calculation and performance tracking
- **Visualization**: Matplotlib for creating publication-quality charts
- **Templating Engines**: Jinja2 for dynamic HTML report generation
- **Email Integration**: SMTP for automated report distribution
- **Scheduling Ready**: Designed for cron job integration

## Installation Requirements
```bash
pip install pandas matplotlib jinja2
```

## Usage
```bash
python day_fortyfour.py
```

## Output Files
- `portfolio_report.html`: Comprehensive HTML dashboard
- `portfolio_report.png`: Portfolio visualization charts

## Email Configuration
To enable email reports:
1. Update SMTP settings in `send_email_report()` method
2. Use app-specific passwords for Gmail/Outlook
3. Uncomment the email sending line in `main()`

## Key Metrics Calculated
- Total portfolio value and cost basis
- Unrealized P&L (absolute and percentage)
- Portfolio allocation by symbol
- Individual holding performance


