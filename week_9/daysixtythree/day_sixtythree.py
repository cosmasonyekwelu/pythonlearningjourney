
"""
Day 63: Weekly Project - AI Trading Agent
Integrated AI trading system combining deep learning, NLP, and reinforcement learning
"""

from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
import gym
from transformers import pipeline
from sklearn.preprocessing import StandardScaler
import torch.nn as nn
import torch
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# Import components from previous days

# Add previous days' directories to path
sys.path.extend(['../dayfiftyseven', '../dayfiftyeight', '../dayfiftynine',
                 '../daysixty', '../daysixtyone', '../daysixtytwo'])

# Core ML and DL

# Reinforcement Learning


class DataPipeline:
    """Unified data pipeline for AI trading agent"""

    def __init__(self, symbols, data_sources=['market', 'news', 'sentiment']):
        self.symbols = symbols
        self.data_sources = data_sources
        self.scaler = StandardScaler()

    def fetch_market_data(self, period='2y', interval='1d'):
        """Fetch and process market data for all symbols"""
        print("Fetching market data...")
        market_data = {}

        for symbol in self.symbols:
            stock_data = yf.download(symbol, period=period, interval=interval)

            # Calculate comprehensive features
            data = pd.DataFrame()
            data['price'] = stock_data['Close']
            data['open'] = stock_data['Open']
            data['high'] = stock_data['High']
            data['low'] = stock_data['Low']
            data['volume'] = stock_data['Volume']

            # Price-based features
            data['returns'] = data['price'].pct_change()
            data['log_returns'] = np.log(
                data['price'] / data['price'].shift(1))
            data['volatility'] = data['returns'].rolling(window=20).std()
            data['volume_ratio'] = data['volume'] / \
                data['volume'].rolling(window=20).mean()

            # Technical indicators
            data['sma_20'] = data['price'].rolling(window=20).mean()
            data['sma_50'] = data['price'].rolling(window=50).mean()
            data['ema_12'] = data['price'].ewm(span=12).mean()
            data['ema_26'] = data['price'].ewm(span=26).mean()
            data['macd'] = data['ema_12'] - data['ema_26']

            # RSI
            delta = data['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            data['bb_upper'] = data['sma_20'] + 2 * \
                data['price'].rolling(window=20).std()
            data['bb_lower'] = data['sma_20'] - 2 * \
                data['price'].rolling(window=20).std()
            data['bb_width'] = (data['bb_upper'] -
                                data['bb_lower']) / data['sma_20']

            # Drop NaN values
            data = data.dropna()

            market_data[symbol] = data

        return market_data

    def generate_sentiment_data(self, market_data):
        """Generate simulated sentiment data (in practice, use real APIs)"""
        print("Generating sentiment data...")
        sentiment_data = {}

        for symbol in self.symbols:
            data = market_data[symbol].copy()

            # Simulate sentiment scores based on price movements
            data['price_momentum'] = data['price'] / \
                data['price'].rolling(window=5).mean() - 1
            data['volume_surge'] = data['volume'] / \
                data['volume'].rolling(window=20).mean() - 1

            # Simulate sentiment scores (-1 to 1)
            np.random.seed(42)  # For reproducibility
            base_sentiment = data['price_momentum'] * \
                0.7 + data['volume_surge'] * 0.3
            noise = np.random.normal(0, 0.1, len(data))
            data['sentiment_score'] = np.clip(base_sentiment + noise, -1, 1)
            data['sentiment_confidence'] = np.abs(data['sentiment_score'])

            sentiment_data[symbol] = data[[
                'sentiment_score', 'sentiment_confidence']]

        return sentiment_data

    def prepare_training_data(self, market_data, sentiment_data, target_symbol, lookback_days=30):
        """Prepare integrated training data"""
        print(f"Preparing training data for {target_symbol}...")

        target_data = market_data[target_symbol].copy()

        # Add sentiment data
        if target_symbol in sentiment_data:
            sentiment_df = sentiment_data[target_symbol]
            target_data = target_data.join(sentiment_df)

        # Add features from other symbols (market correlation)
        for symbol in self.symbols:
            if symbol != target_symbol:
                other_data = market_data[symbol]
                target_data[f'{symbol}_returns'] = other_data['returns']
                target_data[f'{symbol}_volume_ratio'] = other_data['volume_ratio']

        # Create sequences for time series prediction
        feature_columns = [col for col in target_data.columns if col not in [
            'price', 'open', 'high', 'low']]
        features = target_data[feature_columns].values
        # Predict next day return
        targets = target_data['returns'].shift(-1).values

        # Remove rows with NaN
        valid_indices = ~np.isnan(targets)
        features = features[valid_indices]
        targets = targets[valid_indices]

        # Create sequences
        X, y = [], []
        for i in range(len(features) - lookback_days):
            X.append(features[i:i + lookback_days])
            y.append(targets[i + lookback_days])

        X = np.array(X)
        y = np.array(y)

        # Scale features
        X_reshaped = X.reshape(-1, X.shape[-1])
        X_scaled = self.scaler.fit_transform(X_reshaped)
        X_scaled = X_scaled.reshape(X.shape)

        return X_scaled, y, target_data, feature_columns


class DeepLearningPredictor:
    """Deep learning component for price prediction"""

    def __init__(self, input_shape, num_layers=3, hidden_units=128, dropout_rate=0.2):
        self.input_shape = input_shape
        self.model = self._build_model(
            input_shape, num_layers, hidden_units, dropout_rate)
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def _build_model(self, input_shape, num_layers, hidden_units, dropout_rate):
        """Build LSTM-based prediction model"""
        class FinancialLSTM(nn.Module):
            def __init__(self, input_shape, num_layers, hidden_units, dropout_rate):
                super(FinancialLSTM, self).__init__()
                self.lstm = nn.LSTM(
                    input_size=input_shape[-1],
                    hidden_size=hidden_units,
                    num_layers=num_layers,
                    batch_first=True,
                    dropout=dropout_rate,
                    bidirectional=True
                )
                self.attention = nn.Sequential(
                    nn.Linear(hidden_units * 2, 64),
                    nn.Tanh(),
                    nn.Linear(64, 1)
                )
                self.fc = nn.Sequential(
                    nn.Linear(hidden_units * 2, 64),
                    nn.ReLU(),
                    nn.Dropout(dropout_rate),
                    nn.Linear(64, 32),
                    nn.ReLU(),
                    nn.Dropout(dropout_rate),
                    nn.Linear(32, 1)
                )

            def forward(self, x):
                lstm_out, (hidden, cell) = self.lstm(x)

                # Attention mechanism
                attention_weights = torch.softmax(
                    self.attention(lstm_out).squeeze(-1), dim=1)
                context_vector = torch.sum(
                    lstm_out * attention_weights.unsqueeze(-1), dim=1)

                output = self.fc(context_vector)
                return output, attention_weights

        return FinancialLSTM(input_shape, num_layers, hidden_units, dropout_rate)

    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32, learning_rate=0.001):
        """Train the deep learning model"""
        self.model.train()
        optimizer = torch.optim.Adam(
            self.model.parameters(), lr=learning_rate, weight_decay=1e-5)
        criterion = nn.MSELoss()

        train_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_train), torch.FloatTensor(y_train)
        )
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True)

        val_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_val), torch.FloatTensor(y_val)
        )
        val_loader = torch.utils.data.DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False)

        train_losses = []
        val_losses = []

        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(
                    self.device), batch_y.to(self.device)

                optimizer.zero_grad()
                predictions, _ = self.model(batch_X)
                loss = criterion(predictions.squeeze(), batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), max_norm=1.0)
                optimizer.step()

                train_loss += loss.item()

            # Validation
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(
                        self.device), batch_y.to(self.device)
                    predictions, _ = self.model(batch_X)
                    loss = criterion(predictions.squeeze(), batch_y)
                    val_loss += loss.item()

            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)

            train_losses.append(avg_train_loss)
            val_losses.append(avg_val_loss)

            if (epoch + 1) % 20 == 0:
                print(
                    f'Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.6f}, Val Loss: {avg_val_loss:.6f}')

        return train_losses, val_losses

    def predict(self, X):
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions, attention_weights = self.model(X_tensor)
            return predictions.cpu().numpy(), attention_weights.cpu().numpy()


class SentimentAnalyzer:
    """Sentiment analysis component (simplified version)"""

    def __init__(self):
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis",
                                               model="ProsusAI/finbert",
                                               tokenizer="ProsusAI/finbert")
        except:
            print("FinBERT not available, using fallback sentiment analysis")
            self.sentiment_pipeline = None

    def analyze_text(self, text):
        """Analyze sentiment of financial text"""
        if self.sentiment_pipeline is None or not text:
            return {'score': 0, 'confidence': 0.5}

        try:
            result = self.sentiment_pipeline(text[:512])[0]
            score = 1 if result['label'] == 'positive' else - \
                1 if result['label'] == 'negative' else 0
            return {'score': score, 'confidence': result['score']}
        except:
            return {'score': 0, 'confidence': 0.5}

    def aggregate_sentiment(self, texts):
        """Aggregate sentiment from multiple texts"""
        if not texts:
            return {'overall_sentiment': 0, 'confidence': 0}

        sentiments = [self.analyze_text(text) for text in texts]
        weighted_scores = [s['score'] * s['confidence'] for s in sentiments]
        overall_sentiment = np.mean(weighted_scores) if weighted_scores else 0
        confidence = np.mean([s['confidence']
                             for s in sentiments]) if sentiments else 0

        return {'overall_sentiment': overall_sentiment, 'confidence': confidence}


class AITradingAgent:
    """Main AI trading agent integrating all components"""

    def __init__(self, symbols, initial_balance=10000, config=None):
        self.symbols = symbols
        self.initial_balance = initial_balance
        self.config = config or {}

        # Initialize components
        self.data_pipeline = DataPipeline(symbols)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.predictors = {}
        self.portfolio = {symbol: 0 for symbol in symbols}
        self.cash = initial_balance
        self.portfolio_value = initial_balance
        self.trade_history = []

    def train_models(self, retrain=False):
        """Train all AI components"""
        print("Training AI models...")

        # Fetch and prepare data
        market_data = self.data_pipeline.fetch_market_data()
        sentiment_data = self.data_pipeline.generate_sentiment_data(
            market_data)

        # Train predictor for each symbol
        for symbol in self.symbols:
            print(f"Training predictor for {symbol}...")
            X, y, full_data, feature_columns = self.data_pipeline.prepare_training_data(
                market_data, sentiment_data, symbol
            )

            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            val_idx = int(0.8 * len(X_train))
            X_train, X_val = X_train[:val_idx], X_train[val_idx:]
            y_train, y_val = y_train[:val_idx], y_train[val_idx:]

            # Initialize and train predictor
            input_shape = X_train.shape[1:]
            predictor = DeepLearningPredictor(input_shape)
            train_losses, val_losses = predictor.train(
                X_train, y_train, X_val, y_val)

            self.predictors[symbol] = predictor

            # Evaluate model
            test_predictions, _ = predictor.predict(X_test)
            test_rmse = np.sqrt(
                np.mean((test_predictions.flatten() - y_test) ** 2))
            print(f"{symbol} Test RMSE: {test_rmse:.6f}")

        print("All models trained successfully!")

    def generate_signals(self, current_data):
        """Generate trading signals using integrated AI system"""
        signals = {}
        confidence_scores = {}

        for symbol in self.symbols:
            if symbol not in self.predictors:
                signals[symbol] = 0  # Hold
                confidence_scores[symbol] = 0
                continue

            # Prepare current features for prediction
            try:
                # This would use the actual current market data
                # For demonstration, we'll use a simplified approach
                # Last 30 days
                current_features = current_data[symbol].iloc[-30:].values
                current_features_scaled = self.data_pipeline.scaler.transform(
                    current_features)
                current_features_sequence = current_features_scaled.reshape(
                    1, 30, -1)

                # Get prediction
                prediction, attention_weights = self.predictors[symbol].predict(
                    current_features_sequence)
                predicted_return = prediction[0][0]

                # Generate signal based on prediction
                if predicted_return > 0.02:  # 2% threshold
                    signal = 1  # Buy
                    confidence = min(abs(predicted_return) * 10, 1.0)
                elif predicted_return < -0.02:
                    signal = -1  # Sell
                    confidence = min(abs(predicted_return) * 10, 1.0)
                else:
                    signal = 0  # Hold
                    confidence = 0.5

                signals[symbol] = signal
                confidence_scores[symbol] = confidence

            except Exception as e:
                print(f"Error generating signal for {symbol}: {e}")
                signals[symbol] = 0
                confidence_scores[symbol] = 0

        return signals, confidence_scores

    def execute_trades(self, signals, confidence_scores, current_prices,
                       max_position_size=0.2, transaction_cost=0.001):
        """Execute trades based on signals"""
        total_portfolio_value = self.portfolio_value
        trades = []

        for symbol in self.symbols:
            signal = signals[symbol]
            confidence = confidence_scores[symbol]
            current_price = current_prices[symbol]

            if signal == 0 or confidence < 0.3:
                continue  # Skip low-confidence signals

            # Calculate position size based on confidence and risk limits
            position_size = min(confidence * max_position_size,
                                0.2) * total_portfolio_value

            if signal == 1:  # Buy
                # Check if we have enough cash
                cost = position_size * (1 + transaction_cost)
                if self.cash >= cost:
                    shares_to_buy = position_size / current_price
                    self.portfolio[symbol] += shares_to_buy
                    self.cash -= cost
                    trades.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': current_price,
                        'value': position_size,
                        'confidence': confidence
                    })

            elif signal == -1:  # Sell
                # Check if we have enough shares
                current_position_value = self.portfolio[symbol] * current_price
                if current_position_value > 0:
                    shares_to_sell = min(
                        self.portfolio[symbol], position_size / current_price)
                    proceeds = shares_to_sell * \
                        current_price * (1 - transaction_cost)
                    self.portfolio[symbol] -= shares_to_sell
                    self.cash += proceeds
                    trades.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'shares': shares_to_sell,
                        'price': current_price,
                        'value': shares_to_sell * current_price,
                        'confidence': confidence
                    })

        # Update portfolio value
        self._update_portfolio_value(current_prices)

        return trades

    def _update_portfolio_value(self, current_prices):
        """Update total portfolio value"""
        stock_value = 0
        for symbol in self.symbols:
            stock_value += self.portfolio[symbol] * current_prices[symbol]

        self.portfolio_value = self.cash + stock_value

    def run_backtest(self, period='2020-2022'):
        """Run comprehensive backtest"""
        print(f"Running backtest for period: {period}")

        # Fetch historical data
        market_data = self.data_pipeline.fetch_market_data(period=period)
        sentiment_data = self.data_pipeline.generate_sentiment_data(
            market_data)

        # Initialize tracking
        portfolio_history = [self.portfolio_value]
        trade_history = []
        current_prices = {}

        # Get common dates across all symbols
        common_dates = None
        for symbol, data in market_data.items():
            if common_dates is None:
                common_dates = data.index
            else:
                common_dates = common_dates.intersection(data.index)

        # Run simulation
        for date in common_dates[30:]:  # Skip first 30 days for warm-up
            # Get current prices
            for symbol in self.symbols:
                current_prices[symbol] = market_data[symbol].loc[date]['price']

            # Update portfolio value
            self._update_portfolio_value(current_prices)
            portfolio_history.append(self.portfolio_value)

            # Generate and execute signals (every 5 days to reduce trading frequency)
            if len(portfolio_history) % 5 == 0:
                # Get current market state (simplified)
                current_data = {}
                for symbol in self.symbols:
                    current_data[symbol] = market_data[symbol].loc[:date].tail(
                        30)

                signals, confidence_scores = self.generate_signals(
                    current_data)
                trades = self.execute_trades(
                    signals, confidence_scores, current_prices)
                trade_history.extend(trades)

        # Calculate performance metrics
        returns = np.diff(portfolio_history) / portfolio_history[:-1]

        metrics = {
            'total_return': (portfolio_history[-1] - portfolio_history[0]) / portfolio_history[0],
            'annualized_return': (1 + (portfolio_history[-1] - portfolio_history[0]) / portfolio_history[0]) ** (252/len(returns)) - 1,
            'volatility': np.std(returns) * np.sqrt(252),
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'total_trades': len(trade_history),
            'win_rate': 0
        }

        # Calculate Sharpe ratio
        if metrics['volatility'] > 0:
            metrics['sharpe_ratio'] = (
                metrics['annualized_return'] - 0.02) / metrics['volatility']

        # Calculate max drawdown
        peak = np.maximum.accumulate(portfolio_history)
        drawdown = (peak - portfolio_history) / peak
        metrics['max_drawdown'] = np.max(drawdown)

        # Calculate win rate (simplified)
        if trade_history:
            profitable_trades = [t for t in trade_history if
                                 (t['action'] == 'BUY' and t['price'] < current_prices[t['symbol']]) or
                                 (t['action'] == 'SELL' and t['price'] > current_prices[t['symbol']])]
            metrics['win_rate'] = len(profitable_trades) / len(trade_history)

        return portfolio_history, trade_history, metrics

    def plot_results(self, portfolio_history, trade_history, metrics):
        """Plot backtest results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Portfolio value
        axes[0, 0].plot(portfolio_history)
        axes[0, 0].set_title('Portfolio Value Over Time')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].grid(True)

        # Plot 2: Drawdown
        peak = np.maximum.accumulate(portfolio_history)
        drawdown = (peak - portfolio_history) / peak
        axes[0, 1].plot(drawdown)
        axes[0, 1].set_title('Portfolio Drawdown')
        axes[0, 1].set_ylabel('Drawdown')
        axes[0, 1].grid(True)

        # Plot 3: Trade analysis
        if trade_history:
            trade_dates = [i for i in range(len(trade_history))]
            trade_values = [t['value'] for t in trade_history]
            trade_confidence = [t['confidence'] for t in trade_history]

            axes[1, 0].scatter(trade_dates, trade_values,
                               c=trade_confidence, cmap='viridis', alpha=0.6)
            axes[1, 0].set_title('Trade Analysis')
            axes[1, 0].set_xlabel('Trade Number')
            axes[1, 0].set_ylabel('Trade Value ($)')
            axes[1, 0].grid(True)

            # Add colorbar
            plt.colorbar(axes[1, 0].collections[0],
                         ax=axes[1, 0], label='Confidence')

        # Plot 4: Performance metrics
        metric_names = ['Total Return',
                        'Annual Return', 'Sharpe Ratio', 'Max DD']
        metric_values = [
            metrics['total_return'] * 100,
            metrics['annualized_return'] * 100,
            metrics['sharpe_ratio'],
            metrics['max_drawdown'] * 100
        ]

        bars = axes[1, 1].bar(metric_names, metric_values, color=[
                              'blue', 'green', 'orange', 'red'])
        axes[1, 1].set_title('Performance Metrics')
        axes[1, 1].set_ylabel('Value')

        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                            f'{value:.2f}', ha='center', va='bottom')

        axes[1, 1].grid(True, axis='y')

        plt.tight_layout()
        plt.savefig('ai_trading_agent_results.png',
                    dpi=300, bbox_inches='tight')
        plt.show()

    def generate_report(self, portfolio_history, trade_history, metrics):
        """Generate comprehensive performance report"""
        report = {
            'summary': {
                'initial_portfolio': self.initial_balance,
                'final_portfolio': portfolio_history[-1],
                'total_return_percent': metrics['total_return'] * 100,
                'annualized_return_percent': metrics['annualized_return'] * 100,
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown_percent': metrics['max_drawdown'] * 100,
                'total_trades': metrics['total_trades'],
                'win_rate_percent': metrics['win_rate'] * 100
            },
            'trading_activity': {
                'total_trades': len(trade_history),
                'buy_trades': len([t for t in trade_history if t['action'] == 'BUY']),
                'sell_trades': len([t for t in trade_history if t['action'] == 'SELL']),
                'average_trade_confidence': np.mean([t['confidence'] for t in trade_history]) if trade_history else 0
            },
            'risk_metrics': {
                'volatility_percent': metrics['volatility'] * 100,
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown_percent': metrics['max_drawdown'] * 100,
                'calmar_ratio': metrics['annualized_return'] / metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else 0
            }
        }

        # Save report to JSON
        with open('ai_trading_agent_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Main function to run the AI trading agent"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Trading Agent')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
                        help='List of stock symbols')
    parser.add_argument('--initial_balance', type=float,
                        default=10000, help='Initial portfolio value')
    parser.add_argument('--period', type=str,
                        default='2020-2022', help='Backtest period')
    parser.add_argument('--retrain', action='store_true',
                        help='Retrain models')

    args = parser.parse_args()

    print("=" * 70)
    print("AI TRADING AGENT - WEEK 9 PROJECT")
    print("=" * 70)
    print(f"Symbols: {args.symbols}")
    print(f"Initial Balance: ${args.initial_balance:,.2f}")
    print(f"Backtest Period: {args.period}")
    print("=" * 70)

    # Initialize AI trading agent
    agent = AITradingAgent(symbols=args.symbols,
                           initial_balance=args.initial_balance)

    # Train models
    agent.train_models(retrain=args.retrain)

    # Run backtest
    portfolio_history, trade_history, metrics = agent.run_backtest(
        period=args.period)

    # Generate report
    report = agent.generate_report(portfolio_history, trade_history, metrics)

    # Display results
    print("\n" + "=" * 70)
    print("BACKTEST RESULTS")
    print("=" * 70)
    print(f"Initial Portfolio: ${report['summary']['initial_portfolio']:,.2f}")
    print(f"Final Portfolio: ${report['summary']['final_portfolio']:,.2f}")
    print(f"Total Return: {report['summary']['total_return_percent']:.2f}%")
    print(
        f"Annualized Return: {report['summary']['annualized_return_percent']:.2f}%")
    print(f"Sharpe Ratio: {report['summary']['sharpe_ratio']:.3f}")
    print(f"Max Drawdown: {report['summary']['max_drawdown_percent']:.2f}%")
    print(f"Total Trades: {report['summary']['total_trades']}")
    print(f"Win Rate: {report['summary']['win_rate_percent']:.2f}%")
    print("=" * 70)

    # Plot results
    print("\nGenerating visualizations...")
    agent.plot_results(portfolio_history, trade_history, metrics)

    print("\nAI Trading Agent analysis completed successfully!")
    print("Files generated:")
    print("  - ai_trading_agent_results.png (Visualizations)")
    print("  - ai_trading_agent_report.json (Detailed report)")


if __name__ == "__main__":
    main()
