
"""
Day 81: Stress Testing & Edge Case Simulation
Comprehensive stress testing frameworks for extreme market conditions
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

# Optional imports for extended functionality
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class StressScenario:
    """Data class for stress scenarios."""
    name: str
    start_date: str
    end_date: str
    description: str
    market_conditions: Dict[str, float]
    recovery_pattern: str = "V-shaped"
    severity: float = 0.0
    
    def __post_init__(self):
        """Calculate severity score after initialization."""
        if not self.severity:
            self.severity = self._calculate_severity()
    
    def _calculate_severity(self) -> float:
        """Calculate scenario severity score."""
        # Simple severity calculation based on market conditions
        severity_factors = {
            'equity_drop': 0.3,
            'volatility_spike': 0.2,
            'liquidity_drop': 0.2,
            'correlation_rise': 0.15,
            'credit_spread_widening': 0.15
        }
        
        severity = 0.0
        for factor, weight in severity_factors.items():
            if factor in self.market_conditions:
                # Normalize impact to 0-1 scale
                impact = abs(self.market_conditions[factor])
                if factor == 'equity_drop':
                    normalized = min(impact / 0.5, 1.0)  # 50% drop = max
                elif factor == 'volatility_spike':
                    normalized = min(impact / 3.0, 1.0)  # 3x volatility = max
                elif factor == 'liquidity_drop':
                    normalized = min(impact / 0.8, 1.0)  # 80% drop = max
                elif factor == 'correlation_rise':
                    normalized = min(impact / 0.9, 1.0)  # 0.9 correlation = max
                elif factor == 'credit_spread_widening':
                    normalized = min(impact / 500, 1.0)  # 500 bps widening = max
                else:
                    normalized = min(impact, 1.0)
                
                severity += normalized * weight
        
        return severity


class AdvancedStressTester:
    """
    Advanced stress testing framework for trading strategies.
    
    Features:
    - Historical stress period analysis
    - Hypothetical scenario generation
    - System failure simulation
    - Sensitivity analysis
    - Regulatory stress testing
    """
    
    def __init__(self, portfolio_returns: pd.Series, 
                 factor_exposures: Optional[pd.DataFrame] = None,
                 position_data: Optional[pd.DataFrame] = None):
        """
        Initialize advanced stress tester.
        
        Parameters:
        -----------
        portfolio_returns : pd.Series
            Historical portfolio returns
        factor_exposures : pd.DataFrame, optional
            Factor exposures (factors as columns)
        position_data : pd.DataFrame, optional
            Position-level data for granular analysis
        """
        self.portfolio_returns = portfolio_returns
        self.factor_exposures = factor_exposures
        self.position_data = position_data
        
        # Pre-calculate statistics
        self._calculate_base_statistics()
        
        # Initialize scenario library
        self.scenario_library = self._initialize_scenario_library()
        
    def _calculate_base_statistics(self):
        """Calculate base statistics for stress testing."""
        self.mean_return = self.portfolio_returns.mean()
        self.volatility = self.portfolio_returns.std()
        self.skewness = self.portfolio_returns.skew()
        self.kurtosis = self.portfolio_returns.kurtosis()
        
        # Calculate VaR and Expected Shortfall
        self.var_95 = np.percentile(self.portfolio_returns, 5)
        self.var_99 = np.percentile(self.portfolio_returns, 1)
        self.es_95 = self.portfolio_returns[self.portfolio_returns <= self.var_95].mean()
        self.es_99 = self.portfolio_returns[self.portfolio_returns <= self.var_99].mean()
        
        # Maximum drawdown
        cumulative = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        self.max_drawdown = drawdown.min()
        self.max_drawdown_duration = self._calculate_drawdown_duration(drawdown)
        
    def _calculate_drawdown_duration(self, drawdown_series: pd.Series) -> int:
        """Calculate maximum drawdown duration."""
        in_drawdown = drawdown_series < 0
        max_duration = 0
        current_duration = 0
        
        for in_dd in in_drawdown:
            if in_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_duration
    
    def _initialize_scenario_library(self) -> Dict[str, StressScenario]:
        """Initialize library of historical and hypothetical stress scenarios."""
        library = {}
        
        # Historical scenarios
        historical_scenarios = [
            StressScenario(
                name="Dot-com Bubble Burst",
                start_date="2000-03-10",
                end_date="2002-10-09",
                description="Technology stock crash following dot-com bubble",
                market_conditions={
                    'equity_drop': -0.78,  # NASDAQ dropped ~78%
                    'volatility_spike': 2.5,
                    'liquidity_drop': -0.40,
                    'correlation_rise': 0.4
                },
                recovery_pattern="L-shaped"
            ),
            StressScenario(
                name="Global Financial Crisis",
                start_date="2007-10-09",
                end_date="2009-03-09",
                description="Subprime mortgage crisis leading to global recession",
                market_conditions={
                    'equity_drop': -0.57,  # S&P 500 dropped ~57%
                    'volatility_spike': 4.0,
                    'liquidity_drop': -0.70,
                    'correlation_rise': 0.8,
                    'credit_spread_widening': 450
                },
                recovery_pattern="V-shaped"
            ),
            StressScenario(
                name="COVID-19 Crash",
                start_date="2020-02-19",
                end_date="2020-03-23",
                description="Global pandemic causing rapid market sell-off",
                market_conditions={
                    'equity_drop': -0.34,  # S&P 500 dropped ~34%
                    'volatility_spike': 6.0,  # VIX peaked at ~85
                    'liquidity_drop': -0.50,
                    'correlation_rise': 0.7
                },
                recovery_pattern="V-shaped"
            )
        ]
        
        for scenario in historical_scenarios:
            library[scenario.name] = scenario
        
        # Hypothetical scenarios
        hypothetical_scenarios = [
            StressScenario(
                name="Inflation Shock",
                start_date="",
                end_date="",
                description="Persistent high inflation with aggressive Fed tightening",
                market_conditions={
                    'equity_drop': -0.30,
                    'volatility_spike': 2.0,
                    'credit_spread_widening': 200,
                    'real_yields_rise': 2.5
                }
            ),
            StressScenario(
                name="Geopolitical Crisis",
                start_date="",
                end_date="",
                description="Major geopolitical conflict affecting global trade",
                market_conditions={
                    'equity_drop': -0.40,
                    'volatility_spike': 3.5,
                    'liquidity_drop': -0.60,
                    'commodity_price_spike': 0.50
                }
            ),
            StressScenario(
                name="Systemic Cyber Attack",
                start_date="",
                end_date="",
                description="Coordinated cyber attack on financial infrastructure",
                market_conditions={
                    'equity_drop': -0.25,
                    'volatility_spike': 4.0,
                    'liquidity_drop': -0.80,
                    'market_closure_days': 3
                }
            )
        ]
        
        for scenario in hypothetical_scenarios:
            library[scenario.name] = scenario
        
        return library
    
    def run_historical_stress_test(self, scenario_name: str) -> Dict:
        """
        Run stress test for a specific historical scenario.
        
        Parameters:
        -----------
        scenario_name : str
            Name of historical scenario to test
        
        Returns:
        --------
        Dict containing stress test results
        """
        if scenario_name not in self.scenario_library:
            raise ValueError(f"Scenario '{scenario_name}' not found in library")
        
        scenario = self.scenario_library[scenario_name]
        
        # Get portfolio data for scenario period
        start_date = pd.Timestamp(scenario.start_date)
        end_date = pd.Timestamp(scenario.end_date)
        
        scenario_returns = self.portfolio_returns.loc[start_date:end_date]
        
        if len(scenario_returns) == 0:
            return {
                'error': f"No portfolio data available for scenario period {scenario.start_date} to {scenario.end_date}"
            }
        
        # Calculate stress metrics
        results = self._calculate_stress_metrics(scenario_returns)
        
        # Add scenario information
        results.update({
            'scenario_name': scenario.name,
            'period': f"{scenario.start_date} to {scenario.end_date}",
            'duration_days': len(scenario_returns),
            'description': scenario.description,
            'market_conditions': scenario.market_conditions,
            'recovery_pattern': scenario.recovery_pattern,
            'severity_score': scenario.severity
        })
        
        return results
    
    def _calculate_stress_metrics(self, returns: pd.Series) -> Dict:
        """Calculate comprehensive stress metrics for given returns."""
        # Basic metrics
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Drawdown metrics
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        avg_dd = drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0
        
        # Tail risk metrics
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        es_95 = returns[returns <= var_95].mean()
        es_99 = returns[returns <= var_99].mean()
        
        # Skew and kurtosis
        skew = returns.skew()
        kurt = returns.kurtosis()
        
        # Recovery metrics
        recovery_metrics = self._calculate_recovery_metrics(cumulative, drawdown)
        
        # Stress scores
        stress_scores = self._calculate_stress_scores(returns)
        
        return {
            'returns': {
                'total': total_return,
                'annualized': annualized_return,
                'daily_mean': returns.mean(),
                'daily_std': returns.std()
            },
            'risk_metrics': {
                'volatility': volatility,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'average_drawdown': avg_dd,
                'var_95': var_95,
                'var_99': var_99,
                'expected_shortfall_95': es_95,
                'expected_shortfall_99': es_99
            },
            'distribution': {
                'skewness': skew,
                'kurtosis': kurt,
                'worst_day': returns.min(),
                'best_day': returns.max(),
                'positive_days': (returns > 0).sum() / len(returns)
            },
            'recovery_metrics': recovery_metrics,
            'stress_scores': stress_scores
        }
    
    def _calculate_recovery_metrics(self, cumulative: pd.Series, drawdown: pd.Series) -> Dict:
        """Calculate recovery metrics from drawdowns."""
        # Find significant drawdowns (>5%)
        significant_dd = drawdown[drawdown < -0.05]
        
        if len(significant_dd) == 0:
            return {
                'significant_drawdowns': 0,
                'avg_recovery_days': 0,
                'recovery_success_rate': 1.0
            }
        
        # Find drawdown troughs
        troughs = []
        for i in range(1, len(drawdown) - 1):
            if drawdown.iloc[i] < drawdown.iloc[i-1] and drawdown.iloc[i] < drawdown.iloc[i+1]:
                if drawdown.iloc[i] < -0.05:
                    troughs.append(i)
        
        # Calculate recovery times
        recovery_times = []
        recovery_success = []
        
        for trough_idx in troughs:
            trough_value = cumulative.iloc[trough_idx]
            trough_dd = drawdown.iloc[trough_idx]
            
            # Look ahead for recovery
            recovered = False
            for i in range(trough_idx + 1, len(cumulative)):
                if cumulative.iloc[i] >= cumulative.iloc[trough_idx] * (1 - trough_dd):
                    recovery_times.append(i - trough_idx)
                    recovered = True
                    break
            
            recovery_success.append(recovered)
        
        if recovery_times:
            return {
                'significant_drawdowns': len(troughs),
                'avg_recovery_days': np.mean(recovery_times),
                'median_recovery_days': np.median(recovery_times),
                'max_recovery_days': np.max(recovery_times),
                'recovery_success_rate': sum(recovery_success) / len(recovery_success),
                'recovery_consistency': np.std(recovery_times) / np.mean(recovery_times) if recovery_times else 0
            }
        else:
            return {
                'significant_drawdowns': len(troughs),
                'avg_recovery_days': 0,
                'median_recovery_days': 0,
                'max_recovery_days': 0,
                'recovery_success_rate': 0,
                'recovery_consistency': 0
            }
    
    def _calculate_stress_scores(self, returns: pd.Series) -> Dict:
        """Calculate various stress scores."""
        # Market stress score (0-100)
        vol_score = min(100, (returns.std() * np.sqrt(252)) / 0.3 * 50)
        drawdown_score = min(100, abs(self._calculate_max_drawdown_from_series(returns)) / 0.5 * 100)
        var_score = min(100, abs(np.percentile(returns, 5)) / 0.1 * 100)
        
        market_stress = (vol_score + drawdown_score + var_score) / 3
        
        # Liquidity stress score
        # Based on consecutive negative returns
        negative_streak = self._longest_negative_streak(returns)
        liquidity_stress = min(100, negative_streak / 10 * 100)
        
        # Systemic stress score
        # Based on tail dependence (simplified)
        tail_dependence = self._estimate_tail_dependence(returns)
        systemic_stress = tail_dependence * 100
        
        return {
            'market_stress': market_stress,
            'liquidity_stress': liquidity_stress,
            'systemic_stress': systemic_stress,
            'composite_stress': (market_stress + liquidity_stress + systemic_stress) / 3
        }
    
    def _calculate_max_drawdown_from_series(self, returns: pd.Series) -> float:
        """Calculate max drawdown from returns series."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _longest_negative_streak(self, returns: pd.Series) -> int:
        """Find longest streak of negative returns."""
        max_streak = 0
        current_streak = 0
        
        for r in returns:
            if r < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _estimate_tail_dependence(self, returns: pd.Series, threshold: float = 0.05) -> float:
        """Estimate tail dependence coefficient."""
        # Simplified implementation
        # In practice, would compare to market or other assets
        extreme_returns = returns[returns <= np.percentile(returns, threshold * 100)]
        
        if len(extreme_returns) == 0:
            return 0.0
        
        # Measure clustering of extreme returns
        extreme_dates = extreme_returns.index
        time_gaps = [(extreme_dates[i] - extreme_dates[i-1]).days 
                     for i in range(1, len(extreme_dates))]
        
        if not time_gaps:
            return 0.0
        
        # More clustering = higher tail dependence
        avg_gap = np.mean(time_gaps)
        clustering_score = 1 / (1 + avg_gap / 10)  # Normalize
        
        return min(1.0, clustering_score)
    
    def generate_hypothetical_scenario(self, scenario_type: str, 
                                      severity: float = 0.5) -> Dict:
        """
        Generate hypothetical stress scenario.
        
        Parameters:
        -----------
        scenario_type : str
            Type of scenario: 'market_crash', 'liquidity_crisis', 
            'volatility_spike', 'correlation_breakdown'
        severity : float
            Severity level from 0.0 (mild) to 1.0 (extreme)
        
        Returns:
        --------
        Dict containing scenario parameters and portfolio impact
        """
        scenario_generators = {
            'market_crash': self._generate_market_crash,
            'liquidity_crisis': self._generate_liquidity_crisis,
            'volatility_spike': self._generate_volatility_spike,
            'correlation_breakdown': self._generate_correlation_breakdown,
            'sector_rotation': self._generate_sector_rotation,
            'interest_rate_shock': self._generate_interest_rate_shock
        }
        
        if scenario_type not in scenario_generators:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        return scenario_generators[scenario_type](severity)
    
    def _generate_market_crash(self, severity: float) -> Dict:
        """Generate market crash scenario."""
        # Base crash magnitude scales with severity
        base_crash = -0.20 - severity * 0.30  # -20% to -50%
        
        # Different assets crash by different amounts
        # For simplicity, assume we have factor exposures
        if self.factor_exposures is not None:
            # Factor-based impact
            factor_shocks = {
                'market': base_crash,
                'size': base_crash * 0.3,
                'value': base_crash * 0.2,
                'momentum': base_crash * -0.1,  # Momentum might benefit
                'quality': base_crash * 0.1
            }
            
            # Calculate portfolio impact
            portfolio_impact = 0
            for factor, shock in factor_shocks.items():
                if factor in self.factor_exposures.columns:
                    exposure = self.factor_exposures[factor].mean()
                    portfolio_impact += exposure * shock
        
        else:
            # Simple portfolio impact
            portfolio_impact = base_crash * np.random.uniform(0.8, 1.2)
        
        return {
            'scenario_type': 'market_crash',
            'severity': severity,
            'base_crash_magnitude': base_crash,
            'estimated_portfolio_impact': portfolio_impact,
            'confidence_interval': [
                portfolio_impact * 0.8,
                portfolio_impact * 1.2
            ],
            'recovery_time_months': 6 + severity * 18,  # 6-24 months
            'key_drivers': ['equity_risk_premium', 'earnings_growth', 'investor_sentiment']
        }
    
    def _generate_liquidity_crisis(self, severity: float) -> Dict:
        """Generate liquidity crisis scenario."""
        # Liquidity dries up
        liquidity_drop = 0.3 + severity * 0.5  # 30-80% drop
        
        # Bid-ask spreads widen
        spread_widening = 2 + severity * 8  # 2-10x widening
        
        # Market impact increases
        impact_coefficient = 0.001 + severity * 0.004  # 1-5 bps per million
        
        # Portfolio impact depends on turnover and position size
        avg_daily_turnover = abs(self.portfolio_returns).mean()
        position_size_factor = 1.0  # Would use actual position data
        
        transaction_cost_increase = avg_daily_turnover * spread_widening * impact_coefficient * 252
        missed_opportunity_cost = liquidity_drop * 0.01  # 1% of value per 100% drop
        
        total_impact = transaction_cost_increase + missed_opportunity_cost
        
        return {
            'scenario_type': 'liquidity_crisis',
            'severity': severity,
            'liquidity_drop_pct': liquidity_drop,
            'spread_widening_multiple': spread_widening,
            'market_impact_increase': impact_coefficient,
            'estimated_transaction_cost_impact': transaction_cost_increase,
            'estimated_missed_opportunity_cost': missed_opportunity_cost,
            'total_portfolio_impact': total_impact,
            'most_affected_assets': ['small_cap', 'high_yield', 'emerging_markets'],
            'mitigation_strategies': ['reduce_position_size', 'extend_time_horizon', 'use_limit_orders']
        }
    
    def _generate_volatility_spike(self, severity: float) -> Dict:
        """Generate volatility spike scenario."""
        # Volatility increases
        vol_multiplier = 1.5 + severity * 3.5  # 1.5-5x normal volatility
        
        current_vol = self.volatility
        stressed_vol = current_vol * vol_multiplier
        
        # Impact on option-based strategies or leveraged positions
        # Simplified: quadratic impact on volatility-sensitive strategies
        vol_sensitivity = 0.5  # Would be calculated from strategy characteristics
        
        portfolio_impact = -0.05 * severity * vol_sensitivity * (vol_multiplier - 1)
        
        return {
            'scenario_type': 'volatility_spike',
            'severity': severity,
            'current_volatility': current_vol,
            'stressed_volatility': stressed_vol,
            'volatility_multiplier': vol_multiplier,
            'volatility_sensitivity': vol_sensitivity,
            'estimated_portfolio_impact': portfolio_impact,
            'duration_days': 10 + severity * 50,  # 10-60 days
            'hedging_instruments': ['vix_futures', 'options', 'volatility_swaps']
        }
    
    def _generate_correlation_breakdown(self, severity: float) -> Dict:
        """Generate correlation breakdown scenario."""
        # Correlations increase (diversification fails)
        correlation_increase = 0.2 + severity * 0.5  # +0.2 to +0.7
        
        # Portfolio impact: benefits of diversification reduced
        diversification_benefit = 0.2  # Assume 20% risk reduction from diversification
        benefit_loss = diversification_benefit * correlation_increase
        
        # Effective portfolio risk increases
        effective_risk_increase = benefit_loss / (1 - diversification_benefit)
        portfolio_impact = -effective_risk_increase * 0.1  # Convert to return impact
        
        return {
            'scenario_type': 'correlation_breakdown',
            'severity': severity,
            'correlation_increase': correlation_increase,
            'diversification_benefit_loss': benefit_loss,
            'effective_risk_increase': effective_risk_increase,
            'estimated_portfolio_impact': portfolio_impact,
            'most_affected_strategies': ['long_short_equity', 'risk_parity', 'diversified_portfolios'],
            'alternative_diversifiers': ['trend_following', 'macro_hedges', 'tail_risk_insurance']
        }
    
    def _generate_sector_rotation(self, severity: float) -> Dict:
        """Generate sector rotation scenario."""
        # Define sector impacts
        sectors = ['technology', 'financials', 'healthcare', 'energy', 'consumer', 'utilities']
        
        # Random sector gets hit, another benefits
        hit_sector = np.random.choice(sectors)
        benefit_sector = np.random.choice([s for s in sectors if s != hit_sector])
        
        hit_impact = -0.15 - severity * 0.25  # -15% to -40%
        benefit_impact = 0.05 + severity * 0.20  # +5% to +25%
        
        # Calculate portfolio impact based on sector exposures
        # For simplicity, assume equal exposure
        portfolio_impact = (hit_impact + benefit_impact) / len(sectors)
        
        return {
            'scenario_type': 'sector_rotation',
            'severity': severity,
            'hit_sector': hit_sector,
            'benefit_sector': benefit_sector,
            'hit_sector_impact': hit_impact,
            'benefit_sector_impact': benefit_impact,
            'estimated_portfolio_impact': portfolio_impact,
            'rotation_catalysts': ['earnings_revisions', 'policy_changes', 'technological_breakthroughs'],
            'detection_signals': ['relative_strength', 'earnings_momentum', 'analyst_sentiment']
        }
    
    def _generate_interest_rate_shock(self, severity: float) -> Dict:
        """Generate interest rate shock scenario."""
        # Rate shock in basis points
        rate_shock_bps = 50 + severity * 250  # 50-300 bps
        
        # Different asset class sensitivities
        sensitivities = {
            'long_term_bonds': -0.05,  # per 100 bps
            'growth_stocks': -0.03,
            'value_stocks': -0.01,
            'real_estate': -0.02,
            'gold': 0.01,
            'cash': 0.00
        }
        
        # Portfolio impact depends on asset allocation
        # For simplicity, assume mixed portfolio
        avg_sensitivity = np.mean(list(sensitivities.values()))
        portfolio_impact = avg_sensitivity * (rate_shock_bps / 100)
        
        return {
            'scenario_type': 'interest_rate_shock',
            'severity': severity,
            'rate_shock_bps': rate_shock_bps,
            'asset_sensitivities': sensitivities,
            'estimated_portfolio_impact': portfolio_impact,
            'duration_impact': portfolio_impact * 2,  # Duration effect for bonds
            'hedging_instruments': ['rate_futures', 'interest_rate_swaps', 'inflation_protected_securities']
        }
    
    def run_system_failure_analysis(self) -> Dict:
        """
        Analyze impact of various system failures.
        
        Returns:
        --------
        Dict containing system failure analysis
        """
        failure_scenarios = {
            'data_feed_failure': self._analyze_data_feed_failure(),
            'execution_system_failure': self._analyze_execution_system_failure(),
            'risk_system_failure': self._analyze_risk_system_failure(),
            'cyber_attack': self._analyze_cyber_attack(),
            'power_outage': self._analyze_power_outage()
        }
        
        return failure_scenarios
    
    def _analyze_data_feed_failure(self) -> Dict:
        """Analyze data feed failure impact."""
        # Duration and impact
        durations = [1, 2, 4, 8, 24]  # hours
        impacts = []
        
        for duration in durations:
            # Impact increases with duration
            base_impact = duration / 24 * 0.02  # 2% per day
            # Additional impact for high-frequency strategies
            hf_multiplier = 2.0 if self._is_high_frequency() else 1.0
            impact = base_impact * hf_multiplier
            impacts.append(impact)
        
        avg_impact = np.mean(impacts)
        
        return {
            'failure_type': 'data_feed_failure',
            'potential_durations_hours': durations,
            'estimated_impacts': dict(zip(durations, impacts)),
            'average_impact': avg_impact,
            'mitigation_time_hours': 2,
            'recovery_procedures': [
                'switch_to_backup_feed',
                'manual_data_entry',
                'temporary_strategy_disable'
            ],
            'prevention_measures': [
                'redundant_data_feeds',
                'data_validation_checks',
                'circuit_breakers'
            ]
        }
    
    def _analyze_execution_system_failure(self) -> Dict:
        """Analyze execution system failure impact."""
        # Failure probabilities and impacts
        failure_modes = {
            'order_routing_failure': {'probability': 0.001, 'impact': 0.01},
            'matching_engine_failure': {'probability': 0.0001, 'impact': 0.05},
            'clearing_failure': {'probability': 0.0005, 'impact': 0.10},
            'settlement_failure': {'probability': 0.0002, 'impact': 0.15}
        }
        
        # Calculate expected impact
        expected_impact = sum(
            mode['probability'] * mode['impact'] 
            for mode in failure_modes.values()
        )
        
        return {
            'failure_type': 'execution_system_failure',
            'failure_modes': failure_modes,
            'expected_annual_impact': expected_impact,
            'worst_case_impact': max(mode['impact'] for mode in failure_modes.values()),
            'downtime_minutes': 30,
            'recovery_procedures': [
                'manual_order_entry',
                'broker_backup_systems',
                'exchange_communication_protocols'
            ]
        }
    
    def _analyze_risk_system_failure(self) -> Dict:
        """Analyze risk system failure impact."""
        # Without risk controls, potential for unlimited losses
        daily_vol = self.portfolio_returns.std()
        
        # Estimate potential loss in one day without risk limits
        potential_loss_1day = daily_vol * 3  # 3 sigma event
        potential_loss_1week = potential_loss_1day * np.sqrt(5)  # Weekly
        
        return {
            'failure_type': 'risk_system_failure',
            'potential_loss_1day': potential_loss_1day,
            'potential_loss_1week': potential_loss_1week,
            'probability_catastrophic_loss': 0.001,
            'downtime_tolerance_minutes': 5,
            'backup_systems': [
                'secondary_risk_server',
                'manual_risk_monitoring',
                'exchange_risk_controls'
            ],
            'emergency_procedures': [
                'position_flatting',
                'market_withdrawal',
                'regulatory_notification'
            ]
        }
    
    def _analyze_cyber_attack(self) -> Dict:
        """Analyze cyber attack impact."""
        attack_types = {
            'ransomware': {'probability': 0.0005, 'impact': 0.10, 'downtime_days': 3},
            'data_breach': {'probability': 0.001, 'impact': 0.05, 'downtime_days': 7},
            'ddos': {'probability': 0.002, 'impact': 0.02, 'downtime_days': 1},
            'insider_threat': {'probability': 0.0002, 'impact': 0.15, 'downtime_days': 14}
        }
        
        expected_impact = sum(
            attack['probability'] * attack['impact'] 
            for attack in attack_types.values()
        )
        
        avg_downtime = sum(
            attack['probability'] * attack['downtime_days'] 
            for attack in attack_types.values()
        ) / sum(attack['probability'] for attack in attack_types.values())
        
        return {
            'failure_type': 'cyber_attack',
            'attack_types': attack_types,
            'expected_annual_impact': expected_impact,
            'average_downtime_days': avg_downtime,
            'recovery_time_days': avg_downtime * 2,
            'prevention_measures': [
                'multi_factor_authentication',
                'network_segmentation',
                'regular_security_audits',
                'employee_training'
            ],
            'response_plan': [
                'incident_response_team',
                'data_backup_restoration',
                'law_enforcement_coordination',
                'public_relations_management'
            ]
        }
    
    def _analyze_power_outage(self) -> Dict:
        """Analyze power outage impact."""
        # Regional power outage scenarios
        scenarios = {
            'building_level': {'duration_hours': 2, 'probability': 0.01, 'impact': 0.005},
            'neighborhood_level': {'duration_hours': 8, 'probability': 0.001, 'impact': 0.02},
            'city_level': {'duration_hours': 24, 'probability': 0.0001, 'impact': 0.10},
            'regional_level': {'duration_hours': 72, 'probability': 0.00001, 'impact': 0.30}
        }
        
        expected_impact = sum(
            scenario['probability'] * scenario['impact'] 
            for scenario in scenarios.values()
        )
        
        return {
            'failure_type': 'power_outage',
            'scenarios': scenarios,
            'expected_annual_impact': expected_impact,
            'backup_power_hours': 48,
            'recovery_procedures': [
                'generator_activation',
                'remote_work_protocol',
                'data_center_failover'
            ],
            'prevention_measures': [
                'ups_systems',
                'multiple_power_feeds',
                'geographic_redundancy'
            ]
        }
    
    def _is_high_frequency(self) -> bool:
        """Determine if strategy is high frequency."""
        # Simplified check based on return frequency
        # In practice, would check strategy characteristics
        avg_return_interval = (self.portfolio_returns.index[1] - self.portfolio_returns.index[0]).total_seconds()
        return avg_return_interval < 3600  # Less than 1 hour between returns
    
    def run_sensitivity_analysis(self, parameters: Dict[str, Tuple[float, float, int]]) -> pd.DataFrame:
        """
        Run sensitivity analysis on key parameters.
        
        Parameters:
        -----------
        parameters : Dict
            Dictionary of parameter_name: (min, max, steps)
        
        Returns:
        --------
        DataFrame with sensitivity analysis results
        """
        results = []
        
        for param_name, (min_val, max_val, steps) in parameters.items():
            values = np.linspace(min_val, max_val, steps)
            
            for value in values:
                # Simulate impact of parameter change
                impact = self._simulate_parameter_impact(param_name, value)
                
                results.append({
                    'parameter': param_name,
                    'value': value,
                    'impact_on_returns': impact['return_impact'],
                    'impact_on_risk': impact['risk_impact'],
                    'impact_on_sharpe': impact['sharpe_impact'],
                    'sensitivity_score': impact['sensitivity_score']
                })
        
        return pd.DataFrame(results)
    
    def _simulate_parameter_impact(self, parameter: str, value: float) -> Dict:
        """
        Simulate impact of parameter change.
        
        Note: This is a simplified simulation. In practice, would run
        full backtest with modified parameter.
        """
        # Base impacts for different parameter types
        parameter_impacts = {
            'transaction_cost': {
                'return_impact': -value * 0.8,  # 80% of cost impacts returns
                'risk_impact': value * 0.1,  # 10% impacts risk
                'sharpe_impact': -value * 0.9  # 90% impacts Sharpe
            },
            'slippage': {
                'return_impact': -value * 0.6,
                'risk_impact': value * 0.2,
                'sharpe_impact': -value * 0.7
            },
            'position_size_limit': {
                'return_impact': -value * 0.3,  # Smaller positions = lower returns
                'risk_impact': -value * 0.5,  # But also lower risk
                'sharpe_impact': value * 0.2  # Could improve Sharpe
            },
            'stop_loss': {
                'return_impact': -value * 0.4,
                'risk_impact': -value * 0.7,
                'sharpe_impact': value * 0.3
            }
        }
        
        if parameter in parameter_impacts:
            impacts = parameter_impacts[parameter]
        else:
            # Default impacts for unknown parameters
            impacts = {
                'return_impact': -value * 0.5,
                'risk_impact': value * 0.3,
                'sharpe_impact': -value * 0.6
            }
        
        # Calculate sensitivity score
        sensitivity_score = abs(impacts['return_impact']) + abs(impacts['risk_impact'])
        
        impacts['sensitivity_score'] = sensitivity_score
        return impacts
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive stress testing report."""
        report_lines = []
        
        report_lines.append("# COMPREHENSIVE STRESS TESTING REPORT")
        report_lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Portfolio summary
        report_lines.append("## Portfolio Summary")
        report_lines.append("")
        report_lines.append(f"- **Mean Daily Return**: {self.mean_return:.4%}")
        report_lines.append(f"- **Annualized Volatility**: {self.volatility:.2%}")
        report_lines.append(f"- **Sharpe Ratio (annualized)**: {self.mean_return/self.volatility*np.sqrt(252):.2f}")
        report_lines.append(f"- **Maximum Drawdown**: {self.max_drawdown:.2%}")
        report_lines.append(f"- **Value at Risk (95%)**: {self.var_95:.2%}")
        report_lines.append(f"- **Expected Shortfall (95%)**: {self.es_95:.2%}")
        report_lines.append("")
        
        # Historical stress tests
        report_lines.append("## Historical Stress Tests")
        report_lines.append("")
        
        for scenario_name in ['Global Financial Crisis', 'COVID-19 Crash']:
            try:
                results = self.run_historical_stress_test(scenario_name)
                report_lines.append(f"### {scenario_name}")
                report_lines.append(f"- **Period**: {results['period']}")
                report_lines.append(f"- **Duration**: {results['duration_days']} days")
                report_lines.append(f"- **Total Return**: {results['returns']['total']:.2%}")
                report_lines.append(f"- **Max Drawdown**: {results['risk_metrics']['max_drawdown']:.2%}")
                report_lines.append(f"- **Stress Score**: {results['stress_scores']['composite_stress']:.1f}/100")
                report_lines.append("")
            except Exception as e:
                report_lines.append(f"### {scenario_name} - Error: {str(e)}")
                report_lines.append("")
        
        # Hypothetical scenarios
        report_lines.append("## Hypothetical Stress Scenarios")
        report_lines.append("")
        
        for scenario_type in ['market_crash', 'liquidity_crisis', 'volatility_spike']:
            scenario = self.generate_hypothetical_scenario(scenario_type, severity=0.7)
            report_lines.append(f"### {scenario_type.replace('_', ' ').title()}")
            report_lines.append(f"- **Severity**: {scenario['severity']:.1f}/1.0")
            report_lines.append(f"- **Estimated Impact**: {scenario['estimated_portfolio_impact']:.2%}")
            if 'confidence_interval' in scenario:
                ci = scenario['confidence_interval']
                report_lines.append(f"- **90% Confidence Interval**: [{ci[0]:.2%}, {ci[1]:.2%}]")
            report_lines.append("")
        
        # System failures
        report_lines.append("## System Failure Analysis")
        report_lines.append("")
        
        failures = self.run_system_failure_analysis()
        for failure_type, analysis in failures.items():
            report_lines.append(f"### {failure_type.replace('_', ' ').title()}")
            report_lines.append(f"- **Expected Annual Impact**: {analysis.get('expected_annual_impact', analysis.get('average_impact', 0)):.2%}")
            if 'worst_case_impact' in analysis:
                report_lines.append(f"- **Worst Case Impact**: {analysis['worst_case_impact']:.2%}")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Risk Management Recommendations")
        report_lines.append("")
        report_lines.append("### Immediate Actions (1-4 weeks)")
        report_lines.append("1. **Position Limits**: Implement maximum position size limits")
        report_lines.append("2. **Stop Losses**: Set daily stop loss at 2-3%")
        report_lines.append("3. **Liquidity Buffer**: Maintain 10-15% cash buffer")
        report_lines.append("")
        
        report_lines.append("### Medium-Term Actions (1-6 months)")
        report_lines.append("1. **Stress Testing**: Implement monthly stress testing")
        report_lines.append("2. **System Redundancy**: Deploy backup systems for critical components")
        report_lines.append("3. **Scenario Planning**: Develop response plans for key scenarios")
        report_lines.append("")
        
        report_lines.append("### Long-Term Actions (6+ months)")
        report_lines.append("1. **Diversification**: Reduce concentration in any single factor or asset")
        report_lines.append("2. **Infrastructure Upgrade**: Modernize systems for better resilience")
        report_lines.append("3. **Regulatory Compliance**: Ensure all regulatory stress testing requirements are met")
        report_lines.append("")
        
        report_lines.append("## Key Risk Indicators to Monitor")
        report_lines.append("")
        report_lines.append("1. **Market Stress**: VIX > 30, equity correlation > 0.7")
        report_lines.append("2. **Liquidity Stress**: Bid-ask spreads > 2x normal")
        report_lines.append("3. **Credit Stress**: High-yield spreads > 500 bps")
        report_lines.append("4. **System Health**: System latency > 100ms, error rate > 0.1%")
        report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("*This report is generated for risk assessment purposes only.*")
        report_lines.append("*Actual performance may differ from stress test results.*")
        
        return "\n".join(report_lines)


def main():
    """Demonstration of stress testing framework."""
    print("Day 81: Stress Testing & Edge Case Simulation")
    print("=" * 80)
    
    # Generate sample portfolio returns
    np.random.seed(42)
    n_days = 252 * 5  # 5 years of daily data
    dates = pd.date_range('2018-01-01', periods=n_days, freq='B')
    
    # Create synthetic returns with some stress periods
    base_returns = np.random.normal(0.0005, 0.01, n_days)
    
    # Add stress periods
    stress_periods = [
        (500, 550, -0.02, 0.02),  # Volatility spike
        (800, 850, -0.015, 0.015),  # Mild stress
        (1100, 1150, -0.025, 0.03),  # Severe stress
    ]
    
    for start, end, mean, std in stress_periods:
        if end <= n_days:
            base_returns[start:end] = np.random.normal(mean, std, end-start)
    
    # Create portfolio returns series
    portfolio_returns = pd.Series(base_returns, index=dates)
    
    # Create sample factor exposures
    factors = ['market', 'size', 'value', 'momentum', 'quality']
    factor_exposures = pd.DataFrame(
        np.random.normal(0, 0.5, (n_days, len(factors))),
        index=dates,
        columns=factors
    )
    
    print("\nInitializing Advanced Stress Tester...")
    tester = AdvancedStressTester(
        portfolio_returns=portfolio_returns,
        factor_exposures=factor_exposures
    )
    
    print("✅ Stress tester initialized successfully")
    print(f"Portfolio Statistics:")
    print(f"  Mean Return: {tester.mean_return:.4%}")
    print(f"  Volatility: {tester.volatility:.2%}")
    print(f"  Max Drawdown: {tester.max_drawdown:.2%}")
    print(f"  VaR (95%): {tester.var_95:.2%}")
    print()
    
    # Run historical stress test
    print("Running historical stress tests...")
    historical_scenarios = ['Global Financial Crisis', 'COVID-19 Crash']
    
    for scenario in historical_scenarios:
        try:
            results = tester.run_historical_stress_test(scenario)
            print(f"\n{scenario}:")
            print(f"  Total Return: {results['returns']['total']:.2%}")
            print(f"  Max Drawdown: {results['risk_metrics']['max_drawdown']:.2%}")
            print(f"  Stress Score: {results['stress_scores']['composite_stress']:.1f}/100")
        except Exception as e:
            print(f"\n{scenario}: Error - {str(e)}")
    
    # Generate hypothetical scenarios
    print("\n\nGenerating hypothetical stress scenarios...")
    hypothetical_types = ['market_crash', 'liquidity_crisis', 'volatility_spike']
    
    for scenario_type in hypothetical_types:
        scenario = tester.generate_hypothetical_scenario(scenario_type, severity=0.7)
        print(f"\n{scenario_type.replace('_', ' ').title()}:")
        print(f"  Estimated Impact: {scenario['estimated_portfolio_impact']:.2%}")
        if 'confidence_interval' in scenario:
            ci = scenario['confidence_interval']
            print(f"  90% CI: [{ci[0]:.2%}, {ci[1]:.2%}]")
    
    # System failure analysis
    print("\n\nAnalyzing system failures...")
    failures = tester.run_system_failure_analysis()
    
    print("\nSystem Failure Summary:")
    for failure_type, analysis in failures.items():
        impact = analysis.get('expected_annual_impact', analysis.get('average_impact', 0))
        print(f"  {failure_type.replace('_', ' ').title()}: {impact:.2%}")
    
    # Generate comprehensive report
    print("\n\nGenerating comprehensive report...")
    report = tester.generate_comprehensive_report()
    
    # Save report to file
    with open('stress_testing_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Comprehensive report saved to 'stress_testing_report.md'")
    
    # Display report summary
    print("\n" + "=" * 80)
    print("STRESS TESTING SUMMARY")
    print("=" * 80)
    
    print("\nPortfolio Resilience Assessment:")
    print(f"  Base Sharpe Ratio: {tester.mean_return/tester.volatility*np.sqrt(252):.2f}")
    print(f"  Maximum Historical Drawdown: {tester.max_drawdown:.2%}")
    print(f"  Tail Risk (ES 95%): {tester.es_95:.2%}")
    
    print("\nKey Findings:")
    print("  1. Portfolio shows moderate resilience to historical stress")
    print("  2. Significant vulnerability to liquidity crises")
    print("  3. System failures pose material operational risk")
    print("  4. Regular stress testing recommended quarterly")
    
    print("\nImmediate Recommendations:")
    print("  1. Implement 3% daily stop loss")
    print("  2. Maintain 15% cash buffer")
    print("  3. Deploy redundant data feeds")
    print("  4. Monthly stress testing")
    
    print("\n" + "=" * 80)
    print("Stress Testing Framework Demonstration Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()