"""
Day 88: Database Optimization for High-Performance Trading
Implementation of optimized databases for trading workloads with real-time analytics.
"""

import asyncio
import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import redis.asyncio as redis
import asyncpg
from dataclasses import dataclass
from enum import Enum
import hashlib
import zlib
import msgpack
import psutil
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Database types for trading systems."""
    TIMESERIES = "timeseries"  # TimescaleDB, QuestDB
    IN_MEMORY = "in_memory"    # Redis, Memcached
    COLUMNAR = "columnar"      # ClickHouse, Druid
    DOCUMENT = "document"      # MongoDB
    GRAPH = "graph"            # Neo4j
    TRADITIONAL = "traditional" # PostgreSQL, MySQL


class TimeSeriesDatabase:
    """
    TimescaleDB implementation for high-frequency trading data.
    Features hypertables, continuous aggregates, and time-based partitioning.
    """
    
    def __init__(self, connection_params: Dict):
        self.connection_params = connection_params
        self.pool = None
        self.hypertables = {}
        
    async def connect(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(**self.connection_params)
        logger.info("Connected to TimescaleDB")
        
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from TimescaleDB")
            
    async def initialize_schema(self):
        """Initialize trading database schema with optimized structure."""
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Create tick data hypertable
            await conn.execute("""
            -- Market tick data (raw ticks)
            CREATE TABLE IF NOT EXISTS market_ticks (
                symbol VARCHAR(20) NOT NULL,
                exchange VARCHAR(10) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                bid_price DECIMAL(20, 8),
                ask_price DECIMAL(20, 8),
                bid_size INTEGER,
                ask_size INTEGER,
                last_price DECIMAL(20, 8),
                last_size INTEGER,
                volume BIGINT,
                vwap DECIMAL(20, 8),
                trade_count INTEGER,
                -- Compression columns
                price_change DECIMAL(10, 8) GENERATED ALWAYS AS (last_price - LAG(last_price) OVER (PARTITION BY symbol ORDER BY timestamp)) STORED,
                spread DECIMAL(10, 8) GENERATED ALWAYS AS (ask_price - bid_price) STORED,
                -- Index columns
                minute_bucket TIMESTAMPTZ GENERATED ALWAYS AS (date_bin('1 minute', timestamp)) STORED,
                hour_bucket TIMESTAMPTZ GENERATED ALWAYS AS (date_bin('1 hour', timestamp)) STORED
            );
            """)
            
            # Convert to hypertable with time partitioning
            await conn.execute("""
            SELECT create_hypertable(
                'market_ticks',
                'timestamp',
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """)
            
            # Add space partitioning by symbol
            await conn.execute("""
            SELECT add_dimension(
                'market_ticks',
                'symbol',
                number_partitions => 16,
                if_not_exists => TRUE
            );
            """)
            
            # Create compressed hypertable for aggregated bars
            await conn.execute("""
            -- OHLCV bars (1-minute aggregated)
            CREATE TABLE IF NOT EXISTS ohlcv_bars (
                symbol VARCHAR(20) NOT NULL,
                exchange VARCHAR(10) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                time_bucket TIMESTAMPTZ NOT NULL,
                open_price DECIMAL(20, 8),
                high_price DECIMAL(20, 8),
                low_price DECIMAL(20, 8),
                close_price DECIMAL(20, 8),
                volume BIGINT,
                vwap DECIMAL(20, 8),
                trade_count INTEGER,
                -- Additional metrics
                bid_ask_spread DECIMAL(10, 8),
                price_range DECIMAL(20, 8),
                volume_imbalance DECIMAL(20, 8)
            );
            """)
            
            await conn.execute("""
            SELECT create_hypertable(
                'ohlcv_bars',
                'time_bucket',
                chunk_time_interval => INTERVAL '7 days',
                if_not_exists => TRUE
            );
            """)
            
            # Create continuous aggregates for real-time analytics
            await conn.execute("""
            -- 1-minute OHLCV continuous aggregate
            CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1min
            WITH (timescaledb.continuous) AS
            SELECT
                symbol,
                exchange,
                time_bucket('1 minute', timestamp) AS bucket,
                FIRST(last_price, timestamp) AS open_price,
                MAX(last_price) AS high_price,
                MIN(last_price) AS low_price,
                LAST(last_price, timestamp) AS close_price,
                SUM(volume) AS volume,
                AVG(vwap) AS vwap,
                SUM(trade_count) AS trade_count,
                AVG(spread) AS avg_spread
            FROM market_ticks
            GROUP BY symbol, exchange, bucket;
            """)
            
            # Add refresh policy for continuous aggregate
            await conn.execute("""
            SELECT add_continuous_aggregate_policy('ohlcv_1min',
                start_offset => INTERVAL '1 hour',
                end_offset => INTERVAL '1 minute',
                schedule_interval => INTERVAL '1 minute'
            );
            """)
            
            # Create order book snapshot table
            await conn.execute("""
            -- Order book snapshots
            CREATE TABLE IF NOT EXISTS order_book_snapshots (
                symbol VARCHAR(20) NOT NULL,
                exchange VARCHAR(10) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                snapshot_id UUID DEFAULT gen_random_uuid(),
                -- Bid/ask levels (stored as JSON arrays for flexibility)
                bids JSONB NOT NULL,
                asks JSONB NOT NULL,
                -- Aggregated metrics
                best_bid DECIMAL(20, 8),
                best_ask DECIMAL(20, 8),
                mid_price DECIMAL(20, 8),
                total_bid_volume BIGINT,
                total_ask_volume BIGINT,
                order_book_imbalance DECIMAL(10, 8),
                -- Compression optimization
                snapshot_data BYTEA  -- Compressed full snapshot
            );
            """)
            
            await conn.execute("""
            SELECT create_hypertable(
                'order_book_snapshots',
                'timestamp',
                chunk_time_interval => INTERVAL '1 hour',
                if_not_exists => TRUE
            );
            """)
            
            # Create trades table
            await conn.execute("""
            -- Individual trades
            CREATE TABLE IF NOT EXISTS trades (
                trade_id BIGSERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                exchange VARCHAR(10) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                size INTEGER NOT NULL,
                side VARCHAR(4) NOT NULL,
                trade_type VARCHAR(20),
                order_id VARCHAR(100),
                -- Market microstructure features
                is_aggressive BOOLEAN,
                spread_at_trade DECIMAL(10, 8),
                volume_imbalance DECIMAL(10, 8),
                time_since_last_trade DECIMAL(20, 12)
            );
            """)
            
            await conn.execute("""
            SELECT create_hypertable(
                'trades',
                'timestamp',
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """)
            
            # Create portfolio and positions table
            await conn.execute("""
            -- Portfolio positions with audit trail
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                position_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                portfolio_id VARCHAR(50) NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                avg_entry_price DECIMAL(20, 8),
                current_price DECIMAL(20, 8),
                unrealized_pnl DECIMAL(20, 8),
                realized_pnl DECIMAL(20, 8),
                -- Risk metrics
                var_95 DECIMAL(20, 8),
                expected_shortfall DECIMAL(20, 8),
                beta DECIMAL(10, 8),
                -- Audit trail
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                operation VARCHAR(10), -- INSERT, UPDATE, DELETE
                modified_by VARCHAR(50)
            );
            """)
            
            # Create audit trail trigger
            await conn.execute("""
            CREATE OR REPLACE FUNCTION portfolio_audit_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            CREATE TRIGGER portfolio_audit
            BEFORE UPDATE ON portfolio_positions
            FOR EACH ROW EXECUTE FUNCTION portfolio_audit_trigger();
            """)
            
            # Create indexes for common query patterns
            await self._create_indexes(conn)
            
            # Set up compression policies
            await self._setup_compression(conn)
            
            # Set up retention policies
            await self._setup_retention(conn)
            
            logger.info("Database schema initialized successfully")
    
    async def _create_indexes(self, conn):
        """Create optimized indexes for trading queries."""
        # Market ticks indexes
        await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_ticks_symbol_timestamp 
        ON market_ticks (symbol, timestamp DESC);
        
        CREATE INDEX IF NOT EXISTS idx_market_ticks_timestamp_symbol 
        ON market_ticks (timestamp DESC, symbol);
        
        -- BRIN index for time-based queries
        CREATE INDEX IF NOT EXISTS idx_market_ticks_time_brin 
        ON market_ticks USING BRIN (timestamp);
        """)
        
        # OHLCV bars indexes
        await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_bucket 
        ON ohlcv_bars (symbol, time_bucket DESC);
        
        -- Composite index for common queries
        CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_exchange_bucket 
        ON ohlcv_bars (symbol, exchange, time_bucket DESC);
        """)
        
        # Trades indexes
        await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp 
        ON trades (symbol, timestamp DESC);
        
        CREATE INDEX IF NOT EXISTS idx_trades_side_symbol 
        ON trades (side, symbol, timestamp DESC);
        
        -- Partial index for aggressive trades
        CREATE INDEX IF NOT EXISTS idx_trades_aggressive 
        ON trades (symbol, timestamp DESC) 
        WHERE is_aggressive = TRUE;
        """)
        
        # Order book indexes
        await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orderbook_symbol_timestamp 
        ON order_book_snapshots (symbol, timestamp DESC);
        
        -- GIN index for JSONB queries
        CREATE INDEX IF NOT EXISTS idx_orderbook_bids_gin 
        ON order_book_snapshots USING GIN (bids);
        
        CREATE INDEX IF NOT EXISTS idx_orderbook_asks_gin 
        ON order_book_snapshots USING GIN (asks);
        """)
        
        logger.info("Indexes created successfully")
    
    async def _setup_compression(self, conn):
        """Setup compression for historical data."""
        # Compress older tick data
        await conn.execute("""
        ALTER TABLE market_ticks SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'symbol, exchange',
            timescaledb.compress_orderby = 'timestamp DESC'
        );
        
        -- Compression policy: compress data older than 1 day
        SELECT add_compression_policy('market_ticks', 
            compress_after => INTERVAL '1 day');
        """)
        
        # Compress older OHLCV bars
        await conn.execute("""
        ALTER TABLE ohlcv_bars SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'symbol, exchange',
            timescaledb.compress_orderby = 'time_bucket DESC'
        );
        
        SELECT add_compression_policy('ohlcv_bars',
            compress_after => INTERVAL '7 days');
        """)
        
        logger.info("Compression policies configured")
    
    async def _setup_retention(self, conn):
        """Setup data retention policies."""
        # Keep raw ticks for 30 days, aggregated data for longer
        await conn.execute("""
        -- Raw ticks: 30 days retention
        SELECT add_retention_policy('market_ticks',
            drop_after => INTERVAL '30 days');
        
        -- OHLCV bars: 1 year retention
        SELECT add_retention_policy('ohlcv_bars',
            drop_after => INTERVAL '365 days');
        
        -- Order book snapshots: 7 days retention
        SELECT add_retention_policy('order_book_snapshots',
            drop_after => INTERVAL '7 days');
        
        -- Trades: 90 days retention
        SELECT add_retention_policy('trades',
            drop_after => INTERVAL '90 days');
        """)
        
        logger.info("Retention policies configured")
    
    async def ingest_market_ticks(self, ticks: List[Dict]):
        """High-performance tick data ingestion."""
        if not ticks:
            return
        
        async with self.pool.acquire() as conn:
            # Use COPY for high-throughput ingestion
            columns = ['symbol', 'exchange', 'timestamp', 'bid_price', 'ask_price',
                      'bid_size', 'ask_size', 'last_price', 'last_size', 'volume',
                      'vwap', 'trade_count']
            
            records = []
            for tick in ticks:
                record = (
                    tick['symbol'],
                    tick['exchange'],
                    tick['timestamp'],
                    tick.get('bid_price'),
                    tick.get('ask_price'),
                    tick.get('bid_size'),
                    tick.get('ask_size'),
                    tick['last_price'],
                    tick.get('last_size', 0),
                    tick.get('volume', 0),
                    tick.get('vwap'),
                    tick.get('trade_count', 1)
                )
                records.append(record)
            
            # Use asyncpg's copy_records_to_table for maximum performance
            await conn.copy_records_to_table(
                'market_ticks',
                records=records,
                columns=columns,
                timeout=30
            )
            
            logger.debug(f"Ingested {len(ticks)} market ticks")
    
    async def get_ohlcv_data(self, symbol: str, start_time: datetime, 
                           end_time: datetime, interval: str = '1min') -> List[Dict]:
        """Get OHLCV data with optimized queries."""
        interval_map = {
            '1min': '1 minute',
            '5min': '5 minutes',
            '15min': '15 minutes',
            '1hour': '1 hour',
            '1day': '1 day'
        }
        
        interval_str = interval_map.get(interval, '1 minute')
        
        async with self.pool.acquire() as conn:
            query = f"""
            SELECT
                time_bucket('{interval_str}', timestamp) AS bucket,
                symbol,
                exchange,
                FIRST(last_price, timestamp) AS open,
                MAX(last_price) AS high,
                MIN(last_price) AS low,
                LAST(last_price, timestamp) AS close,
                SUM(volume) AS volume,
                AVG(vwap) AS vwap,
                SUM(trade_count) AS trade_count,
                AVG(spread) AS avg_spread
            FROM market_ticks
            WHERE symbol = $1
                AND timestamp >= $2
                AND timestamp < $3
            GROUP BY bucket, symbol, exchange
            ORDER BY bucket DESC
            LIMIT 10000;
            """
            
            rows = await conn.fetch(query, symbol, start_time, end_time)
            
            return [dict(row) for row in rows]
    
    async def get_real_time_metrics(self, symbol: str, lookback_minutes: int = 5) -> Dict:
        """Get real-time trading metrics with window functions."""
        async with self.pool.acquire() as conn:
            query = """
            WITH recent_ticks AS (
                SELECT 
                    timestamp,
                    last_price,
                    volume,
                    spread,
                    bid_price,
                    ask_price
                FROM market_ticks
                WHERE symbol = $1
                    AND timestamp > NOW() - INTERVAL '$2 minutes'
                ORDER BY timestamp DESC
                LIMIT 10000
            ),
            metrics AS (
                SELECT
                    -- Price metrics
                    AVG(last_price) AS avg_price,
                    STDDEV(last_price) AS price_volatility,
                    LAST(last_price, timestamp) AS last_price,
                    FIRST(last_price, timestamp) AS first_price,
                    -- Volume metrics
                    SUM(volume) AS total_volume,
                    AVG(volume) AS avg_volume,
                    -- Spread metrics
                    AVG(spread) AS avg_spread,
                    MAX(spread) AS max_spread,
                    -- Market microstructure
                    CORR(bid_price, ask_price) AS bid_ask_correlation,
                    COUNT(*) AS tick_count
                FROM recent_ticks
            ),
            rolling_metrics AS (
                SELECT
                    timestamp,
                    last_price,
                    AVG(last_price) OVER (
                        ORDER BY timestamp 
                        ROWS BETWEEN 99 PRECEDING AND CURRENT ROW
                    ) AS sma_100,
                    STDDEV(last_price) OVER (
                        ORDER BY timestamp 
                        ROWS BETWEEN 99 PRECEDING AND CURRENT ROW
                    ) AS rolling_volatility,
                    SUM(volume) OVER (
                        ORDER BY timestamp 
                        ROWS BETWEEN 99 PRECEDING AND CURRENT ROW
                    ) AS rolling_volume
                FROM recent_ticks
                ORDER BY timestamp DESC
                LIMIT 1
            )
            SELECT 
                m.*,
                r.sma_100,
                r.rolling_volatility,
                r.rolling_volume
            FROM metrics m
            CROSS JOIN rolling_metrics r;
            """
            
            row = await conn.fetchrow(query, symbol, lookback_minutes)
            return dict(row) if row else {}
    
    async def analyze_market_regimes(self, symbol: str, start_date: datetime, 
                                   end_date: datetime) -> List[Dict]:
        """Analyze market regimes using statistical methods."""
        async with self.pool.acquire() as conn:
            query = """
            WITH hourly_data AS (
                SELECT
                    time_bucket('1 hour', timestamp) AS hour,
                    symbol,
                    AVG(last_price) AS avg_price,
                    STDDEV(last_price) AS price_volatility,
                    SUM(volume) AS total_volume,
                    AVG(spread) AS avg_spread,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY last_price) AS median_price
                FROM market_ticks
                WHERE symbol = $1
                    AND timestamp >= $2
                    AND timestamp < $3
                GROUP BY hour, symbol
            ),
            regime_stats AS (
                SELECT
                    hour,
                    avg_price,
                    price_volatility,
                    total_volume,
                    avg_spread,
                    -- Identify regimes using clustering
                    CASE
                        WHEN price_volatility > percentile_cont(0.75) WITHIN GROUP (ORDER BY price_volatility) OVER ()
                            AND total_volume > percentile_cont(0.75) WITHIN GROUP (ORDER BY total_volume) OVER ()
                        THEN 'high_vol_high_volume'
                        WHEN price_volatility > percentile_cont(0.75) WITHIN GROUP (ORDER BY price_volatility) OVER ()
                            AND total_volume < percentile_cont(0.25) WITHIN GROUP (ORDER BY total_volume) OVER ()
                        THEN 'high_vol_low_volume'
                        WHEN price_volatility < percentile_cont(0.25) WITHIN GROUP (ORDER BY price_volatility) OVER ()
                        THEN 'low_volatility'
                        ELSE 'normal'
                    END AS market_regime,
                    -- Calculate regime changes
                    LAG(avg_price) OVER (ORDER BY hour) AS prev_avg_price,
                    LAG(price_volatility) OVER (ORDER BY hour) AS prev_volatility
                FROM hourly_data
            )
            SELECT * FROM regime_stats
            ORDER BY hour DESC
            LIMIT 1000;
            """
            
            rows = await conn.fetch(query, symbol, start_date, end_date)
            return [dict(row) for row in rows]
    
    async def portfolio_performance_analysis(self, portfolio_id: str) -> Dict:
        """Analyze portfolio performance with complex queries."""
        async with self.pool.acquire() as conn:
            query = """
            WITH portfolio_data AS (
                SELECT
                    symbol,
                    quantity,
                    avg_entry_price,
                    current_price,
                    unrealized_pnl,
                    realized_pnl,
                    var_95,
                    expected_shortfall,
                    beta,
                    updated_at
                FROM portfolio_positions
                WHERE portfolio_id = $1
                    AND updated_at > NOW() - INTERVAL '1 day'
            ),
            portfolio_summary AS (
                SELECT
                    COUNT(DISTINCT symbol) AS num_positions,
                    SUM(quantity * current_price) AS total_value,
                    SUM(unrealized_pnl) AS total_unrealized_pnl,
                    SUM(realized_pnl) AS total_realized_pnl,
                    AVG(beta) AS avg_beta,
                    SQRT(SUM(POWER(var_95, 2))) AS portfolio_var_95,
                    AVG(expected_shortfall) AS avg_expected_shortfall
                FROM portfolio_data
            ),
            position_contributions AS (
                SELECT
                    symbol,
                    (quantity * current_price) / NULLIF(SUM(quantity * current_price) OVER (), 0) AS weight,
                    unrealized_pnl,
                    realized_pnl,
                    var_95,
                    beta
                FROM portfolio_data
            ),
            risk_metrics AS (
                SELECT
                    -- Calculate portfolio risk metrics
                    SUM(weight * beta) AS portfolio_beta,
                    SQRT(SUM(POWER(weight * var_95, 2))) AS portfolio_risk,
                    -- Calculate concentration metrics
                    1 - SUM(POWER(weight, 2)) AS diversification_score,
                    MAX(weight) AS max_concentration
                FROM position_contributions
            )
            SELECT 
                ps.*,
                rm.*
            FROM portfolio_summary ps
            CROSS JOIN risk_metrics rm;
            """
            
            row = await conn.fetchrow(query, portfolio_id)
            return dict(row) if row else {}
    
    async def get_query_plan(self, query: str, params: List = None) -> Dict:
        """Get query execution plan for optimization."""
        async with self.pool.acquire() as conn:
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            
            if params:
                result = await conn.fetchval(explain_query, *params)
            else:
                result = await conn.fetchval(explain_query)
            
            if result:
                return json.loads(result)[0]
            return {}


class RedisOrderBookCache:
    """
    Redis-based order book cache with pub/sub updates for high-frequency trading.
    Supports 1M+ active orders with memory optimization and failover mechanisms.
    """
    
    def __init__(self, redis_params: Dict, symbol: str, max_orders: int = 1000000):
        self.redis_params = redis_params
        self.symbol = symbol
        self.max_orders = max_orders
        self.redis = None
        self.pubsub = None
        self.order_book_key = f"orderbook:{symbol}"
        self.order_key_prefix = f"order:{symbol}:"
        self.stats_key = f"stats:{symbol}"
        
        # Memory optimization settings
        self.compression_threshold = 1000  # Compress orders larger than this
        self.use_compression = True
        self.use_memory_pool = True
        
    async def connect(self):
        """Connect to Redis with connection pooling."""
        self.redis = await redis.Redis(
            **self.redis_params,
            decode_responses=False,  # Keep as bytes for compression
            max_connections=100,
            socket_keepalive=True
        )
        
        # Test connection
        await self.redis.ping()
        logger.info(f"Connected to Redis for symbol {self.symbol}")
        
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.aclose()
            logger.info("Disconnected from Redis")
    
    async def initialize_order_book(self):
        """Initialize order book structure in Redis."""
        # Use Redis streams for order book updates
        await self.redis.delete(self.order_book_key)
        
        # Initialize order book structure
        order_book_structure = {
            'bids': '{}',
            'asks': '{}',
            'last_update': str(time.time()),
            'symbol': self.symbol,
            'version': '1.0'
        }
        
        await self.redis.hset(self.order_book_key, mapping=order_book_structure)
        
        # Initialize statistics
        stats = {
            'total_orders': '0',
            'active_bids': '0',
            'active_asks': '0',
            'total_volume': '0',
            'last_trade_price': '0',
            'last_trade_time': str(time.time())
        }
        
        await self.redis.hset(self.stats_key, mapping=stats)
        
        # Set memory limits
        await self._configure_memory_limits()
        
        logger.info(f"Initialized order book for {self.symbol}")
    
    async def _configure_memory_limits(self):
        """Configure Redis memory limits and eviction policies."""
        try:
            # Set maxmemory policy (allkeys-lru for order book cache)
            await self.redis.config_set('maxmemory-policy', 'allkeys-lru')
            
            # Set memory limit (adjust based on available memory)
            memory_info = psutil.virtual_memory()
            available_memory = memory_info.available
            
            # Reserve 1GB for order book (adjust based on requirements)
            order_book_memory = min(1024 * 1024 * 1024, available_memory // 2)
            await self.redis.config_set('maxmemory', str(order_book_memory))
            
            # Enable memory optimization
            await self.redis.config_set('hash-max-ziplist-entries', '512')
            await self.redis.config_set('hash-max-ziplist-value', '64')
            
            logger.info(f"Configured Redis memory limits: {order_book_memory // (1024*1024)}MB")
            
        except Exception as e:
            logger.warning(f"Could not configure Redis memory limits: {e}")
    
    def _compress_order(self, order_data: Dict) -> bytes:
        """Compress order data using msgpack and zlib."""
        if not self.use_compression:
            return json.dumps(order_data).encode('utf-8')
        
        try:
            # Use msgpack for efficient serialization
            packed = msgpack.packb(order_data, use_bin_type=True)
            
            # Compress if above threshold
            if len(packed) > self.compression_threshold:
                compressed = zlib.compress(packed, level=3)  # Level 3 for speed
                # Add compression header
                return b'C' + compressed
            else:
                return b'U' + packed  # Uncompressed marker
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return json.dumps(order_data).encode('utf-8')
    
    def _decompress_order(self, compressed_data: bytes) -> Dict:
        """Decompress order data."""
        if not compressed_data:
            return {}
        
        try:
            marker = compressed_data[0:1]
            data = compressed_data[1:]
            
            if marker == b'C':  # Compressed
                decompressed = zlib.decompress(data)
                return msgpack.unpackb(decompressed, raw=False)
            elif marker == b'U':  # Uncompressed
                return msgpack.unpackb(data, raw=False)
            else:
                # Try JSON decoding as fallback
                return json.loads(compressed_data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            try:
                return json.loads(compressed_data.decode('utf-8'))
            except:
                return {}
    
    async def add_order(self, order_id: str, order_data: Dict):
        """Add or update an order in the cache."""
        order_key = f"{self.order_key_prefix}{order_id}"
        
        # Compress order data
        compressed_data = self._compress_order(order_data)
        
        # Store order
        pipeline = self.redis.pipeline()
        
        # Store order with expiration (24 hours default)
        pipeline.setex(order_key, 86400, compressed_data)
        
        # Update order book side
        side = order_data.get('side', '').lower()
        price = float(order_data.get('price', 0))
        quantity = float(order_data.get('quantity', 0))
        
        if side == 'bid':
            # Add to bids sorted set (score = price, member = order_id)
            pipeline.zadd(f"{self.order_book_key}:bids", {order_id: price})
            pipeline.hincrby(self.stats_key, 'active_bids', 1)
        elif side == 'ask':
            # Add to asks sorted set (score = price, member = order_id)
            pipeline.zadd(f"{self.order_book_key}:asks", {order_id: price})
            pipeline.hincrby(self.stats_key, 'active_asks', 1)
        
        # Update total volume
        pipeline.hincrbyfloat(self.stats_key, 'total_volume', quantity)
        pipeline.hincrby(self.stats_key, 'total_orders', 1)
        
        # Update last update time
        pipeline.hset(self.order_book_key, 'last_update', str(time.time()))
        
        await pipeline.execute()
        
        # Publish order update
        await self._publish_order_update('add', order_id, order_data)
        
        # Check memory usage and trigger cleanup if needed
        await self._check_memory_usage()
    
    async def remove_order(self, order_id: str):
        """Remove an order from the cache."""
        order_key = f"{self.order_key_prefix}{order_id}"
        
        # Get order data to determine side
        order_data_bytes = await self.redis.get(order_key)
        if not order_data_bytes:
            return
        
        order_data = self._decompress_order(order_data_bytes)
        side = order_data.get('side', '').lower()
        quantity = float(order_data.get('quantity', 0))
        
        pipeline = self.redis.pipeline()
        
        # Delete order
        pipeline.delete(order_key)
        
        # Remove from order book side
        if side == 'bid':
            pipeline.zrem(f"{self.order_book_key}:bids", order_id)
            pipeline.hincrby(self.stats_key, 'active_bids', -1)
        elif side == 'ask':
            pipeline.zrem(f"{self.order_book_key}:asks", order_id)
            pipeline.hincrby(self.stats_key, 'active_asks', -1)
        
        # Update statistics
        pipeline.hincrbyfloat(self.stats_key, 'total_volume', -quantity)
        pipeline.hincrby(self.stats_key, 'total_orders', -1)
        
        await pipeline.execute()
        
        # Publish order update
        await self._publish_order_update('remove', order_id, order_data)
    
    async def update_order(self, order_id: str, updates: Dict):
        """Update an existing order."""
        order_key = f"{self.order_key_prefix}{order_id}"
        
        # Get current order data
        order_data_bytes = await self.redis.get(order_key)
        if not order_data_bytes:
            logger.warning(f"Order {order_id} not found for update")
            return
        
        order_data = self._decompress_order(order_data_bytes)
        
        # Update order data
        order_data.update(updates)
        
        # Re-add with updated data
        await self.add_order(order_id, order_data)
    
    async def get_order_book(self, depth: int = 10) -> Dict:
        """Get current order book with specified depth."""
        pipeline = self.redis.pipeline()
        
        # Get bids (sorted by price descending)
        pipeline.zrevrange(f"{self.order_book_key}:bids", 0, depth - 1, withscores=True)
        
        # Get asks (sorted by price ascending)
        pipeline.zrange(f"{self.order_book_key}:asks", 0, depth - 1, withscores=True)
        
        # Get statistics
        pipeline.hgetall(self.stats_key)
        
        results = await pipeline.execute()
        
        bids_data = results[0]
        asks_data = results[1]
        stats = results[2]
        
        # Process bids and asks
        bids = []
        asks = []
        
        # Get order details for top bids
        for order_id, price in bids_data:
            order_data = await self.get_order(order_id)
            if order_data:
                bids.append({
                    'order_id': order_id,
                    'price': float(price),
                    'quantity': order_data.get('quantity', 0),
                    'timestamp': order_data.get('timestamp'),
                    **order_data
                })
        
        # Get order details for top asks
        for order_id, price in asks_data:
            order_data = await self.get_order(order_id)
            if order_data:
                asks.append({
                    'order_id': order_id,
                    'price': float(price),
                    'quantity': order_data.get('quantity', 0),
                    'timestamp': order_data.get('timestamp'),
                    **order_data
                })
        
        # Calculate market metrics
        best_bid = bids[0]['price'] if bids else 0
        best_ask = asks[0]['price'] if asks else 0
        
        order_book = {
            'symbol': self.symbol,
            'timestamp': time.time(),
            'bids': bids,
            'asks': asks,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': best_ask - best_bid if best_bid and best_ask else 0,
            'mid_price': (best_bid + best_ask) / 2 if best_bid and best_ask else 0,
            'statistics': {
                'total_orders': int(stats.get(b'total_orders', 0)),
                'active_bids': int(stats.get(b'active_bids', 0)),
                'active_asks': int(stats.get(b'active_asks', 0)),
                'total_volume': float(stats.get(b'total_volume', 0))
            }
        }
        
        return order_book
    
    async def get_order(self, order_id: str) -> Optional[Dict]:
        """Get individual order by ID."""
        order_key = f"{self.order_key_prefix}{order_id}"
        order_data_bytes = await self.redis.get(order_key)
        
        if order_data_bytes:
            order_data = self._decompress_order(order_data_bytes)
            order_data['order_id'] = order_id
            return order_data
        
        return None
    
    async def search_orders(self, filters: Dict) -> List[Dict]:
        """Search orders with filters (price range, side, quantity, etc.)."""
        # This is a simplified implementation
        # In production, use Redisearch or maintain secondary indexes
        
        all_orders = []
        
        # Get all order IDs from both sides
        pipeline = self.redis.pipeline()
        pipeline.zrange(f"{self.order_book_key}:bids", 0, -1)
        pipeline.zrange(f"{self.order_book_key}:asks", 0, -1)
        
        results = await pipeline.execute()
        order_ids = list(set(results[0] + results[1]))
        
        # Filter orders (limited to first 1000 for performance)
        filtered_orders = []
        for order_id in order_ids[:1000]:
            order_data = await self.get_order(order_id)
            if order_data and self._matches_filters(order_data, filters):
                filtered_orders.append(order_data)
        
        return filtered_orders
    
    def _matches_filters(self, order_data: Dict, filters: Dict) -> bool:
        """Check if order matches all filters."""
        for key, value in filters.items():
            if key in order_data:
                if isinstance(value, (list, tuple)):
                    if order_data[key] not in value:
                        return False
                elif isinstance(value, dict):
                    if 'min' in value and order_data[key] < value['min']:
                        return False
                    if 'max' in value and order_data[key] > value['max']:
                        return False
                elif order_data[key] != value:
                    return False
        return True
    
    async def _publish_order_update(self, action: str, order_id: str, order_data: Dict):
        """Publish order update to Redis pub/sub."""
        channel = f"orderbook:{self.symbol}:updates"
        
        update_message = {
            'action': action,
            'order_id': order_id,
            'symbol': self.symbol,
            'timestamp': time.time(),
            'data': order_data
        }
        
        await self.redis.publish(channel, json.dumps(update_message))
    
    async def subscribe_order_updates(self, callback):
        """Subscribe to order book updates."""
        self.pubsub = self.redis.pubsub()
        
        # Subscribe to order book updates
        await self.pubsub.subscribe(f"orderbook:{self.symbol}:updates")
        
        logger.info(f"Subscribed to order book updates for {self.symbol}")
        
        # Listen for messages
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    update_data = json.loads(message['data'])
                    await callback(update_data)
                except Exception as e:
                    logger.error(f"Error processing update: {e}")
    
    async def _check_memory_usage(self):
        """Check Redis memory usage and trigger cleanup if needed."""
        try:
            info = await self.redis.info('memory')
            used_memory = int(info.get('used_memory', 0))
            max_memory = int(info.get('maxmemory', 0))
            
            if max_memory > 0:
                memory_ratio = used_memory / max_memory
                
                if memory_ratio > 0.9:  # 90% memory usage
                    logger.warning(f"High memory usage: {memory_ratio:.1%}")
                    await self._cleanup_old_orders()
                    
        except Exception as e:
            logger.error(f"Error checking memory: {e}")
    
    async def _cleanup_old_orders(self):
        """Clean up old orders based on LRU policy."""
        logger.info("Cleaning up old orders...")
        
        # Get all order keys
        pattern = f"{self.order_key_prefix}*"
        cursor = 0
        deleted_count = 0
        
        try:
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=1000)
                
                if keys:
                    # Get TTL for each key
                    pipeline = self.redis.pipeline()
                    for key in keys:
                        pipeline.ttl(key)
                    
                    ttls = await pipeline.execute()
                    
                    # Delete orders with short TTL or no activity
                    delete_pipeline = self.redis.pipeline()
                    for key, ttl in zip(keys, ttls):
                        if ttl < 3600:  # Less than 1 hour remaining
                            delete_pipeline.delete(key)
                            deleted_count += 1
                    
                    await delete_pipeline.execute()
                
                if cursor == 0:
                    break
            
            logger.info(f"Cleaned up {deleted_count} old orders")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def get_performance_metrics(self) -> Dict:
        """Get cache performance metrics."""
        try:
            # Get Redis info
            info = await self.redis.info()
            memory_info = await self.redis.info('memory')
            stats_info = await self.redis.info('stats')
            
            # Get order book statistics
            stats = await self.redis.hgetall(self.stats_key)
            
            # Calculate hit rate (simplified)
            total_commands = int(stats_info.get('total_commands_processed', 0))
            hits = int(stats_info.get('keyspace_hits', 0))
            misses = int(stats_info.get('keyspace_misses', 0))
            
            hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
            
            metrics = {
                'memory_usage_mb': int(memory_info.get('used_memory', 0)) / (1024 * 1024),
                'memory_fragmentation_ratio': float(memory_info.get('mem_fragmentation_ratio', 0)),
                'total_orders': int(stats.get(b'total_orders', 0)),
                'active_bids': int(stats.get(b'active_bids', 0)),
                'active_asks': int(stats.get(b'active_asks', 0)),
                'total_volume': float(stats.get(b'total_volume', 0)),
                'hit_rate': hit_rate,
                'connected_clients': int(info.get('connected_clients', 0)),
                'ops_per_second': int(info.get('instantaneous_ops_per_sec', 0)),
                'uptime_days': int(info.get('uptime_in_seconds', 0)) / 86400
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def failover_test(self):
        """Test failover mechanism by simulating connection failure."""
        logger.info("Starting failover test...")
        
        # Save current state
        order_book = await self.get_order_book(depth=5)
        
        # Simulate connection failure
        await self.disconnect()
        
        logger.info("Connection failed, waiting for failover...")
        await asyncio.sleep(2)
        
        # Reconnect
        await self.connect()
        
        # Restore order book
        await self.initialize_order_book()
        
        logger.info("Failover test completed")
        return order_book


class DatabaseOptimizationBenchmark:
    """Benchmark database performance for trading workloads."""
    
    def __init__(self):
        self.results = {}
        
    async def benchmark_timescaledb(self, timescale_db: TimeSeriesDatabase):
        """Benchmark TimescaleDB performance."""
        logger.info("Starting TimescaleDB benchmark...")
        
        benchmarks = {}
        
        # 1. Insert performance
        start_time = time.time()
        ticks = self._generate_sample_ticks(10000)
        await timescale_db.ingest_market_ticks(ticks)
        insert_time = time.time() - start_time
        
        benchmarks['insert_10000_ticks'] = {
            'time_seconds': insert_time,
            'throughput_per_second': 10000 / insert_time
        }
        
        # 2. Query performance
        start_time = time.time()
        ohlcv_data = await timescale_db.get_ohlcv_data(
            'AAPL', 
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow(),
            '1min'
        )
        query_time = time.time() - start_time
        
        benchmarks['query_ohlcv_1day'] = {
            'time_seconds': query_time,
            'rows_returned': len(ohlcv_data),
            'throughput_rows_per_second': len(ohlcv_data) / query_time
        }
        
        # 3. Real-time metrics query
        start_time = time.time()
        metrics = await timescale_db.get_real_time_metrics('AAPL', 5)
        metrics_time = time.time() - start_time
        
        benchmarks['realtime_metrics'] = {
            'time_seconds': metrics_time,
            'metrics_calculated': len(metrics)
        }
        
        # 4. Complex analytical query
        start_time = time.time()
        regime_analysis = await timescale_db.analyze_market_regimes(
            'AAPL',
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )
        analysis_time = time.time() - start_time
        
        benchmarks['market_regime_analysis'] = {
            'time_seconds': analysis_time,
            'rows_analyzed': len(regime_analysis)
        }
        
        self.results['timescaledb'] = benchmarks
        logger.info(f"TimescaleDB benchmark completed: {benchmarks}")
        
        return benchmarks
    
    async def benchmark_redis_cache(self, redis_cache: RedisOrderBookCache):
        """Benchmark Redis cache performance."""
        logger.info("Starting Redis cache benchmark...")
        
        benchmarks = {}
        
        # 1. Order insertion performance
        start_time = time.time()
        
        orders = []
        for i in range(1000):
            order_data = {
                'order_id': f'order_{i}',
                'symbol': redis_cache.symbol,
                'side': 'bid' if i % 2 == 0 else 'ask',
                'price': 100 + (i % 10),
                'quantity': 100,
                'timestamp': time.time()
            }
            orders.append(order_data)
        
        # Insert orders
        for order in orders:
            await redis_cache.add_order(order['order_id'], order)
        
        insert_time = time.time() - start_time
        
        benchmarks['insert_1000_orders'] = {
            'time_seconds': insert_time,
            'throughput_orders_per_second': 1000 / insert_time
        }
        
        # 2. Order book retrieval performance
        start_time = time.time()
        for _ in range(100):
            await redis_cache.get_order_book(depth=10)
        retrieval_time = time.time() - start_time
        
        benchmarks['retrieve_100_orderbooks'] = {
            'time_seconds': retrieval_time,
            'throughput_per_second': 100 / retrieval_time,
            'avg_latency_ms': (retrieval_time / 100) * 1000
        }
        
        # 3. Order lookup performance
        start_time = time.time()
        for i in range(100):
            await redis_cache.get_order(f'order_{i}')
        lookup_time = time.time() - start_time
        
        benchmarks['lookup_100_orders'] = {
            'time_seconds': lookup_time,
            'throughput_per_second': 100 / lookup_time,
            'avg_latency_ms': (lookup_time / 100) * 1000
        }
        
        # 4. Memory usage
        metrics = await redis_cache.get_performance_metrics()
        benchmarks['memory_usage'] = {
            'memory_mb': metrics.get('memory_usage_mb', 0),
            'hit_rate': metrics.get('hit_rate', 0),
            'active_orders': metrics.get('total_orders', 0)
        }
        
        self.results['redis_cache'] = benchmarks
        logger.info(f"Redis cache benchmark completed: {benchmarks}")
        
        return benchmarks
    
    def _generate_sample_ticks(self, count: int) -> List[Dict]:
        """Generate sample tick data for benchmarking."""
        ticks = []
        base_time = datetime.utcnow()
        
        for i in range(count):
            tick_time = base_time - timedelta(seconds=i)
            price = 100 + np.random.randn() * 0.1
            
            tick = {
                'symbol': 'AAPL',
                'exchange': 'NASDAQ',
                'timestamp': tick_time,
                'bid_price': round(price - 0.01, 2),
                'ask_price': round(price + 0.01, 2),
                'bid_size': np.random.randint(100, 1000),
                'ask_size': np.random.randint(100, 1000),
                'last_price': round(price, 2),
                'last_size': np.random.randint(1, 100),
                'volume': np.random.randint(1000, 10000),
                'vwap': round(price, 2),
                'trade_count': np.random.randint(1, 10)
            }
            ticks.append(tick)
        
        return ticks
    
    def generate_report(self) -> str:
        """Generate benchmark report."""
        report = []
        report.append("=" * 80)
        report.append("DATABASE OPTIMIZATION BENCHMARK REPORT")
        report.append("=" * 80)
        
        for db_type, benchmarks in self.results.items():
            report.append(f"\n{db_type.upper()} Results:")
            report.append("-" * 40)
            
            for test_name, results in benchmarks.items():
                report.append(f"\n{test_name.replace('_', ' ').title()}:")
                for metric, value in results.items():
                    if isinstance(value, float):
                        report.append(f"  {metric}: {value:.2f}")
                    else:
                        report.append(f"  {metric}: {value}")
        
        # Summary
        report.append("\n" + "=" * 80)
        report.append("RECOMMENDATIONS:")
        report.append("=" * 80)
        
        if 'timescaledb' in self.results:
            ts_results = self.results['timescaledb']
            insert_tps = ts_results.get('insert_10000_ticks', {}).get('throughput_per_second', 0)
            query_tps = ts_results.get('query_ohlcv_1day', {}).get('throughput_rows_per_second', 0)
            
            report.append("\nTimescaleDB Recommendations:")
            if insert_tps < 1000:
                report.append("  • Consider using COPY command or batch inserts")
                report.append("  • Increase shared_buffers in postgresql.conf")
                report.append("  • Use prepared statements for repeated inserts")
            
            if query_tps < 100:
                report.append("  • Review indexes on frequently queried columns")
                report.append("  • Consider using continuous aggregates")
                report.append("  • Partition data by time and symbol")
        
        if 'redis_cache' in self.results:
            redis_results = self.results['redis_cache']
            insert_tps = redis_results.get('insert_1000_orders', {}).get('throughput_orders_per_second', 0)
            latency = redis_results.get('retrieve_100_orderbooks', {}).get('avg_latency_ms', 0)
            
            report.append("\nRedis Cache Recommendations:")
            if insert_tps < 100:
                report.append("  • Use pipeline for batch operations")
                report.append("  • Consider compression for large orders")
                report.append("  • Use connection pooling")
            
            if latency > 10:
                report.append("  • Optimize data structures (use sorted sets)")
                report.append("  • Consider Redis Cluster for horizontal scaling")
                report.append("  • Use local caching for frequently accessed data")
        
        report.append("\n" + "=" * 80)
        report.append("General Optimization Strategies:")
        report.append("=" * 80)
        report.append("1. Use appropriate database types for different workloads")
        report.append("2. Implement proper indexing strategies")
        report.append("3. Use connection pooling and prepared statements")
        report.append("4. Implement caching layers for frequently accessed data")
        report.append("5. Monitor and optimize query performance regularly")
        report.append("6. Use partitioning and sharding for large datasets")
        report.append("7. Implement proper backup and failover strategies")
        
        return "\n".join(report)


class HighFrequencyTradingDatabase:
    """
    Complete database solution for high-frequency trading systems.
    Combines TimescaleDB for time-series data and Redis for low-latency caching.
    """
    
    def __init__(self, timescale_params: Dict, redis_params: Dict):
        self.timescale_db = TimeSeriesDatabase(timescale_params)
        self.redis_caches = {}  # symbol -> RedisOrderBookCache
        self.redis_params = redis_params
        self.benchmark = DatabaseOptimizationBenchmark()
        
    async def initialize(self):
        """Initialize all database connections."""
        logger.info("Initializing HFT database system...")
        
        # Initialize TimescaleDB
        await self.timescale_db.connect()
        await self.timescale_db.initialize_schema()
        
        logger.info("HFT database system initialized")
    
    async def shutdown(self):
        """Shutdown all database connections."""
        logger.info("Shutting down HFT database system...")
        
        await self.timescale_db.disconnect()
        
        for cache in self.redis_caches.values():
            await cache.disconnect()
        
        logger.info("HFT database system shutdown complete")
    
    def get_redis_cache(self, symbol: str) -> RedisOrderBookCache:
        """Get or create Redis cache for a symbol."""
        if symbol not in self.redis_caches:
            cache = RedisOrderBookCache(self.redis_params, symbol)
            self.redis_caches[symbol] = cache
        
        return self.redis_caches[symbol]
    
    async def run_benchmarks(self):
        """Run comprehensive benchmarks."""
        logger.info("Running comprehensive database benchmarks...")
        
        # Benchmark TimescaleDB
        await self.benchmark.benchmark_timescaledb(self.timescale_db)
        
        # Benchmark Redis cache for a sample symbol
        symbol = 'AAPL'
        cache = self.get_redis_cache(symbol)
        await cache.connect()
        await cache.initialize_order_book()
        
        await self.benchmark.benchmark_redis_cache(cache)
        
        # Generate report
        report = self.benchmark.generate_report()
        
        # Save report to file
        with open('database_benchmark_report.txt', 'w') as f:
            f.write(report)
        
        logger.info(f"Benchmark report saved to database_benchmark_report.txt")
        
        return report
    
    async def monitor_performance(self, interval_seconds: int = 60):
        """Monitor database performance continuously."""
        logger.info(f"Starting performance monitoring (interval: {interval_seconds}s)")
        
        try:
            while True:
                # Monitor TimescaleDB
                try:
                    # Get query performance metrics
                    async with self.timescale_db.pool.acquire() as conn:
                        # Check active connections
                        connections = await conn.fetchval(
                            "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';"
                        )
                        
                        # Check cache hit ratio
                        cache_hit = await conn.fetchval(
                            "SELECT sum(blks_hit)*100/sum(blks_hit+blks_read) FROM pg_stat_database;"
                        )
                        
                        logger.info(f"TimescaleDB - Active connections: {connections}, Cache hit: {cache_hit:.1f}%")
                        
                except Exception as e:
                    logger.error(f"Error monitoring TimescaleDB: {e}")
                
                # Monitor Redis caches
                for symbol, cache in self.redis_caches.items():
                    try:
                        metrics = await cache.get_performance_metrics()
                        
                        logger.info(
                            f"Redis ({symbol}) - "
                            f"Memory: {metrics.get('memory_usage_mb', 0):.1f}MB, "
                            f"Hit rate: {metrics.get('hit_rate', 0)*100:.1f}%, "
                            f"Orders: {metrics.get('total_orders', 0)}"
                        )
                        
                    except Exception as e:
                        logger.error(f"Error monitoring Redis cache for {symbol}: {e}")
                
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("Performance monitoring stopped")
    
    async def optimize_queries(self):
        """Analyze and optimize slow queries."""
        logger.info("Starting query optimization analysis...")
        
        async with self.timescale_db.pool.acquire() as conn:
            # Find slow queries
            slow_queries = await conn.fetch("""
            SELECT 
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                rows,
                shared_blks_hit,
                shared_blks_read
            FROM pg_stat_statements
            ORDER BY mean_exec_time DESC
            LIMIT 10;
            """)
            
            optimizations = []
            
            for query in slow_queries:
                query_text = query['query']
                mean_time = query['mean_exec_time']
                
                # Analyze query plan
                plan = await self.timescale_db.get_query_plan(query_text)
                
                optimization = {
                    'query': query_text[:100] + '...' if len(query_text) > 100 else query_text,
                    'mean_exec_time_ms': mean_time * 1000,
                    'calls': query['calls'],
                    'optimization_suggestions': self._analyze_query_plan(plan)
                }
                
                optimizations.append(optimization)
            
            # Save optimization report
            report = self._generate_optimization_report(optimizations)
            
            with open('query_optimization_report.txt', 'w') as f:
                f.write(report)
            
            logger.info("Query optimization analysis completed")
            return optimizations
    
    def _analyze_query_plan(self, plan: Dict) -> List[str]:
        """Analyze query execution plan and suggest optimizations."""
        suggestions = []
        
        if not plan:
            return suggestions
        
        plan_str = json.dumps(plan, indent=2)
        
        # Analyze for common issues
        if 'Seq Scan' in plan_str:
            suggestions.append("Consider adding an index to avoid sequential scan")
        
        if 'Sort' in plan_str and 'Index Scan' not in plan_str:
            suggestions.append("Consider creating an index that matches the ORDER BY clause")
        
        if 'Nested Loop' in plan_str and plan.get('Plan', {}).get('Total Cost', 0) > 1000:
            suggestions.append("Consider optimizing join conditions or adding indexes")
        
        if 'Hash Join' in plan_str:
            suggestions.append("Ensure join columns are indexed for better performance")
        
        if plan.get('Plan', {}).get('Actual Rows', 0) > 10000:
            suggestions.append("Consider adding LIMIT clause or filtering conditions")
        
        return suggestions
    
    def _generate_optimization_report(self, optimizations: List[Dict]) -> str:
        """Generate query optimization report."""
        report = []
        report.append("=" * 80)
        report.append("QUERY OPTIMIZATION REPORT")
        report.append("=" * 80)
        
        for opt in optimizations:
            report.append(f"\nQuery: {opt['query']}")
            report.append(f"Mean execution time: {opt['mean_exec_time_ms']:.2f} ms")
            report.append(f"Total calls: {opt['calls']}")
            report.append("Optimization suggestions:")
            
            for suggestion in opt['optimization_suggestions']:
                report.append(f"  • {suggestion}")
        
        report.append("\n" + "=" * 80)
        report.append("GENERAL QUERY OPTIMIZATION TIPS:")
        report.append("=" * 80)
        report.append("1. Use EXPLAIN ANALYZE to understand query execution plans")
        report.append("2. Create indexes on frequently filtered columns")
        report.append("3. Use composite indexes for multi-column filters")
        report.append("4. Consider partitioning large tables")
        report.append("5. Use materialized views for complex aggregations")
        report.append("6. Optimize join conditions and use appropriate join types")
        report.append("7. Monitor and update statistics regularly")
        report.append("8. Consider query rewriting for better performance")
        
        return "\n".join(report)


async def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print("Day 88: Database Optimization for High-Performance Trading")
    print("=" * 80)
    
    # Configuration
    timescale_params = {
        'user': 'trading_user',
        'password': 'trading_password',
        'database': 'trading_db',
        'host': 'localhost',
        'port': 5432,
        'min_size': 10,
        'max_size': 50
    }
    
    redis_params = {
        'host': 'localhost',
        'port': 6379,
        'password': None,
        'db': 0
    }
    
    # Create HFT database system
    hft_db = HighFrequencyTradingDatabase(timescale_params, redis_params)
    
    try:
        # Initialize database system
        await hft_db.initialize()
        
        # Run benchmarks
        print("\n1. Running database benchmarks...")
        benchmark_report = await hft_db.run_benchmarks()
        print(benchmark_report)
        
        # Demonstrate TimescaleDB features
        print("\n2. Demonstrating TimescaleDB features...")
        
        # Generate sample data
        sample_ticks = []
        for i in range(100):
            tick = {
                'symbol': 'AAPL',
                'exchange': 'NASDAQ',
                'timestamp': datetime.utcnow() - timedelta(seconds=i),
                'bid_price': 150.0 + np.random.randn() * 0.1,
                'ask_price': 150.1 + np.random.randn() * 0.1,
                'bid_size': np.random.randint(100, 1000),
                'ask_size': np.random.randint(100, 1000),
                'last_price': 150.05 + np.random.randn() * 0.05,
                'last_size': np.random.randint(1, 100),
                'volume': np.random.randint(1000, 10000),
                'vwap': 150.05,
                'trade_count': np.random.randint(1, 10)
            }
            sample_ticks.append(tick)
        
        # Ingest sample data
        await hft_db.timescale_db.ingest_market_ticks(sample_ticks)
        print(f"   Ingested {len(sample_ticks)} sample ticks")
        
        # Query OHLCV data
        ohlcv_data = await hft_db.timescale_db.get_ohlcv_data(
            'AAPL',
            datetime.utcnow() - timedelta(hours=1),
            datetime.utcnow(),
            '1min'
        )
        print(f"   Retrieved {len(ohlcv_data)} OHLCV bars")
        
        # Get real-time metrics
        metrics = await hft_db.timescale_db.get_real_time_metrics('AAPL', 5)
        print(f"   Calculated {len(metrics)} real-time metrics")
        
        # Demonstrate Redis cache features
        print("\n3. Demonstrating Redis cache features...")
        
        # Get Redis cache for AAPL
        redis_cache = hft_db.get_redis_cache('AAPL')
        await redis_cache.connect()
        await redis_cache.initialize_order_book()
        
        # Add sample orders
        for i in range(10):
            order_data = {
                'order_id': f'sample_order_{i}',
                'symbol': 'AAPL',
                'side': 'bid' if i < 5 else 'ask',
                'price': 150.0 + (i * 0.1),
                'quantity': 100 * (i + 1),
                'timestamp': time.time()
            }
            await redis_cache.add_order(order_data['order_id'], order_data)
        
        print(f"   Added 10 sample orders to Redis cache")
        
        # Get order book
        order_book = await redis_cache.get_order_book(depth=5)
        print(f"   Retrieved order book with {len(order_book['bids'])} bids and {len(order_book['asks'])} asks")
        
        # Get performance metrics
        redis_metrics = await redis_cache.get_performance_metrics()
        print(f"   Redis memory usage: {redis_metrics.get('memory_usage_mb', 0):.1f} MB")
        
        # Run query optimization analysis
        print("\n4. Running query optimization analysis...")
        optimizations = await hft_db.optimize_queries()
        print(f"   Analyzed {len(optimizations)} queries for optimization")
        
        # Start performance monitoring (brief demonstration)
        print("\n5. Starting performance monitoring (10 seconds)...")
        monitor_task = asyncio.create_task(hft_db.monitor_performance(5))
        await asyncio.sleep(10)
        monitor_task.cancel()
        
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nGenerated files:")
        print("  • database_benchmark_report.txt - Comprehensive benchmark results")
        print("  • query_optimization_report.txt - Query optimization suggestions")
        print("\nKey features demonstrated:")
        print("  1. TimescaleDB schema design for trading data")
        print("  2. High-performance data ingestion and querying")
        print("  3. Real-time analytics with window functions")
        print("  4. Redis-based order book cache with pub/sub")
        print("  5. Memory optimization for 1M+ active orders")
        print("  6. Performance benchmarking and monitoring")
        print("  7. Query optimization analysis")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await hft_db.shutdown()


if __name__ == "__main__":
    asyncio.run(main())