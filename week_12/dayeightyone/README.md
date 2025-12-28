# Day 81: Stress Testing & Edge Case Simulation

## Objective
Implement comprehensive stress testing frameworks to evaluate strategy performance under extreme market conditions and edge cases.

## Core Concepts
* **Market Stress Scenarios**: Historical stress periods (2008 crisis, 2020 COVID crash, Flash crashes), hypothetical scenarios (liquidity droughts, correlation breakdowns), regulatory change impacts and black swan events
* **Portfolio Stress Testing**: Maximum loss scenarios under various market shocks, liquidity-adjusted risk measures, counterparty risk and settlement failure simulations
* **System Failure Scenarios**: Network latency and disconnection simulations, data feed corruption and missing data handling, order execution failure recovery procedures
* **Sensitivity to Assumptions**: Transaction cost sensitivity analysis, slippage model robustness testing, financing cost and margin requirement impacts

## Tutorial: Historical Stress Testing Framework

```python
# stress_testing_framework.py
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')


class MarketStressTester:
    """
    Comprehensive market stress testing framework for trading strategies.
    """
    
    def __init__(self, returns_data: pd.DataFrame, portfolio_weights: pd.Series):
        """
        Initialize stress tester.
        
        Parameters:
        -----------
        returns_data : pd.DataFrame
            Historical returns data (assets as columns, dates as index)
        portfolio_weights : pd.Series
            Portfolio weights for each asset
        """
        self.returns = returns_data
        self.weights = portfolio_weights
        self.stress_periods = self._define_stress_periods()
        
    def _define_stress_periods(self) -> Dict[str, Tuple[str, str]]:
        """Define major historical stress periods."""
        return {
            'dotcom_crash': ('2000-03-10', '2002-10-09'),
            'gfc_2008': ('2007-10-09', '2009-03-09'),
            'european_debt_crisis': ('2010-04-01', '2012-06-01'),
            'china_2015': ('2015-06-12', '2016-02-12'),
            'covid_crash': ('2020-02-19', '2020-03-23'),
            'inflation_2022': ('2022-01-03', '2022-10-12')
        }
    
    def analyze_historical_stress_periods(self) -> pd.DataFrame:
        """Analyze portfolio performance during historical stress periods."""
        results = []
        
        for period_name, (start_date, end_date) in self.stress_periods.items():
            # Get returns for the stress period
            period_returns = self.returns.loc[start_date:end_date]
            
            if len(period_returns) > 0:
                # Calculate portfolio returns
                portfolio_returns = period_returns.dot(self.weights)
                
                # Calculate stress metrics
                stress_metrics = self._calculate_stress_metrics(portfolio_returns)
                
                # Add to results
                results.append({
                    'stress_period': period_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': len(period_returns),
                    **stress_metrics
                })
        
        return pd.DataFrame(results)
    
    def _calculate_stress_metrics(self, returns: pd.Series) -> Dict:
        """Calculate comprehensive stress testing metrics."""
        # Convert returns to cumulative performance
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # Calculate various stress metrics
        metrics = {
            'total_return': cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(cumulative_returns),
            'drawdown_duration': self._calculate_max_drawdown_duration(cumulative_returns),
            'volatility': returns.std() * np.sqrt(252),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'var_95': np.percentile(returns, 5),
            'expected_shortfall_95': returns[returns <= np.percentile(returns, 5)].mean(),
            'worst_day': returns.min(),
            'best_day': returns.max(),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'calmar_ratio': returns.mean() * 252 / abs(self._calculate_max_drawdown(cumulative_returns)) if abs(self._calculate_max_drawdown(cumulative_returns)) > 0 else 0
        }
        
        # Add recovery metrics
        recovery_metrics = self._calculate_recovery_metrics(cumulative_returns)
        metrics.update(recovery_metrics)
        
        return metrics
    
    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(cumulative_returns) == 0:
            return 0
        
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / (1 + running_max)
        return drawdowns.min()
    
    def _calculate_max_drawdown_duration(self, cumulative_returns: pd.Series) -> int:
        """Calculate duration of maximum drawdown in days."""
        if len(cumulative_returns) == 0:
            return 0
        
        running_max = cumulative_returns.expanding().max()
        in_drawdown = cumulative_returns < running_max.shift(1)
        
        # Find longest consecutive drawdown period
        max_duration = 0
        current_duration = 0
        
        for in_dd in in_drawdown:
            if in_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_duration
    
    def _calculate_recovery_metrics(self, cumulative_returns: pd.Series) -> Dict:
        """Calculate recovery metrics from drawdowns."""
        if len(cumulative_returns) < 2:
            return {
                'recovery_time_95': 0,
                'recovery_time_99': 0,
                'average_recovery_speed': 0
            }
        
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / (1 + running_max)
        
        # Find drawdown peaks
        drawdown_peaks = []
        for i in range(1, len(drawdowns) - 1):
            if drawdowns.iloc[i] < drawdowns.iloc[i-1] and drawdowns.iloc[i] < drawdowns.iloc[i+1]:
                if drawdowns.iloc[i] < -0.05:  # Only consider >5% drawdowns
                    drawdown_peaks.append(i)
        
        # Calculate recovery times
        recovery_times = []
        for peak_idx in drawdown_peaks:
            peak_dd = drawdowns.iloc[peak_idx]
            
            # Find when cumulative returns recover to pre-drawdown level
            for i in range(peak_idx + 1, len(cumulative_returns)):
                if cumulative_returns.iloc[i] >= running_max.iloc[peak_idx]:
                    recovery_times.append(i - peak_idx)
                    break
        
        if recovery_times:
            return {
                'avg_recovery_days': np.mean(recovery_times),
                'max_recovery_days': np.max(recovery_times),
                'recovery_time_95': np.percentile(recovery_times, 95) if len(recovery_times) >= 20 else np.max(recovery_times),
                'recovery_time_99': np.percentile(recovery_times, 99) if len(recovery_times) >= 100 else np.max(recovery_times),
                'recovery_consistency': len(recovery_times) / len(drawdown_peaks) if drawdown_peaks else 1
            }
        else:
            return {
                'avg_recovery_days': 0,
                'max_recovery_days': 0,
                'recovery_time_95': 0,
                'recovery_time_99': 0,
                'recovery_consistency': 1
            }
    
    def generate_hypothetical_scenarios(self) -> Dict:
        """Generate hypothetical stress scenarios."""
        scenarios = {
            'market_crash': self._market_crash_scenario(),
            'liquidity_crisis': self._liquidity_crisis_scenario(),
            'volatility_spike': self._volatility_spike_scenario(),
            'correlation_breakdown': self._correlation_breakdown_scenario(),
            'sector_rotation': self._sector_rotation_scenario(),
            'interest_rate_shock': self._interest_rate_shock_scenario()
        }
        
        return scenarios
    
    def _market_crash_scenario(self) -> Dict:
        """Simulate a market crash scenario (-20% to -40% across assets)."""
        crash_magnitude = np.random.uniform(-0.4, -0.2)
        
        # Different assets crash by different amounts
        n_assets = len(self.weights)
        asset_crash = np.random.uniform(crash_magnitude * 0.8, crash_magnitude * 1.2, n_assets)
        
        portfolio_crash = np.dot(self.weights.values, asset_crash)
        
        return {
            'scenario': 'market_crash',
            'portfolio_impact': portfolio_crash,
            'asset_impacts': dict(zip(self.weights.index, asset_crash)),
            'confidence_interval': [portfolio_crash * 0.9, portfolio_crash * 1.1]
        }
    
    def _liquidity_crisis_scenario(self) -> Dict:
        """Simulate a liquidity crisis with widened spreads and reduced volumes."""
        # Base market impact
        base_impact = np.random.uniform(-0.15, -0.08)
        
        # Liquidity scores for different assets (hypothetical)
        liquidity_scores = {
            'SPY': 0.9, 'QQQ': 0.8, 'IWM': 0.6, 'TLT': 0.7,
            'GLD': 0.7, 'HYG': 0.5, 'LQD': 0.6, 'VNQ': 0.5
        }
        
        # Assets with lower liquidity suffer more
        asset_impacts = {}
        for asset in self.weights.index:
            if asset in liquidity_scores:
                impact = base_impact * (2 - liquidity_scores[asset])  # Lower liquidity = worse impact
            else:
                impact = base_impact * 1.5  # Unknown assets penalized
            asset_impacts[asset] = impact
        
        portfolio_impact = np.dot(self.weights.values, list(asset_impacts.values()))
        
        return {
            'scenario': 'liquidity_crisis',
            'portfolio_impact': portfolio_impact,
            'asset_impacts': asset_impacts,
            'liquidity_multipliers': liquidity_scores
        }
    
    def _volatility_spike_scenario(self) -> Dict:
        """Simulate volatility spike affecting option-heavy or leveraged strategies."""
        # Normal volatility vs stressed volatility
        normal_vol = self.returns.std().mean() * np.sqrt(252)
        stressed_vol = normal_vol * np.random.uniform(2.0, 4.0)  # 2-4x volatility spike
        
        # Impact depends on strategy type and leverage
        # For simplicity, assume quadratic impact based on current volatility exposure
        vol_exposure = self.weights.abs().sum()  # Rough proxy for volatility exposure
        impact_multiplier = (stressed_vol**2 / normal_vol**2 - 1) * vol_exposure
        
        portfolio_impact = np.random.uniform(-0.1, -0.05) * impact_multiplier
        
        return {
            'scenario': 'volatility_spike',
            'portfolio_impact': portfolio_impact,
            'normal_volatility': normal_vol,
            'stressed_volatility': stressed_vol,
            'volatility_multiplier': stressed_vol / normal_vol,
            'volatility_exposure': vol_exposure
        }
    
    def _correlation_breakdown_scenario(self) -> Dict:
        """Simulate correlation breakdown where diversification fails."""
        # In normal markets, correlations provide diversification
        # In stress, correlations → 1, diversification fails
        
        current_corr = self.returns.corr().mean().mean()
        stressed_corr = min(0.9, current_corr + np.random.uniform(0.3, 0.6))
        
        # Impact: portfolio behaves like single asset
        worst_asset_return = self.returns.min(axis=1).mean() * np.sqrt(252)
        portfolio_impact = worst_asset_return * np.random.uniform(0.8, 1.2)
        
        return {
            'scenario': 'correlation_breakdown',
            'portfolio_impact': portfolio_impact,
            'current_correlation': current_corr,
            'stressed_correlation': stressed_corr,
            'diversification_benefit_loss': stressed_corr - current_corr
        }
    
    def _sector_rotation_scenario(self) -> Dict:
        """Simulate sudden sector rotation."""
        # Define sector groups
        sectors = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
            'financials': ['JPM', 'BAC', 'GS', 'MS', 'C'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABT'],
            'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
            'consumer': ['PG', 'KO', 'PEP', 'WMT', 'COST']
        }
        
        # Random sector gets hit, another benefits
        hit_sector = np.random.choice(list(sectors.keys()))
        benefit_sector = np.random.choice([s for s in sectors.keys() if s != hit_sector])
        
        hit_impact = np.random.uniform(-0.25, -0.15)
        benefit_impact = np.random.uniform(0.05, 0.15)
        
        # Calculate portfolio impact
        portfolio_impact = 0
        asset_impacts = {}
        
        for asset, weight in self.weights.items():
            asset_sector = None
            for sector, stocks in sectors.items():
                if asset in stocks:
                    asset_sector = sector
                    break
            
            if asset_sector == hit_sector:
                impact = hit_impact
            elif asset_sector == benefit_sector:
                impact = benefit_impact
            else:
                impact = np.random.uniform(-0.05, 0.05)
            
            asset_impacts[asset] = impact
            portfolio_impact += weight * impact
        
        return {
            'scenario': 'sector_rotation',
            'portfolio_impact': portfolio_impact,
            'hit_sector': hit_sector,
            'benefit_sector': benefit_sector,
            'hit_sector_impact': hit_impact,
            'benefit_sector_impact': benefit_impact,
            'asset_impacts': asset_impacts
        }
    
    def _interest_rate_shock_scenario(self) -> Dict:
        """Simulate interest rate shock affecting different asset classes differently."""
        rate_shock = np.random.uniform(1.0, 3.0)  # 100-300 bps rate increase
        
        # Different asset class sensitivities
        sensitivities = {
            'bonds': -0.05,  # Duration effect
            'growth_stocks': -0.03,  # Higher discount rate
            'value_stocks': -0.01,
            'real_estate': -0.04,
            'gold': 0.02,  # Inflation hedge
            'cash': 0.00
        }
        
        # Map assets to sensitivities (simplified)
        asset_impacts = {}
        for asset in self.weights.index:
            if 'TLT' in asset or 'IEF' in asset:
                sensitivity = sensitivities['bonds']
            elif 'QQQ' in asset or 'tech' in asset.lower():
                sensitivity = sensitivities['growth_stocks']
            elif 'VNQ' in asset or 'real_estate' in asset.lower():
                sensitivity = sensitivities['real_estate']
            elif 'GLD' in asset or 'gold' in asset.lower():
                sensitivity = sensitivities['gold']
            else:
                sensitivity = sensitivities['value_stocks']
            
            impact = sensitivity * rate_shock
            asset_impacts[asset] = impact
        
        portfolio_impact = np.dot(self.weights.values, list(asset_impacts.values()))
        
        return {
            'scenario': 'interest_rate_shock',
            'portfolio_impact': portfolio_impact,
            'rate_shock_bps': rate_shock * 100,
            'asset_impacts': asset_impacts,
            'sensitivities': sensitivities
        }
    
    def run_monte_carlo_stress_test(self, n_simulations: int = 10000) -> Dict:
        """Run Monte Carlo simulation of extreme events."""
        # Fit distributions to returns
        fitted_params = {}
        for asset in self.returns.columns:
            asset_returns = self.returns[asset].dropna()
            if len(asset_returns) > 30:
                # Fit t-distribution (fat tails)
                df, loc, scale = stats.t.fit(asset_returns)
                fitted_params[asset] = {'dist': 't', 'df': df, 'loc': loc, 'scale': scale}
            else:
                # Use normal if insufficient data
                fitted_params[asset] = {'dist': 'normal', 'mean': asset_returns.mean(), 'std': asset_returns.std()}
        
        # Generate extreme scenarios
        extreme_returns = []
        for _ in range(n_simulations):
            # Sometimes simulate extreme correlations
            if np.random.random() < 0.1:  # 10% chance of extreme correlation
                # All assets move together
                common_shock = np.random.standard_t(3) * 0.05  # Fat-tailed common shock
                asset_returns = {asset: common_shock * np.random.uniform(0.8, 1.2) 
                                for asset in self.returns.columns}
            else:
                # Generate from fitted distributions
                asset_returns = {}
                for asset, params in fitted_params.items():
                    if params['dist'] == 't':
                        r = stats.t.rvs(df=params['df'], loc=params['loc'], scale=params['scale'])
                    else:
                        r = np.random.normal(params['mean'], params['std'])
                    asset_returns[asset] = r
            
            # Calculate portfolio return
            port_return = np.dot(self.weights.values, list(asset_returns.values()))
            extreme_returns.append(port_return)
        
        extreme_returns = np.array(extreme_returns)
        
        # Calculate extreme metrics
        results = {
            'mean_extreme_return': extreme_returns.mean(),
            'std_extreme_return': extreme_returns.std(),
            'var_99': np.percentile(extreme_returns, 1),
            'expected_shortfall_99': extreme_returns[extreme_returns <= np.percentile(extreme_returns, 1)].mean(),
            'worst_case_1pct': np.percentile(extreme_returns, 0.5),
            'worst_case_0pct': extreme_returns.min(),
            'probability_loss_10pct': (extreme_returns < -0.10).mean(),
            'probability_loss_20pct': (extreme_returns < -0.20).mean(),
            'extreme_returns_distribution': {
                'percentiles': np.percentile(extreme_returns, [0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9])
            }
        }
        
        return results
    
    def analyze_system_failures(self) -> Dict:
        """Analyze impact of system failures on strategy."""
        failure_scenarios = {
            'data_feed_outage': self._data_feed_outage_scenario(),
            'network_latency': self._network_latency_scenario(),
            'order_execution_failure': self._order_execution_failure_scenario(),
            'risk_system_failure': self._risk_system_failure_scenario()
        }
        
        return failure_scenarios
    
    def _data_feed_outage_scenario(self) -> Dict:
        """Simulate data feed outage impact."""
        # Duration of outage (hours)
        outage_duration = np.random.choice([1, 2, 4, 8, 24])
        
        # Impact depends on strategy frequency
        # High-frequency: catastrophic, Low-frequency: manageable
        
        # Estimate missed opportunities
        avg_daily_volume = self.returns.abs().mean().mean() * np.sqrt(252)
        missed_opportunities = avg_daily_volume * (outage_duration / 24) * np.random.uniform(0.5, 2.0)
        
        # Risk of stale prices
        stale_price_risk = np.random.uniform(0.001, 0.01) * outage_duration
        
        return {
            'scenario': 'data_feed_outage',
            'outage_duration_hours': outage_duration,
            'estimated_loss': missed_opportunities + stale_price_risk,
            'components': {
                'missed_opportunities': missed_opportunities,
                'stale_price_risk': stale_price_risk
            },
            'recovery_time_hours': outage_duration * np.random.uniform(0.5, 2.0)
        }
    
    def _network_latency_scenario(self) -> Dict:
        """Simulate network latency impact."""
        latency_ms = np.random.choice([100, 250, 500, 1000, 2000])
        
        # Impact on execution quality
        # Higher latency = worse execution
        slippage_multiplier = 1 + (latency_ms / 1000) * np.random.uniform(0.5, 2.0)
        
        # Missed fills probability
        missed_fill_probability = min(0.3, (latency_ms / 1000) * 0.1)
        
        return {
            'scenario': 'network_latency',
            'latency_ms': latency_ms,
            'slippage_multiplier': slippage_multiplier,
            'missed_fill_probability': missed_fill_probability,
            'estimated_impact_pct': (slippage_multiplier - 1) * 0.1 + missed_fill_probability * 0.05
        }
    
    def _order_execution_failure_scenario(self) -> Dict:
        """Simulate order execution failure impact."""
        failure_rate = np.random.uniform(0.001, 0.01)  # 0.1% to 1% failure rate
        
        # Consequences of failed execution
        consequences = {
            'missed_profits': np.random.uniform(0.001, 0.01),
            'unhedged_risk': np.random.uniform(0.002, 0.02),
            'regulatory_issues': np.random.uniform(0.0001, 0.001),
            'reputational_damage': np.random.uniform(0.0005, 0.005)
        }
        
        total_impact = sum(consequences.values()) * failure_rate * 100  # Annualized
        
        return {
            'scenario': 'order_execution_failure',
            'failure_rate': failure_rate,
            'total_impact_pct': total_impact,
            'consequences': consequences,
            'mitigation_cost_pct': total_impact * np.random.uniform(0.1, 0.5)
        }
    
    def _risk_system_failure_scenario(self) -> Dict:
        """Simulate risk system failure impact."""
        # Without risk controls, potential for unlimited losses
        duration_hours = np.random.choice([1, 2, 4, 8])
        
        # Estimate potential losses without risk limits
        avg_daily_vol = self.returns.std().mean() * np.sqrt(252)
        potential_loss = avg_daily_vol * np.sqrt(duration_hours / 24) * np.random.uniform(2, 5)
        
        return {
            'scenario': 'risk_system_failure',
            'duration_hours': duration_hours,
            'potential_loss_pct': potential_loss,
            'probability_catastrophic_loss': min(0.1, duration_hours / 100),
            'recovery_procedures': [
                'manual_override',
                'position_limits',
                'emergency_hedging',
                'market_withdrawal'
            ]
        }
    
    def generate_stress_report(self) -> str:
        """Generate comprehensive stress testing report."""
        report_lines = []
        
        # Historical stress analysis
        report_lines.append("# STRESS TESTING REPORT")
        report_lines.append("## Historical Stress Period Analysis")
        report_lines.append("")
        
        historical_results = self.analyze_historical_stress_periods()
        for _, row in historical_results.iterrows():
            report_lines.append(f"### {row['stress_period'].replace('_', ' ').title()} "
                              f"({row['start_date']} to {row['end_date']})")
            report_lines.append(f"- Duration: {row['duration_days']} days")
            report_lines.append(f"- Total Return: {row['total_return']:.2%}")
            report_lines.append(f"- Max Drawdown: {row['max_drawdown']:.2%}")
            report_lines.append(f"- Volatility: {row['volatility']:.2%}")
            report_lines.append(f"- VaR (95%): {row['var_95']:.2%}")
            report_lines.append("")
        
        # Hypothetical scenarios
        report_lines.append("## Hypothetical Stress Scenarios")
        report_lines.append("")
        
        hypothetical = self.generate_hypothetical_scenarios()
        for scenario_name, scenario in hypothetical.items():
            report_lines.append(f"### {scenario_name.replace('_', ' ').title()}")
            report_lines.append(f"- Portfolio Impact: {scenario['portfolio_impact']:.2%}")
            if 'confidence_interval' in scenario:
                ci = scenario['confidence_interval']
                report_lines.append(f"- 90% CI: [{ci[0]:.2%}, {ci[1]:.2%}]")
            report_lines.append("")
        
        # Monte Carlo extreme events
        report_lines.append("## Monte Carlo Extreme Event Analysis")
        report_lines.append("")
        
        mc_results = self.run_monte_carlo_stress_test(n_simulations=5000)
        report_lines.append(f"- Expected Shortfall (99%): {mc_results['expected_shortfall_99']:.2%}")
        report_lines.append(f"- Probability of >10% loss: {mc_results['probability_loss_10pct']:.2%}")
        report_lines.append(f"- Probability of >20% loss: {mc_results['probability_loss_20pct']:.2%}")
        report_lines.append(f"- Worst Case (0.5%): {mc_results['worst_case_1pct']:.2%}")
        report_lines.append("")
        
        # System failures
        report_lines.append("## System Failure Analysis")
        report_lines.append("")
        
        failures = self.analyze_system_failures()
        for failure_name, failure in failures.items():
            report_lines.append(f"### {failure_name.replace('_', ' ').title()}")
            report_lines.append(f"- Estimated Impact: {failure.get('estimated_loss', failure.get('total_impact_pct', failure.get('potential_loss_pct', 0))):.2%}")
            if 'duration_hours' in failure:
                report_lines.append(f"- Duration: {failure['duration_hours']} hours")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Risk Mitigation Recommendations")
        report_lines.append("")
        report_lines.append("1. **Position Limits**: Reduce maximum position sizes by 20-30%")
        report_lines.append("2. **Stop Losses**: Implement dynamic stop losses at 2-3% daily loss")
        report_lines.append("3. **Liquidity Requirements**: Maintain 10-15% cash buffer")
        report_lines.append("4. **Stress Testing Frequency**: Run comprehensive stress tests quarterly")
        report_lines.append("5. **System Redundancy**: Implement backup systems for critical components")
        report_lines.append("6. **Scenario Planning**: Develop playbooks for identified stress scenarios")
        
        return "\n".join(report_lines)


# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2010-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    n_assets = 8
    
    # Generate correlated returns
    means = np.random.uniform(0.0001, 0.0003, n_assets)
    cov = np.random.uniform(0.0001, 0.0003, (n_assets, n_assets))
    np.fill_diagonal(cov, np.random.uniform(0.0002, 0.0004, n_assets))
    cov = (cov + cov.T) / 2  # Make symmetric
    
    # Generate multivariate normal returns
    returns = np.random.multivariate_normal(means, cov, n_dates)
    
    # Create DataFrame
    assets = ['SPY', 'QQQ', 'IWM', 'TLT', 'GLD', 'HYG', 'LQD', 'VNQ']
    returns_df = pd.DataFrame(returns, index=dates, columns=assets)
    
    # Create sample portfolio weights
    weights = pd.Series(np.random.dirichlet(np.ones(n_assets)), index=assets)
    
    # Initialize stress tester
    tester = MarketStressTester(returns_df, weights)
    
    # Generate report
    report = tester.generate_stress_report()
    print(report)
    
    # Save report
    with open('stress_test_report.md', 'w') as f:
        f.write(report)
    
    print("\n✅ Stress testing report saved to 'stress_test_report.md'")