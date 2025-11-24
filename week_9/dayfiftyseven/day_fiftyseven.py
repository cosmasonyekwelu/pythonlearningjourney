"""
Day 57: Neural Networks Fundamentals for Financial Prediction
Implementation of multi-layer perceptron for next-day return prediction
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score
import yfinance as yf
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FinancialDataset(Dataset):
    """Dataset for financial time series prediction"""
    
    def __init__(self, features, targets, sequence_length=1):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
        self.sequence_length = sequence_length
        
    def __len__(self):
        return len(self.features) - self.sequence_length
    
    def __getitem__(self, idx):
        end_idx = idx + self.sequence_length
        return self.features[idx:end_idx].flatten(), self.targets[end_idx-1]

class FinancialMLP(nn.Module):
    """Multi-Layer Perceptron for financial prediction"""
    
    def __init__(self, input_size, hidden_layers, hidden_units, output_size=1, 
                 activation='relu', dropout_rate=0.2):
        super(FinancialMLP, self).__init__()
        
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(input_size, hidden_units))
        
        # Hidden layers
        for _ in range(hidden_layers - 1):
            self.layers.append(nn.Linear(hidden_units, hidden_units))
            
        # Output layer
        self.output_layer = nn.Linear(hidden_units, output_size)
        
        # Activation function
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'leaky_relu':
            self.activation = nn.LeakyReLU(0.1)
        elif activation == 'tanh':
            self.activation = nn.Tanh()
        elif activation == 'sigmoid':
            self.activation = nn.Sigmoid()
        else:
            self.activation = nn.ReLU()
            
        # Regularization
        self.dropout = nn.Dropout(dropout_rate)
        self.batch_norm = nn.BatchNorm1d(hidden_units)
        
    def forward(self, x):
        for layer in self.layers:
            x = self.activation(layer(x))
            x = self.batch_norm(x)
            x = self.dropout(x)
            
        x = self.output_layer(x)
        return x

class FinancialNeuralNetwork:
    """Main class for financial neural network implementation"""
    
    def __init__(self, symbol='AAPL', lookback_days=60):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = StandardScaler()
        
    def fetch_data(self, period='2y'):
        """Fetch and prepare financial data"""
        print(f"Fetching data for {self.symbol}...")
        stock = yf.download(self.symbol, period=period)
        
        # Calculate features
        data = pd.DataFrame()
        data['price'] = stock['Close']
        data['returns'] = data['price'].pct_change()
        data['volatility'] = data['returns'].rolling(window=20).std()
        data['volume'] = stock['Volume']
        data['high_low_ratio'] = stock['High'] / stock['Low']
        
        # Technical indicators
        data['sma_20'] = data['price'].rolling(window=20).mean()
        data['sma_50'] = data['price'].rolling(window=50).mean()
        data['rsi'] = self.calculate_rsi(data['price'])
        data['macd'] = self.calculate_macd(data['price'])
        
        # Target: next day return (classification: up/down)
        data['target'] = (data['returns'].shift(-1) > 0).astype(int)
        
        # Drop NaN values
        data = data.dropna()
        
        return data
    
    def calculate_rsi(self, prices, window=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        return macd
    
    def prepare_features(self, data):
        """Prepare features for neural network"""
        feature_columns = ['returns', 'volatility', 'volume', 'high_low_ratio', 
                          'sma_20', 'sma_50', 'rsi', 'macd']
        
        features = data[feature_columns].values
        targets = data['target'].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled, targets
    
    def create_sequences(self, features, targets, sequence_length=10):
        """Create sequences for time series prediction"""
        X, y = [], []
        for i in range(len(features) - sequence_length):
            X.append(features[i:(i + sequence_length)])
            y.append(targets[i + sequence_length - 1])
        return np.array(X), np.array(y)
    
    def train_model(self, hidden_layers=3, hidden_units=128, epochs=100, 
                   learning_rate=0.001, batch_size=32):
        """Train the neural network model"""
        
        # Fetch and prepare data
        data = self.fetch_data()
        features, targets = self.prepare_features(data)
        
        # Create sequences
        sequence_length = self.lookback_days
        X, y = self.create_sequences(features, targets, sequence_length)
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        val_idx = int(0.8 * len(X_train))
        X_train, X_val = X_train[:val_idx], X_train[val_idx:]
        y_train, y_val = y_train[:val_idx], y_train[val_idx:]
        
        # Create datasets
        train_dataset = FinancialDataset(X_train, y_train)
        val_dataset = FinancialDataset(X_val, y_val)
        test_dataset = FinancialDataset(X_test, y_test)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        input_size = X_train.shape[1] * X_train.shape[2]  # flattened sequence
        self.model = FinancialMLP(input_size, hidden_layers, hidden_units, output_size=1)
        self.model.to(self.device)
        
        # Loss and optimizer
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        # Training loop
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        
        print("Starting training...")
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            for batch_features, batch_targets in train_loader:
                batch_features = batch_features.to(self.device)
                batch_targets = batch_targets.to(self.device).unsqueeze(1)
                
                optimizer.zero_grad()
                outputs = self.model(batch_features)
                loss = criterion(outputs, batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_features, batch_targets in val_loader:
                    batch_features = batch_features.to(self.device)
                    batch_targets = batch_targets.to(self.device).unsqueeze(1)
                    
                    outputs = self.model(batch_features)
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
                torch.save(self.model.state_dict(), 'best_model.pth')
            
            if (epoch + 1) % 20 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')
        
        # Load best model
        self.model.load_state_dict(torch.load('best_model.pth'))
        
        # Evaluate on test set
        test_accuracy = self.evaluate_model(test_loader)
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Plot training history
        self.plot_training_history(train_losses, val_losses)
        
        return train_losses, val_losses
    
    def evaluate_model(self, test_loader):
        """Evaluate model performance"""
        self.model.eval()
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch_features, batch_targets in test_loader:
                batch_features = batch_features.to(self.device)
                outputs = self.model(batch_features)
                preds = torch.sigmoid(outputs) > 0.5
                
                predictions.extend(preds.cpu().numpy())
                actuals.extend(batch_targets.numpy())
        
        accuracy = accuracy_score(actuals, predictions)
        return accuracy
    
    def plot_training_history(self, train_losses, val_losses):
        """Plot training history"""
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Training Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.grid(True)
        plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def predict(self, new_data):
        """Make predictions on new data"""
        self.model.eval()
        with torch.no_grad():
            features_scaled = self.scaler.transform(new_data)
            features_tensor = torch.FloatTensor(features_scaled).to(self.device)
            prediction = torch.sigmoid(self.model(features_tensor))
            return prediction.cpu().numpy()

def main():
    parser = argparse.ArgumentParser(description='Financial Neural Network')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Stock symbol')
    parser.add_argument('--hidden_layers', type=int, default=3, help='Number of hidden layers')
    parser.add_argument('--hidden_units', type=int, default=128, help='Number of units per hidden layer')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    
    args = parser.parse_args()
    
    # Initialize and train model
    nn_trader = FinancialNeuralNetwork(symbol=args.symbol)
    
    print("=" * 50)
    print("Financial Neural Network Training")
    print("=" * 50)
    print(f"Symbol: {args.symbol}")
    print(f"Architecture: {args.hidden_layers} hidden layers, {args.hidden_units} units each")
    print(f"Training: {args.epochs} epochs, LR: {args.learning_rate}")
    print("=" * 50)
    
    train_losses, val_losses = nn_trader.train_model(
        hidden_layers=args.hidden_layers,
        hidden_units=args.hidden_units,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size
    )
    
    print("\nTraining completed!")
    print(f"Final Training Loss: {train_losses[-1]:.4f}")
    print(f"Final Validation Loss: {val_losses[-1]:.4f}")

if __name__ == "__main__":
    main()