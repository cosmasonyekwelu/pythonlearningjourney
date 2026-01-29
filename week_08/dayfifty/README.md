# Day 50: Financial Exploratory Data Analysis (EDA)

**Date:** November 10, 2025

## Learning Objective
To master the techniques of Exploratory Data Analysis (EDA) specifically for financial time-series data, focusing on quality, distributions, and volatility.

## Concepts Covered
- **Data Quality Assessment**: Identifying missing values, duplicates, and outliers in market data.
- **Return Distributions**: Analyzing the statistical properties of daily returns (Skewness, Kurtosis).
- **Correlation Analysis**: Visualizing relationships between different assets using heatmaps.
- **Time Series Decomposition**: Breaking down prices into trend, seasonality, and residuals.
- **Volatility Clustering**: Observing how volatility changes over time using rolling windows.

## Code Explanation
The `day_fifty.py` script implements the `FinancialEDA` class:
- **`load_data()`**: Fetches historical data using `yfinance` and calculates log returns.
- **`data_quality_report()`**: Provides a summary of the dataset's integrity.
- **`plot_returns_distribution()`**: Generates histograms and Q-Q plots to compare returns against a normal distribution.
- **`time_series_decomposition()`**: Uses `statsmodels` to extract the underlying components of a price series.
- **`run_eda_challenge()`**: A multi-asset comparison task for SPY, QQQ, GLD, and BTC.

## How to Run
1. Install dependencies: `pip install pandas numpy matplotlib seaborn yfinance statsmodels scipy`
2. Run the EDA tool:
```bash
python week_08/dayfifty/day_fifty.py
```

## Reflection
Financial data is "messy"—it often has "fat tails" (kurtosis) and volatility clusters. Standard linear models often fail because market data is rarely normally distributed. EDA is the first step in recognizing these patterns before building predictive models.
