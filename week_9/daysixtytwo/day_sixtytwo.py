
"""
Day 62: Strategy Optimization with Reinforcement Learning
Implementation of advanced RL algorithms for trading strategy optimization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Reinforcement Learning
import gym
from gym import spaces
from stable_baselines3 import PPO, A2C, SAC, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback

class MultiAssetTradingEnvironment(gym.Env):
    """Advanced trading environment with multiple assets and complex state"""
    
    def __init__(self, df_dict, initial_balance=10000, transaction_cost=0.001,
                 lookback_window=30, max_position_per_asset=0.2, 
                 risk_free_rate=0.02/252):
        super(MultiAssetTradingEnvironment, self).__init__()
        
        self.df_dict = df_dict
        self.assets = list(df_dict.keys())
        self.num_assets = len(self.assets)
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.lookback_window = lookback_window
        self.max_position_per_asset = max_position_per_asset
        self.risk_free_rate = risk_free_rate
        
        # Synchronize data
        self._synchronize_data()
        
        # Action space: continuous actions for each asset [-1, 1] 
        # where -1 = max short, 0 = no position, 1 = max long
        self.action_space = spaces.Box(
            low=-1.0, 
            high=1.0, 
            shape=(self.num_assets,), 
            dtype=np.float32
        )
        
        # State space: portfolio state + market features for all assets
        state_size = (3 + 8 * lookback_window) * self.num_assets  # cash, positions, value + features
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(state_size,), 
            dtype=np.float32
        )
        
        self.reset()
    
    def _synchronize_data(self):
        """Synchronize data across all assets"""
        common_index = None
        
        # Find common date range
        for asset, df in self.df_dict.items():
            if common_index is None:
                common_index = df.index
            else:
                common_index = common_index.intersection(df.index)
        
        # Filter data to common range
        self.synchronized_data = {}
        for asset, df in self.df_dict.items():
            self.synchronized_data[asset] = df.loc[common_index]
        
        self.dates = common_index
        self.current_step = self.lookback_window
    
    def _get_asset_features(self, asset):
        """Get features for a specific asset"""
        df = self.synchronized_data[asset]
        
        if self.current_step < self.lookback_window:
            return np.zeros(8 * self.lookback_window)
        
        recent_data = df.iloc[self.current_step - self.lookback_window:self.current_step]
        
        features = []
        # Price-based features
        features.extend(recent_data['price'].values)
        features.extend(recent_data['returns'].values)
        features.extend(recent_data['volume'].values)
        
        # Technical indicators
        features.extend(recent_data['rsi'].values)
        features.extend(recent_data['macd'].values)
        features.extend(recent_data['sma_20'].values)
        features.extend(recent_data['sma_50'].values)
        features.extend(recent_data['volatility'].values)
        
        return np.array(features)
    
    def _get_observation(self):
        """Get current observation for all assets"""
        observation = []
        
        # Portfolio state for each asset
        for asset in self.assets:
            asset_state = [
                self.cash / (self.num_assets * 10),  # Normalized cash allocation
                self.positions[asset],
                self.asset_values[asset] / self.initial_balance  # Normalized value
            ]
            observation.extend(asset_state)
            
            # Market features for each asset
            asset_features = self._get_asset_features(asset)
            observation.extend(asset_features)
        
        return np.array(observation, dtype=np.float32)
    
    def _calculate_portfolio_value(self):
        """Calculate total portfolio value"""
        total_value = self.cash
        for asset in self.assets:
            current_price = self.synchronized_data[asset].iloc[self.current_step]['price']
            total_value += self.positions[asset] * current_price
        return total_value
    
    def _calculate_asset_values(self):
        """Calculate individual asset values"""
        asset_values = {}
        for asset in self.assets:
            current_price = self.synchronized_data[asset].iloc[self.current_step]['price']
            asset_values[asset] = self.positions[asset] * current_price
        return asset_values
    
    def _execute_trades(self, actions):
        """Execute trades based on continuous actions"""
        total_portfolio_value = self._calculate_portfolio_value()
        
        for i, asset in enumerate(self.assets):
            action = actions[i]
            current_price = self.synchronized_data[asset].iloc[self.current_step]['price']
            
            # Calculate target position value
            target_value = action * total_portfolio_value * self.max_position_per_asset
            
            # Current position value
            current_value = self.positions[asset] * current_price
            
            # Trade amount
            trade_value = target_value - current_value
            
            if abs(trade_value) > 0:
                # Calculate shares to trade
                shares_to_trade = trade_value / current_price
                
                # Apply transaction cost
                trade_cost = abs(shares_to_trade * current_price * self.transaction_cost)
                
                # Check if we have enough cash for buy or enough shares for sell
                if trade_value > 0:  # Buy
                    if self.cash >= (trade_value + trade_cost):
                        self.positions[asset] += shares_to_trade
                        self.cash -= (trade_value + trade_cost)
                else:  # Sell
                    if self.positions[asset] >= abs(shares_to_trade):
                        self.positions[asset] += shares_to_trade  # shares_to_trade is negative
                        self.cash += (abs(trade_value) - trade_cost)
    
    def _calculate_advanced_reward(self):
        """Calculate advanced risk-adjusted reward"""
        # Portfolio return
        portfolio_return = (self.portfolio_value - self.prev_portfolio_value) / self.prev_portfolio_value
        
        # Risk-adjusted components
        reward = portfolio_return
        
        # Penalize excessive turnover
        turnover_penalty = 0
        if hasattr(self, 'prev_positions'):
            for asset in self.assets:
                prev_value = self.prev_positions[asset] * self.prev_prices[asset]
                current_value = self.positions[asset] * self.current_prices[asset]
                if prev_value > 0:
                    turnover = abs(current_value - prev_value) / prev_value
                    turnover_penalty += turnover * 0.01
        
        reward -= turnover_penalty
        
        # Penalize concentration risk
        concentration_penalty = 0
        total_value = self.portfolio_value
        for asset in self.assets:
            weight = self.asset_values[asset] / total_value
            concentration_penalty += (weight - 1/self.num_assets) ** 2
        
        reward -= concentration_penalty * 0.1
        
        # Reward risk-adjusted returns (Sharpe-like)
        if hasattr(self, 'return_history'):
            self.return_history.append(portfolio_return)
            if len(self.return_history) > 10:
                recent_returns = np.array(self.return_history[-10:])
                sharpe_like = np.mean(recent_returns) / (np.std(recent_returns) + 1e-8)
                reward += sharpe_like * 0.1
        
        return reward
    
    def reset(self):
        """Reset environment to initial state"""
        self.current_step = self.lookback_window
        self.cash = self.initial_balance
        self.positions = {asset: 0 for asset in self.assets}
        self.portfolio_value = self.initial_balance
        self.prev_portfolio_value = self.initial_balance
        self.asset_values = self._calculate_asset_values()
        self.return_history = []
        
        # Store previous state for reward calculation
        self.prev_positions = self.positions.copy()
        self.prev_prices = {asset: self.synchronized_data[asset].iloc[self.current_step]['price'] 
                          for asset in self.assets}
        self.current_prices = self.prev_prices.copy()
        
        return self._get_observation()
    
    def step(self, actions):
        """Execute one step in the environment"""
        # Store previous state
        self.prev_portfolio_value = self.portfolio_value
        self.prev_positions = self.positions.copy()
        self.prev_prices = self.current_prices.copy()
        
        # Update current prices
        self.current_prices = {asset: self.synchronized_data[asset].iloc[self.current_step]['price'] 
                             for asset in self.assets}
        
        # Execute trades
        self._execute_trades(actions)
        
        # Update portfolio values
        self.portfolio_value = self._calculate_portfolio_value()
        self.asset_values = self._calculate_asset_values()
        
        # Calculate reward
        reward = self._calculate_advanced_reward()
        
        # Move to next step
        self.current_step += 1
        
        # Check if episode is done
        done = self.current_step >= len(self.dates) - 1
        
        # Get new observation
        observation = self._get_observation()
        
        info = {
            'portfolio_value': self.portfolio_value,
            'cash': self.cash,
            'positions': self.positions,
            'asset_values': self.asset_values
        }
        
        return observation, reward, done, info
    
    def render(self, mode='human'):
        """Render environment state"""
        print(f"Step: {self.current_step}, Portfolio Value: {self.portfolio_value:.2f}")
        for asset in self.assets:
            print(f"  {asset}: {self.positions[asset]:.2f} shares, "
                  f"Value: {self.asset_values[asset]:.2f}")

class TrainingProgressCallback(BaseCallback):
    """Custom callback for tracking training progress"""
    
    def __init__(self, check_freq=1000, verbose=1):
        super(TrainingProgressCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.portfolio_values = []
        
    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            # Log training progress
            if len(self.model.ep_info_buffer) > 0:
                mean_reward = np.mean([ep_info['r'] for ep_info in self.model.ep_info_buffer])
                self.logger.record('train/mean_reward', mean_reward)
                
                if self.verbose > 0:
                    print(f"Step {self.n_calls}, Mean Reward: {mean_reward:.4f}")
        
        return True

class AdvancedRLTrader:
    """Advanced RL trading with multiple algorithms and assets"""
    
    def __init__(self, symbols=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN'], 
                 initial_balance=10000):
        self.symbols = symbols
        self.initial_balance = initial_balance
        
    def prepare_multi_asset_data(self, period='2y'):
        """Prepare data for multiple assets"""
        print("Fetching multi-asset data...")
        data_dict = {}
        
        for symbol in self.symbols:
            stock_data = yf.download(symbol, period=period)
            
            # Calculate features
            data = pd.DataFrame()
            data['price'] = stock_data['Close']
            data['returns'] = data['price'].pct_change()
            data['volume'] = stock_data['Volume']
            
            # Technical indicators
            data['sma_20'] = data['price'].rolling(window=20).mean()
            data['sma_50'] = data['price'].rolling(window=50).mean()
            
            # RSI
            delta = data['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = data['price'].ewm(span=12, adjust=False).mean()
            exp2 = data['price'].ewm(span=26, adjust=False).mean()
            data['macd'] = exp1 - exp2
            
            # Volatility
            data['volatility'] = data['returns'].rolling(window=20).std()
            
            # Drop NaN values and normalize
            data = data.dropna()
            for column in data.columns:
                if column != 'price':
                    data[column] = (data[column] - data[column].mean()) / data[column].std()
            
            data_dict[symbol] = data
        
        return data_dict
    
    def train_ppo_agent(self, data_dict, total_timesteps=50000):
        """Train PPO agent"""
        print("Training PPO Agent...")
        
        env = MultiAssetTradingEnvironment(data_dict, initial_balance=self.initial_balance)
        env = Monitor(env)
        
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            clip_range_vf=None,
            normalize_advantage=True,
            ent_coef=0.0,
            vf_coef=0.5,
            max_grad_norm=0.5,
            use_sde=False,
            sde_sample_freq=-1,
            target_kl=None,
            tensorboard_log="./ppo_tensorboard/",
            verbose=1
        )
        
        callback = TrainingProgressCallback(check_freq=1000)
        model.learn(total_timesteps=total_timesteps, callback=callback)
        
        return model, env
    
    def train_sac_agent(self, data_dict, total_timesteps=50000):
        """Train SAC agent"""
        print("Training SAC Agent...")
        
        env = MultiAssetTradingEnvironment(data_dict, initial_balance=self.initial_balance)
        env = Monitor(env)
        
        model = SAC(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            buffer_size=100000,
            learning_starts=100,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            action_noise=None,
            replay_buffer_class=None,
            replay_buffer_kwargs=None,
            optimize_memory_usage=False,
            ent_coef='auto',
            target_update_interval=1,
            target_entropy='auto',
            use_sde=False,
            sde_sample_freq=-1,
            use_sde_at_warmup=False,
            tensorboard_log="./sac_tensorboard/",
            verbose=1
        )
        
        callback = TrainingProgressCallback(check_freq=1000)
        model.learn(total_timesteps=total_timesteps, callback=callback)
        
        return model, env
    
    def evaluate_agent(self, model, env):
        """Evaluate trained agent"""
        print("Evaluating agent...")
        
        obs = env.reset()
        portfolio_history = []
        action_history = []
        
        done = False
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            
            portfolio_history.append(info['portfolio_value'])
            action_history.append(action)
        
        return portfolio_history, action_history, info
    
    def calculate_performance_metrics(self, portfolio_history, benchmark_data):
        """Calculate comprehensive performance metrics"""
        returns = np.diff(portfolio_history) / portfolio_history[:-1]
        
        metrics = {}
        
        # Basic metrics
        metrics['total_return'] = (portfolio_history[-1] - portfolio_history[0]) / portfolio_history[0]
        metrics['annualized_return'] = (1 + metrics['total_return']) ** (252/len(returns)) - 1
        
        # Risk metrics
        metrics['volatility'] = np.std(returns) * np.sqrt(252)
        metrics['sharpe_ratio'] = (metrics['annualized_return'] - 0.02) / metrics['volatility'] if metrics['volatility'] > 0 else 0
        
        # Drawdown metrics
        peak = np.maximum.accumulate(portfolio_history)
        drawdown = (peak - portfolio_history) / peak
        metrics['max_drawdown'] = np.max(drawdown)
        metrics['calmar_ratio'] = metrics['annualized_return'] / metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else 0
        
        # Benchmark comparison
        if benchmark_data is not None:
            benchmark_returns = np.diff(benchmark_data) / benchmark_data[:-1]
            benchmark_total_return = (benchmark_data[-1] - benchmark_data[0]) / benchmark_data[0]
            metrics['excess_return'] = metrics['total_return'] - benchmark_total_return
            
            # Information ratio
            active_returns = returns - benchmark_returns[:len(returns)]
            metrics['information_ratio'] = np.mean(active_returns) / np.std(active_returns) if np.std(active_returns) > 0 else 0
        
        return metrics
    
    def plot_results(self, portfolio_histories, algorithm_names, benchmark_data=None):
        """Plot training and evaluation results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Portfolio value comparison
        for i, (portfolio_history, name) in enumerate(zip(portfolio_histories, algorithm_names)):
            axes[0, 0].plot(portfolio_history, label=name, alpha=0.8)
        
        if benchmark_data is not None:
            axes[0, 0].plot(benchmark_data, label='Equal Weight Benchmark', linestyle='--', alpha=0.7)
        
        axes[0, 0].set_title('Portfolio Value Comparison')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Drawdown comparison
        for i, (portfolio_history, name) in enumerate(zip(portfolio_histories, algorithm_names)):
            peak = np.maximum.accumulate(portfolio_history)
            drawdown = (peak - portfolio_history) / peak
            axes[0, 1].plot(drawdown, label=name, alpha=0.8)
        
        axes[0, 1].set_title('Drawdown Comparison')
        axes[0, 1].set_ylabel('Drawdown')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot 3: Action distribution (for first algorithm)
        if len(portfolio_histories) > 0:
            # Use actions from first algorithm for demonstration
            actions = np.array(portfolio_histories[1])  # This would need actual action data
            if len(actions.shape) > 1:
                for i in range(min(3, actions.shape[1])):
                    axes[1, 0].hist(actions[:, i], alpha=0.7, label=f'Asset {i+1}', bins=20)
                axes[1, 0].set_title('Action Distribution')
                axes[1, 0].set_xlabel('Action Value')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].legend()
                axes[1, 0].grid(True)
        
        # Plot 4: Performance metrics comparison
        metrics_data = []
        metric_names = ['Total Return', 'Volatility', 'Sharpe Ratio', 'Max DD']
        
        for i, portfolio_history in enumerate(portfolio_histories):
            metrics = self.calculate_performance_metrics(portfolio_history, benchmark_data)
            metrics_data.append([
                metrics['total_return'] * 100,
                metrics['volatility'] * 100,
                metrics['sharpe_ratio'],
                metrics['max_drawdown'] * 100
            ])
        
        x = np.arange(len(metric_names))
        width = 0.8 / len(portfolio_histories)
        
        for i, (metrics, name) in enumerate(zip(metrics_data, algorithm_names)):
            axes[1, 1].bar(x + i * width, metrics, width, label=name, alpha=0.8)
        
        axes[1, 1].set_title('Performance Metrics Comparison')
        axes[1, 1].set_ylabel('Value')
        axes[1, 1].set_xticks(x + width * (len(portfolio_histories) - 1) / 2)
        axes[1, 1].set_xticklabels(metric_names)
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('advanced_rl_trading.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_equal_weight_benchmark(self, data_dict):
        """Create equal weight benchmark portfolio"""
        print("Creating equal weight benchmark...")
        
        # Get common dates
        common_dates = None
        for symbol, data in data_dict.items():
            if common_dates is None:
                common_dates = data.index
            else:
                common_dates = common_dates.intersection(data.index)
        
        # Calculate equal weight portfolio
        portfolio_value = [self.initial_balance]
        cash_per_asset = self.initial_balance / len(data_dict)
        
        for i in range(1, len(common_dates)):
            total_value = 0
            for symbol, data in data_dict.items():
                price = data.loc[common_dates[i]]['price']
                shares = cash_per_asset / data.loc[common_dates[0]]['price']
                total_value += shares * price
            
            portfolio_value.append(total_value)
        
        return np.array(portfolio_value)
    
    def run_complete_analysis(self, algorithms=['ppo', 'sac'], total_timesteps=50000):
        """Run complete advanced RL trading analysis"""
        print("Starting Advanced RL Strategy Optimization...")
        print("=" * 60)
        
        # Prepare data
        data_dict = self.prepare_multi_asset_data()
        
        # Create benchmark
        benchmark_data = self.create_equal_weight_benchmark(data_dict)
        
        # Train and evaluate agents
        models = {}
        envs = {}
        portfolio_histories = []
        algorithm_names = []
        
        for algorithm in algorithms:
            print(f"\nTraining {algorithm.upper()} agent...")
            
            if algorithm == 'ppo':
                model, env = self.train_ppo_agent(data_dict, total_timesteps)
            elif algorithm == 'sac':
                model, env = self.train_sac_agent(data_dict, total_timesteps)
            else:
                print(f"Algorithm {algorithm} not supported, skipping...")
                continue
            
            models[algorithm] = model
            envs[algorithm] = env
            
            # Evaluate agent
            portfolio_history, action_history, final_info = self.evaluate_agent(model, env)
            portfolio_histories.append(portfolio_history)
            algorithm_names.append(algorithm.upper())
            
            # Calculate performance metrics
            metrics = self.calculate_performance_metrics(portfolio_history, benchmark_data)
            
            print(f"\n{algorithm.upper()} Performance:")
            print(f"  Final Portfolio Value: ${final_info['portfolio_value']:.2f}")
            print(f"  Total Return: {metrics['total_return']*100:.2f}%")
            print(f"  Annualized Return: {metrics['annualized_return']*100:.2f}%")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
            print(f"  Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
            if 'excess_return' in metrics:
                print(f"  Excess Return: {metrics['excess_return']*100:.2f}%")
        
        # Benchmark performance
        benchmark_metrics = self.calculate_performance_metrics(benchmark_data, None)
        print(f"\nEqual Weight Benchmark Performance:")
        print(f"  Total Return: {benchmark_metrics['total_return']*100:.2f}%")
        print(f"  Annualized Return: {benchmark_metrics['annualized_return']*100:.2f}%")
        print(f"  Sharpe Ratio: {benchmark_metrics['sharpe_ratio']:.3f}")
        print(f"  Max Drawdown: {benchmark_metrics['max_drawdown']*100:.2f}%")
        
        # Plot results
        print("\nGenerating visualizations...")
        self.plot_results(portfolio_histories, algorithm_names, benchmark_data)
        
        return models, envs, portfolio_histories

def main():
    """Main function to run advanced RL trading"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced RL Strategy Optimization')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN'],
                       help='List of stock symbols')
    parser.add_argument('--algorithms', nargs='+', default=['ppo', 'sac'],
                       choices=['ppo', 'sac', 'a2c'], help='RL algorithms to use')
    parser.add_argument('--timesteps', type=int, default=50000, help='Training timesteps')
    parser.add_argument('--initial_balance', type=float, default=10000, help='Initial portfolio value')
    
    args = parser.parse_args()
    
    # Initialize and run advanced RL trading
    advanced_trader = AdvancedRLTrader(symbols=args.symbols, initial_balance=args.initial_balance)
    models, envs, portfolio_histories = advanced_trader.run_complete_analysis(
        algorithms=args.algorithms,
        total_timesteps=args.timesteps
    )
    
    print("\nAdvanced RL trading analysis completed successfully!")
    print(f"Results saved to: advanced_rl_trading.png")
    print(f"TensorBoard logs available in: ./ppo_tensorboard/ and ./sac_tensorboard/")

if __name__ == "__main__":
    main()