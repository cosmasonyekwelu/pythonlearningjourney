"""
Data Validation and Quality Checks
Comprehensive validation for financial data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re


class FinancialDataValidator:
    """
    Validate financial data quality and integrity
    """

    def __init__(self):
        self.validation_results = {}

    def validate_numeric_ranges(self, df, column_rules=None):
        """
        Validate numeric columns against expected ranges
        """
        if column_rules is None:
            column_rules = {
                'Close': {'min': 0, 'max': 10000},
                'Volume': {'min': 0, 'max': 1e12},
                'returns': {'min': -1, 'max': 1},
                'Open': {'min': 0, 'max': 10000},
                'High': {'min': 0, 'max': 10000},
                'Low': {'min': 0, 'max': 10000}
            }

        violations = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in column_rules:
                rules = column_rules[col]
                col_violations = {}

                if 'min' in rules:
                    below_min = df[col] < rules['min']
                    if below_min.any():
                        col_violations['below_min'] = below_min.sum()

                if 'max' in rules:
                    above_max = df[col] > rules['max']
                    if above_max.any():
                        col_violations['above_max'] = above_max.sum()

                if col_violations:
                    violations[col] = col_violations

        self.validation_results['numeric_ranges'] = violations
        return violations

    def validate_temporal_consistency(self, df, date_column=None):
        """
        Validate temporal consistency of time series data
        """
        violations = {}

        if date_column and date_column in df.columns:
            dates = pd.to_datetime(df[date_column])
        elif hasattr(df.index, 'dtype') and np.issubdtype(df.index.dtype, np.datetime64):
            dates = df.index
        else:
            print("No datetime index or column found")
            return violations

        # Check for monotonic increasing dates
        if not dates.is_monotonic_increasing:
            violations['non_monotonic_dates'] = "Dates are not strictly increasing"

        # Check for gaps in time series
        date_diffs = dates.to_series().diff().dropna()
        if not date_diffs.empty:
            common_freq = date_diffs.mode()
            if len(common_freq) > 0:
                expected_freq = common_freq.iloc[0]
                large_gaps = date_diffs > expected_freq * 2
                if large_gaps.any():
                    violations['time_gaps'] = large_gaps.sum()

        # Check for duplicate dates
        duplicate_dates = dates.duplicated()
        if duplicate_dates.any():
            violations['duplicate_dates'] = duplicate_dates.sum()

        self.validation_results['temporal_consistency'] = violations
        return violations

    def validate_business_rules(self, df):
        """
        Validate financial business rules
        """
        violations = {}

        # High should be >= Low
        if 'High' in df.columns and 'Low' in df.columns:
            high_low_violation = df['High'] < df['Low']
            if high_low_violation.any():
                violations['high_low_inversion'] = high_low_violation.sum()

        # High should be >= Open and Close
        if 'High' in df.columns and 'Open' in df.columns:
            high_open_violation = df['High'] < df['Open']
            if high_open_violation.any():
                violations['high_below_open'] = high_open_violation.sum()

        if 'High' in df.columns and 'Close' in df.columns:
            high_close_violation = df['High'] < df['Close']
            if high_close_violation.any():
                violations['high_below_close'] = high_close_violation.sum()

        # Low should be <= Open and Close
        if 'Low' in df.columns and 'Open' in df.columns:
            low_open_violation = df['Low'] > df['Open']
            if low_open_violation.any():
                violations['low_above_open'] = low_open_violation.sum()

        if 'Low' in df.columns and 'Close' in df.columns:
            low_close_violation = df['Low'] > df['Close']
            if low_close_violation.any():
                violations['low_above_close'] = low_close_violation.sum()

        # Volume should be non-negative
        if 'Volume' in df.columns:
            negative_volume = df['Volume'] < 0
            if negative_volume.any():
                violations['negative_volume'] = negative_volume.sum()

        self.validation_results['business_rules'] = violations
        return violations

    def validate_data_completeness(self, df, required_columns=None):
        """
        Validate data completeness and required columns
        """
        if required_columns is None:
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        violations = {}

        # Check for required columns
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            violations['missing_columns'] = missing_columns

        # Check for completely empty columns
        empty_columns = df.columns[df.isnull().all()].tolist()
        if empty_columns:
            violations['empty_columns'] = empty_columns

        # Check for high percentage of missing values
        missing_pct = (df.isnull().sum() / len(df)) * 100
        high_missing = missing_pct[missing_pct > 50].to_dict()
        if high_missing:
            violations['high_missing_pct'] = high_missing

        self.validation_results['completeness'] = violations
        return violations

    def validate_statistical_properties(self, df):
        """
        Validate statistical properties of financial data
        """
        violations = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            col_violations = {}
            series = df[col].dropna()

            if len(series) < 2:
                continue

            # Check for constant values (no variation)
            if series.std() == 0:
                col_violations['constant_values'] = True

            # Check for extreme skewness
            skewness = series.skew()
            if abs(skewness) > 5:  # Arbitrary threshold
                col_violations['extreme_skewness'] = skewness

            # Check for extreme kurtosis
            kurtosis = series.kurtosis()
            if abs(kurtosis) > 10:  # Arbitrary threshold
                col_violations['extreme_kurtosis'] = kurtosis

            if col_violations:
                violations[col] = col_violations

        self.validation_results['statistical_properties'] = violations
        return violations

    def comprehensive_validation(self, df, symbol=None):
        """
        Perform comprehensive data validation
        """
        print(f"Validating data{' for ' + symbol if symbol else ''}...")

        validation_report = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'basic_stats': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'data_types': df.dtypes.to_dict()
            },
            'validations': {}
        }

        # Run all validation checks
        validation_report['validations']['numeric_ranges'] = self.validate_numeric_ranges(
            df)
        validation_report['validations']['temporal_consistency'] = self.validate_temporal_consistency(
            df)
        validation_report['validations']['business_rules'] = self.validate_business_rules(
            df)
        validation_report['validations']['completeness'] = self.validate_data_completeness(
            df)
        validation_report['validations']['statistical_properties'] = self.validate_statistical_properties(
            df)

        # Calculate overall quality score
        total_violations = sum(len(v)
                               for v in validation_report['validations'].values())
        max_possible_violations = len(df.columns) * 5  # Rough estimate
        quality_score = max(0, 100 - (total_violations /
                            max(1, max_possible_violations) * 100))
        validation_report['quality_score'] = quality_score

        self.validation_results = validation_report
        return validation_report

    def generate_validation_report(self, validation_report=None):
        """
        Generate human-readable validation report
        """
        if validation_report is None:
            validation_report = self.validation_results

        print("\n" + "=" * 60)
        print("DATA VALIDATION REPORT")
        print("=" * 60)

        if 'symbol' in validation_report:
            print(f"Symbol: {validation_report['symbol']}")

        print(f"Timestamp: {validation_report.get('timestamp', 'N/A')}")
        print(
            f"Quality Score: {validation_report.get('quality_score', 0):.1f}/100")

        basic_stats = validation_report.get('basic_stats', {})
        print(f"\nBasic Statistics:")
        print(f"  Rows: {basic_stats.get('total_rows', 0)}")
        print(f"  Columns: {basic_stats.get('total_columns', 0)}")
        print(
            f"  Memory: {basic_stats.get('memory_usage', 0) / 1024 / 1024:.2f} MB")

        validations = validation_report.get('validations', {})

        print(f"\nVALIDATION RESULTS:")
        for check_type, results in validations.items():
            print(f"\n{check_type.replace('_', ' ').title()}:")
            if not results:
                print("  ✓ No violations")
            else:
                for violation, details in results.items():
                    if isinstance(details, dict):
                        print(f"  ✗ {violation}:")
                        for sub_violation, count in details.items():
                            print(f"    - {sub_violation}: {count}")
                    else:
                        print(f"  ✗ {violation}: {details}")

        # Overall assessment
        quality_score = validation_report.get('quality_score', 0)
        if quality_score >= 90:
            assessment = "EXCELLENT"
        elif quality_score >= 75:
            assessment = "GOOD"
        elif quality_score >= 60:
            assessment = "FAIR"
        else:
            assessment = "POOR"

        print(f"\nOVERALL ASSESSMENT: {assessment}")
        print(
            f"Data is {'READY' if quality_score >= 70 else 'NOT READY'} for analysis")


def demonstrate_validation():
    """
    Demonstrate data validation capabilities
    """
    print("Financial Data Validation Demonstration")
    print("=" * 50)

    validator = FinancialDataValidator()

    # Create sample data with known issues
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    sample_data = pd.DataFrame({
        'Open': np.random.normal(100, 2, 50),
        'High': np.random.normal(102, 3, 50),
        'Low': np.random.normal(98, 3, 50),
        'Close': np.random.normal(100, 2, 50),
        'Volume': np.random.lognormal(10, 1, 50)
    }, index=dates)

    # Introduce some validation issues
    sample_data.loc[5, 'High'] = 50  # High below Low
    sample_data.loc[10, 'Volume'] = -100  # Negative volume
    sample_data.loc[15, 'Open'] = 1000  # Extreme value
    sample_data.loc[20:25, 'Close'] = np.nan  # Missing values

    # Perform comprehensive validation
    validation_report = validator.comprehensive_validation(
        sample_data, symbol='TEST')

    # Generate report
    validator.generate_validation_report(validation_report)

    return validator, sample_data


if __name__ == "__main__":
    demonstrate_validation()
