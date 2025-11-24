"""
Seasonal Analysis and Decomposition
Time series decomposition and seasonal pattern analysis
"""

import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.stattools import acf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class SeasonalAnalyzer:
    """
    Seasonal decomposition and pattern analysis for financial time series
    """

    def __init__(self):
        self.decompositions = {}

    def seasonal_decomposition(self, series, model='additive', period=252,
                               stl_robust=True):
        """
        Perform seasonal decomposition of time series
        """
        try:
            if model == 'stl':
                # STL decomposition (more robust)
                decomposition = STL(series, period=period,
                                    robust=stl_robust).fit()
            else:
                # Classical decomposition
                decomposition = seasonal_decompose(
                    series, model=model, period=period)

            return decomposition

        except Exception as e:
            print(f"Error in seasonal decomposition: {e}")
            return None

    def plot_decomposition(self, decomposition, title="Seasonal Decomposition"):
        """Plot seasonal decomposition results"""
        if hasattr(decomposition, 'observed'):
            # Classical decomposition
            fig, axes = plt.subplots(4, 1, figsize=(12, 10))

            decomposition.observed.plot(ax=axes[0], title='Observed')
            decomposition.trend.plot(ax=axes[1], title='Trend')
            decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
            decomposition.resid.plot(ax=axes[3], title='Residual')

        else:
            # STL decomposition
            fig, axes = plt.subplots(4, 1, figsize=(12, 10))

            decomposition.observed.plot(ax=axes[0], title='Observed')
            decomposition.trend.plot(ax=axes[1], title='Trend')
            decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
            decomposition.resid.plot(ax=axes[3], title='Residual')

        plt.suptitle(title)
        plt.tight_layout()
        plt.show()

    def detect_seasonal_period(self, series, max_lags=500):
        """Detect seasonal period using autocorrelation"""
        # Calculate autocorrelation
        autocorr = acf(series.dropna(), nlags=max_lags, fft=True)

        # Find significant peaks (potential seasonal periods)
        threshold = 2 / np.sqrt(len(series))
        significant_lags = np.where(np.abs(autocorr) > threshold)[0]

        # Look for regular patterns (seasonality)
        if len(significant_lags) > 1:
            # Calculate differences between significant lags
            lag_differences = np.diff(significant_lags)

            # Find most common difference (potential seasonal period)
            if len(lag_differences) > 0:
                common_period = np.bincount(lag_differences).argmax()
                return common_period

        return None

    def analyze_seasonal_patterns(self, series, frequency='D'):
        """Analyze seasonal patterns at different time frequencies"""
        if not hasattr(series.index, 'strftime'):
            return {}

        # Extract time components
        if frequency == 'D':
            # Daily patterns (day of week)
            series_df = pd.DataFrame({
                'value': series.values,
                'day_of_week': series.index.dayofweek,
                'day_name': series.index.day_name()
            }, index=series.index)

            # Group by day of week
            daily_pattern = series_df.groupby('day_of_week')['value'].mean()

            return {'daily_pattern': daily_pattern}

        elif frequency == 'M':
            # Monthly patterns
            series_df = pd.DataFrame({
                'value': series.values,
                'month': series.index.month,
                'month_name': series.index.month_name()
            }, index=series.index)

            # Group by month
            monthly_pattern = series_df.groupby('month')['value'].mean()

            return {'monthly_pattern': monthly_pattern}

        elif frequency == 'Q':
            # Quarterly patterns
            series_df = pd.DataFrame({
                'value': series.values,
                'quarter': series.index.quarter
            }, index=series.index)

            # Group by quarter
            quarterly_pattern = series_df.groupby('quarter')['value'].mean()

            return {'quarterly_pattern': quarterly_pattern}

        else:
            return {}

    def plot_seasonal_patterns(self, patterns, title="Seasonal Patterns"):
        """Plot seasonal patterns"""
        n_patterns = len(patterns)
        fig, axes = plt.subplots(1, n_patterns, figsize=(5*n_patterns, 4))

        if n_patterns == 1:
            axes = [axes]

        for i, (pattern_name, pattern_data) in enumerate(patterns.items()):
            if hasattr(axes[i], 'bar'):
                # Bar plot for categorical patterns
                axes[i].bar(pattern_data.index, pattern_data.values)
                axes[i].set_title(f'{pattern_name.replace("_", " ").title()}')
                axes[i].set_xlabel(pattern_name.split('_')[0])
                axes[i].set_ylabel('Average Value')
                axes[i].tick_params(axis='x', rotation=45)
            else:
                # Line plot for continuous patterns
                axes[i].plot(pattern_data.index, pattern_data.values)
                axes[i].set_title(f'{pattern_name.replace("_", " ").title()}')
                axes[i].set_xlabel(pattern_name.split('_')[0])
                axes[i].set_ylabel('Average Value')

        plt.suptitle(title)
        plt.tight_layout()
        plt.show()

    def test_seasonal_stationarity(self, series, seasonal_period=252):
        """Test for seasonal stationarity"""
        from statsmodels.tsa.stattools import adfuller

        # Regular ADF test
        regular_adf = adfuller(series.dropna())

        # Seasonal difference and test
        seasonal_diff = series.diff(seasonal_period).dropna()
        seasonal_adf = adfuller(seasonal_diff)

        return {
            'regular_adf': {
                'test_statistic': regular_adf[0],
                'p_value': regular_adf[1],
                'stationary': regular_adf[1] < 0.05
            },
            'seasonal_adf': {
                'test_statistic': seasonal_adf[0],
                'p_value': seasonal_adf[1],
                'stationary': seasonal_adf[1] < 0.05
            }
        }

    def seasonal_arima_modeling(self, series, order, seasonal_order,
                                enforce_stationarity=True):
        """Fit seasonal ARIMA model"""
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        try:
            model = SARIMAX(series,
                            order=order,
                            seasonal_order=seasonal_order,
                            enforce_stationarity=enforce_stationarity)
            fitted_model = model.fit(disp=False)
            return fitted_model
        except Exception as e:
            print(f"Error fitting seasonal ARIMA: {e}")
            return None

    def detect_anomalies_seasonal(self, series, decomposition,
                                  residual_threshold=2.5):
        """Detect anomalies using seasonal decomposition"""
        if hasattr(decomposition, 'resid'):
            residuals = decomposition.resid
        else:
            residuals = decomposition.resid

        # Calculate residual statistics
        residual_mean = residuals.mean()
        residual_std = residuals.std()

        # Find anomalies (residuals beyond threshold standard deviations)
        anomaly_threshold = residual_threshold * residual_std
        anomalies = residuals[np.abs(
            residuals - residual_mean) > anomaly_threshold]

        return {
            'anomalies': anomalies,
            'residual_stats': {
                'mean': residual_mean,
                'std': residual_std,
                'threshold': anomaly_threshold
            },
            'anomaly_count': len(anomalies)
        }

    def rolling_seasonal_analysis(self, series, window=252, step=63):
        """Perform rolling seasonal analysis"""
        seasonal_strength = []
        dates = []

        for i in range(0, len(series) - window + 1, step):
            window_data = series.iloc[i:i+window]

            try:
                # Perform decomposition
                decomposition = self.seasonal_decomposition(
                    window_data, period=63)  # Quarterly seasonality

                if decomposition is not None:
                    if hasattr(decomposition, 'seasonal'):
                        seasonal_component = decomposition.seasonal
                    else:
                        seasonal_component = decomposition.seasonal

                    # Calculate seasonal strength
                    seasonal_var = np.var(seasonal_component.dropna())
                    total_var = np.var(window_data.dropna())

                    if total_var > 0:
                        strength = seasonal_var / total_var
                        seasonal_strength.append(strength)
                        dates.append(window_data.index[-1])

            except Exception as e:
                continue

        return pd.Series(seasonal_strength, index=dates)


def demonstrate_seasonal_analysis():
    """Demonstrate seasonal analysis capabilities"""
    print("Seasonal Analysis Demonstration")
    print("=" * 50)

    analyzer = SeasonalAnalyzer()

    # Load sample data
    symbol = 'AAPL'
    stock = yf.Ticker(symbol)
    data = stock.history(period='5y')  # Longer period for seasonality
    prices = data['Close']

    print(f"Data loaded: {len(prices)} price points")

    # Detect seasonal period
    print("\n1. Detecting seasonal period...")
    seasonal_period = analyzer.detect_seasonal_period(prices)
    print(f"Detected seasonal period: {seasonal_period} days")

    # Use business days (approx 252 per year) if no clear period detected
    if seasonal_period is None:
        seasonal_period = 63  # Quarterly seasonality approximation
        print(f"Using default period: {seasonal_period} days (quarterly)")

    # Perform seasonal decomposition
    print("\n2. Performing seasonal decomposition...")
    decomposition = analyzer.seasonal_decomposition(
        prices, period=seasonal_period)

    if decomposition is not None:
        analyzer.plot_decomposition(decomposition,
                                    title=f"Seasonal Decomposition - {symbol}")

    # Analyze seasonal patterns
    print("\n3. Analyzing seasonal patterns...")
    patterns = analyzer.analyze_seasonal_patterns(prices, frequency='D')

    if patterns:
        analyzer.plot_seasonal_patterns(patterns,
                                        title=f"Seasonal Patterns - {symbol}")

        # Print pattern summary
        for pattern_name, pattern_data in patterns.items():
            print(f"\n{pattern_name}:")
            print(pattern_data)

    # Test seasonal stationarity
    print("\n4. Testing seasonal stationarity...")
    stationarity_test = analyzer.test_seasonal_stationarity(
        prices, seasonal_period)

    print("Stationarity Test Results:")
    print(
        f"Regular ADF p-value: {stationarity_test['regular_adf']['p_value']:.4f}")
    print(
        f"Seasonal ADF p-value: {stationarity_test['seasonal_adf']['p_value']:.4f}")

    # Detect anomalies
    print("\n5. Detecting seasonal anomalies...")
    if decomposition is not None:
        anomalies = analyzer.detect_anomalies_seasonal(prices, decomposition)
        print(f"Number of anomalies detected: {anomalies['anomaly_count']}")

        if len(anomalies['anomalies']) > 0:
            print("Top 5 anomalies:")
            print(anomalies['anomalies'].sort_values(ascending=False).head())

    # Rolling seasonal analysis
    print("\n6. Performing rolling seasonal analysis...")
    rolling_seasonal = analyzer.rolling_seasonal_analysis(prices)

    if len(rolling_seasonal) > 0:
        plt.figure(figsize=(12, 6))
        rolling_seasonal.plot(title='Rolling Seasonal Strength')
        plt.ylabel('Seasonal Strength')
        plt.xlabel('Date')
        plt.grid(True, alpha=0.3)
        plt.show()

        print(f"Average seasonal strength: {rolling_seasonal.mean():.4f}")
        print(f"Maximum seasonal strength: {rolling_seasonal.max():.4f}")

    # Try seasonal ARIMA
    print("\n7. Testing seasonal ARIMA...")
    # Use returns for stationarity
    returns = prices.pct_change().dropna()

    # Simple seasonal ARIMA model (SARIMA)
    seasonal_model = analyzer.seasonal_arima_modeling(
        returns,
        order=(1, 0, 1),
        seasonal_order=(1, 0, 1, 63)  # Quarterly seasonality
    )

    if seasonal_model is not None:
        print("Seasonal ARIMA model fitted successfully")
        print(f"AIC: {seasonal_model.aic:.2f}")

    return analyzer, decomposition, patterns


if __name__ == "__main__":
    demonstrate_seasonal_analysis()
