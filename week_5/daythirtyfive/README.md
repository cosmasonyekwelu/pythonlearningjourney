# **Day 35 — Stock Data Analyzer**

A **comprehensive stock analysis and visualization tool** that combines **technical indicators, fundamental metrics, portfolio risk analytics**, and an **interactive dashboard**.

---

## **Overview**

The **Stock Data Analyzer** fetches live and historical market data, performs in-depth technical and fundamental analysis, evaluates portfolio risks, and generates exportable reports or visual dashboards — all in one system.

---

## **Key Features**

- **Multi-Stock Comparison** — price, returns, and correlations
- **Technical Analysis** — RSI, MACD, Bollinger Bands, Moving Averages
- **Fundamental Analysis** — P/E, ROE, dividends, profit margins
- **Risk Metrics** — volatility, Sharpe ratio, drawdown, VaR
- **Interactive Dashboard** — built with Plotly Dash
- **Reports & Exports** — HTML, CSV, Excel summaries
- **Caching System** — fast local data reuse

---

## **Quick Start**

### **1️ Setup**

```bash
pip install -r requirements.txt
cp .env.example .env
```

(Optional) Add your Alpha Vantage API key in `.env`.

### **2️ CLI Usage**

```bash
# Analyze a stock
python day_thirtyfive.py analyze AAPL --period 1y

# Compare multiple stocks
python day_thirtyfive.py compare AAPL MSFT GOOGL

# Generate HTML report
python day_thirtyfive.py report AAPL --format html

# Launch dashboard
python day_thirtyfive.py dashboard
```

---

## **Dashboard**

Run:

```bash
python day_thirtyfive.py dashboard
```

Then open [http://localhost:8050](http://localhost:8050)

Tabs include:

- **Price Comparison**
- **Technical Analysis**
- **Fundamentals**
- **Risk Metrics**
- **Portfolio View**

---

## **Project Structure**

```
day_thirtyfive/
├── day_thirtyfive.py        # Main entry point
├── requirements.txt
├── .env.example
└── src/
    ├── data_collection.py   # Data fetching & caching
    ├── analysis_engine.py   # Technical/Fundamental/Risk analysis
    ├── reporting.py         # Report generation
    ├── stock_data_analyzer.py
    ├── dashboard.py         # Interactive dashboard
    └── app.py               # CLI interface
```

---
