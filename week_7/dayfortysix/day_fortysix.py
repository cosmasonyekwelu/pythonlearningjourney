import sqlite3
import threading
import time
import json
import requests
from datetime import datetime, timedelta
import logging
from queue import Queue
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class OrderManagementSystem:
    def __init__(self, db_path='trading_system.db'):
        self.db_path = db_path
        self.order_queue = Queue()
        self.is_running = False
        self.sync_interval = 30  # seconds
        self.init_database()

    def init_database(self):
        """Initialize the database with orders and positions tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                order_type TEXT NOT NULL,
                limit_price REAL,
                stop_price REAL,
                status TEXT NOT NULL,
                filled_quantity REAL DEFAULT 0,
                average_fill_price REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                broker_order_id TEXT,
                error_message TEXT
            )
        ''')

        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Order events table for audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logging.info("Database initialized successfully")

    def create_order(self, symbol, quantity, side, order_type, limit_price=None, stop_price=None):
        """Create a new order and add to queue"""
        order_id = f"ORD_{int(time.time())}_{symbol}"

        order = {
            'order_id': order_id,
            'symbol': symbol,
            'side': side,  # 'buy' or 'sell'
            'quantity': quantity,
            'order_type': order_type,  # 'market', 'limit', 'stop', 'stop_limit'
            'limit_price': limit_price,
            'stop_price': stop_price,
            'status': 'PENDING',
            'created_at': datetime.now().isoformat()
        }

        # Save to database
        self.save_order_to_db(order)

        # Add to processing queue
        self.order_queue.put(order)

        # Log order event
        self.log_order_event(order_id, 'CREATED', 'Order created and queued')

        logging.info(f"Order created: {order_id} - {side} {quantity} {symbol}")
        return order_id

    def save_order_to_db(self, order):
        """Save order to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (order_id, symbol, side, quantity, order_type, limit_price, stop_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order['order_id'], order['symbol'], order['side'], order['quantity'],
            order['order_type'], order['limit_price'], order['stop_price'], order['status']
        ))

        conn.commit()
        conn.close()

    def update_order_status(self, order_id, status, filled_quantity=0, avg_fill_price=0, broker_order_id=None, error_msg=None):
        """Update order status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE orders 
            SET status = ?, filled_quantity = ?, average_fill_price = ?, 
                broker_order_id = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        ''', (status, filled_quantity, avg_fill_price, broker_order_id, error_msg, order_id))

        conn.commit()
        conn.close()

        # Log status change event
        self.log_order_event(order_id, 'STATUS_UPDATE',
                             f"Status changed to {status}")

        logging.info(f"Order {order_id} status updated to {status}")

    def log_order_event(self, order_id, event_type, event_data):
        """Log order event for audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO order_events (order_id, event_type, event_data)
            VALUES (?, ?, ?)
        ''', (order_id, event_type, json.dumps(event_data) if isinstance(event_data, dict) else event_data))

        conn.commit()
        conn.close()

    def process_order(self, order):
        """Simulate order processing with broker API"""
        try:
            # Simulate API call to broker
            logging.info(f"Processing order: {order['order_id']}")

            # Update status to submitted
            self.update_order_status(order['order_id'], 'SUBMITTED')

            # Simulate processing delay
            time.sleep(2)

            # Simulate different outcomes
            import random
            outcome = random.choice(['FILLED', 'PARTIALLY_FILLED', 'REJECTED'])

            if outcome == 'FILLED':
                # Simulate fill price (for market orders, use current price + slight variation)
                fill_price = order.get(
                    'limit_price') or 150.0 + random.uniform(-2, 2)
                self.update_order_status(
                    order['order_id'], 'FILLED',
                    filled_quantity=order['quantity'],
                    avg_fill_price=fill_price,
                    broker_order_id=f"BROKER_{order['order_id']}"
                )
                self.update_positions(order, fill_price)

            elif outcome == 'PARTIALLY_FILLED':
                filled_qty = order['quantity'] * 0.7  # 70% filled
                fill_price = order.get(
                    'limit_price') or 150.0 + random.uniform(-2, 2)
                self.update_order_status(
                    order['order_id'], 'PARTIALLY_FILLED',
                    filled_quantity=filled_qty,
                    avg_fill_price=fill_price,
                    broker_order_id=f"BROKER_{order['order_id']}"
                )
                # Update positions with partial fill
                partial_order = order.copy()
                partial_order['quantity'] = filled_qty
                self.update_positions(partial_order, fill_price)

            else:  # REJECTED
                self.update_order_status(
                    order['order_id'], 'REJECTED',
                    error_msg="Insufficient funds"
                )

        except Exception as e:
            logging.error(
                f"Error processing order {order['order_id']}: {str(e)}")
            self.update_order_status(
                order['order_id'], 'ERROR',
                error_msg=str(e)
            )

    def update_positions(self, order, fill_price):
        """Update positions based on filled order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if position exists for symbol
        cursor.execute(
            'SELECT * FROM positions WHERE symbol = ?', (order['symbol'],))
        existing_position = cursor.fetchone()

        if existing_position:
            # Update existing position
            if order['side'] == 'buy':
                new_quantity = existing_position[2] + order['quantity']
                new_avg_price = ((existing_position[2] * existing_position[3]) +
                                 (order['quantity'] * fill_price)) / new_quantity
            else:  # sell
                new_quantity = existing_position[2] - order['quantity']
                # Keep same avg price for remaining
                new_avg_price = existing_position[3]

            if new_quantity == 0:
                # Close position
                cursor.execute(
                    'DELETE FROM positions WHERE symbol = ?', (order['symbol'],))
            else:
                cursor.execute('''
                    UPDATE positions 
                    SET quantity = ?, average_price = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE symbol = ?
                ''', (new_quantity, new_avg_price, order['symbol']))
        else:
            # Create new position (only for buys)
            if order['side'] == 'buy':
                cursor.execute('''
                    INSERT INTO positions (symbol, quantity, average_price)
                    VALUES (?, ?, ?)
                ''', (order['symbol'], order['quantity'], fill_price))

        conn.commit()
        conn.close()
        logging.info(f"Positions updated for {order['symbol']}")

    def start_order_processor(self):
        """Start the order processing thread"""
        self.is_running = True

        def processor():
            while self.is_running:
                try:
                    # Process orders from queue
                    if not self.order_queue.empty():
                        order = self.order_queue.get(timeout=1)
                        self.process_order(order)
                        self.order_queue.task_done()
                    else:
                        time.sleep(0.1)  # Small delay when queue is empty
                except Exception as e:
                    logging.error(f"Error in order processor: {str(e)}")
                    time.sleep(1)

        self.processor_thread = threading.Thread(target=processor, daemon=True)
        self.processor_thread.start()
        logging.info("Order processor started")

    def stop_order_processor(self):
        """Stop the order processing thread"""
        self.is_running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5)
        logging.info("Order processor stopped")

    def sync_with_broker(self):
        """Simulate syncing orders with broker API"""
        logging.info("Syncing orders with broker...")
        # In real implementation, this would call broker API to get latest status
        time.sleep(1)
        logging.info("Order sync completed")

    def get_order_summary(self):
        """Get summary of all orders"""
        conn = sqlite3.connect(self.db_path)

        # Get orders summary
        orders_df = pd.read_sql('''
            SELECT status, COUNT(*) as count, SUM(quantity) as total_quantity
            FROM orders 
            GROUP BY status
        ''', conn)

        # Get recent orders
        recent_orders = pd.read_sql('''
            SELECT order_id, symbol, side, quantity, order_type, status, created_at
            FROM orders 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', conn)

        # Get positions
        positions_df = pd.read_sql('SELECT * FROM positions', conn)

        conn.close()

        return {
            'orders_summary': orders_df,
            'recent_orders': recent_orders,
            'positions': positions_df
        }


def main():
    # Initialize Order Management System
    oms = OrderManagementSystem()

    # Start order processor
    oms.start_order_processor()

    try:
        print("Order Management System Demo")
        print("=" * 50)

        # Create sample orders
        sample_orders = [
            {'symbol': 'AAPL', 'quantity': 10,
                'side': 'buy', 'order_type': 'market'},
            {'symbol': 'GOOGL', 'quantity': 5, 'side': 'buy',
                'order_type': 'limit', 'limit_price': 2400},
            {'symbol': 'AAPL', 'quantity': 5,
                'side': 'sell', 'order_type': 'market'},
            {'symbol': 'MSFT', 'quantity': 8, 'side': 'buy',
                'order_type': 'stop', 'stop_price': 300},
        ]

        print("Creating sample orders...")
        for order_params in sample_orders:
            order_id = oms.create_order(**order_params)
            print(f"Created: {order_id}")

        # Wait for orders to process
        print("Processing orders...")
        time.sleep(10)

        # Get and display summary
        print("System Summary:")
        summary = oms.get_order_summary()

        print("\nOrders Summary:")
        print(summary['orders_summary'].to_string(index=False))

        print("\nRecent Orders:")
        print(summary['recent_orders'].to_string(index=False))

        print("\nCurrent Positions:")
        if not summary['positions'].empty:
            print(summary['positions'].to_string(index=False))
        else:
            print("No positions")

        # Show order events for first order
        conn = sqlite3.connect('trading_system.db')
        events = pd.read_sql('''
            SELECT order_id, event_type, event_data, created_at 
            FROM order_events 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', conn)
        conn.close()

        print("Recent Order Events:")
        print(events.to_string(index=False))

    finally:
        # Cleanup
        oms.stop_order_processor()


if __name__ == "__main__":
    main()
