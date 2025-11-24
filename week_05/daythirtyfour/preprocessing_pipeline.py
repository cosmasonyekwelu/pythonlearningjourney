"""
Complete Data Preprocessing Pipeline
End-to-end data preparation for financial modeling
"""

from feature_engineer import FinancialFeatureEngineer
from data_cleaner import FinancialDataCleaner
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class FinancialPreprocessingPipeline:
    """
    Complete preprocessing pipeline for financial data
    """

    def __init__(self):
        self.cleaner = FinancialDataCleaner()
        self.engineer = FinancialFeatureEngineer()
        self.pipeline_steps = []

    def create_pipeline(self, steps=None):
        """
        Create a preprocessing pipeline with specified steps
        """
        if steps is None:
            steps = [
                ('handle_missing_data', FunctionTransformer(self._handle_missing)),
                ('treat_outliers', FunctionTransformer(self._treat_outliers)),
                ('create_price_features', FunctionTransformer(
                    self._create_price_features)),
                ('create_technical_features', FunctionTransformer(
                    self._create_technical_features)),
                ('create_time_features', FunctionTransformer(
                    self._create_time_features)),
                ('scale_features', FunctionTransformer(self._scale_features))
            ]

        self.pipeline = Pipeline(steps)
        return self.pipeline

    def _handle_missing(self, X):
        """Pipeline step: Handle missing data"""
        return self.cleaner.handle_missing_data(X, method='multiple')

    def _treat_outliers(self, X):
        """Pipeline step: Treat outliers"""
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        return self.cleaner.treat_outliers(X, columns=numeric_cols, method='cap')

    def _create_price_features(self, X):
        """Pipeline step: Create price features"""
        return self.engineer.create_price_features(X)

    def _create_technical_features(self, X):
        """Pipeline step: Create technical indicators"""
        return self.engineer.create_technical_indicators(X)

    def _create_time_features(self, X):
        """Pipeline step: Create time features"""
        return self.engineer.create_time_features(X)

    def _scale_features(self, X):
        """Pipeline step: Scale features"""
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        # Scale only non-binary features
        scaling_cols = [col for col in numeric_cols if X[col].nunique() > 2]
        return self.engineer.scale_features(X, columns=scaling_cols)

    def process_single_stock(self, symbol, period='6mo'):
        """
        Process a single stock through the complete pipeline
        """
        print(f"Processing {symbol}...")

        # Fetch data
        try:
            stock = yf.Ticker(symbol)
            raw_data = stock.history(period=period)

            if raw_data.empty:
                print(f"No data available for {symbol}")
                return None

            # Initial data validation
            initial_quality = self.cleaner.validate_data_quality(raw_data)

            # Apply pipeline
            if not hasattr(self, 'pipeline'):
                self.create_pipeline()

            processed_data = self.pipeline.fit_transform(raw_data)

            # Final data validation
            final_quality = self.cleaner.validate_data_quality(processed_data)

            # Generate processing report
            self._generate_processing_report(
                symbol, raw_data, processed_data, initial_quality, final_quality)

            return processed_data

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            return None

    def process_portfolio(self, symbols, period='6mo'):
        """
        Process multiple stocks through the pipeline
        """
        portfolio_data = {}

        for symbol in symbols:
            processed_data = self.process_single_stock(symbol, period)
            if processed_data is not None:
                portfolio_data[symbol] = processed_data

        print(
            f"\nPortfolio processing complete: {len(portfolio_data)}/{len(symbols)} stocks processed")
        return portfolio_data

    def create_training_dataset(self, portfolio_data, target_column='returns', lookback_days=30, forecast_days=5):
        """
        Create training dataset for machine learning
        """
        X_list = []
        y_list = []
        feature_names = None

        for symbol, data in portfolio_data.items():
            # Ensure we have the target column
            if target_column not in data.columns:
                print(f"Target column '{target_column}' not found in {symbol}")
                continue

            # Prepare features and target
            features = data.select_dtypes(include=[np.number]).columns
            feature_data = data[features].dropna()

            if len(feature_data) < lookback_days + forecast_days:
                print(f"Insufficient data for {symbol}")
                continue

            # Create sequences
            for i in range(lookback_days, len(feature_data) - forecast_days):
                # Features (lookback window)
                X_window = feature_data.iloc[i -
                                             lookback_days:i].values.flatten()

                # Target (future return)
                future_price = feature_data[target_column].iloc[i+forecast_days]
                current_price = feature_data[target_column].iloc[i]
                y_value = (future_price - current_price) / \
                    current_price if current_price != 0 else 0

                X_list.append(X_window)
                y_list.append(y_value)

            # Store feature names for first symbol
            if feature_names is None:
                feature_names = [
                    f"{col}_t-{j}" for j in range(lookback_days-1, -1, -1) for col in features]

        if len(X_list) == 0:
            print("No training data created")
            return None, None, None

        X_array = np.array(X_list)
        y_array = np.array(y_list)

        print(
            f"Training dataset created: {X_array.shape[0]} samples, {X_array.shape[1]} features")

        return X_array, y_array, feature_names

    def _generate_processing_report(self, symbol, raw_data, processed_data, initial_quality, final_quality):
        """
        Generate processing report for a symbol
        """
        print(f"\nPROCESSING REPORT: {symbol}")
        print("=" * 40)
        print(
            f"Original data: {len(raw_data)} records, {len(raw_data.columns)} features")
        print(
            f"Processed data: {len(processed_data)} records, {len(processed_data.columns)} features")
        print(
            f"Features added: {len(processed_data.columns) - len(raw_data.columns)}")

        # Data quality improvement
        initial_missing = initial_quality['completeness']['missing_values']
        final_missing = final_quality['completeness']['missing_values']

        total_initial_missing = sum(initial_missing.values())
        total_final_missing = sum(final_missing.values())

        print(
            f"Missing values: {total_initial_missing} → {total_final_missing}")
        print(
            f"Data completeness: {(1 - total_final_missing/len(processed_data)):.1%}")


def demonstrate_pipeline():
    """
    Demonstrate the complete preprocessing pipeline
    """
    print("Financial Data Preprocessing Pipeline")
    print("=" * 50)

    pipeline = FinancialPreprocessingPipeline()

    # Sample portfolio
    symbols = ['AAPL', 'MSFT', 'GOOGL']

    print("Processing portfolio through pipeline...")
    portfolio_data = pipeline.process_portfolio(symbols, period='3mo')

    if not portfolio_data:
        print("No data processed. Creating synthetic data for demonstration...")
        # Create synthetic data for demonstration
        dates = pd.date_range('2024-01-01', periods=60, freq='D')
        synthetic_data = {}

        for symbol in symbols:
            data = pd.DataFrame({
                'Open': np.random.normal(100, 2, 60).cumsum(),
                'High': np.random.normal(102, 3, 60).cumsum(),
                'Low': np.random.normal(98, 3, 60).cumsum(),
                'Close': np.random.normal(100, 2, 60).cumsum(),
                'Volume': np.random.lognormal(10, 1, 60)
            }, index=dates)
            synthetic_data[symbol] = data

        # Process synthetic data
        processed_data = {}
        for symbol, data in synthetic_data.items():
            processed = pipeline.pipeline.fit_transform(data)
            processed_data[symbol] = processed

        portfolio_data = processed_data

    # Create training dataset
    print("\nCreating training dataset...")
    X, y, feature_names = pipeline.create_training_dataset(
        portfolio_data,
        target_column='returns',
        lookback_days=10,
        forecast_days=5
    )

    if X is not None:
        print(f"Training dataset shape: X {X.shape}, y {y.shape}")
        print(f"Number of features: {len(feature_names)}")

        # Show feature importance (simple correlation)
        if len(feature_names) > 0:
            correlations = []
            for i in range(min(10, X.shape[1])):  # First 10 features
                corr = np.corrcoef(X[:, i], y)[0, 1] if not np.isnan(
                    X[:, i]).any() else 0
                correlations.append((feature_names[i], corr))

            print("\nTop feature correlations with target:")
            for feature, corr in sorted(correlations, key=lambda x: abs(x[1]), reverse=True)[:5]:
                print(f"  {feature}: {corr:.3f}")

    return pipeline, portfolio_data


if __name__ == "__main__":
    pipeline, portfolio_data = demonstrate_pipeline()
