"""
Data Collection Module
Handles stock data fetching, caching, and management
"""

import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
import pickle
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

load_dotenv()


class DataCollector:
    """
    Handles stock data collection with caching and multiple data sources
    """

    def __init__(self, cache_dir='data/cache', cache_duration=3600):
        self.cache_dir = cache_dir
        self.cache_duration = cache_duration
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs('data/exports', exist_ok=True)

    def get_stock_data(self, symbol: str, period: str = '1y',
                       interval: str = '1d', use_cache: bool = True) -> pd.DataFrame:
        """
        Get stock data with caching support
        """
        cache_key = f"{symbol}_{period}_{interval}.pkl"
        cache_path = os.path.join(self.cache_dir, cache_key)

        # Check cache first
        if use_cache and os.path.exists(cache_path):
            cache_age = time.time() - os.path.getmtime(cache_path)
            if cache_age < self.cache_duration:
                try:
                    with open(cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    print(f"Loaded {symbol} data from cache")
                    return cached_data
                except Exception as e:
                    print(f"Cache load error for {symbol}: {e}")

        # Fetch fresh data
        try:
            print(f"Fetching data for {symbol}...")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)

            if data.empty:
                print(f"No data available for {symbol}")
                return pd.DataFrame()

            # Add symbol column
            data['Symbol'] = symbol

            # Calculate additional metrics
            data = self._enhance_data(data)

            # Cache the data
            if use_cache:
                try:
                    with open(cache_path, 'wb') as f:
                        pickle.dump(data, f)
                except Exception as e:
                    print(f"Cache save error for {symbol}: {e}")

            return data

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_multiple_stocks(self, symbols: List[str], period: str = '1y',
                            interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple stocks
        """
        stock_data = {}

        for symbol in symbols:
            data = self.get_stock_data(symbol, period, interval)
            if not data.empty:
                stock_data[symbol] = data
            else:
                print(f"Skipping {symbol} - no data available")

        return stock_data

    def get_fundamental_data(self, symbol: str) -> Dict:
        """
        Get fundamental data from Yahoo Finance and Alpha Vantage
        """
        fundamental_data = {}

        try:
            # Yahoo Finance fundamentals
            ticker = yf.Ticker(symbol)
            info = ticker.info

            fundamental_data = {
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'analyst_recommendation': info.get('recommendationKey', 'N/A')
            }

            # Clean None values
            fundamental_data = {k: (v if v is not None else 'N/A')
                                for k, v in fundamental_data.items()}

        except Exception as e:
            print(f"Error getting fundamental data for {symbol}: {e}")

        # Try Alpha Vantage for enhanced data
        if self.alpha_vantage_key:
            av_data = self._get_alpha_vantage_fundamentals(symbol)
            if av_data:
                fundamental_data.update(av_data)

        return fundamental_data

    def _enhance_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Enhance raw data with additional calculations
        """
        enhanced_data = data.copy()

        # Basic calculations
        enhanced_data['Daily_Return'] = enhanced_data['Close'].pct_change()
        enhanced_data['Cumulative_Return'] = (
            1 + enhanced_data['Daily_Return']).cumprod() - 1
        enhanced_data['Price_Change'] = enhanced_data['Close'].diff()

        # Volume analysis
        enhanced_data['Volume_SMA'] = enhanced_data['Volume'].rolling(
            window=20).mean()
        enhanced_data['Volume_Ratio'] = enhanced_data['Volume'] / \
            enhanced_data['Volume_SMA']

        # High-Low analysis
        enhanced_data['HL_Range'] = (
            enhanced_data['High'] - enhanced_data['Low']) / enhanced_data['Close']
        enhanced_data['HL_Pct'] = (
            enhanced_data['High'] - enhanced_data['Low']) / enhanced_data['Low']

        return enhanced_data

    def _get_alpha_vantage_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data from Alpha Vantage
        """
        if not self.alpha_vantage_key:
            return {}

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }

            response = requests.get(url, params=params)
            data = response.json()

            if 'Error Message' in data:
                return {}

            return {
                'av_description': data.get('Description', 'N/A'),
                'av_eps': data.get('EPS', 'N/A'),
                'av_pe_ratio': data.get('PERatio', 'N/A'),
                'av_peg_ratio': data.get('PEGRatio', 'N/A'),
                'av_book_value': data.get('BookValue', 'N/A'),
                'av_dividend_per_share': data.get('DividendPerShare', 'N/A'),
                'av_dividend_yield': data.get('DividendYield', 'N/A'),
                'av_profit_margin': data.get('ProfitMargin', 'N/A'),
                'av_operating_margin': data.get('OperatingMarginTTM', 'N/A'),
                'av_return_on_assets': data.get('ReturnOnAssetsTTM', 'N/A'),
                'av_return_on_equity': data.get('ReturnOnEquityTTM', 'N/A'),
                'av_revenue_ttm': data.get('RevenueTTM', 'N/A'),
                'av_gross_profit_ttm': data.get('GrossProfitTTM', 'N/A')
            }

        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return {}

    def clear_cache(self, older_than_days: int = 7):
        """
        Clear cache files older than specified days
        """
        cutoff_time = time.time() - (older_than_days * 24 * 3600)

        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                print(f"Removed cache file: {filename}")

    def get_available_symbols(self) -> List[str]:
        """
        Get list of commonly analyzed symbols
        """
        common_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'JNJ', 'V', 'PG', 'UNH', 'HD', 'DIS', 'PYPL', 'NFLX', 'ADBE',
            'CRM', 'INTC', 'CSCO', 'PEP', 'T', 'ABT', 'TMO', 'COST', 'AVGO',
            'TXN', 'LLY', 'XOM', 'WMT', 'CVX', 'MA', 'BAC', 'ABBV', 'KO'
        ]
        return common_symbols


# Singleton instance
data_collector = DataCollector()
