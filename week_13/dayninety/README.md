# Day 90: Real-Time Data Pipelines & Stream Processing

## Objective
Build high-throughput real-time data pipelines for market data ingestion, processing, and distribution using Kafka and Flink.

## Concepts Covered
- **Stream Processing**: Using Apache Kafka for low-latency message streaming and Apache Flink for stateful processing.
- **Complex Event Processing (CEP)**: Detecting arbitrage opportunities (triangular, cross-exchange) in real-time.
- **Data Enrichment**: Performing stream-table joins to enrich market data with instrument metadata.
- **Schema Management**: Using a Schema Registry to manage data contracts and evolution.

## Code Explanation
The `day_ninety.py` script provides a complete implementation of a real-time data pipeline, including WebSocket ingestion, normalization, windowed aggregation, and technical indicator calculation.

## How to Run
This day requires a Kafka cluster and Redis. Review the `day_ninety.py` file for the pipeline orchestration logic and stream processing jobs.
