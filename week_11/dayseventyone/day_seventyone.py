"""
Day 71: Testing Frameworks Overview
Implementation of testing foundation for trading applications
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ============================================================================
# PART 1: CORE TRADING COMPONENTS TO TEST
# ============================================================================

@dataclass
class TradeSignal:
    """Represents a trading signal"""
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL, HOLD
    strength: float  # 0-1 confidence
    price: Optional[float] = None
    
    def __post_init__(self):
        valid_actions = ['BUY', 'SELL', 'HOLD']
        if self.action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")
        if not 0 <= self.strength <= 1:
            raise ValueError("Strength must be between 0 and 1")

class SimpleMovingAverage:
    """Simple Moving Average indicator"""
    
    def __init__(self, window: int = 20):
        self.window = window
        self.validate_window()
    
    def validate_window(self):
        """Validate window parameter"""
        if self.window <= 0:
            raise ValueError("Window must be positive integer")
    
    def calculate(self, prices: pd.Series) -> pd.Series:
        """
        Calculate SMA for given price series
        
        Args:
            prices: Price series
            
        Returns:
            SMA series
        """
        if len(prices) < self.window:
            raise ValueError(f"Need at least {self.window} prices, got {len(prices)}")
        
        return prices.rolling(window=self.window, min_periods=self.window).mean()
    
    def generate_signal(self, current_price: float, sma_value: float) -> str:
        """
        Generate trading signal based on price vs SMA
        
        Args:
            current_price: Current price
            sma_value: Current SMA value
            
        Returns:
            Trading signal
        """
        if pd.isna(sma_value):
            return 'HOLD'
        
        if current_price > sma_value * 1.02:  # 2% above SMA
            return 'BUY'
        elif current_price < sma_value * 0.98:  # 2% below SMA
            return 'SELL'
        else:
            return 'HOLD'

class PositionSizer:
    """Position sizing calculator"""
    
    def __init__(self, max_position_pct: float = 0.1):
        self.max_position_pct = max_position_pct
    
    def calculate_position_size(
        self, 
        capital: float, 
        entry_price: float, 
        stop_loss: float,
        risk_per_trade: float = 0.02
    ) -> Tuple[int, float]:
        """
        Calculate position size based on risk
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade: Risk per trade as percentage of capital
            
        Returns:
            Tuple of (shares, risk_amount)
        """
        if entry_price <= stop_loss:
            raise ValueError("Entry price must be greater than stop loss")
        
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            return 0, 0.0
        
        max_risk_amount = capital * risk_per_trade
        shares = int(max_risk_amount / risk_per_share)
        
        # Apply maximum position limit
        max_shares_by_capital = int((capital * self.max_position_pct) / entry_price)
        shares = min(shares, max_shares_by_capital)
        
        actual_risk = shares * risk_per_share
        return shares, actual_risk

# ============================================================================
# PART 2: UNIT TEST IMPLEMENTATION
# ============================================================================

class TestSimpleMovingAverage:
    """Unit tests for SimpleMovingAverage class"""
    
    def test_init_valid_window(self):
        """Test initialization with valid window"""
        sma = SimpleMovingAverage(window=20)
        assert sma.window == 20
    
    def test_init_invalid_window(self):
        """Test initialization with invalid window"""
        with pytest.raises(ValueError):
            SimpleMovingAverage(window=0)
        with pytest.raises(ValueError):
            SimpleMovingAverage(window=-5)
    
    def test_calculate_basic(self):
        """Test basic SMA calculation"""
        sma = SimpleMovingAverage(window=3)
        prices = pd.Series([10, 20, 30, 40, 50])
        
        result = sma.calculate(prices)
        
        # Manual calculation verification
        expected = pd.Series([np.nan, np.nan, 20.0, 30.0, 40.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_insufficient_data(self):
        """Test SMA calculation with insufficient data"""
        sma = SimpleMovingAverage(window=10)
        prices = pd.Series([10, 20, 30])
        
        with pytest.raises(ValueError):
            sma.calculate(prices)
    
    def test_generate_signal(self):
        """Test signal generation"""
        sma = SimpleMovingAverage(window=10)
        
        # Test cases: (current_price, sma_value, expected_signal)
        test_cases = [
            (102, 100, 'BUY'),      # 2% above SMA
            (98, 100, 'SELL'),      # 2% below SMA
            (101, 100, 'HOLD'),     # Within 2% band
            (99, 100, 'HOLD'),      # Within 2% band
            (100, np.nan, 'HOLD'),  # NaN SMA
        ]
        
        for current_price, sma_value, expected in test_cases:
            signal = sma.generate_signal(current_price, sma_value)
            assert signal == expected, f"Failed for {current_price}, {sma_value}"

class TestTradeSignal:
    """Unit tests for TradeSignal class"""
    
    def test_valid_signal_creation(self):
        """Test creating valid trade signals"""
        timestamp = datetime.now()
        
        buy_signal = TradeSignal(
            timestamp=timestamp,
            symbol='AAPL',
            action='BUY',
            strength=0.8,
            price=150.0
        )
        
        assert buy_signal.symbol == 'AAPL'
        assert buy_signal.action == 'BUY'
        assert buy_signal.strength == 0.8
        assert buy_signal.price == 150.0
    
    def test_invalid_action(self):
        """Test creating signal with invalid action"""
        with pytest.raises(ValueError):
            TradeSignal(
                timestamp=datetime.now(),
                symbol='AAPL',
                action='INVALID',
                strength=0.5
            )
    
    def test_invalid_strength(self):
        """Test creating signal with invalid strength"""
        with pytest.raises(ValueError):
            TradeSignal(
                timestamp=datetime.now(),
                symbol='AAPL',
                action='BUY',
                strength=1.5  # Invalid: > 1
            )
        
        with pytest.raises(ValueError):
            TradeSignal(
                timestamp=datetime.now(),
                symbol='AAPL',
                action='BUY',
                strength=-0.1  # Invalid: < 0
            )

class TestPositionSizer:
    """Unit tests for PositionSizer class"""
    
    def test_position_size_calculation(self):
        """Test basic position size calculation"""
        sizer = PositionSizer(max_position_pct=0.1)
        
        # Test case: $10,000 capital, $100 entry, $95 stop loss
        shares, risk = sizer.calculate_position_size(
            capital=10000,
            entry_price=100,
            stop_loss=95,
            risk_per_trade=0.02  # 2% risk
        )
        
        # Expected: Risk per share = $5, Max risk = $200, Shares = 40
        expected_shares = 40
        expected_risk = 40 * 5  # 40 shares * $5 risk per share
        
        assert shares == expected_shares
        assert risk == expected_risk
    
    def test_position_cap_by_capital(self):
        """Test position size limited by capital constraint"""
        sizer = PositionSizer(max_position_pct=0.1)  # Max 10% of capital
        
        shares, _ = sizer.calculate_position_size(
            capital=10000,
            entry_price=10,
            stop_loss=9,
            risk_per_trade=0.5  # High risk per trade
        )
        
        # Maximum shares by capital: 10% of $10,000 = $1,000 / $10 = 100 shares
        assert shares <= 100
    
    def test_invalid_stop_loss(self):
        """Test with stop loss above entry price"""
        sizer = PositionSizer()
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                capital=10000,
                entry_price=100,
                stop_loss=105,  # Stop loss above entry price
                risk_per_trade=0.02
            )

# ============================================================================
# PART 3: PARAMETERIZED TESTS
# ============================================================================

@pytest.mark.parametrize("window,price_series,expected_sma", [
    (2, [10, 20, 30], [np.nan, 15.0, 25.0]),
    (3, [5, 10, 15, 20], [np.nan, np.nan, 10.0, 15.0]),
    (1, [100, 200, 300], [100.0, 200.0, 300.0]),
])
def test_sma_parameterized(window, price_series, expected_sma):
    """Parameterized test for SMA calculation"""
    sma = SimpleMovingAverage(window=window)
    prices = pd.Series(price_series)
    
    result = sma.calculate(prices)
    expected = pd.Series(expected_sma)
    
    pd.testing.assert_series_equal(result, expected)

@pytest.mark.parametrize("capital,entry,stop_loss,risk_pct,expected_shares", [
    (10000, 100, 95, 0.02, 40),     # Basic case
    (5000, 50, 45, 0.01, 10),       # Different parameters
    (1000, 10, 9.5, 0.05, 10),      # Higher risk percentage
])
def test_position_sizer_parameterized(capital, entry, stop_loss, risk_pct, expected_shares):
    """Parameterized test for position sizing"""
    sizer = PositionSizer(max_position_pct=0.2)
    
    shares, risk_amount = sizer.calculate_position_size(
        capital=capital,
        entry_price=entry,
        stop_loss=stop_loss,
        risk_per_trade=risk_pct
    )
    
    assert shares == expected_shares
    # Verify risk amount calculation
    expected_risk = shares * (entry - stop_loss)
    assert risk_amount == pytest.approx(expected_risk)

# ============================================================================
# PART 4: FIXTURES FOR REUSABLE TEST DATA
# ============================================================================

@pytest.fixture
def sample_price_data():
    """Fixture providing sample price data"""
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    prices = np.random.normal(100, 10, 50).cumsum() + 1000
    return pd.Series(prices, index=dates)

@pytest.fixture
def mock_market_data():
    """Fixture providing mock market data structure"""
    return {
        'AAPL': pd.Series([150, 152, 148, 155, 153]),
        'GOOGL': pd.Series([2800, 2820, 2790, 2850, 2840]),
        'MSFT': pd.Series([330, 332, 328, 335, 334]),
    }

# ============================================================================
# PART 5: INTEGRATION TEST SKELETON
# ============================================================================

class MockExchangeAPI:
    """Mock exchange API for integration testing"""
    
    def __init__(self):
        self.balance = 10000.0
        self.positions = {}
        self.order_history = []
    
    def place_order(self, symbol: str, side: str, quantity: int, price: float):
        """Mock order placement"""
        order = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'status': 'FILLED',
            'timestamp': datetime.now()
        }
        self.order_history.append(order)
        
        # Update balance and positions (simplified)
        cost = quantity * price
        if side == 'BUY':
            self.balance -= cost
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        else:  # SELL
            self.balance += cost
            self.positions[symbol] = self.positions.get(symbol, 0) - quantity
        
        return order
    
    def get_balance(self):
        """Get current balance"""
        return self.balance
    
    def get_position(self, symbol: str):
        """Get current position for symbol"""
        return self.positions.get(symbol, 0)

def test_exchange_integration():
    """Integration test with mock exchange API"""
    # Setup
    exchange = MockExchangeAPI()
    initial_balance = exchange.get_balance()
    
    # Place buy order
    order = exchange.place_order(
        symbol='AAPL',
        side='BUY',
        quantity=10,
        price=150.0
    )
    
    # Verify order details
    assert order['symbol'] == 'AAPL'
    assert order['side'] == 'BUY'
    assert order['quantity'] == 10
    assert order['status'] == 'FILLED'
    
    # Verify balance update
    final_balance = exchange.get_balance()
    expected_balance = initial_balance - (10 * 150.0)
    assert final_balance == expected_balance
    
    # Verify position update
    position = exchange.get_position('AAPL')
    assert position == 10

# ============================================================================
# PART 6: TEST RUNNER AND COVERAGE UTILITY
# ============================================================================

def run_all_tests():
    """Run all tests and display summary"""
    print("Running Day 71: Testing Frameworks Overview")
    print("=" * 50)
    
    # In practice, you would use pytest.main() or similar
    # This is just for demonstration
    test_classes = [
        TestSimpleMovingAverage,
        TestTradeSignal,
        TestPositionSizer,
    ]
    
    for test_class in test_classes:
        print(f"\nRunning tests for {test_class.__name__}...")
        # In real implementation, instantiate and run tests
    
    print("\n" + "=" * 50)
    print("Test execution complete!")
    print("\nKey Takeaways:")
    print("1. Unit tests verify individual components in isolation")
    print("2. Parameterized tests reduce code duplication")
    print("3. Fixtures provide reusable test data")
    print("4. Integration tests verify component interactions")
    print("5. Mock objects isolate tests from external dependencies")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Demonstrate component functionality
    print("Day 71: Testing Frameworks Overview - Component Demonstration")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    prices = 100 + np.random.randn(30).cumsum() * 2
    price_series = pd.Series(prices, index=dates)
    
    # Test SMA
    sma = SimpleMovingAverage(window=10)
    sma_values = sma.calculate(price_series)
    
    print(f"\n1. SMA Calculation (window=10):")
    print(f"   First 5 prices: {price_series.iloc[:5].values.round(2)}")
    print(f"   First 5 SMA values: {sma_values.iloc[:5].values.round(2)}")
    
    # Test signal generation
    current_price = price_series.iloc[-1]
    current_sma = sma_values.iloc[-1]
    signal = sma.generate_signal(current_price, current_sma)
    
    print(f"\n2. Signal Generation:")
    print(f"   Current Price: {current_price:.2f}")
    print(f"   Current SMA: {current_sma:.2f}")
    print(f"   Generated Signal: {signal}")
    
    # Test position sizing
    sizer = PositionSizer(max_position_pct=0.1)
    shares, risk = sizer.calculate_position_size(
        capital=50000,
        entry_price=current_price,
        stop_loss=current_price * 0.95,
        risk_per_trade=0.02
    )
    
    print(f"\n3. Position Sizing:")
    print(f"   Capital: $50,000")
    print(f"   Entry Price: ${current_price:.2f}")
    print(f"   Stop Loss: ${current_price * 0.95:.2f}")
    print(f"   Calculated Shares: {shares}")
    print(f"   Risk Amount: ${risk:.2f}")
    
    # Create trade signal
    trade_signal = TradeSignal(
        timestamp=datetime.now(),
        symbol='AAPL',
        action=signal if signal != 'HOLD' else 'BUY',
        strength=0.75,
        price=current_price
    )
    
    print(f"\n4. Trade Signal Created:")
    print(f"   Symbol: {trade_signal.symbol}")
    print(f"   Action: {trade_signal.action}")
    print(f"   Strength: {trade_signal.strength}")
    print(f"   Price: ${trade_signal.price:.2f}")
    
    print("\n" + "=" * 60)
    print("To run actual tests, execute: pytest day_seventyone.py -v")
    
    # Note: In a real project, tests would be in separate test files
    # and run using pytest command line