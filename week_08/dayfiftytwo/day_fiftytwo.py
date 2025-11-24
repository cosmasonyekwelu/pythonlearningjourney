import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import yfinance as yf
import ta
from ta import add_all_ta_features
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, ROCIndicator
from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    def __init__(self):
        self.data = None
        self.features = None
        self.feature_names = []
        
    def load_data(self, ticker='SPY', start_date='2020-01-01', end_date=None):
        """Load and prepare base data"""
        if end_date is None:
            end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
            
        self.data = yf.download(ticker, start=start_date, end=end_date)
        self.data['Returns'] = self.data['Adj Close'].pct_change()
        self.data['Log_Returns'] = np.log(self.data['Adj Close'] / self.data['Adj Close'].shift(1))
        self.data['Target'] = self.data['Returns'].shift(-1)  # Next day return
        return self.data
    
    def add_technical_indicators(self):
        """Add comprehensive technical indicators"""
        print("Adding technical indicators...")
        
        # Price data
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        volume = self.data['Volume']
        open_price = self.data['Open']
        
        # 1. Momentum Indicators
        # RSI
        rsi = RSIIndicator(close=close, window=14)
        self.data['RSI_14'] = rsi.rsi()
        
        # Stochastic
        stoch = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
        self.data['Stoch_%K'] = stoch.stoch()
        self.data['Stoch_%D'] = stoch.stoch_signal()
        
        # Williams %R
        williams = WilliamsRIndicator(high=high, low=low, close=close, lbp=14)
        self.data['Williams_R'] = williams.williams_r()
        
        # Rate of Change
        roc = ROCIndicator(close=close, window=10)
        self.data['ROC_10'] = roc.roc()
        
        # 2. Trend Indicators
        # MACD
        macd = MACD(close=close)
        self.data['MACD'] = macd.macd()
        self.data['MACD_Signal'] = macd.macd_signal()
        self.data['MACD_Histogram'] = macd.macd_diff()
        
        # ADX
        adx = ADXIndicator(high=high, low=low, close=close, window=14)
        self.data['ADX'] = adx.adx()
        self.data['ADX_Pos'] = adx.adx_pos()
        self.data['ADX_Neg'] = adx.adx_neg()
        
        # CCI
        cci = CCIIndicator(high=high, low=low, close=close, window=20)
        self.data['CCI'] = cci.cci()
        
        # 3. Volatility Indicators
        # Bollinger Bands
        bb = BollingerBands(close=close, window=20, window_dev=2)
        self.data['BB_Upper'] = bb.bollinger_hband()
        self.data['BB_Lower'] = bb.bollinger_lband()
        self.data['BB_Middle'] = bb.bollinger_mavg()
        self.data['BB_Width'] = (self.data['BB_Upper'] - self.data['BB_Lower']) / self.data['BB_Middle']
        self.data['BB_Position'] = (close - self.data['BB_Lower']) / (self.data['BB_Upper'] - self.data['BB_Lower'])
        
        # ATR
        atr = AverageTrueRange(high=high, low=low, close=close, window=14)
        self.data['ATR'] = atr.average_true_range()
        
        # 4. Volume Indicators
        # OBV
        obv = OnBalanceVolumeIndicator(close=close, volume=volume)
        self.data['OBV'] = obv.on_balance_volume()
        
        # VWAP
        vwap = VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume, window=14)
        self.data['VWAP'] = vwap.volume_weighted_average_price()
        self.data['Price_VWAP_Ratio'] = close / self.data['VWAP']
        
        print(f"Added {15} technical indicators")
        
    def add_rolling_statistics(self, windows=[5, 10, 20, 50]):
        """Add rolling window statistics"""
        print("Adding rolling statistics...")
        
        close = self.data['Close']
        returns = self.data['Returns']
        
        for window in windows:
            # Rolling returns
            self.data[f'Roll_Return_{window}'] = returns.rolling(window=window).mean()
            self.data[f'Roll_Vol_{window}'] = returns.rolling(window=window).std()
            
            # Rolling price statistics
            self.data[f'Roll_Mean_{window}'] = close.rolling(window=window).mean()
            self.data[f'Roll_Std_{window}'] = close.rolling(window=window).std()
            self.data[f'Roll_Min_{window}'] = close.rolling(window=window).min()
            self.data[f'Roll_Max_{window}'] = close.rolling(window=window).max()
            
            # Z-score (price relative to rolling mean)
            self.data[f'Z_Score_{window}'] = (close - self.data[f'Roll_Mean_{window}']) / self.data[f'Roll_Std_{window}']
            
            # Rolling highs/lows
            self.data[f'High_Ratio_{window}'] = close / self.data[f'Roll_Max_{window}']
            self.data[f'Low_Ratio_{window}'] = close / self.data[f'Roll_Min_{window}']
        
        print(f"Added {len(windows) * 8} rolling features")
    
    def add_lag_features(self, lags=[1, 2, 3, 5, 10]):
        """Add lagged features"""
        print("Adding lag features...")
        
        features_to_lag = ['Returns', 'Log_Returns', 'Volume', 'RSI_14', 'MACD']
        
        for feature in features_to_lag:
            if feature in self.data.columns:
                for lag in lags:
                    self.data[f'{feature}_Lag_{lag}'] = self.data[feature].shift(lag)
        
        # Price momentum features
        for lag in [1, 5, 10]:
            self.data[f'Price_Ratio_{lag}'] = self.data['Close'] / self.data['Close'].shift(lag)
            self.data[f'Volume_Ratio_{lag}'] = self.data['Volume'] / self.data['Volume'].shift(lag)
        
        print(f"Added {len(features_to_lag) * len(lags) + 6} lag features")
    
    def add_volatility_features(self):
        """Add advanced volatility metrics"""
        print("Adding volatility features...")
        
        returns = self.data['Returns'].dropna()
        
        # Realized volatility (different time horizons)
        for window in [5, 10, 20]:
            self.data[f'Realized_Vol_{window}'] = returns.rolling(window=window).std() * np.sqrt(252)
        
        # Parkinson volatility (using high-low range)
        self.data['Parkinson_Vol'] = (np.log(self.data['High'] / self.data['Low']) ** 2) / (4 * np.log(2))
        self.data['Parkinson_Vol_20'] = self.data['Parkinson_Vol'].rolling(20).mean() * np.sqrt(252)
        
        # Volatility ratio (short-term vs long-term)
        self.data['Vol_Ratio_5_20'] = self.data['Realized_Vol_5'] / self.data['Realized_Vol_20']
        
        # Volatility regime
        vol_median = self.data['Realized_Vol_20'].median()
        self.data['High_Vol_Regime'] = (self.data['Realized_Vol_20'] > vol_median).astype(int)
        
        print("Added 7 volatility features")
    
    def add_temporal_features(self):
        """Add time-based features"""
        print("Adding temporal features...")
        
        # Date features
        self.data['Day_of_Week'] = self.data.index.dayofweek
        self.data['Day_of_Month'] = self.data.index.day
        self.data['Week_of_Year'] = self.data.index.isocalendar().week
        self.data['Month'] = self.data.index.month
        self.data['Quarter'] = self.data.index.quarter
        
        # Time period features
        self.data['Is_Month_Start'] = self.data.index.is_month_start.astype(int)
        self.data['Is_Month_End'] = self.data.index.is_month_end.astype(int)
        self.data['Is_Quarter_Start'] = self.data.index.is_quarter_start.astype(int)
        self.data['Is_Quarter_End'] = self.data.index.is_quarter_end.astype(int)
        
        # Seasonal patterns
        self.data['Sin_Day'] = np.sin(2 * np.pi * self.data.index.dayofyear / 365)
        self.data['Cos_Day'] = np.cos(2 * np.pi * self.data.index.dayofyear / 365)
        
        print("Added 11 temporal features")
    
    def create_custom_mean_reversion_indicator(self):
        """Create custom mean reversion indicator"""
        print("Creating custom mean reversion indicator...")
        
        close = self.data['Close']
        
        # Multiple time frame mean reversion
        for short_window in [5, 10]:
            for long_window in [20, 50]:
                short_ma = close.rolling(short_window).mean()
                long_ma = close.rolling(long_window).mean()
                
                # Price deviation from moving average
                self.data[f'MR_Deviation_{short_window}_{long_window}'] = (
                    close - (short_ma + long_ma) / 2
                ) / close
                
                # Z-score of the deviation
                deviation = self.data[f'MR_Deviation_{short_window}_{long_window}']
                self.data[f'MR_ZScore_{short_window}_{long_window}'] = (
                    deviation - deviation.rolling(long_window).mean()
                ) / deviation.rolling(long_window).std()
        
        # RSI-based mean reversion
        rsi = self.data['RSI_14']
        self.data['RSI_Mean_Reversion'] = np.where(
            (rsi < 30) | (rsi > 70), 
            (rsi - 50) / 50,  # Normalized to -1 to 1
            0
        )
        
        # Bollinger Band mean reversion
        bb_position = self.data['BB_Position']
        self.data['BB_Mean_Reversion'] = np.where(
            (bb_position < 0.1) | (bb_position > 0.9),
            (bb_position - 0.5) * 2,  # Normalized to -1 to 1
            0
        )
        
        # Combined mean reversion signal
        mr_signals = [f'MR_ZScore_5_20', f'MR_ZScore_10_50', 'RSI_Mean_Reversion', 'BB_Mean_Reversion']
        available_signals = [col for col in mr_signals if col in self.data.columns]
        
        if available_signals:
            self.data['Combined_MR_Signal'] = self.data[available_signals].mean(axis=1)
        
        print("Added custom mean reversion indicators")
        
        return self.data['Combined_MR_Signal'] if 'Combined_MR_Signal' in self.data.columns else None
    
    def evaluate_mean_reversion_predictive_power(self, mr_signal_column='Combined_MR_Signal'):
        """Evaluate predictive power of mean reversion indicator"""
        if mr_signal_column not in self.data.columns:
            print("Mean reversion signal not found")
            return None
        
        # Calculate correlation with future returns
        correlations = {}
        for future_period in [1, 2, 3, 5]:
            future_returns = self.data['Returns'].shift(-future_period)
            corr = self.data[mr_signal_column].corr(future_returns)
            correlations[f'Corr_T+{future_period}'] = corr
        
        # Signal effectiveness by regime
        high_vol = self.data['High_Vol_Regime'] == 1
        low_vol = self.data['High_Vol_Regime'] == 0
        
        corr_high_vol = self.data.loc[high_vol, mr_signal_column].corr(
            self.data.loc[high_vol, 'Target']
        )
        corr_low_vol = self.data.loc[low_vol, mr_signal_column].corr(
            self.data.loc[low_vol, 'Target']
        )
        
        print("\nMean Reversion Indicator Evaluation:")
        print("Correlations with Future Returns:")
        for period, corr in correlations.items():
            print(f"  {period}: {corr:.4f}")
        
        print(f"\nCorrelation by Volatility Regime:")
        print(f"  High Volatility: {corr_high_vol:.4f}")
        print(f"  Low Volatility: {corr_low_vol:.4f}")
        
        # Plot signal vs returns
        self.plot_signal_vs_returns(mr_signal_column)
        
        return correlations
    
    def plot_signal_vs_returns(self, signal_column):
        """Plot mean reversion signal vs future returns"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Time series of signal and returns
        ax1.plot(self.data.index, self.data[signal_column], label='MR Signal', alpha=0.7)
        ax1.plot(self.data.index, self.data['Target'] * 10, label='Future Returns (scaled)', alpha=0.7)
        ax1.set_title('Mean Reversion Signal vs Future Returns', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Scatter plot
        valid_data = self.data[[signal_column, 'Target']].dropna()
        ax2.scatter(valid_data[signal_column], valid_data['Target'], alpha=0.5, s=10)
        ax2.set_xlabel('Mean Reversion Signal')
        ax2.set_ylabel('Future Return')
        ax2.set_title('Signal vs Return Scatter Plot', fontweight='bold')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3)
        
        # Add correlation line
        z = np.polyfit(valid_data[signal_column], valid_data['Target'], 1)
        p = np.poly1d(z)
        ax2.plot(valid_data[signal_column], p(valid_data[signal_column]), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.show()
    
    def normalize_features(self, method='standard'):
        """Normalize features for machine learning"""
        print(f"Normalizing features using {method} method...")
        
        # Identify feature columns (exclude price, target, and datetime columns)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 
                       'Returns', 'Log_Returns', 'Target']
        feature_cols = [col for col in self.data.columns if col not in exclude_cols]
        
        # Remove columns with too many NaNs
        feature_cols = [col for col in feature_cols if self.data[col].notna().sum() > len(self.data) * 0.8]
        
        self.feature_names = feature_cols
        feature_data = self.data[feature_cols].copy()
        
        # Handle missing values
        feature_data = feature_data.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        # Normalize
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Method must be 'standard' or 'minmax'")
        
        normalized_features = scaler.fit_transform(feature_data)
        self.features = pd.DataFrame(normalized_features, 
                                   index=self.data.index, 
                                   columns=feature_cols)
        
        print(f"Normalized {len(feature_cols)} features")
        return self.features, scaler
    
    def build_feature_pipeline(self, ticker='SPY'):
        """Build complete feature pipeline"""
        print("BUILDING COMPLETE FEATURE PIPELINE")
        print("=" * 50)
        
        # Load data
        self.load_data(ticker)
        
        # Add all feature types
        self.add_technical_indicators()
        self.add_rolling_statistics()
        self.add_lag_features()
        self.add_volatility_features()
        self.add_temporal_features()
        
        # Create and evaluate custom mean reversion indicator
        mr_signal = self.create_custom_mean_reversion_indicator()
        
        # Normalize features
        features, scaler = self.normalize_features()
        
        # Combine with target
        final_data = pd.concat([features, self.data[['Target']]], axis=1)
        final_data = final_data.dropna()
        
        print(f"\nPipeline Complete!")
        print(f"Original data shape: {self.data.shape}")
        print(f"Final feature set: {len(self.feature_names)} features")
        print(f"Final dataset shape: {final_data.shape}")
        
        # Feature correlation analysis
        self.analyze_feature_correlations()
        
        return final_data, self.feature_names
    
    def analyze_feature_correlations(self, top_n=20):
        """Analyze correlations between features and target"""
        if self.features is None:
            print("Features not built yet")
            return
        
        # Calculate correlations with target
        feature_target_corr = {}
        for feature in self.feature_names:
            if feature in self.data.columns:
                corr = self.data[feature].corr(self.data['Target'])
                feature_target_corr[feature] = corr
        
        # Get top correlated features
        sorted_correlations = sorted(feature_target_corr.items(), key=lambda x: abs(x[1]), reverse=True)
        
        print(f"\nTop {top_n} Features by Absolute Correlation with Target:")
        for feature, corr in sorted_correlations[:top_n]:
            print(f"  {feature}: {corr:.4f}")
        
        # Plot top correlations
        top_features = [x[0] for x in sorted_correlations[:top_n]]
        top_corrs = [x[1] for x in sorted_correlations[:top_n]]
        
        plt.figure(figsize=(12, 8))
        colors = ['red' if x < 0 else 'blue' for x in top_corrs]
        plt.barh(range(len(top_features)), top_corrs, color=colors, alpha=0.7)
        plt.yticks(range(len(top_features)), top_features)
        plt.xlabel('Correlation with Target')
        plt.title(f'Top {top_n} Feature Correlations with Future Returns', fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.show()
        
        return sorted_correlations

# Challenge: Custom mean reversion indicator
def custom_mean_reversion_challenge():
    """Challenge: Design and test custom mean reversion indicator"""
    print("CUSTOM MEAN REVERSION INDICATOR CHALLENGE")
    print("=" * 60)
    
    engineer = FeatureEngineer()
    
    # Build feature pipeline
    final_data, feature_names = engineer.build_feature_pipeline('SPY')
    
    # Evaluate mean reversion indicator
    if 'Combined_MR_Signal' in engineer.data.columns:
        correlations = engineer.evaluate_mean_reversion_predictive_power()
        
        # Test different parameter combinations
        print("\nTesting Different Mean Reversion Parameter Combinations:")
        
        # Test various window combinations
        window_combinations = [(5, 10), (10, 20), (5, 50), (20, 50)]
        
        for short, long in window_combinations:
            col_name = f'MR_ZScore_{short}_{long}'
            if col_name in engineer.data.columns:
                corr = engineer.data[col_name].corr(engineer.data['Target'])
                print(f"  {col_name}: {corr:.4f}")
    
    return engineer, final_data

if __name__ == "__main__":
    # Run complete feature engineering pipeline
    engineer, final_data = custom_mean_reversion_challenge()
    
    # Display final dataset info
    print(f"\nFinal Dataset Info:")
    print(f"Features: {len(engineer.feature_names)}")
    print(f"Samples: {len(final_data)}")
    print(f"Memory usage: {final_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")