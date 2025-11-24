
"""
Day 58: LSTM for Time Series Prediction
Implementation of LSTM networks for financial time series forecasting
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import yfinance as yf
import ta
from datetime import datetime, timedelta
import argparse
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesDataset(Dataset):
    """Dataset for time series forecasting"""
    
    def __init__(self, sequences, targets):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
        
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

class AttentionLayer(nn.Module):
    """Attention mechanism for LSTM"""
    
    def __init__(self, hidden_size):
        super(AttentionLayer, self).__init__()
        self.hidden_size = hidden_size
        self.attention = nn.Linear(hidden_size * 2, 1)
        
    def forward(self, lstm_output):
        # lstm_output shape: (batch_size, seq_len, hidden_size * num_directions)
        batch_size, seq_len, hidden_dim = lstm_output.size()
        
        # Compute attention scores
        attention_scores = torch.zeros(batch_size, seq_len)
        for t in range(seq_len):
            attention_scores[:, t] = self.attention(lstm_output[:, t]).squeeze(1)
        
        # Softmax to get attention weights
        attention_weights = torch.softmax(attention_scores, dim=1)
        
        # Apply attention weights
        context_vector = torch.bmm(attention_weights.unsqueeze(1), lstm_output).squeeze(1)
        
        return context_vector, attention_weights

class FinancialLSTM(nn.Module):
    """LSTM model for financial time series prediction"""
    
    def __init__(self, input_size, hidden_size, num_layers, output_size, 
                 bidirectional=False, use_attention=False, dropout=0.2):
        super(FinancialLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.use_attention = use_attention
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention layer
        if use_attention:
            self.attention = AttentionLayer(hidden_size * (2 if bidirectional else 1))
        
        # Output layer
        output_dim = hidden_size * (2 if bidirectional else 1)
        if use_attention:
            self.fc = nn.Linear(output_dim, output_size)
        else:
            # Use last hidden state
            self.fc = nn.Linear(output_dim, output_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        if self.use_attention:
            # Apply attention mechanism
            context_vector, attention_weights = self.attention(lstm_out)
            output = self.fc(context_vector)
        else:
            # Use last hidden state
            if self.bidirectional:
                # Concatenate last forward and backward hidden states
                hidden_forward = hidden[-2]
                hidden_backward = hidden[-1]
                hidden_concat = torch.cat((hidden_forward, hidden_backward), dim=1)
            else:
                hidden_concat = hidden[-1]
            
            output = self.fc(self.dropout(hidden_concat))
        
        return output

class LSTMForecaster:
    """Main class for LSTM-based financial forecasting"""
    
    def __init__(self, symbol='AAPL', sequence_length=30, forecast_days=1):
        self.symbol = symbol
        self.sequence_length = sequence_length
        self.forecast_days = forecast_days
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = StandardScaler()
        
    def fetch_data(self, period='5y'):
        """Fetch and prepare financial data with technical indicators"""
        print(f"Fetching data for {self.symbol}...")
        stock = yf.download(self.symbol, period=period)
        
        data = pd.DataFrame(index=stock.index)
        data['price'] = stock['Close']
        data['open'] = stock['Open']
        data['high'] = stock['High']
        data['low'] = stock['Low']
        data['volume'] = stock['Volume']
        
        # Price-based features
        data['returns'] = data['price'].pct_change()
        data['log_returns'] = np.log(data['price'] / data['price'].shift(1))
        data['volatility'] = data['returns'].rolling(window=20).std()
        
        # Technical indicators using ta library
        # Trend indicators
        data['sma_20'] = ta.trend.sma_indicator(data['price'], window=20)
        data['sma_50'] = ta.trend.sma_indicator(data['price'], window=50)
        data['ema_12'] = ta.trend.ema_indicator(data['price'], window=12)
        data['macd'] = ta.trend.macd(data['price'])
        data['adx'] = ta.trend.adx(data['high'], data['low'], data['price'])
        
        # Momentum indicators
        data['rsi'] = ta.momentum.rsi(data['price'])
        data['stoch'] = ta.momentum.stoch(data['high'], data['low'], data['price'])
        data['williams_r'] = ta.momentum.williams_r(data['high'], data['low'], data['price'])
        
        # Volume indicators
        data['obv'] = ta.volume.on_balance_volume(data['price'], data['volume'])
        data['cmf'] = ta.volume.chaikin_money_flow(data['high'], data['low'], data['price'], data['volume'])
        
        # Volatility indicators
        data['bb_upper'] = ta.volatility.bollinger_hband(data['price'])
        data['bb_lower'] = ta.volatility.bollinger_lband(data['price'])
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['price']
        
        # Target: future price changes (multiple horizons)
        for days in [1, 3, 5, 10]:
            data[f'target_{days}d'] = (data['price'].shift(-days) / data['price'] - 1) * 100
        
        # Drop NaN values
        data = data.dropna()
        
        print(f"Data shape: {data.shape}")
        print(f"Features: {list(data.columns)}")
        
        return data
    
    def prepare_sequences(self, data, target_column='target_1d'):
        """Prepare sequences for LSTM training"""
        feature_columns = ['price', 'open', 'high', 'low', 'volume', 'returns', 
                          'log_returns', 'volatility', 'sma_20', 'sma_50', 'ema_12',
                          'macd', 'adx', 'rsi', 'stoch', 'williams_r', 'obv', 'cmf',
                          'bb_upper', 'bb_lower', 'bb_width']
        
        features = data[feature_columns].values
        targets = data[target_column].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        for i in range(len(features_scaled) - self.sequence_length):
            X.append(features_scaled[i:(i + self.sequence_length)])
            y.append(targets[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def train_model(self, hidden_size=64, num_layers=2, bidirectional=True,
                   use_attention=True, epochs=100, learning_rate=0.001, 
                   batch_size=32):
        """Train the LSTM model"""
        
        # Fetch and prepare data
        data = self.fetch_data()
        X, y = self.prepare_sequences(data, f'target_{self.forecast_days}d')
        
        # Split data (time series split)
        split_idx = int(0.7 * len(X))
        X_train, X_temp = X[:split_idx], X[split_idx:]
        y_train, y_temp = y[:split_idx], y[split_idx:]
        
        val_idx = int(0.5 * len(X_temp))
        X_val, X_test = X_temp[:val_idx], X_temp[val_idx:]
        y_val, y_test = y_temp[:val_idx], y_temp[val_idx:]
        
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Test samples: {len(X_test)}")
        
        # Create datasets and data loaders
        train_dataset = TimeSeriesDataset(X_train, y_train)
        val_dataset = TimeSeriesDataset(X_val, y_val)
        test_dataset = TimeSeriesDataset(X_test, y_test)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        input_size = X_train.shape[2]  # number of features
        self.model = FinancialLSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            output_size=1,
            bidirectional=bidirectional,
            use_attention=use_attention
        )
        self.model.to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        # Training loop
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        
        print("Starting LSTM training...")
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            for batch_sequences, batch_targets in train_loader:
                batch_sequences = batch_sequences.to(self.device)
                batch_targets = batch_targets.to(self.device).unsqueeze(1)
                
                optimizer.zero_grad()
                outputs = self.model(batch_sequences)
                loss = criterion(outputs, batch_targets)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_sequences, batch_targets in val_loader:
                    batch_sequences = batch_sequences.to(self.device)
                    batch_targets = batch_targets.to(self.device).unsqueeze(1)
                    
                    outputs = self.model(batch_sequences)
                    loss = criterion(outputs, batch_targets)
                    val_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            
            train_losses.append(avg_train_loss)
            val_losses.append(avg_val_loss)
            
            scheduler.step(avg_val_loss)
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                torch.save({
                    'model_state_dict': self.model.state_dict(),
                    'scaler': self.scaler,
                    'config': {
                        'input_size': input_size,
                        'hidden_size': hidden_size,
                        'num_layers': num_layers,
                        'bidirectional': bidirectional,
                        'use_attention': use_attention
                    }
                }, 'best_lstm_model.pth')
            
            if (epoch + 1) % 20 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')
        
        # Load best model
        checkpoint = torch.load('best_lstm_model.pth')
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Evaluate on test set
        test_metrics = self.evaluate_model(test_loader)
        print(f"Test MSE: {test_metrics['mse']:.4f}")
        print(f"Test MAE: {test_metrics['mae']:.4f}")
        
        # Plot results
        self.plot_predictions(test_loader, data, split_idx + val_idx)
        self.plot_training_history(train_losses, val_losses)
        
        return train_losses, val_losses, test_metrics
    
    def evaluate_model(self, test_loader):
        """Evaluate model performance"""
        self.model.eval()
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch_sequences, batch_targets in test_loader:
                batch_sequences = batch_sequences.to(self.device)
                outputs = self.model(batch_sequences)
                
                predictions.extend(outputs.cpu().numpy())
                actuals.extend(batch_targets.numpy())
        
        predictions = np.array(predictions).flatten()
        actuals = np.array(actuals).flatten()
        
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        
        return {'mse': mse, 'mae': mae, 'predictions': predictions, 'actuals': actuals}
    
    def plot_predictions(self, test_loader, data, test_start_idx):
        """Plot predictions vs actual values"""
        results = self.evaluate_model(test_loader)
        predictions = results['predictions']
        actuals = results['actuals']
        
        # Get test dates
        test_dates = data.index[test_start_idx:test_start_idx + len(predictions)]
        
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Predictions vs Actuals
        plt.subplot(2, 1, 1)
        plt.plot(test_dates, actuals, label='Actual Returns', alpha=0.7)
        plt.plot(test_dates, predictions, label='Predicted Returns', alpha=0.7)
        plt.title(f'LSTM Predictions vs Actual Returns ({self.symbol})')
        plt.ylabel('Returns (%)')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Scatter plot
        plt.subplot(2, 1, 2)
        plt.scatter(actuals, predictions, alpha=0.5)
        plt.plot([actuals.min(), actuals.max()], [actuals.min(), actuals.max()], 'r--')
        plt.xlabel('Actual Returns')
        plt.ylabel('Predicted Returns')
        plt.title('Prediction vs Actual Scatter Plot')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('lstm_predictions.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_training_history(self, train_losses, val_losses):
        """Plot training history"""
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Training Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('MSE Loss')
        plt.title('LSTM Training History')
        plt.legend()
        plt.grid(True)
        plt.savefig('lstm_training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def forecast_future(self, data, days=10):
        """Generate future forecasts"""
        self.model.eval()
        
        # Get the most recent sequence
        feature_columns = ['price', 'open', 'high', 'low', 'volume', 'returns', 
                          'log_returns', 'volatility', 'sma_20', 'sma_50', 'ema_12',
                          'macd', 'adx', 'rsi', 'stoch', 'williams_r', 'obv', 'cmf',
                          'bb_upper', 'bb_lower', 'bb_width']
        
        recent_data = data[feature_columns].tail(self.sequence_length)
        recent_scaled = self.scaler.transform(recent_data)
        
        forecasts = []
        current_sequence = recent_scaled.copy()
        
        with torch.no_grad():
            for _ in range(days):
                sequence_tensor = torch.FloatTensor(current_sequence).unsqueeze(0).to(self.device)
                prediction = self.model(sequence_tensor)
                forecasts.append(prediction.cpu().numpy()[0][0])
                
                # Update sequence for next prediction (simplified approach)
                # In practice, you'd want to properly update all features
                current_sequence = np.roll(current_sequence, -1, axis=0)
                # This is a simplified update - real implementation would be more complex
        
        return forecasts

def main():
    parser = argparse.ArgumentParser(description='LSTM Financial Forecaster')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Stock symbol')
    parser.add_argument('--sequence_length', type=int, default=30, help='Sequence length for LSTM')
    parser.add_argument('--forecast_days', type=int, default=1, help='Days ahead to forecast')
    parser.add_argument('--lstm_layers', type=int, default=2, help='Number of LSTM layers')
    parser.add_argument('--units', type=int, default=64, help='Number of LSTM units')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--bidirectional', action='store_true', help='Use bidirectional LSTM')
    parser.add_argument('--attention', action='store_true', help='Use attention mechanism')
    
    args = parser.parse_args()
    
    # Initialize and train LSTM
    lstm_forecaster = LSTMForecaster(
        symbol=args.symbol,
        sequence_length=args.sequence_length,
        forecast_days=args.forecast_days
    )
    
    print("=" * 60)
    print("LSTM Financial Time Series Forecasting")
    print("=" * 60)
    print(f"Symbol: {args.symbol}")
    print(f"Sequence Length: {args.sequence_length}")
    print(f"Forecast Horizon: {args.forecast_days} days")
    print(f"LSTM Layers: {args.lstm_layers}")
    print(f"Hidden Units: {args.units}")
    print(f"Bidirectional: {args.bidirectional}")
    print(f"Attention: {args.attention}")
    print("=" * 60)
    
    train_losses, val_losses, test_metrics = lstm_forecaster.train_model(
        hidden_size=args.units,
        num_layers=args.lstm_layers,
        bidirectional=args.bidirectional,
        use_attention=args.attention,
        epochs=args.epochs
    )
    
    print("\nLSTM Training Completed!")
    print(f"Final Test MSE: {test_metrics['mse']:.4f}")
    print(f"Final Test MAE: {test_metrics['mae']:.4f}")

if __name__ == "__main__":
    main()