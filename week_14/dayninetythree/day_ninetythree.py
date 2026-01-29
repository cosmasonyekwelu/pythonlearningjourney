"""
Day 93: Structured Logging & Audit Systems for Trading
Implements JSON logging with correlation IDs and audit capabilities for compliance.
"""

import logging
import logging.config
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
import threading
from contextvars import ContextVar

# Context-local storage for correlation IDs
correlation_id = ContextVar('correlation_id', default=str(uuid.uuid4()))

class TradingLogger:
    """Main logger class for trading systems."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._setup_logging_config()
        self._initialized = True

    def _setup_logging_config(self):
        """Configure logging with simplified structure for demonstration."""
        # Simple JSON-like formatter for educational purposes
        class SimpleJsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage(),
                    "correlation_id": correlation_id.get(),
                }
                if hasattr(record, 'extra'):
                    log_record.update(record.extra)
                return json.dumps(log_record)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(SimpleJsonFormatter())

        self.logger = logging.getLogger('trading')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade event with extra fields."""
        self.logger.info(f"Trade executed: {trade_data.get('symbol')}", extra=trade_data)

    def audit(self, action: str, details: Dict[str, Any]):
        """Log an audit event."""
        self.logger.info(f"AUDIT: {action}", extra={"audit_action": action, "details": details})

# Global instance
trading_logger = TradingLogger()

def demonstrate_logging():
    print("--- Demonstrating Structured Logging ---")

    # Simulate a request context
    cid = str(uuid.uuid4())
    correlation_id.set(cid)

    trading_logger.logger.info("System initialized")

    trade = {
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.25,
        "strategy": "momentum"
    }
    trading_logger.log_trade(trade)

    trading_logger.audit("LIMIT_CHANGE", {"user": "admin", "old_limit": 1000, "new_limit": 5000})

if __name__ == "__main__":
    demonstrate_logging()
