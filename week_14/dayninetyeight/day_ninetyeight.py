"""
Day 98: Weekly Project – Production Monitoring Integration
Ties together monitoring, logging, and health checks for a production-ready system.
"""

import time
import logging
from typing import Dict

# Use the structured logging concepts from Day 93
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("ProdMonitor")

class ProductionSystem:
    """Simulates a production trading system with integrated monitoring."""

    def __init__(self):
        self.is_running = True
        self.error_count = 0

    def perform_operation(self):
        """Simulate a trading operation."""
        # Simulated activity
        time.sleep(0.1)
        if time.time() % 10 < 1:  # Simulate occasional transient issue
            logger.warning("Network latency spike detected")
            self.error_count += 1

    def run(self):
        logger.info("System starting up...")
        logger.info("Monitoring hooks attached.")

        try:
            for i in range(10):
                self.perform_operation()
                if i % 2 == 0:
                    logger.info(f"Health Check: OK (Total Errors: {self.error_count})")
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("System shutting down gracefully.")

if __name__ == "__main__":
    sys = ProductionSystem()
    sys.run()
