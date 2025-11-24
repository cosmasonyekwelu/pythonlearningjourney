"""
Day 32 - Market Data APIs Integration
Multiple financial data API integrations for comprehensive market data
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class MarketDataAPI:
    """
    Unified interface for multiple financial data APIs
    """

    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.iex_cloud_key = os.getenv('IEX_CLOUD_API_KEY')
        self.polygon_key = os.getenv('POLYGON_API_KEY')

    def get_yfinance_data(self, symbols: List[str], period: str = '1y',
                          interval: str = '1d') -> pd.DataFrame:
        """
        Get historical data using Yahoo Finance API
        """
        print(f"Fetching Yahoo Finance data for {len(symbols)} symbols...")

        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=period, interval=interval)
                if not hist_data.empty:
                    data[symbol] = hist_data['Close']
                    print(f"  ✓ {symbol}: {len(hist_data)} data points")
                else:
                    print(f"  ✗ {symbol}: No data available")
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {e}")

        return pd.DataFrame(data)

    def get_alpha_vantage_data(self, symbol: str, function: str = 'TIME_SERIES_DAILY') -> Optional[Dict]:
        """
        Get data from Alpha Vantage API
        """
        if not self.alpha_vantage_key:
            print("Alpha Vantage API key not found")
            return None

        base_url = "https://www.alphavantage.co/query"
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.alpha_vantage_key,
            'outputsize': 'compact'
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if 'Error Message' in data:
                print(
                    f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None
            elif 'Note' in data:
                print(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            else:
                return data

        except Exception as e:
            print(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None

    def get_iex_cloud_data(self, symbol: str, endpoint: str = 'quote') -> Optional[Dict]:
        """
        Get data from IEX Cloud API
        """
        if not self.iex_cloud_key:
            print("IEX Cloud API key not found")
            return None

        base_url = f"https://cloud.iexapis.com/stable/stock/{symbol}/{endpoint}"
        params = {
            'token': self.iex_cloud_key
        }

        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"IEX Cloud error for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching IEX Cloud data for {symbol}: {e}")
            return None

    def get_polygon_data(self, symbol: str, timespan: str = 'day',
                         from_date: str = None, to_date: str = None) -> Optional[Dict]:
        """
        Get data from Polygon.io API
        """
        if not self.polygon_key:
            print("Polygon.io API key not found")
            return None

        if not from_date:
            from_date = (datetime.now() - timedelta(days=365)
                         ).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')

        base_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{timespan}/{from_date}/{to_date}"
        params = {
            'apiKey': self.polygon_key,
            'adjusted': 'true',
            'sort': 'asc'
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if data.get('status') == 'OK':
                return data
            else:
                print(
                    f"Polygon.io error for {symbol}: {data.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Error fetching Polygon.io data for {symbol}: {e}")
            return None

    def get_multiple_api_data(self, symbol: str) -> Dict:
        """
        Get data from multiple APIs for comprehensive analysis
        """
        results = {
            'symbol': symbol,
            'yfinance': {},
            'alpha_vantage': {},
            'iex_cloud': {},
            'polygon': {}
        }

        # Yahoo Finance data
        try:
            yf_data = self.get_yfinance_data([symbol], period='6mo')
            if not yf_data.empty:
                results['yfinance'] = {
                    'current_price': yf_data[symbol].iloc[-1],
                    'price_change': yf_data[symbol].pct_change().iloc[-1],
                    'data_points': len(yf_data)
                }
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")

        # Alpha Vantage data
        av_data = self.get_alpha_vantage_data(symbol)
        if av_data and 'Time Series (Daily)' in av_data:
            time_series = av_data['Time Series (Daily)']
            latest_date = list(time_series.keys())[0]
            results['alpha_vantage'] = {
                'latest_close': float(time_series[latest_date]['4. close']),
                'volume': int(time_series[latest_date]['5. volume'])
            }

        # IEX Cloud data
        iex_data = self.get_iex_cloud_data(symbol)
        if iex_data:
            results['iex_cloud'] = {
                'latest_price': iex_data.get('latestPrice'),
                'change_percent': iex_data.get('changePercent'),
                'market_cap': iex_data.get('marketCap')
            }

        # Polygon.io data
        poly_data = self.get_polygon_data(symbol)
        if poly_data and 'results' in poly_data:
            latest_result = poly_data['results'][-1]
            results['polygon'] = {
                'close_price': latest_result.get('c'),
                'volume': latest_result.get('v'),
                'transactions': latest_result.get('n')
            }

        return results

    def get_market_summary(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get market summary for multiple symbols
        """
        summary_data = []

        for symbol in symbols:
            print(f"Processing {symbol}...")
            data = self.get_multiple_api_data(symbol)

            # Extract best available price
            price_sources = [
                data.get('yfinance', {}).get('current_price'),
                data.get('alpha_vantage', {}).get('latest_close'),
                data.get('iex_cloud', {}).get('latest_price'),
                data.get('polygon', {}).get('close_price')
            ]
            current_price = next(
                (p for p in price_sources if p is not None), None)

            summary_data.append({
                'symbol': symbol,
                'current_price': current_price,
                'source_used': self._get_primary_source(data),
                'data_quality': self._assess_data_quality(data)
            })

            # Rate limiting
            time.sleep(0.5)

        return pd.DataFrame(summary_data)

    def _get_primary_source(self, data: Dict) -> str:
        """Determine primary data source"""
        sources = ['yfinance', 'alpha_vantage', 'iex_cloud', 'polygon']
        for source in sources:
            if data.get(source):
                return source
        return 'none'

    def _assess_data_quality(self, data: Dict) -> str:
        """Assess quality of available data"""
        available_sources = sum(1 for source in ['yfinance', 'alpha_vantage', 'iex_cloud', 'polygon']
                                if data.get(source))

        if available_sources >= 3:
            return 'excellent'
        elif available_sources == 2:
            return 'good'
        elif available_sources == 1:
            return 'fair'
        else:
            return 'poor'


def demonstrate_market_apis():
    """
    Demonstrate market data API integration
    """
    print("Market Data APIs Demonstration")
    print("=" * 50)

    api_client = MarketDataAPI()

    # Test symbols
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

    # Get market summary
    print("\n1. Market Summary:")
    summary = api_client.get_market_summary(test_symbols)
    print(summary)

    # Detailed data for one symbol
    print(f"\n2. Detailed Data for AAPL:")
    detailed_data = api_client.get_multiple_api_data('AAPL')
    print(json.dumps(detailed_data, indent=2, default=str))

    # Historical data using Yahoo Finance
    print(f"\n3. Historical Data (Yahoo Finance):")
    historical_data = api_client.get_yfinance_data(test_symbols, period='3mo')
    print(f"Retrieved {len(historical_data)} data points for each symbol")
    print(historical_data.tail())


if __name__ == "__main__":
    demonstrate_market_apis()
