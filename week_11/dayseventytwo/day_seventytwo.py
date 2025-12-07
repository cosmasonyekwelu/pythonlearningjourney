"""
Day 72: Setting Up a Test Environment
Implementation of isolated testing environments and synthetic data generation for financial applications
"""

import os
import yaml
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import docker
from docker.models.containers import Container
import tempfile
import shutil
import hashlib
from abc import ABC, abstractmethod
import logging
from logging.handlers import RotatingFileHandler

# ============================================================================
# PART 1: CONFIGURATION MANAGEMENT
# ============================================================================

class EnvironmentMode(Enum):
    """Environment modes for trading system"""
    TEST = "test"
    PAPER = "paper"
    LIVE = "live"
    DEVELOPMENT = "development"

@dataclass
class TestEnvironmentConfig:
    """Configuration for test environment"""
    
    # Environment settings
    mode: EnvironmentMode = EnvironmentMode.TEST
    data_source: str = "synthetic"  # synthetic, historical, api
    
    # Synthetic data parameters
    synthetic_base_price: float = 100.0
    synthetic_volatility: float = 0.02  # daily volatility
    synthetic_trend_direction: float = 0.0  # daily drift
    synthetic_seed: Optional[int] = 42
    
    # Data parameters
    default_start_date: str = "2024-01-01"
    default_end_date: str = "2024-03-31"
    default_timeframe: str = "1D"  # 1D, 1H, 15min
    
    # Test parameters
    max_test_duration_seconds: int = 300
    enable_parallel_tests: bool = False
    log_level: str = "INFO"
    
    # API settings (for integration tests)
    api_timeout_seconds: int = 30
    api_retry_attempts: int = 3
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "test_trading"
    db_user: str = "test_user"
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'TestEnvironmentConfig':
        """Load configuration from YAML file"""
        with open(filepath, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Convert mode string to Enum
        if 'mode' in config_dict:
            config_dict['mode'] = EnvironmentMode(config_dict['mode'])
        
        return cls(**config_dict)
    
    def to_yaml(self, filepath: str) -> None:
        """Save configuration to YAML file"""
        config_dict = self.__dict__.copy()
        config_dict['mode'] = config_dict['mode'].value
        
        with open(filepath, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

# ============================================================================
# PART 2: SYNTHETIC DATA GENERATION
# ============================================================================

class VolatilityRegime(Enum):
    """Market volatility regimes"""
    LOW = "low"      # Stable market
    MEDIUM = "medium" # Normal market
    HIGH = "high"    # Volatile market
    CRISIS = "crisis" # Extreme volatility

class TrendType(Enum):
    """Market trend patterns"""
    SIDEWAYS = "sideways"
    UPWARD = "upward"
    DOWNWARD = "downward"
    CYCLICAL = "cyclical"
    MEAN_REVERTING = "mean_reverting"

class DataFixture:
    """
    Configurable synthetic market data generator for testing
    
    Generates realistic OHLCV data with controlled statistical properties
    """
    
    def __init__(
        self,
        config: Optional[TestEnvironmentConfig] = None,
        random_seed: Optional[int] = None
    ):
        """
        Initialize DataFixture
        
        Args:
            config: Test environment configuration
            random_seed: Random seed for reproducibility
        """
        self.config = config or TestEnvironmentConfig()
        self.random_seed = random_seed or self.config.synthetic_seed
        self.rng = np.random.default_rng(self.random_seed)
        
        # Define volatility parameters for different regimes
        self.volatility_params = {
            VolatilityRegime.LOW: {
                'daily_vol': 0.005,
                'vol_clusters': False,
                'jump_probability': 0.001
            },
            VolatilityRegime.MEDIUM: {
                'daily_vol': 0.015,
                'vol_clusters': True,
                'jump_probability': 0.005
            },
            VolatilityRegime.HIGH: {
                'daily_vol': 0.03,
                'vol_clusters': True,
                'jump_probability': 0.01
            },
            VolatilityRegime.CRISIS: {
                'daily_vol': 0.05,
                'vol_clusters': True,
                'jump_probability': 0.02
            }
        }
        
        # Define trend parameters
        self.trend_params = {
            TrendType.SIDEWAYS: {
                'daily_drift': 0.0,
                'trend_strength': 0.0
            },
            TrendType.UPWARD: {
                'daily_drift': 0.0005,  # ~12.7% annual return
                'trend_strength': 0.8
            },
            TrendType.DOWNWARD: {
                'daily_drift': -0.0005,  # ~-12.7% annual decline
                'trend_strength': 0.8
            },
            TrendType.CYCLICAL: {
                'daily_drift': 0.0,
                'trend_strength': 0.6,
                'cycle_period_days': 63  # ~3 months
            },
            TrendType.MEAN_REVERTING: {
                'daily_drift': 0.0,
                'trend_strength': 0.7,
                'mean_reversion_speed': 0.1
            }
        }
    
    def generate_ohlcv(
        self,
        ticker: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        timeframe: str = "1D",
        base_price: Optional[float] = None,
        volatility_regime: Union[VolatilityRegime, str] = VolatilityRegime.MEDIUM,
        trend_type: Union[TrendType, str] = TrendType.SIDEWAYS,
        include_gaps: bool = False,
        gap_probability: float = 0.01,
        volume_profile: str = "normal"
    ) -> pd.DataFrame:
        """
        Generate synthetic OHLCV data
        
        Args:
            ticker: Symbol/ticker name
            start_date: Start date for data
            end_date: End date for data
            timeframe: Bar timeframe (1D, 1H, 15min, etc.)
            base_price: Starting price (if None, uses config)
            volatility_regime: Market volatility regime
            trend_type: Market trend pattern
            include_gaps: Whether to include missing data periods
            gap_probability: Probability of a gap occurring
            volume_profile: Volume generation profile
            
        Returns:
            DataFrame with OHLCV columns
        """
        # Parse inputs
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        if isinstance(volatility_regime, str):
            volatility_regime = VolatilityRegime(volatility_regime)
        if isinstance(trend_type, str):
            trend_type = TrendType(trend_type)
        
        # Generate date range
        freq_map = {
            "1D": "B",  # Business days
            "1H": "H",
            "15min": "15min",
            "5min": "5min",
            "1min": "T"
        }
        
        freq = freq_map.get(timeframe, "B")
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        if len(dates) == 0:
            raise ValueError(f"No dates generated for range {start_date} to {end_date}")
        
        # Get parameters
        base_price = base_price or self.config.synthetic_base_price
        vol_params = self.volatility_params[volatility_regime]
        trend_params = self.trend_params[trend_type]
        
        # Generate returns
        n_periods = len(dates)
        returns = self._generate_returns(
            n_periods=n_periods,
            vol_params=vol_params,
            trend_params=trend_params,
            trend_type=trend_type
        )
        
        # Generate prices from returns
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Generate OHLC from prices
        ohlc_data = self._generate_ohlc_from_prices(prices, volatility_regime)
        
        # Generate volume
        volumes = self._generate_volume(
            n_periods=n_periods,
            price_series=prices,
            profile=volume_profile,
            volatility_regime=volatility_regime
        )
        
        # Create DataFrame
        df = pd.DataFrame(
            data={
                'open': ohlc_data['open'],
                'high': ohlc_data['high'],
                'low': ohlc_data['low'],
                'close': ohlc_data['close'],
                'volume': volumes
            },
            index=dates
        )
        
        # Add ticker column
        df['ticker'] = ticker
        
        # Introduce gaps if requested
        if include_gaps and gap_probability > 0:
            df = self._introduce_data_gaps(df, gap_probability)
        
        # Reorder columns
        df = df[['ticker', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def _generate_returns(
        self,
        n_periods: int,
        vol_params: Dict[str, Any],
        trend_params: Dict[str, Any],
        trend_type: TrendType
    ) -> np.ndarray:
        """Generate log returns with specified properties"""
        
        # Base returns with volatility clustering
        if vol_params['vol_clusters']:
            # GARCH-like volatility clustering
            returns = np.zeros(n_periods)
            vol = vol_params['daily_vol']
            
            for i in range(1, n_periods):
                # Volatility persistence
                vol = 0.9 * vol + 0.1 * vol_params['daily_vol'] + 0.05 * self.rng.normal(0, 0.01)
                vol = max(0.001, vol)  # Ensure positive volatility
                
                # Generate return
                returns[i] = self.rng.normal(0, vol)
        else:
            # Simple normal returns
            returns = self.rng.normal(0, vol_params['daily_vol'], n_periods)
        
        # Add jumps
        if vol_params['jump_probability'] > 0:
            jump_mask = self.rng.random(n_periods) < vol_params['jump_probability']
            jump_size = self.rng.normal(0, vol_params['daily_vol'] * 5, n_periods)
            returns[jump_mask] += jump_size[jump_mask]
        
        # Add trend component
        returns += self._apply_trend_pattern(
            returns=returns,
            trend_params=trend_params,
            trend_type=trend_type
        )
        
        return returns
    
    def _apply_trend_pattern(
        self,
        returns: np.ndarray,
        trend_params: Dict[str, Any],
        trend_type: TrendType
    ) -> np.ndarray:
        """Apply specific trend pattern to returns"""
        n_periods = len(returns)
        trend_component = np.zeros(n_periods)
        
        if trend_type == TrendType.CYCLICAL:
            # Sine wave pattern
            cycle_length = trend_params.get('cycle_period_days', 63)
            x = np.arange(n_periods)
            trend_component = trend_params['trend_strength'] * 0.01 * np.sin(2 * np.pi * x / cycle_length)
        
        elif trend_type == TrendType.MEAN_REVERTING:
            # Ornstein-Uhlenbeck process
            speed = trend_params.get('mean_reversion_speed', 0.1)
            level = 0.0
            
            for i in range(1, n_periods):
                trend_component[i] = trend_component[i-1] + speed * (level - trend_component[i-1]) + 0.01 * self.rng.normal()
        
        else:
            # Linear trend
            trend_component = np.full(n_periods, trend_params['daily_drift'])
            trend_component *= trend_params.get('trend_strength', 1.0)
        
        return trend_component
    
    def _generate_ohlc_from_prices(
        self,
        prices: np.ndarray,
        volatility_regime: VolatilityRegime
    ) -> Dict[str, np.ndarray]:
        """Generate OHLC data from price series"""
        n_prices = len(prices)
        
        # Base prices as close prices
        close_prices = prices
        
        # Determine intra-period range based on volatility
        vol_multiplier = {
            VolatilityRegime.LOW: 0.002,
            VolatilityRegime.MEDIUM: 0.005,
            VolatilityRegime.HIGH: 0.01,
            VolatilityRegime.CRISIS: 0.02
        }[volatility_regime]
        
        # Generate OHLC with realistic relationships
        open_prices = np.zeros(n_prices)
        high_prices = np.zeros(n_prices)
        low_prices = np.zeros(n_prices)
        
        for i in range(n_prices):
            if i == 0:
                open_prices[i] = close_prices[i] * (1 + self.rng.normal(0, vol_multiplier))
            else:
                open_prices[i] = close_prices[i-1]
            
            # Intra-day range
            intraday_vol = vol_multiplier * close_prices[i]
            high_prices[i] = max(open_prices[i], close_prices[i]) + abs(self.rng.normal(0, intraday_vol))
            low_prices[i] = min(open_prices[i], close_prices[i]) - abs(self.rng.normal(0, intraday_vol))
            
            # Ensure high >= low and high >= close >= low
            high_prices[i] = max(high_prices[i], close_prices[i], open_prices[i])
            low_prices[i] = min(low_prices[i], close_prices[i], open_prices[i])
        
        return {
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices
        }
    
    def _generate_volume(
        self,
        n_periods: int,
        price_series: np.ndarray,
        profile: str,
        volatility_regime: VolatilityRegime
    ) -> np.ndarray:
        """Generate realistic volume data"""
        
        # Base volume
        if profile == "normal":
            base_volume = 1_000_000  # 1 million shares
            volume_vol = 0.3
        elif profile == "high":
            base_volume = 10_000_000  # 10 million shares
            volume_vol = 0.2
        elif profile == "low":
            base_volume = 100_000  # 100k shares
            volume_vol = 0.5
        else:
            base_volume = 1_000_000
            volume_vol = 0.3
        
        # Generate log-normal volume with autocorrelation
        volumes = np.zeros(n_periods)
        volumes[0] = base_volume
        
        for i in range(1, n_periods):
            # Volume persistence
            volumes[i] = volumes[i-1] * np.exp(self.rng.normal(0, volume_vol))
            
            # Volume increase with volatility
            price_change = abs((price_series[i] - price_series[i-1]) / price_series[i-1])
            volumes[i] *= (1 + price_change * 10)
            
            # Add volume spikes
            if self.rng.random() < 0.01:  # 1% chance of volume spike
                volumes[i] *= self.rng.uniform(2, 5)
        
        # Add regime effect
        regime_multiplier = {
            VolatilityRegime.LOW: 0.7,
            VolatilityRegime.MEDIUM: 1.0,
            VolatilityRegime.HIGH: 1.5,
            VolatilityRegime.CRISIS: 2.0
        }[volatility_regime]
        
        volumes *= regime_multiplier
        
        return np.round(volumes).astype(int)
    
    def _introduce_data_gaps(
        self,
        df: pd.DataFrame,
        gap_probability: float
    ) -> pd.DataFrame:
        """Introduce missing data periods to simulate real-world data issues"""
        if gap_probability <= 0:
            return df
        
        # Create a copy to avoid modifying original
        df_with_gaps = df.copy()
        
        # Randomly set some periods to NaN
        mask = self.rng.random(len(df)) < gap_probability
        columns_to_affect = ['open', 'high', 'low', 'close', 'volume']
        
        for col in columns_to_affect:
            df_with_gaps.loc[mask, col] = np.nan
        
        return df_with_gaps
    
    def generate_multiple_assets(
        self,
        tickers: List[str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate synthetic data for multiple assets with correlations
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            **kwargs: Additional arguments passed to generate_ohlcv
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
        data = {}
        
        # Generate data for first ticker
        first_ticker = tickers[0]
        data[first_ticker] = self.generate_ohlcv(
            ticker=first_ticker,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        
        # Generate correlated data for remaining tickers
        for i, ticker in enumerate(tickers[1:], 1):
            base_df = data[tickers[0]]
            
            # Create correlated returns
            base_returns = np.log(base_df['close'] / base_df['close'].shift(1)).fillna(0).values
            
            # Add some correlation (decreasing with index)
            correlation = max(0.3, 0.8 - i * 0.1)
            correlated_returns = correlation * base_returns + np.sqrt(1 - correlation**2) * self.rng.normal(0, 0.02, len(base_returns))
            
            # Generate prices from correlated returns
            base_price = kwargs.get('base_price', self.config.synthetic_base_price)
            prices = base_price * np.exp(np.cumsum(correlated_returns))
            
            # Generate OHLCV
            ohlc_data = self._generate_ohlc_from_prices(
                prices,
                kwargs.get('volatility_regime', VolatilityRegime.MEDIUM)
            )
            
            # Generate volume
            volumes = self._generate_volume(
                n_periods=len(prices),
                price_series=prices,
                profile=kwargs.get('volume_profile', 'normal'),
                volatility_regime=kwargs.get('volatility_regime', VolatilityRegime.MEDIUM)
            )
            
            # Create DataFrame
            df = pd.DataFrame(
                data={
                    'open': ohlc_data['open'],
                    'high': ohlc_data['high'],
                    'low': ohlc_data['low'],
                    'close': ohlc_data['close'],
                    'volume': volumes
                },
                index=base_df.index
            )
            
            df['ticker'] = ticker
            data[ticker] = df[['ticker', 'open', 'high', 'low', 'close', 'volume']]
        
        return data

# ============================================================================
# PART 3: ENVIRONMENT MANAGEMENT
# ============================================================================

class TestEnvironmentManager:
    """Manager for isolated test environments"""
    
    def __init__(self, config: TestEnvironmentConfig):
        self.config = config
        self.docker_client = None
        self.temp_dir = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for test environment"""
        logger = logging.getLogger(f"test_env_{self.config.mode.value}")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = RotatingFileHandler(
            log_dir / f"test_env_{self.config.mode.value}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s - %(message)s')
        )
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def setup_virtual_environment(self, requirements_path: str) -> Tuple[bool, str]:
        """
        Setup Python virtual environment
        
        Args:
            requirements_path: Path to requirements.txt
            
        Returns:
            Tuple of (success, message)
        """
        self.logger.info("Setting up virtual environment...")
        
        try:
            # In a real implementation, this would:
            # 1. Create virtual environment
            # 2. Install dependencies from requirements.txt
            # 3. Verify installation
            
            # For this example, we'll simulate the process
            if not Path(requirements_path).exists():
                return False, f"Requirements file not found: {requirements_path}"
            
            self.logger.info(f"Virtual environment setup with {requirements_path}")
            return True, "Virtual environment setup completed"
            
        except Exception as e:
            self.logger.error(f"Failed to setup virtual environment: {e}")
            return False, str(e)
    
    def create_docker_test_environment(self, dockerfile_path: str) -> Optional[Container]:
        """
        Create Docker container for testing
        
        Args:
            dockerfile_path: Path to Dockerfile
            
        Returns:
            Docker container instance or None if failed
        """
        self.logger.info("Creating Docker test environment...")
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Build Docker image
            self.logger.info(f"Building Docker image from {dockerfile_path}")
            
            # Note: In a real implementation, you would build the image
            # For this example, we'll simulate the process
            image_tag = f"trading-test-env-{hashlib.md5(str(dockerfile_path).encode()).hexdigest()[:8]}"
            
            # Create temporary directory for test data
            self.temp_dir = tempfile.mkdtemp(prefix="trading_test_")
            self.logger.info(f"Created temp directory: {self.temp_dir}")
            
            # Simulate container creation
            self.logger.info(f"Docker environment ready with tag: {image_tag}")
            
            # Return mock container (in real implementation, return actual container)
            return None
            
        except docker.errors.DockerException as e:
            self.logger.error(f"Docker error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create Docker environment: {e}")
            return None
    
    def cleanup(self):
        """Cleanup test environment resources"""
        self.logger.info("Cleaning up test environment...")
        
        # Cleanup temp directory
        if self.temp_dir and Path(self.temp_dir).exists():
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Removed temp directory: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to remove temp directory: {e}")
        
        # Close Docker client
        if self.docker_client:
            self.docker_client.close()
    
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate test environment setup
        
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating test environment...")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'environment_mode': self.config.mode.value,
            'checks': {}
        }
        
        # Check Python version
        import sys
        validation_results['checks']['python_version'] = {
            'status': 'PASS',
            'message': f"Python {sys.version.split()[0]}"
        }
        
        # Check required packages
        required_packages = ['pandas', 'numpy', 'pytest', 'docker']
        for package in required_packages:
            try:
                __import__(package)
                validation_results['checks'][f'package_{package}'] = {
                    'status': 'PASS',
                    'message': f"{package} available"
                }
            except ImportError:
                validation_results['checks'][f'package_{package}'] = {
                    'status': 'FAIL',
                    'message': f"{package} not installed"
                }
        
        # Check write permissions
        try:
            test_file = Path(self.temp_dir or '.') / 'test_write.txt'
            test_file.write_text('test')
            test_file.unlink()
            validation_results['checks']['write_permissions'] = {
                'status': 'PASS',
                'message': 'Write permissions OK'
            }
        except Exception as e:
            validation_results['checks']['write_permissions'] = {
                'status': 'FAIL',
                'message': f'Write permissions failed: {e}'
            }
        
        # Overall status
        all_passed = all(check['status'] == 'PASS' for check in validation_results['checks'].values())
        validation_results['overall_status'] = 'PASS' if all_passed else 'FAIL'
        
        self.logger.info(f"Environment validation: {validation_results['overall_status']}")
        
        return validation_results

# ============================================================================
# PART 4: CONFIGURATION TEMPLATES
# ============================================================================

def generate_dockerfile_template() -> str:
    """Generate Dockerfile template for trading test environment"""
    return """# Trading System Test Environment
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 trader && chown -R trader:trader /app
USER trader

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/logs /app/results

# Default command
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
"""

def generate_requirements_template() -> str:
    """Generate requirements.txt template"""
    return """# Trading System Dependencies
# Core
pandas>=1.5.0
numpy>=1.24.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Data processing
scipy>=1.10.0
statsmodels>=0.14.0
ta-lib>=0.4.25

# API clients (for integration testing)
requests>=2.28.0
websockets>=11.0.0

# Configuration
pyyaml>=6.0
python-dotenv>=1.0.0

# Docker (for environment management)
docker>=6.0.0

# Optional: backtesting frameworks
backtrader>=1.9.78.123
vectorbt>=0.25.0

# Development
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
"""

def generate_ci_config_template() -> str:
    """Generate GitHub Actions CI configuration template"""
    return """name: Trading System CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_trading
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_trading
        DB_USER: postgres
        DB_PASSWORD: test_password
      run: |
        pytest tests/integration/ -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
    
    - name: Archive test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          test-results/
          coverage.xml
"""

# ============================================================================
# PART 5: DEMONSTRATION AND USAGE
# ============================================================================

def demonstrate_test_environment():
    """Demonstrate the test environment setup"""
    print("=" * 70)
    print("Day 72: Setting Up a Test Environment - Demonstration")
    print("=" * 70)
    
    # 1. Create configuration
    print("\n1. Creating Test Environment Configuration...")
    config = TestEnvironmentConfig(
        mode=EnvironmentMode.TEST,
        data_source="synthetic",
        synthetic_base_price=150.0,
        synthetic_volatility=0.015,
        log_level="INFO"
    )
    
    print(f"   Mode: {config.mode.value}")
    print(f"   Data Source: {config.data_source}")
    print(f"   Base Price: ${config.synthetic_base_price:.2f}")
    
    # 2. Generate synthetic data
    print("\n2. Generating Synthetic Market Data...")
    fixture = DataFixture(config=config, random_seed=42)
    
    # Generate single asset data
    single_data = fixture.generate_ohlcv(
        ticker="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        timeframe="1D",
        volatility_regime=VolatilityRegime.MEDIUM,
        trend_type=TrendType.UPWARD,
        include_gaps=True,
        gap_probability=0.02
    )
    
    print(f"   Generated {len(single_data)} days of OHLCV data for AAPL")
    print(f"   Data shape: {single_data.shape}")
    print(f"   First 5 rows:")
    print(single_data.head().to_string())
    
    # Generate multiple correlated assets
    print("\n3. Generating Multiple Correlated Assets...")
    multi_data = fixture.generate_multiple_assets(
        tickers=["AAPL", "MSFT", "GOOGL"],
        start_date="2024-01-01",
        end_date="2024-01-10",
        volatility_regime=VolatilityRegime.MEDIUM,
        trend_type=TrendType.UPWARD
    )
    
    print(f"   Generated data for {len(multi_data)} assets")
    for ticker, df in multi_data.items():
        print(f"   - {ticker}: {len(df)} periods, Close range: ${df['close'].min():.2f}-${df['close'].max():.2f}")
    
    # 4. Setup environment manager
    print("\n4. Setting Up Test Environment Manager...")
    env_manager = TestEnvironmentManager(config=config)
    
    # Validate environment
    validation = env_manager.validate_environment()
    print(f"   Environment validation: {validation['overall_status']}")
    print(f"   Checks performed: {len(validation['checks'])}")
    
    # Show some check results
    for check_name, check_result in list(validation['checks'].items())[:3]:
        print(f"   - {check_name}: {check_result['status']}")
    
    # 5. Generate configuration templates
    print("\n5. Generating Configuration Templates...")
    
    dockerfile = generate_dockerfile_template()
    requirements = generate_requirements_template()
    ci_config = generate_ci_config_template()
    
    print(f"   Dockerfile: {len(dockerfile.split('\\n'))} lines")
    print(f"   Requirements: {len(requirements.split('\\n'))} lines")
    print(f"   CI Config: {len(ci_config.split('\\n'))} lines")
    
    # 6. Demonstrate data with different regimes
    print("\n6. Demonstrating Different Volatility Regimes...")
    
    regimes = [
        (VolatilityRegime.LOW, "Low Volatility"),
        (VolatilityRegime.MEDIUM, "Medium Volatility"),
        (VolatilityRegime.HIGH, "High Volatility"),
        (VolatilityRegime.CRISIS, "Crisis Volatility")
    ]
    
    for regime, description in regimes:
        data = fixture.generate_ohlcv(
            ticker="TEST",
            start_date="2024-01-01",
            end_date="2024-01-31",
            volatility_regime=regime,
            trend_type=TrendType.SIDEWAYS
        )
        
        returns = np.log(data['close'] / data['close'].shift(1)).dropna()
        annualized_vol = returns.std() * np.sqrt(252) * 100
        
        print(f"   {description}:")
        print(f"     - Annualized Volatility: {annualized_vol:.1f}%")
        print(f"     - Max Drawdown: {((data['close'] / data['close'].cummax() - 1).min() * 100):.1f}%")
    
    # 7. Cleanup
    print("\n7. Cleaning Up Resources...")
    env_manager.cleanup()
    print("   Cleanup completed")
    
    print("\n" + "=" * 70)
    print("Demonstration Complete!")
    print("\nSummary:")
    print("- Created configurable test environment")
    print("- Generated synthetic data with various regimes")
    print("- Implemented DataFixture for reproducible testing")
    print("- Generated CI/CD and Docker templates")
    print("- Validated environment setup")
    print("\nNext Steps:")
    print("1. Save templates to files")
    print("2. Configure CI pipeline")
    print("3. Use synthetic data for unit tests")
    print("=" * 70)

# ============================================================================
# PART 6: UTILITY FUNCTIONS
# ============================================================================

def save_templates_to_files(base_dir: str = "."):
    """Save configuration templates to files"""
    base_path = Path(base_dir)
    
    # Create directories
    docker_dir = base_path / "docker"
    docker_dir.mkdir(exist_ok=True)
    
    config_dir = base_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    workflows_dir = base_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Save files
    dockerfile_path = docker_dir / "Dockerfile"
    dockerfile_path.write_text(generate_dockerfile_template())
    print(f"Saved Dockerfile to: {dockerfile_path}")
    
    requirements_path = base_path / "requirements.txt"
    requirements_path.write_text(generate_requirements_template())
    print(f"Saved requirements.txt to: {requirements_path}")
    
    ci_config_path = workflows_dir / "ci-pipeline.yml"
    ci_config_path.write_text(generate_ci_config_template())
    print(f"Saved CI config to: {ci_config_path}")
    
    # Save example config
    example_config = TestEnvironmentConfig()
    config_path = config_dir / "test_config.yaml"
    example_config.to_yaml(str(config_path))
    print(f"Saved example config to: {config_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run demonstration
    demonstrate_test_environment()
    
    # Ask if user wants to save templates
    response = input("\nWould you like to save configuration templates to files? (y/n): ")
    if response.lower() == 'y':
        save_templates_to_files()
        print("\nTemplates saved successfully!")
        print("\nTo use this test environment:")
        print("1. Review and modify the generated templates")
        print("2. Run: docker build -f docker/Dockerfile -t trading-test .")
        print("3. Use DataFixture in your tests for synthetic data")
    else:
        print("\nTemplates not saved. You can generate them later using save_templates_to_files()")
    
    print("\nDay 72 implementation complete!")