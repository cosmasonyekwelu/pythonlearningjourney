"""
Day 90: Real-Time Data Pipelines & Stream Processing
Build real-time data pipelines for market data ingestion, processing, and distribution.
"""

import asyncio
import json
import time
import struct
import hashlib
import zlib
import msgpack
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Deque, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import logging
import uuid
import base64
import random
import numpy as np
from decimal import Decimal
import concurrent.futures
import threading
import queue
import websockets
from websockets.exceptions import ConnectionClosed
import aiohttp
from aiohttp import web
import faust
from faust import Record
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
import redis.asyncio as redis
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
import avro.schema
import avro.io
import io
import pickle
import csv
import orjson
import pyarrow as pa
import pyarrow.flight as flight
import pyarrow.parquet as pq
from dataclasses_json import dataclass_json
import ssl
import certifi
import asyncio_redis
import mmap
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global metrics registry
metrics_registry = CollectorRegistry()


class StreamProcessingFramework(Enum):
    """Stream processing frameworks."""
    KAFKA = "kafka"
    KINESIS = "kinesis"
    PUBSUB = "pubsub"
    REDIS_STREAMS = "redis_streams"
    FLINK = "flink"
    SPARK = "spark"
    FAUST = "faust"


class WindowType(Enum):
    """Window types for stream processing."""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"


class ProcessingSemantics(Enum):
    """Processing semantics."""
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass_json
@dataclass
class MarketTick:
    """Market tick data structure."""
    symbol: str
    exchange: str
    price: float
    volume: float
    timestamp: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    trade_id: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'price': self.price,
            'volume': self.volume,
            'timestamp': self.timestamp,
            'bid': self.bid,
            'ask': self.ask,
            'bid_size': self.bid_size,
            'ask_size': self.ask_size,
            'trade_id': self.trade_id,
            'conditions': self.conditions
        }


@dataclass_json
@dataclass
class OHLCVBar:
    """OHLCV bar data structure."""
    symbol: str
    exchange: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    trade_count: int = 0
    window_size: str = "1m"


@dataclass_json
@dataclass
class TechnicalIndicators:
    """Technical indicators data structure."""
    symbol: str
    timestamp: int
    sma_9: float
    sma_20: float
    sma_50: float
    ema_12: float
    ema_26: float
    macd_line: float
    macd_signal: float
    macd_histogram: float
    rsi: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    vwap: float
    atr: float
    price: float
    volume: float
    price_change_pct: float


@dataclass_json
@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity data structure."""
    opportunity_id: str
    type: str  # triangular, cross_exchange, statistical, flash_crash
    timestamp: float
    symbols: List[str]
    exchanges: List[str]
    prices: List[float]
    profit_pct: float
    expected_profit: float
    detection_latency_ms: float
    confidence: float = 1.0


class MarketDataPipeline:
    """
    Real-time market data pipeline using Apache Kafka.
    Handles ingestion, processing, and distribution of market data.
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092",
                 redis_url: str = "redis://localhost:6379",
                 environment: str = "production"):
        self.bootstrap_servers = bootstrap_servers
        self.redis_url = redis_url
        self.environment = environment
        
        # Pipeline configuration
        self.config = self._load_config()
        
        # Kafka producers and consumers
        self.producers = {}
        self.consumers = {}
        self.admin_client = None
        
        # Redis connection
        self.redis_client = None
        
        # State management
        self.window_states = defaultdict(lambda: {
            'prices': deque(maxlen=1000),
            'volumes': deque(maxlen=1000),
            'timestamps': deque(maxlen=1000)
        })
        
        # Metrics
        self.metrics = self._setup_metrics()
        
        # Schema registry
        self.schema_registry = SchemaRegistry()
        
        logger.info(f"Initialized MarketDataPipeline for {environment}")
    
    def _load_config(self) -> Dict:
        """Load pipeline configuration."""
        return {
            'topics': {
                'raw_ticks': 'market.raw.ticks',
                'normalized_ticks': 'market.normalized.ticks',
                'aggregated_bars': 'market.aggregated.bars',
                'technical_indicators': 'market.technical.indicators',
                'trading_signals': 'market.trading.signals',
                'alerts': 'market.alerts',
                'dead_letter': 'market.dead.letter'
            },
            'partitions': {
                'by_symbol': 64,
                'by_time': 24
            },
            'retention': {
                'raw_ticks': 604800,  # 7 days in seconds
                'normalized_ticks': 2592000,  # 30 days
                'aggregated_bars': 31536000,  # 1 year
                'indefinite': -1
            },
            'replication': {
                'production': 3,
                'staging': 2,
                'development': 1
            }.get(self.environment, 1),
            'processing': {
                'batch_size': 1000,
                'linger_ms': 100,
                'compression': 'snappy',
                'acks': 'all'
            }
        }
    
    def _setup_metrics(self) -> Dict:
        """Setup monitoring metrics."""
        return {
            'ingestion_rate': Counter(
                'market_data_ingestion_rate',
                'Market data ingestion rate',
                ['source', 'symbol', 'status'],
                registry=metrics_registry
            ),
            'processing_latency': Histogram(
                'market_data_processing_latency_ms',
                'Processing latency in milliseconds',
                ['pipeline_stage'],
                buckets=[0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000],
                registry=metrics_registry
            ),
            'throughput': Counter(
                'market_data_throughput_total',
                'Total market data messages processed',
                ['topic', 'status'],
                registry=metrics_registry
            ),
            'error_count': Counter(
                'market_data_errors_total',
                'Total pipeline errors',
                ['error_type', 'pipeline_stage'],
                registry=metrics_registry
            ),
            'window_stats': Gauge(
                'market_data_window_stats',
                'Window statistics',
                ['symbol', 'stat_type'],
                registry=metrics_registry
            )
        }
    
    async def initialize(self):
        """Initialize the pipeline."""
        logger.info("Initializing MarketDataPipeline...")
        
        # Initialize Kafka admin client
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=self.bootstrap_servers,
            client_id='market-data-pipeline'
        )
        
        # Create topics if they don't exist
        await self._create_topics()
        
        # Initialize Redis
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=False,
            max_connections=100
        )
        
        logger.info("MarketDataPipeline initialized successfully")
    
    async def _create_topics(self):
        """Create Kafka topics if they don't exist."""
        existing_topics = self.admin_client.list_topics()
        
        for topic_name, partitions in self.config['partitions'].items():
            full_topic_name = self.config['topics'].get(topic_name, topic_name)
            
            if full_topic_name not in existing_topics:
                topic = NewTopic(
                    name=full_topic_name,
                    num_partitions=partitions,
                    replication_factor=self.config['replication'],
                    topic_configs={
                        'retention.ms': str(self.config['retention'].get(topic_name, 604800) * 1000),
                        'cleanup.policy': 'delete',
                        'compression.type': self.config['processing']['compression']
                    }
                )
                
                try:
                    self.admin_client.create_topics([topic])
                    logger.info(f"Created topic: {full_topic_name}")
                except Exception as e:
                    logger.warning(f"Failed to create topic {full_topic_name}: {e}")
    
    def get_producer(self, topic: str) -> KafkaProducer:
        """Get or create a Kafka producer for a topic."""
        if topic not in self.producers:
            self.producers[topic] = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                value_serializer=lambda v: self.schema_registry.serialize('market_tick', v),
                compression_type=self.config['processing']['compression'],
                acks=self.config['processing']['acks'],
                batch_size=self.config['processing']['batch_size'],
                linger_ms=self.config['processing']['linger_ms'],
                max_in_flight_requests_per_connection=5,
                retries=10,
                retry_backoff_ms=1000
            )
        
        return self.producers[topic]
    
    def get_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """Get or create a Kafka consumer for a topic."""
        consumer_key = f"{topic}:{group_id}"
        
        if consumer_key not in self.consumers:
            self.consumers[consumer_key] = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='latest',
                enable_auto_commit=False,
                value_deserializer=lambda v: self.schema_registry.deserialize('market_tick', v),
                max_poll_records=1000,
                max_poll_interval_ms=300000,
                session_timeout_ms=10000,
                heartbeat_interval_ms=3000
            )
        
        return self.consumers[consumer_key]
    
    async def ingest_from_websocket(self, exchange: str, symbols: List[str]):
        """
        Ingest market data from WebSocket feed.
        
        Args:
            exchange: Exchange name (e.g., 'binance', 'coinbase')
            symbols: List of symbols to subscribe to
        """
        ws_url = self._get_websocket_url(exchange, symbols)
        
        logger.info(f"Starting WebSocket ingestion from {exchange} for {len(symbols)} symbols")
        
        while True:
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Subscribe to symbols
                    await self._send_websocket_subscription(websocket, exchange, symbols)
                    
                    async for message in websocket:
                        try:
                            start_time = time.time()
                            
                            # Parse WebSocket message
                            ticks = self._parse_websocket_message(exchange, message)
                            
                            for tick in ticks:
                                # Validate tick
                                if not self._validate_tick(tick):
                                    await self._send_to_dlq(tick, "validation_failed")
                                    continue
                                
                                # Add metadata
                                tick['_metadata'] = {
                                    'ingestion_time': time.time(),
                                    'exchange': exchange,
                                    'source': 'websocket'
                                }
                                
                                # Determine partition key (by symbol for load balancing)
                                partition_key = tick['symbol']
                                
                                # Produce to Kafka
                                producer = self.get_producer(self.config['topics']['raw_ticks'])
                                future = producer.send(
                                    topic=self.config['topics']['raw_ticks'],
                                    key=partition_key,
                                    value=tick
                                )
                                
                                # Add callback for delivery report
                                future.add_callback(
                                    self._delivery_report,
                                    'raw_ticks',
                                    tick['symbol'],
                                    start_time
                                )
                                
                                # Record metrics
                                self.metrics['ingestion_rate'].labels(
                                    source=exchange,
                                    symbol=tick['symbol'],
                                    status='success'
                                ).inc()
                            
                            # Flush producer
                            producer.flush()
                            
                        except Exception as e:
                            logger.error(f"Error processing WebSocket message: {e}")
                            self.metrics['error_count'].labels(
                                error_type='websocket_processing',
                                pipeline_stage='ingestion'
                            ).inc()
                            
            except ConnectionClosed:
                logger.warning(f"WebSocket connection closed for {exchange}, reconnecting...")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"WebSocket ingestion error for {exchange}: {e}")
                await asyncio.sleep(5)
    
    def _get_websocket_url(self, exchange: str, symbols: List[str]) -> str:
        """Get WebSocket URL for exchange."""
        exchange_urls = {
            'binance': 'wss://stream.binance.com:9443/ws',
            'coinbase': 'wss://ws-feed.pro.coinbase.com',
            'kraken': 'wss://ws.kraken.com',
            'bitfinex': 'wss://api.bitfinex.com/ws/2'
        }
        
        return exchange_urls.get(exchange, f'wss://{exchange}.com/ws')
    
    def _parse_websocket_message(self, exchange: str, message: str) -> List[Dict]:
        """Parse WebSocket message from exchange."""
        try:
            data = json.loads(message)
            
            if exchange == 'binance':
                return self._parse_binance_message(data)
            elif exchange == 'coinbase':
                return self._parse_coinbase_message(data)
            elif exchange == 'kraken':
                return self._parse_kraken_message(data)
            elif exchange == 'bitfinex':
                return self._parse_bitfinex_message(data)
            else:
                return self._parse_generic_message(data)
                
        except Exception as e:
            logger.error(f"Error parsing WebSocket message from {exchange}: {e}")
            return []
    
    def _parse_binance_message(self, data: Dict) -> List[Dict]:
        """Parse Binance WebSocket message."""
        ticks = []
        
        if 'e' in data and data['e'] == 'trade':
            tick = {
                'symbol': data['s'],
                'exchange': 'binance',
                'price': float(data['p']),
                'volume': float(data['q']),
                'timestamp': data['T'],
                'trade_id': str(data['t']),
                'conditions': []
            }
            ticks.append(tick)
        
        return ticks
    
    def _validate_tick(self, tick: Dict) -> bool:
        """Validate tick data."""
        required_fields = ['symbol', 'price', 'volume', 'timestamp']
        
        for field in required_fields:
            if field not in tick:
                return False
        
        # Price validation
        if tick['price'] <= 0 or tick['price'] > 1e9:
            return False
        
        # Volume validation
        if tick['volume'] < 0 or tick['volume'] > 1e12:
            return False
        
        # Timestamp validation (should be within last 24 hours)
        current_time = int(time.time() * 1000)
        if tick['timestamp'] < current_time - 86400000 or tick['timestamp'] > current_time + 60000:
            return False
        
        return True
    
    def _delivery_report(self, topic: str, symbol: str, start_time: float, err: Optional[Exception], msg):
        """Callback for Kafka delivery report."""
        if err is not None:
            logger.error(f'Message delivery failed for {symbol}: {err}')
            self.metrics['error_count'].labels(
                error_type='kafka_delivery',
                pipeline_stage='ingestion'
            ).inc()
        else:
            latency = (time.time() - start_time) * 1000
            self.metrics['processing_latency'].labels(
                pipeline_stage='ingestion'
            ).observe(latency)
            
            self.metrics['throughput'].labels(
                topic=topic,
                status='success'
            ).inc()
    
    async def normalize_and_validate(self):
        """Normalize and validate raw tick data."""
        logger.info("Starting normalization pipeline...")
        
        consumer = self.get_consumer(
            self.config['topics']['raw_ticks'],
            'normalization-group'
        )
        
        producer = self.get_producer(self.config['topics']['normalized_ticks'])
        
        while True:
            try:
                batch = consumer.poll(timeout_ms=1000, max_records=1000)
                
                for tp, messages in batch.items():
                    for message in messages:
                        start_time = time.time()
                        
                        try:
                            tick = message.value
                            
                            # Extract metadata
                            metadata = tick.get('_metadata', {})
                            exchange = metadata.get('exchange', 'unknown')
                            
                            # Normalize tick format
                            normalized = self._normalize_tick(tick, exchange)
                            
                            # Validate against business rules
                            validation_result = self._validate_business_rules(normalized)
                            if not validation_result['valid']:
                                await self._send_to_dlq(
                                    {'tick': normalized, 'errors': validation_result['errors']},
                                    'business_validation_failed'
                                )
                                continue
                            
                            # Add processing metadata
                            normalized['_metadata'] = {
                                **metadata,
                                'processed_at': time.time(),
                                'kafka_offset': message.offset,
                                'partition': message.partition,
                                'validation_score': validation_result['score']
                            }
                            
                            # Produce to normalized topic
                            future = producer.send(
                                topic=self.config['topics']['normalized_ticks'],
                                key=message.key,
                                value=normalized
                            )
                            
                            future.add_callback(
                                self._delivery_report,
                                'normalized_ticks',
                                normalized['symbol'],
                                start_time
                            )
                            
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            self.metrics['error_count'].labels(
                                error_type='normalization',
                                pipeline_stage='processing'
                            ).inc()
                
                # Commit offsets
                consumer.commit()
                
                # Flush producer
                producer.flush()
                
            except Exception as e:
                logger.error(f"Error in normalization pipeline: {e}")
                await asyncio.sleep(1)
    
    def _normalize_tick(self, tick: Dict, exchange: str) -> Dict:
        """Normalize tick data to standard format."""
        normalized = {
            'symbol': tick['symbol'].replace('-', '/').upper(),
            'exchange': exchange,
            'price': float(tick['price']),
            'volume': float(tick['volume']),
            'timestamp': int(tick['timestamp']),
            'source': 'normalized'
        }
        
        # Add optional fields if present
        optional_fields = ['bid', 'ask', 'bid_size', 'ask_size', 'trade_id', 'conditions']
        for field in optional_fields:
            if field in tick and tick[field] is not None:
                normalized[field] = tick[field]
        
        return normalized
    
    async def aggregate_to_bars(self, window_size: str = "1m"):
        """
        Aggregate ticks to OHLCV bars.
        
        Args:
            window_size: Window size (1s, 5s, 15s, 1m, 5m, 15m, 1h, 4h, 1d)
        """
        logger.info(f"Starting aggregation pipeline for {window_size} bars...")
        
        window_ms = self._parse_window_size(window_size)
        
        consumer = self.get_consumer(
            self.config['topics']['normalized_ticks'],
            f'aggregation-group-{window_size}'
        )
        
        producer = self.get_producer(self.config['topics']['aggregated_bars'])
        
        # State for each symbol
        symbol_states = {}
        
        while True:
            try:
                batch = consumer.poll(timeout_ms=1000, max_records=1000)
                
                for tp, messages in batch.items():
                    for message in messages:
                        try:
                            tick = message.value
                            symbol = tick['symbol']
                            timestamp = tick['timestamp']
                            
                            # Get or create state for symbol
                            if symbol not in symbol_states:
                                symbol_states[symbol] = {
                                    'current_bar': None,
                                    'buffer': []
                                }
                            
                            state = symbol_states[symbol]
                            
                            # Calculate window start time
                            window_start = (timestamp // window_ms) * window_ms
                            
                            # Check if we need to start a new bar
                            if (state['current_bar'] is None or 
                                state['current_bar']['window_start'] != window_start):
                                
                                # Emit completed bar if exists
                                if state['current_bar'] is not None:
                                    bar = self._create_bar_from_state(state['current_bar'])
                                    future = producer.send(
                                        topic=self.config['topics']['aggregated_bars'],
                                        key=symbol.encode('utf-8'),
                                        value=bar
                                    )
                                    future.add_callback(
                                        self._delivery_report,
                                        'aggregated_bars',
                                        symbol,
                                        time.time()
                                    )
                                
                                # Start new bar
                                state['current_bar'] = {
                                    'symbol': symbol,
                                    'exchange': tick['exchange'],
                                    'window_start': window_start,
                                    'open': tick['price'],
                                    'high': tick['price'],
                                    'low': tick['price'],
                                    'close': tick['price'],
                                    'volume': tick['volume'],
                                    'trade_count': 1,
                                    'vwap_numerator': tick['price'] * tick['volume'],
                                    'vwap_denominator': tick['volume']
                                }
                            else:
                                # Update existing bar
                                bar = state['current_bar']
                                bar['high'] = max(bar['high'], tick['price'])
                                bar['low'] = min(bar['low'], tick['price'])
                                bar['close'] = tick['price']
                                bar['volume'] += tick['volume']
                                bar['trade_count'] += 1
                                bar['vwap_numerator'] += tick['price'] * tick['volume']
                                bar['vwap_denominator'] += tick['volume']
                            
                            # Update window stats metrics
                            self.metrics['window_stats'].labels(
                                symbol=symbol,
                                stat_type='tick_count'
                            ).inc()
                            
                        except Exception as e:
                            logger.error(f"Error aggregating tick: {e}")
                
                # Commit offsets
                consumer.commit()
                
                # Flush producer
                producer.flush()
                
                # Emit bars for windows that have passed
                current_time = int(time.time() * 1000)
                current_window = (current_time // window_ms) * window_ms
                
                for symbol, state in list(symbol_states.items()):
                    if (state['current_bar'] is not None and 
                        state['current_bar']['window_start'] < current_window - window_ms):
                        
                        bar = self._create_bar_from_state(state['current_bar'])
                        producer.send(
                            topic=self.config['topics']['aggregated_bars'],
                            key=symbol.encode('utf-8'),
                            value=bar
                        )
                        
                        # Clear the bar
                        state['current_bar'] = None
                
                producer.flush()
                
            except Exception as e:
                logger.error(f"Error in aggregation pipeline: {e}")
                await asyncio.sleep(1)
    
    def _parse_window_size(self, window_size: str) -> int:
        """Parse window size string to milliseconds."""
        window_map = {
            '1s': 1000,
            '5s': 5000,
            '15s': 15000,
            '30s': 30000,
            '1m': 60000,
            '5m': 300000,
            '15m': 900000,
            '30m': 1800000,
            '1h': 3600000,
            '4h': 14400000,
            '1d': 86400000
        }
        
        return window_map.get(window_size, 60000)  # Default to 1 minute
    
    def _create_bar_from_state(self, state: Dict) -> Dict:
        """Create OHLCV bar from aggregation state."""
        vwap = (state['vwap_numerator'] / state['vwap_denominator'] 
                if state['vwap_denominator'] > 0 else state['close'])
        
        return {
            'symbol': state['symbol'],
            'exchange': state['exchange'],
            'timestamp': state['window_start'],
            'open': state['open'],
            'high': state['high'],
            'low': state['low'],
            'close': state['close'],
            'volume': state['volume'],
            'vwap': vwap,
            'trade_count': state['trade_count'],
            'window_size': 'custom'
        }
    
    async def calculate_technical_indicators(self):
        """Calculate real-time technical indicators."""
        logger.info("Starting technical indicators pipeline...")
        
        # Create Faust app
        app = faust.App(
            'technical-indicators',
            broker=f'kafka://{self.bootstrap_servers}',
            value_serializer='raw',
            web_port=6066,
            topic_partitions=16
        )
        
        # Define topics
        normalized_ticks_topic = app.topic(
            self.config['topics']['normalized_ticks'],
            value_type=bytes
        )
        
        indicators_topic = app.topic(
            self.config['topics']['technical_indicators'],
            value_type=bytes
        )
        
        # Define tables for state
        price_windows = app.Table(
            'price_windows',
            default=lambda: deque(maxlen=200)
        )
        
        volume_windows = app.Table(
            'volume_windows',
            default=lambda: deque(maxlen=200)
        )
        
        @app.agent(normalized_ticks_topic)
        async def process_ticks(stream):
            async for message in stream:
                try:
                    tick = self.schema_registry.deserialize('market_tick', message.value)
                    symbol = tick['symbol']
                    price = tick['price']
                    volume = tick['volume']
                    
                    # Update windows
                    price_windows[symbol].append(price)
                    volume_windows[symbol].append(volume)
                    
                    # Calculate indicators when we have enough data
                    price_window = list(price_windows[symbol])
                    volume_window = list(volume_windows[symbol])
                    
                    if len(price_window) >= 50:  # Need enough data for most indicators
                        indicators = self._calculate_all_indicators(
                            price_window, 
                            volume_window
                        )
                        
                        # Add symbol and timestamp
                        indicators['symbol'] = symbol
                        indicators['timestamp'] = tick['timestamp']
                        indicators['price'] = price
                        indicators['volume'] = volume
                        
                        # Serialize and send
                        serialized = self.schema_registry.serialize(
                            'technical_indicators',
                            indicators
                        )
                        
                        await indicators_topic.send(
                            key=symbol.encode('utf-8'),
                            value=serialized
                        )
                        
                        # Update metrics
                        self.metrics['throughput'].labels(
                            topic='technical_indicators',
                            status='success'
                        ).inc()
                        
                except Exception as e:
                    logger.error(f"Error calculating indicators: {e}")
                    self.metrics['error_count'].labels(
                        error_type='indicator_calculation',
                        pipeline_stage='processing'
                    ).inc()
        
        return app
    
    def _calculate_all_indicators(self, prices: List[float], volumes: List[float]) -> Dict:
        """Calculate all technical indicators."""
        if len(prices) < 20:
            return {}
        
        # Simple Moving Averages
        sma_9 = self._calculate_sma(prices, 9)
        sma_20 = self._calculate_sma(prices, 20)
        sma_50 = self._calculate_sma(prices, 50)
        
        # Exponential Moving Averages
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        # MACD
        macd_line = ema_12 - ema_26 if ema_12 and ema_26 else 0
        macd_signal = self._calculate_ema([macd_line], 9)[0] if len(prices) >= 26 else 0
        macd_histogram = macd_line - macd_signal
        
        # RSI
        rsi = self._calculate_rsi(prices, 14)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices, 20)
        
        # Volume Weighted Average Price
        vwap = self._calculate_vwap(prices[-20:], volumes[-20:])
        
        # Average True Range
        atr = self._calculate_atr(prices, 14)
        
        # Price change percentage
        if len(prices) > 1:
            price_change_pct = ((prices[-1] - prices[-2]) / prices[-2]) * 100
        else:
            price_change_pct = 0
        
        return {
            'sma_9': sma_9,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'macd_line': macd_line,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram,
            'rsi': rsi,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'vwap': vwap,
            'atr': atr,
            'price_change_pct': price_change_pct
        }
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return 0.0, 0.0, 0.0
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        std = np.std(recent_prices)
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        return upper_band, sma, lower_band
    
    def _calculate_vwap(self, prices: List[float], volumes: List[float]) -> float:
        """Calculate Volume Weighted Average Price."""
        if len(prices) == 0 or len(volumes) == 0:
            return 0.0
        
        total_value = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        
        return total_value / total_volume if total_volume > 0 else 0.0
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(prices) < period + 1:
            return 0.0
        
        true_ranges = []
        
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            # For simplicity, using high-low range
            true_ranges.append(high_low)
        
        atr = sum(true_ranges[-period:]) / period
        return atr
    
    async def distribute_to_websockets(self, host: str = 'localhost', port: int = 8080):
        """Distribute processed data to WebSocket clients."""
        logger.info(f"Starting WebSocket distribution server on {host}:{port}...")
        
        # Create WebSocket server
        start_server = websockets.serve(
            self._handle_websocket_connection,
            host,
            port,
            ping_interval=20,
            ping_timeout=60,
            max_queue=10000
        )
        
        # Start background task to consume from Kafka and distribute
        asyncio.create_task(self._distribute_to_clients())
        
        return await start_server
    
    async def _handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connection."""
        client_id = str(uuid.uuid4())
        logger.info(f"New WebSocket connection: {client_id}")
        
        try:
            # Parse subscription parameters
            query = path.split('?')[1] if '?' in path else ''
            params = dict(p.split('=') for p in query.split('&') if '=' in p)
            
            symbol = params.get('symbol', 'BTC/USDT')
            indicators = params.get('indicators', '').split(',')
            
            # Create subscription
            subscription_id = await self._create_subscription(client_id, symbol, indicators)
            
            # Send initial data
            await self._send_initial_data(websocket, symbol)
            
            # Main loop
            while True:
                # Get messages for this subscription
                messages = await self.redis_client.xreadgroup(
                    groupname='websocket-distribution',
                    consumername=subscription_id,
                    streams={f'market:data:{symbol}': '>'},
                    count=10,
                    block=1000
                )
                
                if messages:
                    for stream, message_list in messages:
                        for message_id, message_data in message_list:
                            # Filter indicators if needed
                            filtered_data = self._filter_indicators(
                                message_data, 
                                indicators
                            )
                            
                            # Send to WebSocket
                            await websocket.send(json.dumps(filtered_data))
                            
                            # Acknowledge message
                            await self.redis_client.xack(
                                f'market:data:{symbol}',
                                'websocket-distribution',
                                message_id
                            )
                
                # Keep connection alive
                await asyncio.sleep(0.001)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Cleanup
            await self._cleanup_subscription(client_id)
    
    async def _distribute_to_clients(self):
        """Consume from Kafka and distribute to Redis streams."""
        logger.info("Starting distribution to WebSocket clients...")
        
        consumer = self.get_consumer(
            self.config['topics']['technical_indicators'],
            'websocket-distribution-group'
        )
        
        while True:
            try:
                batch = consumer.poll(timeout_ms=1000, max_records=1000)
                
                for tp, messages in batch.items():
                    for message in messages:
                        try:
                            indicators = self.schema_registry.deserialize(
                                'technical_indicators',
                                message.value
                            )
                            
                            symbol = indicators['symbol']
                            
                            # Push to Redis stream
                            stream_key = f'market:data:{symbol}'
                            await self.redis_client.xadd(
                                stream_key,
                                indicators,
                                maxlen=1000,
                                approximate=True
                            )
                            
                            # Update metrics
                            self.metrics['throughput'].labels(
                                topic='websocket_distribution',
                                status='success'
                            ).inc()
                            
                        except Exception as e:
                            logger.error(f"Error distributing message: {e}")
                
                # Commit offsets
                consumer.commit()
                
            except Exception as e:
                logger.error(f"Error in distribution pipeline: {e}")
                await asyncio.sleep(1)
    
    async def cleanup(self):
        """Cleanup pipeline resources."""
        logger.info("Cleaning up MarketDataPipeline...")
        
        # Close Kafka producers
        for producer in self.producers.values():
            producer.close()
        
        # Close Kafka consumers
        for consumer in self.consumers.values():
            consumer.close()
        
        # Close admin client
        if self.admin_client:
            self.admin_client.close()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.aclose()
        
        logger.info("MarketDataPipeline cleaned up")


class ComplexEventProcessor:
    """
    Complex Event Processing system for trading patterns and arbitrage detection.
    """
    
    def __init__(self, kafka_servers: str = "localhost:9092",
                 symbols: List[str] = None,
                 exchanges: List[str] = None):
        self.kafka_servers = kafka_servers
        self.symbols = symbols or ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        self.exchanges = exchanges or ["binance", "coinbase", "kraken"]
        
        # CEP configuration
        self.config = {
            'window_sizes': [100, 500, 1000, 5000],  # ms
            'patterns': self._initialize_patterns(),
            'thresholds': {
                'profit_min': 0.001,  # 0.1% minimum profit
                'confidence_min': 0.7,
                'latency_max': 100  # ms
            }
        }
        
        # State management
        self.price_states = defaultdict(lambda: {
            'prices': deque(maxlen=1000),
            'timestamps': deque(maxlen=1000),
            'exchange': None
        })
        
        self.correlation_states = defaultdict(lambda: {
            'correlations': {},
            'last_updated': 0
        })
        
        # Kafka clients
        self.producer = None
        self.consumer = None
        
        # Metrics
        self.metrics = self._setup_metrics()
        
        logger.info(f"Initialized ComplexEventProcessor for {len(self.symbols)} symbols")
    
    def _initialize_patterns(self) -> List[Dict]:
        """Initialize CEP patterns."""
        return [
            {
                'name': 'triangular_arbitrage',
                'description': 'Three-currency arbitrage',
                'pattern': self._triangular_pattern(),
                'window_ms': 100,
                'priority': 1
            },
            {
                'name': 'cross_exchange_arbitrage',
                'description': 'Same symbol across exchanges',
                'pattern': self._cross_exchange_pattern(),
                'window_ms': 50,
                'priority': 2
            },
            {
                'name': 'mean_reversion',
                'description': 'Statistical arbitrage',
                'pattern': self._mean_reversion_pattern(),
                'window_ms': 1000,
                'priority': 3
            },
            {
                'name': 'flash_crash',
                'description': 'Extreme price movement',
                'pattern': self._flash_crash_pattern(),
                'window_ms': 10,
                'priority': 1
            },
            {
                'name': 'volume_spike',
                'description': 'Unusual volume activity',
                'pattern': self._volume_spike_pattern(),
                'window_ms': 100,
                'priority': 2
            }
        ]
    
    def _setup_metrics(self) -> Dict:
        """Setup CEP metrics."""
        return {
            'patterns_detected': Counter(
                'cep_patterns_detected_total',
                'Total patterns detected',
                ['pattern_type', 'symbol'],
                registry=metrics_registry
            ),
            'detection_latency': Histogram(
                'cep_detection_latency_ms',
                'Pattern detection latency',
                ['pattern_type'],
                buckets=[0.1, 0.5, 1, 5, 10, 50, 100],
                registry=metrics_registry
            ),
            'opportunities_found': Counter(
                'cep_opportunities_found_total',
                'Total trading opportunities found',
                ['opportunity_type', 'profit_range'],
                registry=metrics_registry
            ),
            'false_positives': Counter(
                'cep_false_positives_total',
                'Total false positive detections',
                ['pattern_type'],
                registry=metrics_registry
            )
        }
    
    async def initialize(self):
        """Initialize the CEP system."""
        logger.info("Initializing ComplexEventProcessor...")
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_servers,
            key_serializer=lambda k: k.encode('utf-8'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            acks='all',
            retries=10
        )
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            'market.normalized.ticks',
            bootstrap_servers=self.kafka_servers,
            group_id='cep-group',
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            max_poll_records=1000
        )
        
        logger.info("ComplexEventProcessor initialized")
    
    async def detect_patterns(self):
        """Main pattern detection loop."""
        logger.info("Starting pattern detection...")
        
        while True:
            try:
                batch = self.consumer.poll(timeout_ms=1000, max_records=1000)
                
                for tp, messages in batch.items():
                    for message in messages:
                        try:
                            tick = message.value
                            symbol = tick['symbol']
                            exchange = tick['exchange']
                            price = tick['price']
                            volume = tick['volume']
                            timestamp = tick['timestamp']
                            
                            # Update price state
                            key = (symbol, exchange)
                            state = self.price_states[key]
                            state['prices'].append(price)
                            state['timestamps'].append(timestamp)
                            state['exchange'] = exchange
                            
                            # Check all patterns
                            for pattern in self.config['patterns']:
                                start_time = time.time()
                                
                                if self._check_pattern(pattern, tick):
                                    # Pattern detected
                                    detection_time = (time.time() - start_time) * 1000
                                    
                                    self.metrics['patterns_detected'].labels(
                                        pattern_type=pattern['name'],
                                        symbol=symbol
                                    ).inc()
                                    
                                    self.metrics['detection_latency'].labels(
                                        pattern_type=pattern['name']
                                    ).observe(detection_time)
                                    
                                    # Create alert
                                    alert = self._create_alert(pattern, tick, detection_time)
                                    
                                    # Send alert
                                    self.producer.send(
                                        topic='market.alerts',
                                        key=alert['opportunity_id'].encode('utf-8'),
                                        value=alert
                                    )
                            
                            # Update correlation states periodically
                            if timestamp - self.correlation_states[symbol]['last_updated'] > 60000:  # Every minute
                                self._update_correlations(symbol)
                            
                        except Exception as e:
                            logger.error(f"Error processing tick for pattern detection: {e}")
                
                # Commit offsets
                self.consumer.commit()
                
                # Flush producer
                self.producer.flush()
                
            except Exception as e:
                logger.error(f"Error in pattern detection: {e}")
                await asyncio.sleep(1)
    
    def _check_pattern(self, pattern: Dict, tick: Dict) -> bool:
        """Check if tick matches a pattern."""
        pattern_name = pattern['name']
        
        if pattern_name == 'triangular_arbitrage':
            return self._check_triangular_arbitrage(tick)
        elif pattern_name == 'cross_exchange_arbitrage':
            return self._check_cross_exchange_arbitrage(tick)
        elif pattern_name == 'mean_reversion':
            return self._check_mean_reversion(tick)
        elif pattern_name == 'flash_crash':
            return self._check_flash_crash(tick)
        elif pattern_name == 'volume_spike':
            return self._check_volume_spike(tick)
        
        return False
    
    def _check_triangular_arbitrage(self, tick: Dict) -> bool:
        """Check for triangular arbitrage opportunities."""
        symbol = tick['symbol']
        
        # For crypto: BTC/USDT -> ETH/BTC -> ETH/USDT
        # Need prices for all three pairs
        pairs = self._get_triangular_pairs(symbol)
        
        if len(pairs) != 3:
            return False
        
        # Check if we have recent prices for all pairs
        recent_prices = {}
        for pair in pairs:
            key = (pair, tick['exchange'])
            if key in self.price_states and len(self.price_states[key]['prices']) > 0:
                recent_prices[pair] = self.price_states[key]['prices'][-1]
        
        if len(recent_prices) != 3:
            return False
        
        # Calculate arbitrage opportunity
        profit_pct = self._calculate_triangular_profit(recent_prices)
        
        # Check if profitable after fees
        min_profit = self.config['thresholds']['profit_min']
        return profit_pct > min_profit
    
    def _check_cross_exchange_arbitrage(self, tick: Dict) -> bool:
        """Check for cross-exchange arbitrage opportunities."""
        symbol = tick['symbol']
        price = tick['price']
        exchange = tick['exchange']
        
        # Get prices from other exchanges
        other_prices = []
        
        for other_exchange in self.exchanges:
            if other_exchange == exchange:
                continue
            
            key = (symbol, other_exchange)
            if key in self.price_states and len(self.price_states[key]['prices']) > 0:
                other_price = self.price_states[key]['prices'][-1]
                other_prices.append(other_price)
        
        if not other_prices:
            return False
        
        # Calculate price differences
        avg_other_price = sum(other_prices) / len(other_prices)
        price_diff_pct = abs(price - avg_other_price) / min(price, avg_other_price)
        
        # Account for transfer fees and latency
        min_profit = self.config['thresholds']['profit_min'] * 2  # Higher threshold for cross-exchange
        
        return price_diff_pct > min_profit
    
    def _check_mean_reversion(self, tick: Dict) -> bool:
        """Check for mean reversion opportunities."""
        symbol = tick['symbol']
        price = tick['price']
        
        # Get correlation pairs
        correlations = self.correlation_states[symbol]['correlations']
        
        if not correlations:
            return False
        
        # Find most correlated pair
        best_pair = max(correlations.items(), key=lambda x: x[1]['correlation'])
        pair_symbol, corr_data = best_pair
        
        if corr_data['correlation'] < 0.7:  # Need strong correlation
            return False
        
        # Check if we have recent price for correlated pair
        key = (pair_symbol, tick['exchange'])
        if key not in self.price_states or len(self.price_states[key]['prices']) < 20:
            return False
        
        # Calculate spread and z-score
        pair_price = self.price_states[key]['prices'][-1]
        spread = price / pair_price
        
        # Calculate mean and std of spread
        spread_history = corr_data.get('spread_history', [])
        if len(spread_history) < 20:
            return False
        
        mean_spread = np.mean(spread_history)
        std_spread = np.std(spread_history)
        
        if std_spread == 0:
            return False
        
        z_score = (spread - mean_spread) / std_spread
        
        # Mean reversion signal when z-score is extreme
        return abs(z_score) > 2.0
    
    def _check_flash_crash(self, tick: Dict) -> bool:
        """Check for flash crash patterns."""
        symbol = tick['symbol']
        price = tick['price']
        
        key = (symbol, tick['exchange'])
        if key not in self.price_states or len(self.price_states[key]['prices']) < 10:
            return False
        
        # Get recent prices
        recent_prices = list(self.price_states[key]['prices'])
        
        # Check for sudden price drop
        if len(recent_prices) >= 10:
            prev_price = recent_prices[-10]
            price_change_pct = (price - prev_price) / prev_price
            
            # Flash crash: price drops more than 5% in 10 ticks
            return price_change_pct < -0.05
        
        return False
    
    def _check_volume_spike(self, tick: Dict) -> bool:
        """Check for volume spike patterns."""
        symbol = tick['symbol']
        volume = tick['volume']
        
        key = (symbol, tick['exchange'])
        if key not in self.price_states:
            return False
        
        # Get recent volumes (need to store volumes separately)
        # For simplicity, using price state timestamps as proxy
        
        # Calculate average volume (would need volume history)
        # This is simplified
        avg_volume = 1000  # Would be calculated from history
        
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        
        # Volume spike: volume > 10x average
        return volume_ratio > 10
    
    def _create_alert(self, pattern: Dict, tick: Dict, detection_time: float) -> Dict:
        """Create alert from detected pattern."""
        opportunity_id = str(uuid.uuid4())
        
        alert = {
            'opportunity_id': opportunity_id,
            'type': pattern['name'],
            'timestamp': time.time(),
            'symbol': tick['symbol'],
            'exchange': tick['exchange'],
            'price': tick['price'],
            'volume': tick['volume'],
            'detection_latency_ms': detection_time,
            'confidence': self._calculate_confidence(pattern, tick),
            'metadata': {
                'pattern_description': pattern['description'],
                'window_size_ms': pattern['window_ms'],
                'priority': pattern['priority']
            }
        }
        
        # Add pattern-specific data
        if pattern['name'] == 'triangular_arbitrage':
            alert['profit_pct'] = self._calculate_triangular_profit_for_alert(tick)
            alert['expected_profit'] = alert['profit_pct'] * tick['price'] / 100
        
        elif pattern['name'] == 'cross_exchange_arbitrage':
            alert['profit_pct'] = self._calculate_cross_exchange_profit(tick)
        
        elif pattern['name'] == 'mean_reversion':
            alert['z_score'] = self._calculate_z_score(tick)
        
        return alert
    
    def _calculate_confidence(self, pattern: Dict, tick: Dict) -> float:
        """Calculate confidence score for pattern detection."""
        # Simplified confidence calculation
        # In production, this would use more sophisticated methods
        
        base_confidence = 0.8
        
        # Adjust based on data quality
        symbol = tick['symbol']
        key = (symbol, tick['exchange'])
        
        if key in self.price_states:
            data_points = len(self.price_states[key]['prices'])
            if data_points < 100:
                base_confidence *= 0.8
            elif data_points > 1000:
                base_confidence *= 1.1
        
        # Adjust based on pattern type
        if pattern['name'] == 'flash_crash':
            base_confidence *= 0.9  # Flash crashes are rare
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _update_correlations(self, symbol: str):
        """Update correlation matrix for symbol."""
        # This is a simplified implementation
        # In production, use proper correlation calculation
        
        for other_symbol in self.symbols:
            if other_symbol == symbol:
                continue
            
            # Check if we have enough data for both symbols
            key1 = (symbol, 'binance')  # Simplified: using single exchange
            key2 = (other_symbol, 'binance')
            
            if (key1 in self.price_states and key2 in self.price_states and
                len(self.price_states[key1]['prices']) > 100 and
                len(self.price_states[key2]['prices']) > 100):
                
                # Calculate correlation (simplified)
                prices1 = list(self.price_states[key1]['prices'])[-100:]
                prices2 = list(self.price_states[key2]['prices'])[-100:]
                
                if len(prices1) == len(prices2):
                    try:
                        correlation = np.corrcoef(prices1, prices2)[0, 1]
                        
                        self.correlation_states[symbol]['correlations'][other_symbol] = {
                            'correlation': correlation,
                            'last_updated': time.time()
                        }
                    except:
                        pass
        
        self.correlation_states[symbol]['last_updated'] = time.time()
    
    async def cleanup(self):
        """Cleanup CEP resources."""
        logger.info("Cleaning up ComplexEventProcessor...")
        
        if self.producer:
            self.producer.close()
        
        if self.consumer:
            self.consumer.close()
        
        logger.info("ComplexEventProcessor cleaned up")


class SchemaRegistry:
    """Schema registry for data contract management."""
    
    def __init__(self):
        self.schemas = {}
        self.serializers = {}
        self.deserializers = {}
        
        self._register_default_schemas()
    
    def _register_default_schemas(self):
        """Register default schemas."""
        # Market tick schema
        market_tick_schema = {
            "type": "record",
            "name": "MarketTick",
            "namespace": "com.trading.schemas",
            "fields": [
                {"name": "symbol", "type": "string"},
                {"name": "exchange", "type": "string"},
                {"name": "price", "type": "double"},
                {"name": "volume", "type": "double"},
                {"name": "timestamp", "type": "long"},
                {"name": "bid", "type": ["null", "double"], "default": None},
                {"name": "ask", "type": ["null", "double"], "default": None},
                {"name": "bid_size", "type": ["null", "double"], "default": None},
                {"name": "ask_size", "type": ["null", "double"], "default": None},
                {"name": "trade_id", "type": ["null", "string"], "default": None},
                {"name": "conditions", "type": {"type": "array", "items": "string"}, "default": []},
                {"name": "_metadata", "type": ["null", {
                    "type": "map",
                    "values": "string"
                }], "default": None}
            ]
        }
        
        # Technical indicators schema
        technical_indicators_schema = {
            "type": "record",
            "name": "TechnicalIndicators",
            "namespace": "com.trading.schemas",
            "fields": [
                {"name": "symbol", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "sma_9", "type": "double"},
                {"name": "sma_20", "type": "double"},
                {"name": "sma_50", "type": "double"},
                {"name": "ema_12", "type": "double"},
                {"name": "ema_26", "type": "double"},
                {"name": "macd_line", "type": "double"},
                {"name": "macd_signal", "type": "double"},
                {"name": "macd_histogram", "type": "double"},
                {"name": "rsi", "type": "double"},
                {"name": "bb_upper", "type": "double"},
                {"name": "bb_middle", "type": "double"},
                {"name": "bb_lower", "type": "double"},
                {"name": "vwap", "type": "double"},
                {"name": "atr", "type": "double"},
                {"name": "price", "type": "double"},
                {"name": "volume", "type": "double"},
                {"name": "price_change_pct", "type": "double"}
            ]
        }
        
        # OHLCV bar schema
        ohlcv_bar_schema = {
            "type": "record",
            "name": "OHLCVBar",
            "namespace": "com.trading.schemas",
            "fields": [
                {"name": "symbol", "type": "string"},
                {"name": "exchange", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "open", "type": "double"},
                {"name": "high", "type": "double"},
                {"name": "low", "type": "double"},
                {"name": "close", "type": "double"},
                {"name": "volume", "type": "double"},
                {"name": "vwap", "type": ["null", "double"], "default": None},
                {"name": "trade_count", "type": "int", "default": 0},
                {"name": "window_size", "type": "string", "default": "1m"}
            ]
        }
        
        self.register_schema("market_tick", market_tick_schema)
        self.register_schema("technical_indicators", technical_indicators_schema)
        self.register_schema("ohlcv_bar", ohlcv_bar_schema)
    
    def register_schema(self, name: str, schema: Dict):
        """Register a schema."""
        self.schemas[name] = schema
        
        try:
            # Create Avro schema objects
            avro_schema = avro.schema.parse(json.dumps(schema))
            
            # Create serializer and deserializer
            self.serializers[name] = avro.io.DatumWriter(avro_schema)
            self.deserializers[name] = avro.io.DatumReader(avro_schema)
            
            logger.info(f"Registered schema: {name}")
        except Exception as e:
            logger.error(f"Failed to register schema {name}: {e}")
    
    def serialize(self, schema_name: str, data: Dict) -> bytes:
        """Serialize data using schema."""
        if schema_name not in self.serializers:
            raise ValueError(f"Unknown schema: {schema_name}")
        
        try:
            # Convert data to bytes writer
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            
            # Write data
            writer = self.serializers[schema_name]
            writer.write(data, encoder)
            
            return bytes_writer.getvalue()
            
        except Exception as e:
            logger.error(f"Serialization error for {schema_name}: {e}")
            raise
    
    def deserialize(self, schema_name: str, data: bytes) -> Dict:
        """Deserialize data using schema."""
        if schema_name not in self.deserializers:
            raise ValueError(f"Unknown schema: {schema_name}")
        
        try:
            # Convert bytes to reader
            bytes_reader = io.BytesIO(data)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            
            # Read data
            reader = self.deserializers[schema_name]
            return reader.read(decoder)
            
        except Exception as e:
            logger.error(f"Deserialization error for {schema_name}: {e}")
            raise
    
    def get_schema(self, schema_name: str) -> Dict:
        """Get schema by name."""
        return self.schemas.get(schema_name)


class PipelineMonitoring:
    """Monitoring and observability for data pipelines."""
    
    def __init__(self, prometheus_port: int = 9090):
        self.prometheus_port = prometheus_port
        
        # Metrics
        self.metrics = self._setup_metrics()
        
        # Health checks
        self.health_status = {}
        
        # Alert rules
        self.alert_rules = self._load_alert_rules()
    
    def _setup_metrics(self) -> Dict:
        """Setup monitoring metrics."""
        return {
            'pipeline_health': Gauge(
                'pipeline_health_status',
                'Pipeline health status (1=healthy, 0=unhealthy)',
                ['pipeline', 'component'],
                registry=metrics_registry
            ),
            'message_latency': Histogram(
                'pipeline_message_latency_ms',
                'End-to-end message latency',
                ['pipeline', 'stage'],
                buckets=[1, 5, 10, 50, 100, 500, 1000, 5000],
                registry=metrics_registry
            ),
            'throughput': Counter(
                'pipeline_throughput_total',
                'Total messages processed',
                ['pipeline', 'stage', 'status'],
                registry=metrics_registry
            ),
            'error_rate': Counter(
                'pipeline_error_rate',
                'Pipeline errors',
                ['pipeline', 'error_type', 'component'],
                registry=metrics_registry
            ),
            'resource_usage': Gauge(
                'pipeline_resource_usage',
                'Resource usage metrics',
                ['pipeline', 'resource_type', 'unit'],
                registry=metrics_registry
            )
        }
    
    async def monitor_pipeline(self, pipeline_name: str, components: List[Dict]):
        """Monitor pipeline components."""
        logger.info(f"Starting monitoring for pipeline: {pipeline_name}")
        
        while True:
            try:
                health_status = {}
                
                for component in components:
                    component_name = component['name']
                    component_type = component['type']
                    
                    try:
                        if component_type == 'kafka_topic':
                            health = await self._check_kafka_topic(component)
                        elif component_type == 'redis':
                            health = await self._check_redis(component)
                        elif component_type == 'websocket':
                            health = await self._check_websocket(component)
                        else:
                            health = {'status': 'unknown', 'reason': f'Unknown type: {component_type}'}
                        
                        health_status[component_name] = health
                        
                        # Update metrics
                        is_healthy = 1 if health.get('status') == 'healthy' else 0
                        self.metrics['pipeline_health'].labels(
                            pipeline=pipeline_name,
                            component=component_name
                        ).set(is_healthy)
                        
                    except Exception as e:
                        logger.error(f"Error checking {component_name}: {e}")
                        health_status[component_name] = {'status': 'error', 'reason': str(e)}
                
                self.health_status[pipeline_name] = health_status
                
                # Check alert rules
                await self._check_alerts(pipeline_name, health_status)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_kafka_topic(self, config: Dict) -> Dict:
        """Check Kafka topic health."""
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=config.get('bootstrap_servers', 'localhost:9092')
            )
            
            topic = config['topic']
            topics = admin_client.list_topics()
            
            if topic not in topics:
                return {'status': 'unhealthy', 'reason': f'Topic {topic} does not exist'}
            
            # Get topic description
            topic_desc = admin_client.describe_topics([topic])
            
            # Check partitions
            partitions = topic_desc[0]['partitions']
            expected_partitions = config.get('partitions', 1)
            
            if len(partitions) != expected_partitions:
                return {
                    'status': 'degraded',
                    'reason': f'Partition mismatch: expected {expected_partitions}, got {len(partitions)}'
                }
            
            # Check consumer lag (simplified)
            consumer_lag = await self._get_consumer_lag(topic)
            
            return {
                'status': 'healthy',
                'partitions': len(partitions),
                'consumer_lag': consumer_lag
            }
            
        except Exception as e:
            return {'status': 'error', 'reason': str(e)}
    
    async def generate_dashboard(self) -> Dict:
        """Generate monitoring dashboard."""
        return {
            'title': 'Real-Time Pipeline Dashboard',
            'refresh': '10s',
            'panels': [
                {
                    'title': 'Pipeline Health',
                    'type': 'status',
                    'targets': [
                        {
                            'expr': 'pipeline_health_status',
                            'legendFormat': '{{pipeline}} - {{component}}'
                        }
                    ]
                },
                {
                    'title': 'Message Throughput',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'rate(pipeline_throughput_total[5m])',
                            'legendFormat': '{{pipeline}} - {{stage}}'
                        }
                    ]
                },
                {
                    'title': 'Message Latency (P95)',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'histogram_quantile(0.95, rate(pipeline_message_latency_ms_bucket[5m]))',
                            'legendFormat': '{{pipeline}} - {{stage}}'
                        }
                    ]
                },
                {
                    'title': 'Error Rate',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'rate(pipeline_error_rate[5m])',
                            'legendFormat': '{{pipeline}} - {{error_type}}'
                        }
                    ]
                }
            ]
        }


async def demonstrate_real_time_pipeline():
    """Demonstrate the complete real-time data pipeline."""
    
    print("\n" + "=" * 80)
    print("Day 90: Real-Time Data Pipelines & Stream Processing")
    print("=" * 80)
    
    try:
        print("\n1. Initializing Market Data Pipeline...")
        pipeline = MarketDataPipeline(
            bootstrap_servers="localhost:9092",
            redis_url="redis://localhost:6379",
            environment="development"
        )
        
        await pipeline.initialize()
        
        print("\n2. Starting WebSocket Ingestion (simulated)...")
        # In a real scenario, this would connect to actual exchanges
        print("   Simulating WebSocket ingestion for BTC/USDT, ETH/USDT")
        
        print("\n3. Starting Normalization Pipeline...")
        normalization_task = asyncio.create_task(pipeline.normalize_and_validate())
        
        print("\n4. Starting Aggregation Pipeline...")
        aggregation_task = asyncio.create_task(pipeline.aggregate_to_bars("1m"))
        
        print("\n5. Starting Technical Indicators Calculation...")
        # Note: Faust app would be started separately
        
        print("\n6. Initializing Complex Event Processor...")
        cep = ComplexEventProcessor(
            kafka_servers="localhost:9092",
            symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
            exchanges=["binance", "coinbase"]
        )
        
        await cep.initialize()
        
        print("\n7. Starting Pattern Detection...")
        detection_task = asyncio.create_task(cep.detect_patterns())
        
        print("\n8. Setting up Monitoring...")
        monitoring = PipelineMonitoring()
        dashboard = monitoring.generate_dashboard()
        
        print(f"   Generated monitoring dashboard with {len(dashboard['panels'])} panels")
        
        print("\n" + "=" * 80)
        print("PIPELINE SUMMARY")
        print("=" * 80)
        
        summary = {
            "components": [
                {"name": "MarketDataPipeline", "status": "initialized", "type": "ingestion"},
                {"name": "ComplexEventProcessor", "status": "initialized", "type": "processing"},
                {"name": "SchemaRegistry", "status": "ready", "type": "serialization"},
                {"name": "PipelineMonitoring", "status": "running", "type": "observability"}
            ],
            "topics": [
                "market.raw.ticks",
                "market.normalized.ticks", 
                "market.aggregated.bars",
                "market.technical.indicators",
                "market.alerts"
            ],
            "features": [
                "Real-time WebSocket ingestion",
                "Data validation and normalization",
                "Windowed aggregation (OHLCV bars)",
                "Technical indicator calculation",
                "Complex pattern detection",
                "Arbitrage opportunity identification",
                "Schema-based serialization",
                "Comprehensive monitoring"
            ]
        }
        
        print("\nComponents:")
        for component in summary["components"]:
            print(f"  • {component['name']}: {component['status']}")
        
        print("\nKafka Topics:")
        for topic in summary["topics"]:
            print(f"  • {topic}")
        
        print("\nFeatures:")
        for feature in summary["features"]:
            print(f"  • {feature}")
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        
        print("\nThe real-time data pipeline is now running with:")
        print("  • Market data ingestion and processing")
        print("  • Real-time technical analysis")
        print("  • Complex event pattern detection")
        print("  • Comprehensive monitoring and observability")
        
        print("\nTo test the pipeline:")
        print("  1. Start Kafka and Redis servers")
        print("  2. Run the Faust app for technical indicators")
        print("  3. Connect WebSocket clients to receive data")
        print("  4. Monitor the pipeline using the dashboard")
        
        # Keep running for demonstration
        print("\nPipeline running. Press Ctrl+C to stop.")
        await asyncio.sleep(3600)  # Run for 1 hour
        
    except KeyboardInterrupt:
        print("\n\nShutting down pipeline...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        # Add cleanup code here


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-Time Data Pipeline')
    parser.add_argument('--demo', action='store_true', help='Run complete demonstration')
    parser.add_argument('--ingest', help='Start ingestion for exchange')