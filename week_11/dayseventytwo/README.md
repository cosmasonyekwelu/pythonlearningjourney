# Day 72: Advanced Data Mocking and Synthetic Data Generation

## Objective
Learn how to generate high-fidelity synthetic market data and complex mock objects for robust system testing.

## Concepts Covered
- **Synthetic Data Generation**: Creating price series with trends, seasonality, and noise.
- **Advanced Mocking**: Using `unittest.mock` to simulate complex service interactions.
- **Data Fidelity**: Ensuring synthetic data maintains realistic properties (e.g., OHLC consistency).
- **Test Environments**: Setting up isolated environments for data-dependent tests.

## Code Explanation
The `day_seventytwo.py` script demonstrates:
- A `MarketDataGenerator` class that uses `numpy` to create realistic synthetic price paths.
- Mocking a multi-threaded data feed to test concurrency handling in the ingestion pipeline.
- Validation logic for ensuring data quality during ingestion.

## How to Run
Run the demonstration script:
```bash
python day_seventytwo.py
```
Or run the associated tests:
```bash
pytest day_seventytwo.py -v
```
