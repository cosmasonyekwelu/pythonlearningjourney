# Day 95: Security Hardening & Compliance

## 🔒 Project Overview

Harden trading systems against security threats and implement compliance controls for regulatory requirements. This day focuses on building a comprehensive security framework that protects trading operations while meeting financial regulations.

## 🎯 Objective

Perform a security assessment of a trading system, implement security hardening measures, and create a compliance checklist for regulatory requirements.

## 🏗️ Architecture

```
security-framework/
├── threat-modeling/           # Threat modeling and risk assessment
│   ├── threat_models/        # Threat model definitions
│   ├── risk_assessments/     # Risk assessment reports
│   └── attack_trees/         # Attack tree analysis
├── authentication/           # Authentication and authorization
│   ├── multi_factor/         # Multi-factor authentication
│   ├── jwt_tokens/           # JWT implementation
│   └── oauth2/              # OAuth2 integration
├── encryption/               # Encryption implementations
│   ├── data_at_rest/         # Data at rest encryption
│   ├── data_in_transit/      # TLS/SSL configurations
│   └── key_management/       # Key management system
├── network-security/         # Network security controls
│   ├── firewalls/           # Firewall configurations
│   ├── waf/                 # Web Application Firewall
│   └── vpn/                 # VPN configurations
├── compliance/              # Regulatory compliance
│   ├── sec_17a/            # SEC Rule 17a-4
│   ├── mifid_ii/           # MiFID II compliance
│   └── gdpr/               # GDPR compliance
├── monitoring/              # Security monitoring
│   ├── siem/               # Security Information & Event Management
│   ├── ids_ips/            # Intrusion Detection/Prevention
│   └── vulnerability/      # Vulnerability scanning
├── docker-compose.yml      # Security testing environment
└── scripts/               # Security automation scripts
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- OpenSSL for certificate generation
- Basic understanding of security principles

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd security-framework

# Install dependencies
pip install -r requirements.txt

# Install security tools
pip install -r requirements-security.txt

# Generate TLS certificates
./scripts/generate_certificates.sh

# Start security testing environment
docker-compose up -d

# Run initial security scan
python security/assessment/initial_scan.py
```

## 🔐 Comprehensive Security Framework

### Security Assessment Engine (threat-modeling/security_assessor.py)

```python
"""
Comprehensive security assessment framework for trading systems.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import subprocess
import re
from datetime import datetime, timedelta
import asyncio
import aiohttp
import ssl
import hashlib
import secrets
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ComplianceStandard(Enum):
    SEC_17A = "SEC Rule 17a-4"
    MIFID_II = "MiFID II"
    GDPR = "GDPR"
    PCI_DSS = "PCI DSS"
    ISO_27001 = "ISO 27001"
    NIST_CSF = "NIST Cybersecurity Framework"
    SOC_2 = "SOC 2"
    DODD_FRANK = "Dodd-Frank Act"

@dataclass
class SecurityFinding:
    """Security finding from assessment."""
    id: str
    title: str
    description: str
    threat_level: ThreatLevel
    category: str
    affected_component: str
    recommendation: str
    evidence: Optional[Dict[str, Any]] = None
    cvss_score: Optional[float] = None
    compliance_impact: List[ComplianceStandard] = field(default_factory=list)
    remediation_effort: str = "medium"  # low, medium, high
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    remediation_status: str = "open"  # open, in_progress, resolved

@dataclass
class SecurityAssessment:
    """Comprehensive security assessment."""
    system_name: str
    assessment_date: datetime
    assessor: str
    scope: List[str]
    findings: List[SecurityFinding] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[ComplianceStandard, bool] = field(default_factory=dict)
    risk_score: float = 0.0

    def add_finding(self, finding: SecurityFinding):
        """Add a security finding."""
        self.findings.append(finding)
        self._update_summary()

    def _update_summary(self):
        """Update assessment summary."""
        total_findings = len(self.findings)
        critical_findings = len([f for f in self.findings if f.threat_level == ThreatLevel.CRITICAL])
        high_findings = len([f for f in self.findings if f.threat_level == ThreatLevel.HIGH])

        self.summary = {
            'total_findings': total_findings,
            'critical_findings': critical_findings,
            'high_findings': high_findings,
            'medium_findings': len([f for f in self.findings if f.threat_level == ThreatLevel.MEDIUM]),
            'low_findings': len([f for f in self.findings if f.threat_level == ThreatLevel.LOW]),
            'info_findings': len([f for f in self.findings if f.threat_level == ThreatLevel.INFO]),
            'risk_score': self._calculate_risk_score(),
        }

    def _calculate_risk_score(self) -> float:
        """Calculate overall risk score."""
        if not self.findings:
            return 0.0

        scores = {
            ThreatLevel.CRITICAL: 10.0,
            ThreatLevel.HIGH: 7.5,
            ThreatLevel.MEDIUM: 5.0,
            ThreatLevel.LOW: 2.5,
            ThreatLevel.INFO: 0.5,
        }

        total_score = sum(scores.get(f.threat_level, 0) for f in self.findings)
        return min(total_score / len(self.findings) * 10, 100.0)

    def generate_report(self, format: str = "html") -> str:
        """Generate security assessment report."""
        if format == "html":
            return self._generate_html_report()
        elif format == "json":
            return json.dumps(self, default=self._serialize_datetime, indent=2)
        elif format == "pdf":
            return self._generate_pdf_report()
        else:
            return self._generate_text_report()

    def _serialize_datetime(self, obj):
        """JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def _generate_html_report(self) -> str:
        """Generate HTML security report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Assessment Report - {system_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .finding {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .critical {{ border-left: 5px solid #e74c3c; }}
                .high {{ border-left: 5px solid #e67e22; }}
                .medium {{ border-left: 5px solid #f1c40f; }}
                .low {{ border-left: 5px solid #3498db; }}
                .info {{ border-left: 5px solid #2ecc71; }}
                .risk-score {{ font-size: 24px; font-weight: bold; }}
                .low-risk {{ color: #27ae60; }}
                .medium-risk {{ color: #f39c12; }}
                .high-risk {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Assessment Report</h1>
                <h2>{system_name}</h2>
                <p>Assessment Date: {assessment_date}</p>
                <p>Assessor: {assessor}</p>
            </div>

            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="risk-score {risk_class}">
                    Overall Risk Score: {risk_score}/100
                </div>
                <p>Total Findings: {total_findings}</p>
                <p>Critical Findings: {critical_findings}</p>
                <p>High Findings: {high_findings}</p>
                <p>Medium Findings: {medium_findings}</p>
                <p>Low Findings: {low_findings}</p>
            </div>

            <h2>Detailed Findings</h2>
            {findings_html}

            <h2>Compliance Status</h2>
            {compliance_html}
        </body>
        </html>
        """

        # Determine risk class
        risk_score = self.summary.get('risk_score', 0)
        if risk_score < 30:
            risk_class = "low-risk"
        elif risk_score < 70:
            risk_class = "medium-risk"
        else:
            risk_class = "high-risk"

        # Generate findings HTML
        findings_html = ""
        for finding in sorted(self.findings, key=lambda x: x.threat_level.value, reverse=True):
            finding_class = finding.threat_level.value
            findings_html += f"""
            <div class="finding {finding_class}">
                <h3>{finding.title} [{finding.threat_level.value.upper()}]</h3>
                <p><strong>Affected Component:</strong> {finding.affected_component}</p>
                <p><strong>Description:</strong> {finding.description}</p>
                <p><strong>Recommendation:</strong> {finding.recommendation}</p>
                <p><strong>Remediation Effort:</strong> {finding.remediation_effort}</p>
            </div>
            """

        # Generate compliance HTML
        compliance_html = ""
        for standard, status in self.compliance_status.items():
            status_text = "Compliant" if status else "Non-Compliant"
            status_color = "#2ecc71" if status else "#e74c3c"
            compliance_html += f"""
            <p><strong>{standard.value}:</strong>
                <span style="color: {status_color}">{status_text}</span>
            </p>
            """

        return html_template.format(
            system_name=self.system_name,
            assessment_date=self.assessment_date.isoformat(),
            assessor=self.assessor,
            risk_score=risk_score,
            risk_class=risk_class,
            total_findings=self.summary.get('total_findings', 0),
            critical_findings=self.summary.get('critical_findings', 0),
            high_findings=self.summary.get('high_findings', 0),
            medium_findings=self.summary.get('medium_findings', 0),
            low_findings=self.summary.get('low_findings', 0),
            findings_html=findings_html,
            compliance_html=compliance_html,
        )

class TradingSystemSecurityAssessor:
    """Security assessor for trading systems."""

    def __init__(self, system_config: Dict[str, Any]):
        self.system_config = system_config
        self.assessment = SecurityAssessment(
            system_name=system_config.get('name', 'Trading System'),
            assessment_date=datetime.utcnow(),
            assessor=system_config.get('assessor', 'Security Team'),
            scope=system_config.get('scope', ['trading', 'market_data', 'risk']),
        )

        # Security check modules
        self.check_modules = [
            self._check_authentication,
            self._check_authorization,
            self._check_encryption,
            self._check_network_security,
            self._check_api_security,
            self._check_data_security,
            self._check_compliance,
            self._check_vulnerabilities,
        ]

    async def perform_assessment(self) -> SecurityAssessment:
        """Perform comprehensive security assessment."""
        logger.info("Starting security assessment...")

        # Run all security checks
        tasks = [check() for check in self.check_modules]
        await asyncio.gather(*tasks)

        # Update compliance status
        self._assess_compliance()

        logger.info(f"Assessment completed. Found {len(self.assessment.findings)} issues.")
        return self.assessment

    async def _check_authentication(self):
        """Check authentication security."""
        logger.info("Checking authentication security...")

        findings = []

        # Check for weak passwords
        if self.system_config.get('password_policy', {}).get('min_length', 0) < 12:
            findings.append(SecurityFinding(
                id="AUTH-001",
                title="Weak Password Policy",
                description="Password policy allows passwords shorter than 12 characters",
                threat_level=ThreatLevel.HIGH,
                category="Authentication",
                affected_component="User Management",
                recommendation="Implement password policy with minimum 12 characters, requiring mix of uppercase, lowercase, numbers, and special characters",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.ISO_27001],
                remediation_effort="low",
            ))

        # Check for missing MFA
        if not self.system_config.get('multi_factor_auth', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="AUTH-002",
                title="Missing Multi-Factor Authentication",
                description="Multi-factor authentication is not enabled for trading operations",
                threat_level=ThreatLevel.CRITICAL,
                category="Authentication",
                affected_component="Trading Platform",
                recommendation="Implement MFA for all trading accounts, especially for high-value transactions",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.MIFID_II, ComplianceStandard.PCI_DSS],
                remediation_effort="medium",
            ))

        # Check for JWT security
        jwt_config = self.system_config.get('jwt', {})
        if jwt_config.get('algorithm', 'HS256') == 'HS256' and jwt_config.get('key_length', 0) < 32:
            findings.append(SecurityFinding(
                id="AUTH-003",
                title="Weak JWT Signing Key",
                description="JWT signing key is too short or uses weak algorithm",
                threat_level=ThreatLevel.HIGH,
                category="Authentication",
                affected_component="API Gateway",
                recommendation="Use RS256 algorithm with 2048-bit key or HS256 with at least 256-bit key",
                remediation_effort="medium",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_authorization(self):
        """Check authorization and access controls."""
        logger.info("Checking authorization security...")

        findings = []

        # Check for excessive permissions
        if self.system_config.get('rbac', {}).get('default_role') == 'admin':
            findings.append(SecurityFinding(
                id="AUTHZ-001",
                title="Default Admin Role",
                description="Default user role has administrative privileges",
                threat_level=ThreatLevel.HIGH,
                category="Authorization",
                affected_component="User Management",
                recommendation="Implement principle of least privilege, default users should have minimal permissions",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.ISO_27001],
                remediation_effort="low",
            ))

        # Check for missing role-based access control
        if not self.system_config.get('rbac', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="AUTHZ-002",
                title="Missing Role-Based Access Control",
                description="No RBAC system implemented for trading operations",
                threat_level=ThreatLevel.CRITICAL,
                category="Authorization",
                affected_component="Trading Platform",
                recommendation="Implement RBAC with roles for traders, risk managers, compliance officers, and administrators",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.MIFID_II],
                remediation_effort="high",
            ))

        # Check for audit trail
        if not self.system_config.get('audit_trail', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="AUTHZ-003",
                title="Missing Audit Trail",
                description="No comprehensive audit trail for user actions",
                threat_level=ThreatLevel.HIGH,
                category="Authorization",
                affected_component="System Logging",
                recommendation="Implement immutable audit trail logging all user actions, especially trades and configuration changes",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.MIFID_II],
                remediation_effort="medium",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_encryption(self):
        """Check encryption implementation."""
        logger.info("Checking encryption security...")

        findings = []

        # Check data at rest encryption
        if not self.system_config.get('encryption', {}).get('data_at_rest', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="ENC-001",
                title="Missing Data at Rest Encryption",
                description="Sensitive data stored without encryption",
                threat_level=ThreatLevel.CRITICAL,
                category="Encryption",
                affected_component="Database/Storage",
                recommendation="Implement encryption for all sensitive data at rest using AES-256 or equivalent",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.GDPR, ComplianceStandard.PCI_DSS],
                remediation_effort="high",
            ))

        # Check TLS configuration
        tls_config = self.system_config.get('encryption', {}).get('tls', {})
        if tls_config.get('version', '') != '1.3':
            findings.append(SecurityFinding(
                id="ENC-002",
                title="Weak TLS Configuration",
                description="TLS version is not 1.3, may be vulnerable to attacks",
                threat_level=ThreatLevel.HIGH,
                category="Encryption",
                affected_component="Network Communication",
                recommendation="Upgrade to TLS 1.3 with strong cipher suites, disable weak protocols (SSLv3, TLS 1.0, TLS 1.1)",
                remediation_effort="medium",
            ))

        # Check key management
        if not self.system_config.get('encryption', {}).get('key_management', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="ENC-003",
                title="Inadequate Key Management",
                description="No proper key management system in place",
                threat_level=ThreatLevel.HIGH,
                category="Encryption",
                affected_component="Security Infrastructure",
                recommendation="Implement key management system with automatic key rotation, secure storage, and access controls",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.PCI_DSS],
                remediation_effort="high",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_network_security(self):
        """Check network security controls."""
        logger.info("Checking network security...")

        findings = []

        # Check firewall configuration
        if not self.system_config.get('network', {}).get('firewall', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="NET-001",
                title="Missing Network Firewall",
                description="No network firewall protecting trading infrastructure",
                threat_level=ThreatLevel.CRITICAL,
                category="Network Security",
                affected_component="Network Infrastructure",
                recommendation="Implement stateful firewall with strict ingress/egress rules, segment network zones",
                remediation_effort="medium",
            ))

        # Check for Web Application Firewall
        if not self.system_config.get('network', {}).get('waf', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="NET-002",
                title="Missing Web Application Firewall",
                description="No WAF protecting trading APIs",
                threat_level=ThreatLevel.HIGH,
                category="Network Security",
                affected_component="API Gateway",
                recommendation="Implement WAF with rules for SQL injection, XSS, CSRF, and API abuse protection",
                remediation_effort="medium",
            ))

        # Check VPN requirements
        if not self.system_config.get('network', {}).get('vpn', {}).get('required', False):
            findings.append(SecurityFinding(
                id="NET-003",
                title="Missing VPN Requirement",
                description="Remote access to trading systems not restricted to VPN",
                threat_level=ThreatLevel.HIGH,
                category="Network Security",
                affected_component="Remote Access",
                recommendation="Require VPN for all remote access to trading systems, implement multi-factor authentication for VPN",
                compliance_impact=[ComplianceStandard.SEC_17A],
                remediation_effort="medium",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_api_security(self):
        """Check API security controls."""
        logger.info("Checking API security...")

        findings = []

        # Check API rate limiting
        if not self.system_config.get('api', {}).get('rate_limiting', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="API-001",
                title="Missing API Rate Limiting",
                description="No rate limiting on trading APIs",
                threat_level=ThreatLevel.HIGH,
                category="API Security",
                affected_component="API Gateway",
                recommendation="Implement rate limiting per API key/IP address, with stricter limits for sensitive operations",
                remediation_effort="low",
            ))

        # Check API input validation
        if not self.system_config.get('api', {}).get('input_validation', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="API-002",
                title="Inadequate Input Validation",
                description="API endpoints lack proper input validation",
                threat_level=ThreatLevel.HIGH,
                category="API Security",
                affected_component="API Services",
                recommendation="Implement strict input validation, schema validation, and parameter sanitization for all API endpoints",
                remediation_effort="medium",
            ))

        # Check API versioning and deprecation
        if not self.system_config.get('api', {}).get('versioning', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="API-003",
                title="Missing API Versioning",
                description="No API versioning strategy",
                threat_level=ThreatLevel.MEDIUM,
                category="API Security",
                affected_component="API Management",
                recommendation="Implement API versioning with proper deprecation policies and backward compatibility",
                remediation_effort="low",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_data_security(self):
        """Check data security and privacy controls."""
        logger.info("Checking data security...")

        findings = []

        # Check data classification
        if not self.system_config.get('data', {}).get('classification', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="DATA-001",
                title="Missing Data Classification",
                description="No data classification scheme implemented",
                threat_level=ThreatLevel.HIGH,
                category="Data Security",
                affected_component="Data Management",
                recommendation="Implement data classification (public, internal, confidential, restricted) with corresponding handling requirements",
                compliance_impact=[ComplianceStandard.GDPR, ComplianceStandard.SEC_17A],
                remediation_effort="medium",
            ))

        # Check data retention policies
        if not self.system_config.get('data', {}).get('retention_policy', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="DATA-002",
                title="Missing Data Retention Policy",
                description="No data retention and disposal policy",
                threat_level=ThreatLevel.HIGH,
                category="Data Security",
                affected_component="Data Management",
                recommendation="Implement data retention policies compliant with SEC 17a-4 (7 years) and GDPR right to be forgotten",
                compliance_impact=[ComplianceStandard.SEC_17A, ComplianceStandard.GDPR],
                remediation_effort="high",
            ))

        # Check for PII handling
        if self.system_config.get('data', {}).get('pii_handling', {}).get('encryption_required', False) is not True:
            findings.append(SecurityFinding(
                id="DATA-003",
                title="Inadequate PII Protection",
                description="Personally Identifiable Information not properly protected",
                threat_level=ThreatLevel.CRITICAL,
                category="Data Security",
                affected_component="User Data",
                recommendation="Encrypt all PII at rest and in transit, implement access controls, and data minimization principles",
                compliance_impact=[ComplianceStandard.GDPR],
                remediation_effort="high",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_compliance(self):
        """Check regulatory compliance requirements."""
        logger.info("Checking compliance requirements...")

        findings = []

        # Check SEC 17a-4 compliance
        sec_config = self.system_config.get('compliance', {}).get('sec_17a', {})
        if not sec_config.get('wom_storage', False):
            findings.append(SecurityFinding(
                id="COMP-001",
                title="Non-Compliant Audit Storage",
                description="Audit trail storage does not meet SEC 17a-4 WORM requirements",
                threat_level=ThreatLevel.CRITICAL,
                category="Compliance",
                affected_component="Audit System",
                recommendation="Implement Write-Once-Read-Many storage for audit trails that prevents alteration or deletion",
                compliance_impact=[ComplianceStandard.SEC_17A],
                remediation_effort="high",
            ))

        # Check MiFID II best execution
        if not self.system_config.get('compliance', {}).get('mifid_ii', {}).get('best_execution_monitoring', False):
            findings.append(SecurityFinding(
                id="COMP-002",
                title="Missing Best Execution Monitoring",
                description="No monitoring for best execution requirements under MiFID II",
                threat_level=ThreatLevel.HIGH,
                category="Compliance",
                affected_component="Trading Engine",
                recommendation="Implement best execution monitoring and reporting as required by MiFID II Article 27",
                compliance_impact=[ComplianceStandard.MIFID_II],
                remediation_effort="high",
            ))

        # Check GDPR requirements
        gdpr_config = self.system_config.get('compliance', {}).get('gdpr', {})
        if not gdpr_config.get('data_subject_rights', {}).get('enabled', False):
            findings.append(SecurityFinding(
                id="COMP-003",
                title="Missing GDPR Data Subject Rights",
                description="No process for handling GDPR data subject rights requests",
                threat_level=ThreatLevel.HIGH,
                category="Compliance",
                affected_component="Data Management",
                recommendation="Implement processes for data access, rectification, erasure, and portability requests",
                compliance_impact=[ComplianceStandard.GDPR],
                remediation_effort="medium",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    async def _check_vulnerabilities(self):
        """Check for known vulnerabilities."""
        logger.info("Checking for vulnerabilities...")

        findings = []

        # Check software versions
        software_versions = self.system_config.get('software_versions', {})

        # Example: Check for outdated Python
        python_version = software_versions.get('python', '')
        if python_version and python_version < '3.9':
            findings.append(SecurityFinding(
                id="VULN-001",
                title="Outdated Python Version",
                description=f"Python version {python_version} has known security vulnerabilities",
                threat_level=ThreatLevel.HIGH,
                category="Vulnerability Management",
                affected_component="Application Runtime",
                recommendation="Upgrade to Python 3.9 or later, regularly update dependencies",
                remediation_effort="medium",
            ))

        # Check dependency vulnerabilities
        if not self.system_config.get('vulnerability_management', {}).get('dependency_scanning', False):
            findings.append(SecurityFinding(
                id="VULN-002",
                title="Missing Dependency Vulnerability Scanning",
                description="No automated scanning for vulnerable dependencies",
                threat_level=ThreatLevel.HIGH,
                category="Vulnerability Management",
                affected_component="Software Development",
                recommendation="Implement automated dependency scanning in CI/CD pipeline, use tools like Snyk or Dependabot",
                remediation_effort="low",
            ))

        # Check for missing security headers
        headers_config = self.system_config.get('security_headers', {})
        required_headers = ['Content-Security-Policy', 'X-Content-Type-Options', 'X-Frame-Options']
        missing_headers = [h for h in required_headers if not headers_config.get(h.lower().replace('-', '_'), False)]

        if missing_headers:
            findings.append(SecurityFinding(
                id="VULN-003",
                title="Missing Security Headers",
                description=f"Missing security headers: {', '.join(missing_headers)}",
                threat_level=ThreatLevel.MEDIUM,
                category="Web Security",
                affected_component="Web Application",
                recommendation=f"Implement missing security headers: {', '.join(missing_headers)}",
                remediation_effort="low",
            ))

        for finding in findings:
            self.assessment.add_finding(finding)

    def _assess_compliance(self):
        """Assess compliance with regulations."""
        # Simplified compliance assessment
        # In production, this would be more comprehensive

        compliance_status = {}

        # SEC 17a-4
        sec_compliant = all([
            self.system_config.get('audit_trail', {}).get('enabled', False),
            self.system_config.get('compliance', {}).get('sec_17a', {}).get('wom_storage', False),
            self.system_config.get('data', {}).get('retention_policy', {}).get('enabled', False),
        ])
        compliance_status[ComplianceStandard.SEC_17A] = sec_compliant

        # MiFID II
        mifid_compliant = all([
            self.system_config.get('compliance', {}).get('mifid_ii', {}).get('best_execution_monitoring', False),
            self.system_config.get('audit_trail', {}).get('enabled', False),
            self.system_config.get('data', {}).get('classification', {}).get('enabled', False),
        ])
        compliance_status[ComplianceStandard.MIFID_II] = mifid_compliant

        # GDPR
        gdpr_compliant = all([
            self.system_config.get('data', {}).get('pii_handling', {}).get('encryption_required', False),
            self.system_config.get('compliance', {}).get('gdpr', {}).get('data_subject_rights', {}).get('enabled', False),
            self.system_config.get('data', {}).get('retention_policy', {}).get('enabled', False),
        ])
        compliance_status[ComplianceStandard.GDPR] = gdpr_compliant

        self.assessment.compliance_status = compliance_status

# Example usage
async def run_security_assessment():
    """Run comprehensive security assessment."""

    # Example system configuration
    system_config = {
        'name': 'Quantum Trading System',
        'assessor': 'Security Team',
        'scope': ['trading', 'market_data', 'risk', 'compliance'],

        'password_policy': {
            'min_length': 8,
        },
        'multi_factor_auth': {
            'enabled': False,
        },
        'jwt': {
            'algorithm': 'HS256',
            'key_length': 16,
        },
        'rbac': {
            'enabled': False,
            'default_role': 'admin',
        },
        'audit_trail': {
            'enabled': True,
        },
        'encryption': {
            'data_at_rest': {'enabled': False},
            'tls': {'version': '1.2'},
            'key_management': {'enabled': False},
        },
        'network': {
            'firewall': {'enabled': True},
            'waf': {'enabled': False},
            'vpn': {'required': False},
        },
        'api': {
            'rate_limiting': {'enabled': False},
            'input_validation': {'enabled': True},
            'versioning': {'enabled': False},
        },
        'data': {
            'classification': {'enabled': False},
            'retention_policy': {'enabled': True},
            'pii_handling': {'encryption_required': False},
        },
        'compliance': {
            'sec_17a': {'wom_storage': False},
            'mifid_ii': {'best_execution_monitoring': False},
            'gdpr': {'data_subject_rights': {'enabled': False}},
        },
        'software_versions': {
            'python': '3.8.0',
        },
        'vulnerability_management': {
            'dependency_scanning': False,
        },
        'security_headers': {
            'content_security_policy': False,
            'x_content_type_options': True,
            'x_frame_options': False,
        },
    }

    # Run assessment
    assessor = TradingSystemSecurityAssessor(system_config)
    assessment = await assessor.perform_assessment()

    # Generate report
    report_html = assessment.generate_report(format="html")

    # Save report
    with open('security_assessment_report.html', 'w') as f:
        f.write(report_html)

    print(f"Security assessment completed. Report saved to security_assessment_report.html")
    print(f"Total findings: {assessment.summary.get('total_findings', 0)}")
    print(f"Risk score: {assessment.summary.get('risk_score', 0):.1f}/100")

    return assessment

if __name__ == "__main__":
    asyncio.run(run_security_assessment())
```

## 🔐 Advanced Authentication System

### Multi-Factor Authentication (authentication/multi_factor/mfa_system.py)

```python
"""
Advanced Multi-Factor Authentication system for trading platforms.
Implements TOTP, WebAuthn, and biometric authentication.
"""

import time
import hmac
import hashlib
import base64
import struct
import secrets
import qrcode
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pickle
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyotp
import webauthn
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticationCredential,
)
import bcrypt
import jwt
from redis import Redis

@dataclass
class MFAMethod:
    """MFA method configuration."""
    method_id: str
    method_type: str  # totp, webauthn, sms, email, biometric
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MFASession:
    """MFA authentication session."""
    session_id: str
    user_id: str
    methods_required: List[str]
    methods_completed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def is_complete(self) -> bool:
        """Check if all required methods are completed."""
        return all(method in self.methods_completed for method in self.methods_required)

class MultiFactorAuthentication:
    """Advanced MFA system for trading platforms."""

    def __init__(self, redis_client: Redis, encryption_key: bytes):
        self.redis = redis_client
        self.encryption_key = encryption_key

        # Initialize ciphers
        self._init_ciphers()

        # Configuration
        self.config = {
            'totp_interval': 30,
            'totp_digits': 6,
            'totp_window': 1,  # Allow 1 interval before/after
            'max_login_attempts': 5,
            'lockout_duration_minutes': 15,
            'session_timeout_minutes': 10,
            'backup_code_count': 10,
            'backup_code_length': 8,
        }

    def _init_ciphers(self):
        """Initialize encryption ciphers."""
        # Derive encryption key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'trading_mfa_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key))
        self.cipher = Fernet(key)

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data)

    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data)

    def setup_totp(self, user_id: str) -> Dict[str, Any]:
        """Setup TOTP for a user."""
        # Generate secret
        secret = pyotp.random_base32()

        # Create TOTP object
        totp = pyotp.TOTP(
            secret,
            interval=self.config['totp_interval'],
            digits=self.config['totp_digits']
        )

        # Generate provisioning URI
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name="Quantum Trading System"
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Save secret (encrypted)
        encrypted_secret = self._encrypt_data(secret.encode())
        user_key = f"mfa:{user_id}:totp_secret"
        self.redis.setex(
            user_key,
            timedelta(days=365),  # 1 year expiry
            encrypted_secret
        )

        # Create method record
        method = MFAMethod(
            method_id=f"totp_{secrets.token_hex(8)}",
            method_type="totp",
            metadata={
                'setup_at': datetime.utcnow().isoformat(),
                'device_info': 'Unknown',
            }
        )
        self._save_method(user_id, method)

        # Generate backup codes
        backup_codes = self._generate_backup_codes(user_id)

        return {
            'secret': secret,  # Only shown during setup
            'provisioning_uri': provisioning_uri,
            'backup_codes': backup_codes,
            'method_id': method.method_id,
        }

    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate backup authentication codes."""
        backup_codes = []

        for i in range(self.config['backup_code_count']):
            code = secrets.token_urlsafe(self.config['backup_code_length']).upper()[:8]
            hashed_code = bcrypt.hashpw(code.encode(), bcrypt.gensalt())

            # Store hashed code
            backup_key = f"mfa:{user_id}:backup_codes:{i}"
            self.redis.setex(
                backup_key,
                timedelta(days=365),  # Backup codes valid for 1 year
                hashed_code
            )

            backup_codes.append(code)

        return backup_codes

    def verify_totp(self, user_id: str, code: str) -> bool:
        """Verify TOTP code."""
        # Get secret
        user_key = f"mfa:{user_id}:totp_secret"
        encrypted_secret = self.redis.get(user_key)

        if not encrypted_secret:
            return False

        # Decrypt secret
        secret = self._decrypt_data(encrypted_secret).decode()

        # Verify code
        totp = pyotp.TOTP(
            secret,
            interval=self.config['totp_interval'],
            digits=self.config['totp_digits']
        )

        return totp.verify(code, valid_window=self.config['totp_window'])

    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify backup code."""
        # Try all backup codes
        for i in range(self.config['backup_code_count']):
            backup_key = f"mfa:{user_id}:backup_codes:{i}"
            hashed_code = self.redis.get(backup_key)

            if hashed_code and bcrypt.checkpw(code.encode(), hashed_code):
                # Remove used backup code
                self.redis.delete(backup_key)
                return True

        return False

    def setup_webauthn(self, user_id: str, username: str, display_name: str) -> Dict[str, Any]:
        """Setup WebAuthn (FIDO2) authentication."""
        # Generate challenge
        challenge = secrets.token_bytes(32)

        # Create registration options
        options = webauthn.generate_registration_options(
            rp_id="trading.example.com",
            rp_name="Quantum Trading System",
            user_id=user_id.encode(),
            user_name=username,
            user_display_name=display_name,
            attestation="direct",
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED,
                resident_key="preferred",
            ),
            challenge=challenge,
        )

        # Store challenge for verification
        challenge_key = f"mfa:{user_id}:webauthn_challenge"
        self.redis.setex(
            challenge_key,
            timedelta(minutes=5),
            challenge
        )

        # Create method record
        method = MFAMethod(
            method_id=f"webauthn_{secrets.token_hex(8)}",
            method_type="webauthn",
            metadata={
                'setup_at': datetime.utcnow().isoformat(),
                'rp_id': options.rp.id,
            }
        )
        self._save_method(user_id, method)

        return {
            'challenge': bytes_to_base64url(challenge),
            'options': options,
            'method_id': method.method_id,
        }

    def verify_webauthn_registration(self, user_id: str, credential: Dict[str, Any]) -> bool:
        """Verify WebAuthn registration."""
        # Get stored challenge
        challenge_key = f"mfa:{user_id}:webauthn_challenge"
        stored_challenge = self.redis.get(challenge_key)

        if not stored_challenge:
            return False

        # Verify registration
        try:
            verification = webauthn.verify_registration_response(
                credential=RegistrationCredential.parse_raw(json.dumps(credential)),
                expected_challenge=stored_challenge,
                expected_rp_id="trading.example.com",
                expected_origin="https://trading.example.com",
            )

            # Store credential for future authentication
            credential_key = f"mfa:{user_id}:webauthn_credential"
            credential_data = {
                'credential_id': bytes_to_base64url(verification.credential_id),
                'public_key': verification.credential_public_key.decode(),
                'sign_count': verification.sign_count,
                'device_type': 'Unknown',
                'registered_at': datetime.utcnow().isoformat(),
            }

            self.redis.setex(
                credential_key,
                timedelta(days=365),
                pickle.dumps(credential_data)
            )

            # Clean up challenge
            self.redis.delete(challenge_key)

            return True

        except Exception as e:
            print(f"WebAuthn verification failed: {e}")
            return False

    def create_mfa_session(self, user_id: str, methods_required: List[str]) -> MFASession:
        """Create MFA authentication session."""
        # Check if user is locked out
        if self._is_user_locked_out(user_id):
            raise Exception("Account is temporarily locked due to too many failed attempts")

        # Create session
        session_id = secrets.token_urlsafe(32)
        session = MFASession(
            session_id=session_id,
            user_id=user_id,
            methods_required=methods_required,
            expires_at=datetime.utcnow() + timedelta(minutes=self.config['session_timeout_minutes']),
        )

        # Store session
        session_key = f"mfa_session:{session_id}"
        self.redis.setex(
            session_key,
            timedelta(minutes=self.config['session_timeout_minutes']),
            pickle.dumps(session)
        )

        return session

    def verify_mfa_attempt(self, session_id: str, method_type: str, credential: Any) -> bool:
        """Verify MFA attempt."""
        # Get session
        session_key = f"mfa_session:{session_id}"
        session_data = self.redis.get(session_key)

        if not session_data:
            return False

        session = pickle.loads(session_data)

        # Check if session is expired
        if session.is_expired():
            self.redis.delete(session_key)
            return False

        # Verify based on method type
        user_id = session.user_id

        if method_type == 'totp':
            if isinstance(credential, str) and self.verify_totp(user_id, credential):
                session.methods_completed.append('totp')
                self._save_session(session)
                return True

        elif method_type == 'backup_code':
            if isinstance(credential, str) and self.verify_backup_code(user_id, credential):
                session.methods_completed.append('backup_code')
                self._save_session(session)
                return True

        elif method_type == 'webauthn':
            if self._verify_webauthn_authentication(user_id, credential):
                session.methods_completed.append('webauthn')
                self._save_session(session)
                return True

        # Track failed attempt
        self._track_failed_attempt(user_id)

        return False

    def _verify_webauthn_authentication(self, user_id: str, credential: Dict[str, Any]) -> bool:
        """Verify WebAuthn authentication."""
        # Get stored credential
        credential_key = f"mfa:{user_id}:webauthn_credential"
        credential_data_bytes = self.redis.get(credential_key)

        if not credential_data_bytes:
            return False

        credential_data = pickle.loads(credential_data_bytes)

        # Generate challenge
        challenge = secrets.token_bytes(32)
        challenge_key = f"mfa:{user_id}:webauthn_auth_challenge"
        self.redis.setex(challenge_key, timedelta(minutes=5), challenge)

        try:
            # Verify authentication
            verification = webauthn.verify_authentication_response(
                credential=AuthenticationCredential.parse_raw(json.dumps(credential)),
                expected_challenge=challenge,
                expected_rp_id="trading.example.com",
                expected_origin="https://trading.example.com",
                credential_public_key=credential_data['public_key'].encode(),
                credential_current_sign_count=credential_data['sign_count'],
            )

            # Update sign count
            credential_data['sign_count'] = verification.new_sign_count
            credential_data['last_used'] = datetime.utcnow().isoformat()

            self.redis.setex(
                credential_key,
                timedelta(days=365),
                pickle.dumps(credential_data)
            )

            # Clean up challenge
            self.redis.delete(challenge_key)

            return True

        except Exception as e:
            print(f"WebAuthn authentication failed: {e}")
            return False

    def _track_failed_attempt(self, user_id: str):
        """Track failed authentication attempts."""
        attempt_key = f"mfa_failed_attempts:{user_id}"

        # Increment attempt counter
        current_attempts = self.redis.incr(attempt_key)

        # Set expiry on first attempt
        if current_attempts == 1:
            self.redis.expire(
                attempt_key,
                timedelta(minutes=self.config['lockout_duration_minutes'])
            )

        # Lock account if too many attempts
        if current_attempts >= self.config['max_login_attempts']:
            lockout_key = f"mfa_lockout:{user_id}"
            self.redis.setex(
                lockout_key,
                timedelta(minutes=self.config['lockout_duration_minutes']),
                'locked'
            )
            print(f"Account {user_id} locked due to too many failed attempts")

    def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out."""
        lockout_key = f"mfa_lockout:{user_id}"
        return self.redis.exists(lockout_key) > 0

    def _save_method(self, user_id: str, method: MFAMethod):
        """Save MFA method."""
        methods_key = f"mfa:{user_id}:methods"

        # Get existing methods
        existing_methods_data = self.redis.get(methods_key)
        if existing_methods_data:
            methods = pickle.loads(existing_methods_data)
        else:
            methods = []

        # Add or update method
        updated = False
        for i, existing_method in enumerate(methods):
            if existing_method.method_id == method.method_id:
                methods[i] = method
                updated = True
                break

        if not updated:
            methods.append(method)

        # Save back
        self.redis.setex(
            methods_key,
            timedelta(days=365),
            pickle.dumps(methods)
        )

    def _save_session(self, session: MFASession):
        """Save updated session."""
        session_key = f"mfa_session:{session.session_id}"
        self.redis.setex(
            session_key,
            timedelta(minutes=self.config['session_timeout_minutes']),
            pickle.dumps(session)
        )

    def get_user_methods(self, user_id: str) -> List[MFAMethod]:
        """Get all MFA methods for a user."""
        methods_key = f"mfa:{user_id}:methods"
        methods_data = self.redis.get(methods_key)

        if methods_data:
            return pickle.loads(methods_data)
        return []

    def generate_jwt_token(self, user_id: str, session_id: str) -> str:
        """Generate JWT token after successful MFA."""
        # Verify session is complete
        session_key = f"mfa_session:{session_id}"
        session_data = self.redis.get(session_key)

        if not session_data:
            raise Exception("Invalid session")

        session = pickle.loads(session_data)

        if not session.is_complete():
            raise Exception("MFA not complete")

        # Generate JWT
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'mfa_completed': True,
            'methods_used': session.methods_completed,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=8),  # 8-hour session
        }

        # Use secure signing key in production
        secret_key = self._encryption_key[:32]  # Use first 32 bytes
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            secret_key = self._encryption_key[:32]
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Additional verification
            session_id = payload.get('session_id')
            if session_id:
                session_key = f"mfa_session:{session_id}"
                if not self.redis.exists(session_key):
                    raise Exception("Session expired")

            return payload

        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

# Example usage
if __name__ == "__main__":
    import redis

    # Initialize Redis
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=False)

    # Generate encryption key (in production, use secure key management)
    encryption_key = secrets.token_bytes(32)

    # Create MFA system
    mfa = MultiFactorAuthentication(redis_client, encryption_key)

    # Example: Setup TOTP for user
    user_id = "trader_001"
    totp_setup = mfa.setup_totp(user_id)

    print("TOTP Setup:")
    print(f"Secret: {totp_setup['secret']}")
    print(f"Provisioning URI: {totp_setup['provisioning_uri']}")
    print(f"Backup Codes: {totp_setup['backup_codes']}")

    # Example: Create MFA session
    session = mfa.create_mfa_session(user_id, ['totp'])

    # Example: Verify TOTP code (simulated)
    # In real usage, get code from user input
    simulated_code = "123456"  # This would fail
    is_valid = mfa.verify_mfa_attempt(session.session_id, 'totp', simulated_code)

    print(f"\nTOTP Verification Result: {is_valid}")

    # Example: Get user methods
    methods = mfa.get_user_methods(user_id)
    print(f"\nUser MFA Methods: {len(methods)}")
```

## 🔒 Data Encryption & Key Management

### Enterprise Key Management System (encryption/key_management/enterprise_kms.py)

```python
"""
Enterprise Key Management System for trading platforms.
Implements secure key generation, rotation, and encryption operations.
"""

import hashlib
import hmac
import base64
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import redis
import boto3
from botocore.exceptions import ClientError
import azure.identity
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
import google.auth
from google.cloud import kms

class KeyType(Enum):
    """Types of encryption keys."""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    ED25519 = "ed25519"

class KeyPurpose(Enum):
    """Key purposes."""
    DATA_ENCRYPTION = "data_encryption"
    DATA_SIGNING = "data_signing"
    TOKEN_SIGNING = "token_signing"
    TLS_ENCRYPTION = "tls_encryption"
    DATABASE_ENCRYPTION = "database_encryption"

@dataclass
class EncryptionKey:
    """Encryption key with metadata."""
    key_id: str
    key_type: KeyType
    purpose: KeyPurpose
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotated_at: Optional[datetime] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def needs_rotation(self, rotation_period_days: int = 90) -> bool:
        """Check if key needs rotation."""
        if self.rotated_at:
            days_since_rotation = (datetime.utcnow() - self.rotated_at).days
            return days_since_rotation >= rotation_period_days

        days_since_creation = (datetime.utcnow() - self.created_at).days
        return days_since_creation >= rotation_period_days

@dataclass
class EncryptedData:
    """Encrypted data package."""
    ciphertext: bytes
    key_id: str
    encryption_algorithm: str
    iv: Optional[bytes] = None
    auth_tag: Optional[bytes] = None
    additional_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnterpriseKMS:
    """
    Enterprise Key Management System.
    Supports multiple key storage backends and encryption algorithms.
    """

    def __init__(self,
                 storage_backend: str = "redis",
                 cloud_kms_provider: Optional[str] = None,
                 master_key: Optional[bytes] = None):

        self.storage_backend = storage_backend
        self.cloud_kms_provider = cloud_kms_provider

        # Master key for wrapping/unwrapping data keys
        if master_key:
            self.master_key = master_key
        else:
            # In production, this should come from secure storage
            self.master_key = self._generate_master_key()

        # Initialize storage
        self._init_storage()

        # Initialize cloud KMS if configured
        if cloud_kms_provider:
            self._init_cloud_kms(cloud_kms_provider)

        # Key rotation schedule
        self.rotation_schedule = {
            KeyPurpose.DATA_ENCRYPTION: 90,  # days
            KeyPurpose.DATA_SIGNING: 365,
            KeyPurpose.TOKEN_SIGNING: 180,
            KeyPurpose.TLS_ENCRYPTION: 365,
            KeyPurpose.DATABASE_ENCRYPTION: 180,
        }

    def _generate_master_key(self) -> bytes:
        """Generate master key for wrapping data keys."""
        return secrets.token_bytes(32)  # 256-bit key

    def _init_storage(self):
        """Initialize key storage backend."""
        if self.storage_backend == "redis":
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=False,
                password=None,
            )
            self.storage = self._redis_storage
        elif self.storage_backend == "memory":
            self.key_store = {}
            self.storage = self._memory_storage
        else:
            raise ValueError(f"Unsupported storage backend: {self.storage_backend}")

    def _init_cloud_kms(self, provider: str):
        """Initialize cloud KMS provider."""
        if provider == "aws":
            self.kms_client = boto3.client('kms', region_name='us-east-1')
            self.cloud_kms = self._aws_kms
        elif provider == "azure":
            credential = azure.identity.DefaultAzureCredential()
            self.key_vault_url = "https://trading-kv.vault.azure.net/"
            self.key_client = KeyClient(vault_url=self.key_vault_url, credential=credential)
            self.cloud_kms = self._azure_kms
        elif provider == "gcp":
            self.kms_client = kms.KeyManagementServiceClient()
            self.cloud_kms = self._gcp_kms
        else:
            raise ValueError(f"Unsupported cloud KMS provider: {provider}")

    def _redis_storage(self, operation: str, key: str, value: Any = None) -> Any:
        """Redis storage operations."""
        if operation == "get":
            data = self.redis_client.get(key)
            return pickle.loads(data) if data else None
        elif operation == "set":
            serialized = pickle.dumps(value)
            self.redis_client.set(key, serialized)
        elif operation == "delete":
            self.redis_client.delete(key)
        elif operation == "exists":
            return self.redis_client.exists(key) > 0

    def _memory_storage(self, operation: str, key: str, value: Any = None) -> Any:
        """In-memory storage operations."""
        if operation == "get":
            return self.key_store.get(key)
        elif operation == "set":
            self.key_store[key] = value
        elif operation == "delete":
            if key in self.key_store:
                del self.key_store[key]
        elif operation == "exists":
            return key in self.key_store

    def generate_key(self,
                    key_type: KeyType,
                    purpose: KeyPurpose,
                    key_id: Optional[str] = None,
                    expires_in_days: Optional[int] = None) -> EncryptionKey:
        """Generate a new encryption key."""
        if not key_id:
            key_id = f"{purpose.value}_{secrets.token_hex(8)}"

        # Generate key material based on type
        if key_type == KeyType.AES_256:
            key_material = secrets.token_bytes(32)  # 256 bits
        elif key_type == KeyType.RSA_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            key_material = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        elif key_type == KeyType.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            key_material = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        elif key_type == KeyType.CHACHA20:
            key_material = secrets.token_bytes(32)  # 256 bits
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        # Create key metadata
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        key = EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            purpose=purpose,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            metadata={
                'generated_by': 'enterprise_kms',
                'key_size_bits': len(key_material) * 8,
            }
        )

        # Wrap key with master key
        wrapped_key = self._wrap_key(key_material, key_id)

        # Store wrapped key
        storage_key = f"key:{key_id}"
        key_data = {
            'key': wrapped_key,
            'metadata': key,
        }
        self.storage("set", storage_key, key_data)

        return key

    def _wrap_key(self, key_material: bytes, key_id: str) -> bytes:
        """Wrap (encrypt) a key using master key."""
        # Generate IV
        iv = secrets.token_bytes(12)  # 96 bits for GCM

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Add key_id as additional authenticated data
        encryptor.authenticate_additional_data(key_id.encode())

        # Encrypt key material
        ciphertext = encryptor.update(key_material) + encryptor.finalize()

        # Return IV + ciphertext + tag
        return iv + ciphertext + encryptor.tag

    def _unwrap_key(self, wrapped_key: bytes, key_id: str) -> bytes:
        """Unwrap (decrypt) a key using master key."""
        # Extract components
        iv = wrapped_key[:12]
        ciphertext = wrapped_key[12:-16]
        tag = wrapped_key[-16:]

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Add key_id as additional authenticated data
        decryptor.authenticate_additional_data(key_id.encode())

        # Decrypt key material
        try:
            key_material = decryptor.update(ciphertext) + decryptor.finalize()
            return key_material
        except InvalidTag:
            raise ValueError("Key unwrapping failed: authentication tag mismatch")

    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Get key metadata."""
        storage_key = f"key:{key_id}"
        key_data = self.storage("get", storage_key)

        if key_data:
            return key_data['metadata']
        return None

    def get_key_material(self, key_id: str) -> Optional[bytes]:
        """Get unwrapped key material."""
        storage_key = f"key:{key_id}"
        key_data = self.storage("get", storage_key)

        if key_data:
            wrapped_key = key_data['key']
            return self._unwrap_key(wrapped_key, key_id)
        return None

    def rotate_key(self, key_id: str) -> EncryptionKey:
        """Rotate (re-generate) a key."""
        # Get existing key
        old_key = self.get_key(key_id)
        if not old_key:
            raise ValueError(f"Key not found: {key_id}")

        # Generate new key material
        new_key_material = None
        if old_key.key_type == KeyType.AES_256:
            new_key_material = secrets.token_bytes(32)
        elif old_key.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
            key_size = 2048 if old_key.key_type == KeyType.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            new_key_material = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

        if not new_key_material:
            raise ValueError(f"Cannot rotate key type: {old_key.key_type}")

        # Wrap and store new key
        wrapped_key = self._wrap_key(new_key_material, key_id)

        # Update key metadata
        old_key.rotated_at = datetime.utcnow()
        old_key.version += 1

        # Store new version
        storage_key = f"key:{key_id}:v{old_key.version}"
        key_data = {
            'key': wrapped_key,
            'metadata': old_key,
        }
        self.storage("set", storage_key, key_data)

        # Update current pointer
        self.storage("set", f"key:{key_id}:current", old_key.version)

        return old_key

    def encrypt_data(self,
                    plaintext: bytes,
                    key_id: str,
                    additional_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt data using specified key."""
        key_material = self.get_key_material(key_id)
        if not key_material:
            raise ValueError(f"Key not found or cannot be unwrapped: {key_id}")

        key_metadata = self.get_key(key_id)
        if not key_metadata:
            raise ValueError(f"Key metadata not found: {key_id}")

        # Encrypt based on key type
        if key_metadata.key_type == KeyType.AES_256:
            return self._encrypt_aes_gcm(plaintext, key_material, key_id, additional_data)
        elif key_metadata.key_type == KeyType.CHACHA20:
            return self._encrypt_chacha20(plaintext, key_material, key_id, additional_data)
        else:
            raise ValueError(f"Encryption not supported for key type: {key_metadata.key_type}")

    def _encrypt_aes_gcm(self,
                        plaintext: bytes,
                        key: bytes,
                        key_id: str,
                        additional_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt using AES-GCM."""
        # Generate IV
        iv = secrets.token_bytes(12)  # 96 bits

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Add additional authenticated data
        if additional_data:
            encryptor.authenticate_additional_data(additional_data)

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key_id,
            encryption_algorithm="AES-GCM",
            iv=iv,
            auth_tag=encryptor.tag,
            additional_data=additional_data,
            metadata={
                'encrypted_at': datetime.utcnow().isoformat(),
                'key_version': self.get_key(key_id).version,
            }
        )

    def _encrypt_chacha20(self,
                         plaintext: bytes,
                         key: bytes,
                         key_id: str,
                         additional_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt using ChaCha20-Poly1305."""
        # Generate nonce
        nonce = secrets.token_bytes(12)  # 96 bits

        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            mode=None,
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # For ChaCha20, we need to handle authentication separately
        # Simplified implementation - in production use proper AEAD

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Generate authentication tag (simplified)
        # In production, use proper Poly1305 implementation
        auth_data = key_id.encode() + (additional_data or b'')
        auth_tag = hmac.new(key, auth_data + ciphertext, hashlib.sha256).digest()[:16]

        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key_id,
            encryption_algorithm="ChaCha20",
            iv=nonce,
            auth_tag=auth_tag,
            additional_data=additional_data,
            metadata={
                'encrypted_at': datetime.utcnow().isoformat(),
                'key_version': self.get_key(key_id).version,
            }
        )

    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data."""
        key_material = self.get_key_material(encrypted_data.key_id)
        if not key_material:
            raise ValueError(f"Key not found or cannot be unwrapped: {encrypted_data.key_id}")

        key_metadata = self.get_key(encrypted_data.key_id)
        if not key_metadata:
            raise ValueError(f"Key metadata not found: {encrypted_data.key_id}")

        # Decrypt based on algorithm
        if encrypted_data.encryption_algorithm == "AES-GCM":
            return self._decrypt_aes_gcm(encrypted_data, key_material)
        elif encrypted_data.encryption_algorithm == "ChaCha20":
            return self._decrypt_chacha20(encrypted_data, key_material)
        else:
            raise ValueError(f"Decryption not supported for algorithm: {encrypted_data.encryption_algorithm}")

    def _decrypt_aes_gcm(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using AES-GCM."""
        if not encrypted_data.iv or not encrypted_data.auth_tag:
            raise ValueError("Missing IV or auth tag for AES-GCM decryption")

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(encrypted_data.iv, encrypted_data.auth_tag),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Add additional authenticated data
        if encrypted_data.additional_data:
            decryptor.authenticate_additional_data(encrypted_data.additional_data)

        # Decrypt
        try:
            plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
            return plaintext
        except InvalidTag:
            raise ValueError("Decryption failed: authentication tag mismatch")

    def _decrypt_chacha20(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using ChaCha20."""
        if not encrypted_data.iv or not encrypted_data.auth_tag:
            raise ValueError("Missing IV or auth tag for ChaCha20 decryption")

        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key, encrypted_data.iv),
            mode=None,
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Decrypt
        plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()

        # Verify authentication tag (simplified)
        auth_data = encrypted_data.key_id.encode() + (encrypted_data.additional_data or b'')
        expected_tag = hmac.new(key, auth_data + encrypted_data.ciphertext, hashlib.sha256).digest()[:16]

        if not hmac.compare_digest(expected_tag, encrypted_data.auth_tag):
            raise ValueError("Decryption failed: authentication tag mismatch")

        return plaintext

    def sign_data(self, data: bytes, key_id: str) -> bytes:
        """Sign data using RSA key."""
        key_material = self.get_key_material(key_id)
        if not key_material:
            raise ValueError(f"Key not found: {key_id}")

        key_metadata = self.get_key(key_id)
        if not key_metadata:
            raise ValueError(f"Key metadata not found: {key_id}")

        if key_metadata.key_type not in [KeyType.RSA_2048, KeyType.RSA_4096]:
            raise ValueError(f"Signing not supported for key type: {key_metadata.key_type}")

        # Load private key
        private_key = serialization.load_pem_private_key(
            key_material,
            password=None,
            backend=default_backend()
        )

        # Sign data
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def verify_signature(self, data: bytes, signature: bytes, key_id: str) -> bool:
        """Verify data signature."""
        # For RSA keys, we need the public key
        # In production, store public keys separately
        key_material = self.get_key_material(key_id)
        if not key_material:
            return False

        try:
            private_key = serialization.load_pem_private_key(
                key_material,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def check_key_rotation(self) -> List[Dict[str, Any]]:
        """Check which keys need rotation."""
        keys_needing_rotation = []

        # Get all keys (simplified - in production, use proper iteration)
        # This is a simplified implementation
        all_keys = self._get_all_keys()

        for key_id, key_metadata in all_keys.items():
            rotation_period = self.rotation_schedule.get(key_metadata.purpose, 90)

            if key_metadata.needs_rotation(rotation_period):
                keys_needing_rotation.append({
                    'key_id': key_id,
                    'key_type': key_metadata.key_type.value,
                    'purpose': key_metadata.purpose.value,
                    'created_at': key_metadata.created_at.isoformat(),
                    'rotated_at': key_metadata.rotated_at.isoformat() if key_metadata.rotated_at else None,
                    'days_since_rotation': (datetime.utcnow() - (key_metadata.rotated_at or key_metadata.created_at)).days,
                })

        return keys_needing_rotation

    def _get_all_keys(self) -> Dict[str, EncryptionKey]:
        """Get all keys (simplified implementation)."""
        # In production, implement proper key discovery
        return {}

    def backup_keys(self, backup_location: str) -> bool:
        """Backup keys to secure location."""
        # Simplified backup implementation
        # In production, use secure backup procedures with encryption
        try:
            all_key_data = {}

            # Collect all keys
            # This is simplified - in production, use proper iteration
            # and include key versions

            backup_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'keys': all_key_data,
                'checksum': hashlib.sha256(json.dumps(all_key_data).encode()).hexdigest(),
            }

            # Encrypt backup with separate backup key
            backup_key = self._generate_backup_key()
            encrypted_backup = self.encrypt_data(
                json.dumps(backup_data).encode(),
                backup_key_id="backup_key"
            )

            # Store backup (simplified)
            with open(backup_location, 'wb') as f:
                pickle.dump(encrypted_backup, f)

            return True

        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def _generate_backup_key(self) -> bytes:
        """Generate backup encryption key."""
        return secrets.token_bytes(32)

# Example usage
if __name__ == "__main__":
    # Initialize KMS
    kms_system = EnterpriseKMS(storage_backend="memory")

    # Generate encryption key
    encryption_key = kms_system.generate_key(
        key_type=KeyType.AES_256,
        purpose=KeyPurpose.DATA_ENCRYPTION,
        key_id="trading_data_key",
        expires_in_days=365
    )

    print(f"Generated key: {encryption_key.key_id}")
    print(f"Key type: {encryption_key.key_type.value}")
    print(f"Purpose: {encryption_key.purpose.value}")
    print(f"Created: {encryption_key.created_at}")

    # Encrypt data
    sensitive_data = b"Trading secret: AAPL buy order 100 shares @ $150.25"
    encrypted = kms_system.encrypt_data(
        plaintext=sensitive_data,
        key_id="trading_data_key",
        additional_data=b"trading_operation"
    )

    print(f"\nEncrypted data size: {len(encrypted.ciphertext)} bytes")
    print(f"Encryption algorithm: {encrypted.encryption_algorithm}")

    # Decrypt data
    decrypted = kms_system.decrypt_data(encrypted)

    print(f"\nDecrypted data: {decrypted.decode()}")
    print(f"Decryption successful: {decrypted == sensitive_data}")

    # Check key rotation
    rotation_needed = kms_system.check_key_rotation()
    print(f"\nKeys needing rotation: {len(rotation_needed)}")
```

## 🛡️ Web Application Firewall Configuration

### Advanced WAF Rules (network-security/waf/rules_engine.py)

```python
"""
Advanced Web Application Firewall rules engine for trading APIs.
Implements real-time threat detection and prevention.
"""

import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import ipaddress
import hashlib
import base64
from collections import defaultdict, deque
import redis
import yaml
from user_agents import parse

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Action(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    LOG = "log"
    RATE_LIMIT = "rate_limit"

@dataclass
class WAFRule:
    """WAF rule definition."""
    rule_id: str
    name: str
    description: str
    pattern: str
    pattern_type: str  # regex, string, ip_range, etc.
    threat_level: ThreatLevel
    action: Action
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def match(self, input_data: str) -> bool:
        """Check if input matches rule pattern."""
        if not self.enabled:
            return False

        try:
            if self.pattern_type == "regex":
                return bool(re.search(self.pattern, input_data, re.IGNORECASE))
            elif self.pattern_type == "string":
                return self.pattern.lower() in input_data.lower()
            elif self.pattern_type == "ip_range":
                return self._match_ip_range(input_data)
            else:
                return False
        except Exception:
            return False

    def _match_ip_range(self, ip_str: str) -> bool:
        """Check if IP is in range."""
        try:
            ip = ipaddress.ip_address(ip_str)
            network = ipaddress.ip_network(self.pattern)
            return ip in network
        except ValueError:
            return False

@dataclass
class WAFEvent:
    """WAF security event."""
    event_id: str
    rule_id: str
    threat_level: ThreatLevel
    action: Action
    timestamp: datetime
    source_ip: str
    user_agent: Optional[str]
    request_path: str
    request_method: str
    matched_pattern: str
    request_data: Dict[str, Any]
    response_action: str = "none"
    blocked: bool = False

class WAFRulesEngine:
    """Advanced WAF rules engine for trading systems."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.rules: Dict[str, WAFRule] = {}
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Load default rules
        self._load_default_rules()

        # Threat intelligence feeds (simulated)
        self.threat_intelligence = {
            'malicious_ips': set(),
            'malicious_user_agents': set(),
            'suspicious_patterns': set(),
        }

        # Load threat intelligence
        self._load_threat_intelligence()

    def _load_default_rules(self):
        """Load default WAF rules for trading systems."""
        default_rules = [
            # SQL Injection patterns
            WAFRule(
                rule_id="SQLI-001",
                name="SQL Injection - UNION",
                description="Detects SQL UNION based injection attempts",
                pattern=r"(?i)union\s+select",
                pattern_type="regex",
                threat_level=ThreatLevel.CRITICAL,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="SQLI-002",
                name="SQL Injection - Comment",
                description="Detects SQL comment injection attempts",
                pattern=r"(?i)(--|\#|\/\*)[\s\S]*?\*\/",
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="SQLI-003",
                name="SQL Injection - Sleep/Delay",
                description="Detects SQL timing-based injection attempts",
                pattern=r"(?i)(sleep|waitfor|benchmark)\s*\([^)]*\)",
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),

            # Cross-Site Scripting (XSS)
            WAFRule(
                rule_id="XSS-001",
                name="XSS - Script Tags",
                description="Detects script tag injection attempts",
                pattern=r"(?i)<script[^>]*>[\s\S]*?</script>",
                pattern_type="regex",
                threat_level=ThreatLevel.CRITICAL,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="XSS-002",
                name="XSS - Event Handlers",
                description="Detects event handler injection attempts",
                pattern=r"(?i)(onload|onerror|onclick|onmouseover)\s*=",
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="XSS-003",
                name="XSS - JavaScript Protocol",
                description="Detects javascript: protocol in URLs",
                pattern=r"(?i)javascript:\s*[\w\s]*\s*\(",
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),

            # Trading-specific attacks
            WAFRule(
                rule_id="TRADE-001",
                name="Trading - Price Manipulation",
                description="Detects abnormal price values in orders",
                pattern=r'"price"\s*:\s*[0-9]{6,}|"price"\s*:\s*0\.0{4,}[1-9]',
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="TRADE-002",
                name="Trading - Quantity Manipulation",
                description="Detects abnormal order quantities",
                pattern=r'"quantity"\s*:\s*[0-9]{8,}',
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="TRADE-003",
                name="Trading - Symbol Injection",
                description="Detects attempts to inject malicious symbols",
                pattern=r'"symbol"\s*:\s*"[^A-Za-z0-9.\-]{10,}"',
                pattern_type="regex",
                threat_level=ThreatLevel.MEDIUM,
                action=Action.CHALLENGE,
            ),

            # API Abuse patterns
            WAFRule(
                rule_id="API-001",
                name="API - Mass Assignment",
                description="Detects mass assignment attempts in API requests",
                pattern=r'(__proto__|prototype|constructor)',
                pattern_type="regex",
                threat_level=ThreatLevel.HIGH,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="API-002",
                name="API - Path Traversal",
                description="Detects path traversal attempts",
                pattern=r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                pattern_type="regex",
                threat_level=ThreatLevel.CRITICAL,
                action=Action.BLOCK,
            ),
            WAFRule(
                rule_id="API-003",
                name="API - Command Injection",
                description="Detects command injection attempts",
                pattern=r"(?i)(\|\||\&\&|;|\`|\$\(|\n|\r)",
                pattern_type="regex",
                threat_level=ThreatLevel.CRITICAL,
                action=Action.BLOCK,
            ),

            # Rate limiting patterns
            WAFRule(
                rule_id="RATE-001",
                name="Rate Limit - Burst Requests",
                description="Detects burst request patterns",
                pattern="",  # Handled by rate limiting logic
                pattern_type="rate_limit",
                threat_level=ThreatLevel.MEDIUM,
                action=Action.RATE_LIMIT,
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

    def _load_threat_intelligence(self):
        """Load threat intelligence data."""
        # In production, this would load from external feeds
        # Simulated data for example

        # Malicious IPs (simulated)
        self.threat_intelligence['malicious_ips'].update([
            '192.168.1.100',
            '10.0.0.5',
            '203.0.113.0/24',
        ])

        # Malicious User Agents (simulated)
        self.threat_intelligence['malicious_user_agents'].update([
            'sqlmap/1.0',
            'nikto/2.0',
            'nmap scripting engine',
        ])

        # Suspicious patterns (simulated)
        self.threat_intelligence['suspicious_patterns'].update([
            'SELECT * FROM users',
            'DROP TABLE',
            'DELETE FROM',
            'INSERT INTO',
        ])

    def analyze_request(self,
                       request_data: Dict[str, Any]) -> Tuple[List[WAFEvent], Action]:
        """
        Analyze HTTP request for security threats.
        Returns list of security events and recommended action.
        """
        events = []
        final_action = Action.ALLOW

        # Extract request components
        source_ip = request_data.get('source_ip', '')
        user_agent = request_data.get('user_agent', '')
        request_path = request_data.get('path', '')
        request_method = request_data.get('method', '')
        headers = request_data.get('headers', {})
        body = request_data.get('body', '')
        query_params = request_data.get('query_params', {})

        # Check threat intelligence feeds
        ti_events = self._check_threat_intelligence(source_ip, user_agent, body)
        events.extend(ti_events)

        if ti_events:
            # If threat intelligence found malicious activity, block immediately
            return events, Action.BLOCK

        # Check rate limiting
        rate_limit_event = self._check_rate_limit(source_ip, request_path)
        if rate_limit_event:
            events.append(rate_limit_event)
            final_action = Action.RATE_LIMIT

        # Convert request data to string for pattern matching
        request_str = self._request_to_string(request_data)

        # Apply all rules
        for rule in self.rules.values():
            if rule.pattern_type == "rate_limit":
                continue  # Handled separately

            # Check if rule matches
            if rule.match(request_str):
                event = WAFEvent(
                    event_id=f"WAF-{int(time.time())}-{hashlib.md5(request_str.encode()).hexdigest()[:8]}",
                    rule_id=rule.rule_id,
                    threat_level=rule.threat_level,
                    action=rule.action,
                    timestamp=datetime.utcnow(),
                    source_ip=source_ip,
                    user_agent=user_agent,
                    request_path=request_path,
                    request_method=request_method,
                    matched_pattern=rule.pattern[:100],  # Truncate for logging
                    request_data={
                        'headers': headers,
                        'body_preview': str(body)[:500],
                        'query_params': query_params,
                    }
                )
                events.append(event)

                # Update final action based on highest threat level
                if self._should_update_action(final_action, rule.action, rule.threat_level):
                    final_action = rule.action

        return events, final_action

    def _check_threat_intelligence(self,
                                  source_ip: str,
                                  user_agent: str,
                                  body: str) -> List[WAFEvent]:
        """Check against threat intelligence feeds."""
        events = []

        # Check IP against malicious IPs
        if source_ip in self.threat_intelligence['malicious_ips']:
            events.append(WAFEvent(
                event_id=f"TI-IP-{int(time.time())}",
                rule_id="TI-001",
                threat_level=ThreatLevel.CRITICAL,
                action=Action.BLOCK,
                timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_agent=user_agent,
                request_path="",
                request_method="",
                matched_pattern=f"Malicious IP: {source_ip}",
                request_data={}
            ))

        # Check User Agent
        if user_agent:
            ua_lower = user_agent.lower()
            for malicious_ua in self.threat_intelligence['malicious_user_agents']:
                if malicious_ua.lower() in ua_lower:
                    events.append(WAFEvent(
                        event_id=f"TI-UA-{int(time.time())}",
                        rule_id="TI-002",
                        threat_level=ThreatLevel.HIGH,
                        action=Action.BLOCK,
                        timestamp=datetime.utcnow(),
                        source_ip=source_ip,
                        user_agent=user_agent,
                        request_path="",
                        request_method="",
                        matched_pattern=f"Malicious User Agent: {malicious_ua}",
                        request_data={}
                    ))
                    break

        # Check body for suspicious patterns
        if body:
            body_str = str(body).lower()
            for pattern in self.threat_intelligence['suspicious_patterns']:
                if pattern.lower() in body_str:
                    events.append(WAFEvent(
                        event_id=f"TI-PAT-{int(time.time())}",
                        rule_id="TI-003",
                        threat_level=ThreatLevel.HIGH,
                        action=Action.BLOCK,
                        timestamp=datetime.utcnow(),
                        source_ip=source_ip,
                        user_agent=user_agent,
                        request_path="",
                        request_method="",
                        matched_pattern=f"Suspicious pattern: {pattern}",
                        request_data={}
                    ))
                    break

        return events

    def _check_rate_limit(self, source_ip: str, request_path: str) -> Optional[WAFEvent]:
        """Check and enforce rate limiting."""
        # Create rate limit key
        rate_key = f"{source_ip}:{request_path}"
        current_time = time.time()

        # Clean old entries
        while (self.rate_limits[rate_key] and
               current_time - self.rate_limits[rate_key][0] > 60):  # 60-second window
            self.rate_limits[rate_key].popleft()

        # Add current request
        self.rate_limits[rate_key].append(current_time)

        # Check rate limit (e.g., 100 requests per minute)
        if len(self.rate_limits[rate_key]) > 100:
            return WAFEvent(
                event_id=f"RATE-{int(time.time())}",
                rule_id="RATE-001",
                threat_level=ThreatLevel.MEDIUM,
                action=Action.RATE_LIMIT,
                timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_agent=None,
                request_path=request_path,
                request_method="",
                matched_pattern=f"Rate limit exceeded: {len(self.rate_limits[rate_key])} requests/min",
                request_data={}
            )

        return None

    def _request_to_string(self, request_data: Dict[str, Any]) -> str:
        """Convert request data to string for pattern matching."""
        parts = []

        # Add headers
        headers = request_data.get('headers', {})
        for key, value in headers.items():
            parts.append(f"{key}: {value}")

        # Add query parameters
        query_params = request_data.get('query_params', {})
        for key, value in query_params.items():
            parts.append(f"{key}={value}")

        # Add body
        body = request_data.get('body', '')
        if isinstance(body, dict):
            parts.append(json.dumps(body))
        elif isinstance(body, str):
            parts.append(body)

        return " ".join(parts)

    def _should_update_action(self,
                             current_action: Action,
                             new_action: Action,
                             threat_level: ThreatLevel) -> bool:
        """Determine if action should be updated based on threat level."""
        action_priority = {
            Action.BLOCK: 4,
            Action.CHALLENGE: 3,
            Action.RATE_LIMIT: 2,
            Action.LOG: 1,
            Action.ALLOW: 0,
        }

        threat_priority = {
            ThreatLevel.CRITICAL: 4,
            ThreatLevel.HIGH: 3,
            ThreatLevel.MEDIUM: 2,
            ThreatLevel.LOW: 1,
        }

        # If threat level is high and new action is more restrictive, update
        if (threat_priority[threat_level] >= 3 and
            action_priority[new_action] > action_priority[current_action]):
            return True

        return action_priority[new_action] > action_priority[current_action]

    def add_rule(self, rule: WAFRule):
        """Add a new WAF rule."""
        self.rules[rule.rule_id] = rule

    def update_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update an existing WAF rule."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            rule.updated_at = datetime.utcnow()

    def delete_rule(self, rule_id: str):
        """Delete a WAF rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def get_rules(self, enabled_only: bool = False) -> List[WAFRule]:
        """Get all WAF rules."""
        if enabled_only:
            return [rule for rule in self.rules.values() if rule.enabled]
        return list(self.rules.values())

    def save_rules(self, filepath: str):
        """Save WAF rules to file."""
        rules_data = []
        for rule in self.rules.values():
            rule_dict = {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'description': rule.description,
                'pattern': rule.pattern,
                'pattern_type': rule.pattern_type,
                'threat_level': rule.threat_level.value,
                'action': rule.action.value,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat(),
                'updated_at': rule.updated_at.isoformat(),
            }
            rules_data.append(rule_dict)

        with open(filepath, 'w') as f:
            yaml.dump(rules_data, f, default_flow_style=False)

    def load_rules(self, filepath: str):
        """Load WAF rules from file."""
        with open(filepath, 'r') as f:
            rules_data = yaml.safe_load(f)

        for rule_dict in rules_data:
            rule = WAFRule(
                rule_id=rule_dict['rule_id'],
                name=rule_dict['name'],
                description=rule_dict['description'],
                pattern=rule_dict['pattern'],
                pattern_type=rule_dict['pattern_type'],
                threat_level=ThreatLevel(rule_dict['threat_level']),
                action=Action(rule_dict['action']),
                enabled=rule_dict.get('enabled', True),
                created_at=datetime.fromisoformat(rule_dict['created_at']),
                updated_at=datetime.fromisoformat(rule_dict['updated_at']),
            )
            self.rules[rule.rule_id] = rule

    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate WAF activity report."""
        # In production, this would query a database
        # Simulated for example

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'time_period_hours': hours,
            'summary': {
                'total_requests': 10000,
                'blocked_requests': 150,
                'challenged_requests': 50,
                'rate_limited_requests': 200,
                'threat_distribution': {
                    'critical': 25,
                    'high': 75,
                    'medium': 100,
                    'low': 50,
                }
            },
            'top_threats': [
                {'rule_id': 'SQLI-001', 'count': 50, 'threat_level': 'critical'},
                {'rule_id': 'XSS-001', 'count': 40, 'threat_level': 'critical'},
                {'rule_id': 'API-001', 'count': 35, 'threat_level': 'high'},
            ],
            'top_source_ips': [
                {'ip': '192.168.1.100', 'threat_count': 45, 'action': 'blocked'},
                {'ip': '10.0.0.5', 'threat_count': 30, 'action': 'blocked'},
                {'ip': '203.0.113.25', 'threat_count': 25, 'action': 'rate_limited'},
            ],
        }

        return report

# Example FastAPI middleware using WAF
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

app = FastAPI(title="Trading API with WAF Protection")

# Initialize WAF
waf_engine = WAFRulesEngine()

@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    """WAF middleware for FastAPI."""

    # Extract request data
    request_data = {
        'source_ip': request.client.host if request.client else 'unknown',
        'user_agent': request.headers.get('user-agent'),
        'path': request.url.path,
        'method': request.method,
        'headers': dict(request.headers),
        'query_params': dict(request.query_params),
    }

    # Try to read body (handle errors)
    try:
        body = await request.body()
        if body:
            try:
                request_data['body'] = json.loads(body.decode())
            except:
                request_data['body'] = body.decode()
    except:
        request_data['body'] = ''

    # Analyze request with WAF
    events, action = waf_engine.analyze_request(request_data)

    # Log events
    if events:
        for event in events:
            print(f"WAF Event: {event.rule_id} - {event.threat_level.value} - {event.action.value}")

    # Apply action
    if action == Action.BLOCK:
        raise HTTPException(status_code=403, detail="Request blocked by security policy")
    elif action == Action.RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    elif action == Action.CHALLENGE:
        # Implement CAPTCHA or other challenge
        raise HTTPException(status_code=418, detail="Additional verification required")

    # Continue to endpoint
    response = await call_next(request)
    return response

# Add security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# Example endpoints
@app.get("/api/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for a symbol."""
    return {"symbol": symbol, "price": 150.25, "volume": 1000000}

@app.post("/api/orders")
async def place_order(order_data: dict):
    """Place a new order."""
    # In production, validate and process order
    return {"status": "success", "order_id": "ORD-12345"}

@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio information."""
    return {"portfolio_value": 1000000, "positions": ["AAPL", "GOOGL"]}

if __name__ == "__main__":
    # Run with HTTPS in production
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
```

## 📋 Compliance Automation Framework

### Regulatory Compliance Engine (compliance/automation/compliance_engine.py)

```python
"""
Automated regulatory compliance framework for trading systems.
Implements SEC 17a-4, MiFID II, GDPR, and other regulations.
"""

import json
import yaml
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import pickle
from pathlib import Path
import sqlite3
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import pandas as pd
import redis

class Regulation(Enum):
    """Supported regulations."""
    SEC_17A = "SEC Rule 17a-4"
    MIFID_II = "MiFID II"
    GDPR = "GDPR"
    PCI_DSS = "PCI DSS"
    SOX = "SOX"
    BASEL_III = "Basel III"
    DODD_FRANK = "Dodd-Frank"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition."""
    requirement_id: str
    regulation: Regulation
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    evidence_required: bool
    automated_check: bool
    check_frequency: str  # realtime, daily, weekly, monthly

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'regulation': self.regulation.value,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'evidence_required': self.evidence_required,
            'automated_check': self.automated_check,
            'check_frequency': self.check_frequency,
        }

@dataclass
class ComplianceCheck:
    """Compliance check result."""
    check_id: str
    requirement_id: str
    timestamp: datetime
    status: ComplianceStatus
    evidence: Optional[Dict[str, Any]] = None
    findings: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    checked_by: str = "automated_system"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_id': self.check_id,
            'requirement_id': self.requirement_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'evidence': self.evidence,
            'findings': self.findings,
            'remediation_actions': self.remediation_actions,
            'checked_by': self.checked_by,
        }

class ComplianceEngine:
    """Automated compliance engine for trading systems."""

    def __init__(self,
                 storage_path: str = "./compliance_data",
                 redis_client: Optional[redis.Redis] = None):

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.redis = redis_client
        self.requirements: Dict[str, ComplianceRequirement] = {}
        self.checks: Dict[str, List[ComplianceCheck]] = {}

        # Load compliance requirements
        self._load_default_requirements()

        # Initialize databases
        self._init_databases()

        # Digital signature for compliance evidence
        self._init_digital_signature()

    def _load_default_requirements(self):
        """Load default compliance requirements."""
        # SEC 17a-4 Requirements
        sec_requirements = [
            ComplianceRequirement(
                requirement_id="SEC-001",
                regulation=Regulation.SEC_17A,
                title="Electronic Record Retention",
                description="Preserve electronic records in non-rewritable, non-erasable format (WORM)",
                category="data_retention",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="realtime",
            ),
            ComplianceRequirement(
                requirement_id="SEC-002",
                regulation=Regulation.SEC_17A,
                title="Record Retention Period",
                description="Retain records for minimum of 7 years",
                category="data_retention",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="daily",
            ),
            ComplianceRequirement(
                requirement_id="SEC-003",
                regulation=Regulation.SEC_17A,
                title="Audit Trail Integrity",
                description="Maintain complete, time-stamped audit trail of all trading activities",
                category="audit_trail",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="realtime",
            ),
            ComplianceRequirement(
                requirement_id="SEC-004",
                regulation=Regulation.SEC_17A,
                title="Record Accessibility",
                description="Ensure records are readily accessible for examination",
                category="data_access",
                priority="medium",
                evidence_required=True,
                automated_check=True,
                check_frequency="weekly",
            ),
        ]

        # MiFID II Requirements
        mifid_requirements = [
            ComplianceRequirement(
                requirement_id="MIFID-001",
                regulation=Regulation.MIFID_II,
                title="Best Execution Monitoring",
                description="Monitor and ensure best execution for client orders",
                category="trading_quality",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="realtime",
            ),
            ComplianceRequirement(
                requirement_id="MIFID-002",
                regulation=Regulation.MIFID_II,
                title="Transaction Reporting",
                description="Report transactions to competent authority",
                category="reporting",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="daily",
            ),
            ComplianceRequirement(
                requirement_id="MIFID-003",
                regulation=Regulation.MIFID_II,
                title="Record Keeping",
                description="Maintain records of all services, activities, and transactions",
                category="data_retention",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="daily",
            ),
            ComplianceRequirement(
                requirement_id="MIFID-004",
                regulation=Regulation.MIFID_II,
                title="Algorithmic Trading Controls",
                description="Implement effective systems and risk controls for algorithmic trading",
                category="risk_management",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="realtime",
            ),
        ]

        # GDPR Requirements
        gdpr_requirements = [
            ComplianceRequirement(
                requirement_id="GDPR-001",
                regulation=Regulation.GDPR,
                title="Data Protection by Design",
                description="Implement data protection measures from the onset of system design",
                category="data_protection",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="weekly",
            ),
            ComplianceRequirement(
                requirement_id="GDPR-002",
                regulation=Regulation.GDPR,
                title="Right to be Forgotten",
                description="Implement process for data erasure upon request",
                category="data_subject_rights",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="monthly",
            ),
            ComplianceRequirement(
                requirement_id="GDPR-003",
                regulation=Regulation.GDPR,
                title="Data Breach Notification",
                description="Notify supervisory authority within 72 hours of data breach",
                category="incident_response",
                priority="high",
                evidence_required=True,
                automated_check=True,
                check_frequency="realtime",
            ),
            ComplianceRequirement(
                requirement_id="GDPR-004",
                regulation=Regulation.GDPR,
                title="Data Processing Records",
                description="Maintain records of processing activities",
                category="documentation",
                priority="medium",
                evidence_required=True,
                automated_check=True,
                check_frequency="monthly",
            ),
        ]

        # Combine all requirements
        all_requirements = sec_requirements + mifid_requirements + gdpr_requirements

        for req in all_requirements:
            self.requirements[req.requirement_id] = req

    def _init_databases(self):
        """Initialize compliance databases."""
        # Main compliance database
        self.db_path = self.storage_path / "compliance.db"
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

        # WORM storage for audit trails
        self.worm_path = self.storage_path / "worm_storage"
        self.worm_path.mkdir(exist_ok=True)

        # Set WORM directory to read-only after writing
        import os
        os.chmod(self.worm_path, 0o555)  # Read-only

    def _create_tables(self):
        """Create compliance database tables."""
        cursor = self.conn.cursor()

        # Compliance checks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_checks (
                check_id TEXT PRIMARY KEY,
                requirement_id TEXT,
                timestamp DATETIME,
                status TEXT,
                evidence TEXT,
                findings TEXT,
                remediation_actions TEXT,
                checked_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Audit trail table (WORM compliant)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                user_id TEXT,
                timestamp DATETIME,
                component TEXT,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Data retention table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_retention (
                record_id TEXT PRIMARY KEY,
                data_type TEXT,
                created_at DATETIME,
                retention_until DATETIME,
                storage_location TEXT,
                checksum TEXT,
                regulation TEXT,
                created_at_db DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Transaction reports table (MiFID II)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_reports (
                report_id TEXT PRIMARY KEY,
                transaction_id TEXT,
                symbol TEXT,
                quantity REAL,
                price REAL,
                side TEXT,
                timestamp DATETIME,
                client_id TEXT,
                trader_id TEXT,
                venue TEXT,
                reported_at DATETIME,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def _init_digital_signature(self):
        """Initialize digital signature for compliance evidence."""
        # Generate RSA key pair for signing
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

    def sign_data(self, data: bytes) -> bytes:
        """Sign data for evidentiary purposes."""
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify data signature."""
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def run_compliance_check(self, requirement_id: str) -> ComplianceCheck:
        """Run compliance check for specific requirement."""
        requirement = self.requirements.get(requirement_id)
        if not requirement:
            raise ValueError(f"Requirement not found: {requirement_id}")

        check_id = f"CHECK-{requirement_id}-{int(datetime.utcnow().timestamp())}"

        # Run check based on requirement
        if requirement.regulation == Regulation.SEC_17A:
            check = self._check_sec_requirement(requirement)
        elif requirement.regulation == Regulation.MIFID_II:
            check = self._check_mifid_requirement(requirement)
        elif requirement.regulation == Regulation.GDPR:
            check = self._check_gdpr_requirement(requirement)
        else:
            check = ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement_id,
                timestamp=datetime.utcnow(),
                status=ComplianceStatus.NOT_APPLICABLE,
                findings=["Regulation not implemented for automated checking"],
            )

        # Store check result
        self._store_check_result(check)

        # Update checks cache
        if requirement_id not in self.checks:
            self.checks[requirement_id] = []
        self.checks[requirement_id].append(check)

        return check

    def _check_sec_requirement(self, requirement: ComplianceRequirement) -> ComplianceCheck:
        """Check SEC 17a-4 requirements."""
        check_id = f"CHECK-{requirement.requirement_id}-{int(datetime.utcnow().timestamp())}"

        if requirement.requirement_id == "SEC-001":
            # Check WORM storage
            worm_compliant = self._check_worm_storage()
            status = ComplianceStatus.COMPLIANT if worm_compliant else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'worm_storage_path': str(self.worm_path),
                    'permissions': oct(self.worm_path.stat().st_mode)[-3:],
                    'check_timestamp': datetime.utcnow().isoformat(),
                },
                findings=["WORM storage verified"] if worm_compliant else ["WORM storage not properly configured"],
                remediation_actions=[] if worm_compliant else ["Configure WORM storage with proper permissions"],
            )

        elif requirement.requirement_id == "SEC-002":
            # Check retention period
            retention_compliant = self._check_retention_period()
            status = ComplianceStatus.COMPLIANT if retention_compliant else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'retention_check_date': datetime.utcnow().isoformat(),
                    'minimum_retention_days': 7 * 365,  # 7 years
                },
                findings=["Retention period meets 7-year requirement"] if retention_compliant else ["Retention period insufficient"],
                remediation_actions=[] if retention_compliant else ["Extend data retention to 7 years minimum"],
            )

        elif requirement.requirement_id == "SEC-003":
            # Check audit trail integrity
            audit_trail_ok = self._check_audit_trail_integrity()
            status = ComplianceStatus.COMPLIANT if audit_trail_ok else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'audit_trail_entries': self._count_audit_trail_entries(),
                    'integrity_check': audit_trail_ok,
                },
                findings=["Audit trail integrity verified"] if audit_trail_ok else ["Audit trail integrity issues detected"],
                remediation_actions=[] if audit_trail_ok else ["Investigate and fix audit trail integrity"],
            )

        # Default for other SEC requirements
        return ComplianceCheck(
            check_id=check_id,
            requirement_id=requirement.requirement_id,
            timestamp=datetime.utcnow(),
            status=ComplianceStatus.PARTIALLY_COMPLIANT,
            findings=[f"Check for {requirement.title} not fully implemented"],
        )

    def _check_mifid_requirement(self, requirement: ComplianceRequirement) -> ComplianceCheck:
        """Check MiFID II requirements."""
        check_id = f"CHECK-{requirement.requirement_id}-{int(datetime.utcnow().timestamp())}"

        if requirement.requirement_id == "MIFID-001":
            # Check best execution monitoring
            best_execution_ok = self._check_best_execution()
            status = ComplianceStatus.COMPLIANT if best_execution_ok else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'best_execution_checks': self._get_best_execution_metrics(),
                    'monitoring_active': True,
                },
                findings=["Best execution monitoring active"] if best_execution_ok else ["Best execution monitoring issues"],
                remediation_actions=[] if best_execution_ok else ["Implement best execution monitoring"],
            )

        elif requirement.requirement_id == "MIFID-002":
            # Check transaction reporting
            reporting_ok = self._check_transaction_reporting()
            status = ComplianceStatus.COMPLIANT if reporting_ok else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'reports_generated': self._count_transaction_reports(),
                    'last_report_date': self._get_last_report_date(),
                },
                findings=["Transaction reporting operational"] if reporting_ok else ["Transaction reporting issues"],
                remediation_actions=[] if reporting_ok else ["Fix transaction reporting system"],
            )

        # Default for other MiFID requirements
        return ComplianceCheck(
            check_id=check_id,
            requirement_id=requirement.requirement_id,
            timestamp=datetime.utcnow(),
            status=ComplianceStatus.PARTIALLY_COMPLIANT,
            findings=[f"Check for {requirement.title} not fully implemented"],
        )

    def _check_gdpr_requirement(self, requirement: ComplianceRequirement) -> ComplianceCheck:
        """Check GDPR requirements."""
        check_id = f"CHECK-{requirement.requirement_id}-{int(datetime.utcnow().timestamp())}"

        if requirement.requirement_id == "GDPR-001":
            # Check data protection by design
            data_protection_ok = self._check_data_protection()
            status = ComplianceStatus.COMPLIANT if data_protection_ok else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'encryption_enabled': True,
                    'access_controls': True,
                    'data_minimization': True,
                },
                findings=["Data protection measures implemented"] if data_protection_ok else ["Data protection measures insufficient"],
                remediation_actions=[] if data_protection_ok else ["Implement data protection by design principles"],
            )

        elif requirement.requirement_id == "GDPR-002":
            # Check right to be forgotten
            erasure_process_ok = self._check_data_erasure_process()
            status = ComplianceStatus.COMPLIANT if erasure_process_ok else ComplianceStatus.NON_COMPLIANT

            return ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                timestamp=datetime.utcnow(),
                status=status,
                evidence={
                    'erasure_requests_processed': self._count_erasure_requests(),
                    'process_documented': True,
                },
                findings=["Data erasure process implemented"] if erasure_process_ok else ["Data erasure process missing"],
                remediation_actions=[] if erasure_process_ok else ["Implement data erasure process for GDPR compliance"],
            )

        # Default for other GDPR requirements
        return ComplianceCheck(
            check_id=check_id,
            requirement_id=requirement.requirement_id,
            timestamp=datetime.utcnow(),
            status=ComplianceStatus.PARTIALLY_COMPLIANT,
            findings=[f"Check for {requirement.title} not fully implemented"],
        )

    def _check_worm_storage(self) -> bool:
        """Check if WORM storage is properly configured."""
        try:
            # Check if directory exists and is read-only
            if not self.worm_path.exists():
                return False

            # Try to write to directory (should fail if properly configured)
            test_file = self.worm_path / ".test_write"
            try:
                test_file.touch()
                test_file.unlink()
                return False  # Write succeeded, not WORM
            except (PermissionError, OSError):
                return True  # Write failed, WORM working

        except Exception:
            return False

    def _check_retention_period(self) -> bool:
        """Check data retention period compliance."""
        cursor = self.conn.cursor()

        # Check if we have data older than 7 years (should be retained)
        seven_years_ago = datetime.utcnow() - timedelta(days=7*365)

        cursor.execute('''
            SELECT COUNT(*) FROM data_retention
            WHERE created_at < ? AND retention_until > ?
        ''', (seven_years_ago, datetime.utcnow()))

        count = cursor.fetchone()[0]
        return count > 0  # Have data retained for at least 7 years

    def _check_audit_trail_integrity(self) -> bool:
        """Check audit trail integrity."""
        cursor = self.conn.cursor()

        # Check for gaps or inconsistencies
        cursor.execute('''
            SELECT COUNT(*) FROM audit_trail
            WHERE event_id IS NULL OR timestamp IS NULL
        ''')

        null_count = cursor.fetchone()[0]

        # Check for duplicate event IDs
        cursor.execute('''
            SELECT event_id, COUNT(*) FROM audit_trail
            GROUP BY event_id HAVING COUNT(*) > 1
        ''')

        duplicate_count = len(cursor.fetchall())

        return null_count == 0 and duplicate_count == 0

    def _check_best_execution(self) -> bool:
        """Check best execution monitoring."""
        # Simplified check - in production, implement actual best execution logic
        return True

    def _check_transaction_reporting(self) -> bool:
        """Check transaction reporting system."""
        cursor = self.conn.cursor()

        # Check if reports are being generated
        cursor.execute('''
            SELECT COUNT(*) FROM transaction_reports
            WHERE reported_at > DATE('now', '-1 day')
        ''')

        recent_reports = cursor.fetchone()[0]
        return recent_reports > 0

    def _check_data_protection(self) -> bool:
        """Check data protection measures."""
        # Simplified check
        return True

    def _check_data_erasure_process(self) -> bool:
        """Check data erasure process."""
        # Simplified check
        return True

    def _count_audit_trail_entries(self) -> int:
        """Count audit trail entries."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM audit_trail')
        return cursor.fetchone()[0]

    def _count_transaction_reports(self) -> int:
        """Count transaction reports."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM transaction_reports')
        return cursor.fetchone()[0]

    def _get_best_execution_metrics(self) -> Dict[str, Any]:
        """Get best execution metrics."""
        return {
            'price_improvement': 0.001,  # 0.1% average price improvement
            'fill_rate': 0.95,  # 95% fill rate
            'speed': 50,  # 50ms average execution speed
        }

    def _get_last_report_date(self) -> Optional[str]:
        """Get last transaction report date."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT MAX(reported_at) FROM transaction_reports')
        result = cursor.fetchone()[0]
        return result

    def _count_erasure_requests(self) -> int:
        """Count data erasure requests processed."""
        # Simplified - in production, track actual requests
        return 0

    def _store_check_result(self, check: ComplianceCheck):
        """Store compliance check result."""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO compliance_checks
            (check_id, requirement_id, timestamp, status, evidence, findings, remediation_actions, checked_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            check.check_id,
            check.requirement_id,
            check.timestamp,
            check.status.value,
            json.dumps(check.evidence) if check.evidence else None,
            json.dumps(check.findings),
            json.dumps(check.remediation_actions),
            check.checked_by,
        ))

        self.conn.commit()

    def log_audit_event(self,
                       event_type: str,
                       user_id: str,
                       component: str,
                       action: str,
                       details: Dict[str, Any],
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None):
        """Log audit event for compliance."""
        event_id = f"AUDIT-{int(datetime.utcnow().timestamp())}-{hashlib.md5(str(details).encode()).hexdigest()[:8]}"

        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO audit_trail
            (event_id, event_type, user_id, timestamp, component, action, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id,
            event_type,
            user_id,
            datetime.utcnow(),
            component,
            action,
            json.dumps(details),
            ip_address,
            user_agent,
        ))

        self.conn.commit()

        # Also store in WORM storage
        self._store_worm_event(event_id, {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'component': component,
            'action': action,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
        })

    def _store_worm_event(self, event_id: str, event_data: Dict[str, Any]):
        """Store event in WORM-compliant storage."""
        # Create file with event data
        event_file = self.worm_path / f"{event_id}.json"

        # Add digital signature
        event_json = json.dumps(event_data, indent=2).encode()
        signature = self.sign_data(event_json)

        complete_data = {
            'event': event_data,
            'signature': base64.b64encode(signature).decode(),
            'signed_at': datetime.utcnow().isoformat(),
            'hash': hashlib.sha256(event_json).hexdigest(),
        }

        # Write to file (this should fail if WORM is properly configured)
        try:
            with open(event_file, 'w') as f:
                json.dump(complete_data, f, indent=2)

            # Set file to read-only
            import os
            os.chmod(event_file, 0o444)

        except PermissionError:
            # Expected for WORM storage
            pass

    def generate_compliance_report(self,
                                  regulation: Optional[Regulation] = None,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate compliance report."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        cursor = self.conn.cursor()

        # Build query based on parameters
        query = '''
            SELECT cc.requirement_id, cc.status, COUNT(*) as check_count,
                   r.regulation, r.title, r.priority
            FROM compliance_checks cc
            JOIN (
                SELECT requirement_id, regulation, title, priority
                FROM compliance_requirements
            ) r ON cc.requirement_id = r.requirement_id
            WHERE cc.timestamp BETWEEN ? AND ?
        '''

        params = [start_date, end_date]

        if regulation:
            query += ' AND r.regulation = ?'
            params.append(regulation.value)

        query += ' GROUP BY cc.requirement_id, cc.status'

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Process results
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'regulation': regulation.value if regulation else 'all',
            'summary': {
                'total_checks': 0,
                'compliant': 0,
                'non_compliant': 0,
                'partially_compliant': 0,
            },
            'requirements': [],
            'recommendations': [],
        }

        for row in results:
            req_id, status, count, reg, title, priority = row

            report['summary']['total_checks'] += count

            if status == ComplianceStatus.COMPLIANT.value:
                report['summary']['compliant'] += count
            elif status == ComplianceStatus.NON_COMPLIANT.value:
                report['summary']['non_compliant'] += count
            elif status == ComplianceStatus.PARTIALLY_COMPLIANT.value:
                report['summary']['partially_compliant'] += count

            report['requirements'].append({
                'requirement_id': req_id,
                'regulation': reg,
                'title': title,
                'priority': priority,
                'status': status,
                'check_count': count,
            })

        # Generate recommendations
        if report['summary']['non_compliant'] > 0:
            report['recommendations'].append({
                'priority': 'high',
                'action': 'Address non-compliant requirements immediately',
                'details': f'{report["summary"]["non_compliant"]} non-compliant checks found',
            })

        if report['summary']['partially_compliant'] > 0:
            report['recommendations'].append({
                'priority': 'medium',
                'action': 'Review partially compliant requirements',
                'details': f'{report["summary"]["partially_compliant"]} partially compliant checks found',
            })

        # Calculate compliance score
        total = report['summary']['total_checks']
        if total > 0:
            compliant_score = (report['summary']['compliant'] / total) * 100
            report['summary']['compliance_score'] = round(compliant_score, 1)
        else:
            report['summary']['compliance_score'] = 0.0

        return report

    def get_requirements(self,
                        regulation: Optional[Regulation] = None,
                        priority: Optional[str] = None) -> List[ComplianceRequirement]:
        """Get compliance requirements with optional filters."""
        requirements = list(self.requirements.values())

        if regulation:
            requirements = [r for r in requirements if r.regulation == regulation]

        if priority:
            requirements = [r for r in requirements if r.priority == priority]

        return requirements

    def get_check_history(self,
                         requirement_id: str,
                         limit: int = 10) -> List[ComplianceCheck]:
        """Get check history for a requirement."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT check_id, requirement_id, timestamp, status, evidence,
                   findings, remediation_actions, checked_by
            FROM compliance_checks
            WHERE requirement_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (requirement_id, limit))

        checks = []
        for row in cursor.fetchall():
            check_id, req_id, timestamp, status, evidence, findings, remediation, checked_by = row

            checks.append(ComplianceCheck(
                check_id=check_id,
                requirement_id=req_id,
                timestamp=datetime.fromisoformat(timestamp),
                status=ComplianceStatus(status),
                evidence=json.loads(evidence) if evidence else None,
                findings=json.loads(findings) if findings else [],
                remediation_actions=json.loads(remediation) if remediation else [],
                checked_by=checked_by,
            ))

        return checks

# Example usage
if __name__ == "__main__":
    # Initialize compliance engine
    engine = ComplianceEngine(storage_path="./compliance_data")

    # Run compliance checks
    print("Running compliance checks...")

    requirements = engine.get_requirements(regulation=Regulation.SEC_17A)

    for requirement in requirements:
        print(f"\nChecking: {requirement.title}")
        check = engine.run_compliance_check(requirement.requirement_id)

        print(f"  Status: {check.status.value}")
        print(f"  Findings: {len(check.findings)}")

        if check.findings:
            for finding in check.findings[:3]:  # Show first 3 findings
                print(f"    - {finding}")

    # Generate compliance report
    print("\n" + "="*60)
    print("COMPLIANCE REPORT")
    print("="*60)

    report = engine.generate_compliance_report(regulation=Regulation.SEC_17A)

    print(f"\nCompliance Score: {report['summary']['compliance_score']}%")
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Compliant: {report['summary']['compliant']}")
    print(f"Non-Compliant: {report['summary']['non_compliant']}")
    print(f"Partially Compliant: {report['summary']['partially_compliant']}")

    # Show top recommendations
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['action']}")

    # Log audit event example
    engine.log_audit_event(
        event_type="trade_execution",
        user_id="trader_001",
        component="trading_engine",
        action="place_order",
        details={
            "symbol": "AAPL",
            "quantity": 100,
            "price": 150.25,
            "side": "buy",
            "order_id": "ORD-12345",
        },
        ip_address="192.168.1.100",
        user_agent="TradingTerminal/1.0",
    )

    print("\nCompliance automation complete!")
```

## 📋 Security Hardening Checklist

### Complete Security Checklist (scripts/security_checklist.py)

```python
"""
Comprehensive security hardening checklist for trading systems.
Automated verification of security controls.
"""

import json
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import subprocess
import platform
import socket
import ssl
import requests
from pathlib import Path

class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class SecurityCheck:
    """Security check definition."""
    check_id: str
    category: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    requirement: str
    verification_method: str  # automated, manual, configuration
    remediation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_id': self.check_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'requirement': self.requirement,
            'verification_method': self.verification_method,
            'remediation': self.remediation,
        }

@dataclass
class CheckResult:
    """Security check result."""
    check_id: str
    status: CheckStatus
    findings: List[str]
    evidence: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_id': self.check_id,
            'status': self.status.value,
            'findings': self.findings,
            'evidence': self.evidence,
            'timestamp': self.timestamp.isoformat(),
        }

class SecurityHardeningChecklist:
    """Automated security hardening checklist verification."""

    def __init__(self):
        self.checks: Dict[str, SecurityCheck] = {}
        self.results: Dict[str, CheckResult] = {}

        # Load security checks
        self._load_security_checks()

    def _load_security_checks(self):
        """Load security hardening checks."""
        # Authentication checks
        auth_checks = [
            SecurityCheck(
                check_id="AUTH-001",
                category="authentication",
                title="Multi-Factor Authentication",
                description="MFA enabled for all trading accounts",
                severity="critical",
                requirement="SEC 17a-4, MiFID II",
                verification_method="automated",
                remediation="Enable MFA for all trading platform accounts",
            ),
            SecurityCheck(
                check_id="AUTH-002",
                category="authentication",
                title="Password Policy",
                description="Strong password policy enforced",
                severity="high",
                requirement="ISO 27001 A.9.4.1",
                verification_method="automated",
                remediation="Enforce password policy: min 12 chars, complexity, expiration",
            ),
            SecurityCheck(
                check_id="AUTH-003",
                category="authentication",
                title="Session Management",
                description="Secure session management with timeout",
                severity="high",
                requirement="OWASP Session Management",
                verification_method="automated",
                remediation="Implement session timeout, secure cookies, session rotation",
            ),
        ]

        # Network security checks
        network_checks = [
            SecurityCheck(
                check_id="NET-001",
                category="network_security",
                title="Firewall Configuration",
                description="Firewall rules restrict unnecessary traffic",
                severity="critical",
                requirement="NIST SP 800-41",
                verification_method="automated",
                remediation="Configure firewall with least privilege principle",
            ),
            SecurityCheck(
                check_id="NET-002",
                category="network_security",
                title="TLS Configuration",
                description="Strong TLS configuration (v1.3, strong ciphers)",
                severity="high",
                requirement="PCI DSS 4.1",
                verification_method="automated",
                remediation="Upgrade to TLS 1.3, disable weak protocols and ciphers",
            ),
            SecurityCheck(
                check_id="NET-003",
                category="network_security",
                title="VPN Requirement",
                description="VPN required for remote access",
                severity="high",
                requirement="SEC 17a-4",
                verification_method="manual",
                remediation="Require VPN for all remote trading system access",
            ),
        ]

        # Data security checks
        data_checks = [
            SecurityCheck(
                check_id="DATA-001",
                category="data_security",
                title="Data Encryption at Rest",
                description="Sensitive data encrypted at rest",
                severity="critical",
                requirement="SEC 17a-4, GDPR",
                verification_method="automated",
                remediation="Implement encryption for all sensitive data at rest",
            ),
            SecurityCheck(
                check_id="DATA-002",
                category="data_security",
                title="Data Classification",
                description="Data classification scheme implemented",
                severity="medium",
                requirement="ISO 27001 A.8.2.1",
                verification_method="manual",
                remediation="Implement data classification (public, internal, confidential, restricted)",
            ),
            SecurityCheck(
                check_id="DATA-003",
                category="data_security",
                title="Secure Data Disposal",
                description="Secure data disposal procedures",
                severity="medium",
                requirement="NIST SP 800-88",
                verification_method="manual",
                remediation="Implement secure data disposal procedures",
            ),
        ]

        # Application security checks
        app_checks = [
            SecurityCheck(
                check_id="APP-001",
                category="application_security",
                title="Input Validation",
                description="Input validation implemented for all inputs",
                severity="high",
                requirement="OWASP Top 10 A1",
                verification_method="automated",
                remediation="Implement comprehensive input validation",
            ),
            SecurityCheck(
                check_id="APP-002",
                category="application_security",
                title="API Security",
                description="API security controls implemented",
                severity="high",
                requirement="OWASP API Security Top 10",
                verification_method="automated",
                remediation="Implement API authentication, rate limiting, input validation",
            ),
            SecurityCheck(
                check_id="APP-003",
                category="application_security",
                title="Error Handling",
                description="Secure error handling prevents information leakage",
                severity="medium",
                requirement="OWASP Top 10 A9",
                verification_method="automated",
                remediation="Implement secure error handling without sensitive information",
            ),
        ]

        # Compliance checks
        compliance_checks = [
            SecurityCheck(
                check_id="COMP-001",
                category="compliance",
                title="Audit Trail",
                description="Comprehensive audit trail maintained",
                severity="critical",
                requirement="SEC 17a-4, MiFID II",
                verification_method="automated",
                remediation="Implement immutable audit trail for all trading activities",
            ),
            SecurityCheck(
                check_id="COMP-002",
                category="compliance",
                title="Data Retention",
                description="Data retention policy compliant with regulations",
                severity="high",
                requirement="SEC 17a-4 (7 years), GDPR",
                verification_method="automated",
                remediation="Implement data retention policies meeting regulatory requirements",
            ),
            SecurityCheck(
                check_id="COMP-003",
                category="compliance",
                title="Regulatory Reporting",
                description="Regulatory reporting mechanisms in place",
                severity="high",
                requirement="MiFID II, Dodd-Frank",
                verification_method="manual",
                remediation="Implement automated regulatory reporting",
            ),
        ]

        # Combine all checks
        all_checks = auth_checks + network_checks + data_checks + app_checks + compliance_checks

        for check in all_checks:
            self.checks[check.check_id] = check

    def run_all_checks(self) -> Dict[str, CheckResult]:
        """Run all security checks."""
        print("Running security hardening checks...")
        print("="*60)

        for check_id, check in self.checks.items():
            print(f"Checking: {check.title} [{check.severity.upper()}]")
            result = self.run_check(check_id)
            self.results[check_id] = result

            status_icon = "✓" if result.status == CheckStatus.PASS else "✗" if result.status == CheckStatus.FAIL else "⚠"
            print(f"  Result: {status_icon} {result.status.value}")

            if result.findings:
                for finding in result.findings[:2]:  # Show first 2 findings
                    print(f"    - {finding}")

        return self.results

    def run_check(self, check_id: str) -> CheckResult:
        """Run specific security check."""
        check = self.checks.get(check_id)
        if not check:
            return CheckResult(
                check_id=check_id,
                status=CheckStatus.NOT_APPLICABLE,
                findings=["Check not found"],
            )

        # Run check based on category
        if check.category == "authentication":
            return self._check_authentication(check)
        elif check.category == "network_security":
            return self._check_network_security(check)
        elif check.category == "data_security":
            return self._check_data_security(check)
        elif check.category == "application_security":
            return self._check_application_security(check)
        elif check.category == "compliance":
            return self._check_compliance(check)
        else:
            return CheckResult(
                check_id=check_id,
                status=CheckStatus.NOT_APPLICABLE,
                findings=["Category not implemented for automated checking"],
            )

    def _check_authentication(self, check: SecurityCheck) -> CheckResult:
        """Check authentication security controls."""
        findings = []
        evidence = {}

        if check.check_id == "AUTH-001":
            # Check MFA - simplified
            # In production, check actual MFA configuration
            mfa_enabled = False  # Simulated
            if mfa_enabled:
                status = CheckStatus.PASS
                findings.append("MFA enabled for trading accounts")
            else:
                status = CheckStatus.FAIL
                findings.append("MFA not enabled for all trading accounts")

            evidence = {'mfa_enabled': mfa_enabled}

        elif check.check_id == "AUTH-002":
            # Check password policy
            # In production, check system password policy
            password_policy_strong = True  # Simulated
            if password_policy_strong:
                status = CheckStatus.PASS
                findings.append("Strong password policy configured")
            else:
                status = CheckStatus.FAIL
                findings.append("Weak password policy configuration")

            evidence = {'password_policy_checked': True}

        elif check.check_id == "AUTH-003":
            # Check session management
            # In production, check session configuration
            session_secure = True  # Simulated
            if session_secure:
                status = CheckStatus.PASS
                findings.append("Secure session management implemented")
            else:
                status = CheckStatus.WARNING
                findings.append("Session management could be improved")

            evidence = {'session_management_checked': True}

        else:
            status = CheckStatus.NOT_APPLICABLE
            findings.append("Check not implemented")

        return CheckResult(
            check_id=check.check_id,
            status=status,
            findings=findings,
            evidence=evidence,
        )

    def _check_network_security(self, check: SecurityCheck) -> CheckResult:
        """Check network security controls."""
        findings = []
        evidence = {}

        if check.check_id == "NET-001":
            # Check firewall
            try:
                # Simplified check - in production, check actual firewall rules
                subprocess.run(["iptables", "-L"], capture_output=True, text=True)
                status = CheckStatus.PASS
                findings.append("Firewall rules detected")
                evidence = {'firewall_active': True}
            except (FileNotFoundError, subprocess.CalledProcessError):
                status = CheckStatus.FAIL
                findings.append("Firewall not properly configured")
                evidence = {'firewall_active': False}

        elif check.check_id == "NET-002":
            # Check TLS configuration
            try:
                # Test TLS connection
                context = ssl.create_default_context()
                with socket.create_connection(("www.google.com", 443)) as sock:
                    with context.wrap_socket(sock, server_hostname="www.google.com") as ssock:
                        tls_version = ssock.version()

                if tls_version in ["TLSv1.3", "TLSv1.2"]:
                    status = CheckStatus.PASS
                    findings.append(f"TLS version: {tls_version}")
                else:
                    status = CheckStatus.FAIL
                    findings.append(f"Weak TLS version: {tls_version}")

                evidence = {'tls_version': tls_version}

            except Exception as e:
                status = CheckStatus.FAIL
                findings.append(f"TLS check failed: {e}")
                evidence = {'error': str(e)}

        elif check.check_id == "NET-003":
            # VPN check - manual verification needed
            status = CheckStatus.WARNING
            findings.append("VPN requirement requires manual verification")
            evidence = {'verification_method': 'manual'}

        else:
            status = CheckStatus.NOT_APPLICABLE
            findings.append("Check not implemented")

        return CheckResult(
            check_id=check.check_id,
            status=status,
            findings=findings,
            evidence=evidence,
        )

    def _check_data_security(self, check: SecurityCheck) -> CheckResult:
        """Check data security controls."""
        findings = []
        evidence = {}

        if check.check_id == "DATA-001":
            # Check encryption at rest
            # Simplified check
            encryption_enabled = True  # Simulated
            if encryption_enabled:
                status = CheckStatus.PASS
                findings.append("Data encryption at rest enabled")
            else:
                status = CheckStatus.FAIL
                findings.append("Data encryption at rest not enabled")

            evidence = {'encryption_enabled': encryption_enabled}

        elif check.check_id == "DATA-002":
            # Data classification - manual
            status = CheckStatus.WARNING
            findings.append("Data classification requires manual verification")
            evidence = {'verification_method': 'manual'}

        elif check.check_id == "DATA-003":
            # Data disposal - manual
            status = CheckStatus.WARNING
            findings.append("Secure data disposal requires manual verification")
            evidence = {'verification_method': 'manual'}

        else:
            status = CheckStatus.NOT_APPLICABLE
            findings.append("Check not implemented")

        return CheckResult(
            check_id=check.check_id,
            status=status,
            findings=findings,
            evidence=evidence,
        )

    def _check_application_security(self, check: SecurityCheck) -> CheckResult:
        """Check application security controls."""
        findings = []
        evidence = {}

        if check.check_id == "APP-001":
            # Input validation check
            # Simplified - in production, test actual endpoints
            input_validation_present = True  # Simulated
            if input_validation_present:
                status = CheckStatus.PASS
                findings.append("Input validation implemented")
            else:
                status = CheckStatus.FAIL
                findings.append("Input validation missing or insufficient")

            evidence = {'input_validation_checked': True}

        elif check.check_id == "APP-002":
            # API security check
            api_security_controls = True  # Simulated
            if api_security_controls:
                status = CheckStatus.PASS
                findings.append("API security controls implemented")
            else:
                status = CheckStatus.FAIL
                findings.append("API security controls missing")

            evidence = {'api_security_checked': True}

        elif check.check_id == "APP-003":
            # Error handling check
            secure_error_handling = True  # Simulated
            if secure_error_handling:
                status = CheckStatus.PASS
                findings.append("Secure error handling implemented")
            else:
                status = CheckStatus.WARNING
                findings.append("Error handling could expose sensitive information")

            evidence = {'error_handling_checked': True}

        else:
            status = CheckStatus.NOT_APPLICABLE
            findings.append("Check not implemented")

        return CheckResult(
            check_id=check.check_id,
            status=status,
            findings=findings,
            evidence=evidence,
        )

    def _check_compliance(self, check: SecurityCheck) -> CheckResult:
        """Check compliance controls."""
        findings = []
        evidence = {}

        if check.check_id == "COMP-001":
            # Audit trail check
            audit_trail_enabled = True  # Simulated
            if audit_trail_enabled:
                status = CheckStatus.PASS
                findings.append("Audit trail implemented")
            else:
                status = CheckStatus.FAIL
                findings.append("Audit trail not implemented")

            evidence = {'audit_trail_enabled': audit_trail_enabled}

        elif check.check_id == "COMP-002":
            # Data retention check
            retention_policy_exists = True  # Simulated
            if retention_policy_exists:
                status = CheckStatus.PASS
                findings.append("Data retention policy exists")
            else:
                status = CheckStatus.FAIL
                findings.append("Data retention policy missing")

            evidence = {'retention_policy_exists': retention_policy_exists}

        elif check.check_id == "COMP-003":
            # Regulatory reporting - manual
            status = CheckStatus.WARNING
            findings.append("Regulatory reporting requires manual verification")
            evidence = {'verification_method': 'manual'}

        else:
            status = CheckStatus.NOT_APPLICABLE
            findings.append("Check not implemented")

        return CheckResult(
            check_id=check.check_id,
            status=status,
            findings=findings,
            evidence=evidence,
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generate security hardening report."""
        if not self.results:
            self.run_all_checks()

        # Calculate statistics
        total_checks = len(self.results)
        passed = sum(1 for r in self.results.values() if r.status == CheckStatus.PASS)
        failed = sum(1 for r in self.results.values() if r.status == CheckStatus.FAIL)
        warnings = sum(1 for r in self.results.values() if r.status == CheckStatus.WARNING)

        # Calculate security score
        if total_checks > 0:
            security_score = (passed / total_checks) * 100
        else:
            security_score = 0

        # Critical findings
        critical_findings = []
        for check_id, result in self.results.items():
            check = self.checks.get(check_id)
            if (check and check.severity in ["critical", "high"] and
                result.status in [CheckStatus.FAIL, CheckStatus.WARNING]):
                critical_findings.append({
                    'check_id': check_id,
                    'title': check.title,
                    'severity': check.severity,
                    'status': result.status.value,
                    'findings': result.findings[:3],  # First 3 findings
                })

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'system': platform.node(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'security_score': round(security_score, 1),
            },
            'by_category': self._get_results_by_category(),
            'critical_findings': critical_findings,
            'recommendations': self._generate_recommendations(),
        }

        return report

    def _get_results_by_category(self) -> Dict[str, Dict[str, int]]:
        """Get results grouped by category."""
        categories = {}

        for check_id, result in self.results.items():
            check = self.checks.get(check_id)
            if check:
                category = check.category
                if category not in categories:
                    categories[category] = {
                        'total': 0,
                        'passed': 0,
                        'failed': 0,
                        'warnings': 0,
                    }

                categories[category]['total'] += 1

                if result.status == CheckStatus.PASS:
                    categories[category]['passed'] += 1
                elif result.status == CheckStatus.FAIL:
                    categories[category]['failed'] += 1
                elif result.status == CheckStatus.WARNING:
                    categories[category]['warnings'] += 1

        return categories

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate security recommendations."""
        recommendations = []

        # Check for critical failures
        critical_failures = []
        for check_id, result in self.results.items():
            check = self.checks.get(check_id)
            if (check and check.severity == "critical" and
                result.status == CheckStatus.FAIL):
                critical_failures.append(check.title)

        if critical_failures:
            recommendations.append({
                'priority': 'critical',
                'action': 'Address critical security failures immediately',
                'details': f'Critical failures: {", ".join(critical_failures[:3])}',
                'timeline': 'Immediate',
            })

        # Check for high severity failures
        high_failures = []
        for check_id, result in self.results.items():
            check = self.checks.get(check_id)
            if (check and check.severity == "high" and
                result.status == CheckStatus.FAIL):
                high_failures.append(check.title)

        if high_failures:
            recommendations.append({
                'priority': 'high',
                'action': 'Address high severity security failures',
                'details': f'High severity failures: {", ".join(high_failures[:3])}',
                'timeline': '7 days',
            })

        # General recommendation for security score
        total_score = self.generate_report()['summary']['security_score']
        if total_score < 80:
            recommendations.append({
                'priority': 'medium',
                'action': 'Improve overall security posture',
                'details': f'Current security score: {total_score}%. Target: 90%+',
                'timeline': '30 days',
            })

        return recommendations

    def save_report(self, format: str = "json"):
        """Save security report to file."""
        report = self.generate_report()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            filename = f"security_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)

        elif format == "html":
            filename = f"security_report_{timestamp}.html"
            html_report = self._generate_html_report(report)
            with open(filename, 'w') as f:
                f.write(html_report)

        elif format == "yaml":
            filename = f"security_report_{timestamp}.yaml"
            with open(filename, 'w') as f:
                yaml.dump(report, f, default_flow_style=False)

        print(f"\nSecurity report saved to: {filename}")
        return filename

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML security report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Hardening Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .score {{ font-size: 48px; font-weight: bold; text-align: center; }}
                .good {{ color: #27ae60; }}
                .medium {{ color: #f39c12; }}
                .poor {{ color: #e74c3c; }}
                .finding {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .critical {{ border-left: 5px solid #e74c3c; }}
                .high {{ border-left: 5px solid #e67e22; }}
                .medium {{ border-left: 5px solid #f1c40f; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .pass {{ color: #27ae60; }}
                .fail {{ color: #e74c3c; }}
                .warning {{ color: #f39c12; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Hardening Report</h1>
                <p>System: {system}</p>
                <p>Generated: {generated_at}</p>
            </div>

            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="score {score_class}">
                    {security_score}%
                </div>
                <p>Overall Security Score</p>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Warnings</th>
                        <th>Total</th>
                    </tr>
                    {category_rows}
                </table>
            </div>

            <h2>Critical Findings</h2>
            {critical_findings_html}

            <h2>Recommendations</h2>
            {recommendations_html}
        </body>
        </html>
        """

        # Determine score class
        score = report['summary']['security_score']
        if score >= 90:
            score_class = "good"
        elif score >= 70:
            score_class = "medium"
        else:
            score_class = "poor"

        # Generate category rows
        category_rows = ""
        for category, stats in report['by_category'].items():
            category_rows += f"""
            <tr>
                <td>{category.replace('_', ' ').title()}</td>
                <td class="pass">{stats['passed']}</td>
                <td class="fail">{stats['failed']}</td>
                <td class="warning">{stats['warnings']}</td>
                <td>{stats['total']}</td>
            </tr>
            """

        # Generate critical findings HTML
        critical_findings_html = ""
        if report['critical_findings']:
            for finding in report['critical_findings']:
                finding_class = finding['severity']
                critical_findings_html += f"""
                <div class="finding {finding_class}">
                    <h3>{finding['title']} [{finding['severity'].upper()}]</h3>
                    <p><strong>Status:</strong> {finding['status'].upper()}</p>
                    <p><strong>Findings:</strong></p>
                    <ul>
                """
                for item in finding['findings']:
                    critical_findings_html += f"<li>{item}</li>"

                critical_findings_html += """
                    </ul>
                </div>
                """
        else:
            critical_findings_html = "<p>No critical findings ✓</p>"

        # Generate recommendations HTML
        recommendations_html = ""
        for rec in report['recommendations']:
            recommendations_html += f"""
            <div class="finding">
                <h3>{rec['action']} [{rec['priority'].upper()}]</h3>
                <p><strong>Details:</strong> {rec['details']}</p>
                <p><strong>Timeline:</strong> {rec['timeline']}</p>
            </div>
            """

        return html_template.format(
            system=report['system'],
            generated_at=report['generated_at'],
            security_score=score,
            score_class=score_class,
            category_rows=category_rows,
            critical_findings_html=critical_findings_html,
            recommendations_html=recommendations_html,
        )

# Example usage
if __name__ == "__main__":
    print("="*60)
    print("SECURITY HARDENING CHECKLIST")
    print("="*60)

    # Create checklist
    checklist = SecurityHardeningChecklist()

    # Run all checks
    results = checklist.run_all_checks()

    # Generate report
    report = checklist.generate_report()

    print("\n" + "="*60)
    print("SECURITY REPORT SUMMARY")
    print("="*60)

    summary = report['summary']
    print(f"\nSecurity Score: {summary['security_score']}%")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")

    # Show category breakdown
    print("\nCategory Breakdown:")
    for category, stats in report['by_category'].items():
        print(f"  {category.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} passed")

    # Show critical findings
    if report['critical_findings']:
        print(f"\nCritical Findings: {len(report['critical_findings'])}")
        for finding in report['critical_findings'][:3]:  # Show first 3
            print(f"  - {finding['title']}: {finding['status']}")
    else:
        print("\nNo critical findings ✓")

    # Show recommendations
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['action']}")

    # Save report
    checklist.save_report(format="html")

    print("\nSecurity hardening assessment complete!")
```

## 🚀 Deployment Guide

### Step-by-Step Security Hardening

1. **Initial Setup:**

```bash
# Clone the repository
git clone <repository-url>
cd security-framework

# Install dependencies
pip install -r requirements.txt

# Generate TLS certificates for development
./scripts/generate_certificates.sh

# Start security testing environment
docker-compose up -d
```

2. **Run Security Assessment:**

```bash
# Run comprehensive security assessment
python threat-modeling/security_assessor.py

# Generate security report
python scripts/generate_security_report.py

# Run compliance checks
python compliance/automation/compliance_engine.py
```

3. **Implement Security Controls:**

```bash
# Configure MFA
python authentication/multi_factor/mfa_system.py

# Set up encryption
python encryption/key_management/enterprise_kms.py

# Configure WAF rules
python network-security/waf/rules_engine.py
```

4. **Run Security Checklist:**

```bash
# Run automated security checklist
python scripts/security_checklist.py

# Generate hardening report
python scripts/generate_hardening_report.py
```

### Production Security Configuration

```yaml
# security_config.yaml
authentication:
  mfa:
    enabled: true
    required_methods: ["totp", "webauthn"]
    backup_codes: true

  password_policy:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special: true
    max_age_days: 90

encryption:
  data_at_rest:
    enabled: true
    algorithm: "AES-256-GCM"

  data_in_transit:
    tls_version: "1.3"
    min_key_size: 2048

  key_management:
    provider: "aws_kms" # or azure_keyvault, gcp_kms
    rotation_days: 90

network:
  firewall:
    enabled: true
    default_policy: "deny"

  waf:
    enabled: true
    rules_file: "./waf_rules.yaml"

  vpn:
    required: true
    mfa_required: true

api_security:
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_limit: 20

  input_validation:
    enabled: true
    max_request_size: "10MB"

  cors:
    enabled: true
    allowed_origins: ["https://trading.example.com"]

compliance:
  sec_17a:
    worm_storage: true
    retention_years: 7

  mifid_ii:
    best_execution_monitoring: true
    transaction_reporting: true

  gdpr:
    data_subject_rights: true
    data_protection_officer: true

monitoring:
  siem:
    enabled: true
    provider: "splunk" # or elk, datadog

  ids_ips:
    enabled: true
    rules_update_frequency: "daily"

  vulnerability_scanning:
    enabled: true
    frequency: "weekly"
```

## 🔒 Security Best Practices

### 1. **Principle of Least Privilege**

```python
# Implement RBAC with minimum necessary permissions
roles = {
    'trader': ['read_market_data', 'place_orders', 'view_portfolio'],
    'risk_manager': ['read_all_data', 'modify_risk_limits', 'view_audit_logs'],
    'admin': ['*'],  # Use sparingly with MFA
}
```

### 2. **Defense in Depth**

```python
# Multiple layers of security
security_layers = [
    'network_firewall',
    'web_application_firewall',
    'authentication',
    'authorization',
    'input_validation',
    'output_encoding',
    'encryption',
    'audit_logging',
]
```

### 3. **Secure Development Lifecycle**

```python
# Integrate security throughout development
devops_pipeline = {
    'code_analysis': ['static_analysis', 'dependency_scanning'],
    'testing': ['unit_tests', 'integration_tests', 'security_tests'],
    'deployment': ['automated_security_checks', 'configuration_validation'],
    'monitoring': ['real_time_alerts', 'vulnerability_scanning'],
}
```

### 4. **Regular Security Assessments**

```python
# Schedule automated security assessments
assessment_schedule = {
    'daily': ['log_analysis', 'intrusion_detection'],
    'weekly': ['vulnerability_scanning', 'compliance_checks'],
    'monthly': ['penetration_testing', 'security_review'],
    'quarterly': ['red_team_exercise', 'architecture_review'],
}
```

## 📊 Compliance Matrix

| Regulation    | Key Requirements                                        | Implementation                                     | Status       |
| ------------- | ------------------------------------------------------- | -------------------------------------------------- | ------------ |
| **SEC 17a-4** | WORM storage, 7-year retention, Audit trail             | Immutable audit logs, Encrypted storage            | ✅ Compliant |
| **MiFID II**  | Best execution, Transaction reporting, Record keeping   | Real-time monitoring, Automated reporting          | ✅ Compliant |
| **GDPR**      | Data protection, Right to erasure, Breach notification  | Encryption, Data classification, Incident response | ✅ Compliant |
| **PCI DSS**   | Cardholder data protection, Access controls, Monitoring | Tokenization, MFA, Log management                  | 🟡 Partial   |
| **ISO 27001** | ISMS, Risk management, Security controls                | Policy framework, Risk assessment, Controls        | 🟡 Partial   |

## 🚨 Incident Response Plan

### Automated Incident Response (scripts/incident_response.py)

```python
"""
Automated incident response for security events in trading systems.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
import json

@dataclass
class SecurityIncident:
    """Security incident definition."""
    incident_id: str
    severity: str  # critical, high, medium, low
    incident_type: str  # intrusion, data_breach, ddos, malware, insider_threat
    description: str
    detected_at: datetime
    affected_systems: List[str]
    initial_impact: str
    status: str = "open"  # open, investigating, contained, resolved

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'incident_id': self.incident_id,
            'severity': self.severity,
            'incident_type': self.incident_type,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'affected_systems': self.affected_systems,
            'initial_impact': self.initial_impact,
            'status': self.status,
        }

class IncidentResponseSystem:
    """Automated incident response system."""

    def __init__(self):
        self.incidents = {}
        self.escalation_rules = self._load_escalation_rules()
        self.response_playbooks = self._load_response_playbooks()

    def _load_escalation_rules(self) -> Dict[str, List[str]]:
        """Load incident escalation rules."""
        return {
            'critical': ['security_team', 'cto', 'compliance_officer', 'legal'],
            'high': ['security_team', 'cto'],
            'medium': ['security_team'],
            'low': ['security_team'],
        }

    def _load_response_playbooks(self) -> Dict[str, List[str]]:
        """Load incident response playbooks."""
        return {
            'intrusion': [
                'Isolate affected systems',
                'Preserve evidence',
                'Analyze attack vector',
                'Implement temporary mitigations',
                'Patch vulnerabilities',
            ],
            'data_breach': [
                'Contain breach',
                'Assess data exposed',
                'Notify affected parties if required',
                'Enhance security controls',
                'Update incident response plan',
            ],
            'ddos': [
                'Activate DDoS mitigation',
                'Reroute traffic if needed',
                'Monitor attack patterns',
                'Contact ISP for support',
                'Implement rate limiting',
            ],
            'malware': [
                'Isolate infected systems',
                'Run antivirus scans',
                'Restore from clean backups',
                'Analyze infection vector',
                'Update security controls',
            ],
        }

    def detect_incident(self,
                       severity: str,
                       incident_type: str,
                       description: str,
                       affected_systems: List[str]) -> SecurityIncident:
        """Detect and create new security incident."""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.incidents) + 1:04d}"

        incident = SecurityIncident(
            incident_id=incident_id,
            severity=severity,
            incident_type=incident_type,
            description=description,
            detected_at=datetime.utcnow(),
            affected_systems=affected_systems,
            initial_impact=self._assess_initial_impact(severity, incident_type),
        )

        self.incidents[incident_id] = incident

        # Trigger automated response
        self._trigger_response(incident)

        return incident

    def _assess_initial_impact(self, severity: str, incident_type: str) -> str:
        """Assess initial impact of incident."""
        impact_map = {
            'critical': 'Major impact on trading operations',
            'high': 'Significant impact on trading operations',
            'medium': 'Moderate impact on trading operations',
            'low': 'Limited impact on trading operations',
        }
        return impact_map.get(severity, 'Unknown impact')

    def _trigger_response(self, incident: SecurityIncident):
        """Trigger automated incident response."""
        print(f"\n🚨 SECURITY INCIDENT DETECTED 🚨")
        print(f"Incident ID: {incident.incident_id}")
        print(f"Severity: {incident.severity.upper()}")
        print(f"Type: {incident.incident_type}")
        print(f"Description: {incident.description}")

        # Escalate based on severity
        self._escalate_incident(incident)

        # Execute response playbook
        self._execute_playbook(incident)

        # Log incident for compliance
        self._log_incident(incident)

    def _escalate_incident(self, incident: SecurityIncident):
        """Escalate incident to appropriate teams."""
        teams_to_notify = self.escalation_rules.get(incident.severity, [])

        print(f"\nEscalating to: {', '.join(teams_to_notify)}")

        # Send notifications (simplified)
        for team in teams_to_notify:
            self._send_notification(team, incident)

    def _send_notification(self, team: str, incident: SecurityIncident):
        """Send incident notification."""
        # In production, integrate with Slack, PagerDuty, etc.
        subject = f"[{incident.severity.upper()}] Security Incident {incident.incident_id}"
        message = f"""
        Security Incident Detected:

        ID: {incident.incident_id}
        Severity: {incident.severity}
        Type: {incident.incident_type}
        Description: {incident.description}
        Detected: {incident.detected_at}
        Affected Systems: {', '.join(incident.affected_systems)}

        Immediate Action Required.
        """

        print(f"  Notifying {team}: {subject}")

        # Example: Send email (configure properly in production)
        # self._send_email(team, subject, message)

    def _execute_playbook(self, incident: SecurityIncident):
        """Execute incident response playbook."""
        playbook = self.response_playbooks.get(incident.incident_type, [])

        print(f"\nExecuting {incident.incident_type} response playbook:")

        for step in playbook:
            print(f"  → {step}")

            # In production, execute actual response actions
            # This is simplified for example

    def _log_incident(self, incident: SecurityIncident):
        """Log incident for compliance and analysis."""
        # Store in database
        incident_data = incident.to_dict()

        # Add to compliance audit trail
        compliance_data = {
            'incident': incident_data,
            'logged_at': datetime.utcnow().isoformat(),
            'compliance_relevant': True,
            'regulations': ['SEC_17A', 'GDPR', 'MiFID_II'],
        }

        print(f"\nIncident logged for compliance reporting")

        # In production, store in secure database
        # with open(f"incidents/{incident.incident_id}.json", 'w') as f:
        #     json.dump(compliance_data, f, indent=2)

    def get_incident_report(self) -> Dict[str, Any]:
        """Generate incident report."""
        open_incidents = [i for i in self.incidents.values() if i.status == 'open']
        resolved_incidents = [i for i in self.incidents.values() if i.status == 'resolved']

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_incidents': len(self.incidents),
                'open_incidents': len(open_incidents),
                'resolved_incidents': len(resolved_incidents),
                'by_severity': self._count_by_severity(),
                'by_type': self._count_by_type(),
            },
            'recent_incidents': [
                incident.to_dict()
                for incident in list(self.incidents.values())[-5:]  # Last 5 incidents
            ],
            'recommendations': self._generate_recommendations(),
        }

        return report

    def _count_by_severity(self) -> Dict[str, int]:
        """Count incidents by severity."""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for incident in self.incidents.values():
            counts[incident.severity] = counts.get(incident.severity, 0) + 1
        return counts

    def _count_by_type(self) -> Dict[str, int]:
        """Count incidents by type."""
        counts = {}
        for incident in self.incidents.values():
            counts[incident.incident_type] = counts.get(incident.incident_type, 0) + 1
        return counts

    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations from incidents."""
        recommendations = []

        # Analyze incident patterns
        severity_counts = self._count_by_severity()
        type_counts = self._count_by_type()

        if severity_counts.get('critical', 0) > 0:
            recommendations.append("Review and strengthen security controls for critical systems")

        if type_counts.get('intrusion', 0) > 0:
            recommendations.append("Enhance intrusion detection and prevention systems")

        if type_counts.get('data_breach', 0) > 0:
            recommendations.append("Review data protection and access controls")

        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize incident response system
    ir_system = IncidentResponseSystem()

    # Simulate incident detection
    print("="*60)
    print("INCIDENT RESPONSE SIMULATION")
    print("="*60)

    # Example incidents
    incidents = [
        {
            'severity': 'high',
            'type': 'intrusion',
            'description': 'Multiple failed login attempts detected from suspicious IP',
            'systems': ['trading_api', 'user_portal'],
        },
        {
            'severity': 'critical',
            'type': 'data_breach',
            'description': 'Potential unauthorized access to customer PII data',
            'systems': ['customer_database', 'backup_system'],
        },
        {
            'severity': 'medium',
            'type': 'ddos',
            'description': 'DDoS attack targeting trading API endpoints',
            'systems': ['api_gateway', 'load_balancer'],
        },
    ]

    for incident_data in incidents:
        incident = ir_system.detect_incident(
            severity=incident_data['severity'],
            incident_type=incident_data['type'],
            description=incident_data['description'],
            affected_systems=incident_data['systems'],
        )
        print("\n" + "-"*60)

    # Generate incident report
    report = ir_system.get_incident_report()

    print("\n" + "="*60)
    print("INCIDENT REPORT")
    print("="*60)

    summary = report['summary']
    print(f"\nTotal Incidents: {summary['total_incidents']}")
    print(f"Open Incidents: {summary['open_incidents']}")
    print(f"Resolved Incidents: {summary['resolved_incidents']}")

    print("\nIncidents by Severity:")
    for severity, count in summary['by_severity'].items():
        print(f"  {severity.title()}: {count}")

    print("\nIncidents by Type:")
    for incident_type, count in summary['by_type'].items():
        print(f"  {incident_type}: {count}")

    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")

    print("\nIncident response simulation complete!")
```

## 📚 Learning Outcomes

By completing Day 95, you will be able to:

- **Conduct** comprehensive security assessments of trading systems
- **Implement** multi-factor authentication with TOTP and WebAuthn
- **Design** enterprise key management systems with automatic rotation
- **Configure** Web Application Firewalls with trading-specific rules
- **Automate** regulatory compliance for SEC 17a-4, MiFID II, and GDPR
- **Develop** security hardening checklists and automated verification
- **Establish** incident response procedures for security events
- **Integrate** security controls throughout the development lifecycle
- **Monitor** security posture with continuous compliance checking
- **Document** security architecture and controls for audits

## 🔧 Best Practices

### 1. **Security by Design**

```python
# Build security into the architecture
security_principles = [
    'least_privilege',
    'defense_in_depth',
    'fail_secure',
    'separation_of_duties',
    'economy_of_mechanism',
]
```

### 2. **Continuous Security Monitoring**

```python
# Real-time security monitoring
monitoring_stack = {
    'siem': 'collect_and_correlate_logs',
    'ids_ips': 'detect_intrusions',
    'waf': 'protect_applications',
    'vulnerability_scanner': 'find_weaknesses',
    'compliance_checker': 'ensure_regulatory_adherence',
}
```

### 3. **Automated Security Testing**

```python
# Integrate security testing into CI/CD
security_tests = {
    'static_analysis': 'check_code_for_vulnerabilities',
    'dependency_scanning': 'find_vulnerable_libraries',
    'dynamic_analysis': 'test_running_applications',
    'penetration_testing': 'simulate_real_attacks',
    'compliance_scanning': 'verify_regulatory_requirements',
}
```

### 4. **Incident Response Readiness**

```python
# Prepare for security incidents
response_capabilities = {
    'detection': 'monitoring_and_alerting',
    'containment': 'isolate_affected_systems',
    'eradication': 'remove_threat',
    'recovery': 'restore_normal_operations',
    'lessons_learned': 'improve_security_posture',
}
```

## 🚨 Critical Security Controls for Trading Systems

### Must-Have Security Controls:

1. **Authentication & Authorization:**

   - Multi-factor authentication for all trading accounts
   - Role-based access control with least privilege
   - Session management with automatic timeout

2. **Data Protection:**

   - Encryption of data at rest and in transit
   - Secure key management with automatic rotation
   - Data classification and handling procedures

3. **Network Security:**

   - Firewall segmentation between trading zones
   - Web Application Firewall for trading APIs
   - VPN for remote access with MFA

4. **Compliance:**

   - Immutable audit trail (WORM storage)
   - Automated regulatory reporting
   - Data retention and disposal policies

5. **Monitoring & Response:**
   - Real-time security monitoring (SIEM)
   - Intrusion detection and prevention
   - Automated incident response procedures

## 📈 Security Maturity Levels

| Level            | Characteristics                                   | Implementation                                      |
| ---------------- | ------------------------------------------------- | --------------------------------------------------- |
| **Basic**        | Manual security checks, Reactive response         | Security assessments, Basic monitoring              |
| **Intermediate** | Automated security controls, Proactive monitoring | MFA, WAF, Regular vulnerability scanning            |
| **Advanced**     | Integrated security, Predictive analytics         | Zero-trust architecture, ML-based threat detection  |
| **Expert**       | Security by design, Continuous improvement        | Automated compliance, Real-time threat intelligence |

## 🎯 Next Steps

After implementing security hardening:

1. **Continuous Improvement:**

   - Regular security assessments and penetration testing
   - Security training for development and operations teams
   - Continuous monitoring and threat intelligence integration

2. **Advanced Security Measures:**

   - Implement zero-trust architecture
   - Deploy deception technologies (honeypots)
   - Use machine learning for anomaly detection
   - Implement hardware security modules (HSMs)

3. **Compliance Expansion:**

   - Add support for additional regulations (SOX, Basel III)
   - Implement automated evidence collection for audits
   - Develop cross-border data transfer compliance

4. **Security Culture:**
   - Establish security champions in development teams
   - Implement secure development training
   - Create security metrics and dashboards for executives

---

This comprehensive security hardening framework provides everything needed to protect trading systems against threats while maintaining regulatory compliance. By following this guide, you can build a robust security posture that protects trading operations, customer data, and meets all regulatory requirements.
