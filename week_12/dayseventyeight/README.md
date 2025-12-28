# Day 78: Performance Metrics & Analytics

## Objective

Implement comprehensive performance analytics beyond basic metrics, including attribution analysis, drawdown decomposition, and multi-factor risk models.

## Core Concepts

- Advanced Performance Metrics: Modified Sharpe ratio, Omega ratio, Kappa ratios, pain index, ulcer index, and other drawdown-based risk measures
- Drawdown Analysis: Decomposing maximum drawdown into constituent losses and recovery periods, Conditional Value-at-Risk (CVaR) for tail risk assessment
- Multi-Factor Risk Models: Factor exposure analysis using style factors (value, momentum, volatility), benchmark-relative performance attribution
- Performance Attribution: Brinson-Fachler attribution for multi-asset portfolios, timing vs. selection skill decomposition, transaction cost impact analysis

## Tutorial: Comprehensive Performance Analyzer

This tutorial builds a professional-grade performance analyzer that calculates 50+ metrics with statistical significance testing, generates detailed attribution reports, and provides interactive visualizations.

```python
from performance_analyzer import AdvancedPerformanceAnalyzer, MultiFactorRiskModel
import numpy as np
import pandas as pd
import yfinance as yf

# Download historical data for analysis
def download_market_data():
    tickers = ['SPY', 'QQQ', 'IWM', 'EEM', 'TLT']
    data = yf.download(tickers, start='2020-01-01', end='2023-12-31')
    returns = data['Adj Close'].pct_change().dropna()
    return returns

# Generate synthetic strategy returns
def generate_strategy_returns(benchmark_returns, alpha=0.0005, beta=0.8, idiosyncratic_vol=0.008):
    n_days = len(benchmark_returns)
    market_component = benchmark_returns.values.flatten() * beta
    idiosyncratic = np.random.normal(alpha, idiosyncratic_vol, n_days)
    strategy_returns = market_component + idiosyncratic
    return pd.Series(strategy_returns, index=benchmark_returns.index, name='strategy')

# Main analysis
if __name__ == "__main__":
    # Load data
    market_data = download_market_data()
    spy_returns = market_data['SPY']

    # Generate strategy returns
    strategy_returns = generate_strategy_returns(spy_returns)

    # Initialize analyzer
    analyzer = AdvancedPerformanceAnalyzer(
        returns=strategy_returns,
        benchmark_returns=spy_returns,
        risk_free_rate=0.02
    )

    # Calculate comprehensive metrics
    print("Performance Analysis Results")
    print("=" * 60)

    basic_metrics = analyzer.calculate_basic_metrics()
    print("\nBasic Performance Metrics:")
    print("-" * 40)
    for metric, value in basic_metrics.items():
        if isinstance(value, (int, float)):
            print(f"{metric:25}: {value:.4f}")

    advanced_metrics = analyzer.calculate_advanced_metrics()
    print("\nAdvanced Performance Metrics:")
    print("-" * 40)
    for metric, value in advanced_metrics.items():
        if value is not None:
            print(f"{metric:25}: {value:.4f}")

    # Generate detailed report
    report = analyzer.generate_performance_report()
    print(f"\nPerformance Summary: {report['overall_assessment']}")

    # Create visualizations
    analyzer.plot_performance_summary(save_path='performance_summary.png')
    print("\nVisualizations saved to 'performance_summary.png'")

    # Factor attribution analysis
    risk_model = MultiFactorRiskModel()
    factors_data = {
        'market': spy_returns,
        'size': market_data['IWM'] - spy_returns,  # Size factor (small cap - market)
        'value': market_data['EEM'] - spy_returns,  # Value factor (emerging markets - market)
        'momentum': market_data['QQQ'] - spy_returns  # Momentum factor (tech - market)
    }

    attribution = risk_model.analyze(strategy_returns, factors_data)
    print(f"\nFactor Attribution R-squared: {attribution['r_squared']:.3f}")
    print("Factor Contributions:")
    for factor, contribution in attribution['factor_contributions'].items():
        print(f"  {factor:15}: {contribution:.4f}")
```

The analyzer calculates over 50 performance metrics including risk-adjusted returns, drawdown analysis, and factor attribution. Key features include statistical significance testing, regime-based analysis, and comprehensive visualization capabilities.

## Challenge: Multi-Factor Risk Model Implementation

Implement a multi-factor risk model that decomposes strategy returns into market, style, and specific components, identifying hidden risk exposures.

```python
class EnhancedRiskModel:
    """
    Enhanced multi-factor risk model with time-varying factor exposures
    and regime detection.
    """

    def __init__(self):
        self.factors = {}
        self.rolling_betas = {}
        self.regime_indicators = {}

    def estimate_time_varying_exposures(self, strategy_returns, factor_returns,
                                        window=63, method='kalman'):
        """
        Estimate time-varying factor exposures using rolling regression
        or Kalman filtering.

        Parameters:
        -----------
        strategy_returns : pd.Series
            Strategy returns
        factor_returns : dict
            Dictionary of factor return Series
        window : int
            Rolling window size for regression
        method : str
            Estimation method ('rolling', 'kalman', 'ewma')
        """
        # Implementation for rolling window approach
        if method == 'rolling':
            betas = {}
            for factor_name, factor_series in factor_returns.items():
                rolling_beta = []
                for i in range(window, len(strategy_returns)):
                    # Rolling regression
                    X = factor_series.iloc[i-window:i].values.reshape(-1, 1)
                    y = strategy_returns.iloc[i-window:i].values
                    # Simple OLS
                    beta = np.linalg.lstsq(X, y, rcond=None)[0][0]
                    rolling_beta.append(beta)

                betas[factor_name] = pd.Series(rolling_beta,
                                               index=strategy_returns.index[window:])

            self.rolling_betas = betas

        # Add Kalman filter implementation for more sophisticated tracking
        elif method == 'kalman':
            # Kalman filter implementation for time-varying parameters
            pass

        return self.rolling_betas

    def identify_regime_changes(self, strategy_returns, method='hidden_markov'):
        """
        Identify market regimes using statistical methods.

        Parameters:
        -----------
        strategy_returns : pd.Series
            Strategy returns for regime detection
        method : str
            Detection method ('hidden_markov', 'volatility_regime', 'clustering')
        """
        # Implementation using volatility regimes
        if method == 'volatility_regime':
            rolling_vol = strategy_returns.rolling(window=21).std()
            # Simple threshold-based regime detection
            high_vol_threshold = rolling_vol.quantile(0.75)
            low_vol_threshold = rolling_vol.quantile(0.25)

            regimes = pd.Series('normal', index=strategy_returns.index)
            regimes[rolling_vol > high_vol_threshold] = 'high_volatility'
            regimes[rolling_vol < low_vol_threshold] = 'low_volatility'

            self.regime_indicators = regimes

        return self.regime_indicators

    def analyze_regime_specific_exposures(self, strategy_returns, factor_returns):
        """
        Analyze factor exposures in different market regimes.
        """
        # First identify regimes
        regimes = self.identify_regime_changes(strategy_returns)

        # Calculate factor exposures by regime
        regime_exposures = {}
        for regime in regimes.unique():
            regime_mask = regimes == regime
            regime_strategy_returns = strategy_returns[regime_mask]

            exposures = {}
            for factor_name, factor_series in factor_returns.items():
                regime_factor_returns = factor_series[regime_mask]
                # Simple correlation in this regime
                if len(regime_strategy_returns) > 10:  # Minimum observations
                    correlation = regime_strategy_returns.corr(regime_factor_returns)
                    exposures[factor_name] = correlation

            regime_exposures[regime] = exposures

        return regime_exposures

# Next steps for the challenge:
# 1. Implement Bayesian regression for factor exposure estimation with uncertainty
# 2. Add copula-based dependency modeling between factors
# 3. Create regime-switching factor models
# 4. Implement out-of-sample testing for factor model stability
# 5. Add economic interpretation of factor exposures and their implications
```

The challenge extends the basic factor model to include time-varying exposures, regime detection, and more sophisticated statistical methods. Implement Bayesian regression for uncertainty quantification and regime-switching models for different market conditions.

```

```
