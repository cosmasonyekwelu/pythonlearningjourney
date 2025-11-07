import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
from datetime import datetime, timedelta
import os
from jinja2 import Template
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PortfolioReporter:
    def __init__(self):
        self.portfolio_data = self.load_portfolio_data()

    def load_portfolio_data(self):
        """Load or generate sample portfolio data"""
        # In a real scenario, this would come from your database
        sample_data = [
            {'symbol': 'AAPL', 'shares': 10,
                'avg_cost': 150.0, 'current_price': 175.0},
            {'symbol': 'GOOGL', 'shares': 5,
                'avg_cost': 2200.0, 'current_price': 2400.0},
            {'symbol': 'MSFT', 'shares': 8, 'avg_cost': 280.0, 'current_price': 310.0},
            {'symbol': 'TSLA', 'shares': 15,
                'avg_cost': 180.0, 'current_price': 210.0},
            {'symbol': 'AMZN', 'shares': 3,
                'avg_cost': 3200.0, 'current_price': 3400.0}
        ]
        return pd.DataFrame(sample_data)

    def calculate_metrics(self):
        """Calculate portfolio metrics"""
        df = self.portfolio_data.copy()
        df['current_value'] = df['shares'] * df['current_price']
        df['cost_basis'] = df['shares'] * df['avg_cost']
        df['unrealized_pnl'] = df['current_value'] - df['cost_basis']
        df['pnl_percent'] = (df['unrealized_pnl'] / df['cost_basis']) * 100

        total_value = df['current_value'].sum()
        total_cost = df['cost_basis'].sum()
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100

        metrics = {
            'total_portfolio_value': total_value,
            'total_cost_basis': total_cost,
            'total_unrealized_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return df, metrics

    def create_visualizations(self, df):
        """Generate portfolio visualizations"""
        plt.style.use('seaborn-v0_8')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Portfolio allocation pie chart
        allocation = df.groupby('symbol')['current_value'].sum()
        ax1.pie(allocation.values, labels=allocation.index,
                autopct='%1.1f%%', startangle=90)
        ax1.set_title('Portfolio Allocation by Symbol')

        # P&L by symbol bar chart
        colors = ['green' if x >= 0 else 'red' for x in df['unrealized_pnl']]
        ax2.bar(df['symbol'], df['unrealized_pnl'], color=colors)
        ax2.set_title('Unrealized P&L by Symbol')
        ax2.set_ylabel('P&L ($)')
        ax2.tick_params(axis='x', rotation=45)

        # Portfolio value composition
        ax3.bar(df['symbol'], df['current_value'],
                alpha=0.7, label='Current Value')
        ax3.bar(df['symbol'], df['cost_basis'], alpha=0.7, label='Cost Basis')
        ax3.set_title('Portfolio Value vs Cost Basis')
        ax3.set_ylabel('Value ($)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend()

        # P&L percentage
        ax4.bar(df['symbol'], df['pnl_percent'], color=colors)
        ax4.set_title('P&L Percentage by Symbol')
        ax4.set_ylabel('P&L (%)')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('portfolio_report.png', dpi=300, bbox_inches='tight')
        plt.close()

        logging.info("Portfolio visualizations created")

    def generate_html_report(self, df, metrics):
        """Generate HTML report using Jinja2 templating"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Report - {{ metrics.update_time }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
                .metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 20px 0; }
                .metric-card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .positive { color: green; }
                .negative { color: red; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f4f4f4; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Portfolio Performance Report</h1>
                <p>Generated on: {{ metrics.update_time }}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Portfolio Value</h3>
                    <p>${{ "%.2f"|format(metrics.total_portfolio_value) }}</p>
                </div>
                <div class="metric-card">
                    <h3>Total P&L</h3>
                    <p class="{{ 'positive' if metrics.total_unrealized_pnl >= 0 else 'negative' }}">
                        ${{ "%.2f"|format(metrics.total_unrealized_pnl) }} ({{ "%.2f"|format(metrics.total_pnl_percent) }}%)
                    </p>
                </div>
            </div>
            
            <h2>Holdings Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Shares</th>
                        <th>Avg Cost</th>
                        <th>Current Price</th>
                        <th>Current Value</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                    </tr>
                </thead>
                <tbody>
                    {% for holding in holdings %}
                    <tr>
                        <td>{{ holding.symbol }}</td>
                        <td>{{ holding.shares }}</td>
                        <td>${{ "%.2f"|format(holding.avg_cost) }}</td>
                        <td>${{ "%.2f"|format(holding.current_price) }}</td>
                        <td>${{ "%.2f"|format(holding.current_value) }}</td>
                        <td class="{{ 'positive' if holding.unrealized_pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(holding.unrealized_pnl) }}
                        </td>
                        <td class="{{ 'positive' if holding.pnl_percent >= 0 else 'negative' }}">
                            {{ "%.2f"|format(holding.pnl_percent) }}%
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <h2>Portfolio Visualization</h2>
            <img src="portfolio_report.png" alt="Portfolio Charts" style="max-width: 100%;">
        </body>
        </html>
        """

        template = Template(template_str)
        holdings = df.to_dict('records')
        html_content = template.render(metrics=metrics, holdings=holdings)

        with open('portfolio_report.html', 'w') as f:
            f.write(html_content)

        logging.info("HTML report generated")
        return html_content

    def send_email_report(self, html_content):
        """Send report via email (configure with your email settings)"""
        try:
            # Email configuration - replace with your actual credentials
            smtp_server = "smtp.gmail.com"
            port = 587
            sender_email = "your_email@gmail.com"
            password = "your_app_password"  # Use app-specific password for Gmail

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email  # Send to yourself for testing
            msg['Subject'] = f"Portfolio Report - {datetime.now().strftime('%Y-%m-%d')}"

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Attach image
            with open('portfolio_report.png', 'rb') as f:
                img_part = MIMEBase('application', 'octet-stream')
                img_part.set_payload(f.read())
                encoders.encode_base64(img_part)
                img_part.add_header(
                    'Content-Disposition',
                    'attachment; filename=portfolio_report.png'
                )
                msg.attach(img_part)

            # Send email
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            server.quit()

            logging.info("Email report sent successfully")

        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            logging.info("Please configure email settings in the code")


def main():
    reporter = PortfolioReporter()

    # Calculate portfolio metrics
    df, metrics = reporter.calculate_metrics()

    # Print summary to console
    print("\n" + "="*50)
    print("PORTFOLIO REPORT SUMMARY")
    print("="*50)
    print(f"Total Portfolio Value: ${metrics['total_portfolio_value']:,.2f}")
    print(f"Total Cost Basis: ${metrics['total_cost_basis']:,.2f}")
    print(f"Total Unrealized P&L: ${metrics['total_unrealized_pnl']:,.2f}")
    print(f"Total P&L %: {metrics['total_pnl_percent']:.2f}%")
    print(f"Report Time: {metrics['update_time']}")

    print("\nHoldings Details:")
    print(df[['symbol', 'shares', 'current_price', 'current_value',
          'unrealized_pnl', 'pnl_percent']].to_string(index=False))

    # Generate visualizations
    reporter.create_visualizations(df)

    # Generate HTML report
    html_content = reporter.generate_html_report(df, metrics)

    # Uncomment and configure to send email
    # reporter.send_email_report(html_content)

    logging.info("Portfolio report generation completed")
    print(f"\nReport files generated:")
    print("- portfolio_report.html")
    print("- portfolio_report.png")


if __name__ == "__main__":
    main()
