# Day 34: Data Cleaning & Preprocessing Pipeline

**Date:** October 25, 2025

## Learning Objective
To build a production-ready data preprocessing pipeline that handles cleaning, outlier treatment, feature engineering, and validation for machine learning.

## Concepts Covered
- **Missing Data Handling**: Using multiple imputation strategies (mean, median, ffill).
- **Outlier Treatment**: Using the IQR method to cap or remove extreme values.
- **Feature Engineering**: Creating technical indicators, price lags, and derived percentage changes.
- **Data Scaling**: Normalizing features for better performance in ML models.
- **Validation**: Implementing checks for data type consistency, range limits, and statistical sanity.

## Code Explanation
The `day_thirtyfour.py` script integrates several components:
- **`FinancialDataCleaner`**: Detects and fixes "holes" in the historical price data.
- **`FinancialFeatureEngineer`**: Generates a rich set of 20+ features from basic OHLCV data.
- **`FinancialPreprocessingPipeline`**: A high-level class that can process entire portfolios of stocks consistently.
- **`FinancialDataValidator`**: Produces a quality report ensuring the output data is safe for model training.

## How to Run
1. Ensure the `data/sample_stocks.csv` file exists (or run Day 30 to generate some).
2. Run the pipeline:
```bash
python week_05/daythirtyfour/day_thirtyfour.py
```

## Reflection
"Garbage in, garbage out" is the golden rule of machine learning. A robust preprocessing pipeline is the most critical component of any data-driven trading system.
