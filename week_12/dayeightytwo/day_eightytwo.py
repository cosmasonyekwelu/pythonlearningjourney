
"""
Day 82: Risk Assessment Tools & Exposure Management
Advanced portfolio risk analytics and real-time monitoring
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# For advanced functionality
try:
    from sklearn.decomposition import PCA
    from sklearn.covariance import EmpiricalCovariance, MinCovDet
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@dataclass
class PortfolioPosition:
    """Enhanced portfolio position with risk attributes."""
    symbol: str
    quantity: float
    price: float
    asset_class: str = "equity"
    sector: str = ""
    country: str = "US"
    currency: str = "USD"
    beta: float = 1.0
    daily_volume: float = 1000000  # Average daily volume
    avg_bid_ask_spread: float = 0.001  # 0.1%
    
    def __post_init__(self):
        """Calculate derived attributes."""
        self.notional_value = self.quantity * self.price
        self.weight = 0.0  # Will be set when added to portfolio
        self.liquidity_score = self._calculate_liquidity_score()
    
    def _calculate_liquidity_score(self) -> float:
        """Calculate liquidity score (0-100)."""
        # Score based on volume and spread
        volume_score = min(100, self.daily_volume / 1000000)  # 1M shares = 100
        spread_score = max(0, 100 - (self.avg_bid_ask_spread * 10000))  # 0.1% = 90
        
        return (volume_score * 0.6 + spread_score * 0.4)  # Weighted score


class PortfolioRiskEngine:
    """
    Comprehensive portfolio risk analytics engine.
    
    Features:
    - Real-time risk monitoring
    - VaR and Expected Shortfall calculation
    - Concentration and diversification analysis
    - Factor exposure decomposition
    - Liquidity risk assessment
    - Stress testing integration
    - Regulatory compliance reporting
    """
    
    def __init__(self, positions: List[PortfolioPosition], 
                 historical_returns: pd.DataFrame,
                 risk_free_rate: float = 0.02):
        """
        Initialize risk engine.
        
        Parameters:
        -----------
        positions : List[PortfolioPosition]
            Portfolio positions
        historical_returns : pd.DataFrame
            Historical returns data (assets as columns)
        risk_free_rate : float
            Annual risk-free rate for Sharpe ratio
        """
        self.positions = positions
        self.historical_returns = historical_returns
        self.risk_free_rate = risk_free_rate
        
        # Initialize data structures
        self._initialize_portfolio()
        self.risk_metrics = {}
        self.exposures = {}
        self.alerts = []
        
        # Calculate initial metrics
        self.calculate_all_metrics()
    
    def _initialize_portfolio(self):
        """Initialize portfolio data structures."""
        # Create position DataFrame
        position_data = []
        for pos in self.positions:
            position_data.append({
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'price': pos.price,
                'notional_value': pos.notional_value,
                'asset_class': pos.asset_class,
                'sector': pos.sector,
                'country': pos.country,
                'currency': pos.currency,
                'beta': pos.beta,
                'daily_volume': pos.daily_volume,
                'avg_bid_ask_spread': pos.avg_bid_ask_spread,
                'liquidity_score': pos.liquidity_score
            })
        
        self.position_df = pd.DataFrame(position_data)
        
        # Calculate weights
        total_value = self.position_df['notional_value'].sum()
        if total_value > 0:
            self.position_df['weight'] = self.position_df['notional_value'] / total_value
            
            # Update position weights
            for idx, row in self.position_df.iterrows():
                for pos in self.positions:
                    if pos.symbol == row['symbol']:
                        pos.weight = row['weight']
        else:
            self.position_df['weight'] = 0
        
        # Portfolio statistics
        self.portfolio_value = total_value
        self.num_positions = len(self.positions)
        
        # Get returns for portfolio symbols
        portfolio_symbols = [pos.symbol for pos in self.positions 
                           if pos.symbol in self.historical_returns.columns]
        self.portfolio_returns = self.historical_returns[portfolio_symbols].copy()
        
        # Create weight vector aligned with returns
        self.weight_vector = np.zeros(len(portfolio_symbols))
        for i, symbol in enumerate(portfolio_symbols):
            pos_weight = self.position_df.loc[self.position_df['symbol'] == symbol, 'weight']
            if not pos_weight.empty:
                self.weight_vector[i] = pos_weight.values[0]
    
    def calculate_all_metrics(self):
        """Calculate all risk metrics."""
        # Basic portfolio metrics
        self._calculate_basic_metrics()
        
        # Risk metrics
        self._calculate_risk_metrics()
        
        # Concentration metrics
        self._calculate_concentration_metrics()
        
        # Factor exposures
        self._calculate_factor_exposures()
        
        # Liquidity metrics
        self._calculate_liquidity_metrics()
        
        # Regulatory metrics
        self._calculate_regulatory_metrics()
        
        # Generate alerts
        self._generate_alerts()
    
    def _calculate_basic_metrics(self):
        """Calculate basic portfolio metrics."""
        self.risk_metrics['portfolio_value'] = self.portfolio_value
        self.risk_metrics['num_positions'] = self.num_positions
        
        # Calculate portfolio returns if we have data
        if len(self.portfolio_returns.columns) > 0 and len(self.weight_vector) > 0:
            portfolio_returns_series = self.portfolio_returns.dot(self.weight_vector)
            
            self.risk_metrics['avg_daily_return'] = portfolio_returns_series.mean()
            self.risk_metrics['daily_volatility'] = portfolio_returns_series.std()
            self.risk_metrics['annualized_volatility'] = portfolio_returns_series.std() * np.sqrt(252)
            
            # Sharpe ratio
            if self.risk_metrics['daily_volatility'] > 0:
                excess_return = self.risk_metrics['avg_daily_return'] - self.risk_free_rate / 252
                self.risk_metrics['sharpe_ratio'] = excess_return / self.risk_metrics['daily_volatility'] * np.sqrt(252)
            else:
                self.risk_metrics['sharpe_ratio'] = 0
            
            # Maximum drawdown
            cumulative = (1 + portfolio_returns_series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            self.risk_metrics['max_drawdown'] = drawdown.min()
            
            # Skewness and kurtosis
            self.risk_metrics['skewness'] = portfolio_returns_series.skew()
            self.risk_metrics['kurtosis'] = portfolio_returns_series.kurtosis()
        else:
            # Default values if no returns data
            self.risk_metrics.update({
                'avg_daily_return': 0,
                'daily_volatility': 0,
                'annualized_volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'skewness': 0,
                'kurtosis': 0
            })
    
    def _calculate_risk_metrics(self):
        """Calculate advanced risk metrics."""
        if len(self.portfolio_returns.columns) == 0 or len(self.weight_vector) == 0:
            self.risk_metrics.update({
                'var_95': 0,
                'var_99': 0,
                'expected_shortfall_95': 0,
                'expected_shortfall_99': 0,
                'conditional_var_95': 0,
                'conditional_var_99': 0
            })
            return
        
        portfolio_returns = self.portfolio_returns.dot(self.weight_vector)
        
        # Historical VaR
        self.risk_metrics['var_95'] = np.percentile(portfolio_returns, 5)
        self.risk_metrics['var_99'] = np.percentile(portfolio_returns, 1)
        
        # Expected Shortfall (Conditional VaR)
        self.risk_metrics['expected_shortfall_95'] = \
            portfolio_returns[portfolio_returns <= self.risk_metrics['var_95']].mean()
        self.risk_metrics['expected_shortfall_99'] = \
            portfolio_returns[portfolio_returns <= self.risk_metrics['var_99']].mean()
        
        # Parametric VaR (assuming normality)
        mean = portfolio_returns.mean()
        std = portfolio_returns.std()
        self.risk_metrics['parametric_var_95'] = mean + std * stats.norm.ppf(0.05)
        self.risk_metrics['parametric_var_99'] = mean + std * stats.norm.ppf(0.01)
        
        # Cornish-Fisher VaR (adjusting for skewness and kurtosis)
        z_95 = stats.norm.ppf(0.05)
        z_99 = stats.norm.ppf(0.01)
        
        skew = portfolio_returns.skew()
        kurt = portfolio_returns.kurtosis()
        
        cf_z_95 = (z_95 + (z_95**2 - 1) * skew/6 + 
                  (z_95**3 - 3*z_95) * kurt/24 - 
                  (2*z_95**3 - 5*z_95) * skew**2/36)
        
        cf_z_99 = (z_99 + (z_99**2 - 1) * skew/6 + 
                  (z_99**3 - 3*z_99) * kurt/24 - 
                  (2*z_99**3 - 5*z_99) * skew**2/36)
        
        self.risk_metrics['cornish_fisher_var_95'] = mean + std * cf_z_95
        self.risk_metrics['cornish_fisher_var_99'] = mean + std * cf_z_99
        
        # Calculate beta to market (if SPY available)
        if 'SPY' in self.historical_returns.columns:
            market_returns = self.historical_returns['SPY']
            covariance = portfolio_returns.cov(market_returns)
            market_variance = market_returns.var()
            
            if market_variance > 0:
                self.risk_metrics['market_beta'] = covariance / market_variance
            else:
                self.risk_metrics['market_beta'] = 1.0
        else:
            self.risk_metrics['market_beta'] = 1.0
        
        # Calculate portfolio VaR decomposition (marginal VaR)
        if SKLEARN_AVAILABLE and len(self.portfolio_returns.columns) > 1:
            self._calculate_var_decomposition(portfolio_returns)
    
    def _calculate_var_decomposition(self, portfolio_returns: pd.Series):
        """Calculate VaR decomposition to individual positions."""
        try:
            # Get covariance matrix
            cov_matrix = self.portfolio_returns.cov()
            
            # Portfolio variance
            portfolio_variance = self.weight_vector.T @ cov_matrix @ self.weight_vector
            
            if portfolio_variance > 0:
                # Marginal VaR for each position
                marginal_var = (cov_matrix @ self.weight_vector) / np.sqrt(portfolio_variance)
                marginal_var *= stats.norm.ppf(0.95)  # For 95% VaR
                
                # Component VaR
                component_var = marginal_var * self.weight_vector
                
                # Percentage contribution
                total_var = np.sum(np.abs(component_var))
                if total_var > 0:
                    var_contribution = np.abs(component_var) / total_var
                else:
                    var_contribution = np.zeros_like(component_var)
                
                # Store results
                self.exposures['var_decomposition'] = {
                    'marginal_var': dict(zip(self.portfolio_returns.columns, marginal_var)),
                    'component_var': dict(zip(self.portfolio_returns.columns, component_var)),
                    'var_contribution': dict(zip(self.portfolio_returns.columns, var_contribution))
                }
        except Exception as e:
            print(f"Warning: VaR decomposition failed: {e}")
    
    def _calculate_concentration_metrics(self):
        """Calculate concentration and diversification metrics."""
        weights = self.position_df['weight'].values
        
        # Basic concentration metrics
        self.risk_metrics['max_position_weight'] = weights.max() if len(weights) > 0 else 0
        self.risk_metrics['top_3_concentration'] = np.sum(np.sort(weights)[-3:]) if len(weights) >= 3 else weights.sum()
        self.risk_metrics['top_5_concentration'] = np.sum(np.sort(weights)[-5:]) if len(weights) >= 5 else weights.sum()
        
        # Herfindahl-Hirschman Index (HHI)
        self.risk_metrics['hhi'] = np.sum(weights ** 2)
        
        # Diversification ratio (weighted average volatility / portfolio volatility)
        if len(self.portfolio_returns.columns) > 0:
            individual_vols = self.portfolio_returns.std().values
            weighted_avg_vol = np.sum(weights * individual_vols)
            portfolio_vol = self.risk_metrics.get('daily_volatility', 0.01)
            
            if portfolio_vol > 0:
                self.risk_metrics['diversification_ratio'] = weighted_avg_vol / portfolio_vol
            else:
                self.risk_metrics['diversification_ratio'] = 1.0
        else:
            self.risk_metrics['diversification_ratio'] = 1.0
        
        # Effective number of positions
        self.risk_metrics['effective_n_positions'] = 1 / self.risk_metrics['hhi'] if self.risk_metrics['hhi'] > 0 else 0
        
        # Sector concentration
        if 'sector' in self.position_df.columns and not self.position_df['sector'].isna().all():
            sector_weights = self.position_df.groupby('sector')['weight'].sum()
            self.risk_metrics['max_sector_exposure'] = sector_weights.max()
            self.risk_metrics['sector_hhi'] = np.sum(sector_weights.values ** 2)
            self.risk_metrics['num_sectors'] = len(sector_weights)
            
            # Store sector exposures
            self.exposures['sector'] = sector_weights.to_dict()
        
        # Country concentration
        if 'country' in self.position_df.columns and not self.position_df['country'].isna().all():
            country_weights = self.position_df.groupby('country')['weight'].sum()
            self.risk_metrics['max_country_exposure'] = country_weights.max()
            self.risk_metrics['country_hhi'] = np.sum(country_weights.values ** 2)
            self.risk_metrics['num_countries'] = len(country_weights)
            
            # Store country exposures
            self.exposures['country'] = country_weights.to_dict()
        
        # Asset class concentration
        if 'asset_class' in self.position_df.columns and not self.position_df['asset_class'].isna().all():
            asset_weights = self.position_df.groupby('asset_class')['weight'].sum()
            self.risk_metrics['max_asset_class_exposure'] = asset_weights.max()
            self.risk_metrics['asset_class_hhi'] = np.sum(asset_weights.values ** 2)
            
            # Store asset class exposures
            self.exposures['asset_class'] = asset_weights.to_dict()
    
    def _calculate_factor_exposures(self):
        """Calculate factor exposures using statistical methods."""
        if len(self.portfolio_returns.columns) < 2:
            # Not enough data for factor analysis
            self.exposures['factor'] = {}
            return
        
        try:
            if SKLEARN_AVAILABLE:
                # Method 1: PCA for statistical factor analysis
                returns_data = self.portfolio_returns.dropna()
                
                if len(returns_data) > len(returns_data.columns):
                    pca = PCA(n_components=min(5, len(returns_data.columns)))
                    pca.fit(returns_data)
                    
                    # Get factor exposures (loadings)
                    factor_exposures = pca.components_
                    
                    # Calculate portfolio exposure to each factor
                    portfolio_factor_exposure = factor_exposures @ self.weight_vector
                    
                    # Variance explained
                    variance_explained = pca.explained_variance_ratio_
                    
                    self.exposures['pca_factors'] = {
                        'portfolio_exposure': portfolio_factor_exposure.tolist(),
                        'variance_explained': variance_explained.tolist(),
                        'cumulative_variance': np.cumsum(variance_explained).tolist(),
                        'num_factors': len(variance_explained)
                    }
            
            # Method 2: Simple factor exposures (market, size, value, momentum)
            # This is a simplified version - in practice would use factor returns
            
            # Market exposure (already calculated as beta)
            market_exposure = self.risk_metrics.get('market_beta', 1.0)
            
            # Size exposure (simplified: negative for large cap, positive for small cap)
            size_scores = {'AAPL': -1, 'MSFT': -1, 'GOOGL': -1, 'AMZN': -1,  # Large cap
                          'IWM': 1, 'EEM': 1}  # Small cap / emerging markets
            
            size_exposure = 0
            for pos in self.positions:
                size_score = size_scores.get(pos.symbol, 0)
                size_exposure += pos.weight * size_score
            
            # Value exposure (simplified)
            value_exposure = np.random.uniform(-0.5, 0.5)  # Placeholder
            
            # Momentum exposure (simplified)
            momentum_exposure = np.random.uniform(-0.3, 0.3)  # Placeholder
            
            self.exposures['simple_factors'] = {
                'market': market_exposure,
                'size': size_exposure,
                'value': value_exposure,
                'momentum': momentum_exposure
            }
            
            # Calculate factor concentration
            factor_values = [abs(market_exposure), abs(size_exposure), 
                           abs(value_exposure), abs(momentum_exposure)]
            if np.mean(factor_values) > 0:
                self.risk_metrics['factor_concentration'] = \
                    np.std(factor_values) / np.mean(factor_values)
            else:
                self.risk_metrics['factor_concentration'] = 0
                
        except Exception as e:
            print(f"Warning: Factor exposure calculation failed: {e}")
            self.exposures['factor'] = {}
    
    def _calculate_liquidity_metrics(self):
        """Calculate liquidity risk metrics."""
        if self.position_df.empty:
            self.risk_metrics.update({
                'avg_liquidity_score': 0,
                'min_liquidity_score': 0,
                'liquidity_hhi': 0,
                'avg_days_to_liquidate': 0,
                'max_days_to_liquidate': 0,
                'liquidity_at_risk': 0
            })
            return
        
        # Liquidity scores
        liquidity_scores = self.position_df['liquidity_score'].values
        weights = self.position_df['weight'].values
        
        self.risk_metrics['avg_liquidity_score'] = np.average(liquidity_scores, weights=weights)
        self.risk_metrics['min_liquidity_score'] = liquidity_scores.min()
        
        # Liquidity concentration
        liquidity_weights = weights * (100 / liquidity_scores)  # Higher weight for illiquid
        liquidity_weights = liquidity_weights / liquidity_weights.sum() if liquidity_weights.sum() > 0 else liquidity_weights
        self.risk_metrics['liquidity_hhi'] = np.sum(liquidity_weights ** 2)
        
        # Days to liquidate (simplified)
        # Assuming we liquidate 10% of average daily volume per day
        days_to_liquidate = []
        for _, row in self.position_df.iterrows():
            if row['daily_volume'] > 0:
                days = row['quantity'] / (row['daily_volume'] * 0.10)
                days_to_liquidate.append(days)
        
        if days_to_liquidate:
            self.risk_metrics['avg_days_to_liquidate'] = np.mean(days_to_liquidate)
            self.risk_metrics['max_days_to_liquidate'] = np.max(days_to_liquidate)
            
            # Liquidity-at-Risk (LaR) - worst-case liquidation cost
            # Assuming market impact increases with size
            market_impact = 0.001  # 10 bps per 10% of daily volume
            lar = 0
            for _, row in self.position_df.iterrows():
                if row['daily_volume'] > 0:
                    volume_pct = row['quantity'] / row['daily_volume']
                    impact_cost = market_impact * (volume_pct / 0.10) ** 2  # Quadratic impact
                    lar += row['notional_value'] * impact_cost
            
            self.risk_metrics['liquidity_at_risk'] = lar / self.portfolio_value if self.portfolio_value > 0 else 0
        else:
            self.risk_metrics['avg_days_to_liquidate'] = 1
            self.risk_metrics['max_days_to_liquidate'] = 2
            self.risk_metrics['liquidity_at_risk'] = 0.001  # 10 bps default
    
    def _calculate_regulatory_metrics(self):
        """Calculate regulatory risk metrics."""
        # Value-at-Risk for regulatory reporting
        var_99_10day = self.risk_metrics.get('var_99', 0) * np.sqrt(10)
        self.risk_metrics['regulatory_var_99_10d'] = abs(var_99_10day)
        
        # Stressed VaR (simplified - would use stressed period returns)
        stressed_var_multiplier = 3.0  # Basel multiplier
        self.risk_metrics['stressed_var'] = abs(self.risk_metrics.get('var_99', 0)) * stressed_var_multiplier
        
        # Incremental Risk Charge (simplified)
        # For credit instruments - using a placeholder
        credit_exposure = self.position_df[self.position_df['asset_class'] == 'bond']['weight'].sum()
        self.risk_metrics['incremental_risk_charge'] = credit_exposure * 0.01  # 1% of credit exposure
        
        # Comprehensive Risk Measure (simplified)
        # For correlation trading portfolios
        self.risk_metrics['comprehensive_risk_measure'] = \
            self.risk_metrics.get('regulatory_var_99_10d', 0) * 1.5
        
        # Leverage ratio
        total_assets = self.portfolio_value
        # Assuming no debt for simplicity
        self.risk_metrics['leverage_ratio'] = 1.0  # Assets / Equity
        
        # Liquidity Coverage Ratio (simplified)
        # High-quality liquid assets / net cash outflow over 30 days
        hqla = self.position_df[self.position_df['liquidity_score'] > 80]['notional_value'].sum()
        net_cash_outflow = self.portfolio_value * 0.05  # 5% monthly outflow estimate
        self.risk_metrics['liquidity_coverage_ratio'] = hqla / net_cash_outflow if net_cash_outflow > 0 else 10
    
    def _generate_alerts(self):
        """Generate risk alerts based on thresholds."""
        self.alerts = []
        
        # Define alert thresholds
        thresholds = {
            'max_position_weight': 0.10,  # >10% position
            'max_sector_exposure': 0.25,  # >25% sector
            'max_country_exposure': 0.50,  # >50% country
            'var_95': -0.03,  # >3% daily VaR
            'expected_shortfall_95': -0.05,  # >5% ES
            'liquidity_score': 60,  # <60 liquidity score
            'max_drawdown': -0.15,  # >15% drawdown
            'leverage_ratio': 3.0,  # >3x leverage
            'liquidity_coverage_ratio': 1.0  # <100% LCR
        }
        
        # Check each threshold
        for metric, threshold in thresholds.items():
            current_value = self.risk_metrics.get(metric)
            
            if current_value is not None:
                if metric in ['liquidity_score', 'liquidity_coverage_ratio']:
                    # For these, alert if below threshold
                    if current_value < threshold:
                        self.alerts.append({
                            'metric': metric,
                            'current': current_value,
                            'threshold': threshold,
                            'severity': 'HIGH' if metric == 'liquidity_coverage_ratio' else 'MEDIUM',
                            'message': f'{metric} below threshold: {current_value:.2%} < {threshold:.2%}'
                        })
                else:
                    # For others, alert if above threshold (in absolute terms for negative metrics)
                    if abs(current_value) > abs(threshold):
                        self.alerts.append({
                            'metric': metric,
                            'current': current_value,
                            'threshold': threshold,
                            'severity': 'HIGH' if metric in ['var_95', 'expected_shortfall_95'] else 'MEDIUM',
                            'message': f'{metric} above threshold: {current_value:.2%} > {threshold:.2%}'
                        })
        
        # Sort alerts by severity
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        self.alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
    
    def calculate_stressed_metrics(self, stress_period_returns: pd.DataFrame) -> Dict:
        """
        Calculate risk metrics under stressed market conditions.
        
        Parameters:
        -----------
        stress_period_returns : pd.DataFrame
            Returns during stress period
        
        Returns:
        --------
        Dict containing stressed risk metrics
        """
        # Align weights with stress period returns
        stress_symbols = [col for col in stress_period_returns.columns 
                         if col in self.portfolio_returns.columns]
        
        if not stress_symbols:
            return {'error': 'No overlapping symbols with stress period'}
        
        # Create aligned weight vector
        aligned_weights = np.zeros(len(stress_symbols))
        for i, symbol in enumerate(stress_symbols):
            pos_weight = self.position_df.loc[self.position_df['symbol'] == symbol, 'weight']
            if not pos_weight.empty:
                aligned_weights[i] = pos_weight.values[0]
        
        # Calculate portfolio returns during stress
        stress_portfolio_returns = stress_period_returns[stress_symbols].dot(aligned_weights)
        
        # Calculate stressed metrics
        stressed_metrics = {
            'stress_period_return': stress_portfolio_returns.mean(),
            'stress_period_volatility': stress_portfolio_returns.std(),
            'stress_var_95': np.percentile(stress_portfolio_returns, 5),
            'stress_expected_shortfall_95': stress_portfolio_returns[
                stress_portfolio_returns <= np.percentile(stress_portfolio_returns, 5)
            ].mean(),
            'stress_max_drawdown': self._calculate_max_drawdown(stress_portfolio_returns),
            'stress_sharpe_ratio': (
                stress_portfolio_returns.mean() / stress_portfolio_returns.std() * np.sqrt(252)
                if stress_portfolio_returns.std() > 0 else 0
            )
        }
        
        # Compare with normal metrics
        normal_var = self.risk_metrics.get('var_95', 0)
        stressed_var = stressed_metrics['stress_var_95']
        stressed_metrics['var_ratio'] = stressed_var / normal_var if normal_var != 0 else 0
        
        return stressed_metrics
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns series."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def optimize_portfolio_risk(self, target_return: Optional[float] = None,
                               risk_aversion: float = 1.0) -> Dict:
        """
        Optimize portfolio for risk-return tradeoff.
        
        Parameters:
        -----------
        target_return : float, optional
            Target return for optimization
        risk_aversion : float
            Risk aversion parameter (higher = more risk averse)
        
        Returns:
        --------
        Dict containing optimization results
        """
        if len(self.portfolio_returns.columns) < 2:
            return {'error': 'Need at least 2 assets for optimization'}
        
        try:
            returns = self.portfolio_returns
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            
            n_assets = len(mean_returns)
            
            if target_return is not None:
                # Mean-variance optimization with target return
                constraints = [
                    {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # weights sum to 1
                    {'type': 'eq', 'fun': lambda w: w @ mean_returns - target_return}  # target return
                ]
                
                bounds = [(0, 1) for _ in range(n_assets)]  # no short selling
                
                # Initial guess (equal weights)
                initial_weights = np.ones(n_assets) / n_assets
                
                # Optimize for minimum variance
                result = optimize.minimize(
                    fun=lambda w: w @ cov_matrix @ w,  # portfolio variance
                    x0=initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )
                
                if result.success:
                    optimal_weights = result.x
                else:
                    return {'error': 'Optimization failed'}
            else:
                # Risk-aversion based optimization
                # Maximize: w'*mu - risk_aversion/2 * w'*Sigma*w
                def objective(w):
                    portfolio_return = w @ mean_returns
                    portfolio_variance = w @ cov_matrix @ w
                    return -(portfolio_return - risk_aversion/2 * portfolio_variance)
                
                constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
                bounds = [(0, 1) for _ in range(n_assets)]
                initial_weights = np.ones(n_assets) / n_assets
                
                result = optimize.minimize(
                    fun=objective,
                    x0=initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )
                
                if result.success:
                    optimal_weights = result.x
                else:
                    return {'error': 'Optimization failed'}
            
            # Calculate metrics for optimal portfolio
            optimal_return = optimal_weights @ mean_returns
            optimal_volatility = np.sqrt(optimal_weights @ cov_matrix @ optimal_weights)
            optimal_sharpe = optimal_return / optimal_volatility * np.sqrt(252) if optimal_volatility > 0 else 0
            
            # Compare with current portfolio
            current_return = self.weight_vector @ mean_returns
            current_volatility = np.sqrt(self.weight_vector @ cov_matrix @ self.weight_vector)
            
            improvement = {
                'return_improvement': optimal_return - current_return,
                'volatility_improvement': current_volatility - optimal_volatility,
                'sharpe_improvement': optimal_sharpe - self.risk_metrics.get('sharpe_ratio', 0)
            }
            
            return {
                'optimal_weights': dict(zip(returns.columns, optimal_weights)),
                'optimal_metrics': {
                    'expected_return': optimal_return,
                    'expected_volatility': optimal_volatility,
                    'sharpe_ratio': optimal_sharpe
                },
                'improvement': improvement,
                'turnover': np.sum(np.abs(optimal_weights - self.weight_vector)) / 2  # One-way turnover
            }
            
        except Exception as e:
            return {'error': f'Optimization error: {str(e)}'}
    
    def generate_risk_report(self) -> str:
        """Generate comprehensive risk report."""
        report_lines = []
        
        report_lines.append("# PORTFOLIO RISK ASSESSMENT REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Portfolio Value: ${self.portfolio_value:,.2f}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        
        # Risk rating based on metrics
        risk_score = self._calculate_overall_risk_score()
        risk_rating = self._get_risk_rating(risk_score)
        
        report_lines.append(f"**Overall Risk Rating**: {risk_rating}")
        report_lines.append(f"**Risk Score**: {risk_score:.1f}/100")
        report_lines.append("")
        
        # Key Metrics
        report_lines.append("## Key Risk Metrics")
        report_lines.append("")
        
        key_metrics = [
            ('Daily VaR (95%)', 'var_95', True),
            ('Expected Shortfall (95%)', 'expected_shortfall_95', True),
            ('Annualized Volatility', 'annualized_volatility', True),
            ('Maximum Drawdown', 'max_drawdown', True),
            ('Sharpe Ratio', 'sharpe_ratio', False),
            ('Market Beta', 'market_beta', False)
        ]
        
        for name, metric, is_pct in key_metrics:
            value = self.risk_metrics.get(metric, 0)
            if is_pct:
                report_lines.append(f"- **{name}**: {value:.2%}")
            else:
                report_lines.append(f"- **{name}**: {value:.3f}")
        report_lines.append("")
        
        # Concentration Risk
        report_lines.append("## Concentration Risk")
        report_lines.append("")
        
        conc_metrics = [
            ('Max Position Weight', 'max_position_weight'),
            ('Top 3 Concentration', 'top_3_concentration'),
            ('Herfindahl Index', 'hhi'),
            ('Effective N Positions', 'effective_n_positions')
        ]
        
        for name, metric in conc_metrics:
            value = self.risk_metrics.get(metric, 0)
            if metric == 'effective_n_positions':
                report_lines.append(f"- **{name}**: {value:.1f}")
            else:
                report_lines.append(f"- **{name}**: {value:.2%}")
        report_lines.append("")
        
        # Sector/Country Exposure
        if 'sector' in self.exposures:
            report_lines.append("### Sector Exposure")
            for sector, weight in sorted(self.exposures['sector'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report_lines.append(f"- **{sector}**: {weight:.2%}")
            report_lines.append("")
        
        if 'country' in self.exposures:
            report_lines.append("### Country Exposure")
            for country, weight in sorted(self.exposures['country'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report_lines.append(f"- **{country}**: {weight:.2%}")
            report_lines.append("")
        
        # Liquidity Risk
        report_lines.append("## Liquidity Risk")
        report_lines.append("")
        
        liq_metrics = [
            ('Average Liquidity Score', 'avg_liquidity_score', False),
            ('Min Liquidity Score', 'min_liquidity_score', False),
            ('Avg Days to Liquidate', 'avg_days_to_liquidate', False),
            ('Liquidity-at-Risk', 'liquidity_at_risk', True)
        ]
        
        for name, metric, is_pct in liq_metrics:
            value = self.risk_metrics.get(metric, 0)
            if is_pct:
                report_lines.append(f"- **{name}**: {value:.2%}")
            else:
                report_lines.append(f"- **{name}**: {value:.1f}")
        report_lines.append("")
        
        # Regulatory Metrics
        report_lines.append("## Regulatory Risk Metrics")
        report_lines.append("")
        
        reg_metrics = [
            ('Regulatory VaR (99%, 10d)', 'regulatory_var_99_10d', True),
            ('Stressed VaR', 'stressed_var', True),
            ('Leverage Ratio', 'leverage_ratio', False),
            ('Liquidity Coverage Ratio', 'liquidity_coverage_ratio', False)
        ]
        
        for name, metric, is_pct in reg_metrics:
            value = self.risk_metrics.get(metric, 0)
            if is_pct:
                report_lines.append(f"- **{name}**: {value:.2%}")
            else:
                report_lines.append(f"- **{name}**: {value:.2f}")
        report_lines.append("")
        
        # Risk Alerts
        report_lines.append("## Risk Alerts")
        report_lines.append("")
        
        if self.alerts:
            critical_alerts = [a for a in self.alerts if a['severity'] == 'HIGH']
            warning_alerts = [a for a in self.alerts if a['severity'] == 'MEDIUM']
            
            if critical_alerts:
                report_lines.append("### Critical Alerts")
                for alert in critical_alerts:
                    report_lines.append(f"- ⚠️ **{alert['metric']}**: {alert['message']}")
                report_lines.append("")
            
            if warning_alerts:
                report_lines.append("### Warning Alerts")
                for alert in warning_alerts:
                    report_lines.append(f"- ⚠️ **{alert['metric']}**: {alert['message']}")
                report_lines.append("")
        else:
            report_lines.append("✅ No active risk alerts")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Risk Management Recommendations")
        report_lines.append("")
        
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*This report is for risk assessment purposes only.*")
        
        return "\n".join(report_lines)
    
    def _calculate_overall_risk_score(self) -> float:
        """Calculate overall risk score (0-100)."""
        score_components = []
        
        # Market risk component (40%)
        # >5% VaR = 100
        var_score = min(100, abs(self.risk_metrics.get('var_95', 0)) / 0.05 * 100)
        es_score = min(100, abs(self.risk_metrics.get('expected_shortfall_95', 0)) / 0.08 * 100)
        market_risk_score = (var_score * 0.6 + es_score * 0.4)
        score_components.append(market_risk_score * 0.4)
        
        # Concentration risk component (30%)
        hhi_score = max(0, 100 - self.risk_metrics.get('hhi', 0) * 1000)  # HHI of 0.1 = 0 score
        max_pos_score = max(0, 100 - self.risk_metrics.get('max_position_weight', 0) * 1000)
        concentration_score = (hhi_score * 0.7 + max_pos_score * 0.3)
        score_components.append(concentration_score * 0.3)
        
        # Liquidity risk component (20%)
        liquidity_score = self.risk_metrics.get('avg_liquidity_score', 0)
        lar_score = max(0, 100 - self.risk_metrics.get('liquidity_at_risk', 0) * 10000)  # 100 bps = 0
        liquidity_risk_score = (liquidity_score * 0.6 + lar_score * 0.4)
        score_components.append(liquidity_risk_score * 0.2)
        
        # Regulatory risk component (10%)
        lcr_score = min(100, self.risk_metrics.get('liquidity_coverage_ratio', 0) * 100)
        regulatory_score = lcr_score
        score_components.append(regulatory_score * 0.1)
        
        return sum(score_components)
    
    def _get_risk_rating(self, score: float) -> str:
        """Convert risk score to rating."""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "MEDIUM HIGH"
        else:
            return "HIGH"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        # Market risk recommendations
        if abs(self.risk_metrics.get('var_95', 0)) > 0.03:
            recommendations.append("Consider reducing portfolio volatility or adding hedges")
        
        if abs(self.risk_metrics.get('expected_shortfall_95', 0)) > 0.05:
            recommendations.append("Implement tail risk hedging strategies")
        
        # Concentration recommendations
        if self.risk_metrics.get('max_position_weight', 0) > 0.08:
            recommendations.append("Reduce largest position to improve diversification")
        
        if self.risk_metrics.get('top_3_concentration', 0) > 0.40:
            recommendations.append("Diversify away from top 3 positions")
        
        # Liquidity recommendations
        if self.risk_metrics.get('avg_liquidity_score', 0) < 70:
            recommendations.append("Increase allocation to more liquid securities")
        
        if self.risk_metrics.get('avg_days_to_liquidate', 0) > 5:
            recommendations.append("Develop contingency plans for rapid liquidation")
        
        # Regulatory recommendations
        if self.risk_metrics.get('liquidity_coverage_ratio', 0) < 1.1:
            recommendations.append("Increase high-quality liquid assets buffer")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Portfolio risk profile appears well-managed")
            recommendations.append("Continue regular monitoring and stress testing")
        
        return recommendations
    
    def get_top_risk_contributors(self, n: int = 5) -> pd.DataFrame:
        """
        Get top contributors to portfolio risk.
        
        Parameters:
        -----------
        n : int
            Number of top contributors to return
        
        Returns:
        --------
        DataFrame with top risk contributors
        """
        if 'var_decomposition' not in self.exposures:
            # Calculate simple risk contribution if decomposition not available
            contributions = []
            for _, row in self.position_df.iterrows():
                # Simplified risk contribution = weight * individual volatility
                if row['symbol'] in self.portfolio_returns.columns:
                    indiv_vol = self.portfolio_returns[row['symbol']].std()
                    risk_contrib = row['weight'] * indiv_vol
                    contributions.append({
                        'symbol': row['symbol'],
                        'weight': row['weight'],
                        'risk_contribution': risk_contrib,
                        'percent_of_total': risk_contrib / self.risk_metrics.get('daily_volatility', 1)
                    })
            
            df = pd.DataFrame(contributions)
        else:
            # Use VaR decomposition results
            var_contrib = self.exposures['var_decomposition']['var_contribution']
            contributions = []
            for symbol, contrib in var_contrib.items():
                weight = self.position_df.loc[self.position_df['symbol'] == symbol, 'weight']
                if not weight.empty:
                    contributions.append({
                        'symbol': symbol,
                        'weight': weight.values[0],
                        'risk_contribution': contrib,
                        'percent_of_total': contrib
                    })
            
            df = pd.DataFrame(contributions)
        
        # Sort by risk contribution and return top n
        df = df.sort_values('risk_contribution', ascending=False).head(n)
        return df


def main():
    """Demonstration of portfolio risk assessment tools."""
    print("Day 82: Risk Assessment Tools & Exposure Management")
    print("=" * 80)
    
    # Create sample portfolio positions
    positions = [
        PortfolioPosition('AAPL', 1000, 180.0, 'equity', 'Technology', 'US', 'USD', 1.2, 50000000, 0.0005),
        PortfolioPosition('MSFT', 500, 330.0, 'equity', 'Technology', 'US', 'USD', 1.1, 30000000, 0.0004),
        PortfolioPosition('JPM', 2000, 145.0, 'equity', 'Financials', 'US', 'USD', 1.3, 20000000, 0.0008),
        PortfolioPosition('XOM', 1500, 105.0, 'equity', 'Energy', 'US', 'USD', 1.0, 15000000, 0.0010),
        PortfolioPosition('TLT', 5000, 95.0, 'bond', 'Government', 'US', 'USD', -0.2, 40000000, 0.0003),
        PortfolioPosition('GLD', 200, 1850.0, 'commodity', 'Precious Metals', 'US', 'USD', 0.1, 8000000, 0.0015),
        PortfolioPosition('HYG', 3000, 75.0, 'bond', 'High Yield', 'US', 'USD', 0.8, 25000000, 0.0020)
    ]
    
    # Generate sample historical returns
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    symbols = ['AAPL', 'MSFT', 'JPM', 'XOM', 'TLT', 'GLD', 'HYG', 'SPY']
    
    # Generate correlated returns
    n_assets = len(symbols)
    means = np.array([0.0008, 0.0007, 0.0006, 0.0005, 0.0002, 0.0003, 0.0004, 0.0006])
    cov = np.array([
        [0.0004, 0.0003, 0.0002, 0.0001, -0.0001, 0.0000, 0.0001, 0.0003],
        [0.0003, 0.0005, 0.0002, 0.0001, -0.0001, 0.0000, 0.0001, 0.0003],
        [0.0002, 0.0002, 0.0006, 0.0002, 0.0000, 0.0000, 0.0002, 0.0004],
        [0.0001, 0.0001, 0.0002, 0.0007, 0.0001, 0.0001, 0.0001, 0.0002],
        [-0.0001, -0.0001, 0.0000, 0.0001, 0.0003, 0.0001, 0.0002, -0.0002],
        [0.0000, 0.0000, 0.0000, 0.0001, 0.0001, 0.0008, 0.0001, 0.0000],
        [0.0001, 0.0001, 0.0002, 0.0001, 0.0002, 0.0001, 0.0009, 0.0002],
        [0.0003, 0.0003, 0.0004, 0.0002, -0.0002, 0.0000, 0.0002, 0.0004]
    ])
    
    returns = np.random.multivariate_normal(means, cov, len(dates))
    historical_returns = pd.DataFrame(returns, index=dates, columns=symbols)
    
    print("\nInitializing Portfolio Risk Engine...")
    risk_engine = PortfolioRiskEngine(positions, historical_returns)
    
    print("✅ Risk engine initialized successfully")
    print(f"Portfolio Value: ${risk_engine.portfolio_value:,.2f}")
    print(f"Number of Positions: {risk_engine.num_positions}")
    print()
    
    # Display key risk metrics
    print("📊 KEY RISK METRICS")
    print("-" * 40)
    
    metrics_to_display = [
        ('Daily VaR (95%)', 'var_95', True),
        ('Expected Shortfall (95%)', 'expected_shortfall_95', True),
        ('Annualized Volatility', 'annualized_volatility', True),
        ('Maximum Drawdown', 'max_drawdown', True),
        ('Sharpe Ratio', 'sharpe_ratio', False),
        ('Market Beta', 'market_beta', False)
    ]
    
    for name, key, is_pct in metrics_to_display:
        value = risk_engine.risk_metrics.get(key, 0)
        if is_pct:
            print(f"{name:30}: {value:>8.2%}")
        else:
            print(f"{name:30}: {value:>8.3f}")
    
    print()
    
    # Concentration metrics
    print("🎯 CONCENTRATION METRICS")
    print("-" * 40)
    
    conc_metrics = [
        ('Max Position Weight', 'max_position_weight'),
        ('Top 3 Concentration', 'top_3_concentration'),
        ('Herfindahl Index', 'hhi'),
        ('Effective N Positions', 'effective_n_positions')
    ]
    
    for name, key in conc_metrics:
        value = risk_engine.risk_metrics.get(key, 0)
        if key == 'effective_n_positions':
            print(f"{name:30}: {value:>8.1f}")
        else:
            print(f"{name:30}: {value:>8.2%}")
    
    print()
    
    # Liquidity metrics
    print("💧 LIQUIDITY METRICS")
    print("-" * 40)
    
    liq_metrics = [
        ('Avg Liquidity Score', 'avg_liquidity_score'),
        ('Min Liquidity Score', 'min_liquidity_score'),
        ('Avg Days to Liquidate', 'avg_days_to_liquidate'),
        ('Liquidity-at-Risk', 'liquidity_at_risk')
    ]
    
    for name, key in liq_metrics:
        value = risk_engine.risk_metrics.get(key, 0)
        if key.endswith('_score'):
            print(f"{name:30}: {value:>8.1f}/100")
        elif key == 'avg_days_to_liquidate':
            print(f"{name:30}: {value:>8.1f} days")
        else:
            print(f"{name:30}: {value:>8.2%}")
    
    print()
    
    # Risk alerts
    print("⚠️  RISK ALERTS")
    print("-" * 40)
    
    if risk_engine.alerts:
        critical = [a for a in risk_engine.alerts if a['severity'] == 'HIGH']
        warnings = [a for a in risk_engine.alerts if a['severity'] == 'MEDIUM']
        
        if critical:
            print("CRITICAL:")
            for alert in critical[:3]:  # Show top 3
                print(f"  • {alert['message']}")
        
        if warnings:
            print("\nWARNINGS:")
            for alert in warnings[:3]:  # Show top 3
                print(f"  • {alert['message']}")
        
        if len(critical) > 3 or len(warnings) > 3:
            print(f"  ... and {max(0, len(critical)-3) + max(0, len(warnings)-3)} more")
    else:
        print("✅ No active alerts")
    
    print()
    
    # Generate comprehensive report
    print("📝 Generating comprehensive risk report...")
    report = risk_engine.generate_risk_report()
    
    with open('portfolio_risk_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Risk report saved to 'portfolio_risk_report.md'")
    
    # Get top risk contributors
    print("\n🔝 TOP RISK CONTRIBUTORS")
    print("-" * 40)
    
    top_contributors = risk_engine.get_top_risk_contributors(5)
    if not top_contributors.empty:
        for _, row in top_contributors.iterrows():
            print(f"{row['symbol']:6} - Weight: {row['weight']:.2%}, "
                  f"Risk Contribution: {row['percent_of_total']:.2%}")
    
    print()
    
    # Demonstrate portfolio optimization
    print("🔄 PORTFOLIO OPTIMIZATION DEMONSTRATION")
    print("-" * 40)
    
    opt_result = risk_engine.optimize_portfolio_risk(risk_aversion=2.0)
    
    if 'error' not in opt_result:
        print("Current vs Optimal Portfolio:")
        print(f"  Sharpe Ratio: {risk_engine.risk_metrics['sharpe_ratio']:.3f} -> {opt_result['optimal_metrics']['sharpe_ratio']:.3f}")
        print(f"  Volatility: {risk_engine.risk_metrics['annualized_volatility']:.2%} -> {opt_result['optimal_metrics']['expected_volatility']*np.sqrt(252):.2%}")
        print(f"  Expected Improvement: {opt_result['improvement']['sharpe_improvement']:.3f}")
        print(f"  Required Turnover: {opt_result['turnover']:.2%}")
    else:
        print(f"Optimization failed: {opt_result['error']}")
    
    print()
    
    # Calculate overall risk score
    risk_score = risk_engine._calculate_overall_risk_score()
    risk_rating = risk_engine._get_risk_rating(risk_score)
    
    print("📈 OVERALL RISK ASSESSMENT")
    print("-" * 40)
    print(f"Risk Score: {risk_score:.1f}/100")
    print(f"Risk Rating: {risk_rating}")
    
    if risk_rating in ['HIGH', 'MEDIUM HIGH']:
        print("⚠️  Portfolio carries significant risk")
    elif risk_rating == 'MODERATE':
        print("ℹ️  Portfolio risk is moderate")
    else:
        print("✅ Portfolio risk is well-controlled")
    
    print()
    print("=" * 80)
    print("Risk Assessment Tools Demonstration Complete")
    print("=" * 80)
    
    # Display key takeaways
    print("\n🔑 KEY TAKEAWAYS:")
    print("1. VaR and Expected Shortfall quantify potential losses in normal and extreme markets")
    print("2. Concentration metrics identify diversification gaps")
    print("3. Liquidity assessment ensures positions can be exited efficiently")
    print("4. Factor exposures reveal hidden risks and dependencies")
    print("5. Regulatory metrics ensure compliance with financial regulations")
    print("6. Regular optimization can improve risk-adjusted returns")


if __name__ == "__main__":
    main()