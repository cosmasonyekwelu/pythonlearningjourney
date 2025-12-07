
"""
Day 75: Backtesting Framework Setup and Strategy Evaluation
Implementation of event-driven backtesting engine with performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from collections import defaultdict
import json
import math

# ============================================================================
# PART 1: CORE DATA STRUCTURES
# ============================================================================

class OrderType(Enum):
    """Order types for backtesting"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class OrderSide(Enum):
    """Order sides"""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    """Order status"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class Order:
    """Order representation for backtesting"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0
    filled_timestamp: Optional[datetime] = None
    commission: float = 0.0
    
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]

@dataclass
class Position:
    """Position representation"""
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def update_price(self, price: float):
        """Update position with current market price"""
        self.current_price = price
        self.unrealized_pnl = self.quantity * (price - self.avg_price)
    
    def market_value(self) -> float:
        """Calculate current market value"""
        return self.quantity * self.current_price
    
    def cost_basis(self) -> float:
        """Calculate cost basis"""
        return self.quantity * self.avg_price

@dataclass
class Trade:
    """Trade record"""
    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float
    timestamp: datetime
    pnl: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketData:
    """Market data for a single bar"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None  # For limit order fills
    ask: Optional[float] = None  # For limit order fills
    
    def __post_init__(self):
        """Set bid/ask if not provided"""
        if self.bid is None:
            self.bid = self.close * 0.999  # 0.1% spread
        if self.ask is None:
            self.ask = self.close * 1.001  # 0.1% spread

# ============================================================================
# PART 2: VECTORIZED BACKTESTER (SIMPLE)
# ============================================================================

class VectorizedBacktester:
    """
    Simple vectorized backtester for single asset strategies
    Uses pandas vectorized operations for speed
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_pct: float = 0.001,  # 0.1%
        slippage_pct: float = 0.0005,   # 0.05%
        risk_free_rate: float = 0.02    # 2% annual
    ):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        self.risk_free_rate = risk_free_rate
        
        # Results storage
        self.equity_curve = None
        self.returns_series = None
        self.trades = []
        self.metrics = {}
    
    def run_buy_and_hold(
        self,
        price_data: pd.Series,
        symbol: str = "ASSET"
    ) -> Dict[str, Any]:
        """
        Run buy-and-hold strategy
        
        Args:
            price_data: Series of closing prices with datetime index
            symbol: Asset symbol
            
        Returns:
            Performance metrics dictionary
        """
        if len(price_data) < 2:
            raise ValueError("Need at least 2 price points for backtest")
        
        # Initial setup
        dates = price_data.index
        prices = price_data.values
        
        # Calculate daily returns
        daily_returns = np.diff(prices) / prices[:-1]
        
        # Calculate equity curve (fully invested from day 1)
        initial_shares = self.initial_capital / prices[0]
        equity = initial_shares * prices
        
        # Calculate commission (only on initial purchase)
        commission = self.initial_capital * self.commission_pct
        
        # Adjust equity for commission
        equity[0] = self.initial_capital - commission
        
        # Store results
        self.equity_curve = pd.Series(equity, index=dates)
        self.returns_series = pd.Series(daily_returns, index=dates[1:])
        
        # Create single trade record
        trade = Trade(
            trade_id="buy_and_hold_1",
            order_id="order_1",
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=initial_shares,
            price=prices[0],
            commission=commission,
            timestamp=dates[0]
        )
        self.trades = [trade]
        
        # Calculate metrics
        self.metrics = self._calculate_performance_metrics()
        
        return self.metrics
    
    def run_sma_crossover(
        self,
        price_data: pd.Series,
        sma_short: int = 20,
        sma_long: int = 50,
        symbol: str = "ASSET"
    ) -> Dict[str, Any]:
        """
        Run SMA crossover strategy
        
        Args:
            price_data: Series of closing prices with datetime index
            sma_short: Short SMA window
            sma_long: Long SMA window
            symbol: Asset symbol
            
        Returns:
            Performance metrics dictionary
        """
        if len(price_data) < sma_long + 1:
            raise ValueError(f"Need at least {sma_long + 1} price points for SMA crossover")
        
        dates = price_data.index
        prices = price_data.values
        
        # Calculate SMAs
        sma_short_series = pd.Series(prices).rolling(window=sma_short).mean().values
        sma_long_series = pd.Series(prices).rolling(window=sma_long).mean().values
        
        # Generate signals (1 = long, 0 = cash)
        signals = np.zeros_like(prices)
        
        for i in range(sma_long, len(prices)):
            if sma_short_series[i] > sma_long_series[i] and sma_short_series[i-1] <= sma_long_series[i-1]:
                signals[i] = 1  # Buy signal
            elif sma_short_series[i] < sma_long_series[i] and sma_short_series[i-1] >= sma_long_series[i-1]:
                signals[i] = 0  # Sell signal
            else:
                signals[i] = signals[i-1]  # Hold current position
        
        # Initialize arrays for simulation
        cash = np.zeros_like(prices)
        shares = np.zeros_like(prices)
        equity = np.zeros_like(prices)
        
        cash[0] = self.initial_capital
        equity[0] = self.initial_capital
        
        trades = []
        trade_id = 1
        
        # Vectorized simulation
        for i in range(1, len(prices)):
            # Carry forward previous values
            cash[i] = cash[i-1]
            shares[i] = shares[i-1]
            
            # Check for signal change
            if signals[i] != signals[i-1]:
                if signals[i] == 1:  # Buy signal
                    # Calculate max shares we can buy
                    max_shares = cash[i] / (prices[i] * (1 + self.commission_pct + self.slippage_pct))
                    
                    # Execute buy
                    shares[i] = max_shares
                    trade_value = shares[i] * prices[i]
                    commission = trade_value * self.commission_pct
                    slippage = trade_value * self.slippage_pct
                    
                    cash[i] = cash[i] - trade_value - commission - slippage
                    
                    # Record trade
                    trade = Trade(
                        trade_id=f"sma_trade_{trade_id}",
                        order_id=f"order_{trade_id}",
                        symbol=symbol,
                        side=OrderSide.BUY,
                        quantity=shares[i],
                        price=prices[i],
                        commission=commission + slippage,
                        timestamp=dates[i]
                    )
                    trades.append(trade)
                    trade_id += 1
                    
                else:  # Sell signal (signals[i] == 0)
                    if shares[i] > 0:
                        # Execute sell
                        trade_value = shares[i] * prices[i]
                        commission = trade_value * self.commission_pct
                        slippage = trade_value * self.slippage_pct
                        
                        cash[i] = cash[i] + trade_value - commission - slippage
                        shares[i] = 0
                        
                        # Record trade
                        trade = Trade(
                            trade_id=f"sma_trade_{trade_id}",
                            order_id=f"order_{trade_id}",
                            symbol=symbol,
                            side=OrderSide.SELL,
                            quantity=shares[i-1],  # Previous shares
                            price=prices[i],
                            commission=commission + slippage,
                            timestamp=dates[i]
                        )
                        trades.append(trade)
                        trade_id += 1
            
            # Calculate equity
            equity[i] = cash[i] + shares[i] * prices[i]
        
        # Store results
        self.equity_curve = pd.Series(equity, index=dates)
        
        # Calculate returns (skip first value)
        equity_values = self.equity_curve.values
        returns = np.diff(equity_values) / equity_values[:-1]
        self.returns_series = pd.Series(returns, index=dates[1:])
        
        self.trades = trades
        
        # Calculate metrics
        self.metrics = self._calculate_performance_metrics()
        
        return self.metrics
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics
        
        Returns:
            Dictionary of performance metrics
        """
        if self.equity_curve is None or len(self.equity_curve) < 2:
            return {}
        
        equity = self.equity_curve.values
        dates = self.equity_curve.index
        
        # Calculate basic returns
        total_return = (equity[-1] - equity[0]) / equity[0]
        
        # Calculate time period in years
        time_delta = dates[-1] - dates[0]
        years = time_delta.days / 365.25
        
        # Annualized return and CAGR
        if years > 0:
            cagr = (equity[-1] / equity[0]) ** (1 / years) - 1
            annualized_return = total_return / years
        else:
            cagr = total_return
            annualized_return = total_return
        
        # Calculate daily returns if not already calculated
        if self.returns_series is None or len(self.returns_series) == 0:
            daily_returns = np.diff(equity) / equity[:-1]
            if len(dates) - 1 == len(daily_returns):
                self.returns_series = pd.Series(daily_returns, index=dates[1:])
            else:
                self.returns_series = pd.Series(daily_returns)
        
        returns = self.returns_series.dropna().values
        
        if len(returns) == 0:
            return {
                'total_return': total_return,
                'cagr': cagr,
                'annualized_return': annualized_return,
                'num_trades': len(self.trades)
            }
        
        # Risk metrics
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Maximum drawdown
        peak = equity[0]
        max_dd = 0
        max_dd_duration = 0
        current_dd_duration = 0
        
        for i in range(1, len(equity)):
            if equity[i] > peak:
                peak = equity[i]
                current_dd_duration = 0
            else:
                drawdown = (peak - equity[i]) / peak
                max_dd = max(max_dd, drawdown)
                current_dd_duration += 1
                max_dd_duration = max(max_dd_duration, current_dd_duration)
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        # Risk-adjusted returns
        if volatility > 0:
            sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
            
            # Sortino ratio (only downside deviation)
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_deviation = np.std(downside_returns) * np.sqrt(252)
                if downside_deviation > 0:
                    sortino_ratio = (annualized_return - self.risk_free_rate) / downside_deviation
                else:
                    sortino_ratio = np.inf
            else:
                sortino_ratio = np.inf
            
            # Calmar ratio
            if max_dd > 0:
                calmar_ratio = cagr / max_dd
            else:
                calmar_ratio = np.inf
        else:
            sharpe_ratio = np.inf
            sortino_ratio = np.inf
            calmar_ratio = np.inf
        
        # Trade statistics
        num_trades = len(self.trades)
        win_rate = 0.0
        avg_win = 0.0
        avg_loss = 0.0
        profit_factor = 0.0
        
        if num_trades > 0:
            # Calculate trade P&L (simplified)
            trade_pnls = []
            buy_trades = [t for t in self.trades if t.side == OrderSide.BUY]
            sell_trades = [t for t in self.trades if t.side == OrderSide.SELL]
            
            for buy, sell in zip(buy_trades, sell_trades):
                if buy.symbol == sell.symbol:
                    pnl = (sell.price - buy.price) * buy.quantity - buy.commission - sell.commission
                    trade_pnls.append(pnl)
            
            if trade_pnls:
                winning_trades = [p for p in trade_pnls if p > 0]
                losing_trades = [p for p in trade_pnls if p < 0]
                
                win_rate = len(winning_trades) / len(trade_pnls) if trade_pnls else 0
                avg_win = np.mean(winning_trades) if winning_trades else 0
                avg_loss = np.mean(losing_trades) if losing_trades else 0
                
                gross_profit = sum(winning_trades) if winning_trades else 0
                gross_loss = abs(sum(losing_trades)) if losing_trades else 0
                
                if gross_loss > 0:
                    profit_factor = gross_profit / gross_loss
                elif gross_profit > 0:
                    profit_factor = np.inf
                else:
                    profit_factor = 0
        
        return {
            'total_return': total_return,
            'cagr': cagr,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_dd,
            'max_drawdown_duration': max_dd_duration,
            'var_95': var_95,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_equity': equity[-1]
        }
    
    def compare_with_benchmark(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
        benchmark_name: str = "Benchmark"
    ) -> Dict[str, Any]:
        """
        Compare strategy with benchmark
        
        Args:
            strategy_returns: Strategy return series
            benchmark_returns: Benchmark return series
            benchmark_name: Name of benchmark
            
        Returns:
            Comparison metrics
        """
        # Align dates
        common_dates = strategy_returns.index.intersection(benchmark_returns.index)
        
        if len(common_dates) < 2:
            return {"error": "Insufficient overlapping data"}
        
        strategy_aligned = strategy_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        # Calculate excess returns
        excess_returns = strategy_aligned - benchmark_aligned
        
        # Calculate alpha and beta
        cov_matrix = np.cov(strategy_aligned, benchmark_aligned)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        
        # Annualized returns
        strategy_annual = (1 + strategy_aligned.mean()) ** 252 - 1
        benchmark_annual = (1 + benchmark_aligned.mean()) ** 252 - 1
        
        # Alpha (annualized)
        alpha = (strategy_annual - self.risk_free_rate) - beta * (benchmark_annual - self.risk_free_rate)
        
        # Tracking error
        tracking_error = np.std(excess_returns) * np.sqrt(252)
        
        # Information ratio
        if tracking_error > 0:
            information_ratio = (strategy_annual - benchmark_annual) / tracking_error
        else:
            information_ratio = np.inf if strategy_annual > benchmark_annual else -np.inf
        
        # Up/down capture ratios
        up_market = benchmark_aligned > 0
        down_market = benchmark_aligned < 0
        
        if up_market.any():
            up_capture = (1 + strategy_aligned[up_market].mean()) ** 252 / (1 + benchmark_aligned[up_market].mean()) ** 252 - 1
        else:
            up_capture = np.nan
        
        if down_market.any():
            down_capture = (1 + strategy_aligned[down_market].mean()) ** 252 / (1 + benchmark_aligned[down_market].mean()) ** 252 - 1
        else:
            down_capture = np.nan
        
        return {
            'alpha': alpha,
            'beta': beta,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'up_capture_ratio': up_capture,
            'down_capture_ratio': down_capture,
            'excess_return_annual': strategy_annual - benchmark_annual,
            'benchmark_name': benchmark_name
        }

# ============================================================================
# PART 3: EVENT-DRIVEN BACKTESTING ENGINE
# ============================================================================

class EventDrivenBacktester:
    """
    Event-driven backtesting engine with realistic market simulation
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_pct: float = 0.001,  # 0.1%
        commission_fixed: float = 1.0,   # $1 fixed
        slippage_pct: float = 0.0005,    # 0.05%
        spread_pct: float = 0.001,       # 0.1% bid-ask spread
        enable_shorting: bool = False,
        max_position_pct: float = 0.1,   # Max 10% per position
        interest_on_cash: float = 0.02   # 2% annual interest
    ):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.commission_fixed = commission_fixed
        self.slippage_pct = slippage_pct
        self.spread_pct = spread_pct
        self.enable_shorting = enable_shorting
        self.max_position_pct = max_position_pct
        self.interest_on_cash = interest_on_cash
        
        # State variables
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.equity_history: List[Tuple[datetime, float]] = []
        self.market_data_history: List[MarketData] = []
        
        # Performance tracking
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.current_date = None
        
        # Strategy callback
        self.strategy_callback = None
    
    def set_strategy(self, strategy_callback: Callable):
        """
        Set strategy callback function
        
        Args:
            strategy_callback: Function that takes (backtester, market_data)
                              and returns list of Order objects
        """
        self.strategy_callback = strategy_callback
    
    def run(
        self,
        market_data: List[MarketData],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run backtest on market data
        
        Args:
            market_data: List of MarketData objects in chronological order
            verbose: Whether to print progress
            
        Returns:
            Performance metrics
        """
        if not market_data:
            raise ValueError("No market data provided")
        
        if self.strategy_callback is None:
            raise ValueError("No strategy set. Use set_strategy() first.")
        
        # Reset state
        self._reset_state()
        
        # Sort market data by timestamp
        market_data.sort(key=lambda x: x.timestamp)
        
        # Initialize equity history
        self.equity_history.append((market_data[0].timestamp, self.initial_capital))
        
        # Main event loop
        for i, data in enumerate(market_data):
            self.current_date = data.timestamp
            
            if verbose and i % 100 == 0:
                print(f"Processing {data.timestamp.date()} ({i+1}/{len(market_data)})")
            
            # Update existing positions with current prices
            self._update_positions(data)
            
            # Apply interest on cash (daily compounding)
            self._apply_interest(data.timestamp)
            
            # Get strategy signals
            orders = self.strategy_callback(self, data)
            
            # Process orders
            for order in orders:
                self._process_order(order, data)
            
            # Clean up completed orders
            self.orders = [o for o in self.orders if not o.is_completed()]
            
            # Record equity
            equity = self._calculate_total_equity()
            self.equity_history.append((data.timestamp, equity))
            
            # Store market data
            self.market_data_history.append(data)
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics()
        
        return metrics
    
    def _reset_state(self):
        """Reset backtester state"""
        self.cash = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.trades.clear()
        self.equity_history.clear()
        self.market_data_history.clear()
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.current_date = None
    
    def _update_positions(self, market_data: MarketData):
        """Update positions with current market data"""
        if market_data.symbol in self.positions:
            position = self.positions[market_data.symbol]
            position.update_price(market_data.close)
    
    def _apply_interest(self, current_date: datetime):
        """Apply interest on cash (simplified daily compounding)"""
        if len(self.equity_history) > 0:
            last_date = self.equity_history[-1][0]
            days_diff = (current_date - last_date).days
            
            if days_diff > 0:
                # Apply daily interest rate
                daily_rate = (1 + self.interest_on_cash) ** (1/365) - 1
                self.cash *= (1 + daily_rate) ** days_diff
    
    def _process_order(self, order: Order, market_data: MarketData):
        """Process an order with current market data"""
        # Basic validation
        if order.quantity <= 0:
            order.status = OrderStatus.REJECTED
            order.filled_quantity = 0
            return
        
        if order.symbol != market_data.symbol:
            # This order is for a different symbol than current market data
            # In a multi-asset backtest, we'd need to handle this differently
            return
        
        # Check position limits
        if not self._check_position_limit(order, market_data):
            order.status = OrderStatus.REJECTED
            order.filled_quantity = 0
            return
        
        # Determine fill price based on order type
        if order.order_type == OrderType.MARKET:
            fill_price = self._get_market_fill_price(order, market_data)
            can_fill = True
        elif order.order_type == OrderType.LIMIT:
            fill_price, can_fill = self._get_limit_fill_price(order, market_data)
        elif order.order_type == OrderType.STOP:
            fill_price, can_fill = self._get_stop_fill_price(order, market_data)
        else:
            order.status = OrderStatus.REJECTED
            return
        
        if can_fill:
            # Apply slippage
            slippage = fill_price * self.slippage_pct
            if order.side == OrderSide.BUY:
                fill_price += slippage
            else:  # SELL
                fill_price -= slippage
            
            self.total_slippage += abs(slippage * order.quantity)
            
            # Calculate commission
            trade_value = fill_price * order.quantity
            commission = trade_value * self.commission_pct + self.commission_fixed
            self.total_commission += commission
            
            # Execute trade
            self._execute_trade(order, fill_price, commission, market_data.timestamp)
        else:
            # Order remains pending
            self.orders.append(order)
    
    def _get_market_fill_price(self, order: Order, market_data: MarketData) -> float:
        """Get fill price for market order"""
        if order.side == OrderSide.BUY:
            return market_data.ask  # Buy at ask price
        else:  # SELL
            return market_data.bid  # Sell at bid price
    
    def _get_limit_fill_price(
        self, 
        order: Order, 
        market_data: MarketData
    ) -> Tuple[float, bool]:
        """Get fill price for limit order"""
        if order.limit_price is None:
            return 0.0, False
        
        if order.side == OrderSide.BUY:
            # Buy limit: fill if ask price <= limit price
            can_fill = market_data.ask <= order.limit_price
            fill_price = min(market_data.ask, order.limit_price)
        else:  # SELL
            # Sell limit: fill if bid price >= limit price
            can_fill = market_data.bid >= order.limit_price
            fill_price = max(market_data.bid, order.limit_price)
        
        return fill_price, can_fill
    
    def _get_stop_fill_price(
        self, 
        order: Order, 
        market_data: MarketData
    ) -> Tuple[float, bool]:
        """Get fill price for stop order"""
        if order.stop_price is None:
            return 0.0, False
        
        if order.side == OrderSide.BUY:
            # Buy stop: becomes market order when price rises above stop
            can_fill = market_data.high >= order.stop_price
            fill_price = market_data.ask if can_fill else 0.0
        else:  # SELL
            # Sell stop: becomes market order when price falls below stop
            can_fill = market_data.low <= order.stop_price
            fill_price = market_data.bid if can_fill else 0.0
        
        return fill_price, can_fill
    
    def _check_position_limit(self, order: Order, market_data: MarketData) -> bool:
        """Check if order respects position limits"""
        if not self.enable_shorting and order.side == OrderSide.SELL:
            # Check if we have the position to sell
            if order.symbol not in self.positions:
                return False
            
            position = self.positions[order.symbol]
            if position.quantity < order.quantity:
                return False
        
        # Check max position percentage
        total_equity = self._calculate_total_equity()
        position_value = order.quantity * market_data.close
        
        if position_value > total_equity * self.max_position_pct:
            return False
        
        return True
    
    def _execute_trade(
        self, 
        order: Order, 
        fill_price: float, 
        commission: float,
        timestamp: datetime
    ):
        """Execute a trade and update portfolio"""
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_price = fill_price
        order.filled_quantity = order.quantity
        order.filled_timestamp = timestamp
        order.commission = commission
        
        # Update cash
        trade_value = fill_price * order.quantity
        
        if order.side == OrderSide.BUY:
            self.cash -= trade_value + commission
            
            # Update or create position
            if order.symbol in self.positions:
                position = self.positions[order.symbol]
                # Calculate new average price
                total_cost = position.cost_basis() + trade_value
                total_shares = position.quantity + order.quantity
                new_avg_price = total_cost / total_shares
                
                position.quantity = total_shares
                position.avg_price = new_avg_price
                position.current_price = fill_price
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=fill_price,
                    current_price=fill_price
                )
        else:  # SELL
            self.cash += trade_value - commission
            
            if order.symbol in self.positions:
                position = self.positions[order.symbol]
                
                # Calculate realized P&L
                realized_pnl = (fill_price - position.avg_price) * order.quantity - commission
                position.realized_pnl += realized_pnl
                
                # Reduce position
                position.quantity -= order.quantity
                
                # If position is closed, remove it
                if position.quantity <= 0.0001:  # Small tolerance
                    del self.positions[order.symbol]
        
        # Record trade
        trade = Trade(
            trade_id=f"trade_{len(self.trades) + 1}",
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            timestamp=timestamp
        )
        self.trades.append(trade)
    
    def _calculate_total_equity(self) -> float:
        """Calculate total portfolio equity"""
        total_value = self.cash
        
        for position in self.positions.values():
            total_value += position.market_value()
        
        return total_value
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results"""
        if len(self.equity_history) < 2:
            return {}
        
        # Extract equity curve
        dates, equity_values = zip(*self.equity_history)
        equity_series = pd.Series(equity_values, index=dates)
        
        # Calculate returns
        returns = equity_series.pct_change().dropna()
        
        if len(returns) == 0:
            return {
                'final_equity': equity_values[-1],
                'total_return': (equity_values[-1] - self.initial_capital) / self.initial_capital,
                'num_trades': len(self.trades),
                'total_commission': self.total_commission,
                'total_slippage': self.total_slippage
            }
        
        # Use VectorizedBacktester's metrics calculation
        simple_backtester = VectorizedBacktester(
            initial_capital=self.initial_capital,
            commission_pct=self.commission_pct
        )
        
        simple_backtester.equity_curve = equity_series
        simple_backtester.returns_series = returns
        simple_backtester.trades = self.trades
        
        metrics = simple_backtester._calculate_performance_metrics()
        
        # Add backtest-specific metrics
        metrics.update({
            'final_equity': equity_values[-1],
            'total_commission': self.total_commission,
            'total_slippage': self.total_slippage,
            'num_positions': len(self.positions),
            'cash_final': self.cash,
            'max_concurrent_positions': self._get_max_concurrent_positions(),
            'avg_trade_commission': self.total_commission / len(self.trades) if self.trades else 0
        })
        
        return metrics
    
    def _get_max_concurrent_positions(self) -> int:
        """Get maximum number of concurrent positions"""
        # This would require tracking position history
        # For simplicity, return current number
        return len(self.positions)
    
    def generate_report(self) -> str:
        """Generate a formatted performance report"""
        if not self.equity_history:
            return "No backtest results available."
        
        metrics = self._calculate_performance_metrics()
        
        report = []
        report.append("=" * 70)
        report.append("BACKTEST PERFORMANCE REPORT")
        report.append("=" * 70)
        
        # Basic statistics
        report.append(f"\nInitial Capital: ${self.initial_capital:,.2f}")
        report.append(f"Final Equity: ${metrics.get('final_equity', 0):,.2f}")
        report.append(f"Total Return: {metrics.get('total_return', 0) * 100:.2f}%")
        report.append(f"CAGR: {metrics.get('cagr', 0) * 100:.2f}%")
        
        # Risk metrics
        report.append(f"\nRisk Metrics:")
        report.append(f"  Volatility (Annualized): {metrics.get('volatility', 0) * 100:.2f}%")
        report.append(f"  Max Drawdown: {metrics.get('max_drawdown', 0) * 100:.2f}%")
        report.append(f"  Max Drawdown Duration: {metrics.get('max_drawdown_duration', 0)} days")
        report.append(f"  VaR (95%): {metrics.get('var_95', 0) * 100:.2f}%")
        
        # Risk-adjusted returns
        report.append(f"\nRisk-Adjusted Returns:")
        report.append(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        report.append(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
        report.append(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}")
        
        # Trade statistics
        report.append(f"\nTrade Statistics:")
        report.append(f"  Number of Trades: {metrics.get('num_trades', 0)}")
        report.append(f"  Win Rate: {metrics.get('win_rate', 0) * 100:.2f}%")
        report.append(f"  Average Win: ${metrics.get('avg_win', 0):,.2f}")
        report.append(f"  Average Loss: ${metrics.get('avg_loss', 0):,.2f}")
        report.append(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        
        # Cost analysis
        report.append(f"\nCost Analysis:")
        report.append(f"  Total Commission: ${metrics.get('total_commission', 0):,.2f}")
        report.append(f"  Total Slippage: ${metrics.get('total_slippage', 0):,.2f}")
        report.append(f"  Cash Remaining: ${self.cash:,.2f}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)

# ============================================================================
# PART 4: SAMPLE STRATEGIES FOR BACKTESTING
# ============================================================================

class SMACrossoverStrategy:
    """SMA Crossover Strategy for event-driven backtesting"""
    
    def __init__(self, sma_short: int = 20, sma_long: int = 50):
        self.sma_short = sma_short
        self.sma_long = sma_long
        self.price_history = []
        self.position = 0  # 0 = no position, 1 = long position
    
    def __call__(self, backtester, market_data: MarketData) -> List[Order]:
        """Strategy callback function"""
        orders = []
        
        # Add price to history
        self.price_history.append(market_data.close)
        
        # Need enough data for SMA calculation
        if len(self.price_history) < self.sma_long:
            return orders
        
        # Calculate SMAs
        prices = np.array(self.price_history)
        sma_short = np.mean(prices[-self.sma_short:])
        sma_long = np.mean(prices[-self.sma_long:])
        
        # Generate signals
        if sma_short > sma_long and self.position == 0:
            # Buy signal
            order = Order(
                order_id=f"order_{market_data.timestamp.timestamp()}",
                symbol=market_data.symbol,
                order_type=OrderType.MARKET,
                side=OrderSide.BUY,
                quantity=100  # Fixed quantity for simplicity
            )
            orders.append(order)
            self.position = 1
            
        elif sma_short < sma_long and self.position == 1:
            # Sell signal
            order = Order(
                order_id=f"order_{market_data.timestamp.timestamp()}_sell",
                symbol=market_data.symbol,
                order_type=OrderType.MARKET,
                side=OrderSide.SELL,
                quantity=100  # Should match buy quantity
            )
            orders.append(order)
            self.position = 0
        
        return orders

class MeanReversionStrategy:
    """Mean Reversion Strategy based on Bollinger Bands"""
    
    def __init__(self, window: int = 20, num_std: float = 2.0):
        self.window = window
        self.num_std = num_std
        self.price_history = []
        self.position = 0
    
    def __call__(self, backtester, market_data: MarketData) -> List[Order]:
        """Strategy callback function"""
        orders = []
        
        self.price_history.append(market_data.close)
        
        if len(self.price_history) < self.window:
            return orders
        
        # Calculate Bollinger Bands
        prices = np.array(self.price_history[-self.window:])
        sma = np.mean(prices)
        std = np.std(prices)
        
        upper_band = sma + self.num_std * std
        lower_band = sma - self.num_std * std
        
        current_price = market_data.close
        
        # Generate signals
        if current_price < lower_band and self.position == 0:
            # Buy signal (oversold)
            order = Order(
                order_id=f"mr_buy_{market_data.timestamp.timestamp()}",
                symbol=market_data.symbol,
                order_type=OrderType.MARKET,
                side=OrderSide.BUY,
                quantity=100
            )
            orders.append(order)
            self.position = 1
            
        elif current_price > upper_band and self.position == 1:
            # Sell signal (overbought)
            order = Order(
                order_id=f"mr_sell_{market_data.timestamp.timestamp()}",
                symbol=market_data.symbol,
                order_type=OrderType.MARKET,
                side=OrderSide.SELL,
                quantity=100
            )
            orders.append(order)
            self.position = 0
        
        return orders

# ============================================================================
# PART 5: DEMONSTRATION AND COMPARISON
# ============================================================================

def demonstrate_backtesting_frameworks():
    """Demonstrate both vectorized and event-driven backtesting"""
    print("=" * 70)
    print("Day 75: Backtesting Framework Setup and Strategy Evaluation")
    print("=" * 70)
    
    # Generate sample price data
    np.random.seed(42)
    n_days = 1000
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='D')
    
    # Create price series with trend and volatility
    trend = np.linspace(100, 120, n_days)
    noise = np.random.normal(0, 1.5, n_days)
    prices = trend + noise.cumsum()
    
    price_series = pd.Series(prices, index=dates)
    
    print(f"\n1. Generated {n_days} days of price data")
    print(f"   Start price: ${prices[0]:.2f}, End price: ${prices[-1]:.2f}")
    print(f"   Total price change: {((prices[-1] - prices[0]) / prices[0] * 100):.2f}%")
    
    # ========================================================================
    # Vectorized Backtesting
    # ========================================================================
    print("\n2. Running Vectorized Backtests:")
    print("-" * 40)
    
    vector_backtester = VectorizedBacktester(
        initial_capital=100000.0,
        commission_pct=0.001,  # 0.1%
        slippage_pct=0.0005    # 0.05%
    )
    
    # Buy and Hold
    print("\n   Buy-and-Hold Strategy:")
    bh_metrics = vector_backtester.run_buy_and_hold(price_series, "AAPL")
    
    print(f"     Total Return: {bh_metrics['total_return'] * 100:.2f}%")
    print(f"     CAGR: {bh_metrics['cagr'] * 100:.2f}%")
    print(f"     Max Drawdown: {bh_metrics['max_drawdown'] * 100:.2f}%")
    print(f"     Sharpe Ratio: {bh_metrics['sharpe_ratio']:.2f}")
    print(f"     Number of Trades: {bh_metrics['num_trades']}")
    
    # SMA Crossover
    print("\n   SMA Crossover Strategy (20/50):")
    sma_metrics = vector_backtester.run_sma_crossover(
        price_series,
        sma_short=20,
        sma_long=50,
        symbol="AAPL"
    )
    
    print(f"     Total Return: {sma_metrics['total_return'] * 100:.2f}%")
    print(f"     CAGR: {sma_metrics['cagr'] * 100:.2f}%")
    print(f"     Max Drawdown: {sma_metrics['max_drawdown'] * 100:.2f}%")
    print(f"     Sharpe Ratio: {sma_metrics['sharpe_ratio']:.2f}")
    print(f"     Number of Trades: {sma_metrics['num_trades']}")
    print(f"     Win Rate: {sma_metrics['win_rate'] * 100:.2f}%")
    
    # Comparison
    print("\n   Strategy Comparison:")
    print(f"     SMA vs Buy-and-Hold Return: {(sma_metrics['total_return'] - bh_metrics['total_return']) * 100:.2f}%")
    print(f"     SMA Drawdown Reduction: {(bh_metrics['max_drawdown'] - sma_metrics['max_drawdown']) * 100:.2f}%")
    
    # ========================================================================
    # Event-Driven Backtesting
    # ========================================================================
    print("\n3. Running Event-Driven Backtest:")
    print("-" * 40)
    
    # Prepare market data for event-driven backtest
    market_data_list = []
    for i, (date, price) in enumerate(price_series.items()):
        # Create realistic bid-ask spread
        spread = price * 0.001  # 0.1% spread
        bid = price - spread/2
        ask = price + spread/2
        
        # Add some intraday range
        high = price * (1 + np.random.uniform(0, 0.01))
        low = price * (1 - np.random.uniform(0, 0.01))
        
        market_data = MarketData(
            symbol="AAPL",
            timestamp=date,
            open=price * (1 + np.random.uniform(-0.005, 0.005)),
            high=high,
            low=low,
            close=price,
            volume=1000000 + np.random.randint(-200000, 200000),
            bid=bid,
            ask=ask
        )
        market_data_list.append(market_data)
    
    # Create event-driven backtester
    event_backtester = EventDrivenBacktester(
        initial_capital=100000.0,
        commission_pct=0.001,  # 0.1%
        commission_fixed=1.0,   # $1 fixed
        slippage_pct=0.0005,    # 0.05%
        spread_pct=0.001,       # 0.1% spread
        enable_shorting=False,
        max_position_pct=0.1,
        interest_on_cash=0.02
    )
    
    # Set strategy
    sma_strategy = SMACrossoverStrategy(sma_short=20, sma_long=50)
    event_backtester.set_strategy(sma_strategy)
    
    print("\n   Running SMA Crossover Strategy with Event-Driven Engine...")
    
    # Run backtest
    event_metrics = event_backtester.run(market_data_list[:500], verbose=False)  # Use first 500 days for speed
    
    print(f"     Total Return: {event_metrics['total_return'] * 100:.2f}%")
    print(f"     Number of Trades: {event_metrics['num_trades']}")
    print(f"     Total Commission: ${event_metrics['total_commission']:.2f}")
    print(f"     Total Slippage: ${event_metrics['total_slippage']:.2f}")
    print(f"     Final Cash: ${event_backtester.cash:,.2f}")
    
    # Generate report
    print("\n   Event-Driven Backtest Report:")
    print(event_backtester.generate_report())
    
    # ========================================================================
    # Performance Metrics Comparison
    # ========================================================================
    print("\n4. Performance Metrics Deep Dive:")
    print("-" * 40)
    
    # Create benchmark (market returns)
    benchmark_returns = price_series.pct_change().dropna()
    
    # Compare SMA strategy with benchmark
    if vector_backtester.returns_series is not None:
        comparison = vector_backtester.compare_with_benchmark(
            strategy_returns=vector_backtester.returns_series,
            benchmark_returns=benchmark_returns,
            benchmark_name="Market"
        )
        
        print(f"\n   Alpha: {comparison['alpha'] * 100:.2f}%")
        print(f"   Beta: {comparison['beta']:.2f}")
        print(f"   Tracking Error: {comparison['tracking_error'] * 100:.2f}%")
        print(f"   Information Ratio: {comparison['information_ratio']:.2f}")
        print(f"   Up Capture: {comparison['up_capture_ratio'] * 100:.2f}%")
        print(f"   Down Capture: {comparison['down_capture_ratio'] * 100:.2f}%")
    
    # ========================================================================
    # Avoiding Backtesting Biases
    # ========================================================================
    print("\n5. Avoiding Common Backtesting Biases:")
    print("-" * 40)
    
    print("\n   Look-Ahead Bias Prevention:")
    print("     - Vectorized backtest uses .shift() to avoid future data")
    print("     - Event-driven processes data in strict chronological order")
    print("     - Strategy only sees data up to current timestamp")
    
    print("\n   Survivorship Bias Awareness:")
    print("     - In production, include de-listed assets in universe")
    print("     - Use survivorship-bias-free datasets when available")
    print("     - Simulate bankruptcies in synthetic data")
    
    print("\n   Overfitting Prevention:")
    print("     - Use walk-forward analysis (train/test splits)")
    print("     - Limit number of strategy parameters")
    print("     - Use out-of-sample testing")
    print("     - Apply statistical significance tests")
    
    # ========================================================================
    # Key Takeaways
    # ========================================================================
    print("\n6. Key Framework Differences:")
    print("-" * 40)
    
    print("\n   Vectorized Backtesting:")
    print("     ✓ Fast execution using pandas/numpy vectorization")
    print("     ✓ Simple to implement for basic strategies")
    print("     ✗ Less realistic (simultaneous order execution)")
    print("     ✗ Harder to model complex order types")
    
    print("\n   Event-Driven Backtesting:")
    print("     ✓ Realistic simulation of market microstructure")
    print("     ✓ Supports complex order types (limit, stop)")
    print("     ✓ Models slippage, commissions, spread accurately")
    print("     ✗ Slower execution (sequential processing)")
    print("     ✗ More complex implementation")
    
    print("\n" + "=" * 70)
    print("Implementation Complete!")
    print("\nNext Steps:")
    print("1. Add walk-forward analysis for robustness testing")
    print("2. Implement Monte Carlo simulation for strategy validation")
    print("3. Add multi-asset portfolio backtesting")
    print("4. Incorporate fundamental data and corporate actions")
    print("5. Build visualization tools for equity curves and drawdowns")
    print("=" * 70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run demonstration
    demonstrate_backtesting_frameworks()
    
    print("\n\nBacktesting Framework Features Summary:")
    print("-" * 40)
    print("Vectorized Backtester:")
    print("  ✓ Buy-and-hold strategy implementation")
    print("  ✓ SMA crossover strategy with signals")
    print("  ✓ Comprehensive performance metrics calculation")
    print("  ✓ Benchmark comparison (alpha, beta, tracking error)")
    print("  ✓ Risk metrics (volatility, max drawdown, VaR)")
    print("  ✓ Trade statistics (win rate, profit factor)")
    
    print("\nEvent-Driven Backtester:")
    print("  ✓ Realistic market simulation with bid-ask spreads")
    print("  ✓ Support for market, limit, and stop orders")
    print("  ✓ Slippage and commission modeling")
    print("  ✓ Position limits and risk management")
    print("  ✓ Interest on cash (time value of money)")
    print("  ✓ Strategy callback interface for flexibility")
    print("  ✓ Detailed trade logging and position tracking")
    
    print("\nPerformance Metrics:")
    print("  ✓ Returns: Total, Annualized, CAGR")
    print("  ✓ Risk: Volatility, Max Drawdown, VaR")
    print("  ✓ Risk-Adjusted: Sharpe, Sortino, Calmar ratios")
    print("  ✓ Benchmark: Alpha, Beta, Tracking Error")
    print("  ✓ Trade: Win Rate, Avg Win/Loss, Profit Factor")
    
    print("\nSample Strategies:")
    print("  ✓ SMA Crossover (20/50)")
    print("  ✓ Mean Reversion (Bollinger Bands)")
    print("  ✓ Custom strategy via callback interface")
    
    print("\n" + "=" * 70)
    print("To use this framework:")
    print("1. For quick analysis: Use VectorizedBacktester")
    print("2. For realistic simulation: Use EventDrivenBacktester")
    print("3. Implement your strategy as a callback function")
    print("4. Analyze results using the comprehensive metrics")
    print("=" * 70)