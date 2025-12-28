# Day 83: Monte Carlo Simulations for Uncertainty Modeling

## Objective
Implement advanced Monte Carlo simulation techniques for strategy validation, confidence interval estimation, and uncertainty quantification.

## Core Concepts
* **Monte Carlo Methods in Finance**: Path-dependent simulation for complex strategies, bootstrap methods for return distribution estimation, geometric Brownian motion and stochastic volatility models
* **Strategy Stability Assessment**: Confidence intervals for performance metrics, probability of ruin and capital adequacy testing, optimal bet sizing using simulation-based methods
* **Parameter Uncertainty**: Bayesian methods for parameter estimation with uncertainty, posterior predictive distributions for future returns, model risk quantification and management
* **Scenario Generation**: Copula-based dependency modeling for multi-asset strategies, regime-switching models for market state simulation, jump diffusion processes for extreme event modeling

## Tutorial: Advanced Monte Carlo Simulation Framework

```python
# monte_carlo_framework.py
import numpy as np
import pandas as pd
from scipy import stats, optimize, interpolate
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# For advanced statistical methods
try:
    import arch
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, Matern
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class SimulationParameters:
    """Parameters for Monte Carlo simulation."""
    n_simulations: int = 10000
    n_periods: int = 252  # 1 year of daily simulations
    initial_capital: float = 100000
    risk_free_rate: float = 0.02
    transaction_cost: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    seed: Optional[int] = None
    
    # Model parameters
    model_type: str = "gbm"  # gbm, heston, jump_diffusion, regime_switching
    drift_method: str = "historical"  # historical, estimated, zero
    volatility_method: str = "historical"  # historical, garch, stochastic
    correlation_method: str = "historical"  # historical, dynamic, copula
    
    # Advanced parameters
    use_fat_tails: bool = True
    use_regime_switching: bool = False
    include_jumps: bool = False
    stress_scenarios: List[str] = field(default_factory=list)


class MonteCarloSimulator:
    """
    Advanced Monte Carlo simulation framework for trading strategies.
    
    Features:
    - Multiple price process models (GBM, Heston, Jump Diffusion)
    - Bootstrap and parametric simulation methods
    - Regime switching and stress scenario simulation
    - Bayesian parameter uncertainty
    - Strategy performance distribution estimation
    """
    
    def __init__(self, historical_data: pd.DataFrame, 
                 strategy_function: Optional[Callable] = None):
        """
        Initialize Monte Carlo simulator.
        
        Parameters:
        -----------
        historical_data : pd.DataFrame
            Historical price or return data
        strategy_function : Callable, optional
            Function that takes simulated prices and returns portfolio values
        """
        self.historical_data = historical_data
        self.strategy_function = strategy_function
        
        # Extract returns from historical data
        if historical_data is not None and len(historical_data) > 1:
            self.returns = historical_data.pct_change().dropna()
            self.prices = historical_data
        else:
            self.returns = pd.DataFrame()
            self.prices = pd.DataFrame()
        
        # Store simulation results
        self.simulation_results = {}
        self.performance_distributions = {}
        
    def simulate_gbm(self, params: SimulationParameters) -> Dict:
        """
        Simulate Geometric Brownian Motion price paths.
        
        Parameters:
        -----------
        params : SimulationParameters
            Simulation parameters
        
        Returns:
        --------
        Dict containing simulation results
        """
        if self.returns.empty:
            return {'error': 'No historical data available'}
        
        np.random.seed(params.seed)
        
        n_assets = len(self.returns.columns)
        n_periods = params.n_periods
        n_simulations = params.n_simulations
        
        # Calculate parameters from historical data
        dt = 1 / 252  # Daily steps
        
        if params.drift_method == "historical":
            mu = self.returns.mean().values * 252  # Annualized drift
        elif params.drift_method == "estimated":
            # Bayesian estimation of drift
            mu = self._bayesian_drift_estimation()
        else:  # zero drift
            mu = np.zeros(n_assets)
        
        if params.volatility_method == "historical":
            sigma = self.returns.std().values * np.sqrt(252)  # Annualized volatility
        elif params.volatility_method == "garch" and ARCH_AVAILABLE:
            sigma = self._garch_volatility_estimation()
        else:  # Simple historical
            sigma = self.returns.std().values * np.sqrt(252)
        
        # Correlation matrix
        if params.correlation_method == "historical":
            corr_matrix = self.returns.corr().values
        elif params.correlation_method == "dynamic":
            corr_matrix = self._dynamic_correlation_estimation()
        elif params.correlation_method == "copula":
            corr_matrix = self._copula_based_correlation()
        else:
            corr_matrix = np.eye(n_assets)
        
        # Cholesky decomposition for correlated random numbers
        try:
            L = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            # Use nearest positive definite matrix if correlation matrix is not PD
            L = self._nearest_pos_def_cholesky(corr_matrix)
        
        # Initialize price paths
        initial_prices = self.prices.iloc[-1].values if not self.prices.empty else np.ones(n_assets)
        price_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        price_paths[:, 0, :] = initial_prices
        
        # Generate correlated random numbers
        if params.use_fat_tails:
            # Use t-distribution for fat tails
            df = 3  # Degrees of freedom for t-distribution
            Z = stats.t.rvs(df=df, size=(n_simulations, n_periods, n_assets))
            Z = Z @ L.T  # Correlate the random numbers
        else:
            # Normal distribution
            Z = np.random.normal(0, 1, (n_simulations, n_periods, n_assets))
            Z = Z @ L.T  # Correlate the random numbers
        
        # Simulate price paths
        for t in range(n_periods):
            for i in range(n_assets):
                drift = (mu[i] - 0.5 * sigma[i]**2) * dt
                diffusion = sigma[i] * np.sqrt(dt) * Z[:, t, i]
                
                price_paths[:, t+1, i] = price_paths[:, t, i] * np.exp(drift + diffusion)
        
        # Apply stress scenarios if specified
        if params.stress_scenarios:
            price_paths = self._apply_stress_scenarios(price_paths, params.stress_scenarios)
        
        # Store results
        self.simulation_results['gbm'] = {
            'price_paths': price_paths,
            'parameters': {
                'drift': mu,
                'volatility': sigma,
                'correlation': corr_matrix,
                'initial_prices': initial_prices
            },
            'simulation_settings': {
                'n_simulations': n_simulations,
                'n_periods': n_periods,
                'model_type': 'gbm',
                'use_fat_tails': params.use_fat_tails
            }
        }
        
        # Calculate performance if strategy function provided
        if self.strategy_function is not None:
            self._calculate_strategy_performance(price_paths, params)
        
        return self.simulation_results['gbm']
    
    def simulate_heston(self, params: SimulationParameters) -> Dict:
        """
        Simulate Heston stochastic volatility model.
        
        Parameters:
        -----------
        params : SimulationParameters
            Simulation parameters
        
        Returns:
        --------
        Dict containing simulation results
        """
        if self.returns.empty:
            return {'error': 'No historical data available'}
        
        np.random.seed(params.seed)
        
        n_assets = len(self.returns.columns)
        n_periods = params.n_periods
        n_simulations = params.n_simulations
        
        dt = 1 / 252  # Daily steps
        
        # Heston model parameters (calibrated from historical data)
        # For simplicity, using single asset Heston for each asset
        # In practice, would use multi-asset Heston or other multivariate SV models
        
        # Initialize arrays
        price_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        vol_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        
        initial_prices = self.prices.iloc[-1].values if not self.prices.empty else np.ones(n_assets)
        price_paths[:, 0, :] = initial_prices
        
        # Initial volatility (from historical)
        initial_vol = self.returns.std().values * np.sqrt(252)
        vol_paths[:, 0, :] = initial_vol
        
        # Heston parameters for each asset
        # theta: long-term variance, kappa: mean reversion speed, xi: vol of vol, rho: correlation
        heston_params = []
        for i in range(n_assets):
            # Simplified calibration (in practice would use more sophisticated methods)
            returns_i = self.returns.iloc[:, i] if n_assets > 1 else self.returns
            theta = returns_i.var() * 252  # Long-term variance
            kappa = 2.0  # Mean reversion speed
            xi = 0.3  # Volatility of volatility
            rho = -0.7  # Leverage effect (negative correlation between price and vol)
            heston_params.append({
                'theta': theta,
                'kappa': kappa,
                'xi': xi,
                'rho': rho
            })
        
        # Generate correlated random numbers for prices and volatilities
        Z1 = np.random.normal(0, 1, (n_simulations, n_periods, n_assets))
        Z2 = np.random.normal(0, 1, (n_simulations, n_periods, n_assets))
        
        # Correlate Z2 with Z1 for leverage effect
        for i in range(n_assets):
            rho = heston_params[i]['rho']
            Z2[:, :, i] = rho * Z1[:, :, i] + np.sqrt(1 - rho**2) * Z2[:, :, i]
        
        # Simulate Heston model
        for t in range(n_periods):
            for i in range(n_assets):
                params_i = heston_params[i]
                
                # Current volatility
                V_t = vol_paths[:, t, i]**2  # Variance
                
                # Euler discretization (with full truncation scheme to keep variance positive)
                dV = params_i['kappa'] * (params_i['theta'] - V_t) * dt + \
                     params_i['xi'] * np.sqrt(np.maximum(V_t, 0)) * np.sqrt(dt) * Z2[:, t, i]
                
                V_next = np.maximum(V_t + dV, 0.0001)  # Ensure variance stays positive
                vol_paths[:, t+1, i] = np.sqrt(V_next)
                
                # Price evolution
                price_paths[:, t+1, i] = price_paths[:, t, i] * np.exp(
                    (params_i.get('mu', 0.05) - 0.5 * V_t) * dt + 
                    np.sqrt(V_t) * np.sqrt(dt) * Z1[:, t, i]
                )
        
        # Store results
        self.simulation_results['heston'] = {
            'price_paths': price_paths,
            'vol_paths': vol_paths,
            'parameters': heston_params,
            'simulation_settings': {
                'n_simulations': n_simulations,
                'n_periods': n_periods,
                'model_type': 'heston'
            }
        }
        
        # Calculate performance if strategy function provided
        if self.strategy_function is not None:
            self._calculate_strategy_performance(price_paths, params)
        
        return self.simulation_results['heston']
    
    def simulate_jump_diffusion(self, params: SimulationParameters) -> Dict:
        """
        Simulate Merton jump diffusion model.
        
        Parameters:
        -----------
        params : SimulationParameters
            Simulation parameters
        
        Returns:
        --------
        Dict containing simulation results
        """
        if self.returns.empty:
            return {'error': 'No historical data available'}
        
        np.random.seed(params.seed)
        
        n_assets = len(self.returns.columns)
        n_periods = params.n_periods
        n_simulations = params.n_simulations
        
        dt = 1 / 252  # Daily steps
        
        # Jump diffusion parameters
        # lambda_j: jump intensity (jumps per year)
        # mu_j: mean jump size
        # sigma_j: jump volatility
        
        jump_params = []
        for i in range(n_assets):
            # Estimate jump parameters from historical returns
            returns_i = self.returns.iloc[:, i] if n_assets > 1 else self.returns
            
            # Simple jump detection (returns beyond 3 standard deviations)
            std_dev = returns_i.std()
            jumps = returns_i[abs(returns_i) > 3 * std_dev]
            
            if len(jumps) > 0:
                lambda_j = len(jumps) / (len(returns_i) / 252)  # Annual jump intensity
                mu_j = jumps.mean()
                sigma_j = jumps.std()
            else:
                # Default parameters if no jumps detected
                lambda_j = 0.5  # 0.5 jumps per year
                mu_j = -0.02  # Average jump size
                sigma_j = 0.05  # Jump volatility
            
            # GBM parameters
            mu = returns_i.mean() * 252
            sigma = returns_i.std() * np.sqrt(252)
            
            jump_params.append({
                'mu': mu,
                'sigma': sigma,
                'lambda_j': lambda_j,
                'mu_j': mu_j,
                'sigma_j': sigma_j
            })
        
        # Initialize price paths
        initial_prices = self.prices.iloc[-1].values if not self.prices.empty else np.ones(n_assets)
        price_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        price_paths[:, 0, :] = initial_prices
        
        # Generate random numbers
        Z = np.random.normal(0, 1, (n_simulations, n_periods, n_assets))
        
        # Simulate jump diffusion
        for t in range(n_periods):
            for i in range(n_assets):
                params_i = jump_params[i]
                
                # GBM component
                drift = (params_i['mu'] - 0.5 * params_i['sigma']**2) * dt
                diffusion = params_i['sigma'] * np.sqrt(dt) * Z[:, t, i]
                
                # Jump component
                # Number of jumps in this period (Poisson distributed)
                jump_prob = params_i['lambda_j'] * dt
                n_jumps = np.random.poisson(jump_prob, n_simulations)
                
                # Jump sizes (log-normal)
                jump_sizes = np.zeros(n_simulations)
                for s in range(n_simulations):
                    if n_jumps[s] > 0:
                        # Sum of n_jumps jump sizes
                        jumps = np.random.normal(params_i['mu_j'], params_i['sigma_j'], n_jumps[s])
                        jump_sizes[s] = np.sum(jumps)
                
                # Combine GBM and jump components
                price_paths[:, t+1, i] = price_paths[:, t, i] * np.exp(
                    drift + diffusion + jump_sizes
                )
        
        # Store results
        self.simulation_results['jump_diffusion'] = {
            'price_paths': price_paths,
            'parameters': jump_params,
            'simulation_settings': {
                'n_simulations': n_simulations,
                'n_periods': n_periods,
                'model_type': 'jump_diffusion'
            }
        }
        
        # Calculate performance if strategy function provided
        if self.strategy_function is not None:
            self._calculate_strategy_performance(price_paths, params)
        
        return self.simulation_results['jump_diffusion']
    
    def simulate_regime_switching(self, params: SimulationParameters, n_regimes: int = 2) -> Dict:
        """
        Simulate regime-switching model.
        
        Parameters:
        -----------
        params : SimulationParameters
            Simulation parameters
        n_regimes : int
            Number of market regimes
        
        Returns:
        --------
        Dict containing simulation results
        """
        if self.returns.empty:
            return {'error': 'No historical data available'}
        
        np.random.seed(params.seed)
        
        n_assets = len(self.returns.columns)
        n_periods = params.n_periods
        n_simulations = params.n_simulations
        
        dt = 1 / 252  # Daily steps
        
        # Estimate regime parameters using Hidden Markov Model (simplified)
        # In practice, would use proper HMM estimation
        regime_params = self._estimate_regime_parameters(n_regimes)
        
        # Transition probabilities between regimes
        # Simplified: assume regimes are persistent
        transition_matrix = np.array([
            [0.95, 0.05],  # Regime 1: 95% stay, 5% switch to regime 2
            [0.10, 0.90]   # Regime 2: 10% switch to regime 1, 90% stay
        ])
        
        if n_regimes > 2:
            # Extend for more regimes
            transition_matrix = np.eye(n_regimes) * 0.9 + np.ones((n_regimes, n_regimes)) * 0.1 / n_regimes
        
        # Initialize arrays
        price_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        regime_paths = np.zeros((n_simulations, n_periods + 1), dtype=int)
        
        initial_prices = self.prices.iloc[-1].values if not self.prices.empty else np.ones(n_assets)
        price_paths[:, 0, :] = initial_prices
        
        # Initial regime (assume regime 0)
        regime_paths[:, 0] = 0
        
        # Generate random numbers
        Z = np.random.normal(0, 1, (n_simulations, n_periods, n_assets))
        
        # Simulate regime switching
        for t in range(n_periods):
            for s in range(n_simulations):
                current_regime = regime_paths[s, t]
                
                # Transition to next regime
                probs = transition_matrix[current_regime]
                next_regime = np.random.choice(n_regimes, p=probs)
                regime_paths[s, t+1] = next_regime
                
                # Get regime parameters
                regime_mu = regime_params[next_regime]['mu']
                regime_sigma = regime_params[next_regime]['sigma']
                
                # Update prices for each asset
                for i in range(n_assets):
                    drift = (regime_mu[i] - 0.5 * regime_sigma[i]**2) * dt
                    diffusion = regime_sigma[i] * np.sqrt(dt) * Z[s, t, i]
                    
                    price_paths[s, t+1, i] = price_paths[s, t, i] * np.exp(drift + diffusion)
        
        # Store results
        self.simulation_results['regime_switching'] = {
            'price_paths': price_paths,
            'regime_paths': regime_paths,
            'regime_params': regime_params,
            'transition_matrix': transition_matrix,
            'simulation_settings': {
                'n_simulations': n_simulations,
                'n_periods': n_periods,
                'model_type': 'regime_switching',
                'n_regimes': n_regimes
            }
        }
        
        # Calculate performance if strategy function provided
        if self.strategy_function is not None:
            self._calculate_strategy_performance(price_paths, params)
        
        return self.simulation_results['regime_switching']
    
    def bootstrap_simulation(self, params: SimulationParameters, block_size: int = 20) -> Dict:
        """
        Perform block bootstrap simulation.
        
        Parameters:
        -----------
        params : SimulationParameters
            Simulation parameters
        block_size : int
            Size of blocks for block bootstrap
        
        Returns:
        --------
        Dict containing simulation results
        """
        if self.returns.empty:
            return {'error': 'No historical data available'}
        
        np.random.seed(params.seed)
        
        n_assets = len(self.returns.columns)
        n_periods = params.n_periods
        n_simulations = params.n_simulations
        
        # Initialize arrays
        return_paths = np.zeros((n_simulations, n_periods, n_assets))
        price_paths = np.zeros((n_simulations, n_periods + 1, n_assets))
        
        initial_prices = self.prices.iloc[-1].values if not self.prices.empty else np.ones(n_assets)
        price_paths[:, 0, :] = initial_prices
        
        # Historical returns
        historical_returns = self.returns.values
        n_historical = len(historical_returns)
        
        # Block bootstrap
        for s in range(n_simulations):
            t = 0
            while t < n_periods:
                # Randomly select starting point for block
                start_idx = np.random.randint(0, n_historical - block_size)
                block = historical_returns[start_idx:start_idx + block_size]
                
                # Copy block to simulation path
                block_len = min(block_size, n_periods - t)
                return_paths[s, t:t+block_len] = block[:block_len]
                t += block_len
        
        # Convert returns to price paths
        for s in range(n_simulations):
            for t in range(n_periods):
                price_paths[s, t+1] = price_paths[s, t] * (1 + return_paths[s, t])
        
        # Store results
        self.simulation_results['bootstrap'] = {
            'price_paths': price_paths,
            'return_paths': return_paths,
            'simulation_settings': {
                'n_simulations': n_simulations,
                'n_periods': n_periods,
                'model_type': 'bootstrap',
                'block_size': block_size
            }
        }
        
        # Calculate performance if strategy function provided
        if self.strategy_function is not None:
            self._calculate_strategy_performance(price_paths, params)
        
        return self.simulation_results['bootstrap']
    
    def _calculate_strategy_performance(self, price_paths: np.ndarray, params: SimulationParameters):
        """Calculate strategy performance for simulated price paths."""
        if self.strategy_function is None:
            return
        
        n_simulations = price_paths.shape[0]
        n_periods = price_paths.shape[1] - 1
        
        # Initialize portfolio values
        portfolio_values = np.zeros((n_simulations, n_periods + 1))
        portfolio_values[:, 0] = params.initial_capital
        
        # Calculate performance for each simulation
        for s in range(n_simulations):
            # Convert price path to DataFrame for strategy function
            price_df = pd.DataFrame(
                price_paths[s],
                columns=self.returns.columns if hasattr(self.returns, 'columns') else [f'Asset_{i}' for i in range(price_paths.shape[2])]
            )
            
            # Apply strategy function
            try:
                portfolio_values[s] = self.strategy_function(price_df, params.initial_capital)
            except Exception as e:
                print(f"Warning: Strategy function failed for simulation {s}: {e}")
                portfolio_values[s] = params.initial_capital
        
        # Calculate performance metrics
        final_values = portfolio_values[:, -1]
        returns = (final_values / params.initial_capital) - 1
        
        # Annualized returns
        annualized_returns = (1 + returns) ** (252 / n_periods) - 1
        
        # Calculate metrics distribution
        self.performance_distributions = {
            'final_values': final_values,
            'returns': returns,
            'annualized_returns': annualized_returns,
            'portfolio_paths': portfolio_values,
            'metrics': {
                'mean_return': np.mean(returns),
                'median_return': np.median(returns),
                'std_return': np.std(returns),
                'sharpe_ratio': np.mean(annualized_returns - params.risk_free_rate) / np.std(annualized_returns),
                'var_95': np.percentile(returns, 5),
                'var_99': np.percentile(returns, 1),
                'expected_shortfall_95': returns[returns <= np.percentile(returns, 5)].mean(),
                'probability_of_loss': (returns < 0).mean(),
                'probability_of_ruin': (final_values < params.initial_capital * 0.5).mean(),  # 50% loss
                'max_drawdown_distribution': self._calculate_max_drawdown_distribution(portfolio_values)
            }
        }
    
    def _calculate_max_drawdown_distribution(self, portfolio_values: np.ndarray) -> np.ndarray:
        """Calculate maximum drawdown for each simulation path."""
        n_simulations = portfolio_values.shape[0]
        max_drawdowns = np.zeros(n_simulations)
        
        for s in range(n_simulations):
            cumulative = portfolio_values[s]
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_drawdowns[s] = np.min(drawdown)
        
        return max_drawdowns
    
    def _bayesian_drift_estimation(self) -> np.ndarray:
        """Bayesian estimation of drift parameters."""
        # Simplified Bayesian estimation
        # In practice, would use proper Bayesian methods
        
        if self.returns.empty:
            return np.array([])
        
        n_assets = len(self.returns.columns)
        mu_estimate = np.zeros(n_assets)
        
        for i in range(n_assets):
            returns_i = self.returns.iloc[:, i] if n_assets > 1 else self.returns
            
            # Prior: normal distribution centered at historical mean
            prior_mean = returns_i.mean() * 252
            prior_std = 0.1  # Prior uncertainty
            
            # Likelihood: normal distribution
            n_obs = len(returns_i)
            sample_mean = returns_i.mean() * 252
            sample_std = returns_i.std() * np.sqrt(252)
            
            # Posterior (conjugate normal-normal)
            # For simplicity, using weighted average
            weight_prior = 1 / (prior_std**2)
            weight_likelihood = n_obs / (sample_std**2)
            
            posterior_mean = (weight_prior * prior_mean + weight_likelihood * sample_mean) / \
                            (weight_prior + weight_likelihood)
            
            mu_estimate[i] = posterior_mean
        
        return mu_estimate
    
    def _garch_volatility_estimation(self) -> np.ndarray:
        """Estimate volatility using GARCH model."""
        if not ARCH_AVAILABLE or self.returns.empty:
            # Fall back to historical volatility
            return self.returns.std().values * np.sqrt(252)
        
        n_assets = len(self.returns.columns)
        vol_estimates = np.zeros(n_assets)
        
        for i in range(n_assets):
            returns_i = self.returns.iloc[:, i] if n_assets > 1 else self.returns
            
            try:
                # Fit GARCH(1,1) model
                model = arch.arch_model(returns_i * 100, vol='Garch', p=1, q=1)
                result = model.fit(disp='off')
                
                # Forecast volatility
                forecast = result.forecast(horizon=1)
                vol_estimates[i] = forecast.variance.values[-1, 0] / 100  # Convert from percentage
            except:
                # Fall back to historical if GARCH fails
                vol_estimates[i] = returns_i.std() * np.sqrt(252)
        
        return vol_estimates
    
    def _dynamic_correlation_estimation(self) -> np.ndarray:
        """Estimate dynamic correlation matrix."""
        # Simplified dynamic correlation using rolling window
        if self.returns.empty:
            return np.eye(1)  # Identity matrix for single asset
        
        # Use recent correlation (last 63 days ~ 3 months)
        window = min(63, len(self.returns))
        recent_returns = self.returns.iloc[-window:]
        
        return recent_returns.corr().values
    
    def _copula_based_correlation(self) -> np.ndarray:
        """Estimate correlation using copula methods."""
        # Simplified copula implementation
        # In practice, would use proper copula fitting
        
        if self.returns.empty:
            return np.eye(1)
        
        n_assets = len(self.returns.columns)
        
        # Rank correlation (Kendall's tau)
        tau_matrix = np.zeros((n_assets, n_assets))
        
        for i in range(n_assets):
            for j in range(i, n_assets):
                if i == j:
                    tau_matrix[i, j] = 1.0
                else:
                    # Calculate Kendall's tau
                    returns_i = self.returns.iloc[:, i]
                    returns_j = self.returns.iloc[:, j]
                    
                    tau, _ = stats.kendalltau(returns_i, returns_j)
                    tau_matrix[i, j] = tau
                    tau_matrix[j, i] = tau
        
        # Convert Kendall's tau to linear correlation (for Gaussian copula)
        # rho = sin(pi * tau / 2)
        corr_matrix = np.sin(np.pi * tau_matrix / 2)
        
        # Ensure positive definite
        corr_matrix = self._nearest_pos_def(corr_matrix)
        
        return corr_matrix
    
    def _estimate_regime_parameters(self, n_regimes: int) -> List[Dict]:
        """Estimate parameters for each regime."""
        # Simplified regime estimation
        # In practice, would use HMM or other regime detection methods
        
        if self.returns.empty:
            return []
        
        n_assets = len(self.returns.columns)
        regime_params = []
        
        # Define regimes (simplified)
        # Regime 1: Low volatility, positive drift
        # Regime 2: High volatility, negative drift
        
        historical_mean = self.returns.mean().values * 252
        historical_std = self.returns.std().values * np.sqrt(252)
        
        for r in range(n_regimes):
            if r == 0:  # Bull regime
                mu = historical_mean * 1.2  # 20% higher drift
                sigma = historical_std * 0.8  # 20% lower volatility
            elif r == 1:  # Bear regime
                mu = historical_mean * 0.8  # 20% lower drift
                sigma = historical_std * 1.5  # 50% higher volatility
            else:  # Neutral regime
                mu = historical_mean
                sigma = historical_std
            
            regime_params.append({
                'mu': mu,
                'sigma': sigma
            })
        
        return regime_params
    
    def _nearest_pos_def_cholesky(self, A: np.ndarray) -> np.ndarray:
        """Compute Cholesky decomposition of nearest positive definite matrix."""
        # Find nearest positive definite matrix
        B = self._nearest_pos_def(A)
        
        # Compute Cholesky decomposition
        try:
            L = np.linalg.cholesky(B)
        except np.linalg.LinAlgError:
            # Add small diagonal if still not positive definite
            B = B + np.eye(B.shape[0]) * 1e-8
            L = np.linalg.cholesky(B)
        
        return L
    
    def _nearest_pos_def(self, A: np.ndarray) -> np.ndarray:
        """Find the nearest positive definite matrix."""
        # Simple implementation
        # In practice, would use more robust methods
        
        # Symmetrize
        A = (A + A.T) / 2
        
        # Compute eigendecomposition
        eigvals, eigvecs = np.linalg.eigh(A)
        
        # Ensure eigenvalues are positive
        eigvals = np.maximum(eigvals, 1e-8)
        
        # Reconstruct matrix
        A_pos = eigvecs @ np.diag(eigvals) @ eigvecs.T
        
        return A_pos
    
    def _apply_stress_scenarios(self, price_paths: np.ndarray, scenarios: List[str]) -> np.ndarray:
        """Apply stress scenarios to price paths."""
        n_simulations = price_paths.shape[0]
        n_periods = price_paths.shape[1]
        n_assets = price_paths.shape[2]
        
        stressed_paths = price_paths.copy()
        
        for scenario in scenarios:
            if scenario == 'market_crash':
                # Apply market crash: 20-40% drop
                crash_period = n_periods // 3  # Crash happens at 1/3 of the period
                crash_magnitude = np.random.uniform(0.6, 0.8, n_simulations)  # Drop to 60-80% of value
                
                for s in range(n_simulations):
                    stressed_paths[s, crash_period:, :] *= crash_magnitude[s]
            
            elif scenario == 'volatility_spike':
                # Increase volatility by 2-3x for a period
                spike_start = n_periods // 4
                spike_end = spike_start + n_periods // 10  # 10% of period
                vol_multiplier = np.random.uniform(2.0, 3.0, n_simulations)
                
                for s in range(n_simulations):
                    # Add extra volatility during spike period
                    extra_vol = np.random.normal(0, 0.02 * (vol_multiplier[s] - 1), 
                                               (spike_end - spike_start, n_assets))
                    for t in range(spike_start, spike_end):
                        stressed_paths[s, t, :] *= (1 + extra_vol[t - spike_start])
            
            elif scenario == 'liquidity_crisis':
                # Simulate liquidity crisis with increased spreads and gaps
                crisis_start = n_periods // 2
                for s in range(n_simulations):
                    # Random gaps in prices
                    gap_prob = 0.1  # 10% chance of gap each period during crisis
                    for t in range(crisis_start, n_periods):
                        if np.random.random() < gap_prob:
                            # Price gap (up or down)
                            gap_size = np.random.normal(0, 0.05, n_assets)  # 5% gaps
                            stressed_paths[s, t, :] *= (1 + gap_size)
        
        return stressed_paths
    
    def calculate_confidence_intervals(self, metric: str = 'returns', 
                                     confidence_level: float = 0.95) -> Dict:
        """
        Calculate confidence intervals for performance metrics.
        
        Parameters:
        -----------
        metric : str
            Metric to calculate CI for ('returns', 'final_values', 'max_drawdown')
        confidence_level : float
            Confidence level (e.g., 0.95 for 95% CI)
        
        Returns:
        --------
        Dict containing confidence intervals
        """
        if not self.performance_distributions:
            return {'error': 'No performance distributions available. Run simulations with strategy function first.'}
        
        if metric not in self.performance_distributions:
            return {'error': f'Metric {metric} not available'}
        
        data = self.performance_distributions[metric]
        
        # Calculate confidence intervals
        alpha = 1 - confidence_level
        lower = np.percentile(data, alpha/2 * 100)
        upper = np.percentile(data, (1 - alpha/2) * 100)
        mean = np.mean(data)
        median = np.median(data)
        
        # Bootstrap confidence interval for the mean
        n_bootstrap = 1000
        bootstrap_means = np.zeros(n_bootstrap)
        
        for i in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means[i] = np.mean(sample)
        
        mean_ci_lower = np.percentile(bootstrap_means, alpha/2 * 100)
        mean_ci_upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
        
        return {
            'metric': metric,
            'confidence_level': confidence_level,
            'distribution_ci': {
                'lower': lower,
                'upper': upper,
                'width': upper - lower
            },
            'mean_ci': {
                'mean': mean,
                'lower': mean_ci_lower,
                'upper': mean_ci_upper,
                'width': mean_ci_upper - mean_ci_lower
            },
            'median': median,
            'distribution_stats': {
                'mean': mean,
                'std': np.std(data),
                'skew': stats.skew(data),
                'kurtosis': stats.kurtosis(data)
            }
        }
    
    def calculate_probability_of_ruin(self, ruin_level: float = 0.5) -> Dict:
        """
        Calculate probability of ruin (portfolio falling below certain level).
        
        Parameters:
        -----------
        ruin_level : float
            Ruin level as fraction of initial capital (e.g., 0.5 for 50% loss)
        
        Returns:
        --------
        Dict containing ruin probabilities
        """
        if 'portfolio_paths' not in self.performance_distributions:
            return {'error': 'No portfolio paths available'}
        
        portfolio_paths = self.performance_distributions['portfolio_paths']
        initial_capital = portfolio_paths[0, 0]
        
        n_simulations = portfolio_paths.shape[0]
        n_periods = portfolio_paths.shape[1]
        
        # Calculate ruin probabilities
        ruin_threshold = initial_capital * ruin_level
        
        # Probability of ever hitting ruin
        ever_ruin = np.zeros(n_simulations)
        for s in range(n_simulations):
            ever_ruin[s] = np.any(portfolio_paths[s] < ruin_threshold)
        
        prob_ever_ruin = np.mean(ever_ruin)
        
        # Probability of ruin at each period
        period_ruin = np.zeros(n_periods)
        for t in range(n_periods):
            period_ruin[t] = np.mean(portfolio_paths[:, t] < ruin_threshold)
        
        # Time to ruin distribution (for paths that experience ruin)
        time_to_ruin = []
        for s in range(n_simulations):
            ruin_indices = np.where(portfolio_paths[s] < ruin_threshold)[0]
            if len(ruin_indices) > 0:
                time_to_ruin.append(ruin_indices[0])  # First ruin time
        
        if time_to_ruin:
            time_to_ruin = np.array(time_to_ruin)
            time_stats = {
                'mean': np.mean(time_to_ruin),
                'median': np.median(time_to_ruin),
                'std': np.std(time_to_ruin),
                'percentiles': np.percentile(time_to_ruin, [25, 50, 75, 90, 95])
            }
        else:
            time_stats = {}
        
        return {
            'ruin_level': ruin_level,
            'ruin_threshold': ruin_threshold,
            'probability_ever_ruin': prob_ever_ruin,
            'probability_by_period': period_ruin.tolist(),
            'time_to_ruin_stats': time_stats,
            'n_simulations_ruined': np.sum(ever_ruin)
        }
    
    def calculate_optimal_position_sizing(self, risk_tolerance: float = 0.05) -> Dict:
        """
        Calculate optimal position sizing using simulation-based methods.
        
        Parameters:
        -----------
        risk_tolerance : float
            Maximum acceptable probability of ruin
        
        Returns:
        --------
        Dict containing optimal position sizing analysis
        """
        if 'portfolio_paths' not in self.performance_distributions:
            return {'error': 'No portfolio paths available'}
        
        # Simple Kelly criterion approximation using simulation results
        final_values = self.performance_distributions['final_values']
        initial_capital = self.performance_distributions['portfolio_paths'][0, 0]
        
        returns = final_values / initial_capital - 1
        
        # Calculate optimal fraction (simplified)
        mean_return = np.mean(returns)
        var_return = np.var(returns)
        
        if var_return > 0:
            # Simplified Kelly fraction
            kelly_fraction = mean_return / var_return
            # Conservative Kelly (half Kelly)
            half_kelly = kelly_fraction / 2
        else:
            kelly_fraction = 0.5
            half_kelly = 0.25
        
        # Ensure fractions are reasonable
        kelly_fraction = np.clip(kelly_fraction, 0.1, 0.9)
        half_kelly = np.clip(half_kelly, 0.05, 0.5)
        
        # Calculate performance for different position sizes
        position_sizes = np.linspace(0.1, 0.9, 9)  # 10% to 90%
        
        results = []
        for size in position_sizes:
            # Scale returns by position size
            scaled_returns = returns * size
            
            # Calculate metrics
            prob_loss = np.mean(scaled_returns < 0)
            expected_return = np.mean(scaled_returns)
            return_std = np.std(scaled_returns)
            sharpe = expected_return / return_std if return_std > 0 else 0
            
            # Probability of 20% drawdown
            drawdown_prob = np.mean(scaled_returns < -0.2)
            
            results.append({
                'position_size': size,
                'expected_return': expected_return,
                'volatility': return_std,
                'sharpe_ratio': sharpe,
                'probability_loss': prob_loss,
                'probability_20pct_drawdown': drawdown_prob,
                'kelly_optimal': size <= kelly_fraction
            })
        
        # Find optimal size based on risk tolerance
        optimal_size = 0.5  # Default
        for result in results:
            if result['probability_20pct_drawdown'] <= risk_tolerance:
                optimal_size = result['position_size']
                break
        
        return {
            'kelly_fraction': kelly_fraction,
            'half_kelly_fraction': half_kelly,
            'optimal_size_risk_tolerance': optimal_size,
            'position_size_analysis': results,
            'recommendation': {
                'aggressive': kelly_fraction,
                'moderate': half_kelly,
                'conservative': optimal_size,
                'risk_tolerance': risk_tolerance
            }
        }
    
    def generate_simulation_report(self) -> str:
        """Generate comprehensive simulation report."""
        report_lines = []
        
        report_lines.append("# MONTE CARLO SIMULATION REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Simulation Summary
        report_lines.append("## Simulation Summary")
        report_lines.append("")
        
        if self.simulation_results:
            for model_name, results in self.simulation_results.items():
                report_lines.append(f"### {model_name.replace('_', ' ').title()} Model")
                settings = results.get('simulation_settings', {})
                report_lines.append(f"- Simulations: {settings.get('n_simulations', 0)}")
                report_lines.append(f"- Periods: {settings.get('n_periods', 0)}")
                report_lines.append(f"- Assets: {self.returns.shape[1] if not self.returns.empty else 0}")
                report_lines.append("")
        else:
            report_lines.append("No simulations have been run yet.")
            report_lines.append("")
        
        # Performance Distribution Summary
        report_lines.append("## Performance Distribution Summary")
        report_lines.append("")
        
        if self.performance_distributions:
            metrics = self.performance_distributions.get('metrics', {})
            
            report_lines.append("### Key Metrics")
            report_lines.append(f"- Mean Return: {metrics.get('mean_return', 0):.2%}")
            report_lines.append(f"- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
            report_lines.append(f"- VaR (95%): {metrics.get('var_95', 0):.2%}")
            report_lines.append(f"- Expected Shortfall (95%): {metrics.get('expected_shortfall_95', 0):.2%}")
            report_lines.append(f"- Probability of Loss: {metrics.get('probability_of_loss', 0):.2%}")
            report_lines.append(f"- Probability of Ruin (50% loss): {metrics.get('probability_of_ruin', 0):.2%}")
            report_lines.append("")
            
            # Confidence Intervals
            report_lines.append("### Confidence Intervals (95%)")
            ci_returns = self.calculate_confidence_intervals('returns', 0.95)
            if 'distribution_ci' in ci_returns:
                ci = ci_returns['distribution_ci']
                report_lines.append(f"- Returns: [{ci['lower']:.2%}, {ci['upper']:.2%}]")
            
            ci_final = self.calculate_confidence_intervals('final_values', 0.95)
            if 'distribution_ci' in ci_final:
                ci = ci_final['distribution_ci']
                initial_capital = self.performance_distributions['portfolio_paths'][0, 0]
                report_lines.append(f"- Final Value: [${ci['lower']*initial_capital:,.0f}, ${ci['upper']*initial_capital:,.0f}]")
            report_lines.append("")
        else:
            report_lines.append("No performance distributions available.")
            report_lines.append("")
        
        # Risk Assessment
        report_lines.append("## Risk Assessment")
        report_lines.append("")
        
        ruin_analysis = self.calculate_probability_of_ruin(0.5)
        report_lines.append("### Ruin Analysis (50% loss)")
        report_lines.append(f"- Probability of ever experiencing ruin: {ruin_analysis.get('probability_ever_ruin', 0):.2%}")
        
        if ruin_analysis.get('time_to_ruin_stats'):
            stats = ruin_analysis['time_to_ruin_stats']
            report_lines.append(f"- Mean time to ruin: {stats.get('mean', 0):.0f} days")
        report_lines.append("")
        
        # Position Sizing
        report_lines.append("## Optimal Position Sizing")
        report_lines.append("")
        
        sizing_analysis = self.calculate_optimal_position_sizing(0.05)
        report_lines.append("### Kelly Criterion Analysis")
        report_lines.append(f"- Full Kelly Fraction: {sizing_analysis.get('kelly_fraction', 0):.2%}")
        report_lines.append(f"- Half Kelly (Conservative): {sizing_analysis.get('half_kelly_fraction', 0):.2%}")
        
        if 'recommendation' in sizing_analysis:
            rec = sizing_analysis['recommendation']
            report_lines.append(f"- Recommended (5% risk tolerance): {rec.get('conservative', 0):.2%}")
        report_lines.append("")
        
        # Model Comparison
        if len(self.simulation_results) > 1:
            report_lines.append("## Model Comparison")
            report_lines.append("")
            
            report_lines.append("| Model | Key Characteristics | Recommended Use |")
            report_lines.append("|-------|---------------------|-----------------|")
            
            model_descriptions = {
                'gbm': "Geometric Brownian Motion - Simple, assumes normal returns",
                'heston': "Stochastic Volatility - Captures volatility clustering",
                'jump_diffusion': "Jump Diffusion - Incorporates sudden price movements",
                'regime_switching': "Regime Switching - Models different market states",
                'bootstrap': "Bootstrap - Non-parametric, preserves historical dependencies"
            }
            
            model_uses = {
                'gbm': "Baseline analysis, simple derivatives pricing",
                'heston': "Options pricing, volatility-sensitive strategies",
                'jump_diffusion': "Tail risk assessment, event-driven strategies",
                'regime_switching': "Adaptive strategies, macroeconomic analysis",
                'bootstrap': "Historical simulation, model validation"
            }
            
            for model_name in self.simulation_results.keys():
                desc = model_descriptions.get(model_name, "Unknown model")
                use = model_uses.get(model_name, "General purpose")
                report_lines.append(f"| {model_name.replace('_', ' ').title()} | {desc} | {use} |")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        report_lines.append("1. **Use multiple models** for robustness checking")
        report_lines.append("2. **Focus on tail metrics** (VaR, Expected Shortfall) not just averages")
        report_lines.append("3. **Consider ruin probabilities** when sizing positions")
        report_lines.append("4. **Validate models** against out-of-sample data")
        report_lines.append("5. **Update parameters** regularly as market conditions change")
        report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("*This report is based on Monte Carlo simulations for risk assessment.*")
        report_lines.append("*Past performance is not indicative of future results.*")
        
        return "\n".join(report_lines)


# Example strategy function for testing
def example_strategy(prices: pd.DataFrame, initial_capital: float) -> np.ndarray:
    """
    Example strategy: 60/40 stock/bond portfolio with monthly rebalancing.
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Price data for assets
    initial_capital : float
        Initial portfolio capital
    
    Returns:
    --------
    np.ndarray containing portfolio values over time
    """
    n_periods = len(prices)
    portfolio_values = np.zeros(n_periods)
    portfolio_values[0] = initial_capital
    
    # Assume first column is stocks, second is bonds
    if len(prices.columns) >= 2:
        stock_col = prices.columns[0]
        bond_col = prices.columns[1]
        
        # Initial allocation: 60% stocks, 40% bonds
        stock_weight = 0.6
        bond_weight = 0.4
        
        # Calculate number of shares
        stock_shares = (initial_capital * stock_weight) / prices.iloc[0][stock_col]
        bond_shares = (initial_capital * bond_weight) / prices.iloc[0][bond_col]
        
        # Monthly rebalancing
        rebalance_frequency = 21  # Approximately monthly
        
        for t in range(1, n_periods):
            # Calculate current portfolio value
            portfolio_values[t] = (
                stock_shares * prices.iloc[t][stock_col] +
                bond_shares * prices.iloc[t][bond_col]
            )
            
            # Rebalance monthly
            if t % rebalance_frequency == 0:
                stock_shares = (portfolio_values[t] * stock_weight) / prices.iloc[t][stock_col]
                bond_shares = (portfolio_values[t] * bond_weight) / prices.iloc[t][bond_col]
    
    else:
        # Single asset: just hold
        for t in range(n_periods):
            portfolio_values[t] = initial_capital * (prices.iloc[t, 0] / prices.iloc[0, 0])
    
    return portfolio_values


def main():
    """Demonstration of Monte Carlo simulation framework."""
    print("Day 83: Monte Carlo Simulations for Uncertainty Modeling")
    print("=" * 80)
    
    # Generate sample historical data
    np.random.seed(42)
    n_days = 252 * 3  # 3 years of daily data
    dates = pd.date_range('2020-01-01', periods=n_days, freq='B')
    
    # Generate correlated returns for two assets (stocks and bonds)
    means = [0.0005, 0.0002]  # Daily returns
    cov = np.array([
        [0.0004, -0.0001],  # Stock variance and stock-bond covariance
        [-0.0001, 0.0001]   # Bond variance
    ])
    
    returns = np.random.multivariate_normal(means, cov, n_days)
    
    # Create price series
    prices = pd.DataFrame(
        np.exp(np.cumsum(returns, axis=0)) * 100,
        index=dates,
        columns=['Stocks', 'Bonds']
    )
    
    print("\nSample Historical Data:")
    print(f"Period: {dates[0].date()} to {dates[-1].date()}")
    print(f"Days: {n_days}")
    print(f"Assets: {list(prices.columns)}")
    print(f"Final Prices: Stocks=${prices['Stocks'].iloc[-1]:.2f}, Bonds=${prices['Bonds'].iloc[-1]:.2f}")
    print()
    
    # Initialize Monte Carlo simulator with example strategy
    print("Initializing Monte Carlo Simulator...")
    simulator = MonteCarloSimulator(
        historical_data=prices,
        strategy_function=example_strategy
    )
    
    # Set simulation parameters
    params = SimulationParameters(
        n_simulations=1000,
        n_periods=252,  # 1 year simulations
        initial_capital=100000,
        risk_free_rate=0.02,
        transaction_cost=0.001,
        seed=42,
        model_type="gbm",
        use_fat_tails=True,
        stress_scenarios=['market_crash']
    )
    
    # Run different simulations
    print("\nRunning Monte Carlo Simulations...")
    print("-" * 40)
    
    # 1. GBM Simulation
    print("1. Geometric Brownian Motion (GBM) Simulation...")
    gbm_results = simulator.simulate_gbm(params)
    print(f"   Completed: {gbm_results['price_paths'].shape[0]} simulations")
    print(f"   Price paths shape: {gbm_results['price_paths'].shape}")
    
    # 2. Heston Simulation
    print("\n2. Heston Stochastic Volatility Simulation...")
    heston_results = simulator.simulate_heston(params)
    print(f"   Completed: {heston_results['price_paths'].shape[0]} simulations")
    print(f"   Volatility paths: {heston_results['vol_paths'].shape}")
    
    # 3. Bootstrap Simulation
    print("\n3. Block Bootstrap Simulation...")
    bootstrap_params = SimulationParameters(
        n_simulations=500,  # Fewer for bootstrap (more computationally intensive)
        n_periods=252,
        initial_capital=100000,
        seed=42
    )
    bootstrap_results = simulator.bootstrap_simulation(bootstrap_params, block_size=20)
    print(f"   Completed: {bootstrap_results['price_paths'].shape[0]} simulations")
    
    print()
    
    # Display performance results
    if simulator.performance_distributions:
        print("📊 PERFORMANCE DISTRIBUTION SUMMARY")
        print("-" * 40)
        
        metrics = simulator.performance_distributions['metrics']
        
        print(f"Mean Return: {metrics['mean_return']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        print(f"VaR (95%): {metrics['var_95']:.2%}")
        print(f"Expected Shortfall (95%): {metrics['expected_shortfall_95']:.2%}")
        print(f"Probability of Loss: {metrics['probability_of_loss']:.2%}")
        print(f"Probability of Ruin (50% loss): {metrics['probability_of_ruin']:.2%}")
        print()
        
        # Confidence Intervals
        print("📈 CONFIDENCE INTERVALS (95%)")
        print("-" * 40)
        
        ci_returns = simulator.calculate_confidence_intervals('returns', 0.95)
        if 'distribution_ci' in ci_returns:
            ci = ci_returns['distribution_ci']
            print(f"Returns: [{ci['lower']:.2%}, {ci['upper']:.2%}]")
            print(f"Width: {ci['width']:.2%}")
        
        ci_final = simulator.calculate_confidence_intervals('final_values', 0.95)
        if 'distribution_ci' in ci_final:
            ci = ci_final['distribution_ci']
            initial_capital = simulator.performance_distributions['portfolio_paths'][0, 0]
            print(f"\nFinal Value Range:")
            print(f"  Lower: ${ci['lower']*initial_capital:,.0f}")
            print(f"  Upper: ${ci['upper']*initial_capital:,.0f}")
            print(f"  Range: ${(ci['upper'] - ci['lower'])*initial_capital:,.0f}")
        print()
        
        # Ruin Analysis
        print("⚠️  RUIN ANALYSIS")
        print("-" * 40)
        
        ruin_analysis = simulator.calculate_probability_of_ruin(0.5)
        print(f"Probability of 50% loss: {ruin_analysis['probability_ever_ruin']:.2%}")
        
        if ruin_analysis.get('time_to_ruin_stats'):
            stats = ruin_analysis['time_to_ruin_stats']
            print(f"Mean time to ruin: {stats['mean']:.0f} days")
            print(f"Median time to ruin: {stats['median']:.0f} days")
        print()
        
        # Position Sizing
        print("🎯 OPTIMAL POSITION SIZING")
        print("-" * 40)
        
        sizing = simulator.calculate_optimal_position_sizing(0.05)
        print(f"Kelly Fraction: {sizing['kelly_fraction']:.2%}")
        print(f"Half Kelly: {sizing['half_kelly_fraction']:.2%}")
        print(f"Optimal (5% risk tolerance): {sizing['optimal_size_risk_tolerance']:.2%}")
        
        print("\nPosition Size Analysis:")
        for result in sizing['position_size_analysis']:
            if result['position_size'] in [0.3, 0.5, 0.7]:
                print(f"  {result['position_size']:.0%}: Return={result['expected_return']:.2%}, "
                      f"Risk={result['probability_20pct_drawdown']:.2%}")
    else:
        print("No performance distributions available.")
    
    print()
    
    # Generate comprehensive report
    print("📝 Generating simulation report...")
    report = simulator.generate_simulation_report()
    
    with open('monte_carlo_simulation_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Simulation report saved to 'monte_carlo_simulation_report.md'")
    
    print("\n" + "=" * 80)
    print("Monte Carlo Simulation Demonstration Complete")
    print("=" * 80)
    
    # Display key takeaways
    print("\n🔑 KEY TAKEAWAYS:")
    print("1. Monte Carlo simulation provides distribution of possible outcomes")
    print("2. Different models (GBM, Heston, etc.) capture different market dynamics")
    print("3. Confidence intervals quantify uncertainty in performance metrics")
    print("4. Ruin analysis helps determine sustainable position sizes")
    print("5. Bootstrap methods preserve historical dependencies without parametric assumptions")
    print("6. Multiple simulation approaches should be used for robustness")


if __name__ == "__main__":
    main()