"""
Day 95: Security Hardening & Compliance
Automated security assessment and hardening framework for trading systems.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class ThreatLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SecurityFinding:
    id: str
    title: str
    description: str
    threat_level: ThreatLevel
    affected_component: str
    recommendation: str

class TradingSecurityAssessor:
    """Assess trading system security based on configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.findings: List[SecurityFinding] = []

    def perform_assessment(self):
        """Run a battery of security checks."""
        self._check_auth()
        self._check_encryption()
        self._check_api_security()

    def _check_auth(self):
        if not self.config.get('multi_factor_auth', False):
            self.findings.append(SecurityFinding(
                "SEC-001", "Missing MFA",
                "MFA is not enabled for trading operations",
                ThreatLevel.CRITICAL, "User Authentication",
                "Enable TOTP or WebAuthn for all user accounts"
            ))

    def _check_encryption(self):
        if self.config.get('tls_version', 1.2) < 1.3:
            self.findings.append(SecurityFinding(
                "SEC-002", "Legacy TLS",
                "System uses TLS 1.2 which is less secure than 1.3",
                ThreatLevel.MEDIUM, "Network",
                "Upgrade to TLS 1.3"
            ))

    def _check_api_security(self):
        if not self.config.get('rate_limiting', False):
            self.findings.append(SecurityFinding(
                "SEC-003", "No Rate Limiting",
                "API endpoints are vulnerable to brute force",
                ThreatLevel.HIGH, "API Gateway",
                "Implement request throttling and rate limiting"
            ))

    def generate_report(self):
        print(f"--- Security Assessment Report ({datetime.now().date()}) ---")
        if not self.findings:
            print("No vulnerabilities found! ✓")
            return

        for f in self.findings:
            print(f"[{f.threat_level.value.upper()}] {f.title}")
            print(f"   Component: {f.affected_component}")
            print(f"   Recommendation: {f.recommendation}\n")

if __name__ == "__main__":
    # Simulate a system with poor security settings
    risky_config = {
        "multi_factor_auth": False,
        "tls_version": 1.2,
        "rate_limiting": False
    }

    assessor = TradingSecurityAssessor(risky_config)
    assessor.perform_assessment()
    assessor.generate_report()
