"""
Reporting Module
Generate reports, exports, and alerts
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List
import json
import warnings
warnings.filterwarnings('ignore')


class ReportGenerator:
    """
    Generate various types of reports and exports
    """

    def __init__(self, export_dir='data/exports'):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def generate_stock_report(self, analysis_results: Dict, format: str = 'html') -> str:
        """
        Generate comprehensive stock analysis report
        """
        symbol = analysis_results.get('symbol', 'Unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if format == 'html':
            return self._generate_html_report(analysis_results, symbol, timestamp)
        elif format == 'csv':
            return self._generate_csv_report(analysis_results, symbol, timestamp)
        elif format == 'excel':
            return self._generate_excel_report(analysis_results, symbol, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_portfolio_report(self, portfolio_analysis: Dict, format: str = 'html') -> str:
        """
        Generate portfolio analysis report
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if format == 'html':
            return self._generate_portfolio_html_report(portfolio_analysis, timestamp)
        elif format == 'csv':
            return self._generate_portfolio_csv_report(portfolio_analysis, timestamp)
        elif format == 'excel':
            return self._generate_portfolio_excel_report(portfolio_analysis, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html_report(self, analysis: Dict, symbol: str, timestamp: str) -> str:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Stock Analysis Report - {symbol}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9e9e9; border-radius: 3px; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Stock Analysis Report</h1>
                <h2>{symbol}</h2>
                <p>Generated: {timestamp}</p>
            </div>
            
            <div class="section">
                <h3>Price Summary</h3>
                {self._format_price_summary(analysis)}
            </div>
            
            <div class="section">
                <h3>Technical Analysis</h3>
                {self._format_technical_analysis(analysis.get('technical_indicators', {}))}
            </div>
            
            <div class="section">
                <h3>Fundamental Analysis</h3>
                {self._format_fundamental_analysis(analysis.get('fundamental_metrics', {}))}
            </div>
            
            <div class="section">
                <h3>Risk Analysis</h3>
                {self._format_risk_analysis(analysis.get('risk_metrics', {}))}
            </div>
            
            <div class="section">
                <h3>Recommendation</h3>
                {self._generate_recommendation(analysis)}
            </div>
        </body>
        </html>
        """

        filename = f"stock_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.export_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def _generate_csv_report(self, analysis: Dict, symbol: str, timestamp: str) -> str:
        """Generate CSV report"""
        # Flatten analysis data for CSV
        flat_data = {}

        # Price data summary
        if 'data' in analysis and not analysis['data'].empty:
            latest_data = analysis['data'].iloc[-1]
            flat_data.update({
                'current_price': latest_data.get('Close', 'N/A'),
                'daily_change': latest_data.get('Price_Change', 'N/A'),
                'daily_return': latest_data.get('Daily_Return', 'N/A')
            })

        # Technical indicators
        tech_indicators = analysis.get('technical_indicators', {})
        for category, indicators in tech_indicators.items():
            if isinstance(indicators, dict):
                for key, value in indicators.items():
                    flat_data[f'technical_{category}_{key}'] = value

        # Risk metrics
        risk_metrics = analysis.get('risk_metrics', {})
        for key, value in risk_metrics.items():
            flat_data[f'risk_{key}'] = value

        # Create DataFrame and save
        df = pd.DataFrame([flat_data])
        filename = f"stock_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        df.to_csv(filepath, index=False)

        return filepath

    def _generate_excel_report(self, analysis: Dict, symbol: str, timestamp: str) -> str:
        """Generate Excel report with multiple sheets"""
        filename = f"stock_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.export_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Price data sheet
            if 'data' in analysis and not analysis['data'].empty:
                analysis['data'].to_excel(writer, sheet_name='Price Data')

            # Technical indicators sheet
            tech_data = self._flatten_technical_indicators(
                analysis.get('technical_indicators', {}))
            if tech_data:
                pd.DataFrame([tech_data]).to_excel(
                    writer, sheet_name='Technical Analysis')

            # Risk metrics sheet
            risk_data = analysis.get('risk_metrics', {})
            if risk_data:
                pd.DataFrame([risk_data]).to_excel(
                    writer, sheet_name='Risk Analysis')

            # Summary sheet
            summary_data = self._create_summary_data(analysis)
            pd.DataFrame([summary_data]).to_excel(writer, sheet_name='Summary')

        return filepath

    def _format_price_summary(self, analysis: Dict) -> str:
        """Format price summary for HTML report"""
        if 'data' not in analysis or analysis['data'].empty:
            return "<p>No price data available</p>"

        data = analysis['data']
        latest = data.iloc[-1]

        price_change = latest.get('Price_Change', 0)
        price_change_pct = latest.get('Daily_Return', 0) * 100
        change_class = "positive" if price_change >= 0 else "negative"
        change_sign = "+" if price_change >= 0 else ""

        return f"""
        <div class="metric">
            <strong>Current Price:</strong> ${latest.get('Close', 'N/A'):.2f}<br>
            <strong>Daily Change:</strong> <span class="{change_class}">{change_sign}{price_change:.2f} ({change_sign}{price_change_pct:.2f}%)</span><br>
            <strong>Volume:</strong> {latest.get('Volume', 'N/A'):,.0f}<br>
            <strong>High:</strong> ${latest.get('High', 'N/A'):.2f}<br>
            <strong>Low:</strong> ${latest.get('Low', 'N/A'):.2f}
        </div>
        """

    def _format_technical_analysis(self, technicals: Dict) -> str:
        """Format technical analysis for HTML report"""
        if not technicals:
            return "<p>No technical analysis available</p>"

        html = "<table>"

        # Moving averages
        if 'moving_averages' in technicals:
            html += "<tr><th colspan='2'>Moving Averages</th></tr>"
            for ma, value in technicals['moving_averages'].items():
                if value is not None:
                    html += f"<tr><td>{ma}</td><td>{value:.2f}</td></tr>"

        # RSI
        if 'rsi' in technicals and technicals['rsi'] is not None:
            rsi = technicals['rsi']
            rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            rsi_class = "negative" if rsi > 70 else "positive" if rsi < 30 else ""
            html += f"<tr><td>RSI</td><td><span class='{rsi_class}'>{rsi:.2f} ({rsi_status})</span></td></tr>"

        # MACD
        if 'macd' in technicals:
            macd = technicals['macd']
            html += "<tr><th colspan='2'>MACD</th></tr>"
            for key, value in macd.items():
                if value is not None:
                    html += f"<tr><td>{key}</td><td>{value:.4f}</td></tr>"

        html += "</table>"
        return html

    def _format_fundamental_analysis(self, fundamentals: Dict) -> str:
        """Format fundamental analysis for HTML report"""
        if not fundamentals:
            return "<p>No fundamental analysis available</p>"

        html = "<table>"

        for category, metrics in fundamentals.items():
            html += f"<tr><th colspan='2'>{category.title()}</th></tr>"
            for metric, value in metrics.items():
                if value != 'N/A':
                    html += f"<tr><td>{metric.replace('_', ' ').title()}</td><td>{value}</td></tr>"

        html += "</table>"
        return html

    def _format_risk_analysis(self, risk_metrics: Dict) -> str:
        """Format risk analysis for HTML report"""
        if not risk_metrics:
            return "<p>No risk analysis available</p>"

        html = "<table>"

        for metric, value in risk_metrics.items():
            if isinstance(value, (int, float)):
                if 'ratio' in metric.lower():
                    html += f"<tr><td>{metric.replace('_', ' ').title()}</td><td>{value:.3f}</td></tr>"
                elif 'pct' in metric.lower() or 'rate' in metric.lower():
                    html += f"<tr><td>{metric.replace('_', ' ').title()}</td><td>{value:.2%}</td></tr>"
                else:
                    html += f"<tr><td>{metric.replace('_', ' ').title()}</td><td>{value:.4f}</td></tr>"

        html += "</table>"
        return html

    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate investment recommendation"""
        # Simple recommendation logic based on multiple factors
        score = 0
        reasons = []

        # Technical factors
        tech = analysis.get('technical_indicators', {})
        if 'rsi' in tech and tech['rsi'] is not None:
            if tech['rsi'] < 30:
                score += 1
                reasons.append("RSI indicates oversold condition")
            elif tech['rsi'] > 70:
                score -= 1
                reasons.append("RSI indicates overbought condition")

        # Risk factors
        risk = analysis.get('risk_metrics', {})
        if 'sharpe_ratio' in risk:
            if risk['sharpe_ratio'] > 1:
                score += 1
                reasons.append("Good risk-adjusted returns")
            elif risk['sharpe_ratio'] < 0:
                score -= 1
                reasons.append("Poor risk-adjusted returns")

        # Generate recommendation
        if score > 1:
            recommendation = "BUY"
            color = "positive"
        elif score < -1:
            recommendation = "SELL"
            color = "negative"
        else:
            recommendation = "HOLD"
            color = ""

        reasons_html = "<ul>" + "".join(f"<li>{reason}</li>" for reason in reasons) + \
            "</ul>" if reasons else "<p>No specific factors identified</p>"

        return f"""
        <h4 class="{color}">Recommendation: {recommendation}</h4>
        <p><strong>Score: {score}</strong></p>
        <h5>Key Factors:</h5>
        {reasons_html}
        """

    def _flatten_technical_indicators(self, technicals: Dict) -> Dict:
        """Flatten technical indicators for CSV/Excel export"""
        flat_data = {}

        for category, indicators in technicals.items():
            if isinstance(indicators, dict):
                for key, value in indicators.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            flat_data[f"{category}_{key}_{sub_key}"] = sub_value
                    else:
                        flat_data[f"{category}_{key}"] = value

        return flat_data

    def _create_summary_data(self, analysis: Dict) -> Dict:
        """Create summary data for Excel report"""
        summary = {
            'symbol': analysis.get('symbol', 'Unknown'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Add key metrics
        if 'data' in analysis and not analysis['data'].empty:
            latest = analysis['data'].iloc[-1]
            summary['current_price'] = latest.get('Close')
            summary['daily_return'] = latest.get('Daily_Return')

        risk_metrics = analysis.get('risk_metrics', {})
        summary.update({f"risk_{k}": v for k, v in risk_metrics.items()})

        return summary

    def _generate_portfolio_html_report(self, portfolio_analysis: Dict, timestamp: str) -> str:
        """Generate HTML portfolio report"""
        # Implementation for portfolio report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Portfolio Analysis Report</h1>
                <p>Generated: {timestamp}</p>
            </div>
            
            <div class="section">
                <h3>Portfolio Performance</h3>
                <p>Portfolio analysis report would go here...</p>
            </div>
        </body>
        </html>
        """

        filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.export_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def _generate_portfolio_csv_report(self, portfolio_analysis: Dict, timestamp: str) -> str:
        """Generate CSV portfolio report"""
        # Implementation for portfolio CSV report
        filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.export_dir, filename)

        # Create sample data for demonstration
        sample_data = {'portfolio_metrics': portfolio_analysis.get(
            'portfolio_risk', {})}
        df = pd.DataFrame([sample_data])
        df.to_csv(filepath, index=False)

        return filepath

    def _generate_portfolio_excel_report(self, portfolio_analysis: Dict, timestamp: str) -> str:
        """Generate Excel portfolio report"""
        filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.export_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Add portfolio metrics sheet
            portfolio_risk = portfolio_analysis.get('portfolio_risk', {})
            pd.DataFrame([portfolio_risk]).to_excel(
                writer, sheet_name='Portfolio Metrics')

            # Add correlation matrix sheet
            correlation_matrix = portfolio_analysis.get(
                'correlation_matrix', pd.DataFrame())
            if not correlation_matrix.empty:
                correlation_matrix.to_excel(
                    writer, sheet_name='Correlation Matrix')

        return filepath

# Email alert stub (for future implementation)


class EmailAlerts:
    """Email alert system (stub for future implementation)"""

    def __init__(self):
        self.enabled = False

    def send_alert(self, subject: str, message: str, recipients: List[str]) -> bool:
        """Send email alert (stub implementation)"""
        if not self.enabled:
            print(f"Email alert (disabled): {subject}")
            return False

        # Future implementation would integrate with email service
        print(f"Would send email: {subject} to {recipients}")
        return True

    def configure(self, smtp_server: str, port: int, username: str, password: str):
        """Configure email settings"""
        self.enabled = True
        print("Email alerts configured (stub)")


# Singleton instances
report_generator = ReportGenerator()
email_alerts = EmailAlerts()
