# Day 96: Disaster Recovery and Fault Tolerance

## Objective
Design and implement disaster recovery mechanisms and fault-tolerant patterns to ensure 24/7 system availability.

## Concepts Covered
- **Failover Management**: Automatically promoting secondary systems when the primary fails.
- **State Recovery**: Reconciling positions and order states with brokers after a system outage.
- **Resilience Patterns**: Implementing circuit breakers and retries with exponential backoff.
- **High Availability**: Multi-AZ deployments and data replication strategies.

## Code Explanation
The `day_ninetysix.py` script provides a `FailoverManager` that monitors system health and demonstrates an automated failover and state recovery sequence.

## How to Run
Run the disaster recovery simulation:
```bash
python day_ninetysix.py
```
