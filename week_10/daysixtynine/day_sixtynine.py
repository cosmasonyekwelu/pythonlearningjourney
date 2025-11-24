
"""
Day 69: Crypto Trading Strategies
Implementation of cryptocurrency-specific quantitative trading strategies
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Trading and quantitative libraries
import vectorbt as vbt
from scipy import stats
from scipy.optimize import minimize
import talib

# Crypto data libraries
import ccxt
from web3 import Web3

@dataclass
class TradingSignal:
    """Trading signal representation"""
    symbol: str
    timestamp: datetime
    signal_type: str  # 'LONG', 'SHORT', 'EXIT'
    strength: float
    price: float
    confidence: float

@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_return: float

class CryptoDataManager:
    """Manager for cryptocurrency data acquisition and processing"""
    
    def __init__(self):
        self.exchanges = {}
        self.initialize_exchanges()
    
    def initialize_exchanges(self):
        """Initialize exchange connections"""
        self.exchanges['binance'] = ccxt.binance({
            'rateLimit': 1000,
            'enableRateLimit': True,
        })
    
    def fetch_ohlcv_data(self, symbol: str, timeframe: str = '1h', 
                        since: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
        """Fetch OHLCV data"""
        try:
            ohlcv = self.exchanges['binance'].fetch_ohlcv(symbol, timeframe, since, limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_symbols(self, symbols: List[str], timeframe: str = '1h', 
                              lookback_days: int = 365) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols"""
        data = {}
        since = self.exchanges['binance'].parse8601(
            (datetime.now() - timedelta(days=lookback_days)).isoformat()
        )
        
        for symbol in symbols:
            df = self.fetch_ohlcv_data(symbol, timeframe, since)
            if not df.empty:
                data[symbol] = df
                print(f"Fetched {len(df)} bars for {symbol}")
        
        return data

class OnChainAnalyzer:
    """Analyze on-chain data for trading signals"""
    
    def __init__(self, web3_provider: str = None):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider)) if web3_provider else None
    
    def calculate_nvt_ratio(self, market_cap: float, transaction_volume: float) -> float:
        """Calculate NVT (Network Value to Transactions) ratio"""
        if transaction_volume == 0:
            return float('inf')
        return market_cap / transaction_volume
    
    def calculate_mvrv_ratio(self, market_cap: float, realized_cap: float) -> float:
        """Calculate MVRV (Market Value to Realized Value) ratio"""
        if realized_cap == 0:
            return float('inf')
        return market_cap / realized_cap
    
    def detect_whale_movements(self, transactions: List[Dict], 
                             threshold: float = 1000000) -> List[Dict]:
        """Detect large whale movements"""
        whale_txs = []
        for tx in transactions:
            if tx.get('value', 0) >= threshold:
                whale_txs.append(tx)
        return whale_txs
    
    def analyze_exchange_flows(self, transactions: List[Dict],
                             exchange_addresses: List[str]) -> Dict[str, float]:
        """Analyze net flows to/from exchanges"""
        flows = {addr: 0.0 for addr in exchange_addresses}
        for tx in transactions:
            from_addr = tx.get('from', '')
            to_addr = tx.get('to', '')
            value = tx.get('value', 0)
            
            if from_addr in exchange_addresses:
                flows[from_addr] -= value
            if to_addr in exchange_addresses:
                flows[to_addr] += value
        
        return flows

class TechnicalStrategy:
    """Technical analysis-based trading strategies"""
    
    @staticmethod
    def momentum_strategy(df: pd.DataFrame, fast_period: int = 10, 
                         slow_period: int = 30) -> pd.Series:
        """Dual moving average momentum strategy"""
        fast_ma = df['close'].rolling(window=fast_period).mean()
        slow_ma = df['close'].rolling(window=slow_period).mean()
        
        # Generate signals: 1 for long, -1 for short, 0 for neutral
        signals = np.where(fast_ma > slow_ma, 1, -1)
        return pd.Series(signals, index=df.index)
    
    @staticmethod
    def mean_reversion_strategy(df: pd.DataFrame, period: int = 20, 
                              std_dev: float = 2.0) -> pd.Series:
        """Bollinger Bands mean reversion strategy"""
        middle_band = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        signals = np.zeros(len(df))
        signals[df['close'] < lower_band] = 1  # Buy signal
        signals[df['close'] > upper_band] = -1  # Sell signal
        
        return pd.Series(signals, index=df.index)
    
    @staticmethod
    def rsi_strategy(df: pd.DataFrame, period: int = 14, 
                    oversold: int = 30, overbought: int = 70) -> pd.Series:
        """RSI-based momentum strategy"""
        rsi = talib.RSI(df['close'], timeperiod=period)
        
        signals = np.zeros(len(df))
        signals[rsi < oversold] = 1  # Buy signal
        signals[rsi > overbought] = -1  # Sell signal
        
        return pd.Series(signals, index=df.index)

class StatisticalArbitrage:
    """Statistical arbitrage strategies"""
    
    @staticmethod
    def find_cointegrated_pairs(data: Dict[str, pd.DataFrame]) -> List[Tuple[str, str, float]]:
        """Find cointegrated pairs using Engle-Granger test"""
        cointegrated_pairs = []
        symbols = list(data.keys())
        
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                # Align data
                df1 = data[sym1]['close'].dropna()
                df2 = data[sym2]['close'].dropna()
                common_index = df1.index.intersection(df2.index)
                
                if len(common_index) > 100:  # Minimum data points
                    x = df1.loc[common_index]
                    y = df2.loc[common_index]
                    
                    # Test for cointegration
                    score, pvalue, _ = stats.coint(x, y)
                    
                    if pvalue < 0.05:  # Significant cointegration
                        cointegrated_pairs.append((sym1, sym2, pvalue))
        
        return sorted(cointegrated_pairs, key=lambda x: x[2])
    
    @staticmethod
    def calculate_hedge_ratio(x: pd.Series, y: pd.Series) -> float:
        """Calculate optimal hedge ratio using OLS"""
        # y = beta * x + alpha
        beta = np.cov(y, x)[0, 1] / np.var(x)
        return beta
    
    @staticmethod
    def generate_pairs_signals(df1: pd.Series, df2: pd.Series, 
                             lookback: int = 20) -> pd.Series:
        """Generate pairs trading signals"""
        # Calculate spread
        hedge_ratio = StatisticalArbitrage.calculate_hedge_ratio(df1, df2)
        spread = df2 - (hedge_ratio * df1)
        
        # Z-score normalization
        spread_mean = spread.rolling(window=lookback).mean()
        spread_std = spread.rolling(window=lookback).std()
        z_score = (spread - spread_mean) / spread_std
        
        # Generate signals
        signals = np.zeros(len(z_score))
        signals[z_score > 2] = -1  # Short spread (buy df1, sell df2)
        signals[z_score < -2] = 1  # Long spread (sell df1, buy df2)
        signals[abs(z_score) < 0.5] = 0  # Exit position
        
        return pd.Series(signals, index=df1.index)

class OnChainStrategy:
    """On-chain data based strategies"""
    
    @staticmethod
    def whale_accumulation_strategy(whale_transactions: List[Dict],
                                  price_data: pd.DataFrame) -> pd.Series:
        """Strategy based on whale accumulation patterns"""
        # Convert whale transactions to DataFrame
        whale_df = pd.DataFrame(whale_transactions)
        if whale_df.empty:
            return pd.Series(index=price_data.index, data=0)
        
        whale_df['timestamp'] = pd.to_datetime(whale_df['timestamp'])
        whale_df.set_index('timestamp', inplace=True)
        
        # Calculate daily whale net flow
        daily_flow = whale_df['value'].resample('D').sum()
        
        # Align with price data
        aligned_flow = daily_flow.reindex(price_data.index, method='ffill')
        
        # Generate signals based on whale accumulation
        signals = np.where(aligned_flow > 0, 1, 0)
        return pd.Series(signals, index=price_data.index)
    
    @staticmethod
    def network_health_strategy(nvt_ratio: pd.Series, mvrv_ratio: pd.Series,
                              price_data: pd.DataFrame) -> pd.Series:
        """Strategy based on network health metrics"""
        # Normalize metrics
        nvt_z = (nvt_ratio - nvt_ratio.rolling(30).mean()) / nvt_ratio.rolling(30).std()
        mvrv_z = (mvrv_ratio - mvrv_ratio.rolling(30).mean()) / mvrv_ratio.rolling(30).std()
        
        # Combined signal (simplified)
        combined_signal = (nvt_z + mvrv_z) / 2
        
        # Generate trading signals
        signals = np.zeros(len(combined_signal))
        signals[combined_signal < -1] = 1  # Buy when metrics are low
        signals[combined_signal > 1] = -1  # Sell when metrics are high
        
        return pd.Series(signals, index=price_data.index)

class BacktestEngine:
    """Backtesting engine for crypto strategies"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.results = {}
    
    def run_backtest(self, df: pd.DataFrame, signals: pd.Series, 
                    strategy_name: str) -> StrategyPerformance:
        """Run backtest for a single strategy"""
        try:
            # Clean signals
            signals = signals.replace(0, np.nan).ffill().fillna(0)
            
            # Create portfolio using vectorbt
            portfolio = vbt.Portfolio.from_orders(
                close=df['close'],
                entries=signals == 1,
                exits=signals == -1,
                init_cash=self.initial_capital,
                fees=0.001,  # 0.1% trading fees
                freq='1h'
            )
            
            # Calculate performance metrics
            stats = portfolio.stats()
            
            performance = StrategyPerformance(
                total_return=stats['Total Return [%]'],
                sharpe_ratio=stats['Sharpe Ratio'],
                max_drawdown=stats['Max Drawdown [%]'],
                win_rate=stats['Win Rate [%]'],
                profit_factor=stats['Profit Factor'],
                total_trades=stats['Total Trades'],
                avg_trade_return=stats['Avg Trade Return [%]']
            )
            
            self.results[strategy_name] = {
                'performance': performance,
                'portfolio': portfolio
            }
            
            return performance
        
        except Exception as e:
            print(f"Backtest failed for {strategy_name}: {e}")
            return StrategyPerformance(0, 0, 0, 0, 0, 0, 0)
    
    def compare_strategies(self) -> pd.DataFrame:
        """Compare performance of all tested strategies"""
        comparison_data = []
        
        for strategy_name, result in self.results.items():
            perf = result['performance']
            comparison_data.append({
                'Strategy': strategy_name,
                'Total Return (%)': perf.total_return,
                'Sharpe Ratio': perf.sharpe_ratio,
                'Max Drawdown (%)': perf.max_drawdown,
                'Win Rate (%)': perf.win_rate,
                'Profit Factor': perf.profit_factor,
                'Total Trades': perf.total_trades
            })
        
        return pd.DataFrame(comparison_data)

class RiskManager:
    """Risk management for crypto trading"""
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return returns.quantile(1 - confidence_level)
    
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk"""
        var = RiskManager.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def calculate_position_size(account_size: float, risk_per_trade: float,
                              entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = account_size * risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size
    
    @staticmethod
    def volatility_adjusted_stop_loss(price: float, volatility: float, 
                                    multiplier: float = 2.0) -> float:
        """Calculate volatility-adjusted stop loss"""
        return price * (1 - multiplier * volatility)

def main():
    """Main function to demonstrate crypto trading strategies"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto Trading Strategies')
    parser.add_argument('--symbols', nargs='+', default=['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
                       help='Trading symbols')
    parser.add_argument('--strategy', type=str, default='all', 
                       choices=['momentum', 'mean_reversion', 'rsi', 'pairs', 'all'],
                       help='Trading strategy to test')
    parser.add_argument('--backtest_days', type=int, default=365, help='Backtest period in days')
    parser.add_argument('--initial_capital', type=float, default=10000, help='Initial capital')
    
    args = parser.parse_args()
    
    print("="*80)
    print("CRYPTO TRADING STRATEGIES - DAY 69")
    print("="*80)
    
    # Initialize components
    data_manager = CryptoDataManager()
    backtest_engine = BacktestEngine(initial_capital=args.initial_capital)
    
    print(f"Fetching data for {args.symbols}...")
    data = data_manager.fetch_multiple_symbols(args.symbols, lookback_days=args.backtest_days)
    
    if not data:
        print("No data fetched. Exiting.")
        return
    
    # Test different strategies
    strategies_to_test = []
    
    if args.strategy in ['momentum', 'all']:
        strategies_to_test.append('momentum')
    
    if args.strategy in ['mean_reversion', 'all']:
        strategies_to_test.append('mean_reversion')
    
    if args.strategy in ['rsi', 'all']:
        strategies_to_test.append('rsi')
    
    if args.strategy in ['pairs', 'all'] and len(args.symbols) >= 2:
        strategies_to_test.append('pairs')
    
    print(f"\nTesting strategies: {strategies_to_test}")
    
    for symbol in args.symbols[:1]:  # Test first symbol for individual strategies
        df = data[symbol]
        
        for strategy_name in strategies_to_test:
            if strategy_name == 'pairs':
                continue  # Handle pairs separately
            
            print(f"\nTesting {strategy_name} strategy on {symbol}...")
            
            if strategy_name == 'momentum':
                signals = TechnicalStrategy.momentum_strategy(df)
            elif strategy_name == 'mean_reversion':
                signals = TechnicalStrategy.mean_reversion_strategy(df)
            elif strategy_name == 'rsi':
                signals = TechnicalStrategy.rsi_strategy(df)
            else:
                continue
            
            performance = backtest_engine.run_backtest(
                df, signals, f"{strategy_name}_{symbol}"
            )
            
            print(f"  Total Return: {performance.total_return:.2f}%")
            print(f"  Sharpe Ratio: {performance.sharpe_ratio:.2f}")
            print(f"  Max Drawdown: {performance.max_drawdown:.2f}%")
            print(f"  Win Rate: {performance.win_rate:.2f}%")
    
    # Pairs trading strategy
    if 'pairs' in strategies_to_test and len(args.symbols) >= 2:
        print("\nTesting pairs trading strategy...")
        
        # Find cointegrated pairs
        cointegrated_pairs = StatisticalArbitrage.find_cointegrated_pairs(data)
        
        if cointegrated_pairs:
            print(f"Found {len(cointegrated_pairs)} cointegrated pairs")
            
            for sym1, sym2, pvalue in cointegrated_pairs[:2]:  # Test top 2 pairs
                print(f"\nTesting pair: {sym1} - {sym2} (p-value: {pvalue:.4f})")
                
                # Align data
                df1 = data[sym1]['close']
                df2 = data[sym2]['close']
                common_index = df1.index.intersection(df2.index)
                
                if len(common_index) > 100:
                    df1_aligned = df1.loc[common_index]
                    df2_aligned = df2.loc[common_index]
                    
                    # Generate pairs signals
                    signals = StatisticalArbitrage.generate_pairs_signals(
                        df1_aligned, df2_aligned
                    )
                    
                    # For simplicity, backtest on first symbol
                    df_combined = data[sym1].loc[common_index].copy()
                    performance = backtest_engine.run_backtest(
                        df_combined, signals, f"pairs_{sym1}_{sym2}"
                    )
                    
                    print(f"  Total Return: {performance.total_return:.2f}%")
                    print(f"  Sharpe Ratio: {performance.sharpe_ratio:.2f}")
                    print(f"  Max Drawdown: {performance.max_drawdown:.2f}%")
        else:
            print("No cointegrated pairs found")
    
    # Strategy comparison
    print("\n" + "="*50)
    print("STRATEGY COMPARISON")
    print("="*50)
    
    comparison_df = backtest_engine.compare_strategies()
    if not comparison_df.empty:
        print(comparison_df.to_string(index=False))
        
        # Find best strategy
        best_strategy = comparison_df.loc[comparison_df['Sharpe Ratio'].idxmax()]
        print(f"\nBest Strategy: {best_strategy['Strategy']}")
        print(f"Sharpe Ratio: {best_strategy['Sharpe Ratio']:.2f}")
        print(f"Total Return: {best_strategy['Total Return (%)']:.2f}%")
    else:
        print("No strategies to compare")
    
    # Risk management demonstration
    print("\n" + "="*50)
    print("RISK MANAGEMENT ANALYSIS")
    print("="*50)
    
    # Calculate risk metrics for first symbol
    symbol = args.symbols[0]
    df = data[symbol]
    returns = df['close'].pct_change().dropna()
    
    var_95 = RiskManager.calculate_var(returns, 0.95)
    cvar_95 = RiskManager.calculate_cvar(returns, 0.95)
    
    print(f"Risk Metrics for {symbol}:")
    print(f"  95% VaR: {var_95*100:.2f}%")
    print(f"  95% CVaR: {cvar_95*100:.2f}%")
    print(f"  Volatility (annualized): {returns.std() * np.sqrt(365)*100:.2f}%")
    
    # Position sizing example
    entry_price = df['close'].iloc[-1]
    volatility = returns.std()
    stop_loss = RiskManager.volatility_adjusted_stop_loss(entry_price, volatility)
    position_size = RiskManager.calculate_position_size(
        args.initial_capital, 0.02, entry_price, stop_loss  # 2% risk per trade
    )
    
    print(f"\nPosition Sizing Example:")
    print(f"  Entry Price: ${entry_price:.2f}")
    print(f"  Stop Loss: ${stop_loss:.2f}")
    print(f"  Position Size: {position_size:.4f} units")
    print(f"  Capital at Risk: ${abs(entry_price - stop_loss) * position_size:.2f}")
    
    print("\n" + "="*80)
    print("Crypto Trading Strategies demonstration completed!")
    print("="*80)

if __name__ == "__main__":
    main()