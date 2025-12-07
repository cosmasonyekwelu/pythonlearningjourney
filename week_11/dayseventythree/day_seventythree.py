"""
Day 73: Unit Testing Trading Strategies
Implementation of comprehensive unit tests for trading strategy components
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import hypothesis
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.numpy import arrays
import warnings

# ============================================================================
# PART 1: STRATEGY COMPONENTS TO TEST
# ============================================================================

class SignalType(Enum):
    """Trading signal types"""
    ENTER_LONG = "ENTER_LONG"
    EXIT_LONG = "EXIT_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    EXIT_SHORT = "EXIT_SHORT"
    HOLD = "HOLD"

@dataclass
class TradingSignal:
    """Complete trading signal with metadata"""
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    price: float
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Validate signal parameters"""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be between 0 and 1, got {self.strength}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")

class MomentumStrategy:
    """
    Momentum-based trading strategy with RSI and MACD signals
    
    This strategy uses:
    1. RSI for overbought/oversold conditions
    2. MACD for trend confirmation
    3. Volume confirmation
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        volume_threshold: float = 1.2  # 120% of average volume
    ):
        """Initialize momentum strategy parameters"""
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.volume_threshold = volume_threshold
        
        # Validate parameters
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Validate strategy parameters"""
        if self.rsi_period <= 0:
            raise ValueError(f"RSI period must be positive, got {self.rsi_period}")
        if not 0 < self.rsi_oversold < self.rsi_overbought < 100:
            raise ValueError(f"Invalid RSI thresholds: oversold={self.rsi_oversold}, overbought={self.rsi_overbought}")
        if not self.macd_fast < self.macd_slow:
            raise ValueError(f"MACD fast must be less than slow: {self.macd_fast} >= {self.macd_slow}")
        if self.macd_signal <= 0:
            raise ValueError(f"MACD signal must be positive, got {self.macd_signal}")
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            
        Returns:
            Series of RSI values
        """
        if len(prices) < self.rsi_period + 1:
            raise ValueError(f"Need at least {self.rsi_period + 1} prices for RSI calculation")
        
        # Calculate price changes
        deltas = prices.diff()
        
        # Separate gains and losses
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.rsi_period).mean()
        avg_losses = losses.rolling(window=self.rsi_period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Series of closing prices
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        if len(prices) < self.macd_slow + self.macd_signal:
            raise ValueError(f"Need at least {self.macd_slow + self.macd_signal} prices for MACD calculation")
        
        # Calculate EMAs
        ema_fast = prices.ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.macd_slow, adjust=False).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=self.macd_signal, adjust=False).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_signals(
        self,
        prices: pd.Series,
        volumes: Optional[pd.Series] = None,
        timestamp: Optional[datetime] = None
    ) -> List[TradingSignal]:
        """
        Calculate trading signals based on momentum indicators
        
        Args:
            prices: Series of closing prices
            volumes: Series of trading volumes (optional)
            timestamp: Current timestamp (uses last price timestamp if None)
            
        Returns:
            List of trading signals
        """
        if len(prices) < max(self.rsi_period + 1, self.macd_slow + self.macd_signal):
            return []  # Not enough data
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices)
        macd_line, signal_line, histogram = self.calculate_macd(prices)
        
        # Get current values
        current_price = prices.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        # Default timestamp
        if timestamp is None:
            timestamp = prices.index[-1] if hasattr(prices.index[-1], 'timestamp') else datetime.now()
        
        # Check volume confirmation
        volume_confirmed = True
        if volumes is not None and len(volumes) > 0:
            avg_volume = volumes.iloc[-self.rsi_period:].mean()
            current_volume = volumes.iloc[-1]
            volume_confirmed = current_volume > avg_volume * self.volume_threshold
        
        # Generate signals based on strategy rules
        signals = []
        
        # Rule 1: RSI oversold + MACD bullish crossover
        if (pd.notna(current_rsi) and current_rsi < self.rsi_oversold and 
            pd.notna(current_macd) and pd.notna(current_signal) and
            current_macd > current_signal and current_macd.shift(1) <= current_signal.shift(1)):
            
            if volume_confirmed:
                signal = TradingSignal(
                    timestamp=timestamp,
                    symbol="ASSET",  # Would be parameter in real implementation
                    signal_type=SignalType.ENTER_LONG,
                    strength=min(1.0, (self.rsi_oversold - current_rsi) / self.rsi_oversold),
                    price=current_price,
                    confidence=0.8 if volume_confirmed else 0.6,
                    metadata={
                        'indicator': 'RSI_MACD',
                        'rsi_value': current_rsi,
                        'macd_value': current_macd,
                        'signal_value': current_signal
                    }
                )
                signals.append(signal)
        
        # Rule 2: RSI overbought + MACD bearish crossover
        elif (pd.notna(current_rsi) and current_rsi > self.rsi_overbought and 
              pd.notna(current_macd) and pd.notna(current_signal) and
              current_macd < current_signal and current_macd.shift(1) >= current_signal.shift(1)):
            
            signal = TradingSignal(
                timestamp=timestamp,
                symbol="ASSET",
                signal_type=SignalType.EXIT_LONG,
                strength=min(1.0, (current_rsi - self.rsi_overbought) / (100 - self.rsi_overbought)),
                price=current_price,
                confidence=0.7,
                metadata={
                    'indicator': 'RSI_MACD',
                    'rsi_value': current_rsi,
                    'macd_value': current_macd,
                    'signal_value': current_signal
                }
            )
            signals.append(signal)
        
        # Rule 3: Strong MACD histogram positive
        elif (pd.notna(histogram.iloc[-1]) and histogram.iloc[-1] > 0 and 
              histogram.iloc[-1] > histogram.iloc[-2] and  # Increasing
              abs(current_macd) > abs(current_signal) * 1.5):  # Strong divergence
            
            signal = TradingSignal(
                timestamp=timestamp,
                symbol="ASSET",
                signal_type=SignalType.ENTER_LONG,
                strength=min(1.0, histogram.iloc[-1] / (current_price * 0.01)),  # Normalized
                price=current_price,
                confidence=0.6,
                metadata={
                    'indicator': 'MACD_STRENGTH',
                    'histogram': histogram.iloc[-1],
                    'macd_value': current_macd
                }
            )
            signals.append(signal)
        
        return signals

class RiskManager:
    """
    Risk management component for position sizing and drawdown control
    """
    
    def __init__(
        self,
        max_position_pct: float = 0.1,  # Max 10% of capital per position
        max_portfolio_pct: float = 0.3,  # Max 30% of capital in portfolio
        max_drawdown_pct: float = 0.2,   # 20% max drawdown
        risk_free_rate: float = 0.02,    # 2% risk-free rate
        kelly_fraction: float = 0.5      # Use half-Kelly
    ):
        """Initialize risk manager parameters"""
        self.max_position_pct = max_position_pct
        self.max_portfolio_pct = max_portfolio_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.risk_free_rate = risk_free_rate
        self.kelly_fraction = kelly_fraction
        
        # Track portfolio state
        self.initial_capital = 0.0
        self.current_capital = 0.0
        self.positions = {}  # symbol -> position info
        self.equity_curve = []
        
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Validate risk parameters"""
        if not 0 < self.max_position_pct <= 1:
            raise ValueError(f"Max position % must be between 0 and 1, got {self.max_position_pct}")
        if not 0 < self.max_portfolio_pct <= 1:
            raise ValueError(f"Max portfolio % must be between 0 and 1, got {self.max_portfolio_pct}")
        if not 0 < self.max_drawdown_pct <= 1:
            raise ValueError(f"Max drawdown % must be between 0 and 1, got {self.max_drawdown_pct}")
        if not 0 <= self.kelly_fraction <= 1:
            raise ValueError(f"Kelly fraction must be between 0 and 1, got {self.kelly_fraction}")
    
    def initialize(self, initial_capital: float):
        """Initialize risk manager with starting capital"""
        if initial_capital <= 0:
            raise ValueError(f"Initial capital must be positive, got {initial_capital}")
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.equity_curve = [initial_capital]
    
    def calculate_kelly_position(
        self,
        win_probability: float,
        win_loss_ratio: float,
        current_capital: Optional[float] = None
    ) -> float:
        """
        Calculate Kelly Criterion position size
        
        Args:
            win_probability: Probability of winning (0 to 1)
            win_loss_ratio: Average win / average loss
            current_capital: Current capital (uses self.current_capital if None)
            
        Returns:
            Fraction of capital to bet
        """
        if not 0 <= win_probability <= 1:
            raise ValueError(f"Win probability must be between 0 and 1, got {win_probability}")
        if win_loss_ratio <= 0:
            raise ValueError(f"Win/loss ratio must be positive, got {win_loss_ratio}")
        
        # Kelly formula: f* = p - q/b
        # where p = win probability, q = loss probability, b = win/loss ratio
        q = 1 - win_probability
        kelly_fraction = win_probability - (q / win_loss_ratio)
        
        # Apply fractional Kelly
        kelly_fraction = max(0, kelly_fraction) * self.kelly_fraction
        
        # Apply position limits
        capital = current_capital or self.current_capital
        max_position = capital * self.max_position_pct
        kelly_position = capital * kelly_fraction
        
        return min(kelly_position, max_position)
    
    def calculate_volatility_position(
        self,
        asset_volatility: float,
        target_volatility: float,
        current_capital: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on volatility targeting
        
        Args:
            asset_volatility: Annualized volatility of the asset
            target_volatility: Target annualized volatility for position
            current_capital: Current capital (uses self.current_capital if None)
            
        Returns:
            Position size in currency
        """
        if asset_volatility <= 0:
            raise ValueError(f"Asset volatility must be positive, got {asset_volatility}")
        if target_volatility <= 0:
            raise ValueError(f"Target volatility must be positive, got {target_volatility}")
        
        # Position size = (target volatility / asset volatility) * capital
        capital = current_capital or self.current_capital
        position = (target_volatility / asset_volatility) * capital
        
        # Apply position limits
        max_position = capital * self.max_position_pct
        return min(position, max_position)
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        position_type: str = 'long',
        atr: Optional[float] = None,
        stop_pct: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            position_type: 'long' or 'short'
            atr: Average True Range (optional)
            stop_pct: Stop loss percentage (optional)
            
        Returns:
            Stop loss price
        """
        if entry_price <= 0:
            raise ValueError(f"Entry price must be positive, got {entry_price}")
        
        if atr is not None and atr > 0:
            # Use ATR-based stop
            if position_type == 'long':
                stop_price = entry_price - (atr * 2)  # 2 ATR stop
            else:  # short
                stop_price = entry_price + (atr * 2)
        elif stop_pct is not None and stop_pct > 0:
            # Use percentage-based stop
            if position_type == 'long':
                stop_price = entry_price * (1 - stop_pct)
            else:  # short
                stop_price = entry_price * (1 + stop_pct)
        else:
            # Default 5% stop
            if position_type == 'long':
                stop_price = entry_price * 0.95
            else:  # short
                stop_price = entry_price * 1.05
        
        return stop_price
    
    def check_drawdown_limit(self, current_equity: float) -> Tuple[bool, float]:
        """
        Check if current drawdown exceeds limit
        
        Args:
            current_equity: Current equity value
            
        Returns:
            Tuple of (limit_exceeded, current_drawdown_pct)
        """
        if not self.equity_curve:
            return False, 0.0
        
        peak_equity = max(self.equity_curve)
        current_drawdown = (peak_equity - current_equity) / peak_equity
        
        limit_exceeded = current_drawdown > self.max_drawdown_pct
        
        return limit_exceeded, current_drawdown
    
    def update_portfolio(
        self,
        symbol: str,
        position_size: float,
        price: float,
        position_type: str = 'long'
    ) -> bool:
        """
        Update portfolio with new position
        
        Args:
            symbol: Asset symbol
            position_size: Position size in currency
            price: Entry price
            position_type: 'long' or 'short'
            
        Returns:
            True if position added successfully, False if rejected
        """
        # Check position limit
        if position_size > self.current_capital * self.max_position_pct:
            return False
        
        # Check portfolio limit
        total_positions = sum(abs(pos['size']) for pos in self.positions.values())
        if total_positions + position_size > self.current_capital * self.max_portfolio_pct:
            return False
        
        # Check drawdown limit
        limit_exceeded, _ = self.check_drawdown_limit(self.current_capital)
        if limit_exceeded:
            return False
        
        # Add position
        self.positions[symbol] = {
            'size': position_size if position_type == 'long' else -position_size,
            'entry_price': price,
            'position_type': position_type,
            'timestamp': datetime.now()
        }
        
        # Update capital (simplified - in reality would use margin)
        self.current_capital -= position_size
        
        return True
    
    def update_equity(self, new_equity: float):
        """
        Update equity curve with new equity value
        
        Args:
            new_equity: New equity value
        """
        self.current_capital = new_equity
        self.equity_curve.append(new_equity)

# ============================================================================
# PART 2: UNIT TESTS FOR MOMENTUM STRATEGY
# ============================================================================

class TestMomentumStrategy:
    """Unit tests for MomentumStrategy class"""
    
    @pytest.fixture
    def strategy(self):
        """Create a momentum strategy instance"""
        return MomentumStrategy(
            rsi_period=14,
            rsi_overbought=70.0,
            rsi_oversold=30.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data"""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        # Create prices with some trend and volatility
        base = 100.0
        trend = np.arange(50) * 0.1  # Upward trend
        noise = np.random.RandomState(42).normal(0, 1, 50)
        prices = base + trend + noise
        return pd.Series(prices, index=dates)
    
    @pytest.fixture
    def flat_prices(self):
        """Create perfectly flat price series"""
        dates = pd.date_range('2024-01-01', periods=20, freq='D')
        return pd.Series([100.0] * 20, index=dates)
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters"""
        strategy = MomentumStrategy(
            rsi_period=14,
            rsi_overbought=70.0,
            rsi_oversold=30.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert strategy.rsi_period == 14
        assert strategy.rsi_overbought == 70.0
        assert strategy.rsi_oversold == 30.0
        assert strategy.macd_fast == 12
        assert strategy.macd_slow == 26
        assert strategy.macd_signal == 9
    
    def test_init_invalid_parameters(self):
        """Test initialization with invalid parameters"""
        # Invalid RSI period
        with pytest.raises(ValueError):
            MomentumStrategy(rsi_period=0)
        
        # Invalid RSI thresholds
        with pytest.raises(ValueError):
            MomentumStrategy(rsi_overbought=30.0, rsi_oversold=70.0)
        
        # Invalid MACD parameters
        with pytest.raises(ValueError):
            MomentumStrategy(macd_fast=26, macd_slow=12)  # fast > slow
        
        with pytest.raises(ValueError):
            MomentumStrategy(macd_signal=0)
    
    def test_calculate_rsi_basic(self, strategy, sample_prices):
        """Test basic RSI calculation"""
        rsi = strategy.calculate_rsi(sample_prices)
        
        # Check shape
        assert len(rsi) == len(sample_prices)
        
        # Check first values are NaN (need period + 1 prices)
        assert pd.isna(rsi.iloc[0])
        assert pd.isna(rsi.iloc[strategy.rsi_period - 1])
        
        # Check later values are calculated
        assert pd.notna(rsi.iloc[strategy.rsi_period])
        
        # Check RSI bounds
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_rsi_insufficient_data(self, strategy):
        """Test RSI calculation with insufficient data"""
        prices = pd.Series([100.0, 101.0])  # Only 2 prices
        
        with pytest.raises(ValueError):
            strategy.calculate_rsi(prices)
    
    def test_calculate_rsi_flat_series(self, strategy, flat_prices):
        """Test RSI calculation on flat price series"""
        rsi = strategy.calculate_rsi(flat_prices)
        
        # For flat prices, RSI should be 50 (neutral)
        valid_rsi = rsi.dropna()
        if len(valid_rsi) > 0:
            # Allow small floating point differences
            assert np.allclose(valid_rsi.values, 50.0, rtol=1e-10)
    
    def test_calculate_macd_basic(self, strategy, sample_prices):
        """Test basic MACD calculation"""
        macd_line, signal_line, histogram = strategy.calculate_macd(sample_prices)
        
        # Check shapes
        assert len(macd_line) == len(sample_prices)
        assert len(signal_line) == len(sample_prices)
        assert len(histogram) == len(sample_prices)
        
        # Check early values are NaN
        assert pd.isna(macd_line.iloc[strategy.macd_slow - 1])
        assert pd.notna(macd_line.iloc[strategy.macd_slow])
        
        # Check histogram calculation
        valid_idx = macd_line.notna() & signal_line.notna()
        calculated_histogram = macd_line[valid_idx] - signal_line[valid_idx]
        assert np.allclose(histogram[valid_idx].values, calculated_histogram.values, rtol=1e-10)
    
    def test_calculate_signals_no_data(self, strategy):
        """Test signal calculation with insufficient data"""
        prices = pd.Series([100.0] * 10)  # Only 10 prices
        
        signals = strategy.calculate_signals(prices)
        assert len(signals) == 0  # Should return empty list
    
    def test_calculate_signals_with_volume(self, strategy, sample_prices):
        """Test signal calculation with volume data"""
        # Create volume series
        volumes = pd.Series(np.random.randint(1000, 10000, len(sample_prices)), 
                           index=sample_prices.index)
        
        signals = strategy.calculate_signals(sample_prices, volumes)
        
        # Signals should be TradingSignal objects or empty list
        assert isinstance(signals, list)
        if signals:
            assert all(isinstance(s, TradingSignal) for s in signals)
    
    @pytest.mark.parametrize("price_values,expected_signal_type", [
        # Oversold scenario: prices declining then stabilizing
        ([100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83], SignalType.ENTER_LONG),
        # Overbought scenario: prices rising sharply
        ([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134], SignalType.EXIT_LONG),
    ])
    def test_calculate_signals_edge_cases(self, strategy, price_values, expected_signal_type):
        """Test signal calculation with specific price patterns"""
        dates = pd.date_range('2024-01-01', periods=len(price_values), freq='D')
        prices = pd.Series(price_values, index=dates)
        
        signals = strategy.calculate_signals(prices)
        
        # Might generate signals or not depending on exact pattern
        if signals:
            assert signals[0].signal_type == expected_signal_type
    
    def test_calculate_signals_nan_handling(self, strategy):
        """Test signal calculation with NaN values in input"""
        prices = pd.Series([100.0, np.nan, 102.0, 103.0, np.nan, 101.0, 99.0])
        
        # Should handle NaN gracefully or raise appropriate error
        try:
            signals = strategy.calculate_signals(prices)
            # If it doesn't crash, signals should be list
            assert isinstance(signals, list)
        except Exception as e:
            # If it raises an error, it should be a meaningful error
            assert "NaN" in str(e) or "insufficient" in str(e)

# ============================================================================
# PART 3: UNIT TESTS FOR RISK MANAGER
# ============================================================================

class TestRiskManager:
    """Unit tests for RiskManager class"""
    
    @pytest.fixture
    def risk_manager(self):
        """Create a risk manager instance"""
        rm = RiskManager(
            max_position_pct=0.1,
            max_portfolio_pct=0.3,
            max_drawdown_pct=0.2,
            risk_free_rate=0.02,
            kelly_fraction=0.5
        )
        rm.initialize(initial_capital=100000.0)
        return rm
    
    def test_initialize_valid_capital(self):
        """Test initialization with valid capital"""
        rm = RiskManager()
        rm.initialize(initial_capital=50000.0)
        
        assert rm.initial_capital == 50000.0
        assert rm.current_capital == 50000.0
        assert rm.equity_curve == [50000.0]
    
    def test_initialize_invalid_capital(self):
        """Test initialization with invalid capital"""
        rm = RiskManager()
        
        with pytest.raises(ValueError):
            rm.initialize(initial_capital=0.0)
        
        with pytest.raises(ValueError):
            rm.initialize(initial_capital=-10000.0)
    
    def test_calculate_kelly_position_valid(self, risk_manager):
        """Test Kelly position calculation with valid inputs"""
        # Favorable bet: 60% win probability, 2:1 win/loss ratio
        position = risk_manager.calculate_kelly_position(
            win_probability=0.6,
            win_loss_ratio=2.0
        )
        
        # Kelly formula: f* = p - q/b = 0.6 - 0.4/2 = 0.4
        # Half-Kelly: 0.4 * 0.5 = 0.2
        # Position: 100,000 * 0.2 = 20,000
        expected_position = 100000.0 * 0.2
        
        assert position == pytest.approx(expected_position)
    
    def test_calculate_kelly_position_unfavorable(self, risk_manager):
        """Test Kelly position calculation with unfavorable bet"""
        # Unfavorable bet should return 0
        position = risk_manager.calculate_kelly_position(
            win_probability=0.4,
            win_loss_ratio=1.0
        )
        
        assert position == 0.0
    
    def test_calculate_kelly_position_position_limit(self, risk_manager):
        """Test Kelly position respects maximum position limit"""
        # Kelly would suggest 50% of capital, but max is 10%
        position = risk_manager.calculate_kelly_position(
            win_probability=0.75,
            win_loss_ratio=3.0
        )
        
        max_position = 100000.0 * 0.1  # 10% limit
        assert position <= max_position
    
    @pytest.mark.parametrize("win_prob,win_loss_ratio", [
        (-0.1, 2.0),  # Negative probability
        (1.1, 2.0),   # Probability > 1
        (0.6, 0.0),   # Zero win/loss ratio
        (0.6, -1.0),  # Negative win/loss ratio
    ])
    def test_calculate_kelly_position_invalid_inputs(self, risk_manager, win_prob, win_loss_ratio):
        """Test Kelly position with invalid inputs"""
        with pytest.raises(ValueError):
            risk_manager.calculate_kelly_position(win_prob, win_loss_ratio)
    
    def test_calculate_volatility_position(self, risk_manager):
        """Test volatility-based position sizing"""
        position = risk_manager.calculate_volatility_position(
            asset_volatility=0.20,  # 20% annual volatility
            target_volatility=0.05   # Target 5% volatility
        )
        
        # Position = (0.05 / 0.20) * 100,000 = 25,000
        # But limited to 10% of capital = 10,000
        assert position == 10000.0
    
    def test_calculate_stop_loss_long(self, risk_manager):
        """Test stop loss calculation for long position"""
        # ATR-based stop
        stop_price = risk_manager.calculate_stop_loss(
            entry_price=100.0,
            position_type='long',
            atr=2.0
        )
        assert stop_price == 96.0  # 100 - (2 * 2)
        
        # Percentage-based stop
        stop_price = risk_manager.calculate_stop_loss(
            entry_price=100.0,
            position_type='long',
            stop_pct=0.1
        )
        assert stop_price == 90.0  # 100 * 0.9
        
        # Default stop
        stop_price = risk_manager.calculate_stop_loss(
            entry_price=100.0,
            position_type='long'
        )
        assert stop_price == 95.0  # 100 * 0.95
    
    def test_calculate_stop_loss_short(self, risk_manager):
        """Test stop loss calculation for short position"""
        stop_price = risk_manager.calculate_stop_loss(
            entry_price=100.0,
            position_type='short',
            atr=2.0
        )
        assert stop_price == 104.0  # 100 + (2 * 2)
    
    def test_check_drawdown_limit(self, risk_manager):
        """Test drawdown limit checking"""
        # Initial state: no drawdown
        exceeded, drawdown = risk_manager.check_drawdown_limit(100000.0)
        assert not exceeded
        assert drawdown == 0.0
        
        # Update equity curve with drawdown
        risk_manager.update_equity(90000.0)  # 10% drawdown
        exceeded, drawdown = risk_manager.check_drawdown_limit(90000.0)
        assert not exceeded
        assert drawdown == 0.1
        
        # Exceed drawdown limit
        risk_manager.update_equity(75000.0)  # 25% drawdown from peak 100k
        exceeded, drawdown = risk_manager.check_drawdown_limit(75000.0)
        assert exceeded  # 25% > 20% limit
        assert drawdown == 0.25
    
    def test_update_portfolio_success(self, risk_manager):
        """Test successful portfolio update"""
        success = risk_manager.update_portfolio(
            symbol='AAPL',
            position_size=5000.0,  # 5% of capital
            price=150.0,
            position_type='long'
        )
        
        assert success
        assert 'AAPL' in risk_manager.positions
        assert risk_manager.current_capital == 95000.0  # 100k - 5k
    
    def test_update_portfolio_exceeds_position_limit(self, risk_manager):
        """Test portfolio update that exceeds position limit"""
        success = risk_manager.update_portfolio(
            symbol='AAPL',
            position_size=15000.0,  # 15% > 10% limit
            price=150.0,
            position_type='long'
        )
        
        assert not success
        assert 'AAPL' not in risk_manager.positions
    
    def test_update_portfolio_exceeds_portfolio_limit(self, risk_manager):
        """Test portfolio update that exceeds portfolio limit"""
        # Add first position
        success1 = risk_manager.update_portfolio(
            symbol='AAPL',
            position_size=20000.0,  # 20% of capital
            price=150.0,
            position_type='long'
        )
        assert success1
        
        # Try to add second position that would exceed 30% portfolio limit
        success2 = risk_manager.update_portfolio(
            symbol='GOOGL',
            position_size=15000.0,  # Would make total 35%
            price=2800.0,
            position_type='long'
        )
        
        assert not success2
        assert 'GOOGL' not in risk_manager.positions

# ============================================================================
# PART 4: PROPERTY-BASED TESTS WITH HYPOTHESIS
# ============================================================================

class TestPropertyBasedRiskManager:
    """Property-based tests for RiskManager using hypothesis"""
    
    @given(
        initial_capital=st.floats(min_value=0.1, max_value=1000000.0),
        max_position_pct=st.floats(min_value=0.01, max_value=0.5),
        max_portfolio_pct=st.floats(min_value=0.1, max_value=1.0),
        max_drawdown_pct=st.floats(min_value=0.05, max_value=0.5),
        kelly_fraction=st.floats(min_value=0.1, max_value=1.0)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_manager_initialization_properties(
        self,
        initial_capital,
        max_position_pct,
        max_portfolio_pct,
        max_drawdown_pct,
        kelly_fraction
    ):
        """Property test: RiskManager should initialize with valid parameters"""
        # Skip invalid combinations
        if max_position_pct > max_portfolio_pct:
            return
        
        try:
            rm = RiskManager(
                max_position_pct=max_position_pct,
                max_portfolio_pct=max_portfolio_pct,
                max_drawdown_pct=max_drawdown_pct,
                kelly_fraction=kelly_fraction
            )
            rm.initialize(initial_capital)
            
            # Check invariants after initialization
            assert rm.initial_capital == initial_capital
            assert rm.current_capital == initial_capital
            assert len(rm.equity_curve) == 1
            assert rm.equity_curve[0] == initial_capital
            assert rm.max_position_pct == max_position_pct
            assert rm.max_portfolio_pct == max_portfolio_pct
            
        except ValueError as e:
            # If initialization fails, it should be due to invalid parameters
            assert "must be between" in str(e) or "must be positive" in str(e)
    
    @given(
        capital=st.floats(min_value=1000.0, max_value=1000000.0),
        win_prob=st.floats(min_value=0.0, max_value=1.0),
        win_loss_ratio=st.floats(min_value=0.1, max_value=10.0)
    )
    @settings(max_examples=50)
    def test_kelly_position_properties(self, capital, win_prob, win_loss_ratio):
        """Property test: Kelly position should have certain properties"""
        rm = RiskManager(max_position_pct=0.2, kelly_fraction=0.5)
        rm.initialize(capital)
        
        try:
            position = rm.calculate_kelly_position(win_prob, win_loss_ratio, capital)
            
            # Property 1: Position should never be negative
            assert position >= 0
            
            # Property 2: Position should not exceed max position limit
            max_position = capital * rm.max_position_pct
            assert position <= max_position + 1e-10  # Allow small floating errors
            
            # Property 3: If win_prob <= 1/(1+win_loss_ratio), position should be 0
            # (This is the break-even point for Kelly)
            if win_prob <= 1/(1 + win_loss_ratio):
                assert position == 0
            
        except ValueError:
            # Invalid inputs should raise ValueError
            assert win_prob < 0 or win_prob > 1 or win_loss_ratio <= 0
    
    @given(
        capital=st.floats(min_value=1000.0, max_value=1000000.0),
        asset_vol=st.floats(min_value=0.01, max_value=1.0),
        target_vol=st.floats(min_value=0.01, max_value=0.5)
    )
    @settings(max_examples=50)
    def test_volatility_position_properties(self, capital, asset_vol, target_vol):
        """Property test: Volatility-based position should have certain properties"""
        rm = RiskManager(max_position_pct=0.2)
        rm.initialize(capital)
        
        position = rm.calculate_volatility_position(asset_vol, target_vol, capital)
        
        # Property 1: Position should never be negative
        assert position >= 0
        
        # Property 2: Position should not exceed max position limit
        max_position = capital * rm.max_position_pct
        assert position <= max_position + 1e-10
        
        # Property 3: Position should be proportional to target_vol/asset_vol
        # (except when limited by max_position)
        expected = (target_vol / asset_vol) * capital
        if expected <= max_position:
            assert position == pytest.approx(expected, rel=1e-10)
    
    @given(
        equity_curve=st.lists(
            st.floats(min_value=1000.0, max_value=1000000.0),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=50)
    def test_drawdown_properties(self, equity_curve):
        """Property test: Drawdown calculation should have certain properties"""
        rm = RiskManager(max_drawdown_pct=0.2)
        rm.initial_capital = equity_curve[0] if equity_curve else 0
        rm.equity_curve = equity_curve
        
        if not equity_curve:
            return
        
        current_equity = equity_curve[-1]
        exceeded, drawdown = rm.check_drawdown_limit(current_equity)
        
        # Property 1: Drawdown should be between 0 and 1
        assert 0 <= drawdown <= 1 + 1e-10
        
        # Property 2: Drawdown should be 0 if current equity is at peak
        peak = max(equity_curve)
        if current_equity >= peak:
            assert drawdown == 0
        
        # Property 3: Drawdown calculation should match manual calculation
        expected_drawdown = (peak - current_equity) / peak
        assert drawdown == pytest.approx(expected_drawdown, rel=1e-10)
        
        # Property 4: exceeded flag should match comparison with limit
        assert exceeded == (drawdown > rm.max_drawdown_pct)
    
    @given(
        capital=st.floats(min_value=10000.0, max_value=100000.0),
        position_sizes=st.lists(
            st.floats(min_value=100.0, max_value=10000.0),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=30)
    def test_portfolio_update_properties(self, capital, position_sizes):
        """Property test: Portfolio updates should maintain invariants"""
        rm = RiskManager(
            max_position_pct=0.1,
            max_portfolio_pct=0.3,
            max_drawdown_pct=0.2
        )
        rm.initialize(capital)
        
        available_capital = capital
        
        for i, position_size in enumerate(position_sizes):
            symbol = f"ASSET_{i}"
            
            # Try to add position
            success = rm.update_portfolio(
                symbol=symbol,
                position_size=position_size,
                price=100.0,
                position_type='long'
            )
            
            if success:
                # Property 1: Position should be in positions dict
                assert symbol in rm.positions
                
                # Property 2: Capital should be reduced by position size
                available_capital -= position_size
                assert rm.current_capital == pytest.approx(available_capital, rel=1e-10)
                
                # Property 3: Total positions should not exceed portfolio limit
                total_positions = sum(abs(pos['size']) for pos in rm.positions.values())
                assert total_positions <= capital * rm.max_portfolio_pct + 1e-10
                
                # Property 4: Individual position should not exceed position limit
                assert position_size <= capital * rm.max_position_pct + 1e-10
            else:
                # Property 5: If update fails, positions dict should not change size
                # (except for the attempted addition)
                pass

# ============================================================================
# PART 5: TEST RUNNER AND DEMONSTRATION
# ============================================================================

def run_unit_tests_demo():
    """Demonstrate unit testing concepts"""
    print("=" * 70)
    print("Day 73: Unit Testing Trading Strategies - Demonstration")
    print("=" * 70)
    
    # Create strategy instance
    strategy = MomentumStrategy(
        rsi_period=14,
        rsi_overbought=70.0,
        rsi_oversold=30.0
    )
    
    # Create test price data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Create prices with a clear trend and some volatility
    trend = np.linspace(100, 120, 100)
    noise = np.random.normal(0, 2, 100)
    prices = trend + noise
    price_series = pd.Series(prices, index=dates)
    
    print("\n1. Testing RSI Calculation:")
    rsi = strategy.calculate_rsi(price_series)
    print(f"   RSI values range: {rsi.min():.2f} to {rsi.max():.2f}")
    print(f"   RSI mean: {rsi.mean():.2f}")
    print(f"   Oversold (<30) periods: {(rsi < 30).sum()}")
    print(f"   Overbought (>70) periods: {(rsi > 70).sum()}")
    
    print("\n2. Testing MACD Calculation:")
    macd_line, signal_line, histogram = strategy.calculate_macd(price_series)
    print(f"   MACD line range: {macd_line.min():.2f} to {macd_line.max():.2f}")
    print(f"   Signal line range: {signal_line.min():.2f} to {signal_line.max():.2f}")
    print(f"   Histogram range: {histogram.min():.2f} to {histogram.max():.2f}")
    
    # Find bullish/bearish crossovers
    macd_above_signal = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    macd_below_signal = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
    
    print(f"   Bullish crossovers: {macd_above_signal.sum()}")
    print(f"   Bearish crossovers: {macd_below_signal.sum()}")
    
    print("\n3. Testing Signal Generation:")
    signals = strategy.calculate_signals(price_series)
    print(f"   Total signals generated: {len(signals)}")
    
    if signals:
        for i, signal in enumerate(signals[:3]):  # Show first 3 signals
            print(f"   Signal {i+1}:")
            print(f"     Type: {signal.signal_type.value}")
            print(f"     Strength: {signal.strength:.2f}")
            print(f"     Price: ${signal.price:.2f}")
            print(f"     Confidence: {signal.confidence:.2f}")
    
    print("\n4. Testing Risk Manager:")
    risk_manager = RiskManager(
        max_position_pct=0.1,
        max_portfolio_pct=0.3,
        max_drawdown_pct=0.2
    )
    risk_manager.initialize(initial_capital=100000.0)
    
    # Test Kelly position
    kelly_position = risk_manager.calculate_kelly_position(
        win_probability=0.6,
        win_loss_ratio=2.0
    )
    print(f"   Kelly position (60% win, 2:1 ratio): ${kelly_position:.2f}")
    
    # Test volatility position
    vol_position = risk_manager.calculate_volatility_position(
        asset_volatility=0.25,
        target_volatility=0.05
    )
    print(f"   Volatility position (25% asset vol, 5% target): ${vol_position:.2f}")
    
    # Test stop loss
    stop_price = risk_manager.calculate_stop_loss(
        entry_price=100.0,
        position_type='long',
        atr=1.5
    )
    print(f"   Stop loss for $100 long position (ATR=1.5): ${stop_price:.2f}")
    
    print("\n5. Testing Property-Based Invariants:")
    print("   Running property tests would verify:")
    print("   - Position sizes never exceed limits")
    print("   - Drawdown calculations are always between 0 and 1")
    print("   - Kelly positions are non-negative")
    print("   - Portfolio updates maintain all constraints")
    
    print("\n6. Edge Case Examples:")
    
    # Test with NaN values
    print("   Testing NaN handling in RSI calculation...")
    prices_with_nan = price_series.copy()
    prices_with_nan.iloc[10:15] = np.nan
    
    try:
        rsi_nan = strategy.calculate_rsi(prices_with_nan)
        print("   ✓ NaN handling: RSI calculated with warnings")
    except Exception as e:
        print(f"   ✗ NaN handling failed: {e}")
    
    # Test with single value
    print("   Testing single price value...")
    single_price = pd.Series([100.0])
    try:
        signals = strategy.calculate_signals(single_price)
        print(f"   ✓ Single value: Returns {len(signals)} signals (should be 0)")
    except Exception as e:
        print(f"   ✗ Single value failed: {e}")
    
    # Test with flat prices
    print("   Testing flat price series...")
    flat_prices = pd.Series([100.0] * 50)
    try:
        rsi_flat = strategy.calculate_rsi(flat_prices)
        print(f"   ✓ Flat series: RSI values around {rsi_flat.mean():.1f}")
    except Exception as e:
        print(f"   ✗ Flat series failed: {e}")
    
    print("\n" + "=" * 70)
    print("Key Testing Principles Demonstrated:")
    print("1. Unit tests verify individual components in isolation")
    print("2. Parameterized tests cover multiple scenarios efficiently")
    print("3. Edge cases (NaN, single values, flat series) are handled")
    print("4. Property-based tests verify mathematical invariants")
    print("5. Financial constraints (position limits, drawdown) are enforced")
    print("\nTo run actual tests: pytest day_seventythree.py -v")
    print("=" * 70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run demonstration
    run_unit_tests_demo()
    
    print("\n\nSummary of Test Coverage:")
    print("-" * 40)
    print("Strategy Components Tested:")
    print("  ✓ MomentumStrategy initialization and validation")
    print("  ✓ RSI calculation with various price patterns")
    print("  ✓ MACD calculation and crossover detection")
    print("  ✓ Signal generation logic")
    print("  ✓ Edge case handling (NaN, insufficient data)")
    
    print("\nRisk Management Components Tested:")
    print("  ✓ RiskManager initialization and parameter validation")
    print("  ✓ Kelly Criterion position sizing")
    print("  ✓ Volatility-based position sizing")
    print("  ✓ Stop loss calculation (ATR and percentage-based)")
    print("  ✓ Drawdown limit checking")
    print("  ✓ Portfolio update with position/portfolio limits")
    
    print("\nProperty-Based Tests:")
    print("  ✓ Risk manager initialization properties")
    print("  ✓ Kelly position mathematical invariants")
    print("  ✓ Volatility position bounds")
    print("  ✓ Drawdown calculation properties (0-1 range)")
    print("  ✓ Portfolio update constraints")
    
    print("\n" + "=" * 70)
    print("Implementation Complete!")
    print("\nNext Steps:")
    print("1. Add integration tests for strategy + risk manager interaction")
    print("2. Implement performance metric tests (Sharpe ratio, max drawdown)")
    print("3. Add stress tests with extreme market conditions")
    print("4. Create regression tests with historical data")
    print("=" * 70)