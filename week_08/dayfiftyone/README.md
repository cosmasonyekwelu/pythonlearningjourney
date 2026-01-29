# Day 51: Statistical Analysis for Trading

**Date:** November 11, 2025

## Learning Objective
To apply rigorous statistical tests to financial data to validate stationarity, normality, and the random walk hypothesis.

## Concepts Covered
- **Stationarity Testing**: Using the Augmented Dickey-Fuller (ADF) test to ensure data is suitable for time-series modeling.
- **Normality Tests**: Implementing Shapiro-Wilk and Jarque-Bera tests to analyze the distribution of returns.
- **Autocorrelation (ACF/PACF)**: Identifying serial correlation in price movements and returns.
- **Volatility Modeling**: Introduction to GARCH (Generalized Autoregressive Conditional Heteroskedasticity) models.
- **Hypothesis Testing**: Using t-tests and Variance Ratio tests to evaluate the Efficient Market Hypothesis (EMH).

## Code Explanation
The `day_fiftyone.py` script implements the `StatisticalAnalysis` class:
- **`stationarity_test()`**: Runs the ADF test and interprets the p-value.
- **`autocorrelation_analysis()`**: Plots ACF and PACF graphs to identify significant lags.
- **`volatility_modeling()`**: Uses the `arch` library to fit a GARCH(1,1) model to stock returns.
- **`risk_return_metrics()`**: Calculates professional stats like Sharpe Ratio, VaR (Value at Risk), and CVaR.

## How to Run
1. Install requirements: `pip install pandas numpy matplotlib seaborn yfinance arch statsmodels`
2. Run the statistical suite:
```bash
python week_08/dayfiftyone/day_fiftyone.py
```

## Reflection
Trading is a game of probabilities. Rigorous statistical analysis helps separate signal from noise, ensuring that a perceived "trend" isn't just a random fluctuation in a non-stationary series.
