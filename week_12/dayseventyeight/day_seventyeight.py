
"""
Day 78: Performance Metrics & Analytics
Advanced performance analysis with comprehensive metrics and factor attribution
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

# Optional imports with fallbacks
try:
    import empyrical as ep
    EMPYRICIAL_AVAILABLE = True
except ImportError:
    EMPYRICIAL_AVAILABLE = False
    print("Warning: empyrical not available, using custom implementations")

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available, using matplotlib")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


class AdvancedPerformanceAnalyzer:
    """
    Comprehensive performance analyzer for trading strategies.
    
    Calculates 50+ performance metrics including risk-adjusted returns,
    drawdown analysis, factor attribution, and statistical significance tests.
    
    Attributes:
    -----------
    returns : pd.Series
        Strategy returns (daily frequency)
    benchmark_returns : pd.Series, optional
        Benchmark returns for relative performance analysis
    risk_free_rate : float
        Annual risk-free rate for risk-adjusted metrics
    """
    
    def __init__(self, returns: pd.Series, 
                 benchmark_returns: Optional[pd.Series] = None,
                 risk_free_rate: float = 0.02):
        """
        Initialize performance analyzer.
        
        Parameters:
        -----------
        returns : pd.Series
            Strategy returns with datetime index
        benchmark_returns : pd.Series, optional
            Benchmark returns for comparison
        risk_free_rate : float
            Annual risk-free rate (default: 0.02 for 2%)
        """
        self.returns = self._validate_and_clean_returns(returns)
        self.benchmark_returns = self._validate_and_clean_returns(benchmark_returns) if benchmark_returns is not None else None
        self.risk_free_rate = risk_free_rate
        
        # Align dates if benchmark provided
        if self.benchmark_returns is not None:
            self._align_series()
        
        # Cache for computed metrics
        self._metrics_cache = {}
        self._drawdown_cache = {}
    
    def _validate_and_clean_returns(self, returns: pd.Series) -> pd.Series:
        """Validate and clean returns series."""
        if not isinstance(returns, pd.Series):
            raise TypeError("Returns must be a pandas Series")
        
        if returns.empty:
            raise ValueError("Returns series cannot be empty")
        
        # Ensure datetime index
        if not isinstance(returns.index, pd.DatetimeIndex):
            try:
                returns.index = pd.to_datetime(returns.index)
            except:
                raise ValueError("Returns index must be convertible to datetime")
        
        # Remove NaN values
        returns_clean = returns.dropna()
        
        if len(returns_clean) < 30:
            warnings.warn(f"Only {len(returns_clean)} observations available, results may be unreliable")
        
        return returns_clean
    
    def _align_series(self):
        """Align strategy and benchmark returns dates."""
        common_idx = self.returns.index.intersection(self.benchmark_returns.index)
        if len(common_idx) == 0:
            warnings.warn("No overlapping dates between strategy and benchmark")
            self.benchmark_returns = None
        else:
            self.returns = self.returns.loc[common_idx]
            self.benchmark_returns = self.benchmark_returns.loc[common_idx]
    
    def calculate_basic_metrics(self) -> Dict[str, float]:
        """
        Calculate basic performance metrics.
        
        Returns:
        --------
        dict: Dictionary of basic performance metrics
        """
        metrics = {}
        
        # Return metrics
        metrics['total_return'] = self._calculate_total_return()
        metrics['annualized_return'] = self._calculate_annualized_return()
        metrics['annualized_volatility'] = self._calculate_annualized_volatility()
        
        # Risk-adjusted metrics
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio()
        metrics['sortino_ratio'] = self._calculate_sortino_ratio()
        metrics['calmar_ratio'] = self._calculate_calmar_ratio()
        
        # Drawdown metrics
        drawdown_info = self._calculate_max_drawdown()
        metrics['max_drawdown'] = drawdown_info['drawdown']
        metrics['max_drawdown_duration'] = drawdown_info['duration']
        metrics['max_drawdown_start'] = drawdown_info['start']
        metrics['max_drawdown_end'] = drawdown_info['end']
        
        # Win/loss metrics
        metrics['win_rate'] = self._calculate_win_rate()
        metrics['profit_factor'] = self._calculate_profit_factor()
        metrics['gain_loss_ratio'] = self._calculate_gain_loss_ratio()
        
        # Skewness and kurtosis
        metrics['skewness'] = self.returns.skew()
        metrics['kurtosis'] = self.returns.kurtosis()
        
        self._metrics_cache['basic'] = metrics
        return metrics
    
    def calculate_advanced_metrics(self) -> Dict[str, float]:
        """
        Calculate advanced performance metrics.
        
        Returns:
        --------
        dict: Dictionary of advanced performance metrics
        """
        metrics = {}
        
        # Advanced risk-adjusted metrics
        metrics['omega_ratio'] = self._calculate_omega_ratio()
        metrics['kelly_criterion'] = self._calculate_kelly_criterion()
        metrics['tail_ratio'] = self._calculate_tail_ratio()
        
        # Drawdown-based metrics
        metrics['ulcer_index'] = self._calculate_ulcer_index()
        metrics['pain_index'] = self._calculate_pain_index()
        metrics['martin_ratio'] = self._calculate_martin_ratio()
        
        # Risk metrics
        metrics['var_95'] = self._calculate_value_at_risk(0.95)
        metrics['cvar_95'] = self._calculate_conditional_var(0.95)
        metrics['var_99'] = self._calculate_value_at_risk(0.99)
        metrics['cvar_99'] = self._calculate_conditional_var(0.99)
        
        # Time-based metrics
        metrics['time_under_water'] = self._calculate_time_under_water()
        metrics['recovery_factor'] = self._calculate_recovery_factor()
        
        # Benchmark-relative metrics
        if self.benchmark_returns is not None:
            metrics['alpha'] = self._calculate_alpha()
            metrics['beta'] = self._calculate_beta()
            metrics['information_ratio'] = self._calculate_information_ratio()
            metrics['tracking_error'] = self._calculate_tracking_error()
            metrics['up_capture'] = self._calculate_up_capture_ratio()
            metrics['down_capture'] = self._calculate_down_capture_ratio()
        
        # Statistical significance
        metrics['t_statistic'] = self._calculate_t_statistic()
        metrics['p_value'] = self._calculate_p_value()
        
        self._metrics_cache['advanced'] = metrics
        return metrics
    
    # Core metric calculation methods
    def _calculate_total_return(self) -> float:
        """Calculate cumulative total return."""
        return (1 + self.returns).prod() - 1
    
    def _calculate_annualized_return(self) -> float:
        """Calculate annualized return."""
        days = (self.returns.index[-1] - self.returns.index[0]).days
        if days == 0:
            return 0.0
        years = days / 365.25
        total_return = self._calculate_total_return()
        return (1 + total_return) ** (1 / years) - 1
    
    def _calculate_annualized_volatility(self) -> float:
        """Calculate annualized volatility."""
        return self.returns.std() * np.sqrt(252)
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate annualized Sharpe ratio."""
        excess_returns = self.returns - (self.risk_free_rate / 252)
        if excess_returns.std() == 0:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def _calculate_sortino_ratio(self, target_return: float = 0) -> float:
        """Calculate Sortino ratio using downside deviation."""
        excess_returns = self.returns - (self.risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < target_return]
        if len(downside_returns) == 0:
            return float('inf')
        downside_dev = downside_returns.std() * np.sqrt(252)
        if downside_dev == 0:
            return 0.0
        return (self._calculate_annualized_return() - self.risk_free_rate) / downside_dev
    
    def _calculate_max_drawdown(self) -> Dict:
        """Calculate maximum drawdown with detailed information."""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown_series = (cumulative - running_max) / running_max
        
        max_dd = drawdown_series.min()
        max_dd_idx = drawdown_series.idxmin()
        
        # Find peak before drawdown
        peak_idx = cumulative.loc[:max_dd_idx].idxmax()
        
        # Find recovery
        post_drawdown = cumulative.loc[max_dd_idx:]
        recovery_idx = post_drawdown[post_drawdown >= cumulative.loc[peak_idx]].index
        
        if len(recovery_idx) > 0:
            recovery_date = recovery_idx[0]
            duration = (recovery_date - peak_idx).days
        else:
            recovery_date = None
            duration = (self.returns.index[-1] - peak_idx).days
        
        return {
            'drawdown': max_dd,
            'start': peak_idx,
            'end': max_dd_idx,
            'recovery': recovery_date,
            'duration': duration
        }
    
    def _calculate_omega_ratio(self, threshold: float = 0) -> float:
        """Calculate Omega ratio."""
        returns_array = self.returns.values
        gains = returns_array[returns_array > threshold].sum()
        losses = abs(returns_array[returns_array <= threshold].sum())
        return gains / losses if losses != 0 else float('inf')
    
    def _calculate_ulcer_index(self) -> float:
        """Calculate Ulcer Index."""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = ((cumulative - running_max) / running_max) * 100
        return np.sqrt((drawdown ** 2).mean())
    
    def _calculate_value_at_risk(self, confidence: float = 0.95) -> float:
        """Calculate Value at Risk."""
        return np.percentile(self.returns, (1 - confidence) * 100)
    
    def _calculate_conditional_var(self, confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        var = self._calculate_value_at_risk(confidence)
        returns_below_var = self.returns[self.returns <= var]
        if len(returns_below_var) == 0:
            return var
        return returns_below_var.mean()
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate (percentage of positive returns)."""
        return (self.returns > 0).mean()
    
    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profits / gross losses)."""
        gross_profits = self.returns[self.returns > 0].sum()
        gross_losses = abs(self.returns[self.returns < 0].sum())
        return gross_profits / gross_losses if gross_losses != 0 else float('inf')
    
    def _calculate_gain_loss_ratio(self) -> float:
        """Calculate average gain to average loss ratio."""
        gains = self.returns[self.returns > 0]
        losses = self.returns[self.returns < 0]
        if len(losses) == 0:
            return float('inf')
        return gains.mean() / abs(losses.mean())
    
    def _calculate_kelly_criterion(self) -> float:
        """Calculate Kelly Criterion for optimal bet sizing."""
        win_rate = self._calculate_win_rate()
        avg_win = self.returns[self.returns > 0].mean()
        avg_loss = abs(self.returns[self.returns < 0].mean())
        
        if avg_loss == 0:
            return 0.0
        
        # Kelly formula: f* = p - q/b where b = avg_win/avg_loss
        b = avg_win / avg_loss
        return win_rate - (1 - win_rate) / b
    
    def _calculate_tail_ratio(self) -> float:
        """Calculate tail ratio (right tail vs left tail)."""
        right_tail = np.percentile(self.returns, 95)
        left_tail = abs(np.percentile(self.returns, 5))
        return right_tail / left_tail if left_tail != 0 else float('inf')
    
    def _calculate_pain_index(self) -> float:
        """Calculate Pain Index (average drawdown)."""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.mean())
    
    def _calculate_martin_ratio(self) -> float:
        """Calculate Martin ratio (Ulcer Performance Index)."""
        ulcer_index = self._calculate_ulcer_index()
        annual_return = self._calculate_annualized_return()
        return annual_return / ulcer_index if ulcer_index != 0 else 0.0
    
    def _calculate_time_under_water(self) -> float:
        """Calculate average time spent in drawdown (days)."""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        underwater = cumulative < running_max
        
        # Find continuous underwater periods
        underwater_periods = []
        in_period = False
        period_start = None
        
        for date, is_underwater in underwater.items():
            if is_underwater and not in_period:
                period_start = date
                in_period = True
            elif not is_underwater and in_period:
                period_end = date
                duration = (period_end - period_start).days
                underwater_periods.append(duration)
                in_period = False
        
        # Handle case where still underwater at end
        if in_period and period_start:
            duration = (self.returns.index[-1] - period_start).days
            underwater_periods.append(duration)
        
        return np.mean(underwater_periods) if underwater_periods else 0.0
    
    def _calculate_recovery_factor(self) -> float:
        """Calculate recovery factor (total return / max drawdown)."""
        total_return = self._calculate_total_return()
        max_dd = abs(self._calculate_max_drawdown()['drawdown'])
        return total_return / max_dd if max_dd != 0 else float('inf')
    
    # Benchmark-relative methods
    def _calculate_alpha(self) -> float:
        """Calculate Jensen's alpha."""
        if self.benchmark_returns is None:
            return None
        
        excess_strategy = self.returns - (self.risk_free_rate / 252)
        excess_benchmark = self.benchmark_returns - (self.risk_free_rate / 252)
        
        beta = self._calculate_beta()
        alpha = excess_strategy.mean() - beta * excess_benchmark.mean()
        return alpha * 252  # Annualize
    
    def _calculate_beta(self) -> float:
        """Calculate beta relative to benchmark."""
        if self.benchmark_returns is None:
            return None
        
        covariance = np.cov(self.returns, self.benchmark_returns)[0, 1]
        benchmark_variance = np.var(self.benchmark_returns)
        return covariance / benchmark_variance if benchmark_variance != 0 else 0.0
    
    def _calculate_information_ratio(self) -> float:
        """Calculate Information ratio."""
        if self.benchmark_returns is None:
            return None
        
        active_returns = self.returns - self.benchmark_returns
        if active_returns.std() == 0:
            return 0.0
        return np.sqrt(252) * active_returns.mean() / active_returns.std()
    
    def _calculate_tracking_error(self) -> float:
        """Calculate tracking error."""
        if self.benchmark_returns is None:
            return None
        
        active_returns = self.returns - self.benchmark_returns
        return active_returns.std() * np.sqrt(252)
    
    def _calculate_up_capture_ratio(self) -> float:
        """Calculate up-capture ratio."""
        if self.benchmark_returns is None:
            return None
        
        up_market = self.benchmark_returns > 0
        if up_market.sum() == 0:
            return 0.0
        
        strategy_up_returns = self.returns[up_market]
        benchmark_up_returns = self.benchmark_returns[up_market]
        
        strategy_up_cum = (1 + strategy_up_returns).prod() - 1
        benchmark_up_cum = (1 + benchmark_up_returns).prod() - 1
        
        return strategy_up_cum / benchmark_up_cum if benchmark_up_cum != 0 else 0.0
    
    def _calculate_down_capture_ratio(self) -> float:
        """Calculate down-capture ratio."""
        if self.benchmark_returns is None:
            return None
        
        down_market = self.benchmark_returns < 0
        if down_market.sum() == 0:
            return 0.0
        
        strategy_down_returns = self.returns[down_market]
        benchmark_down_returns = self.benchmark_returns[down_market]
        
        strategy_down_cum = (1 + strategy_down_returns).prod() - 1
        benchmark_down_cum = (1 + benchmark_down_returns).prod() - 1
        
        return strategy_down_cum / benchmark_down_cum if benchmark_down_cum != 0 else 0.0
    
    def _calculate_t_statistic(self) -> float:
        """Calculate t-statistic for mean return."""
        n = len(self.returns)
        if n < 2:
            return 0.0
        return np.sqrt(n) * self.returns.mean() / self.returns.std()
    
    def _calculate_p_value(self) -> float:
        """Calculate p-value for mean return being zero."""
        if not SCIPY_AVAILABLE or len(self.returns) < 2:
            return None
        
        t_stat = self._calculate_t_statistic()
        df = len(self.returns) - 1
        return 2 * (1 - stats.t.cdf(abs(t_stat), df))
    
    def generate_performance_report(self) -> Dict:
        """
        Generate comprehensive performance report.
        
        Returns:
        --------
        dict: Complete performance report with metrics and assessment
        """
        basic_metrics = self.calculate_basic_metrics()
        advanced_metrics = self.calculate_advanced_metrics()
        
        report = {
            'basic_metrics': basic_metrics,
            'advanced_metrics': advanced_metrics,
            'overall_assessment': self._assess_performance(basic_metrics, advanced_metrics),
            'data_summary': {
                'start_date': self.returns.index[0],
                'end_date': self.returns.index[-1],
                'n_observations': len(self.returns),
                'data_frequency': self._infer_frequency()
            }
        }
        
        return report
    
    def _assess_performance(self, basic_metrics: Dict, advanced_metrics: Dict) -> str:
        """Generate overall performance assessment."""
        sharpe = basic_metrics.get('sharpe_ratio', 0)
        max_dd = basic_metrics.get('max_drawdown', 0)
        win_rate = basic_metrics.get('win_rate', 0)
        
        assessments = []
        
        if sharpe > 1.5:
            assessments.append("Excellent risk-adjusted returns")
        elif sharpe > 0.8:
            assessments.append("Good risk-adjusted returns")
        elif sharpe > 0:
            assessments.append("Modest risk-adjusted returns")
        else:
            assessments.append("Poor risk-adjusted returns")
        
        if max_dd > -0.15:
            assessments.append("Controlled maximum drawdown")
        elif max_dd > -0.25:
            assessments.append("Moderate drawdown risk")
        else:
            assessments.append("High drawdown risk")
        
        if win_rate > 0.55:
            assessments.append("High win rate strategy")
        elif win_rate > 0.45:
            assessments.append("Balanced win/loss profile")
        else:
            assessments.append("Low win rate, reliant on large gains")
        
        return "; ".join(assessments)
    
    def _infer_frequency(self) -> str:
        """Infer data frequency from index."""
        if len(self.returns) < 2:
            return "Unknown"
        
        time_diffs = np.diff(self.returns.index).astype('timedelta64[D]').astype(int)
        avg_diff = np.mean(time_diffs)
        
        if avg_diff == 1:
            return "Daily"
        elif 5 <= avg_diff <= 7:
            return "Weekly"
        elif avg_diff >= 28:
            return "Monthly"
        else:
            return f"{avg_diff:.0f}-day interval"
    
    def plot_performance_summary(self, save_path: Optional[str] = None):
        """
        Create comprehensive performance visualization.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the visualization
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.gridspec as gridspec
        except ImportError:
            print("Matplotlib not available for plotting")
            return
        
        fig = plt.figure(figsize=(16, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Cumulative returns
        ax1 = fig.add_subplot(gs[0, :2])
        cumulative_returns = (1 + self.returns).cumprod()
        ax1.plot(cumulative_returns.index, cumulative_returns.values, linewidth=2)
        if self.benchmark_returns is not None:
            benchmark_cumulative = (1 + self.benchmark_returns).cumprod()
            ax1.plot(benchmark_cumulative.index, benchmark_cumulative.values, 
                    alpha=0.7, linewidth=1.5)
            ax1.legend(['Strategy', 'Benchmark'], loc='upper left')
        ax1.set_title('Cumulative Returns', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Growth of $1')
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown
        ax2 = fig.add_subplot(gs[0, 2])
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        ax2.fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3)
        ax2.plot(drawdown.index, drawdown.values, color='red', alpha=0.7)
        ax2.set_title('Drawdown Over Time', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Drawdown')
        ax2.grid(True, alpha=0.3)
        
        # 3. Monthly returns heatmap
        ax3 = fig.add_subplot(gs[1, 0])
        returns_df = pd.DataFrame({'returns': self.returns})
        returns_df['year'] = returns_df.index.year
        returns_df['month'] = returns_df.index.month
        monthly_returns = returns_df.groupby(['year', 'month'])['returns'].apply(
            lambda x: (1 + x).prod() - 1
        )
        monthly_returns = monthly_returns.unstack(level='month')
        
        # Simple bar plot for monthly returns
        monthly_mean = monthly_returns.mean(axis=0)
        ax3.bar(range(1, 13), monthly_mean.values)
        ax3.set_title('Average Monthly Returns', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Average Return')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Returns distribution
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.hist(self.returns, bins=50, alpha=0.7, density=True, 
                color='steelblue', edgecolor='black')
        
        if SCIPY_AVAILABLE:
            # Add normal distribution for comparison
            x = np.linspace(self.returns.min(), self.returns.max(), 100)
            normal_pdf = stats.norm.pdf(x, self.returns.mean(), self.returns.std())
            ax4.plot(x, normal_pdf, 'r-', linewidth=2, label='Normal Distribution')
            ax4.legend()
        
        ax4.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        ax4.set_title('Returns Distribution', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Daily Returns')
        ax4.set_ylabel('Density')
        ax4.grid(True, alpha=0.3)
        
        # 5. Rolling metrics
        ax5 = fig.add_subplot(gs[1, 2])
        rolling_window = min(252, len(self.returns) // 4)
        if rolling_window > 10:
            rolling_sharpe = (self.returns.rolling(window=rolling_window).mean() / 
                            self.returns.rolling(window=rolling_window).std() * np.sqrt(252))
            ax5.plot(rolling_sharpe.index, rolling_sharpe.values)
            ax5.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax5.set_title(f'Rolling {rolling_window}-Day Sharpe Ratio', 
                         fontsize=12, fontweight='bold')
            ax5.set_ylabel('Sharpe Ratio')
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'Insufficient data\nfor rolling analysis',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax5.transAxes)
            ax5.set_title('Rolling Analysis', fontsize=12, fontweight='bold')
        
        # 6. Risk-return scatter
        ax6 = fig.add_subplot(gs[2, 0])
        if self.benchmark_returns is not None:
            ax6.scatter([self._calculate_annualized_volatility()], 
                       [self._calculate_annualized_return()], 
                       color='blue', s=100, label='Strategy', zorder=5)
            ax6.scatter([self.benchmark_returns.std() * np.sqrt(252)], 
                       [self.benchmark_returns.mean() * 252], 
                       color='red', s=100, label='Benchmark', zorder=5)
            ax6.legend()
        else:
            ax6.scatter([self._calculate_annualized_volatility()], 
                       [self._calculate_annualized_return()], 
                       color='blue', s=100, zorder=5)
        
        ax6.set_title('Risk-Return Profile', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Annualized Volatility')
        ax6.set_ylabel('Annualized Return')
        ax6.grid(True, alpha=0.3)
        
        # 7. QQ plot (if scipy available)
        ax7 = fig.add_subplot(gs[2, 1])
        if SCIPY_AVAILABLE and len(self.returns) > 30:
            stats.probplot(self.returns, dist="norm", plot=ax7)
            ax7.set_title('Q-Q Plot vs Normal Distribution', 
                         fontsize=12, fontweight='bold')
            ax7.grid(True, alpha=0.3)
        else:
            ax7.text(0.5, 0.5, 'Q-Q plot requires\nsufficient data and scipy',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax7.transAxes)
            ax7.set_title('Q-Q Plot', fontsize=12, fontweight='bold')
        
        # 8. Key metrics summary
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        
        # Select key metrics to display
        key_metrics = {
            'Annual Return': f"{self._calculate_annualized_return():.2%}",
            'Annual Volatility': f"{self._calculate_annualized_volatility():.2%}",
            'Sharpe Ratio': f"{self._calculate_sharpe_ratio():.2f}",
            'Max Drawdown': f"{self._calculate_max_drawdown()['drawdown']:.2%}",
            'Win Rate': f"{self._calculate_win_rate():.2%}",
            'Profit Factor': f"{self._calculate_profit_factor():.2f}",
        }
        
        if self.benchmark_returns is not None:
            key_metrics['Alpha'] = f"{self._calculate_alpha():.2%}"
            key_metrics['Beta'] = f"{self._calculate_beta():.2f}"
            key_metrics['Info Ratio'] = f"{self._calculate_information_ratio():.2f}"
        
        # Display metrics as text
        text_content = "Key Performance Metrics:\n\n"
        for metric, value in key_metrics.items():
            text_content += f"{metric:20}: {value}\n"
        
        ax8.text(0.05, 0.95, text_content, transform=ax8.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('Comprehensive Performance Analysis', fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Performance summary saved to {save_path}")
        
        plt.tight_layout()
        return fig


class MultiFactorRiskModel:
    """
    Multi-factor risk model for return attribution and exposure analysis.
    
    Attributes:
    -----------
    factors : dict
        Dictionary of factor return series
    factor_loadings : dict
        Estimated factor exposures (betas)
    r_squared : float
        Model goodness of fit
    """
    
    def __init__(self):
        self.factors = {}
        self.factor_loadings = {}
        self.r_squared = None
        self.residuals = None
        self.model_summary = None
    
    def add_factor(self, name: str, returns: pd.Series):
        """
        Add a factor to the model.
        
        Parameters:
        -----------
        name : str
            Factor name
        returns : pd.Series
            Factor return series
        """
        self.factors[name] = returns.dropna()
    
    def analyze(self, strategy_returns: pd.Series, 
                factor_data: Optional[Dict[str, pd.Series]] = None) -> Dict:
        """
        Analyze strategy returns using multi-factor model.
        
        Parameters:
        -----------
        strategy_returns : pd.Series
            Strategy returns to analyze
        factor_data : dict, optional
            Dictionary of factor return series
        
        Returns:
        --------
        dict: Analysis results including factor contributions and statistics
        """
        if factor_data is not None:
            for name, returns in factor_data.items():
                self.add_factor(name, returns)
        
        if not self.factors:
            raise ValueError("No factors available for analysis")
        
        # Prepare data matrix
        aligned_data = self._align_data(strategy_returns)
        if aligned_data is None:
            raise ValueError("Insufficient overlapping data")
        
        strategy_aligned, factors_aligned = aligned_data
        
        # Fit regression model
        results = self._fit_regression(strategy_aligned, factors_aligned)
        
        # Calculate contributions
        contributions = self._calculate_contributions(strategy_aligned, factors_aligned, results)
        
        # Compile results
        analysis_results = {
            'factor_loadings': self.factor_loadings,
            'r_squared': self.r_squared,
            'residuals': self.residuals,
            'factor_contributions': contributions['factor_contributions'],
            'specific_return': contributions['specific_return'],
            'total_explained_variance': contributions['total_explained_variance'],
            'model_summary': self.model_summary
        }
        
        return analysis_results
    
    def _align_data(self, strategy_returns: pd.Series) -> Tuple:
        """Align strategy returns with factor returns."""
        # Start with strategy returns index
        common_index = strategy_returns.index
        
        # Intersect with all factor indices
        for factor_name, factor_returns in self.factors.items():
            common_index = common_index.intersection(factor_returns.index)
        
        if len(common_index) < 30:
            warnings.warn(f"Only {len(common_index)} overlapping observations")
            return None
        
        # Align all series
        strategy_aligned = strategy_returns.loc[common_index]
        factors_aligned = {}
        
        for factor_name, factor_returns in self.factors.items():
            factors_aligned[factor_name] = factor_returns.loc[common_index]
        
        return strategy_aligned, factors_aligned
    
    def _fit_regression(self, strategy_returns: pd.Series, 
                       factors: Dict[str, pd.Series]) -> Dict:
        """Fit linear regression model."""
        # Prepare design matrix
        X = pd.DataFrame(factors)
        
        if STATSMODELS_AVAILABLE:
            # Use statsmodels for detailed regression output
            X = sm.add_constant(X)  # Add intercept
            model = sm.OLS(strategy_returns, X).fit()
            
            self.factor_loadings = model.params.to_dict()
            self.r_squared = model.rsquared
            self.residuals = model.resid
            self.model_summary = str(model.summary())
            
            return {
                'params': model.params,
                'rsquared': model.rsquared,
                'residuals': model.resid,
                'summary': model.summary()
            }
        else:
            # Simple numpy implementation
            X_matrix = np.column_stack([np.ones(len(X)), X.values])
            y = strategy_returns.values
            
            # Ordinary least squares
            beta = np.linalg.lstsq(X_matrix, y, rcond=None)[0]
            
            # Store results
            self.factor_loadings = {'intercept': beta[0]}
            for i, factor_name in enumerate(factors.keys()):
                self.factor_loadings[factor_name] = beta[i + 1]
            
            # Calculate R-squared
            y_pred = X_matrix @ beta
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            self.r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            self.residuals = y - y_pred
            
            return {
                'params': beta,
                'rsquared': self.r_squared,
                'residuals': self.residuals
            }
    
    def _calculate_contributions(self, strategy_returns: pd.Series,
                                factors: Dict[str, pd.Series],
                                regression_results: Dict) -> Dict:
        """Calculate factor contributions to returns."""
        # Prepare factor matrix
        X = pd.DataFrame(factors)
        
        # Calculate factor contributions
        factor_contributions = {}
        total_factor_return = 0
        
        for factor_name in factors.keys():
            beta = self.factor_loadings.get(factor_name, 0)
            factor_return = factors[factor_name] * beta
            factor_contributions[factor_name] = factor_return
            total_factor_return += factor_return
        
        # Calculate specific (residual) return
        if STATSMODELS_AVAILABLE:
            specific_return = regression_results['residuals']
        else:
            # Reconstruct predictions
            X_matrix = np.column_stack([np.ones(len(X)), X.values])
            beta = regression_results['params']
            predictions = X_matrix @ beta
            specific_return = pd.Series(strategy_returns.values - predictions,
                                       index=strategy_returns.index)
        
        # Calculate variance explained
        total_variance = np.var(strategy_returns)
        factor_variance = np.var(total_factor_return) if len(total_factor_return) > 0 else 0
        specific_variance = np.var(specific_return) if len(specific_return) > 0 else 0
        
        explained_variance = {
            'factors': factor_variance,
            'specific': specific_variance,
            'total': total_variance,
            'percent_explained': factor_variance / total_variance if total_variance != 0 else 0
        }
        
        return {
            'factor_contributions': factor_contributions,
            'specific_return': specific_return,
            'total_explained_variance': explained_variance
        }


def generate_sample_data() -> Tuple[pd.Series, pd.Series, Dict[str, pd.Series]]:
    """
    Generate sample data for demonstration.
    
    Returns:
    --------
    tuple: (strategy_returns, benchmark_returns, factor_returns)
    """
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    
    # Generate factor returns
    factors = {}
    
    # Market factor (SPY-like)
    market_returns = np.random.normal(0.0003, 0.012, n_dates)
    factors['market'] = pd.Series(market_returns, index=dates)
    
    # Size factor (small cap premium)
    size_returns = np.random.normal(0.0001, 0.008, n_dates)
    factors['size'] = pd.Series(size_returns, index=dates)
    
    # Value factor
    value_returns = np.random.normal(0.00005, 0.006, n_dates)
    factors['value'] = pd.Series(value_returns, index=dates)
    
    # Momentum factor
    momentum_returns = np.random.normal(0.0002, 0.01, n_dates)
    factors['momentum'] = pd.Series(momentum_returns, index=dates)
    
    # Generate strategy returns with factor exposures
    # Strategy has 0.8 market beta, 0.2 size exposure, and some alpha
    strategy_returns = (
        0.8 * factors['market'] +
        0.2 * factors['size'] +
        -0.1 * factors['value'] +
        0.15 * factors['momentum'] +
        np.random.normal(0.0005, 0.005, n_dates)  # Alpha + idiosyncratic risk
    )
    
    strategy_series = pd.Series(strategy_returns, index=dates, name='strategy')
    benchmark_series = factors['market'].copy()
    
    return strategy_series, benchmark_series, factors


def main():
    """Main demonstration function."""
    print("Day 78: Performance Metrics & Analytics")
    print("=" * 60)
    
    # Generate sample data
    print("\nGenerating sample data...")
    strategy_returns, benchmark_returns, factor_data = generate_sample_data()
    
    print(f"Strategy observations: {len(strategy_returns)}")
    print(f"Strategy mean return: {strategy_returns.mean():.6f}")
    print(f"Strategy volatility: {strategy_returns.std():.6f}")
    
    # Initialize analyzer
    print("\nInitializing performance analyzer...")
    analyzer = AdvancedPerformanceAnalyzer(
        returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        risk_free_rate=0.02
    )
    
    # Calculate basic metrics
    print("\nCalculating basic performance metrics...")
    basic_metrics = analyzer.calculate_basic_metrics()
    
    print("\nBasic Performance Metrics:")
    print("-" * 40)
    for metric, value in basic_metrics.items():
        if isinstance(value, float):
            if 'drawdown' in metric.lower() and isinstance(value, float):
                print(f"{metric:25}: {value:>8.2%}")
            elif 'rate' in metric.lower() and isinstance(value, float):
                print(f"{metric:25}: {value:>8.2%}")
            elif 'return' in metric.lower() and isinstance(value, float):
                print(f"{metric:25}: {value:>8.2%}")
            elif 'volatility' in metric.lower() and isinstance(value, float):
                print(f"{metric:25}: {value:>8.2%}")
            else:
                print(f"{metric:25}: {value:>8.4f}")
    
    # Calculate advanced metrics
    print("\nCalculating advanced performance metrics...")
    advanced_metrics = analyzer.calculate_advanced_metrics()
    
    print("\nAdvanced Performance Metrics:")
    print("-" * 40)
    for metric, value in advanced_metrics.items():
        if value is not None:
            if isinstance(value, float):
                print(f"{metric:25}: {value:>8.4f}")
    
    # Generate report
    print("\nGenerating performance report...")
    report = analyzer.generate_performance_report()
    print(f"\nOverall Assessment: {report['overall_assessment']}")
    
    # Create visualization
    print("\nCreating performance visualization...")
    try:
        analyzer.plot_performance_summary(save_path='performance_summary.png')
        print("Performance summary saved to 'performance_summary.png'")
    except Exception as e:
        print(f"Could not create visualization: {e}")
    
    # Factor attribution analysis
    print("\nPerforming factor attribution analysis...")
    risk_model = MultiFactorRiskModel()
    
    try:
        attribution = risk_model.analyze(strategy_returns, factor_data)
        
        print(f"\nFactor Model R-squared: {attribution['r_squared']:.4f}")
        print(f"Variance explained by factors: {attribution['total_explained_variance']['percent_explained']:.2%}")
        
        print("\nFactor Loadings (Betas):")
        print("-" * 40)
        for factor, loading in attribution['factor_loadings'].items():
            print(f"{factor:15}: {loading:>8.4f}")
        
        # Calculate cumulative contributions
        print("\nCumulative Factor Contributions:")
        print("-" * 40)
        total_factor_contrib = 0
        for factor, contrib_series in attribution['factor_contributions'].items():
            cum_contrib = (1 + contrib_series).prod() - 1
            total_factor_contrib += cum_contrib
            print(f"{factor:15}: {cum_contrib:>8.2%}")
        
        specific_cum = (1 + attribution['specific_return']).prod() - 1
        print(f"{'specific':15}: {specific_cum:>8.2%}")
        
        total_from_model = total_factor_contrib + attribution['factor_loadings'].get('intercept', 0) / 252 * len(strategy_returns)
        actual_total = (1 + strategy_returns).prod() - 1
        print(f"\nModel reconstruction: {total_from_model:.2%}")
        print(f"Actual total return: {actual_total:.2%}")
        print(f"Difference: {(actual_total - total_from_model):.4%}")
        
    except Exception as e:
        print(f"Factor analysis failed: {e}")
    
    print("\n" + "=" * 60)
    print("Performance analysis complete")
    print("=" * 60)


if __name__ == "__main__":
    main()