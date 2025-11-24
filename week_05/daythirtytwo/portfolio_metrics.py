"""
Portfolio Performance Metrics Calculator
Comprehensive portfolio analysis with risk-adjusted metrics
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json


class PortfolioMetrics:
    """
    Calculate comprehensive portfolio performance metrics
    """

    def __init__(self, portfolio_weights: Dict, risk_free_rate: float = 0.02):
        self.portfolio_weights = portfolio_weights
        self.risk_free_rate = risk_free_rate
        self.portfolio_data = None
        self.portfolio_returns = None
        self.benchmark_returns = None

    def fetch_portfolio_data(self, start_date: str = '2023-01-01',
                             end_date: str = None) -> pd.DataFrame:
        """
        Fetch historical data for portfolio components
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print("Fetching portfolio data...")
        data = {}

        for symbol in self.portfolio_weights.keys():
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(start=start_date, end=end_date)
                if not hist.empty:
                    data[symbol] = hist['Close']
                    print(f"  ✓ {symbol}: {len(hist)} days")
                else:
                    print(f"  ✗ {symbol}: No data")
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {e}")

        self.portfolio_data = pd.DataFrame(data)
        return self.portfolio_data

    def calculate_portfolio_returns(self) -> pd.Series:
        """
        Calculate weighted portfolio returns
        """
        if self.portfolio_data is None:
            raise ValueError(
                "No portfolio data available. Call fetch_portfolio_data first.")

        # Calculate individual asset returns
        asset_returns = self.portfolio_data.pct_change().dropna()

        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=asset_returns.index)

        for symbol, weight in self.portfolio_weights.items():
            if symbol in asset_returns.columns:
                portfolio_returns += asset_returns[symbol] * weight

        self.portfolio_returns = portfolio_returns
        return self.portfolio_returns

    def set_benchmark(self, benchmark_symbol: str = 'SPY',
                      start_date: str = '2023-01-01') -> pd.Series:
        """
        Set benchmark for comparison
        """
        try:
            benchmark = yf.Ticker(benchmark_symbol)
            hist = benchmark.history(start=start_date)
            if not hist.empty:
                self.benchmark_returns = hist['Close'].pct_change().dropna()
                print(
                    f"Benchmark {benchmark_symbol} set with {len(self.benchmark_returns)} data points")
                return self.benchmark_returns
            else:
                print(f"Could not fetch benchmark data for {benchmark_symbol}")
                return None
        except Exception as e:
            print(f"Error setting benchmark: {e}")
            return None

    def calculate_basic_metrics(self) -> Dict:
        """
        Calculate basic portfolio performance metrics
        """
        if self.portfolio_returns is None:
            self.calculate_portfolio_returns()

        metrics = {}

        # Return metrics
        metrics['total_return'] = (1 + self.portfolio_returns).prod() - 1
        metrics['annualized_return'] = (
            1 + metrics['total_return']) ** (252/len(self.portfolio_returns)) - 1
        # Compound Annual Growth Rate
        metrics['cagr'] = metrics['annualized_return']

        # Risk metrics
        metrics['volatility'] = self.portfolio_returns.std() * np.sqrt(252)
        metrics['downside_volatility'] = self._calculate_downside_volatility()

        # Risk-adjusted metrics
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio()
        metrics['sortino_ratio'] = self._calculate_sortino_ratio()

        # Drawdown metrics
        max_drawdown, max_drawdown_duration = self._calculate_max_drawdown()
        metrics['max_drawdown'] = max_drawdown
        metrics['max_drawdown_duration'] = max_drawdown_duration
        metrics['calmar_ratio'] = metrics['annualized_return'] / \
            abs(max_drawdown) if max_drawdown != 0 else 0

        # Value at Risk
        metrics['var_95'] = self.portfolio_returns.quantile(0.05)
        metrics['cvar_95'] = self.portfolio_returns[self.portfolio_returns <=
                                                    metrics['var_95']].mean()

        return metrics

    def calculate_advanced_metrics(self) -> Dict:
        """
        Calculate advanced portfolio metrics
        """
        if self.portfolio_returns is None:
            self.calculate_portfolio_returns()

        metrics = {}

        # Beta and Alpha (if benchmark available)
        if self.benchmark_returns is not None:
            aligned_returns = self._align_with_benchmark()
            if aligned_returns is not None:
                portfolio_aligned, benchmark_aligned = aligned_returns

                # Beta
                covariance = portfolio_aligned.cov(benchmark_aligned)
                benchmark_variance = benchmark_aligned.var()
                metrics['beta'] = covariance / \
                    benchmark_variance if benchmark_variance != 0 else 0

                # Alpha
                benchmark_total_return = (1 + benchmark_aligned).prod() - 1
                expected_return = self.risk_free_rate + \
                    metrics['beta'] * \
                    (benchmark_total_return - self.risk_free_rate)
                metrics['alpha'] = self.calculate_basic_metrics()[
                    'total_return'] - expected_return

                # Tracking error
                tracking_error = (portfolio_aligned -
                                  benchmark_aligned).std() * np.sqrt(252)
                metrics['tracking_error'] = tracking_error

                # Information ratio
                excess_returns = portfolio_aligned - benchmark_aligned
                metrics['information_ratio'] = (excess_returns.mean(
                ) / excess_returns.std()) * np.sqrt(252) if excess_returns.std() != 0 else 0

        # Additional metrics
        metrics['win_rate'] = (self.portfolio_returns > 0).mean()
        metrics['profit_loss_ratio'] = self._calculate_profit_loss_ratio()
        metrics['skewness'] = self.portfolio_returns.skew()
        metrics['kurtosis'] = self.portfolio_returns.kurtosis()

        return metrics

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        excess_return = self.calculate_basic_metrics(
        )['annualized_return'] - self.risk_free_rate
        volatility = self.calculate_basic_metrics()['volatility']
        return excess_return / volatility if volatility != 0 else 0

    def _calculate_sortino_ratio(self) -> float:
        """Calculate Sortino ratio (uses downside deviation)"""
        excess_return = self.calculate_basic_metrics(
        )['annualized_return'] - self.risk_free_rate
        downside_volatility = self._calculate_downside_volatility()
        return excess_return / downside_volatility if downside_volatility != 0 else 0

    def _calculate_downside_volatility(self) -> float:
        """Calculate downside deviation (semi-deviation)"""
        downside_returns = self.portfolio_returns[self.portfolio_returns < 0]
        return downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0

    def _calculate_max_drawdown(self) -> tuple:
        """Calculate maximum drawdown and duration"""
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max

        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()

        # Calculate drawdown duration
        drawdown_duration = self._calculate_drawdown_duration(drawdown)

        return max_drawdown, drawdown_duration

    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration in days"""
        in_drawdown = drawdown < 0
        drawdown_periods = in_drawdown.astype(int).groupby(
            (in_drawdown != in_drawdown.shift()).cumsum()).sum()
        return drawdown_periods.max() if not drawdown_periods.empty else 0

    def _calculate_profit_loss_ratio(self) -> float:
        """Calculate profit/loss ratio (average gain / average loss)"""
        gains = self.portfolio_returns[self.portfolio_returns > 0]
        losses = self.portfolio_returns[self.portfolio_returns < 0]

        if len(losses) == 0:
            return float('inf')
        elif len(gains) == 0:
            return 0
        else:
            return gains.mean() / abs(losses.mean())

    def _align_with_benchmark(self) -> tuple:
        """Align portfolio returns with benchmark returns"""
        if self.benchmark_returns is None:
            return None

        aligned_data = pd.concat([self.portfolio_returns, self.benchmark_returns],
                                 axis=1, join='inner')
        aligned_data.columns = ['portfolio', 'benchmark']

        return aligned_data['portfolio'], aligned_data['benchmark']

    def generate_performance_report(self) -> Dict:
        """
        Generate comprehensive performance report
        """
        basic_metrics = self.calculate_basic_metrics()
        advanced_metrics = self.calculate_advanced_metrics()

        report = {
            'portfolio_summary': {
                'number_of_assets': len(self.portfolio_weights),
                'total_weight': sum(self.portfolio_weights.values()),
                'risk_free_rate': self.risk_free_rate
            },
            'basic_metrics': basic_metrics,
            'advanced_metrics': advanced_metrics,
            'asset_contributions': self._calculate_asset_contributions()
        }

        return report

    def _calculate_asset_contributions(self) -> Dict:
        """Calculate contribution of each asset to portfolio performance"""
        if self.portfolio_data is None:
            return {}

        contributions = {}
        total_return = self.calculate_basic_metrics()['total_return']

        for symbol, weight in self.portfolio_weights.items():
            if symbol in self.portfolio_data.columns:
                asset_return = (
                    self.portfolio_data[symbol].iloc[-1] / self.portfolio_data[symbol].iloc[0] - 1)
                contributions[symbol] = {
                    'weight': weight,
                    'asset_return': asset_return,
                    'contribution': weight * asset_return,
                    'contribution_percent': (weight * asset_return) / total_return if total_return != 0 else 0
                }

        return contributions

    def plot_performance(self):
        """
        Plot portfolio performance charts
        """
        if self.portfolio_returns is None:
            self.calculate_portfolio_returns()

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Cumulative returns
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        axes[0, 0].plot(cumulative_returns.index, cumulative_returns.values,
                        linewidth=2, label='Portfolio')

        if self.benchmark_returns is not None:
            benchmark_cumulative = (1 + self.benchmark_returns).cumprod()
            axes[0, 0].plot(benchmark_cumulative.index, benchmark_cumulative.values,
                            linewidth=2, label='Benchmark', alpha=0.7)

        axes[0, 0].set_title('Cumulative Returns')
        axes[0, 0].set_ylabel('Cumulative Return')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Drawdown
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        axes[0, 1].fill_between(drawdown.index, drawdown.values, 0,
                                alpha=0.3, color='red')
        axes[0, 1].set_title('Portfolio Drawdown')
        axes[0, 1].set_ylabel('Drawdown')
        axes[0, 1].grid(True, alpha=0.3)

        # Rolling volatility (21-day)
        rolling_vol = self.portfolio_returns.rolling(
            window=21).std() * np.sqrt(252)
        axes[1, 0].plot(rolling_vol.index, rolling_vol.values)
        axes[1, 0].set_title('Rolling Annualized Volatility (21-day)')
        axes[1, 0].set_ylabel('Volatility')
        axes[1, 0].grid(True, alpha=0.3)

        # Returns distribution
        axes[1, 1].hist(self.portfolio_returns, bins=50,
                        alpha=0.7, edgecolor='black')
        axes[1, 1].axvline(self.portfolio_returns.mean(), color='red',
                           linestyle='--', label=f'Mean: {self.portfolio_returns.mean():.4f}')
        axes[1, 1].set_title('Returns Distribution')
        axes[1, 1].set_xlabel('Daily Returns')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


def demonstrate_portfolio_metrics():
    """
    Demonstrate portfolio metrics calculation
    """
    print("Portfolio Performance Metrics Demonstration")
    print("=" * 50)

    # Load sample portfolio
    with open('data/sample_portfolio.json', 'r') as f:
        portfolio_config = json.load(f)

    portfolio_weights = portfolio_config['portfolio']

    # Initialize portfolio analyzer
    portfolio = PortfolioMetrics(portfolio_weights)

    # Fetch data
    portfolio.fetch_portfolio_data(start_date='2023-01-01')

    # Set benchmark
    portfolio.set_benchmark('SPY')

    # Generate report
    report = portfolio.generate_performance_report()

    print("\nPORTFOLIO PERFORMANCE REPORT")
    print("=" * 40)

    print(f"\nPortfolio Summary:")
    for key, value in report['portfolio_summary'].items():
        print(f"  {key}: {value}")

    print(f"\nBasic Metrics:")
    for metric, value in report['basic_metrics'].items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")
        else:
            print(f"  {metric}: {value}")

    print(f"\nAdvanced Metrics:")
    for metric, value in report['advanced_metrics'].items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")
        else:
            print(f"  {metric}: {value}")

    print(f"\nTop Asset Contributions:")
    contributions = report['asset_contributions']
    for symbol, data in sorted(contributions.items(),
                               key=lambda x: x[1]['contribution'], reverse=True)[:5]:
        print(
            f"  {symbol}: {data['contribution']:.4f} ({data['contribution_percent']:.2%})")

    # Plot performance
    portfolio.plot_performance()


if __name__ == "__main__":
    demonstrate_portfolio_metrics()
