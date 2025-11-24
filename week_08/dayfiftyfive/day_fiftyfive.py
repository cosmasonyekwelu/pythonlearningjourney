import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore')


class TradingStrategyBacktester:
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.portfolio = None
        self.performance = {}

    def prepare_data(self, prices, predictions, prediction_horizon=1):
        """Prepare data for backtesting"""
        # Align predictions with prices (accounting for prediction horizon)
        aligned_predictions = predictions.shift(prediction_horizon).dropna()
        aligned_prices = prices.reindex(aligned_predictions.index)

        return aligned_prices, aligned_predictions

    def generate_signals(self, predictions, method='binary', threshold=0.5):
        """Convert model predictions to trading signals"""
        if method == 'binary':
            # Binary classification: 1 for buy, 0 for sell/hold
            signals = (predictions > threshold).astype(int)
        elif method == 'probability':
            # Use prediction probabilities with confidence threshold
            signals = np.where(predictions > threshold, 1,
                               np.where(predictions < (1 - threshold), -1, 0))
        elif method == 'regression':
            # Regression: positive predicted returns = buy, negative = sell
            signals = np.where(predictions > 0, 1, -1)

        return pd.Series(signals, index=predictions.index, name='signal')

    def vectorbt_backtest(self, prices, signals, strategy_name="ML Strategy"):
        """Backtest using vectorbt for efficient vectorized operations"""
        print(f"Running VectorBT Backtest for {strategy_name}...")

        # Create portfolio
        portfolio = vbt.Portfolio.from_signals(
            prices,
            entries=signals == 1,
            exits=signals == -1,
            init_cash=self.initial_capital,
            fees=self.commission,
            freq='1D'
        )

        return portfolio

    def manual_backtest(self, prices, signals):
        """Manual backtest implementation for transparency"""
        print("Running Manual Backtest...")

        # Initialize tracking variables
        cash = self.initial_capital
        position = 0
        trades = []
        portfolio_values = []

        for date, signal in signals.items():
            price = prices.loc[date]

            # Execute trades based on signals
            if signal == 1 and position == 0:  # Buy signal, no position
                # Calculate number of shares (using 95% of cash for safety)
                shares_to_buy = int((cash * 0.95) / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price * (1 + self.commission)
                    cash -= cost
                    position = shares_to_buy
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': price,
                        'value': cost
                    })

            elif signal == -1 and position > 0:  # Sell signal, has position
                proceeds = position * price * (1 - self.commission)
                cash += proceeds
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'shares': position,
                    'price': price,
                    'value': proceeds
                })
                position = 0

            # Calculate portfolio value
            portfolio_value = cash + position * price
            portfolio_values.append(portfolio_value)

        # Create results DataFrame
        results = pd.DataFrame({
            'date': signals.index,
            'portfolio_value': portfolio_values,
            'signal': signals.values
        }).set_index('date')

        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

        return results, trades_df

    def calculate_performance_metrics(self, portfolio_values, prices, risk_free_rate=0.02):
        """Calculate comprehensive performance metrics"""
        returns = portfolio_values.pct_change().dropna()
        benchmark_returns = prices.pct_change().dropna()

        # Align returns
        common_index = returns.index.intersection(benchmark_returns.index)
        returns = returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]

        # Basic metrics
        total_return = (
            portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1)
        annual_return = (1 + total_return) ** (252 / len(portfolio_values)) - 1

        # Volatility and risk metrics
        annual_volatility = returns.std() * np.sqrt(252)

        # Sharpe ratio
        excess_returns = returns - risk_free_rate / 252
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)

        # Sortino ratio (only downside volatility)
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std(
        ) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate) / \
            downside_volatility if downside_volatility > 0 else 0

        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Calmar ratio
        calmar_ratio = annual_return / \
            abs(max_drawdown) if max_drawdown != 0 else 0

        # Win rate and profit factor
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        win_rate = len(positive_returns) / \
            len(returns) if len(returns) > 0 else 0
        profit_factor = abs(positive_returns.sum(
        ) / negative_returns.sum()) if len(negative_returns) > 0 else float('inf')

        # Alpha and Beta
        covariance = returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        alpha = annual_return - \
            (risk_free_rate + beta * (benchmark_returns.mean() * 252 - risk_free_rate))

        metrics = {
            'Total Return': total_return,
            'Annual Return': annual_return,
            'Annual Volatility': annual_volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            'Max Drawdown': max_drawdown,
            'Calmar Ratio': calmar_ratio,
            'Win Rate': win_rate,
            'Profit Factor': profit_factor,
            'Alpha': alpha,
            'Beta': beta
        }

        return metrics

    def plot_performance(self, portfolio_values, prices, signals, strategy_name):
        """Plot comprehensive performance charts"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Equity curve
        portfolio_returns = (portfolio_values / portfolio_values.iloc[0])
        benchmark_returns = (prices / prices.iloc[0])

        ax1.plot(portfolio_returns.index, portfolio_returns,
                 label=f'{strategy_name}', linewidth=2)
        ax1.plot(benchmark_returns.index, benchmark_returns,
                 label='Benchmark', linewidth=1, alpha=0.7)
        ax1.set_title('Equity Curve', fontweight='bold')
        ax1.set_ylabel('Cumulative Return')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Drawdown
        cumulative_returns = (
            1 + portfolio_values.pct_change().dropna()).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max

        ax2.fill_between(drawdown.index, drawdown *
                         100, 0, alpha=0.3, color='red')
        ax2.plot(drawdown.index, drawdown * 100, color='red', linewidth=1)
        ax2.set_title('Drawdown', fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)

        # 3. Rolling Sharpe ratio (6-month)
        returns = portfolio_values.pct_change().dropna()
        rolling_sharpe = returns.rolling(window=126).mean(
        ) / returns.rolling(window=126).std() * np.sqrt(252)

        ax3.plot(rolling_sharpe.index, rolling_sharpe,
                 color='green', linewidth=1)
        ax3.set_title('6-Month Rolling Sharpe Ratio', fontweight='bold')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.grid(True, alpha=0.3)

        # 4. Signal frequency
        signal_changes = signals.diff().fillna(0)
        buy_signals = (signal_changes == 1).astype(int)
        sell_signals = (signal_changes == -1).astype(int)

        ax4.bar(buy_signals.index, buy_signals, color='green',
                alpha=0.6, label='Buy Signals', width=1)
        ax4.bar(sell_signals.index, sell_signals, color='red',
                alpha=0.6, label='Sell Signals', width=1)
        ax4.set_title('Trading Signals', fontweight='bold')
        ax4.set_ylabel('Signal')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def add_transaction_costs(self, portfolio_values, trades, commission_pct=0.001):
        """Add transaction costs to portfolio performance"""
        print(f"Adding transaction costs ({commission_pct:.1%} per trade)...")

        # Calculate total commission costs
        total_commission = sum(
            trade['value'] * commission_pct for trade in trades)

        # Adjust portfolio values
        adjusted_values = portfolio_values.copy()
        cumulative_commission = 0

        for i, (date, value) in enumerate(portfolio_values.items()):
            # Find commissions up to this date
            trades_to_date = [t for t in trades if t['date'] <= date]
            daily_commission = sum(
                t['value'] * commission_pct for t in trades_to_date)
            cumulative_commission = daily_commission

            adjusted_values.loc[date] = value - cumulative_commission

        print(f"Total commission costs: ${total_commission:.2f}")
        print(
            f"Net vs Gross performance impact: {(adjusted_values.iloc[-1] / portfolio_values.iloc[-1] - 1):.2%}")

        return adjusted_values

    def walk_forward_analysis(self, prices, predictions, window_size=252, retrain_frequency=63):
        """Perform walk-forward analysis for strategy robustness"""
        print("Performing Walk-Forward Analysis...")

        all_signals = pd.Series(dtype=float)
        performance_by_period = []

        n_periods = len(prices) - window_size
        for i in range(0, n_periods, retrain_frequency):
            start_idx = i
            end_idx = i + window_size

            if end_idx >= len(prices):
                break

            # Current window
            window_prices = prices.iloc[start_idx:end_idx]
            window_predictions = predictions.iloc[start_idx:end_idx]

            # Generate signals for this window
            window_signals = self.generate_signals(window_predictions)

            # Store signals
            all_signals = pd.concat([all_signals, window_signals])

            # Calculate window performance
            if len(window_signals) > 0:
                window_portfolio = self.vectorbt_backtest(
                    window_prices, window_signals, f"Window_{i}")
                window_metrics = window_portfolio.stats()

                performance_by_period.append({
                    'period': i,
                    'start_date': window_prices.index[0],
                    'end_date': window_prices.index[-1],
                    'total_return': window_metrics['Total Return'],
                    'sharpe_ratio': window_metrics['Sharpe Ratio'],
                    'max_drawdown': window_metrics['Max Drawdown']
                })

        # Remove duplicate indices (overlapping periods)
        all_signals = all_signals[~all_signals.index.duplicated(keep='last')]

        # Overall performance with walk-forward signals
        aligned_prices = prices.reindex(all_signals.index)
        wf_portfolio = self.vectorbt_backtest(
            aligned_prices, all_signals, "Walk-Forward Strategy")

        # Plot walk-forward performance
        performance_df = pd.DataFrame(performance_by_period)

        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(performance_df['end_date'],
                 performance_df['total_return'] * 100, 'o-')
        plt.title('Walk-Forward Analysis: Period Returns', fontweight='bold')
        plt.ylabel('Return (%)')
        plt.grid(True, alpha=0.3)

        plt.subplot(2, 1, 2)
        plt.plot(performance_df['end_date'],
                 performance_df['sharpe_ratio'], 'o-', color='green')
        plt.title('Walk-Forward Analysis: Sharpe Ratio', fontweight='bold')
        plt.ylabel('Sharpe Ratio')
        plt.xlabel('Date')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        return wf_portfolio, performance_df

    def benchmark_comparison(self, strategy_metrics, benchmark_metrics, strategy_name="ML Strategy"):
        """Compare strategy performance against benchmark"""
        print(f"\nBENCHMARK COMPARISON: {strategy_name} vs Buy & Hold")
        print("=" * 50)

        comparison_data = []
        metrics_to_compare = [
            'Annual Return', 'Annual Volatility', 'Sharpe Ratio',
            'Max Drawdown', 'Calmar Ratio', 'Win Rate'
        ]

        for metric in metrics_to_compare:
            strategy_value = strategy_metrics.get(metric, 0)
            benchmark_value = benchmark_metrics.get(metric, 0)

            if metric in ['Annual Return', 'Sharpe Ratio', 'Calmar Ratio', 'Win Rate']:
                # Higher is better
                improvement = strategy_value - benchmark_value
                better = "✅" if improvement > 0 else "❌"
            else:
                # Lower is better (volatility, drawdown)
                improvement = benchmark_value - strategy_value
                better = "✅" if improvement > 0 else "❌"

            comparison_data.append({
                'Metric': metric,
                'Strategy': strategy_value,
                'Benchmark': benchmark_value,
                'Improvement': improvement,
                'Better': better
            })

        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.round(4))

        # Calculate alpha (excess risk-adjusted return)
        alpha = strategy_metrics.get('Alpha', 0)
        print(f"\nAlpha (excess return): {alpha:.4f}")

        return comparison_df

    def run_complete_backtest(self, prices, predictions, strategy_name="ML Strategy"):
        """Run complete backtesting pipeline"""
        print(f"RUNNING COMPLETE BACKTEST: {strategy_name}")
        print("=" * 50)

        # 1. Prepare data and generate signals
        aligned_prices, aligned_predictions = self.prepare_data(
            prices, predictions)
        signals = self.generate_signals(aligned_predictions)

        print(
            f"Backtest period: {aligned_prices.index[0]} to {aligned_prices.index[-1]}")
        print(f"Total signals: {len(signals)}")
        print(f"Buy signals: {(signals == 1).sum()}")
        print(f"Sell signals: {(signals == -1).sum()}")

        # 2. Run vectorbt backtest
        portfolio = self.vectorbt_backtest(
            aligned_prices, signals, strategy_name)

        # 3. Manual backtest for transparency
        manual_results, trades_df = self.manual_backtest(
            aligned_prices, signals)

        # 4. Calculate performance metrics
        portfolio_values = portfolio.get_total_value()
        strategy_metrics = self.calculate_performance_metrics(
            portfolio_values, aligned_prices)

        # 5. Benchmark metrics (buy & hold)
        benchmark_metrics = self.calculate_performance_metrics(
            aligned_prices, aligned_prices)

        # 6. Plot performance
        self.plot_performance(
            portfolio_values, aligned_prices, signals, strategy_name)

        # 7. Compare with benchmark
        comparison = self.benchmark_comparison(
            strategy_metrics, benchmark_metrics, strategy_name)

        # 8. Walk-forward analysis
        wf_portfolio, wf_performance = self.walk_forward_analysis(
            aligned_prices, aligned_predictions)

        # 9. Transaction cost analysis
        if len(trades_df) > 0:
            adjusted_values = self.add_transaction_costs(
                portfolio_values, trades_df.to_dict('records'))
            adjusted_metrics = self.calculate_performance_metrics(
                adjusted_values, aligned_prices)

            print("\nWITH TRANSACTION COSTS:")
            print(
                f"Net Annual Return: {adjusted_metrics['Annual Return']:.2%}")
            print(
                f"Gross Annual Return: {strategy_metrics['Annual Return']:.2%}")
            print(
                f"Cost Impact: {(adjusted_metrics['Annual Return'] - strategy_metrics['Annual Return']):.2%}")

        # Compile final results
        results = {
            'portfolio': portfolio,
            'manual_results': manual_results,
            'trades': trades_df,
            'strategy_metrics': strategy_metrics,
            'benchmark_metrics': benchmark_metrics,
            'comparison': comparison,
            'walk_forward_portfolio': wf_portfolio,
            'walk_forward_performance': wf_performance,
            'signals': signals
        }

        print(f"\n🎯 BACKTESTING COMPLETE: {strategy_name}")
        print(f"Final Strategy Return: {strategy_metrics['Total Return']:.2%}")
        print(
            f"Final Benchmark Return: {benchmark_metrics['Total Return']:.2%}")
        print(
            f"Excess Return: {(strategy_metrics['Total Return'] - benchmark_metrics['Total Return']):.2%}")

        return results

# Tutorial: Backtesting script using vectorbt


def backtesting_tutorial():
    """Tutorial: Build backtesting script with vectorbt"""
    print("BACKTESTING TUTORIAL WITH VECTORBT")
    print("=" * 40)

    # Load sample data
    def load_sample_data():
        prices = yf.download('SPY', start='2020-01-01',
                             end='2023-12-31')['Adj Close']

        # Generate sample predictions (random for demonstration)
        np.random.seed(42)
        predictions = pd.Series(
            np.random.randn(len(prices)) * 0.1 + 0.02,
            index=prices.index
        ).cumsum()  # Random walk for demonstration

        return prices, predictions

    prices, predictions = load_sample_data()

    # Initialize backtester
    backtester = TradingStrategyBacktester(
        initial_capital=10000, commission=0.001)

    # Run complete backtest
    results = backtester.run_complete_backtest(
        prices, predictions, "Tutorial Strategy")

    return backtester, results

# Challenge: Transaction costs and performance comparison


def transaction_cost_challenge(backtester, results):
    """Challenge: Analyze transaction cost impact"""
    print("TRANSACTION COST ANALYSIS CHALLENGE")
    print("=" * 50)

    # Test different commission rates
    commission_rates = [0.0005, 0.001, 0.002, 0.005, 0.01]  # 0.05% to 1%

    performance_by_commission = []

    for commission in commission_rates:
        print(f"\nTesting commission rate: {commission:.2%}")

        # Create new backtester with different commission
        test_backtester = TradingStrategyBacktester(
            initial_capital=10000,
            commission=commission
        )

        # Re-run with adjusted commission
        prices = results['portfolio'].get_data()['Close']
        signals = results['signals']

        test_portfolio = test_backtester.vectorbt_backtest(
            prices, signals, f"Commission_{commission}"
        )

        # Get performance
        test_metrics = test_portfolio.stats()

        performance_by_commission.append({
            'Commission Rate': commission,
            'Total Return': test_metrics['Total Return'],
            'Sharpe Ratio': test_metrics['Sharpe Ratio'],
            'Max Drawdown': test_metrics['Max Drawdown'],
            'Total Trades': test_metrics['Total Trades']
        })

    # Analyze commission impact
    performance_df = pd.DataFrame(performance_by_commission)

    plt.figure(figsize=(12, 10))

    plt.subplot(2, 2, 1)
    plt.plot(performance_df['Commission Rate'] * 100,
             performance_df['Total Return'] * 100, 'o-')
    plt.title('Commission Impact on Total Return', fontweight='bold')
    plt.xlabel('Commission Rate (%)')
    plt.ylabel('Total Return (%)')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 2)
    plt.plot(performance_df['Commission Rate'] * 100,
             performance_df['Sharpe Ratio'], 'o-', color='green')
    plt.title('Commission Impact on Sharpe Ratio', fontweight='bold')
    plt.xlabel('Commission Rate (%)')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 3)
    plt.plot(performance_df['Commission Rate'] * 100,
             performance_df['Max Drawdown'] * 100, 'o-', color='red')
    plt.title('Commission Impact on Max Drawdown', fontweight='bold')
    plt.xlabel('Commission Rate (%)')
    plt.ylabel('Max Drawdown (%)')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 4)
    plt.bar(performance_df['Commission Rate'] *
            100, performance_df['Total Trades'])
    plt.title('Total Trades by Commission Rate', fontweight='bold')
    plt.xlabel('Commission Rate (%)')
    plt.ylabel('Number of Trades')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("\nCommission Impact Analysis:")
    print("Higher commissions reduce profitability, especially for high-frequency strategies")
    print("Optimal commission depends on strategy frequency and expected returns")

    return performance_df


if __name__ == "__main__":
    # Run backtesting tutorial
    backtester, results = backtesting_tutorial()

    # Run transaction cost challenge
    performance_df = transaction_cost_challenge(backtester, results)

    # Display final results
    print("\n" + "=" * 60)
    print("BACKTESTING ANALYSIS COMPLETE")
    print("=" * 60)

    # Key metrics from results
    strategy_metrics = results['strategy_metrics']
    benchmark_metrics = results['benchmark_metrics']

    print(f"\nKEY METRICS:")
    print(f"Strategy Sharpe Ratio: {strategy_metrics['Sharpe Ratio']:.2f}")
    print(f"Benchmark Sharpe Ratio: {benchmark_metrics['Sharpe Ratio']:.2f}")
    print(f"Strategy Max Drawdown: {strategy_metrics['Max Drawdown']:.2%}")
    print(f"Benchmark Max Drawdown: {benchmark_metrics['Max Drawdown']:.2%}")
    print(f"Excess Return (Alpha): {strategy_metrics['Alpha']:.2%}")
