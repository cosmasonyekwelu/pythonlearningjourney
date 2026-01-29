# Day 46: Order Management System (OMS)

**Date:** November 6, 2025

## Learning Objective
To build a multi-threaded Order Management System (OMS) that handles order queuing, asynchronous processing, and position tracking.

## Concepts Covered
- **Queuing**: Using the `queue.Queue` module for thread-safe order handling.
- **Multi-threading**: Running a background "processor" thread that executes orders while the main app remains responsive.
- **Position Tracking**: Calculating average fill prices and managing inventory as orders are filled.
- **Audit Trails**: Recording every status change in an `order_events` table for forensic analysis.
- **State Machines**: Managing the lifecycle of an order (PENDING -> SUBMITTED -> FILLED/REJECTED).

## Code Explanation
The `day_fortysix.py` script implements the `OrderManagementSystem`:
- **`create_order()`**: Generates a unique ID, saves the order to SQLite, and pushes it to the processing queue.
- **`start_order_processor()`**: Spawns a daemon thread that continuously polls the queue.
- **`process_order()`**: Simulates a broker interaction and randomly chooses an outcome (Filled, Partial, or Rejected).
- **`update_positions()`**: Handles the math for updating holdings and average costs when a buy or sell occurs.

## How to Run
1. Install dependencies: `pip install pandas`
2. Run the OMS simulation:
```bash
python week_07/dayfortysix/day_fortysix.py
```

## Reflection
A real trading system never processes orders in a blocking way. Implementing a queue and a separate processor thread is the first step toward building a scalable and resilient trading engine.
