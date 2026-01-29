# Day 33: Advanced Time Series Analysis

**Date:** October 24, 2025

## Learning Objective
To master advanced statistical modeling for time series, including stationarity testing, ARIMA forecasting, and GARCH volatility modeling.

## Concepts Covered
- **Stationarity**: Using ADF and KPSS tests to determine if a time series has a constant mean and variance.
- **Seasonal Decomposition**: Breaking down a stock's price into Trend, Seasonality, and Residual components.
- **ARIMA Modeling**: Building AutoRegressive Integrated Moving Average models for price prediction.
- **GARCH Modeling**: Forecasting future volatility clusters and calculating Value at Risk (VaR).
- **Backtesting**: Evaluating the accuracy of historical forecasts against actual data.

## Code Explanation
The `day_thirtythree.py` script is a high-level orchestrator for several specialized modules:
- **`StationarityAnalyzer`**: Performs statistical tests and plots ACF/PACF.
- **`ARIMAModeler`**: Automatically finds the optimal (p, d, q) order for a price series.
- **`GARCHModeler`**: Estimates volatility and provides annualized risk forecasts.
- **`TimeSeriesForecastingSystem`**: Creates an ensemble of models to improve prediction robustness.

## How to Run
1. Install requirements: `pip install pandas numpy yfinance statsmodels arch matplotlib`
2. Run the full analysis:
```bash
python week_05/daythirtythree/day_thirtythree.py
```

## Reflection
Financial data is non-stationary and heteroscedastic (volatility changes over time). Learning to use ARIMA and GARCH allows us to model these complex real-world behaviors much more accurately than simple linear regressions.
