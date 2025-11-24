import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RiskManager:
    def __init__(self, db_path='trading_system.db'):
        self.db_path = db_path
        self.risk_limits = self.load_risk_limits()

    def load_risk_limits(self):
        """Load risk management limits and parameters"""
        return {
            'max_position_size_percent': 0.05,  # 5% of portfolio per position
            'max_daily_loss_percent': 0.02,     # 2% max daily loss
            'max_drawdown_percent': 0.10,       # 10% max drawdown
            'max_sector_exposure': 0.30,        # 30% max per sector
            'min_risk_reward_ratio': 2.0,       # 2:1 minimum risk/reward
            'max_leverage': 1.0,                # No leverage
            'stop_loss_percent': 0.05,          # 5% stop loss
            'trailing_stop_percent': 0.03       # 3% trailing stop
        }

    def get_portfolio_value(self):
        """Calculate current portfolio value"""
        conn = sqlite3.connect(self.db_path)

        # Get current positions and their values
        positions_df = pd.read_sql('''
            SELECT p.symbol, p.quantity, p.average_price,
                   (SELECT close_price FROM market_data WHERE symbol = p.symbol ORDER BY timestamp DESC LIMIT 1) as current_price
            FROM positions p
            WHERE p.quantity > 0
        ''', conn)

        # Calculate portfolio value (simplified - in reality, you'd have cash balance too)
        if not positions_df.empty:
            positions_df['current_price'] = positions_df['current_price'].fillna(
                positions_df['average_price'])
            positions_df['market_value'] = positions_df['quantity'] * \
                positions_df['current_price']
            portfolio_value = positions_df['market_value'].sum()
        else:
            portfolio_value = 100000  # Default portfolio value for demo

        conn.close()
        return portfolio_value

    def pre_trade_risk_check(self, symbol, quantity, order_type, price=None):
        """Perform pre-trade risk validation"""
        portfolio_value = self.get_portfolio_value()
        max_position_value = portfolio_value * \
            self.risk_limits['max_position_size_percent']

        # Calculate proposed position value
        if price is None:
            # For market orders, use current price
            current_price = self.get_current_price(symbol)
            proposed_value = quantity * current_price
        else:
            proposed_value = quantity * price

        risk_checks = {
            'position_size_ok': proposed_value <= max_position_value,
            'leverage_ok': True,  # Simplified for demo
            'daily_loss_ok': self.check_daily_loss_limit(),
            'drawdown_ok': self.check_drawdown_limit(),
            'sector_exposure_ok': self.check_sector_exposure(symbol, proposed_value, portfolio_value)
        }

        # Generate risk report
        risk_report = {
            'portfolio_value': portfolio_value,
            'max_allowed_position': max_position_value,
            'proposed_position_value': proposed_value,
            'checks_passed': all(risk_checks.values()),
            'failed_checks': [k for k, v in risk_checks.items() if not v],
            'risk_checks': risk_checks
        }

        logging.info(
            f"Pre-trade risk check for {symbol}: {'PASSED' if risk_report['checks_passed'] else 'FAILED'}")
        return risk_report

    def check_daily_loss_limit(self):
        """Check if daily loss limit is exceeded"""
        conn = sqlite3.connect(self.db_path)

        # Calculate today's P&L from closed trades
        today = datetime.now().date()
        daily_pnl = pd.read_sql('''
            SELECT SUM((filled_quantity * average_fill_price) - (filled_quantity * 
                   (SELECT average_price FROM positions_history WHERE symbol = o.symbol AND date < ?)))
            FROM orders o
            WHERE DATE(o.updated_at) = ? AND o.status = 'FILLED' AND o.side = 'sell'
        ''', conn, params=[today, today])

        conn.close()

        daily_loss = abs(daily_pnl.iloc[0, 0] or 0)
        max_daily_loss = self.get_portfolio_value(
        ) * self.risk_limits['max_daily_loss_percent']

        return daily_loss <= max_daily_loss

    def check_drawdown_limit(self):
        """Check portfolio drawdown limits"""
        # Simplified implementation - in reality, you'd track portfolio highs
        portfolio_value = self.get_portfolio_value()
        initial_portfolio_value = 100000  # This would come from your records

        drawdown = (initial_portfolio_value - portfolio_value) / \
            initial_portfolio_value
        return drawdown <= self.risk_limits['max_drawdown_percent']

    def check_sector_exposure(self, new_symbol, new_position_value, portfolio_value):
        """Check sector concentration limits"""
        # Simplified sector mapping
        sector_map = {
            'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology',
            'TSLA': 'Automotive', 'AMZN': 'Consumer', 'JPM': 'Financial'
        }

        new_sector = sector_map.get(new_symbol, 'Unknown')

        conn = sqlite3.connect(self.db_path)

        # Get current sector exposures
        positions_df = pd.read_sql('''
            SELECT p.symbol, p.quantity, p.average_price
            FROM positions p
            WHERE p.quantity > 0
        ''', conn)

        conn.close()

        if not positions_df.empty:
            # Calculate current sector values
            positions_df['sector'] = positions_df['symbol'].map(sector_map)
            positions_df['current_price'] = positions_df['symbol'].apply(
                self.get_current_price)
            positions_df['market_value'] = positions_df['quantity'] * \
                positions_df['current_price']

            sector_exposure = positions_df.groupby(
                'sector')['market_value'].sum() / portfolio_value

            # Check if adding new position would exceed sector limit
            current_sector_exposure = sector_exposure.get(new_sector, 0)
            proposed_exposure = (
                current_sector_exposure * portfolio_value + new_position_value) / portfolio_value

            return proposed_exposure <= self.risk_limits['max_sector_exposure']

        return True

    def get_current_price(self, symbol):
        """Get current price for a symbol (simulated)"""
        # In reality, this would come from your market data feed
        price_map = {'AAPL': 175.0, 'GOOGL': 2400.0,
                     'MSFT': 310.0, 'TSLA': 210.0, 'AMZN': 3400.0}
        return price_map.get(symbol, 100.0)

    def calculate_position_size(self, symbol, stop_loss_price, entry_price):
        """Calculate optimal position size using risk-based methods"""
        portfolio_value = self.get_portfolio_value()
        max_risk_per_trade = portfolio_value * \
            self.risk_limits['max_daily_loss_percent'] / 3  # Conservative

        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share > 0:
            position_size = max_risk_per_trade / risk_per_share
        else:
            position_size = 0

        # Also check against maximum position size limit
        max_shares_by_value = (
            portfolio_value * self.risk_limits['max_position_size_percent']) / entry_price

        final_position_size = min(position_size, max_shares_by_value)

        logging.info(
            f"Calculated position size for {symbol}: {final_position_size:.2f} shares")
        return final_position_size

    def generate_stop_loss_orders(self):
        """Generate stop-loss orders for all open positions"""
        conn = sqlite3.connect(self.db_path)

        positions_df = pd.read_sql('''
            SELECT symbol, quantity, average_price
            FROM positions
            WHERE quantity > 0
        ''', conn)

        stop_orders = []

        for _, position in positions_df.iterrows():
            symbol = position['symbol']
            quantity = position['quantity']
            avg_price = position['average_price']
            current_price = self.get_current_price(symbol)

            # Calculate stop loss price
            if current_price >= avg_price:  # Profitable position - use trailing stop
                stop_price = current_price * \
                    (1 - self.risk_limits['trailing_stop_percent'])
            else:  # Losing position - use fixed stop loss
                stop_price = avg_price * \
                    (1 - self.risk_limits['stop_loss_percent'])

            stop_orders.append({
                'symbol': symbol,
                'quantity': quantity,
                'side': 'sell',
                'order_type': 'stop',
                'stop_price': round(stop_price, 2),
                'reason': 'Trailing stop' if current_price >= avg_price else 'Stop loss'
            })

        conn.close()
        return stop_orders

    def run_risk_checks(self):
        """Run comprehensive risk assessment"""
        risk_report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_metrics': self.get_portfolio_metrics(),
            'violations': self.check_risk_limits(),
            'recommendations': self.generate_risk_recommendations()
        }

        logging.info("Comprehensive risk assessment completed")
        return risk_report

    def get_portfolio_metrics(self):
        """Calculate key portfolio risk metrics"""
        portfolio_value = self.get_portfolio_value()

        conn = sqlite3.connect(self.db_path)

        # Calculate concentration metrics
        positions_df = pd.read_sql(
            'SELECT symbol, quantity, average_price FROM positions WHERE quantity > 0', conn)

        metrics = {
            'portfolio_value': portfolio_value,
            'position_count': len(positions_df),
            'max_single_position': 0,
            'sector_concentration': {},
            'total_leverage': 1.0  # Simplified
        }

        if not positions_df.empty:
            positions_df['current_price'] = positions_df['symbol'].apply(
                self.get_current_price)
            positions_df['market_value'] = positions_df['quantity'] * \
                positions_df['current_price']

            metrics['max_single_position'] = (
                positions_df['market_value'].max() / portfolio_value) * 100

        conn.close()
        return metrics

    def check_risk_limits(self):
        """Check for risk limit violations"""
        violations = []
        metrics = self.get_portfolio_metrics()

        if metrics['max_single_position'] > self.risk_limits['max_position_size_percent'] * 100:
            violations.append(
                f"Single position concentration: {metrics['max_single_position']:.1f}%")

        if not self.check_daily_loss_limit():
            violations.append("Daily loss limit exceeded")

        if not self.check_drawdown_limit():
            violations.append("Maximum drawdown limit exceeded")

        return violations

    def generate_risk_recommendations(self):
        """Generate risk mitigation recommendations"""
        recommendations = []
        stop_orders = self.generate_stop_loss_orders()

        if stop_orders:
            recommendations.append(
                f"Generate {len(stop_orders)} stop-loss orders for protection")

        metrics = self.get_portfolio_metrics()
        if metrics['position_count'] > 10:
            recommendations.append(
                "Consider reducing position count for better diversification")

        return recommendations


def main():
    # Initialize Risk Manager
    risk_manager = RiskManager()

    print("Risk Management System Demo")
    print("=" * 50)

    # Display risk limits
    print("Risk Limits Configuration:")
    for limit, value in risk_manager.risk_limits.items():
        if 'percent' in limit:
            print(f"  {limit}: {value * 100:.1f}%")
        else:
            print(f"  {limit}: {value}")

    # Run pre-trade risk checks
    print("Pre-Trade Risk Checks:")
    test_trades = [
        {'symbol': 'AAPL', 'quantity': 100, 'order_type': 'market', 'price': 175.0},
        {'symbol': 'GOOGL', 'quantity': 50, 'order_type': 'limit', 'price': 2400.0},
        {'symbol': 'TSLA', 'quantity': 200, 'order_type': 'market', 'price': 210.0}
    ]

    for trade in test_trades:
        risk_report = risk_manager.pre_trade_risk_check(**trade)
        print(
            f"\nTrade: {trade['quantity']} {trade['symbol']} {trade['order_type']}")
        print(
            f"Status: {'PASSED' if risk_report['checks_passed'] else 'FAILED'}")
        print(f"Portfolio Value: ${risk_report['portfolio_value']:,.2f}")
        print(
            f"Proposed Value: ${risk_report['proposed_position_value']:,.2f}")
        print(f"Max Allowed: ${risk_report['max_allowed_position']:,.2f}")

        if risk_report['failed_checks']:
            print(f"Failed Checks: {', '.join(risk_report['failed_checks'])}")

    # Calculate position sizing
    print("Position Sizing Examples:")
    sizing_examples = [
        {'symbol': 'AAPL', 'stop_loss': 165.0, 'entry_price': 175.0},
        {'symbol': 'GOOGL', 'stop_loss': 2300.0, 'entry_price': 2400.0}
    ]

    for example in sizing_examples:
        size = risk_manager.calculate_position_size(**example)
        print(f"{example['symbol']}: Optimal size = {size:.1f} shares")

    # Generate stop-loss orders
    print("Stop-Loss Order Generation:")
    stop_orders = risk_manager.generate_stop_loss_orders()
    for order in stop_orders[:3]:  # Show first 3
        print(
            f"{order['symbol']}: {order['reason']} at ${order['stop_price']:.2f}")

    # Comprehensive risk report
    print("Comprehensive Risk Report:")
    risk_report = risk_manager.run_risk_checks()

    print(
        f"Portfolio Value: ${risk_report['portfolio_metrics']['portfolio_value']:,.2f}")
    print(
        f"Position Count: {risk_report['portfolio_metrics']['position_count']}")
    print(
        f"Max Single Position: {risk_report['portfolio_metrics']['max_single_position']:.1f}%")

    if risk_report['violations']:
        print("Risk Limit Violations:")
        for violation in risk_report['violations']:
            print(f"  • {violation}")
    else:
        print("No risk limit violations detected")

    if risk_report['recommendations']:
        print("Risk Mitigation Recommendations:")
        for recommendation in risk_report['recommendations']:
            print(f"  • {recommendation}")


if __name__ == "__main__":
    main()
