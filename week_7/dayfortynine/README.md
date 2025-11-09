## **Day 49: Weekly Project – Automated Trading Bot**

### **Objective**

Combine all your knowledge from the week into a single, autonomous **algorithmic trading system** capable of fetching data, making trading decisions, executing orders, managing risk, and generating daily reports — all with minimal manual intervention.

This marks your transition from learning individual trading components to orchestrating them into a fully functional **trading automation ecosystem**.

---

### **Project Requirements**

#### 1. **Data Ingestion**

Your bot should fetch **live or near-real-time market data** using one or more of the following:

* Broker or exchange APIs (`Alpaca`, `Binance`, `ccxt`).
* Web scraping from financial websites (e.g., CoinMarketCap, Yahoo Finance).
* CSV or JSON fallback data (for testing in offline mode).

#### 2. **Trading Strategy**

Implement a **rule-based strategy** to generate buy/sell signals. You can start with simple, classic strategies such as:

* **Moving Average Crossover Strategy**

  * **Buy Signal:** When the short-term moving average (e.g., 20-day) crosses **above** the long-term MA (e.g., 50-day).
  * **Sell Signal:** When the short-term MA crosses **below** the long-term MA.

* **Mean Reversion Strategy**

  * **Buy Signal:** When the asset’s price falls a certain % below its average.
  * **Sell Signal:** When the price reverts to or above the average.

> 💡 Tip: Keep it simple. Focus on correct signal logic, not profitability yet.

#### 3. **Order Management**

Integrate your **Order Management System (OMS)** from Day 46 to:

* Place and modify orders programmatically.
* Track order states (`PENDING`, `FILLED`, `CANCELLED`, etc.).
* Store order details (symbol, side, quantity, price, status, timestamps) in your local database.

#### 4. **Risk Controls**

Protect your portfolio through **automated risk management scripts**:

* Enforce **maximum position size** (e.g., no more than 10% of portfolio per trade).
* Set **stop-loss** and **take-profit** thresholds for every position.
* Define a **maximum daily drawdown** rule — if triggered, suspend trading for the day.
* Optionally, monitor correlations or volatility to manage exposure.

#### 5. **Automation**

Schedule your bot to run continuously or at fixed intervals (every minute, hour, or day):

* Use libraries like `schedule`, `APScheduler`, or OS-level cron jobs.
* Log all activities (data fetch, trade signals, order execution, errors).
* Implement graceful error handling and recovery from failed API calls.

#### 6. **Reporting**

Generate a daily or weekly **performance report** that summarizes:

* Total trades executed (wins/losses).
* Current portfolio value and P&L.
* Open positions and pending orders.
* Charts or plots of balance over time.

Output this as:

* HTML dashboard, **PDF report**, or terminal summary.
* Optional: Auto-send via email or message (Slack, Telegram).

---

### **Deliverables**

Your final deliverable for Week 7 should include:

1. **A fully functional automated trading bot**, running in a **paper trading environment** (no real money).
2. **Source files:**

   * `day_fortynine.py` — your bot’s main logic.
   * `config.json` or `.env` — for storing API keys, secrets, or thresholds.
3. **Documentation file (`STRATEGY.md` or `BOT_LOGIC.md`):**

   * Describe your chosen trading strategy and logic flow.
   * Outline your risk management framework.
   * Explain your API setup and authentication.
   * Include screenshots, sample logs, or trade reports.

---

### **Example Bot Workflow**

```text
1. Fetch market data from API or scraper
2. Compute indicators (e.g., moving averages, RSI)
3. Evaluate buy/sell signals
4. Apply risk rules (position sizing, stop-loss)
5. Send order to paper trading API
6. Log results (trade ID, price, quantity, timestamp)
7. Generate report at end of day
```

---

### **Weekly Reflection Prompt**

> 💭 *What part of building an automated trading system challenged you the most — designing the strategy, handling API logic, or managing order state? How does automation influence your discipline and emotional response to trading decisions?*

Take time to document your reflections in your journal or `WEEK7_REFLECTION.md`. It’s crucial for improving your future bot design and emotional resilience as a trader.

---

### **Suggested Tools & Libraries**

| **Category**       | **Python**                                 | **Node.js**                                    |
| ------------------ | ------------------------------------------ | ---------------------------------------------- |
| **Web Scraping**   | `requests`, `BeautifulSoup`, `selenium`    | `axios`, `cheerio`, `puppeteer`                |
| **APIs & Trading** | `ccxt`, `alpaca-trade-api`, `binance`      | `ccxt`, `alpaca-trade-api`, `node-binance-api` |
| **Data & Reports** | `pandas`, `matplotlib`, `jinja2`, `pdfkit` | `chart.js`, `puppeteer`, `handlebars`          |
| **Scheduling**     | `schedule`, `APScheduler`, `croniter`      | `node-cron`, `agenda`                          |
| **Databases**      | `sqlite3`, `sqlalchemy`, `pymongo`         | `mongoose`, `better-sqlite3`                   |
| **Logging**        | `logging`, `loguru`                        | `winston`, `pino`                              |

---
