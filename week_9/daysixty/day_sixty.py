
"""
Day 60: Reinforcement Learning Basics for Trading
Implementation of Q-learning and Deep Q-Networks for financial markets
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from collections import deque
import random
import warnings
warnings.filterwarnings('ignore')

# Reinforcement Learning
import gym
from gym import spaces
import torch
import torch.nn as nn
import torch.optim as optim
from stable_baselines3 import PPO, DQN, A2C
from stable_baselines3.common.env_checker import check_env

class TradingEnvironment(gym.Env):
    """Custom trading environment for reinforcement learning"""
    
    def __init__(self, df, initial_balance=10000, transaction_cost=0.001, 
                 lookback_window=50, max_position=0.1):
        super(TradingEnvironment, self).__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.lookback_window = lookback_window
        self.max_position = max_position  # Maximum position as fraction of portfolio
        
        # Define action space: 0=sell, 1=hold, 2=buy
        self.action_space = spaces.Discrete(3)
        
        # Define observation space: portfolio state + market features
        # [cash, shares, portfolio_value] + [price features * lookback_window]
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(3 + 5 * lookback_window,),  # cash, shares, value + features
            dtype=np.float32
        )
        
        self.reset()
    
    def _get_observation(self):
        """Get current observation"""
        if self.current_step < self.lookback_window:
            # Pad with zeros if not enough history
            market_features = np.zeros(5 * self.lookback_window)
        else:
            # Get recent market data
            recent_data = self.df.iloc[self.current_step - self.lookback_window:self.current_step]
            market_features = []
            
            for col in ['price', 'returns', 'volume', 'rsi', 'macd']:
                if col in recent_data.columns:
                    market_features.extend(recent_data[col].values)
                else:
                    market_features.extend(np.zeros(self.lookback_window))
            
            market_features = np.array(market_features)
        
        # Portfolio state
        portfolio_state = np.array([
            self.cash,
            self.shares,
            self.portfolio_value
        ])
        
        observation = np.concatenate([portfolio_state, market_features])
        return observation
    
    def _calculate_portfolio_value(self):
        """Calculate total portfolio value"""
        current_price = self.df.iloc[self.current_step]['price']
        return self.cash + self.shares * current_price
    
    def _calculate_reward(self):
        """Calculate reward based on portfolio performance"""
        # Simple reward: change in portfolio value
        reward = (self.portfolio_value - self.prev_portfolio_value) / self.initial_balance
        
        # Penalize excessive trading
        if self.action != 1:  # if not hold
            reward -= self.transaction_cost
            
        return reward
    
    def reset(self):
        """Reset environment to initial state"""
        self.current_step = self.lookback_window
        self.cash = self.initial_balance
        self.shares = 0
        self.portfolio_value = self.initial_balance
        self.prev_portfolio_value = self.initial_balance
        self.action = 1  # hold
        self.done = False
        
        return self._get_observation()
    
    def step(self, action):
        """Execute one step in the environment"""
        self.action = action
        current_price = self.df.iloc[self.current_step]['price']
        self.prev_portfolio_value = self.portfolio_value
        
        # Execute action
        if action == 0:  # sell
            if self.shares > 0:
                # Sell all shares
                self.cash += self.shares * current_price * (1 - self.transaction_cost)
                self.shares = 0
                
        elif action == 2:  # buy
            if self.cash > 0:
                # Calculate maximum shares we can buy within position limit
                max_shares_value = self.portfolio_value * self.max_position
                max_shares = int(max_shares_value / current_price)
                
                if max_shares > 0:
                    shares_to_buy = min(max_shares, int(self.cash / current_price))
                    cost = shares_to_buy * current_price * (1 + self.transaction_cost)
                    
                    if cost <= self.cash:
                        self.shares += shares_to_buy
                        self.cash -= cost
        
        # Update portfolio value
        self.portfolio_value = self._calculate_portfolio_value()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Move to next step
        self.current_step += 1
        
        # Check if episode is done
        if self.current_step >= len(self.df) - 1:
            self.done = True
        
        # Get new observation
        observation = self._get_observation()
        
        info = {
            'portfolio_value': self.portfolio_value,
            'cash': self.cash,
            'shares': self.shares,
            'price': current_price
        }
        
        return observation, reward, self.done, info
    
    def render(self, mode='human'):
        """Render environment state"""
        current_price = self.df.iloc[self.current_step]['price']
        print(f"Step: {self.current_step}, Price: {current_price:.2f}, "
              f"Cash: {self.cash:.2f}, Shares: {self.shares}, "
              f"Portfolio Value: {self.portfolio_value:.2f}")

class DQNAgent:
    """Deep Q-Network Agent for trading"""
    
    def __init__(self, state_size, action_size, learning_rate=0.001, 
                 gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=2000)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Main network
        self.model = self._build_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
    
    def _build_model(self):
        """Build neural network for Q-value approximation"""
        model = nn.Sequential(
            nn.Linear(self.state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, self.action_size)
        )
        return model.to(self.device)
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_values = self.model(state)
        return np.argmax(q_values.cpu().data.numpy())
    
    def replay(self, batch_size=32):
        """Train network on random batch from memory"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # Current Q values
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values
        next_q = self.model(next_states).max(1)[0].detach()
        target_q = rewards + (self.gamma * next_q * ~dones)
        
        # Compute loss
        loss = self.criterion(current_q.squeeze(), target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        """Load model weights"""
        self.model.load_state_dict(torch.load(name))
    
    def save(self, name):
        """Save model weights"""
        torch.save(self.model.state_dict(), name)

class TabularQLearningAgent:
    """Tabular Q-learning agent for discrete state spaces"""
    
    def __init__(self, state_bins, action_size, learning_rate=0.1, 
                 gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_bins = state_bins
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Initialize Q-table
        self.q_table = np.zeros(state_bins + [action_size])
    
    def _discretize_state(self, state):
        """Convert continuous state to discrete bins"""
        # Simple discretization for demonstration
        # In practice, use more sophisticated methods
        discrete_state = []
        for i, value in enumerate(state[:10]):  # Use first 10 features for simplicity
            if value < -0.1:
                discrete_state.append(0)
            elif value < 0:
                discrete_state.append(1)
            elif value < 0.1:
                discrete_state.append(2)
            else:
                discrete_state.append(3)
        
        return tuple(discrete_state[:len(self.state_bins)])
    
    def act(self, state):
        """Choose action using epsilon-greedy policy"""
        discrete_state = self._discretize_state(state)
        
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        return np.argmax(self.q_table[discrete_state])
    
    def learn(self, state, action, reward, next_state, done):
        """Update Q-table using Q-learning"""
        discrete_state = self._discretize_state(state)
        next_discrete_state = self._discretize_state(next_state)
        
        current_q = self.q_table[discrete_state][action]
        
        if done:
            target_q = reward
        else:
            target_q = reward + self.gamma * np.max(self.q_table[next_discrete_state])
        
        # Update Q-value
        self.q_table[discrete_state][action] += self.learning_rate * (target_q - current_q)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class RLTrader:
    """Main class for reinforcement learning trading"""
    
    def __init__(self, symbol='AAPL', initial_balance=10000):
        self.symbol = symbol
        self.initial_balance = initial_balance
        
    def prepare_data(self, period='2y'):
        """Prepare market data for RL environment"""
        print(f"Fetching data for {self.symbol}...")
        stock_data = yf.download(self.symbol, period=period)
        
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
        
        # Drop NaN values
        data = data.dropna()
        
        # Normalize features
        for column in data.columns:
            if column != 'price':
                data[column] = (data[column] - data[column].mean()) / data[column].std()
        
        return data
    
    def train_dqn_agent(self, data, episodes=1000):
        """Train DQN agent"""
        env = TradingEnvironment(data, initial_balance=self.initial_balance)
        state_size = env.observation_space.shape[0]
        action_size = env.action_space.n
        
        agent = DQNAgent(state_size, action_size)
        
        portfolio_values = []
        episode_rewards = []
        
        print("Training DQN Agent...")
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            for step in range(len(data) - env.lookback_window - 1):
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)
                
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            # Train agent
            agent.replay()
            
            portfolio_values.append(info['portfolio_value'])
            episode_rewards.append(total_reward)
            
            if (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{episodes}, "
                      f"Portfolio Value: {info['portfolio_value']:.2f}, "
                      f"Total Reward: {total_reward:.4f}, "
                      f"Epsilon: {agent.epsilon:.4f}")
        
        return agent, env, portfolio_values, episode_rewards
    
    def train_tabular_agent(self, data, episodes=1000):
        """Train tabular Q-learning agent"""
        env = TradingEnvironment(data, initial_balance=self.initial_balance)
        
        # Define state bins for discretization
        state_bins = [4] * 5  # 5 features, 4 bins each
        action_size = env.action_space.n
        
        agent = TabularQLearningAgent(state_bins, action_size)
        
        portfolio_values = []
        episode_rewards = []
        
        print("Training Tabular Q-Learning Agent...")
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            for step in range(len(data) - env.lookback_window - 1):
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)
                
                agent.learn(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            portfolio_values.append(info['portfolio_value'])
            episode_rewards.append(total_reward)
            
            if (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{episodes}, "
                      f"Portfolio Value: {info['portfolio_value']:.2f}, "
                      f"Total Reward: {total_reward:.4f}, "
                      f"Epsilon: {agent.epsilon:.4f}")
        
        return agent, env, portfolio_values, episode_rewards
    
    def evaluate_agent(self, agent, env, agent_type='dqn'):
        """Evaluate trained agent"""
        state = env.reset()
        portfolio_history = []
        action_history = []
        
        done = False
        while not done:
            if agent_type == 'dqn':
                action = agent.act(state)
            else:  # tabular
                action = agent.act(state)
                
            state, reward, done, info = env.step(action)
            
            portfolio_history.append(info['portfolio_value'])
            action_history.append(action)
        
        return portfolio_history, action_history, info
    
    def plot_results(self, portfolio_values, episode_rewards, portfolio_history, data):
        """Plot training and evaluation results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Portfolio value during training
        axes[0, 0].plot(portfolio_values)
        axes[0, 0].set_title('Portfolio Value During Training')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].grid(True)
        
        # Plot 2: Episode rewards
        axes[0, 1].plot(episode_rewards)
        axes[0, 1].set_title('Episode Rewards')
        axes[0, 1].set_ylabel('Total Reward')
        axes[0, 1].grid(True)
        
        # Plot 3: Final portfolio value vs buy-and-hold
        price_data = data['price'].iloc[len(data) - len(portfolio_history):].values
        initial_price = price_data[0]
        buy_hold_values = [self.initial_balance * (p / initial_price) for p in price_data]
        
        axes[1, 0].plot(portfolio_history, label='RL Agent')
        axes[1, 0].plot(buy_hold_values, label='Buy & Hold')
        axes[1, 0].set_title('RL Agent vs Buy & Hold')
        axes[1, 0].set_ylabel('Portfolio Value ($)')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot 4: Action distribution
        action_names = ['Sell', 'Hold', 'Buy']
        action_counts = [portfolio_history.count(i) for i in range(3)]
        axes[1, 1].bar(action_names, action_counts)
        axes[1, 1].set_title('Action Distribution')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('rl_trading_results.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_complete_analysis(self, agent_type='dqn', episodes=1000):
        """Run complete RL trading analysis"""
        print("Starting Reinforcement Learning Trading Analysis...")
        print("=" * 60)
        
        # Prepare data
        data = self.prepare_data()
        
        # Train agent
        if agent_type == 'dqn':
            agent, env, portfolio_values, episode_rewards = self.train_dqn_agent(data, episodes)
        else:
            agent, env, portfolio_values, episode_rewards = self.train_tabular_agent(data, episodes)
        
        # Evaluate agent
        print("\nEvaluating trained agent...")
        portfolio_history, action_history, final_info = self.evaluate_agent(agent, env, agent_type)
        
        # Calculate performance metrics
        initial_value = self.initial_balance
        final_value = final_info['portfolio_value']
        total_return = (final_value - initial_value) / initial_value * 100
        
        # Buy and hold comparison
        price_data = data['price']
        buy_hold_return = (price_data.iloc[-1] - price_data.iloc[env.lookback_window]) / price_data.iloc[env.lookback_window] * 100
        
        print("\n" + "=" * 60)
        print("PERFORMANCE RESULTS")
        print("=" * 60)
        print(f"Agent Type: {agent_type.upper()}")
        print(f"Initial Portfolio Value: ${initial_value:.2f}")
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Buy & Hold Return: {buy_hold_return:.2f}%")
        print(f"Excess Return: {total_return - buy_hold_return:.2f}%")
        print(f"Final Cash: ${final_info['cash']:.2f}")
        print(f"Final Shares: {final_info['shares']}")
        
        # Plot results
        print("\nGenerating visualizations...")
        self.plot_results(portfolio_values, episode_rewards, portfolio_history, data)
        
        return agent, env, portfolio_values, episode_rewards

def main():
    """Main function to run RL trading"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reinforcement Learning Trading')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Stock symbol')
    parser.add_argument('--agent', type=str, default='dqn', choices=['dqn', 'tabular'], 
                       help='RL agent type')
    parser.add_argument('--episodes', type=int, default=1000, help='Training episodes')
    parser.add_argument('--initial_balance', type=float, default=10000, help='Initial portfolio value')
    
    args = parser.parse_args()
    
    # Initialize and run RL trading
    rl_trader = RLTrader(symbol=args.symbol, initial_balance=args.initial_balance)
    agent, env, portfolio_values, episode_rewards = rl_trader.run_complete_analysis(
        agent_type=args.agent,
        episodes=args.episodes
    )
    
    print("\nRL Trading analysis completed successfully!")
    print(f"Results saved to: rl_trading_results.png")

if __name__ == "__main__":
    main()