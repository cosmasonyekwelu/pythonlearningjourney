# Day 35: Weekly Project – Financial Programming Summary

**Date:** October 26, 2025

## Learning Objective
To consolidate all financial programming concepts learned throughout the week into a unified Command Line Interface (CLI) and interactive dashboard.

## Concepts Covered
- **Command-Line Interface (CLI)**: Using `argparse` to build a professional multi-command tool.
- **Project Structure**: Organizing complex code into a logical `src/` directory with modular responsibilities.
- **Reporting**: Exporting analysis results to HTML, CSV, and Excel formats.
- **Interactive Dashboards**: Launching a Dash-based web application for data exploration.
- **Caching**: Implementing a simple file-based cache to improve API performance and reduce rate-limiting issues.

## Code Explanation
The `day_thirtyfive.py` script serves as the main entry point for the "Stock Data Analyzer" project:
- **Commands**:
    - `analyze`: Provides a technical and risk summary of a single ticker.
    - `compare`: Analyzes correlations and portfolio risk for multiple symbols.
    - `screen`: Filters the stock universe based on volatility and Sharpe ratio.
    - `recommend`: Uses technical analysis to generate Buy/Hold/Sell signals.
    - `dashboard`: Starts a local web server to visualize the data interactively.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. View available commands:
```bash
python week_05/daythirtyfive/day_thirtyfive.py --help
```
3. Run a stock analysis:
```bash
python week_05/daythirtyfive/day_thirtyfive.py analyze AAPL --format json
```

## Reflection
Consolidating individual scripts into a unified tool transforms a collection of experiments into a professional product. This project demonstrates how a robust backend can support multiple frontends (CLI, Reports, Dashboards) simultaneously.
