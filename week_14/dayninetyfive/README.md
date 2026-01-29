# Day 95: Security Hardening & Compliance

## Objective
Harden trading systems against security threats and automate compliance controls for financial regulations.

## Concepts Covered
- **MFA (Multi-Factor Authentication)**: Implementing TOTP and WebAuthn for secure trading access.
- **Enterprise KMS**: Managing encryption keys with automatic rotation and secure wrapping.
- **WAF (Web Application Firewall)**: Creating rules to block SQLi, XSS, and price/quantity manipulation.
- **Compliance Automation**: Automatically verifying SEC 17a-4, MiFID II, and GDPR requirements.

## Code Explanation
The `day_ninetyfive.py` script features a `TradingSecurityAssessor` that scans system configurations for security gaps and generates a compliance report.

## How to Run
Run the security assessment demonstration:
```bash
python day_ninetyfive.py
```
