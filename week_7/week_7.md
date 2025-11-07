
## **Week 7: Trading Automation & Scripting**

**Days 43–49** | *Algorithmic Trading Foundations*

This week takes you from **passive portfolio tracking** to **active, automated trading** — where code executes trades, manages risk, and makes data-driven decisions. You’ll learn how to extract real-world market data, connect with trading APIs, automate your strategies, and enforce disciplined risk management. By the end of this week, you’ll have built a working **Automated Trading Bot** operating in a paper-trading environment.

---

### **Day 43: Web Scraping for Market Data**

* **Objective:** Learn to extract live market and financial data from websites that don’t provide a public API, building custom data pipelines for your trading insights.

* **Core Concepts:**

  * Legality & ethics of web scraping (`robots.txt`, Terms of Service compliance).
  * HTML structure, elements, and parsing fundamentals.
  * Tools for scraping:

    * `BeautifulSoup` / `requests` (Python)
    * `Cheerio` / `axios` (Node.js)
  * Handling sessions, cookies, and pagination.
  * Dynamic content scraping with **headless browsers** (`Selenium`, `Puppeteer`).
  * Rate limiting and anti-bot defenses (best practices for responsible scraping).

* **Hands-On Activity:**

  * **Tutorial:** Build a Python or Node.js script that scrapes the latest stock or crypto prices from Yahoo Finance, Investing.com, or CoinMarketCap.
  * **Challenge:** Extract data from a table (e.g., “Top Gainers”) and save it in structured JSON or a Pandas DataFrame format for later analysis.

---

### **Day 44: Automated Report Generation**

* **Objective:** Automate the creation and delivery of daily portfolio summaries, converting market data into actionable, visualized insights.

* **Core Concepts:**

  * Generating reports with templating engines (`Jinja2`, `Handlebars`).
  * Creating visualizations (`matplotlib`, `plotly`, `Chart.js`).
  * Exporting data-driven PDFs or HTML reports (`WeasyPrint`, `pdfkit`, `puppeteer`).
  * Key metrics: Daily P&L, Volatility, Allocation by Asset/Class.
  * Automating report delivery (via email, Slack, or Telegram).
  * Task scheduling (`cron`, `schedule`, or OS Task Scheduler).

* **Hands-On Activity:**

  * **Tutorial:** Create a daily report generator that summarizes your portfolio and renders a PDF or HTML dashboard.
  * **Challenge:** Automate the process — schedule the report to run daily at market close and email it using `smtplib` (Python) or `nodemailer` (Node.js).

---

### **Day 45: Trade Execution APIs**

* **Objective:** Connect your scripts to a real (or simulated) broker/exchange API to place, monitor, and manage trades programmatically.

* **Core Concepts:**

  * Introduction to broker APIs: **Alpaca**, **Binance**, **Interactive Brokers**, **TD Ameritrade**.
  * API Authentication using keys and secrets.
  * Core endpoints:

    * `/account` – account balance and portfolio data.
    * `/market-data` – price feeds and tickers.
    * `/orders` – placing, viewing, or canceling orders.
  * Understanding order types: **Market**, **Limit**, **Stop**, and **Stop-Limit**.
  * Paper trading vs. live trading environments.
  * Reading and using API documentation effectively.

* **Hands-On Activity:**

  * **Tutorial:** Sign up for a **paper trading** account (e.g., Alpaca or Binance Testnet). Write a script to:

    1. Fetch and print account details.
    2. Place a paper trade (buy 1 share or 0.01 BTC).
    3. Check and log the order status.
  * **Challenge:** Implement a function to cancel open limit orders through the API.

---

### **Day 46: Order Management Systems (OMS)**

* **Objective:** Design a simple Order Management System that tracks and synchronizes your orders with the broker API.

* **Core Concepts:**

  * Order lifecycle:

    * `PENDING` → `FILLED` → `CLOSED` / `CANCELLED` / `REJECTED`
  * Polling vs. streaming (WebSockets) for real-time order updates.
  * Database integration for order tracking (SQLite, MongoDB, or PostgreSQL).
  * Idempotency: avoiding duplicate or conflicting requests.
  * Queues and concurrency: managing multiple orders safely.

* **Hands-On Activity:**

  * **Tutorial:** Extend your database to include an `orders` table or collection:

    * Fields: `symbol`, `quantity`, `side`, `status`, `filled_price`, `timestamp`.
  * **Challenge:** Create a background script that regularly syncs open orders with your broker API and updates their statuses in the database.

---

### **Day 47: Risk Management Automation**

* **Objective:** Protect your capital by embedding automated risk controls directly into your trading system.

* **Core Concepts:**

  * Risk per trade & position sizing (Fixed Fractional, Kelly Criterion).
  * Stop-Loss and Take-Profit orders.
  * Maximum daily loss and drawdown rules.
  * Portfolio diversification and sector exposure limits.
  * Pre-trade risk checks (validating order size and exposure before execution).

* **Hands-On Activity:**

  * **Tutorial:** Write a pre-trade risk validation function:

    1. Ensure no single order exceeds 5% of portfolio equity.
    2. Simulate a stop-loss outcome to estimate worst-case loss.
  * **Challenge:** Automatically place a trailing stop-loss for every new position the bot opens, adjusting dynamically as prices change.

---

### **Day 48: Portfolio Rebalancing Scripts**

* **Objective:** Automate the rebalancing of your portfolio to maintain optimal diversification and target asset weights.

* **Core Concepts:**

  * Target allocation vs. current allocation.
  * Threshold-based rebalancing (e.g., trigger if deviation >5%).
  * Cost and tax efficiency in automated rebalancing.
  * Building and executing a “rebalancing basket” of trades.
  * Automating the process periodically or based on events.

* **Hands-On Activity:**

  * **Tutorial:** Create a script that calculates deviations from target weights (e.g., 60% SPY, 40% AGG) and lists the trades needed to rebalance.
  * **Challenge:** Integrate your script with your paper trading API to execute those rebalancing trades automatically when drift exceeds a set threshold.

---

### **Day 49: Weekly Project – Automated Trading Bot**

* **Objective:** Combine all your knowledge into a complete, autonomous **algorithmic trading system** capable of data ingestion, order execution, and risk management.

* **Project Requirements:**

  1. **Data Ingestion:** Retrieve live market data via an API or scraper.
  2. **Trading Strategy:** Implement a rule-based strategy such as:

     * **Moving Average Crossover:** Buy when short MA crosses above long MA.
     * **Mean Reversion:** Buy when price deviates below average and sell when it normalizes.
  3. **Order Management:** Use your OMS to place and update orders with real-time tracking.
  4. **Risk Controls:** Include at least two automated risk management rules (e.g., position sizing, drawdown halt, stop-loss).
  5. **Automation:** Schedule your bot to run continuously and log every trade.
  6. **Reporting:** Generate a daily activity report summarizing trades, P&L, and portfolio performance.

* **Deliverable:**

  * A fully functional **automated trading bot** running in a paper trading environment.
  * A documentation file (`STRATEGY.md` or `BOT_LOGIC.md`) that includes:

    * Your trading logic and signals.
    * Risk management framework.
    * API configuration details.
    * Example output logs or daily reports.

---

### **Weekly Reflection Prompt**

*What part of building an automated trading system challenged you the most — designing the strategy, handling API logic, or managing order state? How does automation influence your discipline and emotional response to trading decisions?*

---

### **Suggested Tools & Libraries**

| Category           | Python                                     | Node.js                                        |
| ------------------ | ------------------------------------------ | ---------------------------------------------- |
| **Web Scraping**   | `requests`, `BeautifulSoup`, `selenium`    | `axios`, `cheerio`, `puppeteer`                |
| **APIs & Trading** | `ccxt`, `alpaca-trade-api`, `binance`      | `ccxt`, `alpaca-trade-api`, `node-binance-api` |
| **Data & Reports** | `pandas`, `matplotlib`, `jinja2`, `pdfkit` | `chart.js`, `puppeteer`, `handlebars`          |
| **Scheduling**     | `schedule`, `croniter`                     | `node-cron`, `agenda`                          |
| **Databases**      | `sqlite3`, `sqlalchemy`, `pymongo`         | `mongoose`, `better-sqlite3`                   |

---
