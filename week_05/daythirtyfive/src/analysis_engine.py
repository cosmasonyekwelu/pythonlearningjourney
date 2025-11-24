"""
Analysis Engine
Technical analysis, fundamental analysis, and risk assessment
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class AnalysisEngine:
    """
    Comprehensive stock analysis engine
    """

    def __init__(self):
        self.risk_free_rate = 0.02  # Assume 2% risk-free rate

    def technical_analysis(self, data: pd.DataFrame) -> Dict:
        """
        Perform comprehensive technical analysis
        """
        technicals = {}

        # Moving averages
        technicals['moving_averages'] = self._calculate_moving_averages(
            data['Close'])

        # RSI
        technicals['rsi'] = self._calculate_rsi(data['Close'])

        # MACD
        technicals['macd'] = self._calculate_macd(data['Close'])

        # Bollinger Bands
        technicals['bollinger_bands'] = self._calculate_bollinger_bands(
            data['Close'])

        # Support and Resistance
        technicals['support_resistance'] = self._calculate_support_resistance(
            data)

        # Volume analysis
        technicals['volume_analysis'] = self._analyze_volume(data)

        # Price patterns
        technicals['price_patterns'] = self._identify_price_patterns(data)

        return technicals

    def fundamental_analysis(self, fundamental_data: Dict) -> Dict:
        """
        Perform fundamental analysis
        """
        analysis = {
            'valuation': {},
            'profitability': {},
            'efficiency': {},
            'financial_health': {},
            'growth': {},
            'dividends': {}
        }

        # Valuation metrics
        analysis['valuation'] = {
            'pe_ratio': fundamental_data.get('pe_ratio', 'N/A'),
            'forward_pe': fundamental_data.get('forward_pe', 'N/A'),
            'price_to_book': fundamental_data.get('price_to_book', 'N/A'),
            'price_to_sales': fundamental_data.get('price_to_sales', 'N/A'),
            'peg_ratio': fundamental_data.get('peg_ratio', 'N/A')
        }

        # Profitability
        analysis['profitability'] = {
            'profit_margin': fundamental_data.get('profit_margin', 'N/A'),
            'operating_margin': fundamental_data.get('operating_margin', 'N/A'),
            'return_on_equity': fundamental_data.get('return_on_equity', 'N/A'),
            'return_on_assets': fundamental_data.get('return_on_assets', 'N/A')
        }

        # Financial health
        analysis['financial_health'] = {
            'debt_to_equity': fundamental_data.get('debt_to_equity', 'N/A'),
            'current_ratio': fundamental_data.get('current_ratio', 'N/A')
        }

        # Dividends
        analysis['dividends'] = {
            'dividend_yield': fundamental_data.get('dividend_yield', 'N/A'),
            'payout_ratio': fundamental_data.get('payout_ratio', 'N/A')
        }

        # Growth (simplified)
        analysis['growth'] = {
            'earnings_growth': fundamental_data.get('earnings_growth', 'N/A'),
            'revenue_growth': fundamental_data.get('revenue_growth', 'N/A')
        }

        return analysis

    def risk_analysis(self, data: pd.DataFrame) -> Dict:
        """
        Perform comprehensive risk analysis
        """
        returns = data['Daily_Return'].dropna()

        if len(returns) == 0:
            return {}

        risk_metrics = {}

        # Basic risk metrics
        risk_metrics['volatility'] = returns.std() * np.sqrt(252)  # Annualized
        risk_metrics['variance'] = returns.var()

        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        risk_metrics['max_drawdown'] = drawdown.min()
        risk_metrics['max_drawdown_duration'] = self._calculate_drawdown_duration(
            drawdown)

        # Value at Risk (VaR)
        risk_metrics['var_95'] = returns.quantile(0.05)
        risk_metrics['var_99'] = returns.quantile(0.01)

        # Conditional VaR (Expected Shortfall)
        risk_metrics['cvar_95'] = returns[returns <=
                                          risk_metrics['var_95']].mean()

        # Sharpe ratio
        excess_returns = returns.mean() - (self.risk_free_rate / 252)
        risk_metrics['sharpe_ratio'] = (
            excess_returns / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

        # Sortino ratio (downside risk only)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        risk_metrics['sortino_ratio'] = (
            excess_returns / downside_std) * np.sqrt(252) if downside_std != 0 else 0

        # Beta calculation (would need market data for proper calculation)
        risk_metrics['beta'] = self._estimate_beta(returns)

        # Statistical measures
        risk_metrics['skewness'] = returns.skew()
        risk_metrics['kurtosis'] = returns.kurtosis()

        # Win rate and profit factor
        risk_metrics['win_rate'] = (returns > 0).mean()
        gains = returns[returns > 0].mean() if len(
            returns[returns > 0]) > 0 else 0
        losses = abs(returns[returns < 0].mean()) if len(
            returns[returns < 0]) > 0 else 1
        risk_metrics['profit_factor'] = gains / \
            losses if losses != 0 else float('inf')

        return risk_metrics

    def portfolio_analysis(self, portfolio_data: Dict, weights: Dict = None) -> Dict:
        """
        Analyze portfolio of multiple stocks
        """
        if weights is None:
            # Equal weighting if not specified
            n_stocks = len(portfolio_data)
            weights = {symbol: 1/n_stocks for symbol in portfolio_data.keys()}

        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(
            portfolio_data, weights)

        # Portfolio risk metrics
        portfolio_risk = self.risk_analysis(
            pd.DataFrame({'Daily_Return': portfolio_returns}))

        # Correlation matrix
        correlation_matrix = self._calculate_correlation_matrix(portfolio_data)

        # Diversification metrics
        diversification = self._calculate_diversification_metrics(
            portfolio_data, weights)

        return {
            'portfolio_returns': portfolio_returns,
            'portfolio_risk': portfolio_risk,
            'correlation_matrix': correlation_matrix,
            'diversification_metrics': diversification,
            'weights': weights
        }

    def _calculate_moving_averages(self, prices: pd.Series) -> Dict:
        """Calculate various moving averages"""
        windows = [5, 10, 20, 50, 200]
        mas = {}

        for window in windows:
            mas[f'sma_{window}'] = prices.rolling(
                window=window).mean().iloc[-1] if len(prices) >= window else None
            mas[f'ema_{window}'] = prices.ewm(span=window).mean(
            ).iloc[-1] if len(prices) >= window else None

        return mas

    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None

    def _calculate_macd(self, prices: pd.Series) -> Dict:
        """Calculate MACD indicator"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        return {
            'macd_line': macd_line.iloc[-1] if not macd_line.empty else None,
            'signal_line': signal_line.iloc[-1] if not signal_line.empty else None,
            'histogram': histogram.iloc[-1] if not histogram.empty else None
        }

    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, num_std: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()

        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)

        current_price = prices.iloc[-1]
        bb_position = (current_price - lower_band.iloc[-1]) / (
            upper_band.iloc[-1] - lower_band.iloc[-1]) if upper_band.iloc[-1] != lower_band.iloc[-1] else 0.5

        return {
            'upper_band': upper_band.iloc[-1] if not upper_band.empty else None,
            'lower_band': lower_band.iloc[-1] if not lower_band.empty else None,
            'middle_band': rolling_mean.iloc[-1] if not rolling_mean.empty else None,
            'bb_position': bb_position
        }

    def _calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels"""
        recent_data = data.tail(window)

        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()
        current_price = data['Close'].iloc[-1]

        return {
            'resistance': resistance,
            'support': support,
            'distance_to_resistance': (resistance - current_price) / current_price,
            'distance_to_support': (current_price - support) / current_price
        }

    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        volume_data = data['Volume'].dropna()

        if len(volume_data) == 0:
            return {}

        return {
            'avg_volume': volume_data.mean(),
            'volume_trend': volume_data.pct_change().mean(),
            'volume_sma_ratio': data['Volume_Ratio'].iloc[-1] if 'Volume_Ratio' in data.columns else None
        }

    def _identify_price_patterns(self, data: pd.DataFrame) -> List[str]:
        """Identify common price patterns"""
        patterns = []

        # Simple pattern detection
        recent_data = data.tail(10)

        # Uptrend detection
        if len(recent_data) >= 3:
            if (recent_data['Close'].iloc[-3] < recent_data['Close'].iloc[-2] < recent_data['Close'].iloc[-1]):
                patterns.append("Uptrend")

            # Downtrend detection
            if (recent_data['Close'].iloc[-3] > recent_data['Close'].iloc[-2] > recent_data['Close'].iloc[-1]):
                patterns.append("Downtrend")

        return patterns

    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration"""
        in_drawdown = drawdown < 0
        drawdown_periods = in_drawdown.astype(int).groupby(
            (in_drawdown != in_drawdown.shift()).cumsum()).sum()
        return drawdown_periods.max() if not drawdown_periods.empty else 0

    def _estimate_beta(self, returns: pd.Series) -> float:
        """Estimate beta (simplified - would need market returns for accurate calculation)"""
        # This is a simplified version. In practice, you'd need market returns (e.g., SPY)
        return 1.0  # Placeholder

    def _calculate_portfolio_returns(self, portfolio_data: Dict, weights: Dict) -> pd.Series:
        """Calculate portfolio returns from individual stock returns"""
        # Align all return series
        all_returns = []
        for symbol, data in portfolio_data.items():
            if 'Daily_Return' in data.columns:
                returns = data['Daily_Return'].rename(symbol)
                all_returns.append(returns)

        if not all_returns:
            return pd.Series(dtype=float)

        returns_df = pd.concat(all_returns, axis=1).dropna()

        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        for symbol in returns_df.columns:
            if symbol in weights:
                portfolio_returns += returns_df[symbol] * weights[symbol]

        return portfolio_returns

    def _calculate_correlation_matrix(self, portfolio_data: Dict) -> pd.DataFrame:
        """Calculate correlation matrix for portfolio stocks"""
        returns_data = {}

        for symbol, data in portfolio_data.items():
            if 'Daily_Return' in data.columns:
                returns_data[symbol] = data['Daily_Return']

        if not returns_data:
            return pd.DataFrame()

        returns_df = pd.DataFrame(returns_data).dropna()
        return returns_df.corr()

    def _calculate_diversification_metrics(self, portfolio_data: Dict, weights: Dict) -> Dict:
        """Calculate portfolio diversification metrics"""
        correlation_matrix = self._calculate_correlation_matrix(portfolio_data)

        if correlation_matrix.empty:
            return {}

        # Average correlation
        n = len(correlation_matrix)
        avg_correlation = (correlation_matrix.sum().sum() -
                           n) / (n * (n - 1)) if n > 1 else 1

        # Diversification ratio (simplified)
        diversification_ratio = 1 / \
            (1 - avg_correlation) if avg_correlation < 1 else float('inf')

        return {
            'average_correlation': avg_correlation,
            'diversification_ratio': diversification_ratio,
            'number_of_assets': n
        }


# Singleton instance
analysis_engine = AnalysisEngine()
