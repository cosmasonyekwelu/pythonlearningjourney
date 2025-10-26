"""
Day 34 - Data Cleaning & Preprocessing
Handling missing data, outliers, and data quality issues
"""

import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


class FinancialDataCleaner:
    """
    Comprehensive financial data cleaning and preprocessing
    """

    def __init__(self):
        self.cleaning_report = {}

    def load_sample_data(self, symbols, period='1y'):
        """
        Load sample financial data
        """
        data = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)
                data[symbol] = hist
                print(f"Loaded {symbol}: {len(hist)} records")
            except Exception as e:
                print(f"Error loading {symbol}: {e}")

        return data

    def analyze_missing_data(self, df):
        """
        Analyze missing data patterns
        """
        missing_analysis = {
            'total_records': len(df),
            'missing_values': df.isnull().sum(),
            'missing_percentage': (df.isnull().sum() / len(df)) * 100,
            'columns_with_missing': df.columns[df.isnull().any()].tolist()
        }
        return missing_analysis

    def handle_missing_data(self, df, method='ffill', max_consecutive_nan=5):
        """
        Handle missing data in financial time series

        Args:
            method: 'ffill', 'bfill', 'interpolate', 'drop', 'multiple'
            max_consecutive_nan: Maximum allowed consecutive NaN values
        """
        df_clean = df.copy()
        original_shape = df.shape

        if method == 'ffill':
            # Forward fill then backward fill
            df_clean = df_clean.ffill().bfill()
        elif method == 'interpolate':
            # Time-based interpolation
            df_clean = df_clean.interpolate(
                method='time', limit_direction='both')
        elif method == 'drop':
            # Drop rows with any missing values
            df_clean = df_clean.dropna()
        elif method == 'multiple':
            # Strategic approach based on data type
            for column in df_clean.columns:
                if df_clean[column].dtype in ['float64', 'int64']:
                    # For price data, use interpolation
                    if 'price' in column.lower() or 'close' in column.lower():
                        df_clean[column] = df_clean[column].interpolate(
                            method='time')
                    else:
                        # For other numeric, use forward fill
                        df_clean[column] = df_clean[column].ffill().bfill()
                else:
                    # For non-numeric, use forward fill
                    df_clean[column] = df_clean[column].ffill()

        # Remove rows with too many consecutive NaN values
        consecutive_nan = df_clean.isnull().astype(int).groupby(
            df_clean.notnull().astype(int).cumsum()).cumsum()
        mask = consecutive_nan > max_consecutive_nan
        df_clean = df_clean[~mask.any(axis=1)]

        cleaned_shape = df_clean.shape
        rows_removed = original_shape[0] - cleaned_shape[0]

        self.cleaning_report['missing_data'] = {
            'original_records': original_shape[0],
            'cleaned_records': cleaned_shape[0],
            'rows_removed': rows_removed,
            'method_used': method
        }

        return df_clean

    def detect_outliers(self, series, method='iqr', threshold=3):
        """
        Detect outliers using various statistical methods
        """
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(series.dropna()))
            outlier_mask = z_scores > threshold
        elif method == 'iqr':
            # Interquartile Range method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_mask = (series < lower_bound) | (series > upper_bound)
        elif method == 'modified_zscore':
            # Modified Z-score for robust outlier detection
            median = series.median()
            mad = stats.median_abs_deviation(series.dropna())
            modified_z_scores = 0.6745 * (series - median) / mad
            outlier_mask = np.abs(modified_z_scores) > threshold
        elif method == 'percentile':
            # Percentile-based method
            lower_bound = series.quantile(0.01)
            upper_bound = series.quantile(0.99)
            outlier_mask = (series < lower_bound) | (series > upper_bound)
        else:
            raise ValueError("Unknown outlier detection method")

        return outlier_mask

    def treat_outliers(self, df, columns=None, method='cap', **kwargs):
        """
        Treat outliers in specified columns
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns

        df_treated = df.copy()
        outlier_report = {}

        for column in columns:
            if column not in df_treated.columns:
                continue

            series = df_treated[column]
            outlier_mask = self.detect_outliers(series, **kwargs)
            n_outliers = outlier_mask.sum()

            if method == 'cap':
                # Cap outliers at specified percentiles
                lower_bound = series.quantile(0.05)
                upper_bound = series.quantile(0.95)
                df_treated[column] = series.clip(
                    lower=lower_bound, upper=upper_bound)

            elif method == 'remove':
                # Remove outlier rows
                df_treated = df_treated[~outlier_mask]

            elif method == 'median':
                # Replace with median
                median_val = series.median()
                df_treated.loc[outlier_mask, column] = median_val

            elif method == 'winsorize':
                # Winsorize (cap at percentiles)
                lower_pct = kwargs.get('lower_pct', 0.05)
                upper_pct = kwargs.get('upper_pct', 0.95)
                lower_bound = series.quantile(lower_pct)
                upper_bound = series.quantile(upper_pct)
                df_treated[column] = series.clip(
                    lower=lower_bound, upper=upper_bound)

            outlier_report[column] = {
                'outliers_detected': n_outliers,
                'outlier_percentage': (n_outliers / len(series)) * 100,
                'treatment_method': method
            }

        self.cleaning_report['outliers'] = outlier_report
        return df_treated

    def validate_data_quality(self, df):
        """
        Perform comprehensive data quality validation
        """
        quality_report = {
            'basic_stats': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum()
            },
            'completeness': {
                'missing_values': df.isnull().sum().to_dict(),
                'completeness_rate': (1 - df.isnull().sum() / len(df)).to_dict()
            },
            'consistency': {
                'duplicate_rows': df.duplicated().sum(),
                'date_monotonic': pd.Index(df.index).is_monotonic_increasing if hasattr(df.index, 'is_monotonic_increasing') else True
            },
            'value_ranges': {}
        }

        # Check numeric columns for reasonable ranges
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            quality_report['value_ranges'][col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std()
            }

        self.cleaning_report['quality_validation'] = quality_report
        return quality_report

    def plot_data_quality(self, df, before_clean=None):
        """
        Visualize data quality before and after cleaning
        """
        if before_clean is not None:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))

            # Missing data comparison
            missing_before = before_clean.isnull().sum()
            missing_after = df.isnull().sum()

            axes[0, 0].bar(range(len(missing_before)),
                           missing_before.values, alpha=0.7, label='Before')
            axes[0, 0].bar(range(len(missing_after)),
                           missing_after.values, alpha=0.7, label='After')
            axes[0, 0].set_title('Missing Values Before/After Cleaning')
            axes[0, 0].legend()

            # Outlier visualization for a numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                sample_col = numeric_cols[0]
                axes[0, 1].boxplot(
                    [before_clean[sample_col].dropna(), df[sample_col].dropna()])
                axes[0, 1].set_title(f'Outliers in {sample_col}')
                axes[0, 1].set_xticklabels(['Before', 'After'])

            # Data distribution
            if len(numeric_cols) > 0:
                axes[1, 0].hist(before_clean[sample_col].dropna(),
                                alpha=0.7, label='Before', bins=30)
                axes[1, 0].hist(df[sample_col].dropna(),
                                alpha=0.7, label='After', bins=30)
                axes[1, 0].set_title(f'Distribution of {sample_col}')
                axes[1, 0].legend()

            # Time series plot
            if hasattr(df.index, 'dtype') and np.issubdtype(df.index.dtype, np.datetime64):
                axes[1, 1].plot(
                    before_clean.index, before_clean[sample_col], alpha=0.7, label='Before')
                axes[1, 1].plot(df.index, df[sample_col],
                                alpha=0.7, label='After')
                axes[1, 1].set_title(f'Time Series: {sample_col}')
                axes[1, 1].legend()

        else:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))

            # Missing data
            missing_data = df.isnull().sum()
            axes[0].bar(range(len(missing_data)), missing_data.values)
            axes[0].set_title('Missing Values by Column')
            axes[0].set_xticks(range(len(missing_data)))
            axes[0].set_xticklabels(missing_data.index, rotation=45)

            # Data distribution
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                sample_col = numeric_cols[0]
                axes[1].hist(df[sample_col].dropna(), bins=30)
                axes[1].set_title(f'Distribution of {sample_col}')

        plt.tight_layout()
        plt.show()

    def generate_cleaning_report(self):
        """
        Generate comprehensive cleaning report
        """
        print("DATA CLEANING REPORT")
        print("=" * 50)

        if 'missing_data' in self.cleaning_report:
            print("\nMISSING DATA HANDLING:")
            md = self.cleaning_report['missing_data']
            for key, value in md.items():
                print(f"  {key}: {value}")

        if 'outliers' in self.cleaning_report:
            print("\nOUTLIER TREATMENT:")
            for col, stats in self.cleaning_report['outliers'].items():
                print(
                    f"  {col}: {stats['outliers_detected']} outliers ({stats['outlier_percentage']:.2f}%)")

        if 'quality_validation' in self.cleaning_report:
            print("\nDATA QUALITY SUMMARY:")
            qv = self.cleaning_report['quality_validation']
            print(f"  Total records: {qv['basic_stats']['total_rows']}")
            print(f"  Duplicate rows: {qv['consistency']['duplicate_rows']}")
            print(
                f"  Memory usage: {qv['basic_stats']['memory_usage'] / 1024 / 1024:.2f} MB")


def demonstrate_data_cleaning():
    """
    Demonstrate data cleaning capabilities
    """
    print("Financial Data Cleaning Demonstration")
    print("=" * 50)

    cleaner = FinancialDataCleaner()

    # Load sample data
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    data = cleaner.load_sample_data(symbols, period='6mo')

    if not data:
        print("No data loaded. Creating synthetic data for demonstration...")
        # Create synthetic data with known issues
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        synthetic_data = pd.DataFrame({
            'price': np.random.normal(100, 10, 100),
            'volume': np.random.lognormal(10, 1, 100),
            'returns': np.random.normal(0, 0.02, 100)
        }, index=dates)

        # Introduce some data quality issues
        synthetic_data.iloc[5:10, 0] = np.nan  # Missing values
        synthetic_data.iloc[20, 0] = 1000      # Outlier
        synthetic_data.iloc[40, 1] = -500      # Negative volume (impossible)

        data = {'SYNTH': synthetic_data}

    # Clean each dataset
    cleaned_data = {}
    for symbol, raw_df in data.items():
        print(f"\nCleaning data for {symbol}...")

        # Analyze missing data
        missing_analysis = cleaner.analyze_missing_data(raw_df)
        print(
            f"Missing data analysis: {missing_analysis['missing_values'].sum()} total missing values")

        # Handle missing data
        df_clean = cleaner.handle_missing_data(raw_df, method='multiple')

        # Treat outliers
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean = cleaner.treat_outliers(
            df_clean, columns=numeric_cols, method='cap')

        # Validate data quality
        quality_report = cleaner.validate_data_quality(df_clean)

        cleaned_data[symbol] = df_clean

        print(
            f"Cleaning complete. Original: {len(raw_df)} records, Cleaned: {len(df_clean)} records")

    # Generate comprehensive report
    cleaner.generate_cleaning_report()

    # Plot results for first symbol
    first_symbol = list(data.keys())[0]
    cleaner.plot_data_quality(cleaned_data[first_symbol], data[first_symbol])

    return cleaned_data


if __name__ == "__main__":
    demonstrate_data_cleaning()
