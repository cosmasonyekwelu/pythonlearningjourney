# **Day 88: Database Optimization for High-Performance Trading**

## 📊 Objective
Design and optimize databases for trading workloads, implementing real-time analytics, time-series data models, and low-latency queries specifically tailored for high-frequency trading systems.

## 🏗️ Architecture Overview

This implementation provides a comprehensive database solution combining:
- **TimescaleDB** for time-series data storage and analytics
- **Redis** for low-latency order book caching and real-time updates
- **Benchmarking tools** for performance optimization
- **Monitoring systems** for production readiness

## 🚀 Key Features

### **TimescaleDB Trading Schema**
- **Hypertables** with automatic time-based partitioning (daily chunks)
- **Continuous aggregates** for real-time OHLCV calculations (1-minute intervals)
- **Compression policies** reducing storage by up to 90% for historical data
- **Retention policies** automated data lifecycle management
- **Generated columns** for calculated metrics (spreads, price changes)
- **Space partitioning** by symbol for parallel query execution

### **Redis Order Book Cache**
- **High-performance caching** for 1M+ active orders with sub-millisecond latency
- **Memory optimization** using msgpack serialization + zlib compression
- **Pub/sub updates** for real-time order book synchronization
- **LRU eviction policies** with configurable memory limits
- **Failover mechanisms** and connection resilience
- **Compression thresholds** intelligent data compression

### **Data Models Implemented**
| Model | Description | Optimization |
|-------|-------------|--------------|
| `market_ticks` | Raw tick-by-tick data | Time + symbol partitioning, compression |
| `ohlcv_bars` | Aggregated OHLCV bars | Continuous aggregates, weekly chunks |
| `order_book_snapshots` | Order book states | JSONB storage, hourly partitioning |
| `trades` | Individual trade records | BRIN indexes, daily partitioning |
| `portfolio_positions` | Portfolio tracking | Audit trails, real-time updates |

## 📈 Performance Benchmarks

### **TimescaleDB Performance**
- **Insert throughput**: 10,000+ ticks/second using COPY command
- **Query latency**: <100ms for 1-day OHLCV data retrieval
- **Compression ratio**: 10:1 for historical data
- **Concurrent connections**: 50+ active connections with pooling

### **Redis Cache Performance**
- **Order insertion**: 1,000+ orders/second with pipelining
- **Order book retrieval**: <5ms latency for depth=10
- **Memory efficiency**: 70%+ reduction with compression
- **Cache hit rate**: 95%+ for frequent queries

## 🔧 Installation & Setup

### **Prerequisites**
```bash
# Install Python dependencies
pip install asyncpg redis msgpack numpy psutil

# Install TimescaleDB (PostgreSQL extension)
# Follow: https://docs.timescale.com/install/latest/

# Install Redis
# Follow: https://redis.io/docs/getting-started/installation/
```

### **Configuration**
```python
# Database configuration
timescale_params = {
    'user': 'trading_user',
    'password': 'trading_password',
    'database': 'trading_db',
    'host': 'localhost',
    'port': 5432,
    'min_size': 10,     # Connection pool minimum
    'max_size': 50      # Connection pool maximum
}

redis_params = {
    'host': 'localhost',
    'port': 6379,
    'password': None,
    'db': 0,
    'max_connections': 100
}
```

## 💻 Usage Examples

### **1. Initialize the Trading Database System**
```python
from day_88 import HighFrequencyTradingDatabase

# Create database system
hft_db = HighFrequencyTradingDatabase(timescale_params, redis_params)

# Initialize connections and schema
await hft_db.initialize()
```

### **2. Ingest Market Tick Data**
```python
# Generate sample ticks
ticks = [
    {
        'symbol': 'AAPL',
        'exchange': 'NASDAQ',
        'timestamp': datetime.utcnow(),
        'bid_price': 150.25,
        'ask_price': 150.26,
        'last_price': 150.255,
        'volume': 1000,
        # ... other fields
    }
]

# High-performance batch ingestion
await hft_db.timescale_db.ingest_market_ticks(ticks)
```

### **3. Query OHLCV Data**
```python
# Get 1-minute OHLCV bars
ohlcv_data = await hft_db.timescale_db.get_ohlcv_data(
    symbol='AAPL',
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow(),
    interval='1min'
)

# Get real-time metrics with window functions
metrics = await hft_db.timescale_db.get_real_time_metrics('AAPL', lookback_minutes=5)
```

### **4. Manage Order Book Cache**
```python
# Get Redis cache for a symbol
cache = hft_db.get_redis_cache('AAPL')
await cache.connect()
await cache.initialize_order_book()

# Add orders to cache
await cache.add_order('order_123', {
    'symbol': 'AAPL',
    'side': 'bid',
    'price': 150.25,
    'quantity': 100,
    'timestamp': time.time()
})

# Get current order book
order_book = await cache.get_order_book(depth=10)

# Subscribe to real-time updates
async def handle_update(update):
    print(f"Order update: {update}")

await cache.subscribe_order_updates(handle_update)
```

### **5. Run Performance Benchmarks**
```python
# Run comprehensive benchmarks
report = await hft_db.run_benchmarks()
print(report)

# Monitor system performance
monitor_task = asyncio.create_task(hft_db.monitor_performance(interval_seconds=60))

# Analyze and optimize queries
optimizations = await hft_db.optimize_queries()
```

## 🛠️ Optimization Techniques

### **Indexing Strategies**
```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_market_ticks_symbol_timestamp ON market_ticks (symbol, timestamp DESC);
CREATE INDEX idx_ohlcv_symbol_bucket ON ohlcv_bars (symbol, time_bucket DESC);

-- BRIN indexes for time-series data
CREATE INDEX idx_market_ticks_time_brin ON market_ticks USING BRIN (timestamp);

-- Partial indexes for filtered queries
CREATE INDEX idx_trades_aggressive ON trades (symbol, timestamp DESC) 
WHERE is_aggressive = TRUE;

-- GIN indexes for JSONB queries
CREATE INDEX idx_orderbook_bids_gin ON order_book_snapshots USING GIN (bids);
```

### **Compression Configuration**
```sql
-- Compress data older than 1 day
ALTER TABLE market_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, exchange',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Compression policy
SELECT add_compression_policy('market_ticks', 
    compress_after => INTERVAL '1 day');
```

### **Retention Policies**
```sql
-- Automated data lifecycle management
SELECT add_retention_policy('market_ticks', drop_after => INTERVAL '30 days');
SELECT add_retention_policy('ohlcv_bars', drop_after => INTERVAL '365 days');
SELECT add_retention_policy('order_book_snapshots', drop_after => INTERVAL '7 days');
```

## 📊 Benchmark Results

After running the included benchmarks, you'll get:

### **Sample Output:**
```
========================================
DATABASE OPTIMIZATION BENCHMARK REPORT
========================================

TIMESCALEDB Results:
----------------------------------------

Insert 10000 Ticks:
  time_seconds: 0.85
  throughput_per_second: 11764.71

Query Ohlcv 1day:
  time_seconds: 0.12
  rows_returned: 390
  throughput_rows_per_second: 3250.00

REDIS CACHE Results:
----------------------------------------

Insert 1000 Orders:
  time_seconds: 0.45
  throughput_orders_per_second: 2222.22

Retrieve 100 Orderbooks:
  time_seconds: 0.32
  throughput_per_second: 312.50
  avg_latency_ms: 3.20
```

## 🔍 Monitoring & Maintenance

### **Performance Monitoring**
```python
# Continuous monitoring
await hft_db.monitor_performance(interval_seconds=60)

# Output:
# TimescaleDB - Active connections: 12, Cache hit: 99.1%
# Redis (AAPL) - Memory: 245.3MB, Hit rate: 97.5%, Orders: 1250
```

### **Query Optimization**
```python
# Analyze slow queries
optimizations = await hft_db.optimize_queries()

# Generates: query_optimization_report.txt with:
# - Slow queries identified
# - Execution time analysis
# - Indexing recommendations
# - Query rewriting suggestions
```

## 🚨 Production Considerations

### **High Availability Setup**
```python
# Redis failover configuration
redis_params = {
    'host': 'redis-cluster.example.com',
    'sentinel': True,
    'sentinels': [('sentinel1', 26379), ('sentinel2', 26379)],
    'service_name': 'mymaster'
}

# PostgreSQL/TimescaleDB replication
# Configure streaming replication in postgresql.conf:
# wal_level = replica
# max_wal_senders = 10
# hot_standby = on
```

### **Security Best Practices**
```sql
-- Database security
CREATE ROLE trading_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE trading_db TO trading_user;
GRANT USAGE ON SCHEMA public TO trading_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO trading_user;

-- Row-level security
ALTER TABLE portfolio_positions ENABLE ROW LEVEL SECURITY;
CREATE POLICY portfolio_policy ON portfolio_positions
    USING (portfolio_id = current_user);
```

### **Backup Strategy**
```bash
# TimescaleDB backup with WAL archiving
pg_basebackup -D /backup/trading_db -Ft -z -P

# Redis backup
redis-cli SAVE  # RDB snapshot
# or
redis-cli BGSAVE  # Background save

# Automated backup script included
```

## 📁 Generated Files

Running the demonstration generates:

1. **`database_benchmark_report.txt`** - Comprehensive performance analysis
2. **`query_optimization_report.txt`** - SQL optimization recommendations
3. **Schema initialization scripts** - Ready for production deployment
4. **Configuration templates** - For different environments

## 🎯 Use Cases

### **High-Frequency Trading**
- **Tick data ingestion**: 10K+ ticks/second with TimescaleDB COPY
- **Order book management**: Sub-millisecond Redis cache updates
- **Real-time analytics**: Window functions for rolling calculations
- **Portfolio tracking**: Complete audit trails and P&L calculations

### **Quantitative Analysis**
- **Market regime detection**: Statistical clustering on historical data
- **Risk management**: VAR and expected shortfall calculations
- **Performance attribution**: Position-level contribution analysis
- **Backtesting**: Fast historical data retrieval

### **Risk Management**
- **Real-time monitoring**: Continuous portfolio risk metrics
- **Position limits**: Automated constraint checking
- **Market impact analysis**: Order book depth and liquidity metrics
- **Stress testing**: Historical scenario analysis

## 🔄 Integration Examples

### **With Trading System**
```python
class TradingSystem:
    def __init__(self, hft_db):
        self.db = hft_db
        self.order_cache = {}
        
    async def process_tick(self, tick):
        # Store tick data
        await self.db.timescale_db.ingest_market_ticks([tick])
        
        # Update order book cache
        cache = self.db.get_redis_cache(tick['symbol'])
        # ... update logic
        
    async def execute_order(self, order):
        # Record trade
        await self.db.timescale_db.record_trade(order)
        
        # Update portfolio
        await self.db.timescale_db.update_portfolio_position(order)
        
        # Clear order from cache
        cache = self.db.get_redis_cache(order['symbol'])
        await cache.remove_order(order['order_id'])
```

### **With Monitoring Dashboard**
```python
async def generate_dashboard_metrics():
    # Real-time metrics
    metrics = await timescale_db.get_real_time_metrics('AAPL', 5)
    
    # Portfolio performance
    portfolio = await timescale_db.portfolio_performance_analysis('main_portfolio')
    
    # Market regime
    regime = await timescale_db.analyze_market_regimes(
        'AAPL', 
        datetime.utcnow() - timedelta(days=30),
        datetime.utcnow()
    )
    
    return {
        'metrics': metrics,
        'portfolio': portfolio,
        'regime': regime[-1] if regime else None
    }
```

## 🚀 Getting Started

### **Quick Start**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start TimescaleDB and Redis
docker-compose up -d  # See docker-compose.yml example

# 3. Run the demonstration
python day_88.py

# 4. Explore the generated reports
cat database_benchmark_report.txt
cat query_optimization_report.txt
```

### **Docker Compose Example**
```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: trading_db
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: trading_password
    ports:
      - "5432:5432"
    volumes:
      - timescale-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

volumes:
  timescale-data:
  redis-data:
```

## 📚 Learning Resources

### **TimescaleDB Documentation**
- [Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/)
- [Continuous Aggregates](https://docs.timescale.com/use-timescale/latest/continuous-aggregates/)
- [Compression](https://docs.timescale.com/use-timescale/latest/compression/)
- [Data Retention](https://docs.timescale.com/use-timescale/latest/data-retention/)

### **Redis Best Practices**
- [Memory Optimization](https://redis.io/topics/memory-optimization)
- [Pipelining](https://redis.io/topics/pipelining)
- [Pub/Sub](https://redis.io/topics/pubsub)
- [Persistence](https://redis.io/topics/persistence)

### **Trading Database Patterns**
- [Time-Series Data Modeling](https://www.timescale.com/learn/time-series-data-modeling)
- [Financial Tick Data](https://www.quantstart.com/articles/storing-high-frequency-tick-data-in-a-database/)
- [Order Book Implementation](https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/)

## 🤝 Contributing

This implementation is designed to be extensible. Key extension points:

1. **Add new database types** (ClickHouse, QuestDB, etc.)
2. **Implement additional caching strategies** (LRU, LFU, ARC)
3. **Add more analytics functions** (technical indicators, statistical tests)
4. **Integrate with message queues** (Kafka, RabbitMQ for data streaming)
5. **Add authentication and authorization layers**

## 📄 License

This implementation is provided for educational purposes as part of the "100 Days of Trading Systems" series. Use in production requires proper testing and customization.

## 🆘 Troubleshooting

### **Common Issues**

1. **TimescaleDB connection errors**
   - Check PostgreSQL is running: `pg_isready`
   - Verify extension is enabled: `CREATE EXTENSION IF NOT EXISTS timescaledb;`

2. **Redis memory issues**
   - Monitor memory: `redis-cli info memory`
   - Adjust maxmemory policy: `CONFIG SET maxmemory-policy allkeys-lru`
   - Enable compression in RedisOrderBookCache

3. **Performance bottlenecks**
   - Check indexes: `EXPLAIN ANALYZE your_query;`
   - Monitor connection pool usage
   - Adjust chunk intervals for hypertables

### **Performance Tuning**
```sql
-- TimescaleDB tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Redis tuning
CONFIG SET maxmemory 4gb
CONFIG SET maxmemory-policy allkeys-lru
CONFIG SET hash-max-ziplist-entries 512
```

---

