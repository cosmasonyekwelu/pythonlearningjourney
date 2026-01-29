# Day 43: Market Data Scraper

**Date:** November 3, 2025

## Learning Objective
To understand how to extract financial data from web pages using Web Scraping techniques with `BeautifulSoup` and `requests`.

## Concepts Covered
- **Web Scraping Fundamentals**: Navigating the HTML DOM and extracting specific elements.
- **BeautifulSoup**: Using CSS selectors and HTML tags to find data.
- **Session Management**: Using `requests.Session()` to handle headers and cookies efficiently.
- **Data Persistence**: Saving scraped data into JSON and Pandas DataFrames.
- **Rate Limiting**: Implementing `time.sleep()` to avoid being blocked by servers.

## Code Explanation
The `day_fortythree.py` script implements a `MarketDataScraper`:
- **`scrape_yahoo_finance(symbol)`**: Extracts the current price, previous close, and market cap for a specific stock by parsing the Yahoo Finance page.
- **`scrape_top_gainers()`**: Fetches the "Top Gainers" table from Yahoo Finance and extracts the first 5 records.
- **Logging**: Uses the `logging` module to track successes and errors during the scraping process.

## How to Run
1. Install dependencies: `pip install requests beautifulsoup4 pandas`
2. Run the scraper:
```bash
python week_07/dayfortythree/day_fortythree.py
```

## Reflection
Web scraping is a powerful way to gather data when an official API is unavailable. However, it is brittle—if the website changes its layout, the scraper may break. Always check a site's `robots.txt` before scraping.
