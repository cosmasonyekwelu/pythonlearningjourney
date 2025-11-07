# Day 43: Web Scraping for Market Data

## Objective
Learn to extract live market and financial data from websites that don't provide public APIs, building custom data pipelines for your trading insights.

## Features
- **Multi-Source Scraping**: Extract data from Yahoo Finance and financial news sites
- **Structured Data Output**: Save data in JSON and pandas DataFrame formats
- **Rate Limiting**: Built-in delays between requests to be respectful to servers
- **Error Handling**: Robust error handling for network issues and parsing failures
- **Top Gainers Extraction**: Specialized function for trending stocks

## Core Concepts Demonstrated
- **HTML Parsing**: Using BeautifulSoup to navigate and extract specific data elements
- **HTTP Session Management**: Maintaining sessions with proper headers and cookies
- **Ethical Scraping**: Respecting `robots.txt` and implementing rate limiting
- **Data Transformation**: Converting unstructured HTML to structured data formats
- **Logging & Monitoring**: Comprehensive logging for debugging and monitoring

## Installation Requirements
```bash
pip install requests beautifulsoup4 pandas
```

## Usage
```bash
python day_fortythree.py
```

## Output Files
- `stock_data.json`: Individual stock data for major tech companies
- `top_gainers.json`: Top 5 gaining stocks with price change information

## Ethical Scraping Practices
- 1-second delays between requests to avoid overwhelming servers
- Proper User-Agent headers to identify the scraper
- Respect for website terms of service
- Graceful error handling without retry storms

## Customization
- Modify `symbols` list in `main()` function to scrape different stocks
- Adjust `scrape_top_gainers()` to extract different metrics
- Add new data sources by creating additional scraping methods
```
