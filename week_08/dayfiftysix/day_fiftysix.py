"""
Day 56: Predictive Market Model - Complete End-to-End Trading System
Integrates EDA, Feature Engineering, ML Modeling, Validation, and Backtesting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')


class PredictiveMarketModel:
    """
    Complete predictive trading system integrating all weekly concepts.
    """

    def __init__(self, ticker='SPY', start_date='2018-01-01', end_date=None):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.data = None
        self.features = None
        self.models = {}
        self.predictions = None
        self.backtest_results = None

        print(f"Predictive Market Model Initialized for {ticker}")
        print(f"Period: {start_date} to {self.end_date}")

    def run_full_pipeline(self):
        """Execute complete end-to-end pipeline"""
        print("\n" + "=" * 70)
        print("STARTING END-TO-END PREDICTIVE TRADING PIPELINE")
        print("=" * 70)

        # Step 1: Data Collection & EDA
        print("\nSTEP 1: DATA COLLECTION AND EXPLORATORY ANALYSIS")
        self.data_collection_eda()

        # Step 2: Feature Engineering
        print("\nSTEP 2: FEATURE ENGINEERING")
        self.feature_engineering()

        # Step 3: Model Training & Validation
        print("\nSTEP 3: MODEL TRAINING AND VALIDATION")
        self.model_training()

        # Step 4: Strategy Implementation & Backtesting
        print("\nSTEP 4: STRATEGY IMPLEMENTATION AND BACKTESTING")
        self.strategy_backtesting()

        # Step 5: Reporting
        print("\nSTEP 5: REPORT GENERATION")
        self.generate_reports()

        print("\n" + "=" * 70)
        print("PREDICTIVE MARKET MODEL PIPELINE COMPLETE")
        print("=" * 70)

        return self

    def data_collection_eda(self):
        """Step 1: Data collection and exploratory data analysis"""
        print("Loading market data...")

        # Load data
        self.data = yf.download(
            self.ticker, start=self.start_date, end=self.end_date)

        # Compute returns and target
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data['Target'] = (self.data['Returns'].shift(-1) > 0).astype(int)

        # Remove missing rows
        self.data = self.data.dropna()

        # Perform EDA
        self._perform_eda()

        print(f"Loaded {len(self.data)} trading days.")
        return self.data

    def _perform_eda(self):
        """Perform exploratory data analysis"""
        print("Performing Exploratory Data Analysis...")

        # Basic summary
        print(f"\nDataset Shape: {self.data.shape}")
        print(
            f"Date Range: {self.data.index.min()} to {self.data.index.max()}")
        print(f"Missing Values: {self.data.isnull().sum().sum()}")

        # Return statistics
        returns = self.data['Returns']
        print("\nReturn Statistics:")
        print(f"  Mean: {returns.mean():.6f}")
        print(f"  Std: {returns.std():.6f}")
        print(f"  Skewness: {returns.skew():.4f}")
        print(f"  Kurtosis: {returns.kurtosis():.4f}")
        print(
            f"  Target Distribution: {self.data['Target'].value_counts().to_dict()}")

        # Visual EDA
        self._plot_eda()

    def _plot_eda(self):
        """Generate EDA plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Price series
        axes[0, 0].plot(self.data.index, self.data['Close'])
        axes[0, 0].set_title('Price Series')
        axes[0, 0].set_ylabel('Price')
        axes[0, 0].grid(True, alpha=0.3)

        # Returns histogram
        axes[0, 1].hist(self.data['Returns'], bins=50, edgecolor='black')
        axes[0, 1].set_title('Returns Distribution')
        axes[0, 1].set_xlabel('Returns')
        axes[0, 1].grid(True, alpha=0.3)

        # Volume
        axes[1, 0].bar(self.data.index, self.data['Volume'])
        axes[1, 0].set_title('Volume')
        axes[1, 0].set_ylabel('Volume')
        axes[1, 0].grid(True, alpha=0.3)

        # Target distribution
        target_counts = self.data['Target'].value_counts()
        axes[1, 1].pie(target_counts.values, labels=[
                       'Down', 'Up'], autopct='%1.1f%%')
        axes[1, 1].set_title('Target Distribution')

        plt.tight_layout()
        plt.show()

    def feature_engineering(self):
        """Step 2: Build predictive features"""
        print("Building predictive feature set...")

        feature_groups = []

        feature_groups.append(self._add_technical_indicators())
        feature_groups.append(self._add_rolling_statistics())
        feature_groups.append(self._add_lag_features())
        feature_groups.append(self._add_volatility_features())
        feature_groups.append(self._add_temporal_features())

        # Merge
        self.features = pd.concat(feature_groups, axis=1).dropna()

        # Reduce multicollinearity
        self.features = self._remove_highly_correlated(self.features)

        # Align with target series
        self.features = self.features.reindex(self.data.index).dropna()
        self.data = self.data.reindex(self.features.index)

        print(f"Generated {len(self.features.columns)} features.")
        return self.features

    def _add_technical_indicators(self):
        """Technical indicators"""
        df = pd.DataFrame(index=self.data.index)

        # RSI
        delta = self.data['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = self.data['Close'].ewm(span=12).mean()
        exp2 = self.data['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        mid = self.data['Close'].rolling(20).mean()
        std = self.data['Close'].rolling(20).std()
        df['BB_Upper'] = mid + 2 * std
        df['BB_Lower'] = mid - 2 * std
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / mid

        return df

    def _add_rolling_statistics(self, windows=[5, 10, 20]):
        """Rolling window statistics"""
        df = pd.DataFrame(index=self.data.index)

        for w in windows:
            df[f'Roll_Mean_{w}'] = self.data['Close'].rolling(w).mean()
            df[f'Roll_Std_{w}'] = self.data['Close'].rolling(w).std()
            df[f'Roll_Return_{w}'] = self.data['Returns'].rolling(w).mean()

        return df

    def _add_lag_features(self, lags=[1, 2, 3, 5]):
        """Lagged features"""
        df = pd.DataFrame(index=self.data.index)
        for lag in lags:
            df[f'Return_Lag_{lag}'] = self.data['Returns'].shift(lag)
            df[f'Volume_Lag_{lag}'] = self.data['Volume'].shift(lag)
        return df

    def _add_volatility_features(self):
        """Volatility-related features"""
        df = pd.DataFrame(index=self.data.index)
        returns = self.data['Returns']

        for w in [5, 10, 20]:
            df[f'Realized_Vol_{w}'] = returns.rolling(w).std() * np.sqrt(252)

        return df

    def _add_temporal_features(self):
        """Date-based features"""
        df = pd.DataFrame(index=self.data.index)
        df['Day_of_Week'] = self.data.index.dayofweek
        df['Month'] = self.data.index.month
        df['Quarter'] = self.data.index.quarter
        return df

    def _remove_highly_correlated(self, features, threshold=0.95):
        """Drop highly correlated features"""
        corr_matrix = features.corr().abs()
        upper = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
        if to_drop:
            print(f"Removing {len(to_drop)} highly correlated features")
            features = features.drop(columns=to_drop)
        return features

    def model_training(self):
        """Step 3: Train multiple ML models"""
        print("Training machine learning models...")

        X = self.features
        y = self.data['Target']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        models = {
            'LogisticRegression': {
                'model': LogisticRegression(),
                'params': {'C': [0.1, 1, 10]}
            },
            'RandomForest': {
                'model': RandomForestClassifier(),
                'params': {'n_estimators': [100, 200], 'max_depth': [10, None]}
            },
            'GradientBoosting': {
                'model': GradientBoostingClassifier(),
                'params': {'n_estimators': [100, 200], 'learning_rate': [0.05, 0.1]}
            }
        }

        tscv = TimeSeriesSplit(n_splits=5)

        for name, config in models.items():
            print(f"\nTraining {name}...")
            grid = GridSearchCV(
                config['model'], config['params'], cv=tscv, scoring='accuracy')
            grid.fit(X_scaled, y)

            self.models[name] = {
                'model': grid.best_estimator_,
                'best_score': grid.best_score_,
                'best_params': grid.best_params_
            }

            print(f"  Best Accuracy: {grid.best_score_:.4f}")
            print(f"  Best Params: {grid.best_params_}")

        # Select best model
        best_name = max(
            self.models, key=lambda x: self.models[x]['best_score'])
        self.best_model = self.models[best_name]['model']

        self.predictions = self.best_model.predict(X_scaled)

        print(f"\nBest Model: {best_name}")
        return self.models

    def strategy_backtesting(self):
        """Step 4: Simple backtest"""
        print("Running backtest...")

        signals = pd.Series(self.predictions, index=self.features.index)
        price = self.data['Close']

        capital = 10000
        shares = 0
        values = []

        for date, signal in signals.items():
            p = price.loc[date]

            # Buy if signal is 1
            if signal == 1 and shares == 0:
                shares = capital // p
                capital -= shares * p

            # Sell if signal = 0
            if signal == 0 and shares > 0:
                capital += shares * p
                shares = 0

            values.append(capital + shares * p)

        portfolio = pd.Series(values, index=signals.index)

        self.backtest_results = {
            "final_value": portfolio.iloc[-1],
            "return": portfolio.iloc[-1] / portfolio.iloc[0] - 1
        }

        print(f"Final Portfolio Value: ${portfolio.iloc[-1]:.2f}")
        print(f"Total Return: {self.backtest_results['return']:.2%}")

    def generate_reports(self):
        print("Generating reports...")
        # Extend with charts or tables as needed


def run_complete_project():
    """Execute full pipeline"""
    model = PredictiveMarketModel(
        ticker="SPY",
        start_date="2018-01-01",
        end_date="2023-12-31"
    )
    model.run_full_pipeline()
    return model


if __name__ == "__main__":
    predictive_model = run_complete_project()
    print("\nPREDICTIVE MARKET MODEL COMPLETE")
