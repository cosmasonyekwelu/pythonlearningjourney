
# Day 79: Walk-Forward and Sensitivity Analysis

## Objective
Implement robust validation frameworks to test strategy stability across time periods and parameter variations, preventing overfitting.

## Core Concepts
* Walk-Forward Optimization: Rolling window analysis with expanding, sliding, and anchored windows, out-of-sample consistency metrics and statistical significance tests
* Parameter Sensitivity Analysis: One-factor-at-a-time (OFAT) and full factorial experimental designs, response surface methodology for parameter optimization
* Overfitting Prevention: Cross-validation techniques adapted for time-series data, minimum backtest length (Prado's formula) calculations, false strategy probability estimation using combinatorics
* Monte Carlo Permutation Tests: Randomizing trade sequences to test strategy significance, bootstrapping returns for confidence interval estimation, strategy comparison using statistical hypothesis testing

## Tutorial: Walk-Forward Analyzer

This tutorial builds a professional walk-forward analysis framework that implements multiple validation schemes, calculates out-of-sample performance metrics, and provides statistical significance testing to prevent overfitting.

```python
from walkforward_analyzer import WalkForwardAnalyzer, ParameterSensitivityAnalyzer
import numpy as np
import pandas as pd

# Generate sample strategy data with parameters
def generate_strategy_with_params(window=20, threshold=0.5):
    """
    Mock strategy that depends on parameters.
    In practice, this would be your actual trading strategy.
    """
    np.random.seed(42)
    dates = pd.date_range('2015-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    
    # Simulate market returns
    market_returns = np.random.normal(0.0003, 0.015, n_dates)
    
    # Strategy logic based on parameters
    signals = []
    for i in range(n_dates):
        if i < window:
            signals.append(0)
        else:
            # Simple momentum strategy
            recent_returns = market_returns[i-window:i].mean()
            if recent_returns > threshold:
                signals.append(1)  # Long
            elif recent_returns < -threshold:
                signals.append(-1)  # Short
            else:
                signals.append(0)  # Neutral
    
    # Strategy returns = signal * market returns + some alpha
    strategy_returns = np.array(signals) * market_returns + np.random.normal(0.0001, 0.005, n_dates)
    
    return pd.Series(strategy_returns, index=dates, name='strategy')

# Main analysis
if __name__ == "__main__":
    # Generate strategy returns with base parameters
    strategy_returns = generate_strategy_with_params(window=20, threshold=0.5)
    
    # Initialize walk-forward analyzer
    analyzer = WalkForwardAnalyzer(
        returns=strategy_returns,
        initial_train_period=252*2,  # 2 years initial training
        test_period=252,             # 1 year testing
        step_size=63,                # Quarterly re-optimization
        window_type='expanding'      # Expanding window
    )
    
    # Run walk-forward analysis
    print("Running walk-forward analysis...")
    wf_results = analyzer.analyze()
    
    # Display results
    print("\nWalk-Forward Analysis Results:")
    print("=" * 60)
    print(f"Number of walk-forward windows: {wf_results['n_windows']}")
    print(f"Average out-of-sample return: {wf_results['average_oos_return']:.4%}")
    print(f"Out-of-sample Sharpe ratio: {wf_results['oos_sharpe']:.3f}")
    print(f"Performance consistency: {wf_results['performance_consistency']:.2%}")
    print(f"Probability of overfitting: {wf_results['overfitting_probability']:.2%}")
    
    # Plot walk-forward performance
    analyzer.plot_walkforward_performance(save_path='walkforward_analysis.png')
    print("\nWalk-forward visualization saved to 'walkforward_analysis.png'")
    
    # Parameter sensitivity analysis
    print("\n" + "=" * 60)
    print("Parameter Sensitivity Analysis")
    print("=" * 60)
    
    sensitivity_analyzer = ParameterSensitivityAnalyzer(
        strategy_function=generate_strategy_with_params,
        param_ranges={
            'window': np.arange(5, 61, 5),      # 5 to 60 days, step 5
            'threshold': np.arange(0.1, 1.1, 0.1)  # 0.1 to 1.0, step 0.1
        }
    )
    
    # Run full factorial analysis
    sensitivity_results = sensitivity_analyzer.analyze()
    
    # Display optimal parameters
    optimal_params = sensitivity_results['optimal_parameters']
    print(f"\nOptimal parameters found:")
    print(f"  Window size: {optimal_params['window']} days")
    print(f"  Threshold: {optimal_params['threshold']:.2f}")
    print(f"  Expected Sharpe ratio: {optimal_params['sharpe']:.3f}")
    
    # Plot response surface
    sensitivity_analyzer.plot_response_surface(save_path='parameter_sensitivity.png')
    print("Parameter sensitivity visualization saved to 'parameter_sensitivity.png'")
    
    # Overfitting diagnostics
    print("\n" + "=" * 60)
    print("Overfitting Diagnostics")
    print("=" * 60)
    
    diagnostics = analyzer.calculate_overfitting_diagnostics()
    print(f"Minimum backtest length (Prado): {diagnostics['minimum_backtest_length']:.0f} days")
    print(f"Probability of false strategy: {diagnostics['false_strategy_probability']:.2%}")
    print(f"Degrees of freedom consumed: {diagnostics['degrees_of_freedom']:.1f}")
    
    if diagnostics['overfitting_warning']:
        print("WARNING: High probability of overfitting detected!")
        print("Recommendations:")
        for rec in diagnostics['recommendations']:
            print(f"  - {rec}")
```

The walk-forward analyzer implements professional-grade validation including statistical significance testing, multiple windowing schemes, and comprehensive overfitting diagnostics. It calculates minimum backtest lengths and false discovery rates to ensure strategy robustness.

## Challenge: Parameter Sensitivity Analyzer with 3D Response Surfaces

Implement a parameter sensitivity analyzer that creates 3D response surfaces and identifies robust parameter regions across different market conditions.

```python
class EnhancedSensitivityAnalyzer:
    """
    Enhanced parameter sensitivity analyzer with 3D visualization
    and robustness testing across market regimes.
    """
    
    def __init__(self, strategy_function, param_ranges, n_regimes=3):
        self.strategy_function = strategy_function
        self.param_ranges = param_ranges
        self.n_regimes = n_regimes
        self.results_by_regime = {}
        
    def identify_market_regimes(self, market_data):
        """
        Identify different market regimes using clustering or
        statistical methods.
        
        Parameters:
        -----------
        market_data : pd.Series
            Market returns for regime identification
        """
        from sklearn.cluster import KMeans
        
        # Create features for regime identification
        features = pd.DataFrame({
            'returns': market_data,
            'volatility': market_data.rolling(21).std(),
            'skewness': market_data.rolling(63).skew()
        }).dropna()
        
        # Scale features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Cluster into regimes
        kmeans = KMeans(n_clusters=self.n_regimes, random_state=42)
        regime_labels = kmeans.fit_predict(features_scaled)
        
        # Map back to original index
        regimes = pd.Series(regime_labels, index=features.index)
        
        # Characterize each regime
        regime_stats = {}
        for regime in range(self.n_regimes):
            regime_mask = regimes == regime
            regime_data = market_data.loc[regime_mask.index[regime_mask]]
            regime_stats[regime] = {
                'mean_return': regime_data.mean(),
                'volatility': regime_data.std(),
                'n_observations': len(regime_data)
            }
        
        return regimes, regime_stats
    
    def analyze_regime_specific_sensitivity(self, market_returns):
        """
        Analyze parameter sensitivity in different market regimes.
        
        Parameters:
        -----------
        market_returns : pd.Series
            Market returns for regime analysis
        """
        # Identify regimes
        regimes, regime_stats = self.identify_market_regimes(market_returns)
        
        # Analyze each regime
        for regime in range(self.n_regimes):
            regime_mask = regimes == regime
            regime_dates = regimes.index[regime_mask]
            
            # We need to modify the strategy function to work with
            # regime-specific data. In practice, this would involve
            # running the strategy only on dates in this regime.
            
            # This is a placeholder - actual implementation would
            # require strategy to accept date ranges
            print(f"Analyzing regime {regime}:")
            print(f"  Mean return: {regime_stats[regime]['mean_return']:.4%}")
            print(f"  Volatility: {regime_stats[regime]['volatility']:.4%}")
            print(f"  Observations: {regime_stats[regime]['n_observations']}")
            
            # For demonstration, we'll analyze sensitivity on the
            # full dataset but this would be regime-specific in practice
            
            # The key insight is that optimal parameters may differ
            # across market regimes
            # Robust parameters perform well across multiple regimes
    
    def create_3d_response_surface(self, param1_name, param2_name, 
                                  performance_metric='sharpe'):
        """
        Create 3D response surface visualization.
        
        Parameters:
        -----------
        param1_name : str
            First parameter for x-axis
        param2_name : str
            Second parameter for y-axis
        performance_metric : str
            Performance metric for z-axis
        """
        import numpy as np
        import plotly.graph_objects as go
        
        # Generate parameter grid
        param1_values = self.param_ranges[param1_name]
        param2_values = self.param_ranges[param2_name]
        
        # Initialize results matrix
        results_matrix = np.zeros((len(param1_values), len(param2_values)))
        
        # Evaluate strategy for each parameter combination
        for i, p1 in enumerate(param1_values):
            for j, p2 in enumerate(param2_values):
                # Run strategy with these parameters
                strategy_returns = self.strategy_function(
                    **{param1_name: p1, param2_name: p2}
                )
                
                # Calculate performance metric
                if performance_metric == 'sharpe':
                    sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
                    results_matrix[i, j] = sharpe
        
        # Create 3D surface plot
        X, Y = np.meshgrid(param1_values, param2_values)
        
        fig = go.Figure(data=[
            go.Surface(
                x=X,
                y=Y,
                z=results_matrix.T,
                colorscale='RdYlGn',
                opacity=0.8
            )
        ])
        
        fig.update_layout(
            title=f'3D Response Surface: {param1_name} vs {param2_name}',
            scene=dict(
                xaxis_title=param1_name,
                yaxis_title=param2_name,
                zaxis_title=performance_metric
            )
        )
        
        return fig
    
    def identify_robust_parameter_regions(self, stability_threshold=0.8):
        """
        Identify parameter regions that are robust to small changes.
        
        Parameters:
        -----------
        stability_threshold : float
            Minimum performance stability score (0-1)
        """
        # This method would identify parameter combinations where
        # small changes in parameters don't cause large performance drops
        
        # Implementation steps:
        # 1. Calculate performance gradient for each parameter
        # 2. Identify regions with low gradient (flat response surface)
        # 3. Calculate robustness score for each parameter combination
        # 4. Return parameters with high robustness scores
        
        robust_params = []
        
        # For each parameter combination, test nearby points
        param_names = list(self.param_ranges.keys())
        
        if len(param_names) >= 2:
            p1_name, p2_name = param_names[:2]
            p1_values = self.param_ranges[p1_name]
            p2_values = self.param_ranges[p2_name]
            
            for i, p1 in enumerate(p1_values):
                for j, p2 in enumerate(p2_values):
                    # Calculate robustness score
                    robustness = self._calculate_robustness_score(p1_name, p1, p2_name, p2)
                    
                    if robustness >= stability_threshold:
                        robust_params.append({
                            'parameters': {p1_name: p1, p2_name: p2},
                            'robustness_score': robustness
                        })
        
        return sorted(robust_params, key=lambda x: x['robustness_score'], reverse=True)
    
    def _calculate_robustness_score(self, p1_name, p1_value, p2_name, p2_value):
        """
        Calculate robustness score for a parameter combination.
        """
        # Evaluate performance at target parameters
        base_performance = self._evaluate_parameters({p1_name: p1_value, p2_name: p2_value})
        
        # Evaluate performance at neighboring points
        p1_range = self.param_ranges[p1_name]
        p2_range = self.param_ranges[p2_name]
        
        # Find neighboring parameter values
        p1_idx = np.where(p1_range == p1_value)[0][0]
        p2_idx = np.where(p2_range == p2_value)[0][0]
        
        neighbor_performances = []
        
        # Check neighboring points (if they exist)
        for i_offset in [-1, 0, 1]:
            for j_offset in [-1, 0, 1]:
                if i_offset == 0 and j_offset == 0:
                    continue
                
                new_i = p1_idx + i_offset
                new_j = p2_idx + j_offset
                
                if 0 <= new_i < len(p1_range) and 0 <= new_j < len(p2_range):
                    neighbor_perf = self._evaluate_parameters({
                        p1_name: p1_range[new_i],
                        p2_name: p2_range[new_j]
                    })
                    neighbor_performances.append(neighbor_perf)
        
        # Calculate robustness as 1 - normalized performance variance
        if neighbor_performances:
            performance_variance = np.var(neighbor_performances)
            max_variance = np.var([base_performance * 0.5, base_performance * 1.5])
            robustness = 1 - (performance_variance / max_variance if max_variance > 0 else 0)
            return max(0, min(1, robustness))
        
        return 0.0
    
    def _evaluate_parameters(self, parameters):
        """
        Evaluate strategy performance with given parameters.
        """
        strategy_returns = self.strategy_function(**parameters)
        sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
        return sharpe

# Next steps for the challenge:
# 1. Implement regime-specific parameter optimization
# 2. Add Monte Carlo permutation tests for parameter significance
# 3. Implement cross-validation for time-series data
# 4. Create stability maps showing parameter robustness
# 5. Add Bayesian optimization for efficient parameter search
# 6. Implement multi-objective optimization (risk vs return trade-offs)
```

The challenge extends basic sensitivity analysis to include regime-specific optimization, 3D visualization, and robustness testing. The goal is to identify parameters that perform well across different market conditions and are insensitive to small changes.
```
