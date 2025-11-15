# Day 51: Statistical Analysis for Trading

## Overview

Use statistical methods to validate trading hypotheses and detect underlying market structures.

## Key Statistical Tests and Methods

### 1. Stationarity Analysis

- **Augmented Dickey-Fuller (ADF) Test**: Determines if price series are stationary
- **Returns vs Prices**: Returns are typically stationary while prices are not
- **Implications**: Stationary series are required for many statistical models

### 2. Normality Testing

- **Shapiro-Wilk Test**: Formal test for normality
- **Jarque-Bera Test**: Tests both skewness and kurtosis
- **Q-Q Plots**: Visual normality assessment
- **Key Insight**: Financial returns are rarely normal (exhibit fat tails)

### 3. Autocorrelation Analysis

- **ACF/PACF Plots**: Identify serial correlation patterns
- **Significant Lags**: Detect predictable patterns in returns
- **Market Efficiency**: Random walk hypothesis testing

### 4. Volatility Modeling

- **GARCH Models**: Capture volatility clustering
- **Model Comparison**: AIC/BIC for model selection
- **Conditional Volatility**: Time-varying risk assessment

### 5. Hypothesis Testing

- **One-sample t-test**: Test if mean returns are zero
- **Two-sample t-test**: Compare different return series
- **Variance Ratio Test**: Test random walk hypothesis
- **Confidence Intervals**: Range estimation for parameters

### 6. Risk-Return Metrics

- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst-case loss
- **Value at Risk (VaR)**: Tail risk measurement
- **Expected Shortfall**: Conditional VaR

## Key Findings from Financial Data

1. **Non-Stationarity**: Price series are non-stationary, returns are stationary
2. **Non-Normality**: Returns exhibit fat tails and skewness
3. **Volatility Clustering**: High volatility periods cluster together
4. **Weak Autocorrelation**: Some short-term predictability may exist
5. **Risk-Return Tradeoff**: Higher returns typically come with higher volatility

## Challenge: Volatility Analysis

The script includes advanced volatility analysis comparing:

- Different GARCH model specifications
- Rolling volatility vs conditional volatility
- Volatility regime identification
- Clustering pattern visualization

## Usage

```python
# Complete analysis
analyzer = StatisticalAnalysis()
analyzer.run_complete_analysis('SPY')

# Individual tests
analyzer.stationarity_test()
analyzer.normality_tests()
analyzer.volatility_modeling(p=1, q=1)
```
