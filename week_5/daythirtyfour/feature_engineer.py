"""
Feature Engineering for Financial Data
Creating technical indicators and derived features
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import warnings
warnings.filterwarnings('ignore')


class FinancialFeatureEngineer:
    """
    Create and transform features for financial modeling
    """

    def __init__(self):
        self.scalers = {}
        self.feature_stats = {}

    def create_price_features(self, df, price_column='Close'):
        """
        Create basic price-based features
        """
        features_df = df.copy()

        # Basic returns
        features_df['returns'] = df[price_column].pct_change()
        features_df['log_returns'] = np.log(
            df[price_column] / df[price_column].shift(1))

        # Price momentum
        features_df['price_change'] = df[price_column].diff()
        features_df['price_gap'] = (
            df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) if 'Open' in df.columns else 0

        # High-Low range
        if 'High' in df.columns and 'Low' in df.columns:
            features_df['hl_range'] = (df['High'] - df['Low']) / df['Close']
            features_df['hl_range_pct'] = (df['High'] - df['Low']) / df['Low']

        return features_df

    def create_technical_indicators(self, df, price_column='Close', volume_column='Volume'):
        """
        Create comprehensive technical indicators
        """
        features_df = df.copy()

        # Moving averages
        windows = [5, 10, 20, 50]
        for window in windows:
            # Simple Moving Average
            features_df[f'SMA_{window}'] = df[price_column].rolling(
                window=window).mean()

            # Exponential Moving Average
            features_df[f'EMA_{window}'] = df[price_column].ewm(
                span=window, adjust=False).mean()

            # Moving average crossovers
            if window > 5:
                features_df[f'SMA_cross_{window}'] = (
                    features_df[f'SMA_{window}'] > features_df['SMA_5']).astype(int)

        # Volatility measures
        for window in [5, 10, 20]:
            features_df[f'volatility_{window}'] = df[price_column].pct_change().rolling(
                window=window).std()
            features_df[f'rolling_range_{window}'] = (df[price_column].rolling(window=window).max() -
                                                      df[price_column].rolling(window=window).min()) / df[price_column]

        # RSI
        features_df['RSI'] = self.calculate_rsi(df[price_column])

        # MACD
        features_df['MACD'], features_df['MACD_signal'] = self.calculate_macd(
            df[price_column])
        features_df['MACD_histogram'] = features_df['MACD'] - \
            features_df['MACD_signal']

        # Bollinger Bands
        features_df['BB_upper'], features_df['BB_lower'], features_df['BB_middle'] = self.calculate_bollinger_bands(
            df[price_column])
        features_df['BB_position'] = (df[price_column] - features_df['BB_lower']) / (
            features_df['BB_upper'] - features_df['BB_lower'])

        # Volume indicators
        if volume_column in df.columns:
            features_df['volume_sma'] = df[volume_column].rolling(
                window=20).mean()
            features_df['volume_ratio'] = df[volume_column] / \
                features_df['volume_sma']
            features_df['volume_price_trend'] = df[volume_column] * \
                df[price_column].pct_change()

        # Support and resistance levels (simplified)
        features_df['resistance'] = df[price_column].rolling(window=20).max()
        features_df['support'] = df[price_column].rolling(window=20).min()
        features_df['price_vs_resistance'] = df[price_column] / \
            features_df['resistance']
        features_df['price_vs_support'] = df[price_column] / \
            features_df['support']

        return features_df

    def create_time_features(self, df):
        """
        Create time-based features
        """
        features_df = df.copy()

        if hasattr(df.index, 'hour'):
            # Intraday features
            features_df['hour'] = df.index.hour
            features_df['day_of_week'] = df.index.dayofweek
            features_df['day_of_month'] = df.index.day
            features_df['week_of_year'] = df.index.isocalendar().week
            features_df['month'] = df.index.month
            features_df['quarter'] = df.index.quarter

            # Time-based indicators
            features_df['is_market_open'] = (
                (df.index.hour >= 9) & (df.index.hour < 16)).astype(int)
            features_df['is_month_end'] = (df.index.is_month_end).astype(int)
            features_df['is_quarter_end'] = (
                df.index.is_quarter_end).astype(int)

        return features_df

    def create_derived_features(self, df):
        """
        Create derived statistical features
        """
        features_df = df.copy()

        numeric_cols = features_df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Rolling statistics
            features_df[f'{col}_rolling_mean_5'] = features_df[col].rolling(
                5).mean()
            features_df[f'{col}_rolling_std_5'] = features_df[col].rolling(
                5).std()
            features_df[f'{col}_rolling_skew_5'] = features_df[col].rolling(
                5).skew()

            # Lag features
            for lag in [1, 2, 3, 5]:
                features_df[f'{col}_lag_{lag}'] = features_df[col].shift(lag)

            # Difference features
            for diff in [1, 2, 3]:
                features_df[f'{col}_diff_{diff}'] = features_df[col].diff(diff)

            # Percentage change features
            for period in [1, 2, 3]:
                features_df[f'{col}_pct_change_{period}'] = features_df[col].pct_change(
                    period)

        return features_df

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
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band, rolling_mean

    def scale_features(self, df, columns=None, method='standard', store_scaler=True):
        """
        Scale features for machine learning
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns

        df_scaled = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'robust':
                scaler = RobustScaler()
            else:
                raise ValueError("Unknown scaling method")

            # Handle NaN values temporarily
            valid_data = df[col].dropna()
            if len(valid_data) == 0:
                continue

            scaled_values = scaler.fit_transform(
                valid_data.values.reshape(-1, 1))

            # Create new column with scaled values
            df_scaled[f'{col}_scaled'] = np.nan
            df_scaled.loc[valid_data.index,
                          f'{col}_scaled'] = scaled_values.flatten()

            if store_scaler:
                self.scalers[col] = scaler
                self.feature_stats[col] = {
                    'mean': valid_data.mean(),
                    'std': valid_data.std(),
                    'min': valid_data.min(),
                    'max': valid_data.max()
                }

        return df_scaled

    def create_feature_summary(self, df):
        """
        Create summary of all features
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        summary = {
            'total_features': len(df.columns),
            'numeric_features': len(numeric_cols),
            'categorical_features': len(df.columns) - len(numeric_cols),
            'feature_categories': {}
        }

        # Categorize features
        for col in df.columns:
            if 'return' in col.lower():
                category = 'returns'
            elif 'volume' in col.lower():
                category = 'volume'
            elif 'rsi' in col.lower() or 'macd' in col.lower() or 'bb' in col.lower():
                category = 'technical_indicators'
            elif 'sma' in col.lower() or 'ema' in col.lower():
                category = 'moving_averages'
            elif 'lag' in col.lower() or 'diff' in col.lower():
                category = 'time_series'
            elif col in ['hour', 'day_of_week', 'month']:
                category = 'time_features'
            else:
                category = 'other'

            if category not in summary['feature_categories']:
                summary['feature_categories'][category] = []
            summary['feature_categories'][category].append(col)

        return summary


def demonstrate_feature_engineering():
    """
    Demonstrate feature engineering capabilities
    """
    print("Financial Feature Engineering Demonstration")
    print("=" * 50)

    engineer = FinancialFeatureEngineer()

    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'Open': np.random.normal(100, 2, 100).cumsum(),
        'High': np.random.normal(102, 3, 100).cumsum(),
        'Low': np.random.normal(98, 3, 100).cumsum(),
        'Close': np.random.normal(100, 2, 100).cumsum(),
        'Volume': np.random.lognormal(10, 1, 100)
    }, index=dates)

    print("Original data shape:", sample_data.shape)

    # Create price features
    price_features = engineer.create_price_features(sample_data)
    print("After price features:", price_features.shape)

    # Create technical indicators
    technical_features = engineer.create_technical_indicators(price_features)
    print("After technical indicators:", technical_features.shape)

    # Create time features
    time_features = engineer.create_time_features(technical_features)
    print("After time features:", time_features.shape)

    # Create derived features
    derived_features = engineer.create_derived_features(time_features)
    print("After derived features:", derived_features.shape)

    # Scale features
    numeric_cols = derived_features.select_dtypes(include=[np.number]).columns
    scaled_features = engineer.scale_features(
        derived_features, columns=numeric_cols[:5])  # Scale first 5 for demo
    print("After scaling:", scaled_features.shape)

    # Generate feature summary
    summary = engineer.create_feature_summary(scaled_features)

    print("\nFEATURE ENGINEERING SUMMARY")
    print("=" * 30)
    print(f"Total features created: {summary['total_features']}")
    print(f"Numeric features: {summary['numeric_features']}")
    print(f"Categorical features: {summary['categorical_features']}")

    print("\nFeature categories:")
    for category, features in summary['feature_categories'].items():
        print(f"  {category}: {len(features)} features")

    # Show first few rows of new features
    new_feature_cols = [
        col for col in scaled_features.columns if col not in sample_data.columns]
    print(f"\nSample of new features (first 5):")
    print(scaled_features[new_feature_cols[:5]].head())

    return scaled_features, summary


if __name__ == "__main__":
    demonstrate_feature_engineering()
