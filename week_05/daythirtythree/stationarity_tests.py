"""
Day 33 - Stationarity Tests and Time Series Properties
Advanced stationarity testing and time series properties analysis
"""

import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


class StationarityAnalyzer:
    """
    Comprehensive stationarity analysis for financial time series
    """

    def __init__(self):
        self.results = {}

    def load_stock_data(self, symbol, period='2y'):
        """Load stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
            return None

    def augmented_dickey_fuller_test(self, series, autolag='AIC'):
        """
        Augmented Dickey-Fuller test for stationarity
        H0: Series has unit root (non-stationary)
        H1: Series is stationary
        """
        result = adfuller(series.dropna(), autolag=autolag)

        adf_output = {
            'test_statistic': result[0],
            'p_value': result[1],
            'lags_used': result[2],
            'observations': result[3],
            'critical_values': result[4],
            'stationary': result[1] < 0.05
        }

        return adf_output

    def kpss_test(self, series, regression='c'):
        """
        KPSS test for stationarity
        H0: Series is stationary
        H1: Series has unit root (non-stationary)
        """
        result = kpss(series.dropna(), regression=regression)

        kpss_output = {
            'test_statistic': result[0],
            'p_value': result[1],
            'lags_used': result[2],
            'critical_values': result[3],
            'stationary': result[1] > 0.05
        }

        return kpss_output

    def comprehensive_stationarity_test(self, series):
        """
        Perform comprehensive stationarity testing using multiple methods
        """
        # ADF Test
        adf_result = self.augmented_dickey_fuller_test(series)

        # KPSS Test
        kpss_result = self.kpss_test(series)

        # Additional metrics
        mean_reversion_metric = self.calculate_mean_reversion_metric(series)
        variance_ratio = self.calculate_variance_ratio(series)

        comprehensive_result = {
            'adf_test': adf_result,
            'kpss_test': kpss_result,
            'mean_reversion_metric': mean_reversion_metric,
            'variance_ratio': variance_ratio,
            'conclusion': self._interpret_stationarity(adf_result, kpss_result)
        }

        return comprehensive_result

    def calculate_mean_reversion_metric(self, series, lag=1):
        """Calculate mean reversion metric (Hurst exponent approximation)"""
        returns = series.pct_change().dropna()
        if len(returns) < lag + 1:
            return 0

        # Simplified mean reversion metric
        autocorr = returns.autocorr(lag=lag)
        if autocorr is None:
            return 0

        # Negative autocorrelation suggests mean reversion
        return -autocorr

    def calculate_variance_ratio(self, series, periods=[2, 5, 10]):
        """Calculate variance ratio test (simplified)"""
        returns = series.pct_change().dropna()
        variance_ratios = {}

        for period in periods:
            if len(returns) > period:
                # Calculate multi-period returns
                multi_period_returns = returns.rolling(
                    window=period).sum().dropna()

                # Variance ratio
                var_ratio = multi_period_returns.var() / (period * returns.var())
                variance_ratios[f'period_{period}'] = var_ratio

        return variance_ratios

    def _interpret_stationarity(self, adf_result, kpss_result):
        """Interpret stationarity test results"""
        adf_stationary = adf_result['stationary']
        kpss_stationary = kpss_result['stationary']

        if adf_stationary and kpss_stationary:
            return "Definitely Stationary"
        elif not adf_stationary and not kpss_stationary:
            return "Definitely Non-Stationary"
        elif adf_stationary and not kpss_stationary:
            return "Trend Stationary"
        else:
            return "Difference Stationary"

    def plot_autocorrelation(self, series, lags=40):
        """Plot autocorrelation and partial autocorrelation functions"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # ACF plot
        plot_acf(series.dropna(), lags=lags, ax=ax1)
        ax1.set_title(f'Autocorrelation Function (ACF) - {len(series)} lags')

        # PACF plot
        plot_pacf(series.dropna(), lags=lags, ax=ax2)
        ax2.set_title(
            f'Partial Autocorrelation Function (PACF) - {len(series)} lags')

        plt.tight_layout()
        plt.show()

        # Return ACF and PACF values
        acf_values = acf(series.dropna(), nlags=lags)
        pacf_values = pacf(series.dropna(), nlags=lags)

        return acf_values, pacf_values

    def make_stationary(self, series, method='diff'):
        """
        Transform series to stationary using various methods
        """
        if method == 'diff':
            # First difference
            stationary_series = series.diff().dropna()
        elif method == 'log_diff':
            # Log returns
            stationary_series = np.log(series).diff().dropna()
        elif method == 'pct_change':
            # Percentage returns
            stationary_series = series.pct_change().dropna()
        elif method == 'detrend':
            # Remove linear trend
            from scipy import stats
            x = np.arange(len(series))
            slope, intercept, _, _, _ = stats.linregress(x, series)
            trend = slope * x + intercept
            stationary_series = series - trend
        else:
            raise ValueError(
                "Unknown method. Use 'diff', 'log_diff', 'pct_change', or 'detrend'")

        return stationary_series

    def analyze_multiple_transformations(self, series):
        """Analyze stationarity for multiple transformations"""
        transformations = {
            'original': series,
            'first_difference': series.diff().dropna(),
            'log_returns': np.log(series).diff().dropna(),
            'percentage_returns': series.pct_change().dropna()
        }

        results = {}
        for name, transformed_series in transformations.items():
            if len(transformed_series) > 0:
                results[name] = self.comprehensive_stationarity_test(
                    transformed_series)

        return results


def demonstrate_stationarity_analysis():
    """Demonstrate stationarity analysis capabilities"""
    print("Stationarity Analysis Demonstration")
    print("=" * 50)

    analyzer = StationarityAnalyzer()

    # Load sample data
    symbol = 'AAPL'
    data = analyzer.load_stock_data(symbol, '2y')

    if data is None:
        print("Creating synthetic data for demonstration...")
        # Create synthetic data
        dates = pd.date_range('2020-01-01', periods=500, freq='D')
        # Random walk with drift
        prices = 100 + np.cumsum(np.random.normal(0.01, 0.02, 500))
        data = pd.DataFrame({'Close': prices}, index=dates)

    prices = data['Close']
    returns = prices.pct_change().dropna()

    print(f"Analyzing {symbol} - {len(prices)} data points")

    # Test stationarity of prices
    print("\n1. Stationarity Test - Price Series:")
    price_stationarity = analyzer.comprehensive_stationarity_test(prices)
    print(f"ADF p-value: {price_stationarity['adf_test']['p_value']:.4f}")
    print(f"KPSS p-value: {price_stationarity['kpss_test']['p_value']:.4f}")
    print(f"Conclusion: {price_stationarity['conclusion']}")

    # Test stationarity of returns
    print("\n2. Stationarity Test - Return Series:")
    return_stationarity = analyzer.comprehensive_stationarity_test(returns)
    print(f"ADF p-value: {return_stationarity['adf_test']['p_value']:.4f}")
    print(f"KPSS p-value: {return_stationarity['kpss_test']['p_value']:.4f}")
    print(f"Conclusion: {return_stationarity['conclusion']}")

    # Analyze multiple transformations
    print("\n3. Multiple Transformations Analysis:")
    transformation_results = analyzer.analyze_multiple_transformations(prices)
    for transform, result in transformation_results.items():
        print(f"  {transform:20}: {result['conclusion']}")

    # Plot autocorrelation
    print("\n4. Generating ACF/PACF plots...")
    analyzer.plot_autocorrelation(returns, lags=20)

    # Critical values from ADF test
    print("\n5. ADF Test Critical Values:")
    for key, value in price_stationarity['adf_test']['critical_values'].items():
        print(f"  {key}: {value:.4f}")

    return analyzer, prices, returns


if __name__ == "__main__":
    demonstrate_stationarity_analysis()
