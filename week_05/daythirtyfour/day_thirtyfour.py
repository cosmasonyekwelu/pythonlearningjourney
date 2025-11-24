"""
Day 34 - Data Cleaning & Preprocessing
Main execution script that integrates data cleaning, feature engineering,
preprocessing pipeline, and validation into a unified workflow.
"""

import pandas as pd
import numpy as np
import os
from data_cleaner import FinancialDataCleaner
from feature_engineer import FinancialFeatureEngineer
from preprocessing_pipeline import FinancialPreprocessingPipeline
from data_validation import FinancialDataValidator


def main():
    print("=" * 70)
    print("DAY 34 - DATA CLEANING & PREPROCESSING PIPELINE")
    print("=" * 70)

    # Load sample dataset
    data_path = os.path.join("data", "sample_stocks.csv")
    print(f"\nLoading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    # Convert date to datetime and set index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    print("Converted 'date' column to datetime index.")

    # 1️ Data Cleaning
    print("\nSTEP 1: Data Cleaning")
    cleaner = FinancialDataCleaner()

    # Analyze missing data
    missing_analysis = cleaner.analyze_missing_data(df)
    print("Missing Data Summary:")
    print(missing_analysis['missing_values'])

    # Handle missing data
    df_clean = cleaner.handle_missing_data(df, method='multiple')

    # Treat outliers
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    df_clean = cleaner.treat_outliers(
        df_clean, columns=numeric_cols, method='cap')

    # Validate cleaned data
    quality_report = cleaner.validate_data_quality(df_clean)
    cleaner.generate_cleaning_report()

    # 2️ Feature Engineering
    print("\nSTEP 2: Feature Engineering")
    engineer = FinancialFeatureEngineer()

    # Create price-based, technical, and derived features
    df_features = engineer.create_price_features(
        df_clean, price_column='close')
    df_features = engineer.create_technical_indicators(
        df_features, price_column='close', volume_column='volume')
    df_features = engineer.create_derived_features(df_features)
    df_features = engineer.scale_features(df_features)

    # Generate summary of features
    feature_summary = engineer.create_feature_summary(df_features)
    print("\nFeature Engineering Summary:")
    print(f"Total features: {feature_summary['total_features']}")
    print(f"Numeric features: {feature_summary['numeric_features']}")
    print(f"Categorical features: {feature_summary['categorical_features']}")

    # 3️ Preprocessing Pipeline
    print("\nSTEP 3: Preprocessing Pipeline")
    pipeline = FinancialPreprocessingPipeline()
    pipeline.create_pipeline()

    # Use the pipeline to process multiple symbols
    symbols = ['AAPL', 'GOOGL']
    print(f"Processing portfolio: {symbols}")
    portfolio_data = pipeline.process_portfolio(symbols, period='1mo')

    # Create ML training dataset
    X, y, feature_names = pipeline.create_training_dataset(
        portfolio_data,
        target_column='returns',
        lookback_days=5,
        forecast_days=2
    )

    if X is not None:
        print(f"\nTraining Dataset Created:")
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        print(f"Feature count: {len(feature_names)}")
    else:
        print("\nNo training dataset could be generated (check data availability).")

    # 4️ Data Validation
    print("\nSTEP 4: Data Validation")
    validator = FinancialDataValidator()

    # Perform validation on one of the processed datasets
    if portfolio_data:
        symbol = list(portfolio_data.keys())[0]
        df_to_validate = portfolio_data[symbol]
        validation_report = validator.comprehensive_validation(
            df_to_validate, symbol=symbol)
        validator.generate_validation_report(validation_report)
    else:
        print("No processed data found for validation.")

    print("\nPipeline execution completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
