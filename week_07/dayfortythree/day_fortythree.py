import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MarketDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_yahoo_finance(self, symbol='AAPL'):
        """Scrape basic stock data from Yahoo Finance"""
        try:
            url = f'https://finance.yahoo.com/quote/{symbol}'
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract current price
            price_element = soup.find(
                'fin-streamer', {'data-field': 'regularMarketPrice'})
            current_price = float(
                price_element['value']) if price_element else None

            # Extract previous close
            prev_close_element = soup.find(
                'td', {'data-test': 'PREV_CLOSE-value'})
            prev_close = float(prev_close_element.find('span').text.replace(
                ',', '')) if prev_close_element else None

            # Extract market cap
            market_cap_element = soup.find(
                'td', {'data-test': 'MARKET_CAP-value'})
            market_cap = market_cap_element.find(
                'span').text if market_cap_element else None

            data = {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': prev_close,
                'market_cap': market_cap,
                'timestamp': datetime.now().isoformat(),
                'source': 'yahoo_finance'
            }

            logging.info(f"Scraped data for {symbol}: ${current_price}")
            return data

        except Exception as e:
            logging.error(f"Error scraping {symbol}: {str(e)}")
            return None

    def scrape_top_gainers(self):
        """Scrape top gainers from Yahoo Finance"""
        try:
            url = 'https://finance.yahoo.com/gainers'
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            gainers = []

            # Find the table with gainers
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:6]  # Get top 5 gainers

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        symbol = cells[0].find('a').text if cells[0].find(
                            'a') else cells[0].text
                        name = cells[1].text
                        price = cells[2].text
                        change = cells[3].text
                        change_percent = cells[4].text

                        gainers.append({
                            'symbol': symbol.strip(),
                            'name': name.strip(),
                            'price': price.strip(),
                            'change': change.strip(),
                            'change_percent': change_percent.strip()
                        })

            return gainers

        except Exception as e:
            logging.error(f"Error scraping top gainers: {str(e)}")
            return []

    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Data saved to {filename}")

    def save_to_dataframe(self, data):
        """Convert data to pandas DataFrame"""
        return pd.DataFrame(data)


def main():
    scraper = MarketDataScraper()

    # Scrape individual stock data
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    stock_data = []

    for symbol in symbols:
        data = scraper.scrape_yahoo_finance(symbol)
        if data:
            stock_data.append(data)
        time.sleep(1)  # Be respectful with requests

    # Save individual stock data
    if stock_data:
        scraper.save_to_json(stock_data, 'stock_data.json')
        df = scraper.save_to_dataframe(stock_data)
        print("\nStock Data DataFrame:")
        print(df[['symbol', 'current_price', 'previous_close']])

    # Scrape top gainers
    print("\nScraping Top Gainers...")
    gainers = scraper.scrape_top_gainers()
    if gainers:
        scraper.save_to_json(gainers, 'top_gainers.json')
        gainers_df = pd.DataFrame(gainers)
        print("\nTop Gainers:")
        print(gainers_df)


if __name__ == "__main__":
    main()
