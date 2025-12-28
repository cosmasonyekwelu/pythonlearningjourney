# Day 82: Risk Assessment Tools & Exposure Management

## Objective
Build advanced risk assessment tools for real-time exposure monitoring, concentration risk analysis, and regulatory compliance.

## Core Concepts
* **Real-Time Risk Monitoring**: Position-level and portfolio-level risk metrics, concentration limits and diversification scoring, leverage and margin utilization tracking
* **Exposure Analytics**: Sector, industry, and geographical exposure decomposition, factor exposure analysis using PCA and statistical models, correlation and beta exposure to benchmarks
* **Regulatory Risk Measures**: Value-at-Risk (VaR) calculation using historical, parametric, and Monte Carlo methods, Expected Shortfall (ES) and tail risk measures, stress testing for regulatory compliance (CCAR, DFAST)
* **Liquidity Risk Assessment**: Position liquidity scoring based on volume and bid-ask spreads, market impact estimation for large positions, exit strategy analysis under stressed conditions

## Tutorial: Real-Time Risk Dashboard Implementation

```python
# risk_dashboard.py
import numpy as np
import pandas as pd
from scipy import stats, optimize
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Optional imports for visualization
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@dataclass
class Position:
    """Data class for trading positions."""
    symbol: str
    quantity: float
    price: float
    sector: str = ""
    country: str = "US"
    asset_class: str = "equity"
    notional_value: float = field(init=False)
    
    def __post_init__(self):
        """Calculate notional value."""
        self.notional_value = self.quantity * self.price


@dataclass
class RiskLimit:
    """Data class for risk limits."""
    limit_type: str
    threshold: float
    warning_level: float = 0.8  # 80% of threshold triggers warning
    time_horizon: str = "daily"  # daily, weekly, monthly
    measurement_method: str = "absolute"  # absolute, relative


class RealTimeRiskDashboard:
    """
    Real-time risk monitoring and exposure management dashboard.
    
    Features:
    - Real-time position monitoring
    - Concentration risk analysis
    - VaR and Expected Shortfall calculation
    - Liquidity risk assessment
    - Regulatory compliance checks
    - Alert generation
    """
    
    def __init__(self, positions: List[Position], 
                 market_data: pd.DataFrame,
                 risk_limits: Optional[List[RiskLimit]] = None):
        """
        Initialize risk dashboard.
        
        Parameters:
        -----------
        positions : List[Position]
            Current trading positions
        market_data : pd.DataFrame
            Historical market data with returns
        risk_limits : List[RiskLimit], optional
            Risk limits to monitor
        """
        self.positions = positions
        self.market_data = market_data
        self.risk_limits = risk_limits or self._default_risk_limits()
        
        # Initialize data structures
        self.position_df = self._create_position_dataframe()
        self.alerts = []
        self.risk_metrics = {}
        
        # Calculate initial metrics
        self._calculate_all_metrics()
    
    def _create_position_dataframe(self) -> pd.DataFrame:
        """Create DataFrame from positions."""
        data = []
        for pos in self.positions:
            data.append({
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'price': pos.price,
                'notional_value': pos.notional_value,
                'sector': pos.sector,
                'country': pos.country,
                'asset_class': pos.asset_class
            })
        
        df = pd.DataFrame(data)
        
        # Add weights
        total_value = df['notional_value'].sum()
        if total_value > 0:
            df['weight'] = df['notional_value'] / total_value
        else:
            df['weight'] = 0
        
        return df
    
    def _default_risk_limits(self) -> List[RiskLimit]:
        """Create default risk limits."""
        return [
            RiskLimit('max_position_size', 0.10),  # No position > 10%
            RiskLimit('max_sector_exposure', 0.25),  # No sector > 25%
            RiskLimit('max_country_exposure', 0.50),  # No country > 50%
            RiskLimit('max_leverage', 2.0),  # Max leverage 2:1
            RiskLimit('var_95_daily', -0.05),  # Daily VaR(95%) < 5%
            RiskLimit('expected_shortfall_95_daily', -0.08),  # ES(95%) < 8%
            RiskLimit('max_drawdown', -0.20),  # Max drawdown < 20%
            RiskLimit('liquidity_coverage_ratio', 0.80)  # LCR > 80%
        ]
    
    def _calculate_all_metrics(self):
        """Calculate all risk metrics."""
        # Portfolio metrics
        self.risk_metrics['portfolio_value'] = self.position_df['notional_value'].sum()
        self.risk_metrics['num_positions'] = len(self.position_df)
        
        # Concentration metrics
        self.risk_metrics.update(self._calculate_concentration_metrics())
        
        # Factor exposures
        self.risk_metrics.update(self._calculate_factor_exposures())
        
        # VaR and ES
        self.risk_metrics.update(self._calculate_var_es())
        
        # Liquidity metrics
        self.risk_metrics.update(self._calculate_liquidity_metrics())
        
        # Check limits
        self._check_risk_limits()
    
    def _calculate_concentration_metrics(self) -> Dict:
        """Calculate concentration risk metrics."""
        metrics = {}
        
        # Position concentration
        metrics['max_position_weight'] = self.position_df['weight'].max()
        metrics['top_3_position_concentration'] = self.position_df['weight'].nlargest(3).sum()
        metrics['herfindahl_index'] = (self.position_df['weight'] ** 2).sum()
        
        # Sector concentration
        if 'sector' in self.position_df.columns:
            sector_weights = self.position_df.groupby('sector')['weight'].sum()
            metrics['max_sector_exposure'] = sector_weights.max()
            metrics['num_sectors'] = len(sector_weights)
            metrics['sector_herfindahl'] = (sector_weights ** 2).sum()
        
        # Country concentration
        if 'country' in self.position_df.columns:
            country_weights = self.position_df.groupby('country')['weight'].sum()
            metrics['max_country_exposure'] = country_weights.max()
            metrics['num_countries'] = len(country_weights)
        
        # Asset class concentration
        if 'asset_class' in self.position_df.columns:
            asset_weights = self.position_df.groupby('asset_class')['weight'].sum()
            metrics['max_asset_class_exposure'] = asset_weights.max()
        
        # Diversification score (0-100)
        diversification_score = 100 * (1 - metrics.get('herfindahl_index', 0))
        metrics['diversification_score'] = diversification_score
        
        return metrics
    
    def _calculate_factor_exposures(self) -> Dict:
        """Calculate factor exposures."""
        # This is a simplified version
        # In practice, would use factor models like Barra, Axioma, etc.
        
        metrics = {}
        
        # Market beta (simplified)
        if 'SPY' in self.market_data.columns and len(self.position_df) > 0:
            # Calculate portfolio returns (simplified)
            portfolio_symbols = [pos.symbol for pos in self.positions 
                               if pos.symbol in self.market_data.columns]
            
            if portfolio_symbols:
                portfolio_returns = self.market_data[portfolio_symbols].mean(axis=1)
                market_returns = self.market_data['SPY']
                
                # Calculate beta
                covariance = portfolio_returns.cov(market_returns)
                market_variance = market_returns.var()
                
                if market_variance > 0:
                    beta = covariance / market_variance
                    metrics['market_beta'] = beta
                else:
                    metrics['market_beta'] = 1.0
            else:
                metrics['market_beta'] = 1.0
        else:
            metrics['market_beta'] = 1.0
        
        # Size, value, momentum exposures (simplified)
        # In practice, would use factor returns data
        metrics['size_exposure'] = 0.0  # Neutral
        metrics['value_exposure'] = 0.0  # Neutral
        metrics['momentum_exposure'] = 0.0  # Neutral
        metrics['quality_exposure'] = 0.0  # Neutral
        metrics['volatility_exposure'] = 0.0  # Neutral
        
        # Factor concentration
        factor_exposures = [
            metrics['market_beta'],
            abs(metrics['size_exposure']),
            abs(metrics['value_exposure']),
            abs(metrics['momentum_exposure']),
            abs(metrics['quality_exposure']),
            abs(metrics['volatility_exposure'])
        ]
        
        metrics['factor_concentration'] = np.std(factor_exposures) / np.mean(factor_exposures) \
            if np.mean(factor_exposures) > 0 else 0
        
        return metrics
    
    def _calculate_var_es(self, confidence_level: float = 0.95, 
                         method: str = 'historical') -> Dict:
        """
        Calculate Value at Risk and Expected Shortfall.
        
        Parameters:
        -----------
        confidence_level : float
            Confidence level for VaR/ES (e.g., 0.95 for 95%)
        method : str
            'historical', 'parametric', or 'monte_carlo'
        """
        portfolio_symbols = [pos.symbol for pos in self.positions 
                           if pos.symbol in self.market_data.columns]
        
        if not portfolio_symbols:
            return {
                f'var_{int(confidence_level*100)}': 0,
                f'es_{int(confidence_level*100)}': 0
            }
        
        # Get portfolio weights
        weights_dict = dict(zip(self.position_df['symbol'], self.position_df['weight']))
        weights = np.array([weights_dict.get(sym, 0) for sym in portfolio_symbols])
        
        # Get returns for portfolio symbols
        returns = self.market_data[portfolio_symbols].dropna()
        
        if len(returns) == 0:
            return {
                f'var_{int(confidence_level*100)}': 0,
                f'es_{int(confidence_level*100)}': 0
            }
        
        if method == 'historical':
            return self._calculate_historical_var_es(returns, weights, confidence_level)
        elif method == 'parametric':
            return self._calculate_parametric_var_es(returns, weights, confidence_level)
        elif method == 'monte_carlo':
            return self._calculate_monte_carlo_var_es(returns, weights, confidence_level)
        else:
            raise ValueError(f"Unknown VaR method: {method}")
    
    def _calculate_historical_var_es(self, returns: pd.DataFrame, 
                                    weights: np.ndarray,
                                    confidence_level: float) -> Dict:
        """Calculate historical VaR and ES."""
        # Calculate portfolio returns
        portfolio_returns = returns.dot(weights)
        
        # Calculate VaR and ES
        var_percentile = (1 - confidence_level) * 100
        var = np.percentile(portfolio_returns, var_percentile)
        es = portfolio_returns[portfolio_returns <= var].mean()
        
        return {
            f'var_{int(confidence_level*100)}': var,
            f'es_{int(confidence_level*100)}': es,
            'var_method': 'historical',
            'lookback_days': len(returns)
        }
    
    def _calculate_parametric_var_es(self, returns: pd.DataFrame,
                                    weights: np.ndarray,
                                    confidence_level: float) -> Dict:
        """Calculate parametric (normal distribution) VaR and ES."""
        # Calculate portfolio mean and variance
        portfolio_mean = returns.mean().dot(weights)
        portfolio_std = np.sqrt(weights.T @ returns.cov() @ weights)
        
        # Calculate VaR and ES under normality assumption
        z_score = stats.norm.ppf(1 - confidence_level)
        var = portfolio_mean + z_score * portfolio_std
        es = portfolio_mean + portfolio_std * stats.norm.pdf(z_score) / (1 - confidence_level)
        
        return {
            f'var_{int(confidence_level*100)}': var,
            f'es_{int(confidence_level*100)}': es,
            'var_method': 'parametric',
            'portfolio_mean': portfolio_mean,
            'portfolio_std': portfolio_std
        }
    
    def _calculate_monte_carlo_var_es(self, returns: pd.DataFrame,
                                     weights: np.ndarray,
                                     confidence_level: float,
                                     n_simulations: int = 10000) -> Dict:
        """Calculate VaR and ES using Monte Carlo simulation."""
        # Fit distributions to returns
        means = returns.mean()
        cov = returns.cov()
        
        # Generate Monte Carlo simulations
        simulated_returns = np.random.multivariate_normal(means, cov, n_simulations)
        portfolio_returns = simulated_returns.dot(weights)
        
        # Calculate VaR and ES
        var_percentile = (1 - confidence_level) * 100
        var = np.percentile(portfolio_returns, var_percentile)
        es = portfolio_returns[portfolio_returns <= var].mean()
        
        return {
            f'var_{int(confidence_level*100)}': var,
            f'es_{int(confidence_level*100)}': es,
            'var_method': 'monte_carlo',
            'n_simulations': n_simulations
        }
    
    def _calculate_liquidity_metrics(self) -> Dict:
        """Calculate liquidity risk metrics."""
        # Simplified liquidity metrics
        # In practice, would use actual volume and spread data
        
        metrics = {}
        
        # Average position size relative to average daily volume
        # Assuming we have volume data
        if all(pos.symbol in self.market_data.columns for pos in self.positions):
            volumes = []
            for pos in self.positions:
                if f"{pos.symbol}_volume" in self.market_data.columns:
                    avg_volume = self.market_data[f"{pos.symbol}_volume"].mean()
                    if avg_volume > 0:
                        days_to_liquidate = pos.quantity / (avg_volume * 0.1)  # 10% of volume
                        volumes.append(days_to_liquidate)
            
            if volumes:
                metrics['avg_days_to_liquidate'] = np.mean(volumes)
                metrics['max_days_to_liquidate'] = np.max(volumes)
                metrics['liquidity_score'] = 100 / (1 + metrics['avg_days_to_liquidate'])
            else:
                metrics['avg_days_to_liquidate'] = 1.0
                metrics['max_days_to_liquidate'] = 2.0
                metrics['liquidity_score'] = 50.0
        else:
            metrics['avg_days_to_liquidate'] = 1.0
            metrics['max_days_to_liquidate'] = 2.0
            metrics['liquidity_score'] = 50.0
        
        # Liquidity Coverage Ratio (simplified)
        # High-quality liquid assets / net cash outflow over 30 days
        metrics['liquidity_coverage_ratio'] = 0.9  # Placeholder
        
        # Market impact cost (simplified)
        metrics['estimated_market_impact_bps'] = 5.0  # 5 bps average impact
        
        return metrics
    
    def _check_risk_limits(self):
        """Check all risk limits and generate alerts if breached."""
        self.alerts = []
        
        for limit in self.risk_limits:
            current_value = self._get_current_metric_value(limit.limit_type)
            
            if current_value is not None:
                # Check for breach
                if limit.measurement_method == 'absolute':
                    is_breached = abs(current_value) > abs(limit.threshold)
                    warning_level = limit.threshold * limit.warning_level
                    is_warning = abs(current_value) > abs(warning_level)
                else:  # relative
                    is_breached = current_value > limit.threshold
                    warning_level = limit.threshold * limit.warning_level
                    is_warning = current_value > warning_level
                
                if is_breached:
                    alert = {
                        'timestamp': datetime.now(),
                        'limit_type': limit.limit_type,
                        'current_value': current_value,
                        'threshold': limit.threshold,
                        'severity': 'CRITICAL',
                        'message': f"{limit.limit_type} breach: {current_value:.2%} > {limit.threshold:.2%}"
                    }
                    self.alerts.append(alert)
                
                elif is_warning:
                    alert = {
                        'timestamp': datetime.now(),
                        'limit_type': limit.limit_type,
                        'current_value': current_value,
                        'threshold': limit.threshold,
                        'severity': 'WARNING',
                        'message': f"{limit.limit_type} warning: {current_value:.2%} > {warning_level:.2%}"
                    }
                    self.alerts.append(alert)
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric."""
        metric_map = {
            'max_position_size': 'max_position_weight',
            'max_sector_exposure': 'max_sector_exposure',
            'max_country_exposure': 'max_country_exposure',
            'var_95_daily': 'var_95',
            'expected_shortfall_95_daily': 'es_95',
            'liquidity_coverage_ratio': 'liquidity_coverage_ratio'
        }
        
        actual_metric = metric_map.get(metric_name, metric_name)
        return self.risk_metrics.get(actual_metric)
    
    def update_positions(self, new_positions: List[Position]):
        """Update positions and recalculate metrics."""
        self.positions = new_positions
        self.position_df = self._create_position_dataframe()
        self._calculate_all_metrics()
    
    def update_market_data(self, new_market_data: pd.DataFrame):
        """Update market data and recalculate metrics."""
        self.market_data = new_market_data
        self._calculate_all_metrics()
    
    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary."""
        summary = {
            'portfolio_summary': {
                'total_value': self.risk_metrics.get('portfolio_value', 0),
                'num_positions': self.risk_metrics.get('num_positions', 0),
                'diversification_score': self.risk_metrics.get('diversification_score', 0)
            },
            'concentration_risk': {
                'max_position': self.risk_metrics.get('max_position_weight', 0),
                'top_3_concentration': self.risk_metrics.get('top_3_position_concentration', 0),
                'max_sector': self.risk_metrics.get('max_sector_exposure', 0),
                'herfindahl_index': self.risk_metrics.get('herfindahl_index', 0)
            },
            'market_risk': {
                'var_95': self.risk_metrics.get('var_95', 0),
                'expected_shortfall_95': self.risk_metrics.get('es_95', 0),
                'market_beta': self.risk_metrics.get('market_beta', 1.0)
            },
            'liquidity_risk': {
                'liquidity_score': self.risk_metrics.get('liquidity_score', 0),
                'avg_days_to_liquidate': self.risk_metrics.get('avg_days_to_liquidate', 0),
                'liquidity_coverage_ratio': self.risk_metrics.get('liquidity_coverage_ratio', 0)
            },
            'alerts': {
                'critical': len([a for a in self.alerts if a['severity'] == 'CRITICAL']),
                'warning': len([a for a in self.alerts if a['severity'] == 'WARNING']),
                'total': len(self.alerts)
            }
        }
        
        return summary
    
    def generate_report(self) -> str:
        """Generate detailed risk report."""
        report_lines = []
        
        report_lines.append("# REAL-TIME RISK DASHBOARD REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Portfolio Summary
        report_lines.append("## Portfolio Summary")
        report_lines.append("")
        report_lines.append(f"- **Total Value**: ${self.risk_metrics.get('portfolio_value', 0):,.2f}")
        report_lines.append(f"- **Number of Positions**: {self.risk_metrics.get('num_positions', 0)}")
        report_lines.append(f"- **Diversification Score**: {self.risk_metrics.get('diversification_score', 0):.1f}/100")
        report_lines.append("")
        
        # Concentration Risk
        report_lines.append("## Concentration Risk")
        report_lines.append("")
        report_lines.append(f"- **Maximum Position Weight**: {self.risk_metrics.get('max_position_weight', 0):.2%}")
        report_lines.append(f"- **Top 3 Positions Concentration**: {self.risk_metrics.get('top_3_position_concentration', 0):.2%}")
        report_lines.append(f"- **Herfindahl-Hirschman Index**: {self.risk_metrics.get('herfindahl_index', 0):.4f}")
        
        if 'max_sector_exposure' in self.risk_metrics:
            report_lines.append(f"- **Maximum Sector Exposure**: {self.risk_metrics['max_sector_exposure']:.2%}")
        if 'max_country_exposure' in self.risk_metrics:
            report_lines.append(f"- **Maximum Country Exposure**: {self.risk_metrics['max_country_exposure']:.2%}")
        
        report_lines.append("")
        
        # Market Risk
        report_lines.append("## Market Risk")
        report_lines.append("")
        report_lines.append(f"- **Daily VaR (95%)**: {self.risk_metrics.get('var_95', 0):.2%}")
        report_lines.append(f"- **Expected Shortfall (95%)**: {self.risk_metrics.get('es_95', 0):.2%}")
        report_lines.append(f"- **Market Beta**: {self.risk_metrics.get('market_beta', 1.0):.2f}")
        report_lines.append("")
        
        # Liquidity Risk
        report_lines.append("## Liquidity Risk")
        report_lines.append("")
        report_lines.append(f"- **Liquidity Score**: {self.risk_metrics.get('liquidity_score', 0):.1f}/100")
        report_lines.append(f"- **Average Days to Liquidate**: {self.risk_metrics.get('avg_days_to_liquidate', 0):.1f} days")
        report_lines.append(f"- **Liquidity Coverage Ratio**: {self.risk_metrics.get('liquidity_coverage_ratio', 0):.2%}")
        report_lines.append("")
        
        # Alerts
        report_lines.append("## Risk Alerts")
        report_lines.append("")
        
        critical_alerts = [a for a in self.alerts if a['severity'] == 'CRITICAL']
        warning_alerts = [a for a in self.alerts if a['severity'] == 'WARNING']
        
        if critical_alerts:
            report_lines.append("### CRITICAL Alerts")
            for alert in critical_alerts:
                report_lines.append(f"- **{alert['limit_type']}**: {alert['message']}")
            report_lines.append("")
        
        if warning_alerts:
            report_lines.append("### WARNING Alerts")
            for alert in warning_alerts:
                report_lines.append(f"- **{alert['limit_type']}**: {alert['message']}")
            report_lines.append("")
        
        if not self.alerts:
            report_lines.append("No active alerts.")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Risk Management Recommendations")
        report_lines.append("")
        
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Report generated by Real-Time Risk Dashboard*")
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        # Check concentration
        max_pos = self.risk_metrics.get('max_position_weight', 0)
        if max_pos > 0.08:  # Close to 10% limit
            recommendations.append("Reduce largest position to maintain diversification")
        
        top3 = self.risk_metrics.get('top_3_position_concentration', 0)
        if top3 > 0.30:  # Top 3 > 30%
            recommendations.append("Diversify away from top 3 positions")
        
        # Check market risk
        var_95 = abs(self.risk_metrics.get('var_95', 0))
        if var_95 > 0.04:  > 4% daily VaR
            recommendations.append("Consider reducing portfolio beta or adding hedges")
        
        # Check liquidity
        liquidity_score = self.risk_metrics.get('liquidity_score', 0)
        if liquidity_score < 60:  # Poor liquidity
            recommendations.append("Increase allocation to more liquid securities")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("Portfolio risk profile appears within acceptable limits")
            recommendations.append("Continue regular monitoring and stress testing")
        
        return recommendations
    
    def visualize_dashboard(self, save_path: Optional[str] = None):
        """Create interactive risk dashboard visualization."""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available for visualization")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('Portfolio Composition', 'Concentration Risk', 
                          'VaR Distribution', 'Liquidity Profile', 
                          'Sector Exposure', 'Risk Metrics Summary',
                          'Alert Status', 'Factor Exposures', 'Historical VaR'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}, {'type': 'histogram'}],
                   [{'type': 'bar'}, {'type': 'pie'}, {'type': 'table'}],
                   [{'type': 'indicator'}, {'type': 'bar'}, {'type': 'line'}]]
        )
        
        # 1. Portfolio Composition (Pie chart)
        if not self.position_df.empty:
            fig.add_trace(
                go.Pie(
                    labels=self.position_df['symbol'],
                    values=self.position_df['notional_value'],
                    hole=0.3,
                    name='Portfolio Composition'
                ),
                row=1, col=1
            )
        
        # 2. Concentration Risk (Bar chart)
        position_weights = self.position_df.nlargest(10, 'weight')
        fig.add_trace(
            go.Bar(
                x=position_weights['symbol'],
                y=position_weights['weight'],
                name='Position Weights',
                marker_color='royalblue'
            ),
            row=1, col=2
        )
        
        # 3. VaR Distribution (Histogram)
        # Simulate portfolio returns for visualization
        if len(self.positions) > 0:
            portfolio_symbols = [pos.symbol for pos in self.positions 
                               if pos.symbol in self.market_data.columns]
            if portfolio_symbols:
                returns = self.market_data[portfolio_symbols].dropna()
                if not returns.empty:
                    weights_dict = dict(zip(self.position_df['symbol'], self.position_df['weight']))
                    weights = np.array([weights_dict.get(sym, 0) for sym in portfolio_symbols])
                    portfolio_returns = returns.dot(weights)
                    
                    fig.add_trace(
                        go.Histogram(
                            x=portfolio_returns,
                            nbinsx=50,
                            name='Return Distribution',
                            marker_color='lightseagreen'
                        ),
                        row=1, col=3
                    )
                    
                    # Add VaR line
                    var_95 = self.risk_metrics.get('var_95', 0)
                    fig.add_vline(x=var_95, line_dash="dash", line_color="red", 
                                 annotation_text=f"VaR 95%: {var_95:.2%}",
                                 row=1, col=3)
        
        # 4. Liquidity Profile (Bar chart)
        # Placeholder - would use actual liquidity data
        fig.add_trace(
            go.Bar(
                x=['High', 'Medium', 'Low'],
                y=[60, 30, 10],
                name='Liquidity Profile',
                marker_color=['green', 'yellow', 'red']
            ),
            row=2, col=1
        )
        
        # 5. Sector Exposure (Pie chart)
        if 'sector' in self.position_df.columns:
            sector_exposure = self.position_df.groupby('sector')['weight'].sum()
            fig.add_trace(
                go.Pie(
                    labels=sector_exposure.index,
                    values=sector_exposure.values,
                    name='Sector Exposure'
                ),
                row=2, col=2
            )
        
        # 6. Risk Metrics Summary (Table)
        metrics_data = [
            ['Metric', 'Value', 'Limit'],
            ['Max Position', f"{self.risk_metrics.get('max_position_weight', 0):.2%}", "10%"],
            ['VaR (95%)', f"{self.risk_metrics.get('var_95', 0):.2%}", "5%"],
            ['ES (95%)', f"{self.risk_metrics.get('es_95', 0):.2%}", "8%"],
            ['Liquidity Score', f"{self.risk_metrics.get('liquidity_score', 0):.1f}", ">60"],
            ['Diversification', f"{self.risk_metrics.get('diversification_score', 0):.1f}", ">70"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=metrics_data[0]),
                cells=dict(values=[row[i] for i in range(3)] for row in metrics_data[1:])
            ),
            row=2, col=3
        )
        
        # 7. Alert Status (Indicator)
        critical_alerts = len([a for a in self.alerts if a['severity'] == 'CRITICAL'])
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=critical_alerts,
                title={'text': "Critical Alerts"},
                domain={'row': 2, 'column': 0},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "red" if critical_alerts > 0 else "green"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightgreen"},
                        {'range': [2, 5], 'color': "yellow"},
                        {'range': [5, 10], 'color': "red"}
                    ]
                }
            ),
            row=3, col=1
        )
        
        # 8. Factor Exposures (Bar chart)
        factors = ['Market Beta', 'Size', 'Value', 'Momentum', 'Quality', 'Volatility']
        exposures = [
            self.risk_metrics.get('market_beta', 1.0),
            self.risk_metrics.get('size_exposure', 0),
            self.risk_metrics.get('value_exposure', 0),
            self.risk_metrics.get('momentum_exposure', 0),
            self.risk_metrics.get('quality_exposure', 0),
            self.risk_metrics.get('volatility_exposure', 0)
        ]
        
        fig.add_trace(
            go.Bar(
                x=factors,
                y=exposures,
                name='Factor Exposures',
                marker_color='purple'
            ),
            row=3, col=2
        )
        
        # 9. Historical VaR (Line chart)
        # Calculate rolling VaR
        if len(self.positions) > 0 and portfolio_symbols and not returns.empty:
            rolling_var = returns.dot(weights).rolling(63).apply(
                lambda x: np.percentile(x, 5)
            )
            
            fig.add_trace(
                go.Scatter(
                    x=rolling_var.index,
                    y=rolling_var.values,
                    mode='lines',
                    name='63-day Rolling VaR',
                    line=dict(color='orange')
                ),
                row=3, col=3
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1600,
            title_text="Real-Time Risk Dashboard",
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Dashboard saved to {save_path}")
        
        return fig


class RegulatoryRiskAssessor:
    """
    Regulatory risk assessment for compliance with requirements.
    
    Supports:
    - Basel III
    - Dodd-Frank
    - MiFID II
    - EMIR
    - CCAR/DFAST
    """
    
    def __init__(self, portfolio_data: Dict, entity_type: str = 'bank'):
        """
        Initialize regulatory risk assessor.
        
        Parameters:
        -----------
        portfolio_data : Dict
            Portfolio data including positions, risk metrics, etc.
        entity_type : str
            'bank', 'broker_dealer', 'asset_manager', 'insurance'
        """
        self.portfolio_data = portfolio_data
        self.entity_type = entity_type
        
        # Regulatory frameworks based on entity type
        self.regulatory_frameworks = self._get_applicable_frameworks()
        
    def _get_applicable_frameworks(self) -> List[str]:
        """Get applicable regulatory frameworks."""
        frameworks = {
            'bank': ['Basel III', 'Dodd-Frank', 'CCAR', 'DFAST', 'Volcker Rule'],
            'broker_dealer': ['SEC Net Capital', 'FINRA', 'Dodd-Frank', 'MiFID II'],
            'asset_manager': ['SEC Form PF', 'AIFMD', 'MiFID II', 'SFTR'],
            'insurance': ['Solvency II', 'NAIC', 'ORSA']
        }
        
        return frameworks.get(self.entity_type, ['General Compliance'])
    
    def assess_basel_iii(self) -> Dict:
        """Assess compliance with Basel III requirements."""
        # Basel III key requirements
        requirements = {
            'common_equity_tier1_ratio': {'minimum': 0.045, 'capital_conservation': 0.07},
            'tier1_capital_ratio': {'minimum': 0.06},
            'total_capital_ratio': {'minimum': 0.08},
            'leverage_ratio': {'minimum': 0.03},
            'liquidity_coverage_ratio': {'minimum': 1.0},
            'net_stable_funding_ratio': {'minimum': 1.0}
        }
        
        # Calculate or retrieve metrics
        metrics = {}
        for req in requirements:
            # Placeholder - would calculate actual metrics
            metrics[req] = self._calculate_basel_metric(req)
        
        # Check compliance
        compliance = {}
        for req, thresholds in requirements.items():
            value = metrics.get(req, 0)
            minimum = thresholds['minimum']
            
            compliance[req] = {
                'value': value,
                'minimum': minimum,
                'compliant': value >= minimum,
                'buffer': value - minimum
            }
            
            if 'capital_conservation' in thresholds:
                conservation = thresholds['capital_conservation']
                compliance[req]['capital_conservation_buffer'] = conservation
                compliance[req]['above_conservation'] = value >= conservation
        
        return {
            'framework': 'Basel III',
            'metrics': metrics,
            'compliance': compliance,
            'overall_compliant': all(c['compliant'] for c in compliance.values()),
            'key_risks': self._identify_basel_risks(compliance)
        }
    
    def _calculate_basel_metric(self, metric: str) -> float:
        """Calculate Basel III metric (simplified)."""
        # Placeholder calculations
        calculations = {
            'common_equity_tier1_ratio': 0.12,  # 12%
            'tier1_capital_ratio': 0.14,  # 14%
            'total_capital_ratio': 0.16,  # 16%
            'leverage_ratio': 0.05,  # 5%
            'liquidity_coverage_ratio': 1.2,  # 120%
            'net_stable_funding_ratio': 1.1  # 110%
        }
        
        return calculations.get(metric, 0.0)
    
    def _identify_basel_risks(self, compliance: Dict) -> List[str]:
        """Identify Basel III compliance risks."""
        risks = []
        
        for req, data in compliance.items():
            if not data['compliant']:
                risks.append(f"{req.replace('_', ' ').title()} below minimum requirement")
            elif data.get('buffer', 0) < 0.01:  # Less than 1% buffer
                risks.append(f"{req.replace('_', ' ').title()} buffer thin")
        
        return risks if risks else ["No immediate compliance risks identified"]
    
    def assess_dodd_frank(self) -> Dict:
        """Assess compliance with Dodd-Frank requirements."""
        # Key Dodd-Frank requirements
        requirements = {
            'volcker_rule_compliance': True,
            'swap_data_reporting': True,
            'clearing_requirement': True,
            'margin_requirements': True,
            'stress_testing': True,
            'living_will': True
        }
        
        # Check compliance (simplified)
        compliance_status = {}
        for req in requirements:
            # Placeholder - would check actual compliance
            compliant = np.random.choice([True, False], p=[0.9, 0.1])
            compliance_status[req] = {
                'required': requirements[req],
                'compliant': compliant,
                'last_review': (datetime.now() - timedelta(days=np.random.randint(30, 180))).strftime('%Y-%m-%d')
            }
        
        return {
            'framework': 'Dodd-Frank',
            'requirements': requirements,
            'compliance_status': compliance_status,
            'overall_compliant': all(status['compliant'] for status in compliance_status.values()),
            'next_deadline': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        }
    
    def assess_ccar_dfast(self) -> Dict:
        """Assess CCAR/DFAST stress testing requirements."""
        scenarios = {
            'severely_adverse': {
                'equity_drop': -0.50,
                'unemployment_peak': 0.10,
                'gdp_drop': -0.085,
                'house_price_drop': -0.35
            },
            'adverse': {
                'equity_drop': -0.20,
                'unemployment_peak': 0.075,
                'gdp_drop': -0.025,
                'house_price_drop': -0.15
            },
            'baseline': {
                'equity_growth': 0.04,
                'unemployment': 0.04,
                'gdp_growth': 0.025,
                'house_price_growth': 0.03
            }
        }
        
        # Run stress tests (simplified)
        results = {}
        for scenario, params in scenarios.items():
            # Calculate portfolio impact
            impact = self._calculate_stress_impact(params)
            
            results[scenario] = {
                'scenario_parameters': params,
                'portfolio_impact': impact,
                'capital_adequacy': impact > -0.05,  > 5% loss
                'regulatory_minimum': -0.025 if scenario == 'severely_adverse' else -0.01
            }
        
        return {
            'framework': 'CCAR/DFAST',
            'scenarios': scenarios,
            'results': results,
            'overall_compliant': all(r['capital_adequacy'] for r in results.values()),
            'submission_deadline': 'April 5, 2024'  # Example
        }
    
    def _calculate_stress_impact(self, scenario_params: Dict) -> float:
        """Calculate portfolio impact under stress scenario."""
        # Simplified impact calculation
        base_impact = -0.02  # Base 2% loss
        
        # Adjust for scenario severity
        if 'equity_drop' in scenario_params:
            severity_multiplier = abs(scenario_params['equity_drop']) / 0.5  # Relative to 50% drop
            impact = base_impact * severity_multiplier
        else:
            impact = base_impact * 0.5  # Baseline scenario
        
        return impact
    
    def generate_regulatory_report(self) -> str:
        """Generate comprehensive regulatory compliance report."""
        report_lines = []
        
        report_lines.append("# REGULATORY COMPLIANCE REPORT")
        report_lines.append(f"Entity Type: {self.entity_type}")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        report_lines.append("## Applicable Regulatory Frameworks")
        report_lines.append("")
        for framework in self.regulatory_frameworks:
            report_lines.append(f"- {framework}")
        report_lines.append("")
        
        # Basel III Assessment
        if 'Basel III' in self.regulatory_frameworks:
            report_lines.append("## Basel III Compliance")
            report_lines.append("")
            
            basel_results = self.assess_basel_iii()
            
            for metric, data in basel_results['compliance'].items():
                status = "✅" if data['compliant'] else "❌"
                report_lines.append(f"{status} **{metric.replace('_', ' ').title()}**: "
                                  f"{data['value']:.2%} (Minimum: {data['minimum']:.2%})")
            
            report_lines.append("")
            report_lines.append(f"**Overall Compliance**: {'COMPLIANT' if basel_results['overall_compliant'] else 'NON-COMPLIANT'}")
            report_lines.append("")
            
            report_lines.append("**Key Risks:**")
            for risk in basel_results['key_risks']:
                report_lines.append(f"- {risk}")
            report_lines.append("")
        
        # Dodd-Frank Assessment
        if 'Dodd-Frank' in self.regulatory_frameworks:
            report_lines.append("## Dodd-Frank Compliance")
            report_lines.append("")
            
            dodd_frank_results = self.assess_dodd_frank()
            
            for req, data in dodd_frank_results['compliance_status'].items():
                status = "✅" if data['compliant'] else "❌"
                report_lines.append(f"{status} **{req.replace('_', ' ').title()}**: "
                                  f"Last reviewed: {data['last_review']}")
            
            report_lines.append("")
            report_lines.append(f"**Overall Compliance**: {'COMPLIANT' if dodd_frank_results['overall_compliant'] else 'NON-COMPLIANT'}")
            report_lines.append(f"**Next Submission Deadline**: {dodd_frank_results['next_deadline']}")
            report_lines.append("")
        
        # CCAR/DFAST Assessment
        if 'CCAR' in self.regulatory_frameworks or 'DFAST' in self.regulatory_frameworks:
            report_lines.append("## CCAR/DFAST Stress Testing")
            report_lines.append("")
            
            ccar_results = self.assess_ccar_dfast()
            
            for scenario, data in ccar_results['results'].items():
                status = "✅" if data['capital_adequacy'] else "❌"
                report_lines.append(f"### {scenario.replace('_', ' ').title()} Scenario")
                report_lines.append(f"{status} **Portfolio Impact**: {data['portfolio_impact']:.2%}")
                report_lines.append(f"**Capital Adequacy**: {'Adequate' if data['capital_adequacy'] else 'Inadequate'}")
                report_lines.append("")
            
            report_lines.append(f"**Overall Compliance**: {'COMPLIANT' if ccar_results['overall_compliant'] else 'NON-COMPLIANT'}")
            report_lines.append(f"**Submission Deadline**: {ccar_results['submission_deadline']}")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Compliance Recommendations")
        report_lines.append("")
        
        recommendations = self._generate_regulatory_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*This report is for compliance assessment purposes only.*")
        report_lines.append("*Consult legal counsel for definitive regulatory advice.*")
        
        return "\n".join(report_lines)
    
    def _generate_regulatory_recommendations(self) -> List[str]:
        """Generate regulatory compliance recommendations."""
        recommendations = []
        
        # Basel III recommendations
        if 'Basel III' in self.regulatory_frameworks:
            basel_results = self.assess_basel_iii()
            for metric, data in basel_results['compliance'].items():
                if not data['compliant']:
                    recommendations.append(
                        f"Increase {metric.replace('_', ' ')} to meet Basel III minimum of {data['minimum']:.2%}"
                    )
                elif data.get('buffer', 0) < 0.01:
                    recommendations.append(
                        f"Build additional buffer for {metric.replace('_', ' ')}"
                    )
        
        # Dodd-Frank recommendations
        if 'Dodd-Frank' in self.regulatory_frameworks:
            dodd_frank_results = self.assess_dodd_frank()
            non_compliant = [req for req, data in dodd_frank_results['compliance_status'].items() 
                           if not data['compliant']]
            
            if non_compliant:
                recommendations.append(
                    f"Address non-compliance with Dodd-Frank requirements: {', '.join(non_compliant)}"
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Maintain current compliance monitoring and reporting procedures")
            recommendations.append("Schedule quarterly compliance reviews")
            recommendations.append("Stay updated on regulatory changes and interpretations")
        
        return recommendations


def main():
    """Demonstration of risk assessment tools."""
    print("Day 82: Risk Assessment Tools & Exposure Management")
    print("=" * 80)
    
    # Create sample positions
    positions = [
        Position('AAPL', 100, 180.0, 'Technology', 'US', 'equity'),
        Position('MSFT', 50, 330.0, 'Technology', 'US', 'equity'),
        Position('JPM', 200, 145.0, 'Financials', 'US', 'equity'),
        Position('XOM', 150, 105.0, 'Energy', 'US', 'equity'),
        Position('TLT', 1000, 95.0, 'Government', 'US', 'bond'),
        Position('GLD', 50, 1850.0, 'Precious Metals', 'US', 'commodity')
    ]
    
    # Generate sample market data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    symbols = ['AAPL', 'MSFT', 'JPM', 'XOM', 'TLT', 'GLD', 'SPY']
    
    # Generate correlated returns
    n_assets = len(symbols)
    means = np.random.uniform(0.0001, 0.0003, n_assets)
    cov = np.random.uniform(0.0001, 0.0002, (n_assets, n_assets))
    np.fill_diagonal(cov, np.random.uniform(0.0002, 0.0004, n_assets))
    cov = (cov + cov.T) / 2
    
    returns = np.random.multivariate_normal(means, cov, len(dates))
    market_data = pd.DataFrame(returns, index=dates, columns=symbols)
    
    # Add volume data (simplified)
    for symbol in symbols:
        market_data[f'{symbol}_volume'] = np.random.lognormal(14, 1, len(dates))
    
    print("\nInitializing Real-Time Risk Dashboard...")
    dashboard = RealTimeRiskDashboard(positions, market_data)
    
    print("✅ Dashboard initialized successfully")
    
    # Get risk summary
    summary = dashboard.get_risk_summary()
    
    print("\n📊 RISK SUMMARY")
    print("-" * 40)
    
    print(f"\nPortfolio Summary:")
    print(f"  Total Value: ${summary['portfolio_summary']['total_value']:,.2f}")
    print(f"  Number of Positions: {summary['portfolio_summary']['num_positions']}")
    print(f"  Diversification Score: {summary['portfolio_summary']['diversification_score']:.1f}/100")
    
    print(f"\nConcentration Risk:")
    print(f"  Max Position: {summary['concentration_risk']['max_position']:.2%}")
    print(f"  Top 3 Concentration: {summary['concentration_risk']['top_3_concentration']:.2%}")
    print(f"  Herfindahl Index: {summary['concentration_risk']['herfindahl_index']:.4f}")
    
    print(f"\nMarket Risk:")
    print(f"  VaR (95%): {summary['market_risk']['var_95']:.2%}")
    print(f"  Expected Shortfall (95%): {summary['market_risk']['expected_shortfall_95']:.2%}")
    print(f"  Market Beta: {summary['market_risk']['market_beta']:.2f}")
    
    print(f"\nLiquidity Risk:")
    print(f"  Liquidity Score: {summary['liquidity_risk']['liquidity_score']:.1f}/100")
    print(f"  Avg Days to Liquidate: {summary['liquidity_risk']['avg_days_to_liquidate']:.1f}")
    
    print(f"\nAlerts:")
    print(f"  Critical: {summary['alerts']['critical']}")
    print(f"  Warning: {summary['alerts']['warning']}")
    print(f"  Total: {summary['alerts']['total']}")
    
    # Generate and save reports
    print("\n📝 Generating reports...")
    
    # Risk dashboard report
    risk_report = dashboard.generate_report()
    with open('risk_dashboard_report.md', 'w') as f:
        f.write(risk_report)
    print("✅ Risk dashboard report saved to 'risk_dashboard_report.md'")
    
    # Regulatory compliance report
    portfolio_data = {
        'positions': positions,
        'risk_metrics': summary,
        'market_data': market_data
    }
    
    regulator = RegulatoryRiskAssessor(portfolio_data, entity_type='bank')
    regulatory_report = regulator.generate_regulatory_report()
    
    with open('regulatory_compliance_report.md', 'w') as f:
        f.write(regulatory_report)
    print("✅ Regulatory compliance report saved to 'regulatory_compliance_report.md'")
    
    # Create visualization if Plotly is available
    if PLOTLY_AVAILABLE:
        print("\n📈 Creating interactive dashboard...")
        fig = dashboard.visualize_dashboard(save_path='risk_dashboard.html')
        print("✅ Interactive dashboard saved to 'risk_dashboard.html'")
    
    # Demonstrate position update
    print("\n🔄 Simulating position update...")
    
    # Add a new position
    new_positions = positions + [
        Position('AMZN', 30, 150.0, 'Consumer', 'US', 'equity')
    ]
    
    dashboard.update_positions(new_positions)
    
    print("✅ Positions updated")
    print(f"  New portfolio value: ${dashboard.risk_metrics['portfolio_value']:,.2f}")
    print(f"  New number of positions: {dashboard.risk_metrics['num_positions']}")
    
    # Check for alerts
    if dashboard.alerts:
        print(f"\n⚠️  Active Alerts:")
        for alert in dashboard.alerts:
            print(f"  [{alert['severity']}] {alert['message']}")
    else:
        print("\n✅ No active alerts")
    
    print("\n" + "=" * 80)
    print("Risk Assessment Tools Demonstration Complete")
    print("=" * 80)
    
    # Display key takeaways
    print("\n🔑 KEY TAKEAWAYS:")
    print("1. Real-time risk monitoring enables proactive risk management")
    print("2. Concentration metrics help identify diversification gaps")
    print("3. VaR and Expected Shortfall quantify potential losses")
    print("4. Liquidity assessment ensures exit strategy viability")
    print("5. Regulatory compliance requires ongoing monitoring")
    print("6. Automated alerts enable timely risk mitigation")


if __name__ == "__main__":
    main()