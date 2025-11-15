import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
warnings.filterwarnings('ignore')


class FinancialEDA:
    def __init__(self):
        self.data = None
        self.returns = None

    def load_data(self, ticker='SPY', start_date='2020-01-01', end_date=None):
        """Load financial data from Yahoo Finance"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"Loading data for {ticker} from {start_date} to {end_date}")
        self.data = yf.download(ticker, start=start_date, end=end_date)
        self.data['Returns'] = self.data['Adj Close'].pct_change()
        self.data['Log_Returns'] = np.log(
            self.data['Adj Close'] / self.data['Adj Close'].shift(1))
        self.returns = self.data['Returns'].dropna()

        print(f"Data loaded: {len(self.data)} records")
        return self.data

    def data_quality_report(self):
        """Generate comprehensive data quality assessment"""
        print("=" * 50)
        print("DATA QUALITY REPORT")
        print("=" * 50)

        # Basic info
        print(f"Dataset shape: {self.data.shape}")
        print(
            f"Date range: {self.data.index.min()} to {self.data.index.max()}")

        # Missing values
        missing_data = self.data.isnull().sum()
        print("\nMissing Values:")
        for col, missing in missing_data.items():
            print(f"  {col}: {missing} ({missing/len(self.data)*100:.2f}%)")

        # Duplicates
        duplicates = self.data.duplicated().sum()
        print(f"\nDuplicate rows: {duplicates}")

        # Descriptive statistics
        print("\nDescriptive Statistics:")
        print(self.data[['Open', 'High', 'Low',
              'Close', 'Volume', 'Returns']].describe())

    def detect_outliers(self, column='Returns'):
        """Detect outliers using IQR method"""
        Q1 = self.data[column].quantile(0.25)
        Q3 = self.data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = self.data[(self.data[column] < lower_bound) | (
            self.data[column] > upper_bound)]
        print(
            f"\nOutliers in {column}: {len(outliers)} ({len(outliers)/len(self.data)*100:.2f}%)")
        return outliers

    def plot_price_series(self):
        """Plot price series with volume"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Price chart
        ax1.plot(self.data.index,
                 self.data['Adj Close'], label='Adj Close', linewidth=1)
        ax1.set_title('Price Series', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Volume chart
        ax2.bar(self.data.index,
                self.data['Volume'], alpha=0.7, color='orange')
        ax2.set_title('Trading Volume', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def plot_returns_distribution(self):
        """Plot returns distribution with statistical insights"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Returns time series
        ax1.plot(self.returns.index, self.returns, linewidth=0.5)
        ax1.set_title('Returns Time Series', fontweight='bold')
        ax1.set_ylabel('Returns')
        ax1.grid(True, alpha=0.3)

        # Histogram with normal distribution
        ax2.hist(self.returns.dropna(), bins=50,
                 density=True, alpha=0.7, edgecolor='black')
        ax2.set_title('Returns Distribution', fontweight='bold')
        ax2.set_xlabel('Returns')
        ax2.set_ylabel('Density')

        # Add normal distribution for comparison
        x = np.linspace(self.returns.min(), self.returns.max(), 100)
        from scipy.stats import norm
        ax2.plot(x, norm.pdf(x, self.returns.mean(), self.returns.std()),
                 'r-', label='Normal Dist')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Box plot
        ax3.boxplot(self.returns.dropna())
        ax3.set_title('Returns Box Plot', fontweight='bold')
        ax3.set_ylabel('Returns')
        ax3.grid(True, alpha=0.3)

        # Q-Q plot
        from scipy import stats
        stats.probplot(self.returns.dropna(), dist="norm", plot=ax4)
        ax4.set_title('Q-Q Plot', fontweight='bold')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # Print statistical properties
        print("\nReturns Statistics:")
        print(f"Mean: {self.returns.mean():.6f}")
        print(f"Std Dev: {self.returns.std():.6f}")
        print(f"Skewness: {self.returns.skew():.4f}")
        print(f"Kurtosis: {self.returns.kurtosis():.4f}")
        print(f"Min: {self.returns.min():.6f}")
        print(f"Max: {self.returns.max():.6f}")

    def correlation_analysis(self):
        """Analyze correlations between different price features"""
        price_features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Returns']
        correlation_matrix = self.data[price_features].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                    square=True, fmt='.3f')
        plt.title('Feature Correlation Heatmap',
                  fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

        return correlation_matrix

    def time_series_decomposition(self, period=252):
        """Decompose time series into trend, seasonality, and residuals"""
        # Use log prices for multiplicative decomposition
        log_prices = np.log(self.data['Adj Close'].dropna())

        if len(log_prices) < period * 2:
            period = len(log_prices) // 2
            print(f"Adjusting period to {period} due to limited data")

        decomposition = seasonal_decompose(
            log_prices, model='multiplicative', period=period)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10))

        decomposition.observed.plot(ax=axes[0], title='Observed', legend=False)
        decomposition.trend.plot(ax=axes[1], title='Trend', legend=False)
        decomposition.seasonal.plot(ax=axes[2], title='Seasonal', legend=False)
        decomposition.resid.plot(ax=axes[3], title='Residual', legend=False)

        for ax in axes:
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def volatility_analysis(self, window=21):
        """Analyze volatility clustering and rolling volatility"""
        rolling_vol = self.returns.rolling(window=window).std() * np.sqrt(252)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Returns with volatility overlay
        ax1.plot(self.returns.index, self.returns,
                 alpha=0.7, linewidth=0.5, label='Returns')
        ax1.set_title('Returns and Volatility Clustering', fontweight='bold')
        ax1.set_ylabel('Returns')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Rolling volatility
        ax2.plot(rolling_vol.index, rolling_vol, color='red',
                 linewidth=1.5, label=f'{window}-day Rolling Vol')
        ax2.set_title('Rolling Annualized Volatility', fontweight='bold')
        ax2.set_ylabel('Volatility')
        ax2.set_xlabel('Date')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def generate_complete_report(self, ticker='SPY'):
        """Generate a complete EDA report"""
        print("GENERATING COMPLETE EDA REPORT")
        print("=" * 60)

        # Load data
        self.load_data(ticker)

        # Generate all analyses
        self.data_quality_report()
        self.detect_outliers()
        self.plot_price_series()
        self.plot_returns_distribution()
        self.correlation_analysis()
        self.time_series_decomposition()
        self.volatility_analysis()

        print("\n" + "=" * 60)
        print("EDA REPORT COMPLETE")
        print("=" * 60)

# Example usage and challenge


def run_eda_challenge():
    """Challenge: Generate complete EDA report for multiple assets"""
    eda = FinancialEDA()

    # Single asset analysis
    print("SINGLE ASSET ANALYSIS (SPY)")
    eda.generate_complete_report('SPY')

    # Multi-asset analysis challenge
    print("\n" + "=" * 60)
    print("MULTI-ASSET COMPARISON CHALLENGE")
    print("=" * 60)

    assets = ['SPY', 'QQQ', 'GLD', 'BTC-USD']

    for asset in assets:
        try:
            print(f"\nAnalyzing {asset}:")
            asset_eda = FinancialEDA()
            asset_eda.load_data(asset)

            # Quick comparison stats
            returns = asset_eda.returns
            print(f"  Annual Return: {returns.mean() * 252:.2%}")
            print(f"  Annual Volatility: {returns.std() * np.sqrt(252):.2%}")
            print(
                f"  Sharpe Ratio: {returns.mean() / returns.std() * np.sqrt(252):.2f}")
            print(
                f"  Max Drawdown: {(1 - (1 + returns).cumprod() / (1 + returns).cumprod().expanding().max()).max():.2%}")

        except Exception as e:
            print(f"  Error analyzing {asset}: {e}")


if __name__ == "__main__":
    run_eda_challenge()
