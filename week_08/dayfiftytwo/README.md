# Day 52: Feature Engineering

## Overview

Transform raw time-series data into **informative, predictive features** for machine learning models.

## Feature Categories Implemented

### 1. Technical Indicators

- **Momentum**: RSI, Stochastic, Williams %R, ROC
- **Trend**: MACD, ADX, CCI
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, VWAP

### 2. Rolling Statistics

- Multiple time windows (5, 10, 20, 50 days)
- Rolling means, standard deviations, min/max
- Z-scores and price ratios
- High/Low ratios relative to rolling windows

### 3. Lag Features

- Lagged returns, volume, and technical indicators
- Price and volume momentum ratios
- Multiple lag periods (1, 2, 3, 5, 10 days)

### 4. Volatility Features

- Realized volatility at different horizons
- Parkinson volatility (using high-low range)
- Volatility ratios and regimes
- Conditional volatility features

### 5. Temporal Features

- Day of week, month, quarter
- Seasonal patterns using trigonometric encoding
- Calendar effects (month start/end, quarter start/end)

### 6. Custom Mean Reversion Indicators

- Multiple time frame mean reversion signals
- RSI-based mean reversion
- Bollinger Band position signals
- Combined mean reversion score

## Challenge: Custom Mean Reversion Indicator

The script implements and evaluates a sophisticated mean reversion indicator that:

1. **Combines Multiple Time Frames**: Uses short (5,10) and long (20,50) windows
2. **Multiple Signal Types**: Price deviation, Z-scores, RSI, Bollinger Bands
3. **Regime Awareness**: Different behavior in high/low volatility periods
4. **Predictive Power Analysis**: Correlation with future returns

## Key Insights

1. **Feature Diversity**: No single feature type dominates; combination is key
2. **Time Horizon Matters**: Different features work for different prediction horizons
3. **Regime Dependency**: Feature effectiveness varies with market conditions
4. **Normalization Importance**: Proper scaling crucial for model performance

## Usage

```python
# Complete pipeline
engineer = FeatureEngineer()
final_data, feature_names = engineer.build_feature_pipeline('SPY')

# Individual components
engineer.add_technical_indicators()
engineer.add_rolling_statistics()
mr_signal = engineer.create_custom_mean_reversion_indicator()
```
