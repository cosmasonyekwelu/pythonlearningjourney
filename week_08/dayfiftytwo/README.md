# Day 52: Feature Engineering for Financial ML

**Date:** November 12, 2025

## Learning Objective
To create a high-dimensional feature set from raw market data, transforming prices into predictive inputs for machine learning models.

## Concepts Covered
- **Technical Indicators**: Using the `ta` library to generate RSI, MACD, Bollinger Bands, and Ichimoku features.
- **Rolling Statistics**: Calculating z-scores and price ratios over multiple time horizons.
- **Lag Features**: Creating shifted time-series data to capture historical momentum.
- **Advanced Volatility**: Implementing Parkinson Volatility and realized volatility ratios.
- **Predictive Power Evaluation**: Using correlation analysis to identify features that actually lead future returns.

## Code Explanation
The `day_fiftytwo.py` script implements the `FeatureEngineer` class:
- **`add_technical_indicators()`**: Injects 15+ classic signals into the dataset.
- **`add_volatility_features()`**: Compares short-term vs. long-term volatility regimes.
- **`create_custom_mean_reversion_indicator()`**: A proprietary signal that combines RSI, BB, and multi-timeframe MA deviations.
- **`normalize_features()`**: Uses `StandardScaler` to prepare the data for ML algorithms.

## How to Run
1. Install dependencies: `pip install pandas numpy matplotlib seaborn yfinance ta scikit-learn`
2. Run the pipeline:
```bash
python week_08/dayfiftytwo/day_fiftytwo.py
```

## Reflection
Raw price data is rarely enough for a model to learn from. Feature engineering is the process of extracting the "latent information" in the market—transforming absolute prices into relative signals that a model can generalize from.
