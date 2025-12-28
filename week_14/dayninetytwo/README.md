# Day 92: Monitoring & Alerting with Grafana and Prometheus

## 📊 Project Overview

Implement comprehensive monitoring and alerting for trading systems using industry-standard tools to detect issues before they impact trading performance. This day focuses on building a robust monitoring infrastructure that provides real-time visibility into system health, trading performance, and risk metrics.

## 🎯 Objective

Set up a complete Prometheus/Grafana stack with custom exporters for trading metrics, create comprehensive dashboards, and configure alerting for critical conditions.

## 🏗️ Architecture

```
monitoring-system/
├── prometheus/                 # Prometheus configuration
│   ├── prometheus.yml         # Main configuration
│   ├── recording_rules.yml    # Custom recording rules
│   ├── alert_rules.yml        # Alerting rules
│   └── targets/              # Service discovery targets
├── grafana/                   # Grafana configuration
│   ├── dashboards/           # Dashboard definitions
│   │   ├── trading_overview.json
│   │   ├── system_health.json
│   │   ├── performance_metrics.json
│   │   └── risk_monitoring.json
│   ├── datasources/          # Data source configurations
│   └── provisioning/         # Provisioning configs
├── exporters/                # Custom metric exporters
│   ├── trading_exporter.py   # Trading-specific metrics
│   ├── market_data_exporter.py
│   └── risk_metrics_exporter.py
├── alertmanager/            # Alert manager configuration
│   ├── alertmanager.yml
│   ├── templates/          # Alert templates
│   └── receivers/          # Notification receivers
├── docker-compose.yml      # Local development stack
└── scripts/               # Deployment and maintenance scripts
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Basic understanding of Prometheus and Grafana

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd monitoring-system

# Start the monitoring stack
docker-compose up -d

# Access the services:
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# AlertManager: http://localhost:9093

# Install Python dependencies for custom exporters
pip install -r requirements.txt
```

## 🔧 Configuration

### Prometheus Configuration (prometheus/prometheus.yml)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alert_rules.yml"
  - "recording_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'trading-services'
    static_configs:
      - targets:
        - 'market-data-service:8000'
        - 'order-execution-service:8001'
        - 'risk-service:8002'
        - 'signal-service:8003'

  - job_name: 'trading-exporter'
    static_configs:
      - targets: ['trading-exporter:9100']
      params:
        collect[]:
          - trading_metrics
          - risk_metrics
          - performance_metrics

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

## 📊 Custom Trading Exporter

### Python Trading Metrics Exporter (exporters/trading_exporter.py)

```python
#!/usr/bin/env python3
"""
Trading-specific Prometheus metrics exporter.
Collects trading performance, risk metrics, and system health indicators.
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary
import psutil
import time
import json
from datetime import datetime
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingMetricsExporter:
    """Exports trading-specific metrics to Prometheus."""
    
    def __init__(self, port: int = 9100):
        self.port = port
        
        # Initialize metrics
        self._init_metrics()
        
    def _init_metrics(self):
        """Initialize all Prometheus metrics."""
        
        # Trading Performance Metrics
        self.total_pnl = Gauge(
            'trading_total_pnl',
            'Total profit and loss in base currency',
            ['strategy', 'symbol']
        )
        
        self.daily_pnl = Gauge(
            'trading_daily_pnl',
            'Daily profit and loss',
            ['strategy', 'symbol', 'date']
        )
        
        self.open_positions = Gauge(
            'trading_open_positions',
            'Number of open positions',
            ['strategy', 'symbol']
        )
        
        self.position_value = Gauge(
            'trading_position_value',
            'Current position value',
            ['strategy', 'symbol', 'side']
        )
        
        # Order Metrics
        self.orders_total = Counter(
            'trading_orders_total',
            'Total number of orders placed',
            ['strategy', 'order_type', 'status']
        )
        
        self.order_execution_latency = Histogram(
            'trading_order_execution_latency_seconds',
            'Order execution latency in seconds',
            ['strategy', 'order_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )
        
        # Risk Metrics
        self.var_95 = Gauge(
            'trading_var_95',
            'Value at Risk at 95% confidence',
            ['strategy', 'timeframe']
        )
        
        self.max_drawdown = Gauge(
            'trading_max_drawdown_percent',
            'Maximum drawdown percentage',
            ['strategy']
        )
        
        self.exposure_ratio = Gauge(
            'trading_exposure_ratio',
            'Current exposure as percentage of capital',
            ['strategy']
        )
        
        # Market Data Metrics
        self.market_data_latency = Histogram(
            'trading_market_data_latency_ms',
            'Market data latency in milliseconds',
            ['data_source', 'symbol'],
            buckets=[1, 5, 10, 50, 100, 500, 1000]
        )
        
        self.quote_updates = Counter(
            'trading_quote_updates_total',
            'Total number of quote updates received',
            ['symbol', 'data_source']
        )
        
        # System Health Metrics
        self.service_health = Gauge(
            'trading_service_health',
            'Health status of trading services (1=healthy, 0=unhealthy)',
            ['service_name', 'instance']
        )
        
        self.queue_depth = Gauge(
            'trading_queue_depth',
            'Depth of internal message queues',
            ['queue_name', 'service']
        )
        
        self.process_memory_mb = Gauge(
            'trading_process_memory_mb',
            'Memory usage of trading processes in MB',
            ['process_name', 'service']
        )
        
    async def collect_trading_metrics(self):
        """Collect trading-specific metrics from various sources."""
        try:
            # Simulate collecting metrics from trading services
            # In production, this would connect to actual trading services
            await self._collect_from_market_data_service()
            await self._collect_from_order_service()
            await self._collect_from_risk_service()
            await self._collect_system_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            
    async def _collect_from_market_data_service(self):
        """Collect metrics from market data service."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://market-data-service:8000/metrics') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update market data metrics
                        for symbol, metrics in data.get('market_data', {}).items():
                            latency = metrics.get('latency_ms', 0)
                            self.market_data_latency.labels(
                                data_source=metrics.get('source', 'unknown'),
                                symbol=symbol
                            ).observe(latency)
                            
                            updates = metrics.get('updates_today', 0)
                            self.quote_updates.labels(
                                symbol=symbol,
                                data_source=metrics.get('source', 'unknown')
                            ).inc(updates)
                            
            except Exception as e:
                logger.warning(f"Could not connect to market data service: {e}")
                self.service_health.labels(
                    service_name='market_data_service',
                    instance='default'
                ).set(0)
    
    async def _collect_from_order_service(self):
        """Collect metrics from order execution service."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://order-execution-service:8001/metrics') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update order metrics
                        self.open_positions.labels(
                            strategy=data.get('strategy', 'default'),
                            symbol='ALL'
                        ).set(data.get('open_positions', 0))
                        
                        for order in data.get('recent_orders', []):
                            self.orders_total.labels(
                                strategy=order.get('strategy', 'default'),
                                order_type=order.get('type', 'market'),
                                status=order.get('status', 'unknown')
                            ).inc()
                            
            except Exception as e:
                logger.warning(f"Could not connect to order service: {e}")
                self.service_health.labels(
                    service_name='order_execution_service',
                    instance='default'
                ).set(0)
    
    async def _collect_from_risk_service(self):
        """Collect metrics from risk management service."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://risk-service:8002/metrics') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update risk metrics
                        for strategy, metrics in data.get('strategies', {}).items():
                            self.var_95.labels(
                                strategy=strategy,
                                timeframe='1d'
                            ).set(metrics.get('var_95', 0))
                            
                            self.max_drawdown.labels(
                                strategy=strategy
                            ).set(metrics.get('max_drawdown_pct', 0))
                            
                            self.exposure_ratio.labels(
                                strategy=strategy
                            ).set(metrics.get('exposure_ratio', 0))
                            
            except Exception as e:
                logger.warning(f"Could not connect to risk service: {e}")
                self.service_health.labels(
                    service_name='risk_service',
                    instance='default'
                ).set(0)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # Update process memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        self.process_memory_mb.labels(
            process_name='trading_exporter',
            service='monitoring'
        ).set(memory_mb)
        
        # Update queue depths (simulated)
        self.queue_depth.labels(
            queue_name='market_data',
            service='trading_exporter'
        ).set(100)  # Simulated value
        
    def run(self):
        """Start the metrics exporter server."""
        logger.info(f"Starting trading metrics exporter on port {self.port}")
        start_http_server(self.port)
        
        # Start async metric collection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            loop.run_until_complete(self.collect_trading_metrics())
            time.sleep(15)  # Collect every 15 seconds

if __name__ == "__main__":
    exporter = TradingMetricsExporter(port=9100)
    exporter.run()
```

## 📈 Alert Rules Configuration

### Alerting Rules (prometheus/alert_rules.yml)

```yaml
groups:
  - name: trading_alerts
    rules:
      # System Health Alerts
      - alert: TradingServiceDown
        expr: up{job="trading-services"} == 0
        for: 1m
        labels:
          severity: critical
          service: trading
        annotations:
          summary: "Trading service {{ $labels.instance }} is down"
          description: "The trading service {{ $labels.instance }} has been down for more than 1 minute."
          
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes{job="trading-services"} > 1.5e9
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High memory usage in {{ $labels.instance }}"
          description: "Service {{ $labels.instance }} is using {{ $value | humanize }} bytes of memory."
          
      # Trading Performance Alerts
      - alert: ExcessiveDrawdown
        expr: trading_max_drawdown_percent{strategy=~".*"} > 10
        for: 5m
        labels:
          severity: critical
          service: trading
        annotations:
          summary: "Excessive drawdown in {{ $labels.strategy }}"
          description: "Strategy {{ $labels.strategy }} has exceeded 10% drawdown. Current: {{ $value }}%"
          
      - alert: DailyLossLimitBreached
        expr: trading_daily_pnl{strategy=~".*"} < -5000
        for: 0m
        labels:
          severity: critical
          service: risk
        annotations:
          summary: "Daily loss limit breached for {{ $labels.strategy }}"
          description: "Strategy {{ $labels.strategy }} has lost {{ $value | abs }} today."
          
      # Risk Monitoring Alerts
      - alert: VaRLimitExceeded
        expr: trading_var_95{timeframe="1d"} > 10000
        for: 5m
        labels:
          severity: warning
          service: risk
        annotations:
          summary: "VaR limit exceeded"
          description: "1-day VaR has exceeded $10,000. Current: ${{ $value }}"
          
      - alert: HighExposure
        expr: trading_exposure_ratio{strategy=~".*"} > 0.8
        for: 2m
        labels:
          severity: warning
          service: risk
        annotations:
          summary: "High exposure in {{ $labels.strategy }}"
          description: "Strategy {{ $labels.strategy }} has {{ $value | humanizePercentage }} exposure."
          
      # Market Data Alerts
      - alert: MarketDataLatencyHigh
        expr: trading_market_data_latency_ms{quantile="0.95"} > 100
        for: 2m
        labels:
          severity: warning
          service: market_data
        annotations:
          summary: "High market data latency for {{ $labels.symbol }}"
          description: "95th percentile latency for {{ $labels.symbol }} is {{ $value }}ms"
          
      - alert: MarketDataFeedStale
        expr: time() - trading_market_data_last_update{data_source=~".*"} > 60
        for: 1m
        labels:
          severity: critical
          service: market_data
        annotations:
          summary: "Market data feed {{ $labels.data_source }} is stale"
          description: "No updates from {{ $labels.data_source }} for {{ $value }} seconds"
          
      # Order Execution Alerts
      - alert: OrderExecutionSlow
        expr: trading_order_execution_latency_seconds{quantile="0.95"} > 1
        for: 5m
        labels:
          severity: warning
          service: order_execution
        annotations:
          summary: "Slow order execution"
          description: "95th percentile order execution latency is {{ $value }} seconds"
          
      - alert: HighOrderRejectionRate
        expr: rate(trading_orders_total{status="rejected"}[5m]) / rate(trading_orders_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          service: order_execution
        annotations:
          summary: "High order rejection rate"
          description: "More than 10% of orders are being rejected"
          
  - name: predictive_alerts
    rules:
      # Predictive alerting using recording rules
      - alert: PotentialPositionSizingIssue
        expr: |
          (
            rate(trading_orders_total[1h])
            / avg_over_time(trading_open_positions[1h])
          ) > 10
        for: 30m
        labels:
          severity: warning
          service: trading
        annotations:
          summary: "Potential position sizing issue"
          description: "High order churn relative to open positions detected"
          
      - alert: PerformanceDegradationTrend
        expr: |
          (
            avg_over_time(trading_daily_pnl[7d])
            / stddev_over_time(trading_daily_pnl[7d])
          ) < 0.5
        for: 1d
        labels:
          severity: warning
          service: performance
        annotations:
          summary: "Performance degradation trend detected"
          description: "Signal-to-noise ratio of daily PnL has fallen below 0.5"
```

## 📊 Grafana Dashboard Examples

### Trading Overview Dashboard (grafana/dashboards/trading_overview.json)

```json
{
  "dashboard": {
    "title": "Trading System Overview",
    "tags": ["trading", "overview", "production"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Total P&L by Strategy",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(trading_total_pnl) by (strategy)",
            "legendFormat": "{{strategy}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "green", "value": 0}
              ]
            }
          }
        }
      },
      {
        "title": "Open Positions",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(trading_open_positions)",
            "instant": true
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 80}
              ]
            }
          }
        }
      },
      {
        "title": "Daily P&L Trend",
        "type": "timeseries",
        "targets": [
          {
            "expr": "trading_daily_pnl",
            "legendFormat": "{{strategy}} - {{symbol}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "fillOpacity": 10,
              "lineWidth": 2
            }
          }
        }
      },
      {
        "title": "Risk Metrics",
        "type": "table",
        "targets": [
          {
            "expr": "trading_var_95",
            "instant": true,
            "format": "table"
          },
          {
            "expr": "trading_max_drawdown_percent",
            "instant": true,
            "format": "table"
          },
          {
            "expr": "trading_exposure_ratio",
            "instant": true,
            "format": "table"
          }
        ]
      },
      {
        "title": "Order Execution Latency",
        "type": "histogram",
        "targets": [
          {
            "expr": "rate(trading_order_execution_latency_seconds_bucket[5m])",
            "legendFormat": "{{strategy}}"
          }
        ]
      },
      {
        "title": "Market Data Latency",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(trading_market_data_latency_ms_bucket[5m])",
            "legendFormat": "{{symbol}}"
          }
        ]
      },
      {
        "title": "System Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "trading_service_health",
            "instant": true
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [
              {
                "type": "value",
                "options": {
                  "1": {"text": "Healthy", "color": "green"},
                  "0": {"text": "Unhealthy", "color": "red"}
                }
              }
            ]
          }
        }
      }
    ],
    "refresh": "10s",
    "time": {
      "from": "now-6h",
      "to": "now"
    }
  }
}
```

## 🚨 AlertManager Configuration

### AlertManager Configuration (alertmanager/alertmanager.yml)

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@trading-system.com'
  smtp_auth_username: 'alerts@trading-system.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'trading-team'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 10s
      repeat_interval: 30m
    - match:
        service: market_data
      receiver: 'market-data-team'
    - match:
        service: risk
      receiver: 'risk-team'

receivers:
  - name: 'trading-team'
    email_configs:
      - to: 'trading-team@company.com'
        headers:
          subject: '[Trading Alert] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#trading-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}\n{{ .CommonAnnotations.description }}'
        
  - name: 'critical-alerts'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'
        description: '{{ .CommonAnnotations.summary }}'
        details:
          alertname: '{{ .GroupLabels.alertname }}'
          severity: '{{ .GroupLabels.severity }}'
    phone_configs:
      - to: '+15551234567'
        text: 'CRITICAL: {{ .CommonAnnotations.summary }}'
        
  - name: 'market-data-team'
    email_configs:
      - to: 'market-data@company.com'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#market-data-alerts'
        
  - name: 'risk-team'
    email_configs:
      - to: 'risk-team@company.com'
    webhook_configs:
      - url: 'http://risk-service:8002/api/alerts'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'service']
```

## 🐳 Docker Compose Configuration

### Full Monitoring Stack (docker-compose.yml)

```yaml
version: '3.8'

services:
  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - ./prometheus/recording_rules.yml:/etc/prometheus/recording_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  # AlertManager - Alert handling
  alertmanager:
    image: prom/alertmanager:v0.25.0
    container_name: alertmanager
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    ports:
      - "3000:3000"
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus

  # Node Exporter - System metrics
  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: node-exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped

  # cAdvisor - Container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.0
    container_name: cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring
    restart: unless-stopped

  # Custom Trading Exporter
  trading-exporter:
    build:
      context: ./exporters
      dockerfile: Dockerfile
    container_name: trading-exporter
    volumes:
      - ./exporters:/app
    ports:
      - "9101:9100"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    networks:
      - monitoring
    restart: unless-stopped

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:
```

## 📈 Prometheus Recording Rules

### Advanced Recording Rules (prometheus/recording_rules.yml)

```yaml
groups:
  - name: trading_recording_rules
    interval: 60s
    rules:
      # Rolling window calculations
      - record: trading:rolling_sharpe_ratio_30d
        expr: |
          avg_over_time(trading_daily_pnl[30d])
          /
          stddev_over_time(trading_daily_pnl[30d])
          *
          sqrt(252)
          
      - record: trading:win_rate_7d
        expr: |
          count_over_time(trading_daily_pnl > 0[7d])
          /
          count_over_time(trading_daily_pnl[7d])
          
      # Anomaly detection metrics
      - record: trading:anomaly_score
        expr: |
          (
            abs(
              trading_daily_pnl
              -
              avg_over_time(trading_daily_pnl[30d])
            )
            /
            stddev_over_time(trading_daily_pnl[30d])
          ) > 3
            
      # Performance degradation detection
      - record: trading:performance_trend
        expr: |
          predict_linear(trading_total_pnl[7d], 86400 * 7) < 0
          
      # Capacity planning metrics
      - record: trading:order_rate_per_hour
        expr: |
          rate(trading_orders_total[1h])
          
      - record: trading:position_turnover
        expr: |
          rate(trading_orders_total[1h])
          /
          avg_over_time(trading_open_positions[1h])
```

## 🧪 Testing the Monitoring System

### Test Script (scripts/test_monitoring.py)

```python
#!/usr/bin/env python3
"""
Test script for the monitoring system.
Generates test metrics and triggers alerts for verification.
"""

import requests
import time
import random
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringTester:
    def __init__(self, prometheus_url="http://localhost:9090", grafana_url="http://localhost:3000"):
        self.prometheus_url = prometheus_url
        self.grafana_url = grafana_url
        
    def test_prometheus_connectivity(self):
        """Test connection to Prometheus."""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query?query=up")
            if response.status_code == 200:
                logger.info("Prometheus is reachable")
                return True
            else:
                logger.error(f"Prometheus returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
            return False
            
    def test_grafana_connectivity(self):
        """Test connection to Grafana."""
        try:
            response = requests.get(f"{self.grafana_url}/api/health")
            if response.status_code == 200:
                logger.info("Grafana is reachable")
                return True
            else:
                logger.error(f"Grafana returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Grafana: {e}")
            return False
            
    def generate_test_metrics(self):
        """Generate test metrics to verify the monitoring system."""
        test_metrics = [
            {
                "name": "test_trading_pnl",
                "value": random.uniform(-1000, 1000),
                "labels": {"strategy": "test_strategy", "symbol": "TEST"}
            },
            {
                "name": "test_market_data_latency",
                "value": random.uniform(1, 100),
                "labels": {"symbol": "TEST", "data_source": "test_feed"}
            },
            {
                "name": "test_order_execution_latency",
                "value": random.uniform(0.001, 2.0),
                "labels": {"strategy": "test_strategy", "order_type": "market"}
            }
        ]
        
        # In a real implementation, these would be pushed to the metrics endpoint
        logger.info("Test metrics generated (simulated)")
        return test_metrics
        
    def trigger_test_alert(self, alert_name="TestAlert"):
        """Trigger a test alert to verify the alerting pipeline."""
        # This is a simulation - in production, you would trigger actual conditions
        logger.info(f"Simulating alert trigger: {alert_name}")
        
        # Query Prometheus for active alerts to verify alert rules are working
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": "ALERTS{alertstate='firing'}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('data', {}).get('result', [])
                logger.info(f"Active alerts: {len(alerts)}")
                
                for alert in alerts:
                    logger.info(f"  - {alert['metric']['alertname']}: {alert['metric'].get('severity', 'unknown')}")
                    
        except Exception as e:
            logger.error(f"Failed to query alerts: {e}")
            
    def run_comprehensive_test(self):
        """Run all tests and generate a report."""
        logger.info("Starting comprehensive monitoring system test...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test connectivity
        results["tests"]["prometheus_connectivity"] = self.test_prometheus_connectivity()
        results["tests"]["grafana_connectivity"] = self.test_grafana_connectivity()
        
        # Generate test metrics
        results["tests"]["metrics_generation"] = bool(self.generate_test_metrics())
        
        # Test alerting
        self.trigger_test_alert()
        
        # Verify dashboard availability
        try:
            response = requests.get(f"{self.grafana_url}/api/search")
            if response.status_code == 200:
                dashboards = response.json()
                results["tests"]["dashboards_available"] = len(dashboards) > 0
                logger.info(f"Found {len(dashboards)} dashboards in Grafana")
            else:
                results["tests"]["dashboards_available"] = False
        except Exception as e:
            logger.error(f"Failed to query dashboards: {e}")
            results["tests"]["dashboards_available"] = False
            
        # Generate report
        passed_tests = sum(1 for test in results["tests"].values() if test)
        total_tests = len(results["tests"])
        
        logger.info(f"\nTest Summary: {passed_tests}/{total_tests} tests passed")
        
        for test_name, result in results["tests"].items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"  {status} - {test_name}")
            
        return results

if __name__ == "__main__":
    tester = MonitoringTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open("monitoring_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    logger.info("Test results saved to monitoring_test_results.json")
```

## 📋 Deployment Guide

### Step-by-Step Deployment

1. **Clone and setup the monitoring system:**
```bash
git clone <repository-url>
cd monitoring-system
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Build and start the monitoring stack:**
```bash
docker-compose up -d --build
```

4. **Verify services are running:**
```bash
docker-compose ps
```

5. **Access the dashboards:**
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093

6. **Import pre-built dashboards in Grafana:**
- Navigate to Dashboards → Import
- Use the JSON files from `grafana/dashboards/`

7. **Configure alert notifications:**
- Edit `alertmanager/alertmanager.yml` with your notification channels
- Set up Slack, email, or PagerDuty integrations

### Production Considerations

1. **Security:**
```bash
# Set secure passwords
docker-compose run --rm grafana grafana-cli admin reset-admin-password <new_password>
```

2. **Data Persistence:**
```yaml
# In docker-compose.yml, ensure volumes are mounted
volumes:
  prometheus_data:
    driver: local
    driver_opts:
      type: 'nfs'
      o: 'addr=nfs-server.example.com,rw'
      device: ':/path/to/prometheus-data'
```

3. **High Availability:**
- Deploy Prometheus in HA mode with Thanos or Cortex
- Use clustered Grafana with external database
- Configure AlertManager clustering

## 🎯 Challenge: Predictive Alerting Implementation

### Task: Implement Anomaly Detection for Trading Patterns

Create a predictive alerting system that detects anomalies in trading patterns before they become critical issues:

```python
# predictive_alerting.py
import numpy as np
from sklearn.ensemble import IsolationForest
from prometheus_client import push_to_gateway
import pandas as pd
from datetime import datetime, timedelta

class PredictiveAlertingSystem:
    def __init__(self, prometheus_url="http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
    def fetch_historical_metrics(self, metric_name, hours=24):
        """Fetch historical metrics from Prometheus."""
        query = f'avg_over_time({metric_name}[{hours}h])'
        # Implement Prometheus query logic
        pass
        
    def detect_anomalies(self, metrics_data):
        """Use machine learning to detect anomalies."""
        # Transform data for anomaly detection
        features = self._extract_features(metrics_data)
        
        # Fit and predict anomalies
        self.anomaly_detector.fit(features)
        predictions = self.anomaly_detector.predict(features)
        
        return predictions == -1  # -1 indicates anomaly
        
    def generate_predictive_alerts(self):
        """Generate alerts based on predictive analysis."""
        # Monitor key metrics for early warning signs
        metrics_to_monitor = [
            'trading_order_execution_latency_seconds',
            'trading_market_data_latency_ms',
            'rate(trading_orders_total[5m])',
            'trading_open_positions'
        ]
        
        anomalies = {}
        for metric in metrics_to_monitor:
            data = self.fetch_historical_metrics(metric)
            is_anomalous = self.detect_anomalies(data)
            
            if np.any(is_anomalous):
                anomalies[metric] = {
                    'detected_at': datetime.now(),
                    'severity': self._calculate_severity(metric, data),
                    'recommended_action': self._get_recommendation(metric)
                }
                
        return anomalies
        
    def _extract_features(self, data):
        """Extract features for anomaly detection."""
        features = []
        if len(data) > 10:
            features.append(np.mean(data[-10:]))  # Recent mean
            features.append(np.std(data[-10:]))   # Recent std
            features.append(data[-1] / np.mean(data) if np.mean(data) != 0 else 0)  # Current vs average
            features.append(np.max(data[-10:]) - np.min(data[-10:]))  # Recent range
        return np.array(features).reshape(1, -1)
```

## 📚 Learning Outcomes

By completing Day 92, you will be able to:

- **Design** and implement comprehensive monitoring architectures for trading systems
- **Configure** Prometheus for efficient metrics collection and alerting
- **Create** custom metric exporters for trading-specific metrics
- **Build** informative Grafana dashboards for real-time monitoring
- **Implement** multi-level alerting with appropriate routing and notification
- **Develop** predictive alerting systems using recording rules and anomaly detection
- **Test** and validate monitoring system functionality
- **Deploy** monitoring stacks in both development and production environments

## 🚨 Best Practices

1. **Alert Design:**
   - Use meaningful alert names and descriptions
   - Set appropriate thresholds based on historical data
   - Implement alert deduplication and grouping
   - Create runbooks for each alert type

2. **Dashboard Design:**
   - Group related metrics together
   - Use consistent color schemes
   - Include both real-time and historical views
   - Add annotations for significant events

3. **Performance Considerations:**
   - Limit scrape intervals based on metric importance
   - Use recording rules for expensive queries
   - Implement metric cardinality controls
   - Monitor the monitoring system itself

4. **Security:**
   - Secure Prometheus and Grafana endpoints
   - Use authentication for metric endpoints
   - Encrypt sensitive alert configurations
   - Implement access controls for dashboards

## 🔧 Troubleshooting Guide

### Common Issues and Solutions:

1. **Prometheus not scraping metrics:**
```bash
# Check target status
curl http://localhost:9090/api/v1/targets

# Check service discovery
curl http://localhost:9090/api/v1/discovery
```

2. **Alerts not firing:**
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Test alert expression
curl http://localhost:9090/api/v1/query?query=ALERTS
```

3. **High resource usage:**
```yaml
# In prometheus.yml
global:
  scrape_interval: 30s  # Increase interval
  evaluation_interval: 30s
```

4. **Missing metrics:**
- Verify exporter is running
- Check firewall rules
- Verify metric names match queries
- Check Prometheus service discovery

## 📈 Next Steps

After setting up the basic monitoring system, consider:

1. **Advanced Monitoring:**
   - Implement distributed tracing with Jaeger
   - Add log aggregation with ELK stack
   - Set up synthetic monitoring for critical paths

2. **Scalability:**
   - Deploy Prometheus in HA mode
   - Implement long-term storage with Thanos
   - Set up federation for multi-cluster monitoring

3. **Advanced Analytics:**
   - Integrate machine learning for anomaly detection
   - Implement predictive capacity planning
   - Add automated root cause analysis

4. **Compliance:**
   - Implement audit logging for monitoring access
   - Set up compliance reporting dashboards
   - Create alert retention policies

---

This monitoring system provides the foundation for operational excellence in trading systems, enabling you to detect issues before they impact trading performance and maintain system reliability 24/7.