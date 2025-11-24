"""
Fundamental Data Analysis
Integration with fundamental data APIs for comprehensive analysis
"""

import yfinance as yf
import pandas as pd
import requests
import json
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class FundamentalAnalyzer:
    """
    Analyze fundamental data for stocks
    """

    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    def get_yfinance_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data from Yahoo Finance
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            fundamentals = {
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
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'earnings_growth': info.get('earningsGrowth'),
                'revenue_growth': info.get('revenueGrowth'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow')
            }

            # Clean None values
            fundamentals = {k: (v if v is not None else 'N/A')
                            for k, v in fundamentals.items()}

            return fundamentals

        except Exception as e:
            print(
                f"Error getting Yahoo Finance fundamentals for {symbol}: {e}")
            return {}

    def get_alpha_vantage_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data from Alpha Vantage
        """
        if not self.alpha_vantage_key:
            print("Alpha Vantage API key not found")
            return {}

        base_url = "https://www.alphavantage.co/query"
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if 'Error Message' in data:
                print(
                    f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                return {}
            elif 'Note' in data:
                print(f"Alpha Vantage rate limit: {data['Note']}")
                return {}
            else:
                return data

        except Exception as e:
            print(
                f"Error fetching Alpha Vantage fundamentals for {symbol}: {e}")
            return {}

    def calculate_valuation_metrics(self, symbol: str) -> Dict:
        """
        Calculate comprehensive valuation metrics
        """
        yf_data = self.get_yfinance_fundamentals(symbol)
        av_data = self.get_alpha_vantage_fundamentals(symbol)

        metrics = {}

        # Price-based metrics
        metrics['pe_ratio'] = yf_data.get('pe_ratio', av_data.get('PERatio'))
        metrics['forward_pe'] = yf_data.get('forward_pe')
        metrics['price_to_book'] = yf_data.get(
            'price_to_book', av_data.get('PriceToBookRatio'))
        metrics['price_to_sales'] = yf_data.get(
            'price_to_sales', av_data.get('PriceToSalesRatio'))

        # Growth metrics
        metrics['peg_ratio'] = yf_data.get(
            'peg_ratio', av_data.get('PEGRatio'))
        metrics['earnings_growth'] = yf_data.get(
            'earnings_growth', av_data.get('QuarterlyEarningsGrowthYOY'))
        metrics['revenue_growth'] = yf_data.get(
            'revenue_growth', av_data.get('QuarterlyRevenueGrowthYOY'))

        # Profitability metrics
        metrics['profit_margin'] = yf_data.get(
            'profit_margin', av_data.get('ProfitMargin'))
        metrics['operating_margin'] = yf_data.get(
            'operating_margin', av_data.get('OperatingMarginTTM'))
        metrics['return_on_equity'] = yf_data.get(
            'return_on_equity', av_data.get('ReturnOnEquityTTM'))

        # Financial health metrics
        metrics['debt_to_equity'] = yf_data.get(
            'debt_to_equity', av_data.get('DebtToEquity'))
        metrics['current_ratio'] = yf_data.get(
            'current_ratio', av_data.get('CurrentRatio'))

        # Dividend metrics
        metrics['dividend_yield'] = yf_data.get(
            'dividend_yield', av_data.get('DividendYield'))
        metrics['payout_ratio'] = yf_data.get(
            'payout_ratio', av_data.get('PayoutRatio'))

        return metrics

    def generate_fundamental_report(self, symbol: str) -> Dict:
        """
        Generate comprehensive fundamental analysis report
        """
        yf_data = self.get_yfinance_fundamentals(symbol)
        av_data = self.get_alpha_vantage_fundamentals(symbol)
        valuation_metrics = self.calculate_valuation_metrics(symbol)

        report = {
            'company_info': {
                'name': yf_data.get('company_name', av_data.get('Name', 'N/A')),
                'sector': yf_data.get('sector', av_data.get('Sector', 'N/A')),
                'industry': yf_data.get('industry', av_data.get('Industry', 'N/A')),
                'description': av_data.get('Description', 'N/A')
            },
            'valuation': valuation_metrics,
            'financial_health': {
                'market_cap': yf_data.get('market_cap', av_data.get('MarketCapitalization')),
                'debt_to_equity': valuation_metrics.get('debt_to_equity'),
                'current_ratio': valuation_metrics.get('current_ratio'),
                'quick_ratio': yf_data.get('quick_ratio')
            },
            'profitability': {
                'profit_margin': valuation_metrics.get('profit_margin'),
                'operating_margin': valuation_metrics.get('operating_margin'),
                'return_on_equity': valuation_metrics.get('return_on_equity'),
                'return_on_assets': yf_data.get('return_on_assets')
            },
            'growth': {
                'earnings_growth': valuation_metrics.get('earnings_growth'),
                'revenue_growth': valuation_metrics.get('revenue_growth'),
                'peg_ratio': valuation_metrics.get('peg_ratio')
            }
        }

        return report

    def compare_companies(self, symbols: List[str]) -> pd.DataFrame:
        """
        Compare fundamental metrics across multiple companies
        """
        comparison_data = []

        for symbol in symbols:
            print(f"Analyzing {symbol}...")
            report = self.generate_fundamental_report(symbol)

            # Extract key metrics for comparison
            metrics = {
                'symbol': symbol,
                'company_name': report['company_info']['name'],
                'sector': report['company_info']['sector'],
                'pe_ratio': report['valuation'].get('pe_ratio', 'N/A'),
                'price_to_book': report['valuation'].get('price_to_book', 'N/A'),
                'profit_margin': report['profitability'].get('profit_margin', 'N/A'),
                'return_on_equity': report['profitability'].get('return_on_equity', 'N/A'),
                'debt_to_equity': report['financial_health'].get('debt_to_equity', 'N/A'),
                'dividend_yield': report['valuation'].get('dividend_yield', 'N/A')
            }

            comparison_data.append(metrics)

        return pd.DataFrame(comparison_data)


def demonstrate_fundamental_analysis():
    """
    Demonstrate fundamental analysis capabilities
    """
    print("Fundamental Analysis Demonstration")
    print("=" * 45)

    analyzer = FundamentalAnalyzer()

    # Test symbols
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'JNJ', 'JPM']

    # Generate report for one company
    print("\n1. Fundamental Report for Apple (AAPL):")
    aapl_report = analyzer.generate_fundamental_report('AAPL')

    print(f"\nCompany Info:")
    for key, value in aapl_report['company_info'].items():
        if key != 'description':  # Skip long description
            print(f"  {key}: {value}")

    print(f"\nValuation Metrics:")
    for key, value in aapl_report['valuation'].items():
        print(f"  {key}: {value}")

    # Compare multiple companies
    print(f"\n2. Company Comparison:")
    comparison_df = analyzer.compare_companies(test_symbols)
    print(comparison_df.to_string(index=False))

    # Analyze specific metrics
    print(f"\n3. Key Financial Health Metrics:")
    health_metrics = ['debt_to_equity', 'current_ratio',
                      'profit_margin', 'return_on_equity']
    for symbol in test_symbols:
        report = analyzer.generate_fundamental_report(symbol)
        print(f"\n{symbol}:")
        for metric in health_metrics:
            value = report['financial_health'].get(
                metric) or report['profitability'].get(metric)
            print(f"  {metric}: {value}")


if __name__ == "__main__":
    demonstrate_fundamental_analysis()
