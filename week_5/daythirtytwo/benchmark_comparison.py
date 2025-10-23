"""
Benchmark Comparison and Analysis
Compare portfolio performance against various benchmarks
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json


class BenchmarkComparison:
    """
    Compare portfolio performance against benchmarks
    """

    def __init__(self, portfolio_returns: pd.Series):
        self.portfolio_returns = portfolio_returns
        self.benchmarks = {}
        self.comparison_data = None

    def add_benchmark(self, symbol: str, name: str = None) -> bool:
        """
        Add a benchmark for comparison
        """
        if not name:
            name = symbol

        try:
            benchmark = yf.Ticker(symbol)
            hist = benchmark.history(start=self.portfolio_returns.index[0],
                                     end=self.portfolio_returns.index[-1])
            if not hist.empty:
                benchmark_returns = hist['Close'].pct_change().dropna()
                self.benchmarks[name] = benchmark_returns
                print(f"✓ Added benchmark: {name} ({symbol})")
                return True
            else:
                print(f"✗ Could not fetch data for benchmark: {symbol}")
                return False
        except Exception as e:
            print(f"Error adding benchmark {symbol}: {e}")
            return False

    def load_common_benchmarks(self):
        """
        Load common market benchmarks
        """
        common_benchmarks = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ 100',
            'IWM': 'Russell 2000',
            'DIA': 'Dow Jones',
            'VGK': 'FTSE Europe',
            'VWO': 'Emerging Markets'
        }

        for symbol, name in common_benchmarks.items():
            self.add_benchmark(symbol, name)

    def calculate_comparison_metrics(self) -> pd.DataFrame:
        """
        Calculate comparison metrics between portfolio and benchmarks
        """
        if not self.benchmarks:
            print("No benchmarks available. Add benchmarks first.")
            return pd.DataFrame()

        comparison_metrics = []

        # Add portfolio to comparison
        portfolio_metrics = self._calculate_single_metrics(
            self.portfolio_returns, 'Portfolio')
        comparison_metrics.append(portfolio_metrics)

        # Add benchmarks to comparison
        for name, returns in self.benchmarks.items():
            benchmark_metrics = self._calculate_single_metrics(returns, name)
            comparison_metrics.append(benchmark_metrics)

        self.comparison_data = pd.DataFrame(comparison_metrics)
        return self.comparison_data

    def _calculate_single_metrics(self, returns: pd.Series, name: str) -> Dict:
        """
        Calculate metrics for a single return series
        """
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252/len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - 0.02) / \
            volatility if volatility != 0 else 0

        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # Win rate
        win_rate = (returns > 0).mean()

        return {
            'Name': name,
            'Total Return': total_return,
            'Annualized Return': annualized_return,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Win Rate': win_rate,
            'Data Points': len(returns)
        }

    def calculate_relative_performance(self) -> pd.DataFrame:
        """
        Calculate portfolio performance relative to benchmarks
        """
        if self.comparison_data is None:
            self.calculate_comparison_metrics()

        portfolio_metrics = self.comparison_data[self.comparison_data['Name']
                                                 == 'Portfolio'].iloc[0]
        relative_performance = []

        for _, benchmark in self.comparison_data[self.comparison_data['Name'] != 'Portfolio'].iterrows():
            relative_metrics = {
                'Benchmark': benchmark['Name'],
                'Excess Return': portfolio_metrics['Total Return'] - benchmark['Total Return'],
                'Excess Annual Return': portfolio_metrics['Annualized Return'] - benchmark['Annualized Return'],
                'Volatility Difference': portfolio_metrics['Volatility'] - benchmark['Volatility'],
                'Sharpe Difference': portfolio_metrics['Sharpe Ratio'] - benchmark['Sharpe Ratio'],
                'Drawdown Difference': portfolio_metrics['Max Drawdown'] - benchmark['Max Drawdown'],
                'Information Ratio': self._calculate_information_ratio(benchmark['Name'])
            }
            relative_performance.append(relative_metrics)

        return pd.DataFrame(relative_performance)

    def _calculate_information_ratio(self, benchmark_name: str) -> float:
        """
        Calculate information ratio relative to benchmark
        """
        if benchmark_name in self.benchmarks:
            benchmark_returns = self.benchmarks[benchmark_name]

            # Align dates
            aligned_data = pd.concat([self.portfolio_returns, benchmark_returns],
                                     axis=1, join='inner')
            aligned_data.columns = ['portfolio', 'benchmark']

            excess_returns = aligned_data['portfolio'] - \
                aligned_data['benchmark']
            information_ratio = (excess_returns.mean() /
                                 excess_returns.std()) * np.sqrt(252)

            return information_ratio if not np.isnan(information_ratio) else 0
        return 0

    def plot_comparison(self):
        """
        Plot comprehensive comparison charts
        """
        if self.comparison_data is None:
            self.calculate_comparison_metrics()

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Cumulative returns comparison
        self._plot_cumulative_returns(axes[0, 0])

        # Risk-return scatter plot
        self._plot_risk_return(axes[0, 1])

        # Drawdown comparison
        self._plot_drawdown_comparison(axes[1, 0])

        # Metrics comparison
        self._plot_metrics_comparison(axes[1, 1])

        plt.tight_layout()
        plt.show()

    def _plot_cumulative_returns(self, ax):
        """Plot cumulative returns comparison"""
        # Portfolio
        portfolio_cumulative = (1 + self.portfolio_returns).cumprod()
        ax.plot(portfolio_cumulative.index, portfolio_cumulative.values,
                linewidth=3, label='Portfolio', color='black')

        # Benchmarks
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.benchmarks)))
        for (name, returns), color in zip(self.benchmarks.items(), colors):
            benchmark_cumulative = (1 + returns).cumprod()
            ax.plot(benchmark_cumulative.index, benchmark_cumulative.values,
                    linewidth=2, label=name, color=color, alpha=0.8)

        ax.set_title('Cumulative Returns Comparison')
        ax.set_ylabel('Cumulative Return')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    def _plot_risk_return(self, ax):
        """Plot risk-return scatter plot"""
        if self.comparison_data is None:
            return

        for _, row in self.comparison_data.iterrows():
            if row['Name'] == 'Portfolio':
                ax.scatter(row['Volatility'], row['Annualized Return'],
                           s=200, label=row['Name'], color='red', marker='*')
            else:
                ax.scatter(row['Volatility'], row['Annualized Return'],
                           s=100, label=row['Name'], alpha=0.7)

        ax.set_xlabel('Annualized Volatility')
        ax.set_ylabel('Annualized Return')
        ax.set_title('Risk-Return Profile')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_drawdown_comparison(self, ax):
        """Plot drawdown comparison"""
        # Portfolio drawdown
        portfolio_cumulative = (1 + self.portfolio_returns).cumprod()
        portfolio_running_max = portfolio_cumulative.expanding().max()
        portfolio_drawdown = (portfolio_cumulative -
                              portfolio_running_max) / portfolio_running_max
        ax.fill_between(portfolio_drawdown.index, portfolio_drawdown.values, 0,
                        alpha=0.7, label='Portfolio', color='red')

        # Benchmark drawdowns (show worst one)
        worst_drawdown = None
        worst_name = None

        for name, returns in self.benchmarks.items():
            benchmark_cumulative = (1 + returns).cumprod()
            benchmark_running_max = benchmark_cumulative.expanding().max()
            benchmark_drawdown = (benchmark_cumulative -
                                  benchmark_running_max) / benchmark_running_max

            if worst_drawdown is None or benchmark_drawdown.min() < worst_drawdown.min():
                worst_drawdown = benchmark_drawdown
                worst_name = name

        if worst_drawdown is not None:
            ax.fill_between(worst_drawdown.index, worst_drawdown.values, 0,
                            alpha=0.3, label=f'Worst Benchmark ({worst_name})', color='blue')

        ax.set_title('Drawdown Comparison')
        ax.set_ylabel('Drawdown')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_metrics_comparison(self, ax):
        """Plot metrics comparison bar chart"""
        if self.comparison_data is None:
            return

        metrics_to_plot = ['Annualized Return',
                           'Volatility', 'Sharpe Ratio', 'Max Drawdown']
        comparison_subset = self.comparison_data[['Name'] + metrics_to_plot]

        x = np.arange(len(comparison_subset))
        width = 0.2

        for i, metric in enumerate(metrics_to_plot):
            values = comparison_subset[metric].values
            # Normalize for better visualization
            if metric in ['Volatility', 'Max Drawdown']:
                values = -values  # Lower is better
            values = (values - values.min()) / (values.max() -
                                                values.min()) if values.max() != values.min() else 0.5

            ax.bar(x + i * width, values, width, label=metric, alpha=0.7)

        ax.set_xlabel('Portfolio/Benchmarks')
        ax.set_ylabel('Normalized Metric Value')
        ax.set_title('Normalized Metrics Comparison')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(comparison_subset['Name'], rotation=45)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    def generate_comparison_report(self) -> Dict:
        """
        Generate comprehensive comparison report
        """
        comparison_metrics = self.calculate_comparison_metrics()
        relative_performance = self.calculate_relative_performance()

        report = {
            'absolute_performance': comparison_metrics.to_dict('records'),
            'relative_performance': relative_performance.to_dict('records'),
            'summary': {
                'number_of_benchmarks': len(self.benchmarks),
                'analysis_period': f"{self.portfolio_returns.index[0].strftime('%Y-%m-%d')} to {self.portfolio_returns.index[-1].strftime('%Y-%m-%d')}",
                'portfolio_outperformed': len([x for x in relative_performance['Excess Return'] if x > 0])
            }
        }

        return report


def demonstrate_benchmark_comparison():
    """
    Demonstrate benchmark comparison capabilities
    """
    print("Benchmark Comparison Demonstration")
    print("=" * 45)

    # Create sample portfolio returns
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]

    # Fetch data and calculate portfolio returns
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        hist = stock.history(start='2023-01-01')
        data[symbol] = hist['Close']

    price_data = pd.DataFrame(data)
    asset_returns = price_data.pct_change().dropna()

    # Calculate weighted portfolio returns
    portfolio_returns = pd.Series(0.0, index=asset_returns.index)
    for symbol, weight in zip(symbols, weights):
        portfolio_returns += asset_returns[symbol] * weight

    # Initialize benchmark comparison
    comparator = BenchmarkComparison(portfolio_returns)

    # Load common benchmarks
    comparator.load_common_benchmarks()

    # Generate comparison report
    report = comparator.generate_comparison_report()

    print("\nABSOLUTE PERFORMANCE COMPARISON")
    print("=" * 40)
    comparison_df = comparator.calculate_comparison_metrics()
    print(comparison_df.to_string(index=False, float_format='%.4f'))

    print("\nRELATIVE PERFORMANCE (vs Benchmarks)")
    print("=" * 40)
    relative_df = comparator.calculate_relative_performance()
    print(relative_df.to_string(index=False, float_format='%.4f'))

    print(f"\nSUMMARY")
    print("=" * 20)
    for key, value in report['summary'].items():
        print(f"{key}: {value}")

    # Plot comparisons
    comparator.plot_comparison()


if __name__ == "__main__":
    demonstrate_benchmark_comparison()
