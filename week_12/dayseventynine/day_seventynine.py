
"""
Day 79: Walk-Forward and Sensitivity Analysis
Robust validation frameworks for strategy stability testing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Callable
import warnings
warnings.filterwarnings('ignore')


class WalkForwardAnalyzer:
    """
    Professional walk-forward analysis framework for trading strategies.
    
    Implements multiple validation schemes, statistical significance testing,
    and overfitting diagnostics to ensure strategy robustness.
    
    Attributes:
    -----------
    returns : pd.Series
        Strategy returns
    initial_train_period : int
        Initial training period in days
    test_period : int
        Testing period in days
    step_size : int
        Step size between windows in days
    window_type : str
        Type of window ('expanding', 'rolling', 'anchored')
    """
    
    def __init__(self, returns: pd.Series,
                 initial_train_period: int = 252 * 2,  # 2 years
                 test_period: int = 252,               # 1 year
                 step_size: int = 63,                  # Quarterly
                 window_type: str = 'expanding'):
        """
        Initialize walk-forward analyzer.
        
        Parameters:
        -----------
        returns : pd.Series
            Strategy returns with datetime index
        initial_train_period : int
            Initial training period length in trading days
        test_period : int
            Out-of-sample testing period length
        step_size : int
            Step size between windows
        window_type : str
            Window type: 'expanding', 'rolling', or 'anchored'
        """
        self.returns = self._validate_returns(returns)
        self.initial_train_period = initial_train_period
        self.test_period = test_period
        self.step_size = step_size
        self.window_type = window_type
        
        # Calculate window indices
        self.window_indices = self._calculate_windows()
        
        # Results storage
        self.results = {}
    
    def _validate_returns(self, returns: pd.Series) -> pd.Series:
        """Validate and prepare returns series."""
        if not isinstance(returns, pd.Series):
            raise TypeError("Returns must be a pandas Series")
        
        if len(returns) < self.initial_train_period + self.test_period:
            raise ValueError(f"Insufficient data. Need at least "
                           f"{self.initial_train_period + self.test_period} "
                           f"observations")
        
        returns = returns.dropna()
        if len(returns) == 0:
            raise ValueError("Returns series contains only NaN values")
        
        return returns
    
    def _calculate_windows(self) -> List[Tuple[int, int, int, int]]:
        """
        Calculate walk-forward window indices.
        
        Returns:
        --------
        list: List of tuples (train_start, train_end, test_start, test_end)
        """
        n_obs = len(self.returns)
        windows = []
        
        # Initial training window
        train_start = 0
        train_end = self.initial_train_period - 1
        test_start = train_end + 1
        test_end = min(test_start + self.test_period - 1, n_obs - 1)
        
        windows.append((train_start, train_end, test_start, test_end))
        
        # Subsequent windows
        while test_end < n_obs - 1:
            if self.window_type == 'expanding':
                # Expanding window: training grows, testing moves forward
                train_end = test_start - 1
                train_start = 0  # Always start from beginning
            elif self.window_type == 'rolling':
                # Rolling window: fixed training length
                train_start += self.step_size
                train_end = test_start - 1
            elif self.window_type == 'anchored':
                # Anchored: training fixed at initial, only test moves
                train_start = 0
                train_end = self.initial_train_period - 1
            else:
                raise ValueError(f"Unknown window type: {self.window_type}")
            
            test_start = train_end + 1
            test_end = min(test_start + self.test_period - 1, n_obs - 1)
            
            # Ensure we have enough data
            if test_end - test_start + 1 < self.test_period * 0.5:
                break  # Last window too small
            
            windows.append((train_start, train_end, test_start, test_end))
        
        return windows
    
    def analyze(self, metric: str = 'sharpe') -> Dict:
        """
        Perform walk-forward analysis.
        
        Parameters:
        -----------
        metric : str
            Performance metric to track ('sharpe', 'return', 'sortino')
        
        Returns:
        --------
        dict: Walk-forward analysis results
        """
        if not self.window_indices:
            raise ValueError("No valid windows calculated")
        
        results = {
            'n_windows': len(self.window_indices),
            'window_type': self.window_type,
            'in_sample_metrics': [],
            'out_of_sample_metrics': [],
            'dates': [],
            'consistency_scores': {}
        }
        
        for i, (train_start, train_end, test_start, test_end) in enumerate(self.window_indices):
            # Extract train and test returns
            train_returns = self.returns.iloc[train_start:train_end+1]
            test_returns = self.returns.iloc[test_start:test_end+1]
            
            # Calculate metrics
            train_metric = self._calculate_metric(train_returns, metric)
            test_metric = self._calculate_metric(test_returns, metric)
            
            # Store results
            results['in_sample_metrics'].append(train_metric)
            results['out_of_sample_metrics'].append(test_metric)
            
            # Store window dates for reference
            window_dates = {
                'train_start': self.returns.index[train_start],
                'train_end': self.returns.index[train_end],
                'test_start': self.returns.index[test_start],
                'test_end': self.returns.index[test_end]
            }
            results['dates'].append(window_dates)
        
        # Calculate summary statistics
        results.update(self._calculate_summary_statistics(results))
        
        # Calculate overfitting diagnostics
        results.update(self.calculate_overfitting_diagnostics())
        
        self.results = results
        return results
    
    def _calculate_metric(self, returns: pd.Series, metric: str) -> float:
        """Calculate specified performance metric."""
        if len(returns) == 0:
            return np.nan
        
        if metric == 'sharpe':
            if returns.std() == 0:
                return 0.0
            return returns.mean() / returns.std() * np.sqrt(252)
        
        elif metric == 'return':
            return ((1 + returns).prod() - 1) * (252 / len(returns))  # Annualized
        
        elif metric == 'sortino':
            # Sortino ratio using downside deviation
            excess_returns = returns - 0.02/252  # Risk-free assumption
            downside_returns = excess_returns[excess_returns < 0]
            if len(downside_returns) == 0 or downside_returns.std() == 0:
                return 0.0
            downside_dev = downside_returns.std() * np.sqrt(252)
            annual_return = returns.mean() * 252
            return (annual_return - 0.02) / downside_dev
        
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def _calculate_summary_statistics(self, results: Dict) -> Dict:
        """Calculate summary statistics for walk-forward analysis."""
        is_metrics = np.array(results['in_sample_metrics'])
        oos_metrics = np.array(results['out_of_sample_metrics'])
        
        # Remove NaN values
        is_metrics = is_metrics[~np.isnan(is_metrics)]
        oos_metrics = oos_metrics[~np.isnan(oos_metrics)]
        
        if len(is_metrics) == 0 or len(oos_metrics) == 0:
            return {
                'average_is_return': np.nan,
                'average_oos_return': np.nan,
                'is_sharpe': np.nan,
                'oos_sharpe': np.nan,
                'performance_consistency': np.nan,
                'performance_decay': np.nan
            }
        
        summary = {
            'average_is_return': np.mean(is_metrics),
            'average_oos_return': np.mean(oos_metrics),
            'is_sharpe': np.mean(is_metrics) / np.std(is_metrics) if np.std(is_metrics) > 0 else 0,
            'oos_sharpe': np.mean(oos_metrics) / np.std(oos_metrics) if np.std(oos_metrics) > 0 else 0,
            'performance_consistency': self._calculate_performance_consistency(is_metrics, oos_metrics),
            'performance_decay': np.mean(is_metrics) - np.mean(oos_metrics)
        }
        
        return summary
    
    def _calculate_performance_consistency(self, is_metrics: np.ndarray, 
                                         oos_metrics: np.ndarray) -> float:
        """Calculate performance consistency between in-sample and out-of-sample."""
        if len(is_metrics) != len(oos_metrics):
            return 0.0
        
        # Correlation between in-sample and out-of-sample performance
        correlation = np.corrcoef(is_metrics, oos_metrics)[0, 1]
        
        # Percentage of windows where out-of-sample > 0 (if Sharpe)
        positive_oos = np.mean(oos_metrics > 0)
        
        # Combine metrics
        consistency = 0.6 * (correlation + 1) / 2 + 0.4 * positive_oos
        
        return max(0, min(1, consistency))  # Ensure between 0 and 1
    
    def calculate_overfitting_diagnostics(self) -> Dict:
        """
        Calculate overfitting diagnostics including Prado's formula.
        
        Returns:
        --------
        dict: Overfitting diagnostics
        """
        if not self.results:
            self.analyze()
        
        diagnostics = {}
        
        # Prado's minimum backtest length
        # MBL = -2 * ln(α) * (N² / θ²)
        # where α = significance level, N = number of trials, θ = track record length
        
        alpha = 0.05  # 95% confidence
        n_trials = len(self.window_indices)
        avg_track_record = self.test_period / 252  # Years
        
        if avg_track_record > 0:
            mbl = -2 * np.log(alpha) * (n_trials ** 2) / (avg_track_record ** 2)
            diagnostics['minimum_backtest_length'] = mbl
        else:
            diagnostics['minimum_backtest_length'] = np.inf
        
        # Probability of false strategy (combinatorics)
        # Based on number of trials and significance level
        false_strategy_prob = 1 - (1 - alpha) ** n_trials
        diagnostics['false_strategy_probability'] = false_strategy_prob
        
        # Degrees of freedom consumed
        # Rough estimate based on number of windows and parameters tested
        diagnostics['degrees_of_freedom'] = n_trials * 2  # Conservative estimate
        
        # Overfitting warning
        diagnostics['overfitting_warning'] = (
            false_strategy_prob > 0.5 or 
            diagnostics['minimum_backtest_length'] > len(self.returns) / 252
        )
        
        # Recommendations
        recommendations = []
        if diagnostics['overfitting_warning']:
            if false_strategy_prob > 0.5:
                recommendations.append("Reduce number of trials/optimizations")
            if diagnostics['minimum_backtest_length'] > len(self.returns) / 252:
                recommendations.append("Increase backtest length or reduce test frequency")
        
        diagnostics['recommendations'] = recommendations
        
        return diagnostics
    
    def plot_walkforward_performance(self, save_path: Optional[str] = None):
        """
        Plot walk-forward analysis results.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.gridspec as gridspec
        except ImportError:
            print("Matplotlib not available for plotting")
            return
        
        if not self.results:
            self.analyze()
        
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. In-sample vs Out-of-sample performance
        ax1 = fig.add_subplot(gs[0, 0])
        windows = range(1, len(self.results['in_sample_metrics']) + 1)
        ax1.plot(windows, self.results['in_sample_metrics'], 
                'b-', linewidth=2, label='In-sample', marker='o')
        ax1.plot(windows, self.results['out_of_sample_metrics'], 
                'r-', linewidth=2, label='Out-of-sample', marker='s')
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax1.set_title('Walk-Forward Performance', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Window Number')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Performance consistency scatter
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.scatter(self.results['in_sample_metrics'], 
                   self.results['out_of_sample_metrics'],
                   alpha=0.6, s=50)
        
        # Add identity line
        min_val = min(min(self.results['in_sample_metrics']),
                     min(self.results['out_of_sample_metrics'])) - 0.1
        max_val = max(max(self.results['in_sample_metrics']),
                     max(self.results['out_of_sample_metrics'])) + 0.1
        ax2.plot([min_val, max_val], [min_val, max_val], 
                'k--', alpha=0.5, label='Perfect consistency')
        
        ax2.set_title('In-sample vs Out-of-sample Performance', 
                     fontsize=12, fontweight='bold')
        ax2.set_xlabel('In-sample Sharpe')
        ax2.set_ylabel('Out-of-sample Sharpe')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Performance decay over time
        ax3 = fig.add_subplot(gs[1, 0])
        performance_decay = []
        cumulative_decay = 0
        
        for i, (is_metric, oos_metric) in enumerate(
            zip(self.results['in_sample_metrics'], 
                self.results['out_of_sample_metrics'])):
            decay = is_metric - oos_metric
            cumulative_decay += decay
            performance_decay.append(cumulative_decay)
        
        ax3.plot(windows, performance_decay, 'g-', linewidth=2, marker='o')
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax3.set_title('Cumulative Performance Decay', 
                     fontsize=12, fontweight='bold')
        ax3.set_xlabel('Window Number')
        ax3.set_ylabel('Cumulative Decay (IS - OOS)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Key statistics
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        
        stats_text = (
            f"Walk-Forward Analysis Summary\n\n"
            f"Window Type: {self.window_type}\n"
            f"Number of Windows: {self.results['n_windows']}\n"
            f"Average IS Sharpe: {self.results['average_is_return']:.3f}\n"
            f"Average OOS Sharpe: {self.results['average_oos_return']:.3f}\n"
            f"Performance Consistency: {self.results['performance_consistency']:.2%}\n"
            f"Performance Decay: {self.results['performance_decay']:.3f}\n"
            f"\nOverfitting Diagnostics:\n"
            f"Min Backtest Length: {self.results.get('minimum_backtest_length', 0):.0f} years\n"
            f"False Strategy Prob: {self.results.get('false_strategy_probability', 0):.2%}\n"
        )
        
        if self.results.get('overfitting_warning', False):
            stats_text += "\n⚠️ OVERFITTING WARNING"
        
        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle(f'Walk-Forward Analysis ({self.window_type.capitalize()} Windows)', 
                    fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Walk-forward plot saved to {save_path}")
        
        plt.tight_layout()
        return fig


class ParameterSensitivityAnalyzer:
    """
    Parameter sensitivity analyzer for trading strategies.
    
    Implements full factorial designs, response surface methodology,
    and robustness testing for parameter optimization.
    """
    
    def __init__(self, strategy_function: Callable, 
                 param_ranges: Dict[str, np.ndarray]):
        """
        Initialize sensitivity analyzer.
        
        Parameters:
        -----------
        strategy_function : callable
            Function that takes parameters and returns strategy returns
        param_ranges : dict
            Dictionary mapping parameter names to value arrays
        """
        self.strategy_function = strategy_function
        self.param_ranges = param_ranges
        self.results = None
        
    def analyze(self, n_simulations: int = 1000) -> Dict:
        """
        Perform full factorial parameter sensitivity analysis.
        
        Parameters:
        -----------
        n_simulations : int
            Number of Monte Carlo simulations for stability testing
        
        Returns:
        --------
        dict: Sensitivity analysis results
        """
        param_names = list(self.param_ranges.keys())
        
        if len(param_names) == 0:
            raise ValueError("No parameter ranges specified")
        
        # Generate full factorial design
        param_combinations = self._generate_full_factorial()
        
        # Evaluate each parameter combination
        evaluation_results = []
        
        print(f"Evaluating {len(param_combinations)} parameter combinations...")
        
        for i, params in enumerate(param_combinations):
            # Run strategy with these parameters
            try:
                strategy_returns = self.strategy_function(**params)
                
                # Calculate performance metrics
                metrics = self._calculate_performance_metrics(strategy_returns)
                
                # Store results
                result = {
                    'parameters': params,
                    'metrics': metrics,
                    'returns': strategy_returns
                }
                evaluation_results.append(result)
                
            except Exception as e:
                print(f"Error evaluating parameters {params}: {e}")
                continue
        
        # Analyze results
        analysis = self._analyze_results(evaluation_results, param_names)
        
        # Monte Carlo stability testing
        stability_results = self._monte_carlo_stability_test(
            evaluation_results, n_simulations
        )
        
        analysis.update(stability_results)
        
        self.results = analysis
        return analysis
    
    def _generate_full_factorial(self) -> List[Dict]:
        """Generate full factorial parameter combinations."""
        from itertools import product
        
        param_names = list(self.param_ranges.keys())
        param_values = list(self.param_ranges.values())
        
        combinations = []
        for values in product(*param_values):
            param_dict = dict(zip(param_names, values))
            combinations.append(param_dict)
        
        return combinations
    
    def _calculate_performance_metrics(self, returns: pd.Series) -> Dict:
        """Calculate performance metrics for strategy returns."""
        if len(returns) == 0:
            return {
                'sharpe': 0,
                'annual_return': 0,
                'max_drawdown': 0,
                'win_rate': 0
            }
        
        metrics = {
            'sharpe': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'annual_return': returns.mean() * 252,
            'total_return': (1 + returns).prod() - 1,
            'volatility': returns.std() * np.sqrt(252),
            'max_drawdown': self._calculate_max_drawdown(returns),
            'win_rate': (returns > 0).mean()
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _analyze_results(self, results: List[Dict], 
                        param_names: List[str]) -> Dict:
        """Analyze evaluation results to find optimal parameters."""
        if not results:
            raise ValueError("No valid results to analyze")
        
        # Find best parameters by Sharpe ratio
        best_by_sharpe = max(results, 
                            key=lambda x: x['metrics']['sharpe'])
        
        # Find best parameters by return
        best_by_return = max(results, 
                           key=lambda x: x['metrics']['annual_return'])
        
        # Find best parameters by risk-adjusted return (Sharpe)
        best_by_risk_adjusted = max(results,
                                  key=lambda x: x['metrics']['sharpe'])
        
        # Calculate parameter importance (sensitivity)
        sensitivity = self._calculate_parameter_sensitivity(results, param_names)
        
        # Create response surface data for 2D visualization
        response_surface = None
        if len(param_names) >= 2:
            response_surface = self._create_response_surface(results, 
                                                           param_names[:2])
        
        analysis = {
            'optimal_parameters': {
                'by_sharpe': best_by_sharpe['parameters'],
                'by_return': best_by_return['parameters'],
                'by_risk_adjusted': best_by_risk_adjusted['parameters']
            },
            'optimal_performance': {
                'sharpe': best_by_sharpe['metrics']['sharpe'],
                'annual_return': best_by_return['metrics']['annual_return'],
                'max_drawdown': best_by_risk_adjusted['metrics']['max_drawdown']
            },
            'parameter_sensitivity': sensitivity,
            'response_surface': response_surface,
            'n_valid_combinations': len(results)
        }
        
        return analysis
    
    def _calculate_parameter_sensitivity(self, results: List[Dict], 
                                        param_names: List[str]) -> Dict:
        """Calculate parameter sensitivity using ANOVA-like approach."""
        sensitivity = {}
        
        for param_name in param_names:
            # Group results by parameter value
            param_values = []
            performance_values = []
            
            for result in results:
                param_value = result['parameters'][param_name]
                performance = result['metrics']['sharpe']
                
                param_values.append(param_value)
                performance_values.append(performance)
            
            # Calculate sensitivity (correlation coefficient)
            if len(set(param_values)) > 1 and len(set(performance_values)) > 1:
                correlation = np.corrcoef(param_values, performance_values)[0, 1]
                sensitivity[param_name] = abs(correlation)
            else:
                sensitivity[param_name] = 0.0
        
        # Normalize sensitivities to sum to 1
        total_sensitivity = sum(sensitivity.values())
        if total_sensitivity > 0:
            sensitivity = {k: v/total_sensitivity 
                          for k, v in sensitivity.items()}
        
        return sensitivity
    
    def _create_response_surface(self, results: List[Dict], 
                                param_names: Tuple[str, str]) -> Dict:
        """Create 2D response surface for visualization."""
        p1_name, p2_name = param_names
        p1_values = sorted(set(r['parameters'][p1_name] for r in results))
        p2_values = sorted(set(r['parameters'][p2_name] for r in results))
        
        # Create performance matrix
        performance_matrix = np.zeros((len(p1_values), len(p2_values)))
        
        for i, p1 in enumerate(p1_values):
            for j, p2 in enumerate(p2_values):
                # Find result for this parameter combination
                matching_results = [
                    r for r in results 
                    if (r['parameters'][p1_name] == p1 and 
                        r['parameters'][p2_name] == p2)
                ]
                
                if matching_results:
                    performance_matrix[i, j] = matching_results[0]['metrics']['sharpe']
                else:
                    performance_matrix[i, j] = np.nan
        
        response_surface = {
            'param1_name': p1_name,
            'param1_values': p1_values,
            'param2_name': p2_name,
            'param2_values': p2_values,
            'performance_matrix': performance_matrix
        }
        
        return response_surface
    
    def _monte_carlo_stability_test(self, results: List[Dict], 
                                   n_simulations: int) -> Dict:
        """Perform Monte Carlo stability testing."""
        if not results:
            return {
                'stability_scores': {},
                'robust_parameters': []
            }
        
        # Extract all parameter combinations and their performances
        param_combinations = []
        performances = []
        
        for result in results:
            param_combinations.append(result['parameters'])
            performances.append(result['metrics']['sharpe'])
        
        # Bootstrap sampling to test stability
        stability_scores = {}
        n_combinations = len(param_combinations)
        
        if n_combinations < 10:
            return {
                'stability_scores': {},
                'robust_parameters': []
            }
        
        # For each parameter, calculate how often it appears in top performers
        for param_name in self.param_ranges.keys():
            top_performer_counts = {value: 0 for value in self.param_ranges[param_name]}
            
            for sim in range(n_simulations):
                # Bootstrap sample of results
                sample_indices = np.random.choice(n_combinations, 
                                                 size=n_combinations, 
                                                 replace=True)
                
                # Find best performer in this sample
                sample_performances = [performances[i] for i in sample_indices]
                best_idx = sample_indices[np.argmax(sample_performances)]
                best_params = param_combinations[best_idx]
                
                # Count this parameter value
                param_value = best_params[param_name]
                if param_value in top_performer_counts:
                    top_performer_counts[param_value] += 1
            
            # Calculate stability score (entropy of distribution)
            counts = np.array(list(top_performer_counts.values()))
            total_counts = counts.sum()
            
            if total_counts > 0:
                probabilities = counts / total_counts
                # Stability is 1 - normalized entropy
                entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
                max_entropy = np.log(len(probabilities))
                stability = 1 - (entropy / max_entropy if max_entropy > 0 else 0)
            else:
                stability = 0
            
            stability_scores[param_name] = stability
        
        # Find robust parameters (high stability across simulations)
        robust_parameters = []
        threshold = 0.7  # Stability threshold
        
        for i, params in enumerate(param_combinations):
            # Calculate average stability for this parameter combination
            param_stability = np.mean([
                stability_scores.get(param_name, 0) 
                for param_name in params.keys()
            ])
            
            if param_stability >= threshold:
                robust_parameters.append({
                    'parameters': params,
                    'stability_score': param_stability,
                    'performance': performances[i]
                })
        
        # Sort by performance within stability threshold
        robust_parameters.sort(key=lambda x: x['performance'], reverse=True)
        
        return {
            'stability_scores': stability_scores,
            'robust_parameters': robust_parameters[:10]  # Top 10
        }
    
    def plot_response_surface(self, save_path: Optional[str] = None):
        """
        Plot response surface for parameter sensitivity.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print("Matplotlib not available for 3D plotting")
            return
        
        if self.results is None or 'response_surface' not in self.results:
            print("No response surface data available")
            return
        
        rs = self.results['response_surface']
        if rs is None:
            print("Response surface requires at least 2 parameters")
            return
        
        fig = plt.figure(figsize=(12, 8))
        
        # 3D surface plot
        ax1 = fig.add_subplot(121, projection='3d')
        
        X, Y = np.meshgrid(rs['param1_values'], rs['param2_values'])
        Z = rs['performance_matrix'].T
        
        surf = ax1.plot_surface(X, Y, Z, cmap='viridis', 
                               alpha=0.8, linewidth=0.5)
        
        ax1.set_xlabel(rs['param1_name'])
        ax1.set_ylabel(rs['param2_name'])
        ax1.set_zlabel('Sharpe Ratio')
        ax1.set_title('3D Response Surface', fontweight='bold')
        
        # Add colorbar
        fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)
        
        # 2D contour plot
        ax2 = fig.add_subplot(122)
        
        contour = ax2.contourf(X, Y, Z, 20, cmap='viridis')
        ax2.contour(X, Y, Z, 10, colors='black', alpha=0.3, linewidths=0.5)
        
        # Mark optimal point
        optimal_params = self.results['optimal_parameters']['by_sharpe']
        if (rs['param1_name'] in optimal_params and 
            rs['param2_name'] in optimal_params):
            ax2.scatter(optimal_params[rs['param1_name']],
                       optimal_params[rs['param2_name']],
                       color='red', s=100, marker='*',
                       label='Optimal')
            ax2.legend()
        
        ax2.set_xlabel(rs['param1_name'])
        ax2.set_ylabel(rs['param2_name'])
        ax2.set_title('2D Contour Plot', fontweight='bold')
        
        # Add colorbar
        fig.colorbar(contour, ax=ax2, shrink=0.8, aspect=20)
        
        plt.suptitle('Parameter Sensitivity Response Surface', 
                    fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Response surface saved to {save_path}")
        
        plt.tight_layout()
        return fig


class MonteCarloPermutationTester:
    """
    Monte Carlo permutation tester for strategy significance.
    
    Tests whether strategy performance is statistically significant
    or could have occurred by random chance.
    """
    
    def __init__(self, strategy_returns: pd.Series,
                 benchmark_returns: Optional[pd.Series] = None):
        """
        Initialize permutation tester.
        
        Parameters:
        -----------
        strategy_returns : pd.Series
            Strategy returns to test
        benchmark_returns : pd.Series, optional
            Benchmark returns for comparison
        """
        self.strategy_returns = strategy_returns.dropna()
        self.benchmark_returns = benchmark_returns.dropna() if benchmark_returns is not None else None
        
        if self.benchmark_returns is not None:
            # Align dates
            common_idx = self.strategy_returns.index.intersection(
                self.benchmark_returns.index
            )
            self.strategy_returns = self.strategy_returns.loc[common_idx]
            self.benchmark_returns = self.benchmark_returns.loc[common_idx]
    
    def permutation_test(self, n_permutations: int = 10000, 
                        test_statistic: str = 'sharpe') -> Dict:
        """
        Perform permutation test for strategy significance.
        
        Parameters:
        -----------
        n_permutations : int
            Number of random permutations
        test_statistic : str
            Test statistic ('sharpe', 'return', 'alpha')
        
        Returns:
        --------
        dict: Permutation test results
        """
        # Calculate actual test statistic
        actual_stat = self._calculate_test_statistic(test_statistic)
        
        # Generate null distribution via permutation
        null_distribution = []
        
        for i in range(n_permutations):
            # Randomly permute returns (under null hypothesis of no skill)
            permuted_returns = self._generate_null_returns()
            
            # Calculate test statistic for permuted data
            permuted_stat = self._calculate_statistic_for_returns(
                permuted_returns, test_statistic
            )
            null_distribution.append(permuted_stat)
        
        null_distribution = np.array(null_distribution)
        
        # Calculate p-value
        if test_statistic in ['sharpe', 'return', 'alpha']:
            # One-tailed test (greater than)
            p_value = np.mean(null_distribution >= actual_stat)
        else:
            # Two-tailed test
            p_value = np.mean(np.abs(null_distribution) >= np.abs(actual_stat))
        
        # Calculate confidence intervals
        ci_lower = np.percentile(null_distribution, 2.5)
        ci_upper = np.percentile(null_distribution, 97.5)
        
        results = {
            'actual_statistic': actual_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'confidence_interval': (ci_lower, ci_upper),
            'null_mean': np.mean(null_distribution),
            'null_std': np.std(null_distribution),
            'effect_size': (actual_stat - np.mean(null_distribution)) / np.std(null_distribution)
        }
        
        return results
    
    def _calculate_test_statistic(self, statistic: str) -> float:
        """Calculate test statistic for actual returns."""
        if statistic == 'sharpe':
            return self.strategy_returns.mean() / self.strategy_returns.std() * np.sqrt(252)
        
        elif statistic == 'return':
            return self.strategy_returns.mean() * 252
        
        elif statistic == 'alpha':
            if self.benchmark_returns is None:
                raise ValueError("Benchmark required for alpha calculation")
            
            # Simple alpha calculation
            beta = np.cov(self.strategy_returns, self.benchmark_returns)[0, 1] / np.var(self.benchmark_returns)
            alpha = self.strategy_returns.mean() - beta * self.benchmark_returns.mean()
            return alpha * 252
        
        else:
            raise ValueError(f"Unknown test statistic: {statistic}")
    
    def _generate_null_returns(self) -> pd.Series:
        """Generate null returns under hypothesis of no skill."""
        if self.benchmark_returns is not None:
            # Under null, strategy returns are just random noise around benchmark
            noise = np.random.normal(0, self.strategy_returns.std(), 
                                   len(self.strategy_returns))
            null_returns = self.benchmark_returns.values + noise
        else:
            # Randomly shuffle the returns (preserves distribution but not autocorrelation)
            null_returns = np.random.permutation(self.strategy_returns.values)
        
        return pd.Series(null_returns, index=self.strategy_returns.index)
    
    def _calculate_statistic_for_returns(self, returns: pd.Series, 
                                        statistic: str) -> float:
        """Calculate test statistic for given returns."""
        if statistic == 'sharpe':
            if returns.std() == 0:
                return 0
            return returns.mean() / returns.std() * np.sqrt(252)
        
        elif statistic == 'return':
            return returns.mean() * 252
        
        elif statistic == 'alpha':
            if self.benchmark_returns is None:
                raise ValueError("Benchmark required for alpha")
            
            beta = np.cov(returns, self.benchmark_returns)[0, 1] / np.var(self.benchmark_returns)
            alpha = returns.mean() - beta * self.benchmark_returns.mean()
            return alpha * 252
        
        else:
            raise ValueError(f"Unknown statistic: {statistic}")


def generate_sample_strategy(window: int = 20, threshold: float = 0.5) -> pd.Series:
    """
    Generate sample strategy returns for demonstration.
    
    Parameters:
    -----------
    window : int
        Lookback window for momentum calculation
    threshold : float
        Signal threshold
    
    Returns:
    --------
    pd.Series: Strategy returns
    """
    np.random.seed(42)
    dates = pd.date_range('2015-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    
    # Generate market returns with autocorrelation (momentum)
    market_returns = np.zeros(n_dates)
    market_returns[0] = np.random.normal(0.0003, 0.015)
    
    for i in range(1, n_dates):
        # Add momentum effect
        momentum = 0.1 * market_returns[i-1] if i > 1 else 0
        market_returns[i] = np.random.normal(0.0003 + momentum, 0.015)
    
    # Simple momentum strategy
    signals = np.zeros(n_dates)
    
    for i in range(n_dates):
        if i < window:
            signals[i] = 0
        else:
            recent_return = market_returns[i-window:i].mean()
            if recent_return > threshold * 0.01:  # Convert to daily scale
                signals[i] = 1
            elif recent_return < -threshold * 0.01:
                signals[i] = -1
    
    # Strategy returns = signal * market returns + some skill
    strategy_returns = signals * market_returns * 1.2 + np.random.normal(0.0001, 0.005, n_dates)
    
    return pd.Series(strategy_returns, index=dates, name='strategy')


def main():
    """Main demonstration function."""
    print("Day 79: Walk-Forward and Sensitivity Analysis")
    print("=" * 60)
    
    # Generate sample strategy
    print("\nGenerating sample strategy data...")
    strategy_returns = generate_sample_strategy(window=20, threshold=0.5)
    
    print(f"Strategy observations: {len(strategy_returns)}")
    print(f"Strategy Sharpe ratio: {strategy_returns.mean()/strategy_returns.std()*np.sqrt(252):.3f}")
    
    # Walk-forward analysis
    print("\n" + "=" * 60)
    print("Walk-Forward Analysis")
    print("=" * 60)
    
    wf_analyzer = WalkForwardAnalyzer(
        returns=strategy_returns,
        initial_train_period=252 * 2,  # 2 years
        test_period=252,               # 1 year
        step_size=63,                  # Quarterly
        window_type='expanding'
    )
    
    wf_results = wf_analyzer.analyze(metric='sharpe')
    
    print(f"\nWalk-Forward Results:")
    print(f"Number of windows: {wf_results['n_windows']}")
    print(f"Average in-sample Sharpe: {wf_results['average_is_return']:.3f}")
    print(f"Average out-of-sample Sharpe: {wf_results['average_oos_return']:.3f}")
    print(f"Performance consistency: {wf_results['performance_consistency']:.2%}")
    print(f"Performance decay: {wf_results['performance_decay']:.3f}")
    
    # Overfitting diagnostics
    print(f"\nOverfitting Diagnostics:")
    print(f"Minimum backtest length: {wf_results['minimum_backtest_length']:.1f} years")
    print(f"Probability of false strategy: {wf_results['false_strategy_probability']:.2%}")
    print(f"Degrees of freedom consumed: {wf_results['degrees_of_freedom']:.1f}")
    
    if wf_results['overfitting_warning']:
        print("\nWARNING: Potential overfitting detected!")
        print("Recommendations:")
        for rec in wf_results['recommendations']:
            print(f"  - {rec}")
    
    # Create walk-forward plot
    try:
        wf_analyzer.plot_walkforward_performance(save_path='walkforward_analysis.png')
        print("\nWalk-forward plot saved to 'walkforward_analysis.png'")
    except Exception as e:
        print(f"\nCould not create walk-forward plot: {e}")
    
    # Parameter sensitivity analysis
    print("\n" + "=" * 60)
    print("Parameter Sensitivity Analysis")
    print("=" * 60)
    
    # Define parameter ranges
    param_ranges = {
        'window': np.arange(5, 61, 5),      # 5 to 60 days
        'threshold': np.arange(0.1, 1.1, 0.1)  # 0.1 to 1.0
    }
    
    sensitivity_analyzer = ParameterSensitivityAnalyzer(
        strategy_function=generate_sample_strategy,
        param_ranges=param_ranges
    )
    
    sensitivity_results = sensitivity_analyzer.analyze(n_simulations=100)
    
    print(f"\nSensitivity Analysis Results:")
    print(f"Valid parameter combinations evaluated: {sensitivity_results['n_valid_combinations']}")
    
    # Display optimal parameters
    optimal = sensitivity_results['optimal_parameters']['by_sharpe']
    print(f"\nOptimal parameters (by Sharpe):")
    print(f"  Window: {optimal['window']} days")
    print(f"  Threshold: {optimal['threshold']:.2f}")
    
    optimal_perf = sensitivity_results['optimal_performance']
    print(f"\nOptimal performance:")
    print(f"  Sharpe ratio: {optimal_perf['sharpe']:.3f}")
    print(f"  Annual return: {optimal_perf['annual_return']:.2%}")
    print(f"  Max drawdown: {optimal_perf['max_drawdown']:.2%}")
    
    # Display parameter sensitivity
    print(f"\nParameter Sensitivity (importance):")
    for param, importance in sensitivity_results['parameter_sensitivity'].items():
        print(f"  {param:15}: {importance:.3f}")
    
    # Display robust parameters
    robust_params = sensitivity_results['robust_parameters']
    if robust_params:
        print(f"\nTop robust parameter combinations:")
        for i, params in enumerate(robust_params[:3]):
            print(f"  {i+1}. Window={params['parameters']['window']}, "
                  f"Threshold={params['parameters']['threshold']:.2f}, "
                  f"Stability={params['stability_score']:.3f}, "
                  f"Sharpe={params['performance']:.3f}")
    
    # Create response surface plot
    try:
        sensitivity_analyzer.plot_response_surface(save_path='parameter_sensitivity.png')
        print("\nResponse surface plot saved to 'parameter_sensitivity.png'")
    except Exception as e:
        print(f"\nCould not create response surface plot: {e}")
    
    # Monte Carlo permutation test
    print("\n" + "=" * 60)
    print("Monte Carlo Permutation Test")
    print("=" * 60)
    
    permutation_tester = MonteCarloPermutationTester(strategy_returns)
    
    permutation_results = permutation_tester.permutation_test(
        n_permutations=5000,  # Reduced for speed
        test_statistic='sharpe'
    )
    
    print(f"\nPermutation Test Results:")
    print(f"Actual Sharpe ratio: {permutation_results['actual_statistic']:.3f}")
    print(f"Null distribution mean: {permutation_results['null_mean']:.3f}")
    print(f"Null distribution std: {permutation_results['null_std']:.3f}")
    print(f"p-value: {permutation_results['p_value']:.4f}")
    print(f"Significant at 5% level: {permutation_results['significant']}")
    print(f"95% confidence interval: [{permutation_results['confidence_interval'][0]:.3f}, "
          f"{permutation_results['confidence_interval'][1]:.3f}]")
    print(f"Effect size: {permutation_results['effect_size']:.3f}")
    
    if permutation_results['significant']:
        print("\nConclusion: Strategy performance is statistically significant")
    else:
        print("\nConclusion: Strategy performance could have occurred by random chance")
    
    print("\n" + "=" * 60)
    print("Analysis complete")
    print("=" * 60)


if __name__ == "__main__":
    main()