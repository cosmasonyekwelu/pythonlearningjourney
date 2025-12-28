
"""
Day 83: Monte Carlo Simulations for Uncertainty Modeling
Advanced simulation techniques for strategy validation and risk assessment
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize, interpolate, special
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# For advanced statistical methods
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import emcee  # MCMC sampler
    EMCEE_AVAILABLE = True
except ImportError:
    EMCEE_AVAILABLE = False


@dataclass
class UncertaintyParameters:
    """Parameters for uncertainty modeling."""
    # Simulation parameters
    n_simulations: int = 5000
    n_periods: int = 252  # 1 year of daily simulations
    initial_capital: float = 100000
    risk_free_rate: float = 0.02
    
    # Uncertainty sources to model
    model_uncertainty: bool = True
    parameter_uncertainty: bool = True
    estimation_uncertainty: bool = True
    regime_uncertainty: bool = True
    
    # Statistical methods
    use_bayesian: bool = False
    use_bootstrap: bool = True
    use_gaussian_process: bool = False
    
    # Advanced options
    confidence_levels: List[float] = field(default_factory=lambda: [0.90, 0.95, 0.99])
    seed: Optional[int] = None


class UncertaintyQuantifier:
    """
    Advanced uncertainty quantification for trading strategies.
    
    Features:
    - Monte Carlo simulation with multiple uncertainty sources
    - Bayesian parameter estimation with credible intervals
    - Bootstrap confidence intervals
    - Gaussian Process regression for prediction uncertainty
    - Regime detection and switching
    - Model risk assessment
    """
    
    def __init__(self, historical_returns: pd.DataFrame,
                 strategy_performance: Optional[pd.Series] = None):
        """
        Initialize uncertainty quantifier.
        
        Parameters:
        -----------
        historical_returns : pd.DataFrame
            Historical returns data
        strategy_performance : pd.Series, optional
            Historical strategy performance
        """
        self.historical_returns = historical_returns
        self.strategy_performance = strategy_performance
        
        # Store simulation results
        self.simulation_results = {}
        self.uncertainty_metrics = {}
        self.confidence_intervals = {}
        
        # Initialize random seed
        if UncertaintyParameters().seed is not None:
            np.random.seed(UncertaintyParameters().seed)
    
    def run_comprehensive_uncertainty_analysis(self, params: UncertaintyParameters) -> Dict:
        """
        Run comprehensive uncertainty analysis.
        
        Parameters:
        -----------
        params : UncertaintyParameters
            Analysis parameters
        
        Returns:
        --------
        Dict containing comprehensive uncertainty analysis
        """
        print("Running comprehensive uncertainty analysis...")
        
        analysis_results = {}
        
        # 1. Parameter Uncertainty
        if params.parameter_uncertainty:
            print("  Analyzing parameter uncertainty...")
            param_uncertainty = self.analyze_parameter_uncertainty(params)
            analysis_results['parameter_uncertainty'] = param_uncertainty
        
        # 2. Model Uncertainty
        if params.model_uncertainty:
            print("  Analyzing model uncertainty...")
            model_uncertainty = self.analyze_model_uncertainty(params)
            analysis_results['model_uncertainty'] = model_uncertainty
        
        # 3. Estimation Uncertainty
        if params.estimation_uncertainty:
            print("  Analyzing estimation uncertainty...")
            estimation_uncertainty = self.analyze_estimation_uncertainty(params)
            analysis_results['estimation_uncertainty'] = estimation_uncertainty
        
        # 4. Regime Uncertainty
        if params.regime_uncertainty:
            print("  Analyzing regime uncertainty...")
            regime_uncertainty = self.analyze_regime_uncertainty(params)
            analysis_results['regime_uncertainty'] = regime_uncertainty
        
        # 5. Combined Uncertainty
        print("  Calculating combined uncertainty...")
        combined = self.combine_uncertainty_sources(analysis_results, params)
        analysis_results['combined_uncertainty'] = combined
        
        # 6. Confidence Intervals
        print("  Calculating confidence intervals...")
        confidence_intervals = self.calculate_all_confidence_intervals(params.confidence_levels)
        analysis_results['confidence_intervals'] = confidence_intervals
        
        self.uncertainty_metrics = analysis_results
        return analysis_results
    
    def analyze_parameter_uncertainty(self, params: UncertaintyParameters) -> Dict:
        """
        Analyze uncertainty due to parameter estimation.
        
        Parameters:
        -----------
        params : UncertaintyParameters
        
        Returns:
        --------
        Dict containing parameter uncertainty analysis
        """
        if self.historical_returns.empty:
            return {'error': 'No historical data available'}
        
        n_assets = len(self.historical_returns.columns)
        
        # Method 1: Bootstrap parameter estimation
        bootstrap_params = self._bootstrap_parameter_estimation(params.n_simulations)
        
        # Method 2: Bayesian parameter estimation (if available)
        bayesian_params = {}
        if params.use_bayesian and EMCEE_AVAILABLE:
            bayesian_params = self._bayesian_parameter_estimation()
        
        # Calculate parameter distributions
        param_distributions = {
            'means': self._calculate_parameter_distributions(bootstrap_params.get('means', [])),
            'volatilities': self._calculate_parameter_distributions(bootstrap_params.get('volatilities', [])),
            'correlations': self._calculate_correlation_distributions(bootstrap_params.get('correlations', []))
        }
        
        if bayesian_params:
            param_distributions['bayesian'] = bayesian_params
        
        # Calculate parameter uncertainty metrics
        uncertainty_metrics = self._calculate_parameter_uncertainty_metrics(param_distributions)
        
        return {
            'parameter_distributions': param_distributions,
            'uncertainty_metrics': uncertainty_metrics,
            'n_bootstrap_samples': params.n_simulations,
            'key_findings': self._extract_parameter_uncertainty_findings(param_distributions)
        }
    
    def analyze_model_uncertainty(self, params: UncertaintyParameters) -> Dict:
        """
        Analyze uncertainty due to model specification.
        
        Parameters:
        -----------
        params : UncertaintyParameters
        
        Returns:
        --------
        Dict containing model uncertainty analysis
        """
        # Define different models to compare
        models = {
            'normal': self._simulate_normal_model,
            't_distribution': self._simulate_t_distribution_model,
            'garch': self._simulate_garch_model,
            'regime_switching': self._simulate_regime_switching_model
        }
        
        model_results = {}
        
        for model_name, model_func in models.items():
            try:
                print(f"    Running {model_name} model...")
                results = model_func(params)
                model_results[model_name] = results
            except Exception as e:
                print(f"    Warning: {model_name} model failed: {e}")
                continue
        
        # Calculate model uncertainty metrics
        uncertainty_metrics = self._calculate_model_uncertainty_metrics(model_results)
        
        # Model comparison
        model_comparison = self._compare_models(model_results)
        
        return {
            'model_results': model_results,
            'uncertainty_metrics': uncertainty_metrics,
            'model_comparison': model_comparison,
            'best_model': self._select_best_model(model_comparison),
            'model_risk': self._calculate_model_risk(model_results)
        }
    
    def analyze_estimation_uncertainty(self, params: UncertaintyParameters) -> Dict:
        """
        Analyze uncertainty due to finite sample estimation.
        
        Parameters:
        -----------
        params : UncertaintyParameters
        
        Returns:
        --------
        Dict containing estimation uncertainty analysis
        """
        if self.historical_returns.empty:
            return {'error': 'No historical data available'}
        
        n_observations = len(self.historical_returns)
        
        # Method 1: Bootstrap confidence intervals
        bootstrap_cis = self._bootstrap_confidence_intervals(params.n_simulations)
        
        # Method 2: Analytical confidence intervals
        analytical_cis = self._analytical_confidence_intervals()
        
        # Method 3: Subsampling analysis
        subsampling_results = self._subsampling_analysis()
        
        # Calculate estimation uncertainty metrics
        uncertainty_metrics = {
            'sample_size_effect': self._analyze_sample_size_effect(),
            'estimation_error': self._calculate_estimation_error(bootstrap_cis, analytical_cis),
            'convergence_rate': self._estimate_convergence_rate(),
            'effective_sample_size': self._calculate_effective_sample_size()
        }
        
        return {
            'bootstrap_confidence_intervals': bootstrap_cis,
            'analytical_confidence_intervals': analytical_cis,
            'subsampling_results': subsampling_results,
            'uncertainty_metrics': uncertainty_metrics,
            'n_observations': n_observations,
            'recommended_min_sample': self._recommend_minimum_sample_size()
        }
    
    def analyze_regime_uncertainty(self, params: UncertaintyParameters) -> Dict:
        """
        Analyze uncertainty due to market regime changes.
        
        Parameters:
        -----------
        params : UncertaintyParameters
        
        Returns:
        --------
        Dict containing regime uncertainty analysis
        """
        # Detect regimes in historical data
        regimes = self._detect_market_regimes()
        
        if not regimes:
            return {'error': 'Could not detect market regimes'}
        
        # Analyze regime characteristics
        regime_characteristics = self._analyze_regime_characteristics(regimes)
        
        # Simulate regime switching
        regime_simulations = self._simulate_regime_switching(params.n_simulations, regimes)
        
        # Calculate regime uncertainty metrics
        uncertainty_metrics = self._calculate_regime_uncertainty_metrics(
            regime_characteristics, regime_simulations
        )
        
        # Regime transition analysis
        transition_analysis = self._analyze_regime_transitions(regimes)
        
        return {
            'detected_regimes': regimes,
            'regime_characteristics': regime_characteristics,
            'regime_simulations': regime_simulations,
            'uncertainty_metrics': uncertainty_metrics,
            'transition_analysis': transition_analysis,
            'regime_persistence': self._calculate_regime_persistence(regimes),
            'regime_forecast': self._forecast_regime_probabilities(regimes)
        }
    
    def combine_uncertainty_sources(self, uncertainty_sources: Dict, 
                                   params: UncertaintyParameters) -> Dict:
        """
        Combine uncertainties from different sources.
        
        Parameters:
        -----------
        uncertainty_sources : Dict
            Individual uncertainty analyses
        params : UncertaintyParameters
        
        Returns:
        --------
        Dict containing combined uncertainty analysis
        """
        combined_uncertainty = {}
        
        # Extract key uncertainty metrics from each source
        uncertainty_components = {}
        
        if 'parameter_uncertainty' in uncertainty_sources:
            param_uncertainty = uncertainty_sources['parameter_uncertainty']
            uncertainty_components['parameter'] = \
                param_uncertainty.get('uncertainty_metrics', {}).get('total_uncertainty', 0)
        
        if 'model_uncertainty' in uncertainty_sources:
            model_uncertainty = uncertainty_sources['model_uncertainty']
            uncertainty_components['model'] = \
                model_uncertainty.get('uncertainty_metrics', {}).get('model_disagreement', 0)
        
        if 'estimation_uncertainty' in uncertainty_sources:
            estimation_uncertainty = uncertainty_sources['estimation_uncertainty']
            uncertainty_components['estimation'] = \
                estimation_uncertainty.get('uncertainty_metrics', {}).get('estimation_error', 0)
        
        if 'regime_uncertainty' in uncertainty_sources:
            regime_uncertainty = uncertainty_sources['regime_uncertainty']
            uncertainty_components['regime'] = \
                regime_uncertainty.get('uncertainty_metrics', {}).get('regime_volatility', 0)
        
        # Calculate combined uncertainty using different methods
        combined_metrics = {}
        
        # Method 1: Simple addition (upper bound)
        combined_metrics['additive'] = sum(uncertainty_components.values())
        
        # Method 2: Root sum of squares (assuming independence)
        combined_metrics['rss'] = np.sqrt(sum(c**2 for c in uncertainty_components.values()))
        
        # Method 3: Weighted combination (accounting for correlations)
        # Simplified correlation estimation
        correlations = self._estimate_uncertainty_correlations(uncertainty_sources)
        combined_metrics['correlated'] = self._correlated_combination(
            list(uncertainty_components.values()), correlations
        )
        
        # Method 4: Monte Carlo combination
        combined_metrics['monte_carlo'] = self._monte_carlo_combination(
            uncertainty_sources, params.n_simulations
        )
        
        # Calculate uncertainty decomposition
        decomposition = {}
        total_uncertainty = combined_metrics.get('correlated', combined_metrics['rss'])
        
        for source, uncertainty in uncertainty_components.items():
            if total_uncertainty > 0:
                decomposition[source] = uncertainty / total_uncertainty
            else:
                decomposition[source] = 0
        
        return {
            'uncertainty_components': uncertainty_components,
            'combined_metrics': combined_metrics,
            'uncertainty_decomposition': decomposition,
            'primary_uncertainty_source': max(decomposition.items(), key=lambda x: x[1])[0],
            'recommended_uncertainty_metric': self._recommend_uncertainty_metric(combined_metrics)
        }
    
    def calculate_all_confidence_intervals(self, confidence_levels: List[float]) -> Dict:
        """
        Calculate confidence intervals at multiple levels.
        
        Parameters:
        -----------
        confidence_levels : List[float]
            Confidence levels to calculate
        
        Returns:
        --------
        Dict containing confidence intervals
        """
        if not self.uncertainty_metrics:
            return {'error': 'Run uncertainty analysis first'}
        
        confidence_intervals = {}
        
        for level in confidence_levels:
            cis = self._calculate_single_confidence_interval(level)
            confidence_intervals[f'ci_{int(level*100)}'] = cis
        
        # Calculate prediction intervals
        prediction_intervals = self._calculate_prediction_intervals(confidence_levels)
        
        # Calculate credible intervals (if Bayesian analysis was done)
        credible_intervals = {}
        if 'parameter_uncertainty' in self.uncertainty_metrics:
            bayesian_params = self.uncertainty_metrics['parameter_uncertainty'].get(
                'parameter_distributions', {}
            ).get('bayesian', {})
            
            if bayesian_params:
                credible_intervals = self._calculate_credible_intervals(
                    bayesian_params, confidence_levels
                )
        
        return {
            'confidence_intervals': confidence_intervals,
            'prediction_intervals': prediction_intervals,
            'credible_intervals': credible_intervals,
            'interval_comparison': self._compare_interval_methods(
                confidence_intervals, prediction_intervals, credible_intervals
            )
        }
    
    def generate_uncertainty_report(self) -> str:
        """Generate comprehensive uncertainty quantification report."""
        report_lines = []
        
        report_lines.append("# UNCERTAINTY QUANTIFICATION REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        
        if self.uncertainty_metrics:
            combined = self.uncertainty_metrics.get('combined_uncertainty', {})
            
            if combined:
                primary_source = combined.get('primary_uncertainty_source', 'Unknown')
                decomposition = combined.get('uncertainty_decomposition', {})
                
                report_lines.append("### Key Findings")
                report_lines.append(f"- **Primary Uncertainty Source**: {primary_source}")
                report_lines.append(f"- **Total Uncertainty Score**: {combined.get('combined_metrics', {}).get('correlated', 0):.3f}")
                report_lines.append("")
                
                report_lines.append("### Uncertainty Decomposition")
                for source, proportion in decomposition.items():
                    report_lines.append(f"- **{source.title()}**: {proportion:.1%}")
                report_lines.append("")
            else:
                report_lines.append("No combined uncertainty analysis available.")
                report_lines.append("")
        else:
            report_lines.append("No uncertainty metrics available. Run analysis first.")
            report_lines.append("")
        
        # Detailed Analysis
        if self.uncertainty_metrics:
            report_lines.append("## Detailed Uncertainty Analysis")
            report_lines.append("")
            
            # Parameter Uncertainty
            if 'parameter_uncertainty' in self.uncertainty_metrics:
                report_lines.append("### Parameter Uncertainty")
                param_uncertainty = self.uncertainty_metrics['parameter_uncertainty']
                metrics = param_uncertainty.get('uncertainty_metrics', {})
                
                report_lines.append(f"- **Total Parameter Uncertainty**: {metrics.get('total_uncertainty', 0):.4f}")
                report_lines.append(f"- **Mean Estimation Error**: {metrics.get('mean_uncertainty', 0):.4f}")
                report_lines.append(f"- **Volatility Estimation Error**: {metrics.get('volatility_uncertainty', 0):.4f}")
                report_lines.append("")
            
            # Model Uncertainty
            if 'model_uncertainty' in self.uncertainty_metrics:
                report_lines.append("### Model Uncertainty")
                model_uncertainty = self.uncertainty_metrics['model_uncertainty']
                metrics = model_uncertainty.get('uncertainty_metrics', {})
                
                report_lines.append(f"- **Model Disagreement**: {metrics.get('model_disagreement', 0):.4f}")
                report_lines.append(f"- **Best Model**: {model_uncertainty.get('best_model', 'Unknown')}")
                report_lines.append(f"- **Model Risk Score**: {metrics.get('model_risk', 0):.3f}")
                report_lines.append("")
            
            # Estimation Uncertainty
            if 'estimation_uncertainty' in self.uncertainty_metrics:
                report_lines.append("### Estimation Uncertainty")
                est_uncertainty = self.uncertainty_metrics['estimation_uncertainty']
                metrics = est_uncertainty.get('uncertainty_metrics', {})
                
                report_lines.append(f"- **Estimation Error**: {metrics.get('estimation_error', 0):.4f}")
                report_lines.append(f"- **Effective Sample Size**: {metrics.get('effective_sample_size', 0):.0f}")
                report_lines.append(f"- **Recommended Minimum Sample**: {est_uncertainty.get('recommended_min_sample', 0)}")
                report_lines.append("")
            
            # Regime Uncertainty
            if 'regime_uncertainty' in self.uncertainty_metrics:
                report_lines.append("### Regime Uncertainty")
                regime_uncertainty = self.uncertainty_metrics['regime_uncertainty']
                metrics = regime_uncertainty.get('uncertainty_metrics', {})
                
                report_lines.append(f"- **Regime Volatility**: {metrics.get('regime_volatility', 0):.4f}")
                report_lines.append(f"- **Regime Persistence**: {regime_uncertainty.get('regime_persistence', 0):.3f}")
                report_lines.append(f"- **Detected Regimes**: {len(regime_uncertainty.get('detected_regimes', []))}")
                report_lines.append("")
        
        # Confidence Intervals
        if 'confidence_intervals' in self.uncertainty_metrics:
            report_lines.append("## Confidence Intervals")
            report_lines.append("")
            
            cis = self.uncertainty_metrics['confidence_intervals']
            conf_intervals = cis.get('confidence_intervals', {})
            
            for level, interval in conf_intervals.items():
                if 'mean' in interval:
                    report_lines.append(f"### {level.replace('_', ' ').upper()}")
                    report_lines.append(f"- **Mean**: {interval['mean']:.4f}")
                    report_lines.append(f"- **Lower Bound**: {interval['lower']:.4f}")
                    report_lines.append(f"- **Upper Bound**: {interval['upper']:.4f}")
                    report_lines.append(f"- **Width**: {interval['width']:.4f}")
                    report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        
        recommendations = self._generate_uncertainty_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*This report quantifies various sources of uncertainty in strategy evaluation.*")
        report_lines.append("*Higher uncertainty requires more conservative position sizing and risk management.*")
        
        return "\n".join(report_lines)
    
    # Implementation of helper methods
    def _bootstrap_parameter_estimation(self, n_samples: int) -> Dict:
        """Estimate parameter distributions using bootstrap."""
        if self.historical_returns.empty:
            return {}
        
        n_assets = len(self.historical_returns.columns)
        n_obs = len(self.historical_returns)
        
        means = []
        volatilities = []
        correlations = []
        
        for _ in range(n_samples):
            # Bootstrap sample
            sample_indices = np.random.choice(n_obs, size=n_obs, replace=True)
            bootstrap_sample = self.historical_returns.iloc[sample_indices]
            
            # Calculate parameters
            sample_mean = bootstrap_sample.mean().values * 252
            sample_vol = bootstrap_sample.std().values * np.sqrt(252)
            sample_corr = bootstrap_sample.corr().values
            
            means.append(sample_mean)
            volatilities.append(sample_vol)
            correlations.append(sample_corr)
        
        return {
            'means': np.array(means),
            'volatilities': np.array(volatilities),
            'correlations': np.array(correlations)
        }
    
    def _bayesian_parameter_estimation(self) -> Dict:
        """Estimate parameters using Bayesian methods."""
        if not EMCEE_AVAILABLE:
            return {'error': 'emcee not available for MCMC'}
        
        # Simplified Bayesian estimation
        # In practice, would implement proper MCMC
        
        return {
            'method': 'MCMC (emcee)',
            'status': 'Not implemented in this example',
            'note': 'Full implementation would require significant computational resources'
        }
    
    def _calculate_parameter_distributions(self, parameter_samples: np.ndarray) -> Dict:
        """Calculate distribution statistics for parameters."""
        if len(parameter_samples) == 0:
            return {}
        
        return {
            'mean': np.mean(parameter_samples, axis=0),
            'std': np.std(parameter_samples, axis=0),
            'median': np.median(parameter_samples, axis=0),
            'percentiles': {
                '5': np.percentile(parameter_samples, 5, axis=0),
                '25': np.percentile(parameter_samples, 25, axis=0),
                '75': np.percentile(parameter_samples, 75, axis=0),
                '95': np.percentile(parameter_samples, 95, axis=0)
            },
            'skewness': stats.skew(parameter_samples, axis=0),
            'kurtosis': stats.kurtosis(parameter_samples, axis=0)
        }
    
    def _calculate_correlation_distributions(self, correlation_samples: np.ndarray) -> Dict:
        """Calculate distribution statistics for correlation matrices."""
        if len(correlation_samples) == 0:
            return {}
        
        n_assets = correlation_samples.shape[1]
        
        # Calculate mean correlation matrix
        mean_corr = np.mean(correlation_samples, axis=0)
        
        # Calculate uncertainty for each correlation
        corr_uncertainty = np.std(correlation_samples, axis=0)
        
        # Calculate probability of positive/negative correlation
        prob_positive = np.mean(correlation_samples > 0, axis=0)
        prob_negative = np.mean(correlation_samples < 0, axis=0)
        
        return {
            'mean_correlation': mean_corr,
            'correlation_uncertainty': corr_uncertainty,
            'prob_positive': prob_positive,
            'prob_negative': prob_negative,
            'correlation_stability': 1 - corr_uncertainty  # Higher = more stable
        }
    
    def _calculate_parameter_uncertainty_metrics(self, param_distributions: Dict) -> Dict:
        """Calculate metrics for parameter uncertainty."""
        metrics = {}
        
        # Uncertainty in means
        if 'means' in param_distributions:
            mean_dist = param_distributions['means']
            metrics['mean_uncertainty'] = np.mean(mean_dist.get('std', 0))
            metrics['mean_relative_uncertainty'] = \
                metrics['mean_uncertainty'] / np.abs(np.mean(mean_dist.get('mean', 1)))
        
        # Uncertainty in volatilities
        if 'volatilities' in param_distributions:
            vol_dist = param_distributions['volatilities']
            metrics['volatility_uncertainty'] = np.mean(vol_dist.get('std', 0))
            metrics['volatility_relative_uncertainty'] = \
                metrics['volatility_uncertainty'] / np.mean(vol_dist.get('mean', 1))
        
        # Uncertainty in correlations
        if 'correlations' in param_distributions:
            corr_dist = param_distributions['correlations']
            if 'correlation_uncertainty' in corr_dist:
                metrics['correlation_uncertainty'] = np.mean(corr_dist['correlation_uncertainty'])
        
        # Total parameter uncertainty (combined metric)
        uncertainty_components = [
            metrics.get('mean_relative_uncertainty', 0),
            metrics.get('volatility_relative_uncertainty', 0),
            metrics.get('correlation_uncertainty', 0)
        ]
        metrics['total_uncertainty'] = np.sqrt(sum(c**2 for c in uncertainty_components))
        
        return metrics
    
    def _extract_parameter_uncertainty_findings(self, param_distributions: Dict) -> List[str]:
        """Extract key findings from parameter uncertainty analysis."""
        findings = []
        
        if 'means' in param_distributions:
            mean_dist = param_distributions['means']
            mean_uncertainty = np.mean(mean_dist.get('std', 0))
            
            if mean_uncertainty > 0.05:
                findings.append("High uncertainty in mean return estimates")
            elif mean_uncertainty > 0.02:
                findings.append("Moderate uncertainty in mean return estimates")
            else:
                findings.append("Low uncertainty in mean return estimates")
        
        if 'volatilities' in param_distributions:
            vol_dist = param_distributions['volatilities']
            vol_uncertainty = np.mean(vol_dist.get('std', 0))
            
            if vol_uncertainty > 0.03:
                findings.append("High uncertainty in volatility estimates")
            elif vol_uncertainty > 0.01:
                findings.append("Moderate uncertainty in volatility estimates")
            else:
                findings.append("Low uncertainty in volatility estimates")
        
        if 'correlations' in param_distributions:
            corr_dist = param_distributions['correlations']
            if 'correlation_stability' in corr_dist:
                avg_stability = np.mean(corr_dist['correlation_stability'])
                
                if avg_stability < 0.7:
                    findings.append("Correlations are highly unstable")
                elif avg_stability < 0.9:
                    findings.append("Moderate correlation instability")
                else:
                    findings.append("Correlations are relatively stable")
        
        return findings
    
    def _simulate_normal_model(self, params: UncertaintyParameters) -> Dict:
        """Simulate using normal distribution model."""
        if self.historical_returns.empty:
            return {'error': 'No historical data'}
        
        n_assets = len(self.historical_returns.columns)
        n_simulations = params.n_simulations // 4  # Use subset for each model
        
        # Estimate parameters
        mu = self.historical_returns.mean().values * 252
        sigma = self.historical_returns.std().values * np.sqrt(252)
        corr = self.historical_returns.corr().values
        
        # Generate simulations
        dt = 1 / 252
        price_paths = np.zeros((n_simulations, params.n_periods + 1, n_assets))
        price_paths[:, 0, :] = 100  # Initial price
        
        # Cholesky decomposition
        try:
            L = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError:
            L = np.eye(n_assets)
        
        for s in range(n_simulations):
            Z = np.random.normal(0, 1, (params.n_periods, n_assets))
            Z = Z @ L.T  # Correlate
            
            for t in range(params.n_periods):
                for i in range(n_assets):
                    drift = (mu[i] - 0.5 * sigma[i]**2) * dt
                    diffusion = sigma[i] * np.sqrt(dt) * Z[t, i]
                    price_paths[s, t+1, i] = price_paths[s, t, i] * np.exp(drift + diffusion)
        
        # Calculate returns
        returns = (price_paths[:, -1, :] / price_paths[:, 0, :]) - 1
        
        return {
            'model_type': 'normal',
            'parameters': {'mu': mu, 'sigma': sigma, 'corr': corr},
            'price_paths': price_paths,
            'returns': returns,
            'mean_return': np.mean(returns),
            'return_std': np.std(returns)
        }
    
    def _simulate_t_distribution_model(self, params: UncertaintyParameters) -> Dict:
        """Simulate using t-distribution model (fat tails)."""
        if self.historical_returns.empty:
            return {'error': 'No historical data'}
        
        n_assets = len(self.historical_returns.columns)
        n_simulations = params.n_simulations // 4
        
        # Estimate parameters with t-distribution
        mu = self.historical_returns.mean().values * 252
        sigma = self.historical_returns.std().values * np.sqrt(252)
        corr = self.historical_returns.corr().values
        
        # Degrees of freedom for t-distribution (estimate from kurtosis)
        kurtosis = stats.kurtosis(self.historical_returns.values, axis=0)
        df = np.clip(6 / kurtosis + 4, 3, 100)  # Ensure reasonable values
        
        dt = 1 / 252
        price_paths = np.zeros((n_simulations, params.n_periods + 1, n_assets))
        price_paths[:, 0, :] = 100
        
        # Cholesky decomposition
        try:
            L = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError:
            L = np.eye(n_assets)
        
        for s in range(n_simulations):
            # Generate t-distributed random numbers
            t_vars = []
            for i in range(n_assets):
                t_var = stats.t.rvs(df[i], size=params.n_periods)
                t_vars.append(t_var)
            
            Z = np.column_stack(t_vars)
            Z = Z @ L.T  # Correlate
            
            for t in range(params.n_periods):
                for i in range(n_assets):
                    # Adjust for t-distribution variance
                    scale_factor = np.sqrt(df[i] / (df[i] - 2)) if df[i] > 2 else 1
                    adjusted_sigma = sigma[i] / scale_factor
                    
                    drift = (mu[i] - 0.5 * adjusted_sigma**2) * dt
                    diffusion = adjusted_sigma * np.sqrt(dt) * Z[t, i]
                    price_paths[s, t+1, i] = price_paths[s, t, i] * np.exp(drift + diffusion)
        
        returns = (price_paths[:, -1, :] / price_paths[:, 0, :]) - 1
        
        return {
            'model_type': 't_distribution',
            'parameters': {'mu': mu, 'sigma': sigma, 'corr': corr, 'df': df},
            'price_paths': price_paths,
            'returns': returns,
            'mean_return': np.mean(returns),
            'return_std': np.std(returns),
            'excess_kurtosis': np.mean(stats.kurtosis(returns, axis=0))
        }
    
    def _simulate_garch_model(self, params: UncertaintyParameters) -> Dict:
        """Simulate using GARCH model (volatility clustering)."""
        # Simplified GARCH simulation
        if self.historical_returns.empty:
            return {'error': 'No historical data'}
        
        n_assets = len(self.historical_returns.columns)
        n_simulations = params.n_simulations // 4
        
        # Use simplified GARCH(1,1) parameters
        mu = self.historical_returns.mean().values * 252
        sigma = self.historical_returns.std().values * np.sqrt(252)
        corr = self.historical_returns.corr().values
        
        dt = 1 / 252
        price_paths = np.zeros((n_simulations, params.n_periods + 1, n_assets))
        price_paths[:, 0, :] = 100
        
        # GARCH parameters (simplified)
        omega = 0.05 * sigma**2  # Long-term variance
        alpha = 0.1  # ARCH parameter
        beta = 0.85  # GARCH parameter
        
        # Cholesky decomposition
        try:
            L = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError:
            L = np.eye(n_assets)
        
        for s in range(n_simulations):
            # Initialize volatility
            volatility = np.copy(sigma)
            
            for t in range(params.n_periods):
                # Generate correlated random numbers
                Z = np.random.normal(0, 1, n_assets)
                Z = Z @ L.T
                
                for i in range(n_assets):
                    # Update volatility (GARCH process)
                    if t > 0:
                        # Use previous return for volatility update
                        prev_return = (price_paths[s, t, i] / price_paths[s, t-1, i] - 1) * np.sqrt(252)
                        volatility[i] = np.sqrt(
                            omega[i] + 
                            alpha * (prev_return - mu[i]*dt)**2 + 
                            beta * volatility[i]**2
                        )
                    
                    # Price update
                    drift = (mu[i] - 0.5 * volatility[i]**2) * dt
                    diffusion = volatility[i] * np.sqrt(dt) * Z[i]
                    price_paths[s, t+1, i] = price_paths[s, t, i] * np.exp(drift + diffusion)
        
        returns = (price_paths[:, -1, :] / price_paths[:, 0, :]) - 1
        
        return {
            'model_type': 'garch',
            'parameters': {'mu': mu, 'sigma': sigma, 'corr': corr, 'omega': omega, 'alpha': alpha, 'beta': beta},
            'price_paths': price_paths,
            'returns': returns,
            'mean_return': np.mean(returns),
            'return_std': np.std(returns),
            'volatility_clustering': self._calculate_volatility_clustering(price_paths)
        }
    
    def _simulate_regime_switching_model(self, params: UncertaintyParameters) -> Dict:
        """Simulate using regime switching model."""
        # Simplified regime switching simulation
        if self.historical_returns.empty:
            return {'error': 'No historical data'}
        
        n_assets = len(self.historical_returns.columns)
        n_simulations = params.n_simulations // 4
        
        # Define two regimes: high and low volatility
        mu_low = self.historical_returns.mean().values * 252
        sigma_low = self.historical_returns.std().values * np.sqrt(252)
        
        mu_high = mu_low * 0.8  # Lower returns in high volatility
        sigma_high = sigma_low * 1.5  # Higher volatility
        
        # Transition probabilities
        p_stay_low = 0.95
        p_stay_high = 0.90
        transition_matrix = np.array([
            [p_stay_low, 1 - p_stay_low],
            [1 - p_stay_high, p_stay_high]
        ])
        
        dt = 1 / 252
        price_paths = np.zeros((n_simulations, params.n_periods + 1, n_assets))
        price_paths[:, 0, :] = 100
        regime_paths = np.zeros((n_simulations, params.n_periods + 1), dtype=int)
        
        # Correlation (same for both regimes)
        corr = self.historical_returns.corr().values
        try:
            L = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError:
            L = np.eye(n_assets)
        
        for s in range(n_simulations):
            # Start in low volatility regime
            current_regime = 0
            
            for t in range(params.n_periods):
                # Transition to next regime
                probs = transition_matrix[current_regime]
                next_regime = np.random.choice(2, p=probs)
                regime_paths[s, t+1] = next_regime
                
                # Get regime parameters
                if next_regime == 0:
                    mu = mu_low
                    sigma = sigma_low
                else:
                    mu = mu_high
                    sigma = sigma_high
                
                # Generate random numbers
                Z = np.random.normal(0, 1, n_assets)
                Z = Z @ L.T
                
                # Update prices
                for i in range(n_assets):
                    drift = (mu[i] - 0.5 * sigma[i]**2) * dt
                    diffusion = sigma[i] * np.sqrt(dt) * Z[i]
                    price_paths[s, t+1, i] = price_paths[s, t, i] * np.exp(drift + diffusion)
                
                current_regime = next_regime
        
        returns = (price_paths[:, -1, :] / price_paths[:, 0, :]) - 1
        
        return {
            'model_type': 'regime_switching',
            'parameters': {
                'mu_low': mu_low, 'sigma_low': sigma_low,
                'mu_high': mu_high, 'sigma_high': sigma_high,
                'transition_matrix': transition_matrix
            },
            'price_paths': price_paths,
            'regime_paths': regime_paths,
            'returns': returns,
            'mean_return': np.mean(returns),
            'return_std': np.std(returns),
            'regime_fraction': np.mean(regime_paths == 1)  # Fraction in high volatility
        }
    
    def _calculate_model_uncertainty_metrics(self, model_results: Dict) -> Dict:
        """Calculate metrics for model uncertainty."""
        metrics = {}
        
        # Collect performance metrics from each model
        model_performances = []
        model_volatilities = []
        
        for model_name, results in model_results.items():
            if 'mean_return' in results:
                model_performances.append(results['mean_return'])
            if 'return_std' in results:
                model_volatilities.append(results['return_std'])
        
        if model_performances:
            metrics['model_disagreement'] = np.std(model_performances) / np.abs(np.mean(model_performances)) \
                if np.mean(np.abs(model_performances)) > 0 else 0
            
            metrics['performance_range'] = max(model_performances) - min(model_performances)
            metrics['mean_performance'] = np.mean(model_performances)
            
            # Calculate model risk as disagreement normalized by average volatility
            if model_volatilities:
                avg_volatility = np.mean(model_volatilities)
                if avg_volatility > 0:
                    metrics['model_risk'] = metrics['model_disagreement'] / avg_volatility
                else:
                    metrics['model_risk'] = metrics['model_disagreement']
        
        return metrics
    
    def _compare_models(self, model_results: Dict) -> pd.DataFrame:
        """Compare different models."""
        comparison_data = []
        
        for model_name, results in model_results.items():
            row = {
                'Model': model_name,
                'Mean Return': results.get('mean_return', np.nan),
                'Return Std': results.get('return_std', np.nan),
                'Sharpe Ratio': results.get('mean_return', 0) / results.get('return_std', 1) if results.get('return_std', 0) > 0 else 0
            }
            
            # Add model-specific metrics
            if model_name == 't_distribution' and 'excess_kurtosis' in results:
                row['Excess Kurtosis'] = results['excess_kurtosis']
            elif model_name == 'garch' and 'volatility_clustering' in results:
                row['Volatility Clustering'] = results['volatility_clustering']
            elif model_name == 'regime_switching' and 'regime_fraction' in results:
                row['High Vol Regime %'] = results['regime_fraction']
            
            comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def _select_best_model(self, model_comparison: pd.DataFrame) -> str:
        """Select the best model based on multiple criteria."""
        if model_comparison.empty:
            return "No models available"
        
        # Simple selection: highest Sharpe ratio
        if 'Sharpe Ratio' in model_comparison.columns:
            best_idx = model_comparison['Sharpe Ratio'].idxmax()
            return model_comparison.loc[best_idx, 'Model']
        
        # Fallback: first model
        return model_comparison.iloc[0]['Model']
    
    def _calculate_model_risk(self, model_results: Dict) -> float:
        """Calculate model risk score."""
        if not model_results:
            return 0.0
        
        # Calculate disagreement among models
        returns = []
        for results in model_results.values():
            if 'mean_return' in results:
                returns.append(results['mean_return'])
        
        if len(returns) < 2:
            return 0.0
        
        # Model risk = standard deviation of model predictions
        model_risk = np.std(returns)
        
        # Normalize by average absolute return
        avg_return = np.mean(np.abs(returns))
        if avg_return > 0:
            model_risk /= avg_return
        
        return model_risk
    
    def _bootstrap_confidence_intervals(self, n_bootstrap: int) -> Dict:
        """Calculate bootstrap confidence intervals."""
        if self.historical_returns.empty:
            return {}
        
        n_obs = len(self.historical_returns)
        
        # Bootstrap sample statistics
        bootstrap_stats = {
            'mean': [],
            'volatility': [],
            'sharpe': []
        }
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            sample_indices = np.random.choice(n_obs, size=n_obs, replace=True)
            bootstrap_sample = self.historical_returns.iloc[sample_indices]
            
            # Calculate statistics
            mean_return = bootstrap_sample.mean().mean() * 252
            volatility = bootstrap_sample.std().mean() * np.sqrt(252)
            
            bootstrap_stats['mean'].append(mean_return)
            bootstrap_stats['volatility'].append(volatility)
            
            if volatility > 0:
                sharpe = mean_return / volatility
                bootstrap_stats['sharpe'].append(sharpe)
        
        # Calculate confidence intervals
        cis = {}
        for stat_name, values in bootstrap_stats.items():
            if values:
                cis[stat_name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'ci_95_lower': np.percentile(values, 2.5),
                    'ci_95_upper': np.percentile(values, 97.5),
                    'ci_90_lower': np.percentile(values, 5),
                    'ci_90_upper': np.percentile(values, 95)
                }
        
        return cis
    
    def _analytical_confidence_intervals(self) -> Dict:
        """Calculate analytical confidence intervals."""
        if self.historical_returns.empty:
            return {}
        
        n_obs = len(self.historical_returns)
        
        # Mean return CI (assuming normality)
        sample_mean = self.historical_returns.mean().mean() * 252
        sample_std = self.historical_returns.std().mean() * np.sqrt(252)
        
        # Standard error of the mean
        sem = sample_std / np.sqrt(n_obs)
        
        # t-value for 95% CI
        t_value = stats.t.ppf(0.975, n_obs - 1)
        
        mean_ci = {
            'mean': sample_mean,
            'se': sem,
            'ci_95_lower': sample_mean - t_value * sem,
            'ci_95_upper': sample_mean + t_value * sem
        }
        
        # Volatility CI (using chi-square distribution)
        volatility_ci = {
            'volatility': sample_std,
            'ci_95_lower': sample_std * np.sqrt((n_obs - 1) / stats.chi2.ppf(0.975, n_obs - 1)),
            'ci_95_upper': sample_std * np.sqrt((n_obs - 1) / stats.chi2.ppf(0.025, n_obs - 1))
        }
        
        return {
            'mean': mean_ci,
            'volatility': volatility_ci
        }
    
    def _subsampling_analysis(self) -> Dict:
        """Analyze uncertainty using subsampling."""
        if self.historical_returns.empty:
            return {}
        
        n_obs = len(self.historical_returns)
        
        # Different subsample sizes
        sample_sizes = [int(n_obs * 0.5), int(n_obs * 0.7), int(n_obs * 0.9)]
        
        results = {}
        for size in sample_sizes:
            size_results = {
                'mean': [],
                'volatility': []
            }
            
            # Multiple subsamples
            for _ in range(100):
                if size >= n_obs:
                    subsample = self.historical_returns
                else:
                    indices = np.random.choice(n_obs, size=size, replace=False)
                    subsample = self.historical_returns.iloc[indices]
                
                mean_return = subsample.mean().mean() * 252
                volatility = subsample.std().mean() * np.sqrt(252)
                
                size_results['mean'].append(mean_return)
                size_results['volatility'].append(volatility)
            
            results[f'size_{size}'] = {
                'mean_mean': np.mean(size_results['mean']),
                'mean_std': np.std(size_results['mean']),
                'vol_mean': np.mean(size_results['volatility']),
                'vol_std': np.std(size_results['volatility'])
            }
        
        return results
    
    def _analyze_sample_size_effect(self) -> Dict:
        """Analyze how uncertainty changes with sample size."""
        # Theoretical relationship: uncertainty ∝ 1/√n
        return {
            'theoretical_scaling': '1 / sqrt(n)',
            'note': 'Estimation uncertainty decreases with square root of sample size'
        }
    
    def _calculate_estimation_error(self, bootstrap_cis: Dict, analytical_cis: Dict) -> float:
        """Calculate estimation error metric."""
        # Compare bootstrap and analytical CIs
        if not bootstrap_cis or not analytical_cis:
            return 0.0
        
        # Focus on mean estimate
        if 'mean' in bootstrap_cis and 'mean' in analytical_cis:
            bootstrap_mean = bootstrap_cis['mean'].get('mean', 0)
            analytical_mean = analytical_cis['mean'].get('mean', 0)
            
            if analytical_mean != 0:
                return abs(bootstrap_mean - analytical_mean) / abs(analytical_mean)
        
        return 0.0
    
    def _estimate_convergence_rate(self) -> float:
        """Estimate convergence rate of estimates."""
        # Simplified: estimate how quickly statistics converge
        if self.historical_returns.empty:
            return 0.0
        
        n_obs = len(self.historical_returns)
        
        # Calculate rolling statistics
        rolling_means = self.historical_returns.rolling(window=63).mean().dropna()
        
        # Measure convergence: how much do later estimates differ from final estimate?
        final_mean = self.historical_returns.mean().mean()
        
        if len(rolling_means) > 0:
            # Average absolute deviation from final mean
            convergence_error = (rolling_means - final_mean).abs().mean().mean()
            
            # Normalize by final mean
            if final_mean != 0:
                convergence_rate = 1 - (convergence_error / abs(final_mean))
                return max(0, min(1, convergence_rate))
        
        return 0.8  # Default reasonable value
    
    def _calculate_effective_sample_size(self) -> float:
        """Calculate effective sample size accounting for autocorrelation."""
        if self.historical_returns.empty:
            return 0.0
        
        n_obs = len(self.historical_returns)
        
        # Calculate autocorrelation
        autocorr = self.historical_returns.apply(
            lambda x: x.autocorr(lag=1)
        ).mean()
        
        # Adjust for autocorrelation
        if autocorr != 1:
            effective_size = n_obs * (1 - autocorr) / (1 + autocorr)
        else:
            effective_size = n_obs
        
        return effective_size
    
    def _recommend_minimum_sample_size(self) -> int:
        """Recommend minimum sample size for reliable estimates."""
        # Based on desired precision
        desired_precision = 0.1  # 10% relative error
        
        # Using formula: n ≈ (z * σ / (precision * μ))^2
        # For typical values: z=1.96 (95% CI), σ/μ ≈ 2 (sharpe ratio inverse)
        
        required_n = (1.96 * 2 / desired_precision) ** 2
        return int(np.ceil(required_n))
    
    def _detect_market_regimes(self) -> List[Dict]:
        """Detect different market regimes in historical data."""
        if self.historical_returns.empty:
            return []
        
        # Simple regime detection based on volatility
        returns_series = self.historical_returns.mean(axis=1)  # Average across assets
        
        # Calculate rolling volatility
        window = 63  # 3 months
        rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252)
        rolling_vol = rolling_vol.dropna()
        
        if len(rolling_vol) == 0:
            return []
        
        # Detect regimes based on volatility thresholds
        vol_median = rolling_vol.median()
        vol_std = rolling_vol.std()
        
        regimes = []
        current_regime = None
        regime_start = None
        
        for i, (date, vol) in enumerate(rolling_vol.items()):
            if vol < vol_median - vol_std:
                regime_type = 'low_volatility'
            elif vol > vol_median + vol_std:
                regime_type = 'high_volatility'
            else:
                regime_type = 'normal'
            
            if current_regime != regime_type:
                if current_regime is not None and regime_start is not None:
                    # End previous regime
                    regimes.append({
                        'type': current_regime,
                        'start': regime_start,
                        'end': date,
                        'duration': (date - regime_start).days,
                        'avg_volatility': rolling_vol.loc[regime_start:date].mean()
                    })
                
                # Start new regime
                current_regime = regime_type
                regime_start = date
        
        # Add final regime
        if current_regime is not None and regime_start is not None:
            regimes.append({
                'type': current_regime,
                'start': regime_start,
                'end': rolling_vol.index[-1],
                'duration': (rolling_vol.index[-1] - regime_start).days,
                'avg_volatility': rolling_vol.loc[regime_start:].mean()
            })
        
        return regimes
    
    def _analyze_regime_characteristics(self, regimes: List[Dict]) -> Dict:
        """Analyze characteristics of different regimes."""
        if not regimes:
            return {}
        
        # Group by regime type
        regime_types = {}
        for regime in regimes:
            regime_type = regime['type']
            if regime_type not in regime_types:
                regime_types[regime_type] = {
                    'count': 0,
                    'total_duration': 0,
                    'volatilities': []
                }
            
            regime_types[regime_type]['count'] += 1
            regime_types[regime_type]['total_duration'] += regime['duration']
            regime_types[regime_type]['volatilities'].append(regime['avg_volatility'])
        
        # Calculate statistics
        characteristics = {}
        for regime_type, data in regime_types.items():
            characteristics[regime_type] = {
                'frequency': data['count'] / len(regimes),
                'avg_duration': data['total_duration'] / data['count'],
                'avg_volatility': np.mean(data['volatilities']),
                'volatility_std': np.std(data['volatilities'])
            }
        
        return characteristics
    
    def _simulate_regime_switching(self, n_simulations: int, regimes: List[Dict]) -> Dict:
        """Simulate regime switching process."""
        if not regimes:
            return {}
        
        # Extract regime transition probabilities
        regime_types = [r['type'] for r in regimes]
        unique_regimes = list(set(regime_types))
        
        # Count transitions
        transition_counts = {}
        for i in range(len(regime_types) - 1):
            from_regime = regime_types[i]
            to_regime = regime_types[i + 1]
            
            if from_regime not in transition_counts:
                transition_counts[from_regime] = {}
            if to_regime not in transition_counts[from_regime]:
                transition_counts[from_regime][to_regime] = 0
            
            transition_counts[from_regime][to_regime] += 1
        
        # Calculate transition probabilities
        transition_probs = {}
        for from_regime, counts in transition_counts.items():
            total = sum(counts.values())
            transition_probs[from_regime] = {
                to_regime: count / total for to_regime, count in counts.items()
            }
        
        # Simulate regime paths
        simulated_regimes = []
        for _ in range(n_simulations):
            # Start with most common regime
            current_regime = max(set(regime_types), key=regime_types.count)
            regime_path = [current_regime]
            
            for _ in range(100):  # Simulate 100 periods
                if current_regime in transition_probs:
                    # Choose next regime based on transition probabilities
                    next_regimes = list(transition_probs[current_regime].keys())
                    next_probs = list(transition_probs[current_regime].values())
                    
                    # Ensure probabilities sum to 1
                    if sum(next_probs) > 0:
                        next_probs = [p / sum(next_probs) for p in next_probs]
                        current_regime = np.random.choice(next_regimes, p=next_probs)
                    else:
                        # Stay in same regime if no transition data
                        pass
                
                regime_path.append(current_regime)
            
            simulated_regimes.append(regime_path)
        
        return {
            'transition_probabilities': transition_probs,
            'simulated_regime_paths': simulated_regimes,
            'regime_stationary_distribution': self._calculate_stationary_distribution(transition_probs)
        }
    
    def _calculate_regime_uncertainty_metrics(self, regime_characteristics: Dict, 
                                            regime_simulations: Dict) -> Dict:
        """Calculate metrics for regime uncertainty."""
        metrics = {}
        
        if regime_characteristics:
            # Volatility variation across regimes
            regime_volatilities = [char['avg_volatility'] for char in regime_characteristics.values()]
            metrics['regime_volatility'] = np.std(regime_volatilities) / np.mean(regime_volatilities) \
                if np.mean(regime_volatilities) > 0 else 0
            
            # Regime persistence
            avg_durations = [char['avg_duration'] for char in regime_characteristics.values()]
            metrics['avg_regime_duration'] = np.mean(avg_durations)
        
        if regime_simulations and 'regime_stationary_distribution' in regime_simulations:
            stationary = regime_simulations['regime_stationary_distribution']
            if stationary:
                # Entropy of stationary distribution (measure of uncertainty)
                probs = list(stationary.values())
                entropy = -sum(p * np.log(p) for p in probs if p > 0)
                max_entropy = np.log(len(probs))
                
                metrics['regime_entropy'] = entropy
                metrics['regime_entropy_normalized'] = entropy / max_entropy if max_entropy > 0 else 0
        
        return metrics
    
    def _analyze_regime_transitions(self, regimes: List[Dict]) -> Dict:
        """Analyze regime transition patterns."""
        if len(regimes) < 2:
            return {}
        
        # Calculate time between regime changes
        transition_times = []
        for i in range(len(regimes) - 1):
            transition_time = (regimes[i + 1]['start'] - regimes[i]['end']).days
            transition_times.append(transition_time)
        
        return {
            'avg_transition_time': np.mean(transition_times) if transition_times else 0,
            'transition_time_std': np.std(transition_times) if transition_times else 0,
            'n_transitions': len(transition_times)
        }
    
    def _calculate_regime_persistence(self, regimes: List[Dict]) -> float:
        """Calculate regime persistence metric."""
        if len(regimes) < 2:
            return 1.0  # Perfect persistence if only one regime
        
        # Count regime changes
        regime_types = [r['type'] for r in regimes]
        changes = 0
        for i in range(len(regime_types) - 1):
            if regime_types[i] != regime_types[i + 1]:
                changes += 1
        
        # Persistence = 1 - (changes / (n_regimes - 1))
        persistence = 1 - (changes / (len(regimes) - 1))
        return persistence
    
    def _forecast_regime_probabilities(self, regimes: List[Dict]) -> Dict:
        """Forecast probabilities of being in each regime."""
        if not regimes:
            return {}
        
        # Simple forecast: use frequency of past regimes
        regime_types = [r['type'] for r in regimes]
        unique_regimes = list(set(regime_types))
        
        probabilities = {}
        for regime in unique_regimes:
            frequency = regime_types.count(regime) / len(regime_types)
            probabilities[regime] = frequency
        
        return probabilities
    
    def _estimate_uncertainty_correlations(self, uncertainty_sources: Dict) -> np.ndarray:
        """Estimate correlations between different uncertainty sources."""
        # Simplified correlation estimation
        # In practice, would use more sophisticated methods
        
        n_sources = len(uncertainty_sources)
        if n_sources < 2:
            return np.eye(1)
        
        # Default correlation matrix (assuming moderate positive correlations)
        corr = np.eye(n_sources) * 0.5 + np.ones((n_sources, n_sources)) * 0.5 / n_sources
        
        # Ensure positive definiteness
        eigenvalues = np.linalg.eigvals(corr)
        if np.any(eigenvalues <= 0):
            corr = self._nearest_pos_def(corr)
        
        return corr
    
    def _correlated_combination(self, uncertainties: List[float], 
                              correlations: np.ndarray) -> float:
        """Combine uncertainties accounting for correlations."""
        if not uncertainties:
            return 0.0
        
        uncertainties = np.array(uncertainties)
        
        if len(uncertainties) == 1:
            return uncertainties[0]
        
        # Ensure correlation matrix matches uncertainties
        if correlations.shape[0] != len(uncertainties):
            # Use identity matrix if sizes don't match
            correlations = np.eye(len(uncertainties))
        
        # Combined uncertainty = sqrt(u' * R * u)
        combined = np.sqrt(uncertainties.T @ correlations @ uncertainties)
        return combined
    
    def _monte_carlo_combination(self, uncertainty_sources: Dict, 
                               n_simulations: int) -> float:
        """Combine uncertainties using Monte Carlo simulation."""
        # Extract uncertainty distributions
        distributions = []
        
        for source_name, source_data in uncertainty_sources.items():
            if 'uncertainty_metrics' in source_data:
                metrics = source_data['uncertainty_metrics']
                
                # Extract relevant uncertainty metric
                if 'total_uncertainty' in metrics:
                    uncertainty = metrics['total_uncertainty']
                    # Assume normal distribution for simplicity
                    distributions.append({
                        'mean': uncertainty,
                        'std': uncertainty * 0.3  # 30% uncertainty about uncertainty
                    })
        
        if not distributions:
            return 0.0
        
        # Generate Monte Carlo samples
        samples = []
        for _ in range(n_simulations):
            combined = 0
            for dist in distributions:
                sample = np.random.normal(dist['mean'], dist['std'])
                combined += sample
            
            samples.append(combined)
        
        return np.mean(samples)
    
    def _recommend_uncertainty_metric(self, combined_metrics: Dict) -> str:
        """Recommend which uncertainty metric to use."""
        # Prefer correlated combination if available
        if 'correlated' in combined_metrics:
            return 'correlated'
        elif 'rss' in combined_metrics:
            return 'rss'
        elif 'monte_carlo' in combined_metrics:
            return 'monte_carlo'
        else:
            return 'additive'
    
    def _calculate_single_confidence_interval(self, confidence_level: float) -> Dict:
        """Calculate confidence interval for strategy performance."""
        if self.strategy_performance is None or self.strategy_performance.empty:
            # Use simulated data if available
            if self.simulation_results:
                # Extract returns from simulations
                all_returns = []
                for model_results in self.simulation_results.values():
                    if 'returns' in model_results:
                        returns_flat = model_results['returns'].flatten()
                        all_returns.extend(returns_flat)
                
                if all_returns:
                    returns_array = np.array(all_returns)
                else:
                    return {'error': 'No performance data available'}
            else:
                return {'error': 'No performance data available'}
        else:
            returns_array = self.strategy_performance.values
        
        # Calculate confidence interval
        alpha = 1 - confidence_level
        lower = np.percentile(returns_array, alpha/2 * 100)
        upper = np.percentile(returns_array, (1 - alpha/2) * 100)
        mean = np.mean(returns_array)
        median = np.median(returns_array)
        
        return {
            'mean': mean,
            'median': median,
            'lower': lower,
            'upper': upper,
            'width': upper - lower,
            'confidence_level': confidence_level
        }
    
    def _calculate_prediction_intervals(self, confidence_levels: List[float]) -> Dict:
        """Calculate prediction intervals (wider than confidence intervals)."""
        if self.strategy_performance is None or self.strategy_performance.empty:
            return {}
        
        returns = self.strategy_performance.values
        n = len(returns)
        
        prediction_intervals = {}
        
        for level in confidence_levels:
            alpha = 1 - level
            
            # Prediction interval: accounts for both parameter uncertainty and future randomness
            mean = np.mean(returns)
            std = np.std(returns)
            
            # t-value for prediction interval
            t_value = stats.t.ppf(1 - alpha/2, n - 1)
            
            # Standard error for prediction
            # Includes both estimation error and inherent variability
            prediction_se = std * np.sqrt(1 + 1/n)
            
            lower = mean - t_value * prediction_se
            upper = mean + t_value * prediction_se
            
            prediction_intervals[f'pi_{int(level*100)}'] = {
                'mean': mean,
                'lower': lower,
                'upper': upper,
                'width': upper - lower,
                'confidence_level': level
            }
        
        return prediction_intervals
    
    def _calculate_credible_intervals(self, bayesian_params: Dict, 
                                    confidence_levels: List[float]) -> Dict:
        """Calculate Bayesian credible intervals."""
        # Simplified implementation
        # In practice, would use actual posterior samples
        
        credible_intervals = {}
        
        for level in confidence_levels:
            # Placeholder: same as confidence intervals for now
            ci = self._calculate_single_confidence_interval(level)
            credible_intervals[f'credible_{int(level*100)}'] = ci
        
        return credible_intervals
    
    def _compare_interval_methods(self, confidence_intervals: Dict,
                                prediction_intervals: Dict,
                                credible_intervals: Dict) -> Dict:
        """Compare different interval calculation methods."""
        comparison = {}
        
        # Compare widths at 95% level
        if 'ci_95' in confidence_intervals:
            comparison['confidence_interval_width'] = confidence_intervals['ci_95'].get('width', 0)
        
        if 'pi_95' in prediction_intervals:
            comparison['prediction_interval_width'] = prediction_intervals['pi_95'].get('width', 0)
            
            # Calculate ratio
            if comparison.get('confidence_interval_width', 0) > 0:
                comparison['width_ratio'] = (
                    comparison['prediction_interval_width'] / 
                    comparison['confidence_interval_width']
                )
        
        if 'credible_95' in credible_intervals:
            comparison['credible_interval_width'] = credible_intervals['credible_95'].get('width', 0)
        
        return comparison
    
    def _generate_uncertainty_recommendations(self) -> List[str]:
        """Generate recommendations based on uncertainty analysis."""
        recommendations = []
        
        if not self.uncertainty_metrics:
            recommendations.append("Run comprehensive uncertainty analysis first")
            return recommendations
        
        # Check combined uncertainty
        combined = self.uncertainty_metrics.get('combined_uncertainty', {})
        if combined:
            uncertainty_metric = combined.get('recommended_uncertainty_metric', '')
            uncertainty_value = combined.get('combined_metrics', {}).get(uncertainty_metric, 0)
            
            if uncertainty_value > 0.3:
                recommendations.append("Very high uncertainty: Consider reducing position sizes by 50% or more")
            elif uncertainty_value > 0.2:
                recommendations.append("High uncertainty: Consider reducing position sizes by 25-50%")
            elif uncertainty_value > 0.1:
                recommendations.append("Moderate uncertainty: Maintain normal position sizes with close monitoring")
            else:
                recommendations.append("Low uncertainty: Normal position sizing appropriate")
        
        # Check primary uncertainty source
        if 'primary_uncertainty_source' in combined:
            primary_source = combined['primary_uncertainty_source']
            
            if primary_source == 'parameter':
                recommendations.append("Focus on improving parameter estimation with more data or better methods")
            elif primary_source == 'model':
                recommendations.append("Use model averaging or ensemble methods to reduce model uncertainty")
            elif primary_source == 'estimation':
                recommendations.append("Collect more data to reduce estimation uncertainty")
            elif primary_source == 'regime':
                recommendations.append("Implement regime detection and adaptive strategies")
        
        # General recommendations
        recommendations.append("Use conservative confidence intervals (e.g., 99% instead of 95%)")
        recommendations.append("Regularly update uncertainty estimates as new data arrives")
        recommendations.append("Consider worst-case scenarios in risk management")
        recommendations.append("Document uncertainty assumptions and limitations")
        
        return recommendations
    
    def _calculate_volatility_clustering(self, price_paths: np.ndarray) -> float:
        """Calculate volatility clustering metric."""
        if len(price_paths.shape) != 3:
            return 0.0
        
        n_simulations, n_periods, n_assets = price_paths.shape
        
        # Calculate returns
        returns = np.zeros((n_simulations, n_periods - 1, n_assets))
        for s in range(n_simulations):
            for t in range(1, n_periods):
                returns[s, t-1] = (price_paths[s, t] / price_paths[s, t-1]) - 1
        
        # Calculate autocorrelation of squared returns (volatility clustering)
        autocorrs = []
        for s in range(min(10, n_simulations)):  # Use subset for efficiency
            for i in range(n_assets):
                squared_returns = returns[s, :, i] ** 2
                if len(squared_returns) > 1:
                    autocorr = np.corrcoef(squared_returns[:-1], squared_returns[1:])[0, 1]
                    if not np.isnan(autocorr):
                        autocorrs.append(autocorr)
        
        return np.mean(autocorrs) if autocorrs else 0.0
    
    def _calculate_stationary_distribution(self, transition_probs: Dict) -> Dict:
        """Calculate stationary distribution of Markov chain."""
        if not transition_probs:
            return {}
        
        # Convert to matrix form
        states = list(transition_probs.keys())
        n_states = len(states)
        
        # Build transition matrix
        P = np.zeros((n_states, n_states))
        for i, from_state in enumerate(states):
            for j, to_state in enumerate(states):
                P[i, j] = transition_probs.get(from_state, {}).get(to_state, 0)
            
            # Normalize row
            if P[i].sum() > 0:
                P[i] = P[i] / P[i].sum()
            else:
                # If no transitions from this state, stay put
                P[i, i] = 1
        
        # Find stationary distribution (eigenvector with eigenvalue 1)
        eigenvalues, eigenvectors = np.linalg.eig(P.T)
        
        # Find eigenvalue closest to 1
        idx = np.argmin(np.abs(eigenvalues - 1))
        stationary = np.real(eigenvectors[:, idx])
        
        # Normalize to sum to 1
        if stationary.sum() > 0:
            stationary = stationary / stationary.sum()
        
        # Return as dictionary
        return {state: stationary[i] for i, state in enumerate(states)}
    
    def _nearest_pos_def(self, A: np.ndarray) -> np.ndarray:
        """Find the nearest positive definite matrix."""
        # Symmetrize
        B = (A + A.T) / 2
        
        # Compute eigendecomposition
        eigvals, eigvecs = np.linalg.eigh(B)
        
        # Ensure eigenvalues are positive
        eigvals = np.maximum(eigvals, 1e-8)
        
        # Reconstruct matrix
        A_pos = eigvecs @ np.diag(eigvals) @ eigvecs.T
        
        return A_pos


def main():
    """Demonstration of uncertainty quantification framework."""
    print("Day 83: Monte Carlo Simulations for Uncertainty Modeling")
    print("=" * 80)
    
    # Generate sample historical returns
    np.random.seed(42)
    n_days = 252 * 5  # 5 years of daily data
    dates = pd.date_range('2018-01-01', periods=n_days, freq='B')
    
    # Generate returns with some structure
    base_volatility = 0.15 / np.sqrt(252)  # 15% annual
    
    # Create synthetic returns with regimes
    returns = np.zeros(n_days)
    
    # Regime 1: Low volatility (first 2 years)
    returns[:504] = np.random.normal(0.0005, base_volatility * 0.7, 504)
    
    # Regime 2: High volatility (next 1.5 years)
    returns[504:882] = np.random.normal(0.0002, base_volatility * 1.5, 378)
    
    # Regime 3: Medium volatility (last 1.5 years)
    returns[882:] = np.random.normal(0.0004, base_volatility, n_days - 882)
    
    # Add some autocorrelation (volatility clustering)
    for i in range(1, n_days):
        returns[i] = returns[i] * 0.7 + returns[i-1] * 0.3
    
    # Create DataFrame
    historical_returns = pd.DataFrame({
        'Strategy_Returns': returns
    }, index=dates)
    
    print("\nSample Historical Data:")
    print(f"Period: {dates[0].date()} to {dates[-1].date()}")
    print(f"Days: {n_days}")
    print(f"Mean Return (annualized): {historical_returns.mean().iloc[0]*252:.2%}")
    print(f"Volatility (annualized): {historical_returns.std().iloc[0]*np.sqrt(252):.2%}")
    print()
    
    # Initialize uncertainty quantifier
    print("Initializing Uncertainty Quantifier...")
    quantifier = UncertaintyQuantifier(
        historical_returns=historical_returns,
        strategy_performance=historical_returns['Strategy_Returns']
    )
    
    # Set parameters
    params = UncertaintyParameters(
        n_simulations=1000,
        n_periods=252,
        initial_capital=100000,
        risk_free_rate=0.02,
        model_uncertainty=True,
        parameter_uncertainty=True,
        estimation_uncertainty=True,
        regime_uncertainty=True,
        use_bayesian=False,  # Requires emcee
        use_bootstrap=True,
        use_gaussian_process=False,  # Requires scikit-learn
        confidence_levels=[0.90, 0.95, 0.99],
        seed=42
    )
    
    # Run comprehensive analysis
    print("\nRunning Comprehensive Uncertainty Analysis...")
    print("-" * 60)
    
    analysis_results = quantifier.run_comprehensive_uncertainty_analysis(params)
    
    print("\n✅ Analysis completed successfully!")
    print()
    
    # Display key results
    print("📊 KEY UNCERTAINTY METRICS")
    print("-" * 40)
    
    # Combined uncertainty
    combined = analysis_results.get('combined_uncertainty', {})
    if combined:
        uncertainty_components = combined.get('uncertainty_components', {})
        decomposition = combined.get('uncertainty_decomposition', {})
        
        print("\nCombined Uncertainty Analysis:")
        print(f"  Recommended Metric: {combined.get('recommended_uncertainty_metric', 'N/A')}")
        
        if 'correlated' in combined.get('combined_metrics', {}):
            uncertainty = combined['combined_metrics']['correlated']
            print(f"  Total Uncertainty: {uncertainty:.3f}")
        
        print("\nUncertainty Decomposition:")
        for source, proportion in decomposition.items():
            print(f"  {source.title():15}: {proportion:.1%}")
    
    # Confidence intervals
    confidence = analysis_results.get('confidence_intervals', {})
    if 'confidence_intervals' in confidence:
        print("\nConfidence Intervals (Returns):")
        cis = confidence['confidence_intervals']
        
        if 'ci_95' in cis:
            ci = cis['ci_95']
            print(f"  95% CI: [{ci['lower']:.2%}, {ci['upper']:.2%}]")
            print(f"  Width: {ci['width']:.2%}")
        
        if 'ci_99' in cis:
            ci = cis['ci_99']
            print(f"  99% CI: [{ci['lower']:.2%}, {ci['upper']:.2%}]")
            print(f"  Width: {ci['width']:.2%}")
    
    # Model uncertainty
    model = analysis_results.get('model_uncertainty', {})
    if model:
        metrics = model.get('uncertainty_metrics', {})
        print(f"\nModel Uncertainty: {metrics.get('model_disagreement', 0):.3f}")
        print(f"Best Model: {model.get('best_model', 'N/A')}")
    
    # Parameter uncertainty
    param = analysis_results.get('parameter_uncertainty', {})
    if param:
        metrics = param.get('uncertainty_metrics', {})
        print(f"\nParameter Uncertainty: {metrics.get('total_uncertainty', 0):.3f}")
        
        findings = param.get('key_findings', [])
        if findings:
            print("Key Findings:")
            for finding in findings[:2]:  # Show top 2
                print(f"  • {finding}")
    
    # Regime uncertainty
    regime = analysis_results.get('regime_uncertainty', {})
    if regime:
        regimes = regime.get('detected_regimes', [])
        if regimes:
            print(f"\nDetected Regimes: {len(regimes)}")
            
            characteristics = regime.get('regime_characteristics', {})
            for regime_type, chars in characteristics.items():
                print(f"  {regime_type}: {chars.get('frequency', 0):.1%} frequency, "
                      f"{chars.get('avg_duration', 0):.0f} days avg duration")
    
    print()
    
    # Generate comprehensive report
    print("📝 Generating uncertainty report...")
    report = quantifier.generate_uncertainty_report()
    
    with open('uncertainty_quantification_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Uncertainty report saved to 'uncertainty_quantification_report.md'")
    
    print("\n" + "=" * 80)
    print("Uncertainty Quantification Demonstration Complete")
    print("=" * 80)
    
    # Display key takeaways
    print("\n🔑 KEY TAKEAWAYS:")
    print("1. Uncertainty comes from multiple sources: parameters, models, estimation, and regimes")
    print("2. Combined uncertainty provides complete picture of strategy reliability")
    print("3. Confidence intervals should account for all uncertainty sources")
    print("4. Different models can give significantly different predictions")
    print("5. Regime changes are a major source of uncertainty in financial markets")
    print("6. Uncertainty quantification enables better risk management and position sizing")


if __name__ == "__main__":
    main()