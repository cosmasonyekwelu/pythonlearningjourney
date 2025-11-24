"""
Python Learning Journey - Day Thirty Two
Topic: Market Data APIs & Portfolio Performance Metrics
Date: October 23, 2025
Author: Cosmas Onyekwelu
"""

from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
from datetime import datetime
import json
import requests
import yfinance as yf
import numpy as np
import pandas as pd

load_dotenv()


class PortfolioAnalyzer: 
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_portfolio_returns(self, portfolio, start_date, end_date):
        """
        portfolio: dict of {symbol: weight}
        """
        returns_data = {}

        for symbol, weight in portfolio.items():
            try:
                stock_data = yf.download(
                    symbol, start=start_date, end=end_date)
                returns = stock_data['Close'].pct_change().dropna()
                returns_data[symbol] = returns * weight
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")

        # Create DataFrame properly with the index from one of the return series
        if returns_data:
            portfolio_returns = pd.DataFrame(returns_data).sum(axis=1)
            return portfolio_returns
        else:
            return pd.Series(dtype=float)

    def calculate_metrics(self, portfolio_returns, benchmark_returns=None):
        if portfolio_returns.empty:
            return {}

        metrics = {}

        # Total return
        metrics['total_return'] = (portfolio_returns + 1).prod() - 1

        # Annualized return
        metrics['annualized_return'] = (
            1 + metrics['total_return']) ** (252/len(portfolio_returns)) - 1

        # Volatility
        metrics['volatility'] = portfolio_returns.std() * np.sqrt(252)

        # Sharpe ratio
        risk_free_rate = 0.02
        excess_returns = metrics['annualized_return'] - risk_free_rate
        metrics['sharpe_ratio'] = excess_returns / \
            metrics['volatility'] if metrics['volatility'] != 0 else 0

        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        metrics['max_drawdown'] = drawdown.min()

        # Alpha and Beta
        if benchmark_returns is not None and not benchmark_returns.empty:
            # Align the dates
            aligned_data = pd.concat(
                [portfolio_returns, benchmark_returns], axis=1, join='inner')
            aligned_data.columns = ['portfolio', 'benchmark']

            covariance = aligned_data['portfolio'].cov(
                aligned_data['benchmark'])
            benchmark_variance = aligned_data['benchmark'].var()
            metrics['beta'] = covariance / \
                benchmark_variance if benchmark_variance != 0 else 0

            benchmark_total_return = (aligned_data['benchmark'] + 1).prod() - 1
            metrics['alpha'] = metrics['total_return'] - \
                (risk_free_rate + metrics['beta'] *
                 (benchmark_total_return - risk_free_rate))

        return metrics

    def get_benchmark_returns(self, benchmark_symbol, start_date, end_date):
        """Get benchmark data for comparison"""
        try:
            benchmark_data = yf.download(
                benchmark_symbol, start=start_date, end=end_date)
            return benchmark_data['Close'].pct_change().dropna()
        except Exception as e:
            print(f"Error fetching benchmark: {e}")
            return pd.Series(dtype=float)


def demonstrate_portfolio_analysis():
    """Main demonstration function"""
    print("Portfolio Analysis Demo")
    print("=" * 40)

    # Initialize analyzer
    analyzer = PortfolioAnalyzer()

    # Sample portfolio
    portfolio = {'AAPL': 0.4, 'GOOGL': 0.3, 'MSFT': 0.3}

    # Get portfolio returns
    returns = analyzer.get_portfolio_returns(
        portfolio, '2023-01-01', '2024-01-01')

    if returns.empty:
        print("No data retrieved. Please check your internet connection and symbols.")
        return

    # Get benchmark returns
    benchmark_returns = analyzer.get_benchmark_returns(
        'SPY', '2023-01-01', '2024-01-01')

    # Calculate metrics
    metrics = analyzer.calculate_metrics(returns, benchmark_returns)

    # Display results
    print("\nPortfolio Performance Metrics:")
    print("-" * 30)
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"{metric:20}: {value:>8.4f}")
        else:
            print(f"{metric:20}: {value:>8}")

    # Basic plot
    cumulative_returns = (1 + returns).cumprod()
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_returns.index,
             cumulative_returns.values, label='Portfolio')

    if not benchmark_returns.empty:
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        plt.plot(benchmark_cumulative.index,
                 benchmark_cumulative.values, label='SPY Benchmark', alpha=0.7)

    plt.title('Portfolio Cumulative Returns')
    plt.ylabel('Cumulative Return')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    demonstrate_portfolio_analysis()
