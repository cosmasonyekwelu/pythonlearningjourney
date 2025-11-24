"""
Stock Data Analyzer - Main Facade Class
High-level interface combining all modules
"""

from .reporting import report_generator
from .analysis_engine import analysis_engine
from .data_collection import data_collector
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class StockDataAnalyzer:
    """
    Main facade class providing high-level interface to all analysis capabilities
    """

    def __init__(self):
        self.data_collector = data_collector
        self.analysis_engine = analysis_engine
        self.report_generator = report_generator

    def analyze_stock(self, symbol: str, period: str = '1y',
                      interval: str = '1d') -> Dict:
        """
        Perform comprehensive analysis of a single stock
        """
        print(f"Analyzing {symbol}...")

        # Data collection
        stock_data = self.data_collector.get_stock_data(
            symbol, period, interval)
        fundamental_data = self.data_collector.get_fundamental_data(symbol)

        if stock_data.empty:
            return {'error': f'No data available for {symbol}'}

        # Analysis
        technical_indicators = self.analysis_engine.technical_analysis(
            stock_data)
        fundamental_metrics = self.analysis_engine.fundamental_analysis(
            fundamental_data)
        risk_metrics = self.analysis_engine.risk_analysis(stock_data)

        # Compile results
        analysis_results = {
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': stock_data,
            'technical_indicators': technical_indicators,
            'fundamental_metrics': fundamental_metrics,
            'risk_metrics': risk_metrics,
            'analysis_timestamp': datetime.now().isoformat()
        }

        return analysis_results

    def compare_stocks(self, symbols: List[str], period: str = '1y',
                       interval: str = '1d') -> Dict:
        """
        Compare multiple stocks and analyze their relationships
        """
        print(f"Comparing {len(symbols)} stocks...")

        # Individual analysis for each stock
        individual_analysis = {}
        for symbol in symbols:
            analysis = self.analyze_stock(symbol, period, interval)
            if 'error' not in analysis:
                individual_analysis[symbol] = analysis

        if not individual_analysis:
            return {'error': 'No valid data for any symbols'}

        # Portfolio analysis
        portfolio_data = {symbol: analysis['data']
                          for symbol, analysis in individual_analysis.items()}
        portfolio_analysis = self.analysis_engine.portfolio_analysis(
            portfolio_data)

        # Compile comparison results
        comparison_results = {
            'symbols': symbols,
            'period': period,
            'individual_analysis': individual_analysis,
            'portfolio_analysis': portfolio_analysis,
            'comparison_timestamp': datetime.now().isoformat()
        }

        return comparison_results

    def generate_report(self, analysis_results: Dict, report_type: str = 'stock',
                        format: str = 'html') -> str:
        """
        Generate report from analysis results
        """
        if report_type == 'stock':
            return self.report_generator.generate_stock_report(analysis_results, format)
        elif report_type == 'portfolio':
            return self.report_generator.generate_portfolio_report(analysis_results, format)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def get_stock_recommendation(self, symbol: str, period: str = '1y') -> Dict:
        """
        Generate investment recommendation for a stock
        """
        analysis = self.analyze_stock(symbol, period)

        if 'error' in analysis:
            return {'error': analysis['error']}

        # Simple recommendation logic
        recommendation = self._generate_recommendation(analysis)

        return {
            'symbol': symbol,
            'recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'reasons': recommendation['reasons'],
            'analysis_summary': {
                'technical_score': recommendation.get('technical_score', 0),
                'fundamental_score': recommendation.get('fundamental_score', 0),
                'risk_score': recommendation.get('risk_score', 0)
            }
        }

    def screen_stocks(self, criteria: Dict) -> List[Dict]:
        """
        Screen stocks based on specified criteria
        """
        available_symbols = self.data_collector.get_available_symbols()
        screened_stocks = []

        print(f"Screening {len(available_symbols)} stocks...")

        for symbol in available_symbols[:10]:  # Limit for demo
            try:
                analysis = self.analyze_stock(symbol, '6mo')

                if self._meets_criteria(analysis, criteria):
                    screened_stocks.append({
                        'symbol': symbol,
                        'analysis': analysis,
                        'score': self._calculate_screening_score(analysis, criteria)
                    })
            except Exception as e:
                print(f"Error screening {symbol}: {e}")
                continue

        # Sort by score
        screened_stocks.sort(key=lambda x: x['score'], reverse=True)

        return screened_stocks

    def _generate_recommendation(self, analysis: Dict) -> Dict:
        """
        Generate investment recommendation based on analysis
        """
        score = 0
        reasons = []

        # Technical factors
        tech = analysis.get('technical_indicators', {})
        if 'rsi' in tech and tech['rsi'] is not None:
            if tech['rsi'] < 30:
                score += 2
                reasons.append(
                    "Strong buy signal: RSI indicates oversold condition")
            elif tech['rsi'] < 40:
                score += 1
                reasons.append(
                    "Moderate buy signal: RSI near oversold territory")
            elif tech['rsi'] > 70:
                score -= 2
                reasons.append(
                    "Strong sell signal: RSI indicates overbought condition")
            elif tech['rsi'] > 60:
                score -= 1
                reasons.append(
                    "Moderate sell signal: RSI near overbought territory")

        # Risk factors
        risk = analysis.get('risk_metrics', {})
        if 'sharpe_ratio' in risk:
            if risk['sharpe_ratio'] > 1.5:
                score += 2
                reasons.append("Excellent risk-adjusted returns")
            elif risk['sharpe_ratio'] > 0.5:
                score += 1
                reasons.append("Good risk-adjusted returns")
            elif risk['sharpe_ratio'] < 0:
                score -= 1
                reasons.append("Poor risk-adjusted returns")

        if 'volatility' in risk:
            if risk['volatility'] < 0.2:  # 20% annual volatility
                score += 1
                reasons.append("Low volatility")
            elif risk['volatility'] > 0.4:  # 40% annual volatility
                score -= 1
                reasons.append("High volatility")

        # Fundamental factors (simplified)
        fundamental = analysis.get('fundamental_metrics', {})
        valuation = fundamental.get('valuation', {})

        if valuation.get('pe_ratio') != 'N/A' and isinstance(valuation['pe_ratio'], (int, float)):
            if valuation['pe_ratio'] < 15:
                score += 1
                reasons.append("Attractive valuation (low P/E)")
            elif valuation['pe_ratio'] > 30:
                score -= 1
                reasons.append("Expensive valuation (high P/E)")

        # Determine recommendation
        if score >= 3:
            action = "STRONG BUY"
            confidence = "High"
        elif score >= 1:
            action = "BUY"
            confidence = "Medium"
        elif score == 0:
            action = "HOLD"
            confidence = "Neutral"
        elif score >= -2:
            action = "SELL"
            confidence = "Medium"
        else:
            action = "STRONG SELL"
            confidence = "High"

        return {
            'action': action,
            'confidence': confidence,
            'reasons': reasons,
            'technical_score': score,  # Simplified - in practice would have separate scores
            'fundamental_score': 0,    # Placeholder
            'risk_score': 0            # Placeholder
        }

    def _meets_criteria(self, analysis: Dict, criteria: Dict) -> bool:
        """
        Check if stock meets screening criteria
        """
        # Implementation would check various criteria
        # This is a simplified version
        risk_metrics = analysis.get('risk_metrics', {})

        # Example criteria check
        if 'max_volatility' in criteria:
            if risk_metrics.get('volatility', float('inf')) > criteria['max_volatility']:
                return False

        if 'min_sharpe' in criteria:
            if risk_metrics.get('sharpe_ratio', -float('inf')) < criteria['min_sharpe']:
                return False

        return True

    def _calculate_screening_score(self, analysis: Dict, criteria: Dict) -> float:
        """
        Calculate screening score based on criteria
        """
        score = 0

        risk_metrics = analysis.get('risk_metrics', {})

        # Higher Sharpe ratio is better
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        score += sharpe * 10

        # Lower volatility is better
        volatility = risk_metrics.get('volatility', 0)
        score -= volatility * 5

        # Positive returns are better
        if 'data' in analysis and not analysis['data'].empty:
            returns = analysis['data']['Daily_Return'].mean()
            score += returns * 1000

        return score

    def clear_cache(self, older_than_days: int = 7):
        """
        Clear data cache
        """
        self.data_collector.clear_cache(older_than_days)

    def get_available_analysis_methods(self) -> List[str]:
        """
        Get list of available analysis methods
        """
        return [
            'technical_analysis',
            'fundamental_analysis',
            'risk_analysis',
            'portfolio_analysis',
            'stock_screening',
            'comparison_analysis'
        ]


# Singleton instance
stock_analyzer = StockDataAnalyzer()
