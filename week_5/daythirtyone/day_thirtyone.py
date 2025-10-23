"""
Python Learning Journey - Day Thirty One
Topic: Pandas for Financial Data & Basic Financial Calculations
Date: October 22, 2025
Author: Cosmas Onyekwelu
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class FinancialDataProcessor:
    """
    Process and analyze financial data using pandas
    """

    def __init__(self):
        self.data = None
        self.returns = None

    def fetch_stock_data(self, symbols, period='1y'):
        """
        Fetch stock data for multiple symbols
        """
        print(f"Fetching data for {len(symbols)} symbols...")

        data_dict = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)
                if not hist.empty:
                    data_dict[symbol] = hist[['Close', 'Volume']]
                    data_dict[symbol].columns = [
                        f'{symbol}_Close', f'{symbol}_Volume']
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")

        if data_dict:
            self.data = pd.concat(data_dict.values(), axis=1)
            print(f"Successfully fetched data for {len(data_dict)} symbols")
            return self.data
        else:
            raise ValueError("No data could be fetched")

    def calculate_returns(self):
        """
        Calculate various types of returns
        """
        if self.data is None:
            raise ValueError("No data available. Please fetch data first.")

        close_columns = [col for col in self.data.columns if 'Close' in col]
        returns_data = {}

        for col in close_columns:
            symbol = col.replace('_Close', '')

            # Daily returns
            daily_returns = self.data[col].pct_change()

            # Log returns
            log_returns = np.log(self.data[col] / self.data[col].shift(1))

            # Cumulative returns
            cumulative_returns = (1 + daily_returns).cumprod() - 1

            returns_data[f'{symbol}_DailyReturn'] = daily_returns
            returns_data[f'{symbol}_LogReturn'] = log_returns
            returns_data[f'{symbol}_CumulativeReturn'] = cumulative_returns

        self.returns = pd.DataFrame(returns_data)
        return self.returns

    def calculate_rolling_statistics(self, window=20):
        """
        Calculate rolling statistics for price and returns
        """
        if self.data is None:
            raise ValueError("No data available")

        rolling_stats = {}
        close_columns = [col for col in self.data.columns if 'Close' in col]

        for col in close_columns:
            symbol = col.replace('_Close', '')

            # Rolling mean and standard deviation
            rolling_mean = self.data[col].rolling(window=window).mean()
            rolling_std = self.data[col].rolling(window=window).std()

            # Rolling min and max
            rolling_min = self.data[col].rolling(window=window).min()
            rolling_max = self.data[col].rolling(window=window).max()

            # Bollinger Bands
            bb_upper = rolling_mean + (2 * rolling_std)
            bb_lower = rolling_mean - (2 * rolling_std)

            rolling_stats[f'{symbol}_RollingMean'] = rolling_mean
            rolling_stats[f'{symbol}_RollingStd'] = rolling_std
            rolling_stats[f'{symbol}_BB_Upper'] = bb_upper
            rolling_stats[f'{symbol}_BB_Lower'] = bb_lower

        return pd.DataFrame(rolling_stats)

    def resample_data(self, frequency='W'):
        """
        Resample data to different frequencies
        """
        if self.data is None:
            raise ValueError("No data available")

        resampled_data = {}

        for col in self.data.columns:
            if 'Close' in col:
                # OHLC resampling
                resampled = self.data[col].resample(frequency).ohlc()
                for ohlc_col in resampled.columns:
                    resampled_data[f"{col}_{ohlc_col}"] = resampled[ohlc_col]
            elif 'Volume' in col:
                # Volume resampling (sum)
                resampled_data[f"{col}_Sum"] = self.data[col].resample(
                    frequency).sum()

        return pd.DataFrame(resampled_data)

    def calculate_volatility(self, window=21):
        """
        Calculate rolling volatility (annualized)
        """
        if self.returns is None:
            self.calculate_returns()

        volatility_data = {}
        return_columns = [
            col for col in self.returns.columns if 'DailyReturn' in col]

        for col in return_columns:
            symbol = col.replace('_DailyReturn', '')
            # Rolling volatility (annualized)
            rolling_vol = self.returns[col].rolling(
                window=window).std() * np.sqrt(252)
            volatility_data[f'{symbol}_Volatility'] = rolling_vol

        return pd.DataFrame(volatility_data)

    def calculate_correlation_matrix(self):
        """
        Calculate correlation matrix between assets
        """
        if self.returns is None:
            self.calculate_returns()

        return_columns = [
            col for col in self.returns.columns if 'DailyReturn' in col]
        returns_subset = self.returns[return_columns].dropna()

        # Rename columns for better readability
        renamed_columns = [col.replace('_DailyReturn', '')
                           for col in returns_subset.columns]
        returns_subset.columns = renamed_columns

        correlation_matrix = returns_subset.corr()
        return correlation_matrix

    def analyze_stock(self, symbol, period='1y'):
        """
        Comprehensive stock analysis with key metrics
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)

            if hist.empty:
                return None, None

            # Calculate daily returns
            hist['Daily_Return'] = hist['Close'].pct_change()

            # Calculate moving averages
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()

            # Calculate volatility (annualized)
            daily_volatility = hist['Daily_Return'].std()
            annual_volatility = daily_volatility * np.sqrt(252)

            # Calculate Sharpe ratio (assuming risk-free rate = 0.02)
            excess_returns = hist['Daily_Return'].mean() - 0.02/252
            sharpe_ratio = excess_returns / daily_volatility * np.sqrt(252)

            analysis = {
                'symbol': symbol,
                'current_price': hist['Close'].iloc[-1],
                'total_return': (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100,
                'annual_volatility': annual_volatility * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': self.calculate_max_drawdown(hist['Close'])
            }

            return hist, analysis

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None, None

    def calculate_max_drawdown(self, prices):
        """
        Calculate maximum drawdown for price series
        """
        cumulative = prices / prices.cummax()
        return (1 - cumulative.min()) * 100


class PortfolioAnalyzer:
    """
    Analyze portfolio performance and risk metrics
    """

    def __init__(self, portfolio_data=None):
        self.portfolio = portfolio_data
        self.portfolio_data = None
        self.portfolio_returns = None

    def create_sample_portfolio(self):
        """
        Create a sample portfolio for demonstration
        """
        self.portfolio = pd.DataFrame({
            'symbol': ['AAPL', 'GOOGL', 'MSFT', 'JNJ', 'JPM'],
            'shares': [100, 50, 80, 60, 70],
            'purchase_price': [150.00, 2800.00, 300.00, 160.00, 140.00],
            'sector': ['Technology', 'Technology', 'Technology', 'Healthcare', 'Financial']
        })
        return self.portfolio

    def fetch_portfolio_data(self, period='1y'):
        """
        Fetch current data for portfolio assets
        """
        if self.portfolio is None:
            self.create_sample_portfolio()

        portfolio_data = {}

        for symbol in self.portfolio['symbol']:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)
                if not hist.empty:
                    portfolio_data[symbol] = hist['Close']
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

        self.portfolio_data = pd.DataFrame(portfolio_data)
        self._calculate_portfolio_weights()
        return self.portfolio_data

    def _calculate_portfolio_weights(self):
        """
        Calculate portfolio weights based on current prices
        """
        if self.portfolio_data is None:
            raise ValueError("No portfolio data available")

        # Get latest prices
        latest_prices = self.portfolio_data.iloc[-1]

        # Calculate current values and weights
        self.portfolio = self.portfolio.copy()
        self.portfolio['current_price'] = 0.0
        self.portfolio['current_value'] = 0.0
        self.portfolio['weight'] = 0.0

        for idx, row in self.portfolio.iterrows():
            symbol = row['symbol']
            if symbol in latest_prices:
                current_price = latest_prices[symbol]
                current_value = row['shares'] * current_price
                self.portfolio.at[idx, 'current_price'] = current_price
                self.portfolio.at[idx, 'current_value'] = current_value

        # Calculate weights
        total_value = self.portfolio['current_value'].sum()
        self.portfolio['weight'] = self.portfolio['current_value'] / total_value

        print(f"Portfolio Total Value: ${total_value:,.2f}")
        return self.portfolio

    def calculate_portfolio_returns(self):
        """
        Calculate portfolio returns
        """
        if self.portfolio_data is None:
            self.fetch_portfolio_data()

        # Calculate individual asset returns
        asset_returns = self.portfolio_data.pct_change().dropna()

        # Calculate portfolio returns (weighted average)
        weights = self.portfolio.set_index('symbol')['weight']
        portfolio_returns = pd.Series(index=asset_returns.index, dtype=float)

        for date in asset_returns.index:
            date_returns = asset_returns.loc[date]
            weighted_return = 0

            for symbol in weights.index:
                if symbol in date_returns:
                    weighted_return += weights[symbol] * date_returns[symbol]

            portfolio_returns[date] = weighted_return

        self.portfolio_returns = portfolio_returns
        return self.portfolio_returns

    def calculate_portfolio_metrics(self, risk_free_rate=0.02):
        """
        Calculate key portfolio performance metrics
        """
        if self.portfolio_returns is None:
            self.calculate_portfolio_returns()

        metrics = {}

        # Basic statistics
        metrics['total_return'] = (1 + self.portfolio_returns).prod() - 1
        metrics['annual_return'] = (
            1 + metrics['total_return']) ** (252/len(self.portfolio_returns)) - 1
        metrics['volatility'] = self.portfolio_returns.std() * np.sqrt(252)

        # Risk-adjusted metrics
        excess_returns = self.portfolio_returns - risk_free_rate/252
        metrics['sharpe_ratio'] = (excess_returns.mean(
        ) / self.portfolio_returns.std()) * np.sqrt(252)

        # Drawdown analysis
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        metrics['max_drawdown'] = drawdown.min()
        metrics['calmar_ratio'] = metrics['annual_return'] / \
            abs(metrics['max_drawdown']) if metrics['max_drawdown'] != 0 else 0

        # Additional metrics
        metrics['var_95'] = self.portfolio_returns.quantile(0.05)
        metrics['cvar_95'] = self.portfolio_returns[self.portfolio_returns <=
                                                    metrics['var_95']].mean()

        return metrics

    def calculate_sector_allocation(self):
        """
        Calculate portfolio allocation by sector
        """
        if self.portfolio is None:
            raise ValueError("No portfolio loaded")

        sector_allocation = self.portfolio.groupby(
            'sector')['current_value'].sum()
        sector_weights = sector_allocation / sector_allocation.sum()

        return sector_weights

    def generate_portfolio_report(self):
        """
        Generate comprehensive portfolio report
        """
        if self.portfolio_data is None:
            self.fetch_portfolio_data()

        metrics = self.calculate_portfolio_metrics()
        sector_allocation = self.calculate_sector_allocation()

        print("PORTFOLIO ANALYSIS REPORT")
        print("=" * 50)

        print(f"\nPortfolio Composition:")
        display_cols = ['symbol', 'shares',
                        'current_price', 'current_value', 'weight']
        print(self.portfolio[display_cols].to_string(
            index=False, float_format='%.2f'))

        print(f"\nSector Allocation:")
        for sector, weight in sector_allocation.items():
            print(f"  {sector}: {weight:.2%}")

        print(f"\nPerformance Metrics:")
        print(f"  Total Return: {metrics['total_return']:.2%}")
        print(f"  Annual Return: {metrics['annual_return']:.2%}")
        print(f"  Annual Volatility: {metrics['volatility']:.2%}")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"  Maximum Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"  Calmar Ratio: {metrics['calmar_ratio']:.2f}")
        print(f"  VaR (95%): {metrics['var_95']:.2%}")
        print(f"  CVaR (95%): {metrics['cvar_95']:.2%}")

        return metrics

    def plot_portfolio_performance(self):
        """
        Plot portfolio performance vs individual assets
        """
        if self.portfolio_returns is None:
            self.calculate_portfolio_returns()

        # Cumulative returns
        portfolio_cumulative = (1 + self.portfolio_returns).cumprod()
        asset_cumulative = (
            1 + self.portfolio_data.pct_change().dropna()).cumprod()

        plt.figure(figsize=(12, 8))

        # Plot individual assets
        for symbol in asset_cumulative.columns:
            plt.plot(asset_cumulative.index, asset_cumulative[symbol],
                     alpha=0.3, label=f'{symbol}')

        # Plot portfolio
        plt.plot(portfolio_cumulative.index, portfolio_cumulative.values,
                 linewidth=3, color='black', label='Portfolio')

        plt.title('Portfolio Performance vs Individual Assets')
        plt.ylabel('Cumulative Return')
        plt.xlabel('Date')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


class RiskMetricsCalculator:
    """
    Calculate advanced risk metrics for financial assets
    """

    def __init__(self, returns_data=None):
        self.returns = returns_data
        self.metrics = {}

    def set_returns_data(self, returns_data):
        """
        Set returns data for analysis
        """
        self.returns = returns_data

    def calculate_basic_risk_metrics(self):
        """
        Calculate basic risk metrics
        """
        if self.returns is None:
            raise ValueError("No returns data available")

        basic_metrics = {}

        for column in self.returns.columns:
            returns = self.returns[column].dropna()

            metrics = {
                'mean_return': returns.mean() * 252,
                'volatility': returns.std() * np.sqrt(252),
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252),
                'var_95': returns.quantile(0.05),
                'cvar_95': returns[returns <= returns.quantile(0.05)].mean()
            }

            basic_metrics[column] = metrics

        return pd.DataFrame(basic_metrics).T

    def calculate_max_drawdown(self, prices):
        """
        Calculate maximum drawdown for price series
        """
        cumulative_returns = (1 + prices.pct_change().fillna(0)).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        return max_drawdown

    def calculate_beta(self, asset_returns, market_returns='^GSPC'):
        """
        Calculate beta coefficient relative to market
        """
        if isinstance(market_returns, str):
            # Fetch market data if symbol provided
            market_data = yf.download(market_returns, start=asset_returns.index[0],
                                      end=asset_returns.index[-1])['Close']
            market_returns = market_data.pct_change().dropna()

        # Align dates
        aligned_data = pd.concat(
            [asset_returns, market_returns], axis=1, join='inner')
        aligned_data.columns = ['asset', 'market']

        # Calculate covariance and variance
        covariance = aligned_data[['asset', 'market']].cov().iloc[0, 1]
        market_variance = aligned_data['market'].var()

        beta = covariance / market_variance
        return beta

    def calculate_treynor_ratio(self, asset_returns, market_returns='^GSPC', risk_free_rate=0.02):
        """
        Calculate Treynor ratio (return per unit of systematic risk)
        """
        beta = self.calculate_beta(asset_returns, market_returns)
        excess_return = asset_returns.mean() * 252 - risk_free_rate
        treynor_ratio = excess_return / beta if beta != 0 else 0

        return treynor_ratio

    def calculate_jensens_alpha(self, asset_returns, market_returns='^GSPC', risk_free_rate=0.02):
        """
        Calculate Jensen's alpha (excess return over CAPM)
        """
        beta = self.calculate_beta(asset_returns, market_returns)

        if isinstance(market_returns, str):
            market_data = yf.download(market_returns, start=asset_returns.index[0],
                                      end=asset_returns.index[-1])['Close']
            market_returns_data = market_data.pct_change().dropna()
        else:
            market_returns_data = market_returns

        # Align data
        aligned_data = pd.concat(
            [asset_returns, market_returns_data], axis=1, join='inner')
        aligned_data.columns = ['asset', 'market']

        # Calculate expected return using CAPM
        market_return_annual = aligned_data['market'].mean() * 252
        expected_return = risk_free_rate + beta * \
            (market_return_annual - risk_free_rate)

        # Calculate actual return
        actual_return = aligned_data['asset'].mean() * 252

        # Jensen's alpha
        alpha = actual_return - expected_return

        return alpha

    def generate_risk_report(self):
        """
        Generate comprehensive risk report
        """
        if self.returns is None:
            raise ValueError("No returns data available")

        print("COMPREHENSIVE RISK ANALYSIS REPORT")
        print("=" * 50)

        # Basic metrics
        basic_metrics = self.calculate_basic_risk_metrics()
        print("\nBasic Risk Metrics:")
        print(basic_metrics.round(4))

        # Advanced metrics for first asset
        first_asset = self.returns.columns[0]
        asset_returns = self.returns[first_asset].dropna()

        print(f"\nAdvanced Metrics for {first_asset}:")
        try:
            beta = self.calculate_beta(asset_returns)
            treynor = self.calculate_treynor_ratio(asset_returns)
            alpha = self.calculate_jensens_alpha(asset_returns)

            print(f"  Beta: {beta:.4f}")
            print(f"  Treynor Ratio: {treynor:.4f}")
            print(f"  Jensen's Alpha: {alpha:.4f}")
        except Exception as e:
            print(f"  Could not calculate advanced metrics: {e}")

        return {
            'basic_metrics': basic_metrics
        }


class FinancialTimeSeries:
    """
    Advanced time series analysis for financial data
    """

    def __init__(self):
        self.data = None

    def create_price_features(self, price_series):
        """
        Create technical features from price series
        """
        features = pd.DataFrame(index=price_series.index)
        features['price'] = price_series

        # Lagged prices
        for lag in [1, 5, 10, 20]:
            features[f'price_lag_{lag}'] = price_series.shift(lag)

        # Moving averages
        features['sma_10'] = price_series.rolling(window=10).mean()
        features['sma_30'] = price_series.rolling(window=30).mean()
        features['sma_50'] = price_series.rolling(window=50).mean()

        # Exponential moving averages
        features['ema_12'] = price_series.ewm(span=12).mean()
        features['ema_26'] = price_series.ewm(span=26).mean()

        # Price momentum
        features['momentum_5'] = price_series / price_series.shift(5) - 1
        features['momentum_10'] = price_series / price_series.shift(10) - 1
        features['momentum_20'] = price_series / price_series.shift(20) - 1

        # Volatility features
        features['volatility_10'] = price_series.pct_change().rolling(
            window=10).std()
        features['volatility_20'] = price_series.pct_change().rolling(
            window=20).std()

        return features.dropna()

    def analyze_seasonality(self, price_series):
        """
        Analyze seasonal patterns in financial data
        """
        returns = price_series.pct_change().dropna()

        # Extract time features
        time_features = pd.DataFrame(index=returns.index)
        time_features['day_of_week'] = returns.index.dayofweek
        time_features['day_of_month'] = returns.index.day
        time_features['month'] = returns.index.month
        time_features['quarter'] = returns.index.quarter

        # Calculate average returns by time period
        seasonal_patterns = {}

        seasonal_patterns['day_of_week'] = returns.groupby(
            time_features['day_of_week']).mean()
        seasonal_patterns['month'] = returns.groupby(
            time_features['month']).mean()
        seasonal_patterns['quarter'] = returns.groupby(
            time_features['quarter']).mean()

        return seasonal_patterns

    def calculate_autocorrelation(self, series, lags=20):
        """
        Calculate autocorrelation for different lags
        """
        autocorrelations = []

        for lag in range(1, lags + 1):
            autocorr = series.autocorr(lag=lag)
            autocorrelations.append(autocorr)

        return pd.Series(autocorrelations, index=range(1, lags + 1))


def demonstrate_pandas_operations():
    """
    Demonstrate key pandas operations for financial data
    """
    print("Pandas Financial Operations Demonstration")
    print("=" * 50)

    # Initialize processor
    processor = FinancialDataProcessor()

    # Sample symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'JNJ', 'JPM']

    try:
        # Fetch data
        data = processor.fetch_stock_data(symbols, '6mo')
        print(f"\nData Shape: {data.shape}")
        print(f"Data Columns: {list(data.columns)}")
        print(f"Date Range: {data.index.min()} to {data.index.max()}")

        # Calculate returns
        returns = processor.calculate_returns()
        print(f"\nReturns Statistics:")
        print(returns.describe())

        # Rolling statistics
        rolling_stats = processor.calculate_rolling_statistics(window=20)
        print(f"\nRolling Statistics (first 5 rows):")
        print(rolling_stats.head())

        # Volatility
        volatility = processor.calculate_volatility()
        print(f"\nRecent Volatility (annualized):")
        print(volatility.tail())

        # Correlation matrix
        correlation_matrix = processor.calculate_correlation_matrix()
        print(f"\nCorrelation Matrix:")
        print(correlation_matrix)

        # Resample data
        weekly_data = processor.resample_data('W')
        print(f"\nWeekly Resampled Data (first 3 rows):")
        print(weekly_data.head(3))

    except Exception as e:
        print(f"Error in demonstration: {e}")


def demonstrate_portfolio_analysis():
    """
    Demonstrate portfolio analysis
    """
    print("\nPortfolio Analysis Demonstration")
    print("=" * 40)

    # Create analyzer and load portfolio
    analyzer = PortfolioAnalyzer()

    # Fetch data and generate report
    analyzer.fetch_portfolio_data(period='1y')
    analyzer.generate_portfolio_report()

    # Plot performance
    analyzer.plot_portfolio_performance()


def demonstrate_risk_metrics():
    """
    Demonstrate risk metrics calculation
    """
    print("\nRisk Metrics Calculation Demonstration")
    print("=" * 45)

    # Fetch sample data
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    data = {}

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1y')
        data[symbol] = hist['Close']

    price_data = pd.DataFrame(data)
    returns_data = price_data.pct_change().dropna()

    # Initialize calculator
    risk_calc = RiskMetricsCalculator(returns_data)

    # Generate report
    report = risk_calc.generate_risk_report()

    # Plot rolling volatility
    rolling_vol = returns_data.rolling(window=21).std() * np.sqrt(252)

    plt.figure(figsize=(12, 6))
    for column in rolling_vol.columns:
        plt.plot(rolling_vol.index, rolling_vol[column], label=column)

    plt.title('Rolling Annualized Volatility (21-day window)')
    plt.ylabel('Volatility')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def demonstrate_time_series_analysis():
    """
    Demonstrate time series analysis techniques
    """
    print("\nFinancial Time Series Analysis Demonstration")
    print("=" * 50)

    # Initialize analyzer
    ts_analyzer = FinancialTimeSeries()

    # Fetch data for AAPL
    stock = yf.Ticker('AAPL')
    hist = stock.history(period='2y')
    prices = hist['Close']

    # Feature engineering
    features = ts_analyzer.create_price_features(prices)
    print(f"Generated {len(features.columns)} technical features")
    print("Feature columns:", list(features.columns))

    # Seasonality analysis
    seasonal_patterns = ts_analyzer.analyze_seasonality(prices)
    print(f"\nSeasonal Patterns - Average Daily Returns:")
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    for i, day in enumerate(days):
        if i in seasonal_patterns['day_of_week'].index:
            ret = seasonal_patterns['day_of_week'].loc[i]
            print(f"  {day}: {ret:.4%}")

    # Autocorrelation analysis
    returns = prices.pct_change().dropna()
    autocorr = ts_analyzer.calculate_autocorrelation(returns, lags=10)
    print(f"\nAutocorrelation of Returns (lags 1-10):")
    for lag, corr in autocorr.items():
        print(f"  Lag {lag}: {corr:.4f}")

    # Plot autocorrelation
    plt.figure(figsize=(10, 6))
    plt.bar(autocorr.index, autocorr.values)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.axhline(y=0.1, color='red', linestyle='--',
                alpha=0.5, label='Significance level')
    plt.axhline(y=-0.1, color='red', linestyle='--', alpha=0.5)
    plt.title('Autocorrelation of Stock Returns')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def demonstrate_stock_analysis():
    """
    Demonstrate individual stock analysis
    """
    print("\nIndividual Stock Analysis Demonstration")
    print("=" * 45)

    processor = FinancialDataProcessor()
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    portfolio_analysis = {}

    for symbol in symbols:
        data, analysis = processor.analyze_stock(symbol)
        if analysis:
            portfolio_analysis[symbol] = analysis
            print(f"\n{symbol} Analysis:")
            for key, value in analysis.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")


def main():
    """
    Main function to run all demonstrations
    """
    print("Day 31 - Pandas for Financial Data & Basic Financial Calculations")
    print("=" * 70)

    # Run all demonstrations
    demonstrate_pandas_operations()
    demonstrate_stock_analysis()
    demonstrate_portfolio_analysis()
    demonstrate_risk_metrics()
    demonstrate_time_series_analysis()

    print("\n" + "=" * 70)
    print("Day 31 Complete! Mastered:")
    print("✓ Pandas DataFrames for financial data")
    print("✓ Time series operations and resampling")
    print("✓ Returns and volatility calculations")
    print("✓ Moving averages and rolling statistics")
    print("✓ Portfolio return calculations")
    print("✓ Risk metrics and Sharpe ratio")
    print("✓ Correlation analysis")


if __name__ == "__main__":
    main()
