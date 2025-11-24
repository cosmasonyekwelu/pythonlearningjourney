
"""
Day 61: Reward System Design for Reinforcement Learning
Implementation of advanced reward functions for trading agents
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats
from enum import Enum
import warnings
warnings.filterwarnings('ignore')


class RewardType(Enum):
    """Types of reward functions"""
    SIMPLE_RETURN = "simple_return"
    LOG_RETURN = "log_return"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    DRAWDOWN_PENALIZED = "drawdown_penalized"
    RISK_ADJUSTED = "risk_adjusted"
    ADAPTIVE = "adaptive"


class RewardSystem:
    """Advanced reward system for trading reinforcement learning"""

    def __init__(self, initial_balance=10000, risk_free_rate=0.02/252):
        self.initial_balance = initial_balance
        self.risk_free_rate = risk_free_rate
        self.portfolio_history = []
        self.return_history = []
        self.drawdown_history = []

    def update_portfolio(self, portfolio_value):
        """Update portfolio history for reward calculations"""
        self.portfolio_history.append(portfolio_value)

        # Calculate returns
        if len(self.portfolio_history) > 1:
            daily_return = (
                portfolio_value - self.portfolio_history[-2]) / self.portfolio_history[-2]
            self.return_history.append(daily_return)

        # Calculate drawdown
        if len(self.portfolio_history) > 0:
            peak = max(self.portfolio_history)
            current_drawdown = (peak - portfolio_value) / peak
            self.drawdown_history.append(current_drawdown)

    def simple_return_reward(self, current_value, previous_value, transaction_cost=0):
        """Simple percentage return reward"""
        if previous_value == 0:
            return 0

        raw_return = (current_value - previous_value) / previous_value
        reward = raw_return - abs(transaction_cost)
        return reward

    def log_return_reward(self, current_value, previous_value, transaction_cost=0):
        """Logarithmic return reward"""
        if previous_value == 0 or current_value == 0:
            return 0

        log_return = np.log(current_value / previous_value)
        reward = log_return - abs(transaction_cost)
        return reward

    def sharpe_ratio_reward(self, window=20):
        """Sharpe ratio based reward"""
        if len(self.return_history) < window:
            return 0

        recent_returns = np.array(self.return_history[-window:])
        excess_returns = recent_returns - self.risk_free_rate

        if len(excess_returns) < 2 or np.std(excess_returns) == 0:
            return 0

        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        # Annualize (assuming daily returns)
        sharpe_annualized = sharpe * np.sqrt(252)

        return sharpe_annualized / 10  # Scale for reasonable reward range

    def sortino_ratio_reward(self, window=20):
        """Sortino ratio based reward (downside risk only)"""
        if len(self.return_history) < window:
            return 0

        recent_returns = np.array(self.return_history[-window:])
        excess_returns = recent_returns - self.risk_free_rate

        # Only consider negative returns for downside deviation
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return np.mean(excess_returns) * 10  # Reward positive returns

        sortino = np.mean(excess_returns) / np.std(downside_returns)
        sortino_annualized = sortino * np.sqrt(252)

        return sortino_annualized / 10

    def calmar_ratio_reward(self, window=252):
        """Calmar ratio based reward (return vs max drawdown)"""
        if len(self.portfolio_history) < window:
            return 0

        recent_values = np.array(self.portfolio_history[-window:])
        recent_returns = np.array(self.return_history[-window+1:])

        # Calculate annualized return
        total_return = (recent_values[-1] -
                        recent_values[0]) / recent_values[0]
        annualized_return = (1 + total_return) ** (252/len(recent_values)) - 1

        # Calculate maximum drawdown
        peak = np.maximum.accumulate(recent_values)
        drawdown = (peak - recent_values) / peak
        max_drawdown = np.max(drawdown)

        if max_drawdown == 0:
            return annualized_return * 10

        calmar_ratio = annualized_return / max_drawdown
        return calmar_ratio / 10

    def drawdown_penalized_reward(self, current_value, previous_value,
                                  drawdown_penalty_factor=2.0, transaction_cost=0):
        """Reward that heavily penalizes drawdowns"""
        if previous_value == 0:
            return 0

        raw_return = (current_value - previous_value) / previous_value

        # Calculate current drawdown
        peak = max(self.portfolio_history)
        current_drawdown = (peak - current_value) / peak

        # Base reward with drawdown penalty
        base_reward = raw_return - abs(transaction_cost)
        drawdown_penalty = current_drawdown * drawdown_penalty_factor

        reward = base_reward - drawdown_penalty
        return reward

    def risk_adjusted_reward(self, current_value, previous_value,
                             risk_aversion=1.0, transaction_cost=0):
        """Multi-factor risk-adjusted reward"""
        if previous_value == 0:
            return 0

        # Base return component
        raw_return = (current_value - previous_value) / previous_value

        # Volatility penalty (using recent returns)
        if len(self.return_history) >= 10:
            volatility = np.std(self.return_history[-10:])
            volatility_penalty = risk_aversion * volatility
        else:
            volatility_penalty = 0

        # Drawdown penalty
        peak = max(self.portfolio_history)
        current_drawdown = (peak - current_value) / peak
        drawdown_penalty = current_drawdown * 0.5

        # Concentration penalty (simplified)
        # In practice, this would consider position concentrations

        reward = (raw_return - abs(transaction_cost) -
                  volatility_penalty - drawdown_penalty)

        return reward

    def adaptive_reward(self, current_value, previous_value, market_volatility,
                        performance_trend, transaction_cost=0):
        """Adaptive reward that changes based on market conditions"""
        if previous_value == 0:
            return 0

        raw_return = (current_value - previous_value) / previous_value

        # Adjust risk aversion based on market volatility
        base_risk_aversion = 1.0
        volatility_adjusted_aversion = base_risk_aversion * \
            (1 + market_volatility)

        # Adjust drawdown sensitivity based on performance
        if performance_trend < -0.1:  # Poor recent performance
            drawdown_sensitivity = 2.0
        else:
            drawdown_sensitivity = 1.0

        # Calculate adaptive components
        peak = max(self.portfolio_history)
        current_drawdown = (peak - current_value) / peak

        volatility_penalty = volatility_adjusted_aversion * market_volatility
        drawdown_penalty = drawdown_sensitivity * current_drawdown

        reward = (raw_return - abs(transaction_cost) -
                  volatility_penalty - drawdown_penalty)

        return reward

    def calculate_reward(self, reward_type, current_value, previous_value,
                         transaction_cost=0, **kwargs):
        """Calculate reward based on specified type"""
        self.update_portfolio(current_value)

        if reward_type == RewardType.SIMPLE_RETURN:
            return self.simple_return_reward(current_value, previous_value, transaction_cost)

        elif reward_type == RewardType.LOG_RETURN:
            return self.log_return_reward(current_value, previous_value, transaction_cost)

        elif reward_type == RewardType.SHARPE_RATIO:
            return self.sharpe_ratio_reward(**kwargs)

        elif reward_type == RewardType.SORTINO_RATIO:
            return self.sortino_ratio_reward(**kwargs)

        elif reward_type == RewardType.CALMAR_RATIO:
            return self.calmar_ratio_reward(**kwargs)

        elif reward_type == RewardType.DRAWDOWN_PENALIZED:
            return self.drawdown_penalized_reward(current_value, previous_value,
                                                  transaction_cost=transaction_cost, **kwargs)

        elif reward_type == RewardType.RISK_ADJUSTED:
            return self.risk_adjusted_reward(current_value, previous_value,
                                             transaction_cost=transaction_cost, **kwargs)

        elif reward_type == RewardType.ADAPTIVE:
            return self.adaptive_reward(current_value, previous_value,
                                        transaction_cost=transaction_cost, **kwargs)

        else:
            return self.simple_return_reward(current_value, previous_value, transaction_cost)


class RewardComparator:
    """Compare different reward functions on historical data"""

    def __init__(self, symbol='AAPL', initial_balance=10000):
        self.symbol = symbol
        self.initial_balance = initial_balance

    def generate_trading_signals(self, data):
        """Generate simple trading signals for reward comparison"""
        signals = []
        positions = []
        portfolio_values = [self.initial_balance]

        # Simple moving average crossover strategy
        data['sma_20'] = data['Close'].rolling(window=20).mean()
        data['sma_50'] = data['Close'].rolling(window=50).mean()

        position = 0  # 0: out, 1: long
        cash = self.initial_balance

        for i in range(1, len(data)):
            current_price = data['Close'].iloc[i]
            prev_price = data['Close'].iloc[i-1]

            # Generate signal
            if data['sma_20'].iloc[i] > data['sma_50'].iloc[i] and position == 0:
                # Buy signal
                position = 1
                shares = cash / current_price
                cash = 0
                signal = 2  # buy

            elif data['sma_20'].iloc[i] < data['sma_50'].iloc[i] and position == 1:
                # Sell signal
                cash = shares * current_price
                shares = 0
                position = 0
                signal = 0  # sell
            else:
                signal = 1  # hold

            # Calculate portfolio value
            if position == 1:
                portfolio_value = shares * current_price
            else:
                portfolio_value = cash

            signals.append(signal)
            positions.append(position)
            portfolio_values.append(portfolio_value)

        return signals, positions, portfolio_values

    def evaluate_reward_functions(self, portfolio_values, signals):
        """Evaluate different reward functions on the same trading strategy"""
        reward_systems = {}
        reward_histories = {}

        reward_types = [
            RewardType.SIMPLE_RETURN,
            RewardType.LOG_RETURN,
            RewardType.SHARPE_RATIO,
            RewardType.SORTINO_RATIO,
            RewardType.DRAWDOWN_PENALIZED,
            RewardType.RISK_ADJUSTED
        ]

        for reward_type in reward_types:
            reward_system = RewardSystem(self.initial_balance)
            rewards = []

            for i in range(1, len(portfolio_values)):
                current_value = portfolio_values[i]
                previous_value = portfolio_values[i-1]

                # Simple transaction cost model
                transaction_cost = 0
                if i > 1 and signals[i-1] != signals[i-2]:
                    transaction_cost = 0.001  # 0.1% transaction cost

                reward = reward_system.calculate_reward(
                    reward_type,
                    current_value,
                    previous_value,
                    transaction_cost=transaction_cost
                )
                rewards.append(reward)

            reward_systems[reward_type.value] = reward_system
            reward_histories[reward_type.value] = rewards

        return reward_systems, reward_histories

    def calculate_performance_metrics(self, portfolio_values):
        """Calculate comprehensive performance metrics"""
        returns = np.diff(portfolio_values) / portfolio_values[:-1]

        metrics = {}

        # Basic metrics
        metrics['total_return'] = (
            portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
        metrics['annualized_return'] = (
            1 + metrics['total_return']) ** (252/len(returns)) - 1

        # Risk metrics
        metrics['volatility'] = np.std(returns) * np.sqrt(252)
        metrics['sharpe_ratio'] = (metrics['annualized_return'] - 0.02) / \
            metrics['volatility'] if metrics['volatility'] > 0 else 0

        # Drawdown metrics
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (peak - portfolio_values) / peak
        metrics['max_drawdown'] = np.max(drawdown)
        metrics['calmar_ratio'] = metrics['annualized_return'] / \
            metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else 0

        # Sortino ratio (downside risk)
        downside_returns = returns[returns < 0]
        downside_volatility = np.std(
            downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        metrics['sortino_ratio'] = (metrics['annualized_return'] - 0.02) / \
            downside_volatility if downside_volatility > 0 else 0

        return metrics

    def plot_reward_comparison(self, reward_histories, portfolio_values):
        """Plot comparison of different reward functions"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Cumulative rewards
        axes[0, 0].set_title('Cumulative Rewards by Function')
        for reward_type, rewards in reward_histories.items():
            cumulative_rewards = np.cumsum(rewards)
            axes[0, 0].plot(cumulative_rewards, label=reward_type, alpha=0.7)
        axes[0, 0].set_ylabel('Cumulative Reward')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Plot 2: Portfolio value
        axes[0, 1].plot(portfolio_values)
        axes[0, 1].set_title('Portfolio Value Over Time')
        axes[0, 1].set_ylabel('Portfolio Value ($)')
        axes[0, 1].grid(True)

        # Plot 3: Reward distributions
        reward_data = []
        reward_labels = []
        for reward_type, rewards in reward_histories.items():
            reward_data.append(rewards)
            reward_labels.append(reward_type)

        axes[1, 0].boxplot(reward_data, labels=reward_labels)
        axes[1, 0].set_title('Reward Distributions')
        axes[1, 0].set_ylabel('Reward Value')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True)

        # Plot 4: Rolling Sharpe ratio of rewards
        axes[1, 1].set_title('Rolling Sharpe Ratio of Rewards (Window=20)')
        for reward_type, rewards in reward_histories.items():
            rolling_sharpe = []
            for i in range(20, len(rewards)):
                window_rewards = rewards[i-20:i]
                if np.std(window_rewards) > 0:
                    sharpe = np.mean(window_rewards) / \
                        np.std(window_rewards) * np.sqrt(252)
                    rolling_sharpe.append(sharpe)
                else:
                    rolling_sharpe.append(0)

            axes[1, 1].plot(range(20, len(rewards)),
                            rolling_sharpe, label=reward_type, alpha=0.7)

        axes[1, 1].set_ylabel('Rolling Sharpe Ratio')
        axes[1, 1].legend()
        axes[1, 1].grid(True)

        plt.tight_layout()
        plt.savefig('reward_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

    def run_complete_analysis(self):
        """Run complete reward system analysis"""
        print("Starting Reward System Design Analysis...")
        print("=" * 60)

        # Fetch market data
        print("1. Fetching market data...")
        data = yf.download(self.symbol, period='2y')

        # Generate trading signals
        print("2. Generating trading signals...")
        signals, positions, portfolio_values = self.generate_trading_signals(
            data)

        # Evaluate reward functions
        print("3. Evaluating different reward functions...")
        reward_systems, reward_histories = self.evaluate_reward_functions(
            portfolio_values, signals)

        # Calculate performance metrics
        print("4. Calculating performance metrics...")
        metrics = self.calculate_performance_metrics(portfolio_values)

        # Display results
        print("\n" + "=" * 60)
        print("REWARD SYSTEM ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Symbol: {self.symbol}")
        print(f"Initial Portfolio: ${self.initial_balance:.2f}")
        print(f"Final Portfolio: ${portfolio_values[-1]:.2f}")
        print(f"Total Return: {metrics['total_return']*100:.2f}%")
        print(f"Annualized Return: {metrics['annualized_return']*100:.2f}%")
        print(f"Volatility: {metrics['volatility']*100:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        print(f"Sortino Ratio: {metrics['sortino_ratio']:.3f}")
        print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"Calmar Ratio: {metrics['calmar_ratio']:.3f}")

        print("\nReward Function Statistics:")
        for reward_type, rewards in reward_histories.items():
            reward_array = np.array(rewards)
            print(f"\n{reward_type}:")
            print(f"  Mean: {np.mean(reward_array):.6f}")
            print(f"  Std: {np.std(reward_array):.6f}")
            print(
                f"  Sharpe: {np.mean(reward_array)/np.std(reward_array) if np.std(reward_array) > 0 else 0:.3f}")
            print(f"  Total: {np.sum(reward_array):.3f}")

        # Plot results
        print("\n5. Generating visualizations...")
        self.plot_reward_comparison(reward_histories, portfolio_values)

        return reward_systems, reward_histories, metrics


def main():
    """Main function to run reward system analysis"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Reward System Design Analysis')
    parser.add_argument('--symbol', type=str,
                        default='AAPL', help='Stock symbol')
    parser.add_argument('--initial_balance', type=float,
                        default=10000, help='Initial portfolio value')

    args = parser.parse_args()

    # Initialize and run analysis
    comparator = RewardComparator(
        symbol=args.symbol, initial_balance=args.initial_balance)
    reward_systems, reward_histories, metrics = comparator.run_complete_analysis()

    print("\nReward system analysis completed successfully!")
    print(f"Results saved to: reward_comparison.png")


if __name__ == "__main__":
    main()
