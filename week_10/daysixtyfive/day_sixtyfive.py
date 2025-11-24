
"""
Day 65: Crypto APIs & Data Feeds
Implementation of multi-exchange data aggregation and real-time market data processing
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Crypto data libraries
import ccxt
from websocket import create_connection, WebSocketConnectionClosedException
import websockets

class ExchangeDataManager:
    """Manage data from multiple cryptocurrency exchanges"""
    
    def __init__(self, exchange_ids: List[str]):
        self.exchanges = {}
        self.symbols = {}
        self.market_data = {}
        self.initialize_exchanges(exchange_ids)
    
    def initialize_exchanges(self, exchange_ids: List[str]) -> None:
        """Initialize exchange connections"""
        for exchange_id in exchange_ids:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class({
                    'rateLimit': 1000,
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                
                # Load markets
                markets = exchange.load_markets()
                self.exchanges[exchange_id] = exchange
                self.symbols[exchange_id] = list(markets.keys())[:50]  # Limit for demo
                
                print(f"Initialized {exchange_id} with {len(markets)} markets")
                
            except Exception as e:
                print(f"Failed to initialize {exchange_id}: {e}")
    
    def fetch_ohlcv_data(self, symbol: str, timeframe: str = '1h', 
                        since: Optional[int] = None, limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV data from all exchanges"""
        ohlcv_data = {}
        
        for exchange_id, exchange in self.exchanges.items():
            try:
                # Check if symbol is available on this exchange
                if symbol not in exchange.symbols:
                    continue
                
                # Fetch OHLCV data
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                ohlcv_data[exchange_id] = df
                print(f"Fetched {len(df)} {timeframe} candles for {symbol} from {exchange_id}")
                
            except Exception as e:
                print(f"Error fetching OHLCV from {exchange_id} for {symbol}: {e}")
        
        return ohlcv_data
    
    def fetch_order_books(self, symbol: str, limit: int = 20) -> Dict[str, Dict]:
        """Fetch order book data from all exchanges"""
        order_books = {}
        
        for exchange_id, exchange in self.exchanges.items():
            try:
                if symbol not in exchange.symbols:
                    continue
                
                order_book = exchange.fetch_order_book(symbol, limit)
                order_books[exchange_id] = order_book
                
                # Calculate spread
                best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
                best_ask = order_book['asks'][0][0] if order_book['asks'] else 0
                spread = (best_ask - best_bid) / best_bid * 100 if best_bid > 0 else 0
                
                print(f"Order book from {exchange_id}: Spread={spread:.4f}%, "
                      f"Bids={len(order_book['bids'])}, Asks={len(order_book['asks'])}")
                
            except Exception as e:
                print(f"Error fetching order book from {exchange_id}: {e}")
        
        return order_books
    
    def calculate_arbitrage_opportunities(self, symbol: str) -> List[Dict[str, Any]]:
        """Calculate arbitrage opportunities across exchanges"""
        opportunities = []
        
        try:
            # Get current prices from all exchanges
            prices = {}
            for exchange_id, exchange in self.exchanges.items():
                if symbol not in exchange.symbols:
                    continue
                
                ticker = exchange.fetch_ticker(symbol)
                prices[exchange_id] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last']
                }
            
            # Find arbitrage opportunities
            exchanges = list(prices.keys())
            for i, exchange1 in enumerate(exchanges):
                for exchange2 in exchanges[i+1:]:
                    price1 = prices[exchange1]
                    price2 = prices[exchange2]
                    
                    # Calculate potential arbitrage
                    if price1['bid'] > price2['ask']:
                        spread = (price1['bid'] - price2['ask']) / price2['ask'] * 100
                        opportunities.append({
                            'buy_exchange': exchange2,
                            'sell_exchange': exchange1,
                            'buy_price': price2['ask'],
                            'sell_price': price1['bid'],
                            'spread_percent': spread,
                            'symbol': symbol,
                            'timestamp': datetime.now()
                        })
                    
                    elif price2['bid'] > price1['ask']:
                        spread = (price2['bid'] - price1['ask']) / price1['ask'] * 100
                        opportunities.append({
                            'buy_exchange': exchange1,
                            'sell_exchange': exchange2,
                            'buy_price': price1['ask'],
                            'sell_price': price2['bid'],
                            'spread_percent': spread,
                            'symbol': symbol,
                            'timestamp': datetime.now()
                        })
        
        except Exception as e:
            print(f"Error calculating arbitrage: {e}")
        
        return opportunities

class WebSocketManager:
    """Manage real-time WebSocket connections"""
    
    def __init__(self):
        self.connections = {}
        self.data_buffer = {}
        self.callbacks = {}
    
    async def connect_binance(self, symbols: List[str]) -> None:
        """Connect to Binance WebSocket"""
        base_url = "wss://stream.binance.com:9443/ws/"
        
        for symbol in symbols:
            stream_name = f"{symbol.lower()}@ticker"
            url = base_url + stream_name
            
            try:
                websocket = await websockets.connect(url)
                self.connections[f"binance_{symbol}"] = websocket
                self.data_buffer[f"binance_{symbol}"] = []
                
                print(f"Connected to Binance WebSocket for {symbol}")
                
                # Start listening
                asyncio.create_task(self._listen_binance(websocket, symbol))
                
            except Exception as e:
                print(f"Failed to connect to Binance WebSocket for {symbol}: {e}")
    
    async def _listen_binance(self, websocket, symbol: str) -> None:
        """Listen to Binance WebSocket messages"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Process ticker data
                ticker_data = {
                    'symbol': symbol,
                    'exchange': 'binance',
                    'timestamp': datetime.now(),
                    'price': float(data.get('c', 0)),
                    'volume': float(data.get('v', 0)),
                    'price_change': float(data.get('p', 0)),
                    'price_change_percent': float(data.get('P', 0)),
                    'high': float(data.get('h', 0)),
                    'low': float(data.get('l', 0)),
                    'open': float(data.get('o', 0))
                }
                
                self.data_buffer[f"binance_{symbol}"].append(ticker_data)
                
                # Keep only recent data
                if len(self.data_buffer[f"binance_{symbol}"]) > 1000:
                    self.data_buffer[f"binance_{symbol}"] = self.data_buffer[f"binance_{symbol}"][-500:]
                
                # Execute callback if registered
                if 'binance' in self.callbacks:
                    await self.callbacks['binance'](ticker_data)
        
        except Exception as e:
            print(f"Error in Binance WebSocket for {symbol}: {e}")
    
    def register_callback(self, exchange: str, callback) -> None:
        """Register callback for real-time data"""
        self.callbacks[exchange] = callback
    
    def get_recent_data(self, exchange: str, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent WebSocket data"""
        key = f"{exchange}_{symbol}"
        if key in self.data_buffer:
            return self.data_buffer[key][-limit:]
        return []
    
    async def close_all(self) -> None:
        """Close all WebSocket connections"""
        for connection in self.connections.values():
            await connection.close()
        self.connections.clear()

class OnChainAnalyzer:
    """Analyze on-chain data for trading signals"""
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
        self.metrics = {}
    
    def calculate_network_metrics(self, transaction_data: List[Dict]) -> Dict[str, float]:
        """Calculate network health metrics"""
        if not transaction_data:
            return {}
        
        # Calculate basic metrics
        volumes = [tx.get('value', 0) for tx in transaction_data]
        fees = [tx.get('gas', 0) * tx.get('gasPrice', 0) for tx in transaction_data]
        
        metrics = {
            'daily_transactions': len(transaction_data),
            'total_volume': sum(volumes),
            'average_transaction_value': np.mean(volumes) if volumes else 0,
            'median_transaction_value': np.median(volumes) if volumes else 0,
            'total_fees': sum(fees),
            'average_fee': np.mean(fees) if fees else 0,
            'network_congestion': len([f for f in fees if f > np.median(fees) * 2]) / len(fees) if fees else 0
        }
        
        return metrics
    
    def detect_whale_movements(self, transactions: List[Dict], threshold: float = 1000000) -> List[Dict]:
        """Detect large whale movements"""
        whale_txs = []
        
        for tx in transactions:
            value = tx.get('value', 0)
            if value >= threshold:
                whale_txs.append({
                    'hash': tx.get('hash', ''),
                    'from': tx.get('from', ''),
                    'to': tx.get('to', ''),
                    'value': value,
                    'timestamp': tx.get('timestamp', ''),
                    'type': 'WHALE_MOVEMENT'
                })
        
        return whale_txs
    
    def calculate_exchange_flows(self, transactions: List[Dict], 
                               exchange_addresses: List[str]) -> Dict[str, float]:
        """Calculate net flows to/from exchanges"""
        exchange_flows = {addr: 0.0 for addr in exchange_addresses}
        
        for tx in transactions:
            from_addr = tx.get('from', '')
            to_addr = tx.get('to', '')
            value = tx.get('value', 0)
            
            # Check if transaction involves exchange
            if from_addr in exchange_addresses:
                exchange_flows[from_addr] -= value
            if to_addr in exchange_addresses:
                exchange_flows[to_addr] += value
        
        return exchange_flows

class DataVisualizer:
    """Visualize cryptocurrency market data"""
    
    @staticmethod
    def plot_ohlcv_comparison(ohlcv_data: Dict[str, pd.DataFrame], symbol: str) -> None:
        """Plot OHLCV data comparison across exchanges"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'OHLCV Comparison for {symbol}', fontsize=16)
        
        # Plot closing prices
        axes[0, 0].set_title('Closing Prices')
        for exchange, data in ohlcv_data.items():
            axes[0, 0].plot(data.index, data['close'], label=exchange, alpha=0.7)
        axes[0, 0].set_ylabel('Price')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot volumes
        axes[0, 1].set_title('Trading Volume')
        for exchange, data in ohlcv_data.items():
            axes[0, 1].plot(data.index, data['volume'], label=exchange, alpha=0.7)
        axes[0, 1].set_ylabel('Volume')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot price differences
        axes[1, 0].set_title('Price Differences (%)')
        exchanges = list(ohlcv_data.keys())
        if len(exchanges) >= 2:
            base_exchange = exchanges[0]
            base_data = ohlcv_data[base_exchange]
            
            for exchange in exchanges[1:]:
                compare_data = ohlcv_data[exchange]
                # Align data
                common_index = base_data.index.intersection(compare_data.index)
                if len(common_index) > 0:
                    price_diff = ((compare_data.loc[common_index, 'close'] - 
                                 base_data.loc[common_index, 'close']) / 
                                base_data.loc[common_index, 'close'] * 100)
                    axes[1, 0].plot(common_index, price_diff, label=f'{exchange} vs {base_exchange}')
            
            axes[1, 0].set_ylabel('Price Difference (%)')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
        
        # Plot volatility
        axes[1, 1].set_title('Rolling Volatility (20 periods)')
        for exchange, data in ohlcv_data.items():
            returns = data['close'].pct_change()
            volatility = returns.rolling(window=20).std() * np.sqrt(365)  # Annualized
            axes[1, 1].plot(data.index, volatility, label=exchange, alpha=0.7)
        axes[1, 1].set_ylabel('Annualized Volatility')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(f'crypto_data_comparison_{symbol.replace("/", "_")}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_arbitrage_opportunities(opportunities: List[Dict]) -> None:
        """Plot arbitrage opportunities over time"""
        if not opportunities:
            print("No arbitrage opportunities to plot")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(opportunities)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        plt.figure(figsize=(12, 6))
        
        # Group by symbol and plot spread
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol]
            plt.plot(symbol_data.index, symbol_data['spread_percent'], 
                    label=symbol, marker='o', markersize=3, alpha=0.7)
        
        plt.title('Arbitrage Opportunities Over Time')
        plt.xlabel('Time')
        plt.ylabel('Spread (%)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('arbitrage_opportunities.png', dpi=300, bbox_inches='tight')
        plt.show()

async def main():
    """Main function to demonstrate crypto data aggregation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto APIs & Data Feeds')
    parser.add_argument('--exchanges', nargs='+', default=['binance', 'coinbasepro', 'kraken'],
                       help='Exchanges to connect to')
    parser.add_argument('--symbols', nargs='+', default=['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
                       help='Trading symbols to monitor')
    parser.add_argument('--fetch_historical', action='store_true', help='Fetch historical data')
    parser.add_argument('--real_time', action='store_true', help='Enable real-time data')
    parser.add_argument('--analyze_arbitrage', action='store_true', help='Analyze arbitrage opportunities')
    
    args = parser.parse_args()
    
    print("="*80)
    print("CRYPTO APIS & DATA FEEDS - DAY 65")
    print("="*80)
    
    # Initialize exchange data manager
    exchange_manager = ExchangeDataManager(args.exchanges)
    websocket_manager = WebSocketManager()
    onchain_analyzer = OnChainAnalyzer()
    visualizer = DataVisualizer()
    
    try:
        if args.fetch_historical:
            print("\n1. HISTORICAL DATA FETCHING")
            print("-" * 40)
            
            for symbol in args.symbols:
                print(f"\nFetching historical data for {symbol}...")
                
                # Fetch OHLCV data
                ohlcv_data = exchange_manager.fetch_ohlcv_data(symbol, '1h', limit=500)
                
                if ohlcv_data:
                    # Plot comparison
                    visualizer.plot_ohlcv_comparison(ohlcv_data, symbol)
                    
                    # Display summary statistics
                    for exchange, data in ohlcv_data.items():
                        returns = data['close'].pct_change().dropna()
                        print(f"{exchange} - {symbol}:")
                        print(f"  Period: {data.index[0]} to {data.index[-1]}")
                        print(f"  Total Return: {(data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100:.2f}%")
                        print(f"  Volatility: {returns.std() * np.sqrt(365) * 100:.2f}%")
                        print(f"  Sharpe Ratio: {returns.mean() / returns.std() * np.sqrt(365) if returns.std() > 0 else 0:.2f}")
        
        if args.analyze_arbitrage:
            print("\n2. ARBITRAGE ANALYSIS")
            print("-" * 40)
            
            all_opportunities = []
            for symbol in args.symbols:
                opportunities = exchange_manager.calculate_arbitrage_opportunities(symbol)
                all_opportunities.extend(opportunities)
                
                if opportunities:
                    print(f"\nArbitrage opportunities for {symbol}:")
                    for opp in opportunities:
                        print(f"  Buy on {opp['buy_exchange']} at {opp['buy_price']:.2f}, "
                              f"Sell on {opp['sell_exchange']} at {opp['sell_price']:.2f}, "
                              f"Spread: {opp['spread_percent']:.4f}%")
                else:
                    print(f"No arbitrage opportunities found for {symbol}")
            
            # Plot arbitrage opportunities
            if all_opportunities:
                visualizer.plot_arbitrage_opportunities(all_opportunities)
        
        if args.real_time:
            print("\n3. REAL-TIME DATA STREAMING")
            print("-" * 40)
            
            # WebSocket callback function
            async def handle_realtime_data(data):
                print(f"Real-time update - {data['symbol']}: ${data['price']:.2f} "
                      f"({data['price_change_percent']:+.2f}%)")
            
            # Connect to WebSocket
            websocket_manager.register_callback('binance', handle_realtime_data)
            await websocket_manager.connect_binance(args.symbols)
            
            # Keep running for a while to collect data
            print("Collecting real-time data for 30 seconds...")
            await asyncio.sleep(30)
            
            # Display collected data
            for symbol in args.symbols:
                recent_data = websocket_manager.get_recent_data('binance', symbol, 5)
                if recent_data:
                    print(f"\nRecent data for {symbol}:")
                    for data_point in recent_data:
                        print(f"  {data_point['timestamp'].strftime('%H:%M:%S')}: "
                              f"${data_point['price']:.2f}")
        
        print("\n4. ORDER BOOK ANALYSIS")
        print("-" * 40)
        
        for symbol in args.symbols[:1]:  # Analyze first symbol only for demo
            order_books = exchange_manager.fetch_order_books(symbol)
            
            if order_books:
                print(f"\nOrder Book Analysis for {symbol}:")
                for exchange, book in order_books.items():
                    if book['bids'] and book['asks']:
                        mid_price = (book['bids'][0][0] + book['asks'][0][0]) / 2
                        spread = (book['asks'][0][0] - book['bids'][0][0]) / mid_price * 100
                        total_bid_volume = sum([bid[1] for bid in book['bids']])
                        total_ask_volume = sum([ask[1] for ask in book['asks']])
                        
                        print(f"  {exchange}:")
                        print(f"    Mid Price: ${mid_price:.2f}")
                        print(f"    Spread: {spread:.4f}%")
                        print(f"    Bid/Ask Volume: {total_bid_volume:.2f}/{total_ask_volume:.2f}")
                        print(f"    Order Imbalance: {(total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) * 100:.2f}%")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        await websocket_manager.close_all()
    
    print("\n" + "="*80)
    print("Crypto APIs & Data Feeds demonstration completed!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
