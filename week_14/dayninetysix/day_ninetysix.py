"""
Day 96: Disaster Recovery & Fault Tolerance
Demonstrates failover mechanisms, state recovery, and health checks.
"""

import time
import random
from typing import Dict, Optional
from enum import Enum

class SystemStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"

class FailoverManager:
    """Manages system health and handles automated failover."""

    def __init__(self):
        self.primary_active = True
        self.last_sync_time = time.time()
        self.status = SystemStatus.HEALTHY

    def check_health(self) -> SystemStatus:
        """Simulate health check logic."""
        # Randomly simulate failures for demonstration
        if random.random() < 0.1:
            return SystemStatus.FAILED
        return SystemStatus.HEALTHY

    def execute_failover(self):
        """Handle failover from primary to secondary."""
        print("CRITICAL: Primary system failed! Initiating failover...")
        self.primary_active = False
        print("SUCCESS: Secondary system promoted to Active.")
        self.status = SystemStatus.DEGRADED  # Running on backup

    def recover_state(self):
        """Simulate state recovery and position reconciliation."""
        print("INFO: Reconciling positions with broker...")
        time.sleep(1)
        print("INFO: State recovery complete.")

def run_simulation():
    manager = FailoverManager()
    print("--- Disaster Recovery Simulation ---")

    for i in range(5):
        print(f"\nCycle {i+1}: Monitoring health...")
        status = manager.check_health()

        if status == SystemStatus.FAILED and manager.primary_active:
            manager.execute_failover()
            manager.recover_state()
        elif manager.primary_active:
            print("Status: Primary Healthy ✓")
        else:
            print("Status: Running on Secondary ⚠")

        time.sleep(0.5)

if __name__ == "__main__":
    run_simulation()
