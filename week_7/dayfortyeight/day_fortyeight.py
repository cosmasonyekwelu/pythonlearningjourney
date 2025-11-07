import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PortfolioRebalancer:
    def __init__(self, db_path='trading_system.db'):
        self.db_path = db_path
        self.rebalance_threshold = 0.05  # 5% deviation threshold
        self.target_allocations = self.load_target_allocations()

    def load_target_allocations(self):
        """Load target portfolio allocations"""
        return {
            'AAPL': 0.25,   # 25% Technology - Apple
            'GOOGL': 0.20,  # 20% Technology - Google
            'MSFT': 0.15,   # 15% Technology - Microsoft
            'TSLA': 0.10,   # 10% Automotive - Tesla
            'AMZN': 0.10,   # 10% Consumer - Amazon
            'JPM': 0.10,    # 10% Financial - JPMorgan
            'CASH': 0.10    # 10% Cash
        }

    def get_current_portfolio(self):
        """Get current portfolio holdings and values"""
        conn = sqlite3.connect(self.db_path)

        # Get current positions
        positions_df = pd.read_sql('''
            SELECT symbol, quantity, average_price
            FROM positions
            WHERE quantity > 0
        ''', conn)

        # Get current prices (simulated)
        if not positions_df.empty:
            positions_df['current_price'] = positions_df['symbol'].apply(
                self.get_current_price)
            positions_df['market_value'] = positions_df['quantity'] * \
                positions_df['current_price']

        conn.close()
        return positions_df

    def get_current_price(self, symbol):
        """Get current price for a symbol (simulated)"""
        price_map = {
            'AAPL': 175.0, 'GOOGL': 2400.0, 'MSFT': 310.0,
            'TSLA': 210.0, 'AMZN': 3400.0, 'JPM': 150.0
        }
        return price_map.get(symbol, 100.0)

    def calculate_current_allocations(self, portfolio_value):
        """Calculate current portfolio allocations"""
        current_positions = self.get_current_portfolio()

        if current_positions.empty:
            return {'CASH': 1.0}  # 100% cash if no positions

        allocations = {}

        for _, position in current_positions.iterrows():
            symbol = position['symbol']
            value = position['market_value']
            allocations[symbol] = value / portfolio_value

        # Add cash allocation (simplified)
        total_invested = sum(allocations.values())
        allocations['CASH'] = max(0, 1.0 - total_invested)

        return allocations

    def calculate_rebalance_trades(self, current_allocations, target_allocations, portfolio_value):
        """Calculate trades needed to rebalance portfolio"""
        trades = []
        cash_available = current_allocations.get('CASH', 0) * portfolio_value

        for symbol, target_weight in target_allocations.items():
            if symbol == 'CASH':
                continue

            current_weight = current_allocations.get(symbol, 0)
            deviation = current_weight - target_weight

            # Check if rebalancing is needed (exceeds threshold)
            if abs(deviation) > self.rebalance_threshold:
                current_value = current_weight * portfolio_value
                target_value = target_weight * portfolio_value
                value_difference = target_value - current_value

                current_price = self.get_current_price(symbol)

                if current_price > 0:
                    shares_to_trade = value_difference / current_price

                    if abs(shares_to_trade) >= 1:  # Only trade whole shares
                        trades.append({
                            'symbol': symbol,
                            'shares': abs(round(shares_to_trade)),
                            'side': 'buy' if shares_to_trade > 0 else 'sell',
                            'current_weight': current_weight,
                            'target_weight': target_weight,
                            'deviation': deviation,
                            'trade_value': abs(value_difference),
                            'current_price': current_price
                        })

        # Sort trades by deviation magnitude (largest deviations first)
        trades.sort(key=lambda x: abs(x['deviation']), reverse=True)

        return trades

    def check_rebalance_conditions(self):
        """Check if rebalancing conditions are met"""
        portfolio_value = self.calculate_portfolio_value()
        current_allocations = self.calculate_current_allocations(
            portfolio_value)

        # Calculate maximum deviation
        max_deviation = 0
        for symbol, target_weight in self.target_allocations.items():
            if symbol == 'CASH':
                continue
            current_weight = current_allocations.get(symbol, 0)
            deviation = abs(current_weight - target_weight)
            max_deviation = max(max_deviation, deviation)

        # Check threshold condition
        threshold_condition = max_deviation > self.rebalance_threshold

        # Check time-based condition (rebalance monthly)
        last_rebalance = self.get_last_rebalance_date()
        time_condition = (datetime.now() - last_rebalance) > timedelta(days=30)

        return {
            'should_rebalance': threshold_condition or time_condition,
            'max_deviation': max_deviation,
            'threshold_condition': threshold_condition,
            'time_condition': time_condition,
            'last_rebalance': last_rebalance
        }

    def calculate_portfolio_value(self):
        """Calculate total portfolio value"""
        current_positions = self.get_current_portfolio()

        if current_positions.empty:
            return 100000  # Default portfolio value

        total_value = current_positions['market_value'].sum()
        # Add cash (simplified - in reality, you'd have actual cash balance)
        total_value += 10000  # $10,000 cash

        return total_value

    def get_last_rebalance_date(self):
        """Get the last rebalance date (simulated)"""
        # In reality, this would come from your database
        # Simulate last rebalance 35 days ago
        return datetime.now() - timedelta(days=35)

    def simulate_rebalance(self, trades, portfolio_value):
        """Simulate the rebalance and calculate expected results"""
        simulated_allocations = self.calculate_current_allocations(
            portfolio_value).copy()
        total_trade_value = 0
        commission_cost = 0

        for trade in trades:
            symbol = trade['symbol']
            trade_value = trade['trade_value']
            current_weight = simulated_allocations.get(symbol, 0)

            if trade['side'] == 'buy':
                new_weight = current_weight + (trade_value / portfolio_value)
                simulated_allocations[symbol] = new_weight
                # Reduce cash
                simulated_allocations['CASH'] = max(0, simulated_allocations.get(
                    'CASH', 0) - (trade_value / portfolio_value))
            else:  # sell
                new_weight = current_weight - (trade_value / portfolio_value)
                simulated_allocations[symbol] = new_weight
                # Increase cash
                simulated_allocations['CASH'] = simulated_allocations.get(
                    'CASH', 0) + (trade_value / portfolio_value)

            total_trade_value += trade_value
            commission_cost += 1.0  # $1 per trade commission

        # Calculate improvement metrics
        improvement = self.calculate_allocation_improvement(
            simulated_allocations)

        return {
            'simulated_allocations': simulated_allocations,
            'total_trade_value': total_trade_value,
            'commission_cost': commission_cost,
            'improvement_score': improvement,
            'number_of_trades': len(trades)
        }

    def calculate_allocation_improvement(self, new_allocations):
        """Calculate how much closer the new allocations are to targets"""
        total_deviation_before = 0
        total_deviation_after = 0

        for symbol, target_weight in self.target_allocations.items():
            if symbol == 'CASH':
                continue
            current_weight = self.calculate_current_allocations(
                self.calculate_portfolio_value()).get(symbol, 0)
            new_weight = new_allocations.get(symbol, 0)

            total_deviation_before += abs(current_weight - target_weight)
            total_deviation_after += abs(new_weight - target_weight)

        if total_deviation_before > 0:
            improvement = (total_deviation_before -
                           total_deviation_after) / total_deviation_before * 100
        else:
            improvement = 0

        return improvement

    def generate_rebalance_plan(self):
        """Generate comprehensive rebalance plan"""
        portfolio_value = self.calculate_portfolio_value()
        current_allocations = self.calculate_current_allocations(
            portfolio_value)
        rebalance_conditions = self.check_rebalance_conditions()

        print("Rebalance Conditions Check:")
        print(
            f"  Maximum Deviation: {rebalance_conditions['max_deviation']*100:.1f}%")
        print(
            f"  Threshold Condition: {'MET' if rebalance_conditions['threshold_condition'] else 'Not Met'}")
        print(
            f"  Time Condition: {'MET' if rebalance_conditions['time_condition'] else 'Not Met'}")
        print(
            f"  Should Rebalance: {'YES' if rebalance_conditions['should_rebalance'] else 'NO'}")

        if not rebalance_conditions['should_rebalance']:
            return None

        trades = self.calculate_rebalance_trades(
            current_allocations, self.target_allocations, portfolio_value)
        simulation = self.simulate_rebalance(trades, portfolio_value)

        rebalance_plan = {
            'portfolio_value': portfolio_value,
            'current_allocations': current_allocations,
            'target_allocations': self.target_allocations,
            'trades': trades,
            'simulation': simulation,
            'timestamp': datetime.now().isoformat()
        }

        return rebalance_plan

    def execute_rebalance(self, rebalance_plan, execute_trades=False):
        """Execute the rebalance plan"""
        if not rebalance_plan:
            logging.info("No rebalance needed")
            return

        print(f"Rebalance Execution Plan")
        print("=" * 60)
        print(f"Portfolio Value: ${rebalance_plan['portfolio_value']:,.2f}")
        print(f"Number of Trades: {len(rebalance_plan['trades'])}")
        print(
            f"Total Trade Value: ${rebalance_plan['simulation']['total_trade_value']:,.2f}")
        print(
            f"Commission Cost: ${rebalance_plan['simulation']['commission_cost']:.2f}")
        print(
            f"Improvement Score: {rebalance_plan['simulation']['improvement_score']:.1f}%")

        print("Allocation Comparison:")
        print(f"{'Symbol':<8} {'Current':<8} {'Target':<8} {'New':<8} {'Action':<10}")
        print("-" * 50)

        for symbol in self.target_allocations.keys():
            current = rebalance_plan['current_allocations'].get(
                symbol, 0) * 100
            target = self.target_allocations[symbol] * 100
            new = rebalance_plan['simulation']['simulated_allocations'].get(
                symbol, 0) * 100

            action = "HOLD"
            for trade in rebalance_plan['trades']:
                if trade['symbol'] == symbol:
                    action = f"{trade['side'].upper()} {trade['shares']}"
                    break

            print(
                f"{symbol:<8} {current:>6.1f}% {target:>6.1f}% {new:>6.1f}% {action:<10}")

        print("Recommended Trades:")
        for i, trade in enumerate(rebalance_plan['trades'], 1):
            print(f"{i}. {trade['side'].upper()} {trade['shares']} {trade['symbol']} "
                  f"@ ${trade['current_price']:.2f} (${trade['trade_value']:.2f})")

        if execute_trades:
            print("Executing Trades...")
            # This would integrate with your Order Management System
            for trade in rebalance_plan['trades']:
                logging.info(
                    f"Executing: {trade['side']} {trade['shares']} {trade['symbol']}")
                # order_id = oms.create_order(...)
            print("Rebalance execution completed!")
        else:
            print(
                "Note: Trade execution is disabled. Set execute_trades=True to execute.")


def main():
    # Initialize Portfolio Rebalancer
    rebalancer = PortfolioRebalancer()

    print("Portfolio Rebalancing System")
    print("=" * 50)

    # Display target allocations
    print("Target Portfolio Allocations:")
    for symbol, weight in rebalancer.target_allocations.items():
        print(f"  {symbol}: {weight * 100:.1f}%")

    print(
        f"Rebalance Threshold: {rebalancer.rebalance_threshold * 100:.1f}%")

    # Generate rebalance plan
    rebalance_plan = rebalancer.generate_rebalance_plan()

    if rebalance_plan:
        # Execute the rebalance plan (simulation only - set execute_trades=True for real execution)
        rebalancer.execute_rebalance(rebalance_plan, execute_trades=False)

        # Show detailed allocation analysis
        print("Detailed Allocation Analysis:")
        portfolio_value = rebalance_plan['portfolio_value']

        for symbol in rebalancer.target_allocations.keys():
            if symbol == 'CASH':
                continue

            current = rebalance_plan['current_allocations'].get(symbol, 0)
            target = rebalancer.target_allocations[symbol]
            deviation = (current - target) * 100

            if abs(deviation) > rebalancer.rebalance_threshold * 100:
                status = "REBALANCE NEEDED"
            else:
                status = "WITHIN TOLERANCE"

            print(f"{symbol:<6}: Current {current*100:5.1f}% | Target {target*100:5.1f}% | "
                  f"Deviation {deviation:5.1f}% | {status}")

    else:
        print("Portfolio is within rebalance thresholds. No action needed.")

    # Show portfolio statistics
    print("Portfolio Statistics:")
    portfolio_value = rebalancer.calculate_portfolio_value()
    current_allocations = rebalancer.calculate_current_allocations(
        portfolio_value)

    print(f"Total Portfolio Value: ${portfolio_value:,.2f}")
    print(
        f"Number of Holdings: {len([k for k, v in current_allocations.items() if v > 0 and k != 'CASH'])}")
    print(f"Cash Allocation: {current_allocations.get('CASH', 0)*100:.1f}%")


if __name__ == "__main__":
    main()
