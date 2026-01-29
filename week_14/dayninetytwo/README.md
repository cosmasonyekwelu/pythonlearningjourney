# Day 92: Monitoring & Alerting with Grafana and Prometheus

## Objective
Set up a comprehensive monitoring and alerting infrastructure for trading systems using Prometheus and Grafana.

## Concepts Covered
- **Prometheus Metrics**: Implementing custom exporters for trading-specific metrics (PnL, position value, latency).
- **Grafana Dashboards**: Designing real-time visualizations for system health and trading performance.
- **Alerting Rules**: Configuring critical alerts for drawdown, service downtime, and high latency.
- **Predictive Alerting**: Using recording rules to detect anomalies in trading patterns.

## Code Explanation
The `day_ninetytwo.py` script implements a `TradingMetricsExporter` that collects and serves metrics from trading services to a Prometheus server.

## How to Run
This day requires a Prometheus and Grafana stack. Run the exporter script:
```bash
python day_ninetytwo.py
```
