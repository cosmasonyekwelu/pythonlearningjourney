# Day 41: Network Scanning & Monitoring

## Overview

This module provides hands-on experience with network security fundamentals, including network reconnaissance, packet analysis, and security monitoring. You'll learn to use both command-line tools and Python scripts to scan networks, analyze traffic, and detect security events.

## Learning Objectives

- Perform network reconnaissance using scanning tools and techniques
- Analyze network traffic using packet capture and analysis
- Implement basic intrusion detection and security monitoring
- Understand firewall concepts and network security architecture
- Set up logging and monitoring for security events
- Conduct basic packet analysis for troubleshooting and security

## Core Concepts Covered

### 1. Defense in Depth

- Layered security approach
- Network segmentation principles
- Multiple security controls implementation
- Redundancy in protection strategies

### 2. Network Reconnaissance

- Host Discovery: Ping sweeps, ARP scanning
- Port Scanning: TCP/UDP port enumeration
- Service Detection: Banner grabbing, version detection
- OS Fingerprinting: Remote operating system identification

### 3. Network Security Controls

- Firewalls: Packet filtering, stateful inspection
- IDS/IPS: Intrusion Detection/Prevention Systems
- SIEM: Security Information and Event Management
- Network Access Control (NAC) implementation

### 4. Packet Analysis

- Protocol Analysis: TCP/IP stack understanding
- Traffic Patterns: Normal vs. anomalous behavior
- Security Monitoring: Threat detection in packets
- Forensic Analysis: Incident investigation techniques

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Administrative/root privileges for full functionality

### Required Dependencies

```bash
pip install scapy rich
```

### Optional Dependencies for Enhanced Features

```bash
pip install netifaces
```

### Platform-Specific Requirements

#### Windows:

- Run PowerShell or Command Prompt as Administrator
- Install Npcap (required for Scapy on Windows): https://npcap.com/

#### Linux:

```bash
sudo apt-get update
sudo apt-get install python3-pip wireshark tcpdump
sudo pip install scapy rich
```

#### macOS:

````bash
brew install python wireshark
pip install scapy rich



## Tool Features

### Network Scanner Capabilities

- **ARP Scanning**: Fast host discovery on local network using ARP requests
- **Ping Sweep**: ICMP-based host discovery for cross-platform compatibility
- **TCP Port Scanning**: Common service port enumeration (21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389)
- **Service Detection**: Automatic service identification based on port numbers
- **Results Export**: JSON report generation for documentation and analysis

### Security Monitor Features

- **Continuous Monitoring**: Real-time network observation with configurable duration
- **Anomaly Detection**: Automatic detection of new hosts and services
- **Security Event Logging**: Incident recording and alerting system
- **Packet Analysis**: Real-time traffic pattern analysis

### Packet Analyzer Functions

- **Protocol Distribution**: Breakdown of network protocols in captured traffic
- **Top Talkers**: Identification of busiest network hosts
- **Security Event Detection**: Automatic detection of scan attempts and unusual traffic
- **Traffic Visualization**: Rich console output with formatted tables

## Hands-On Exercises

### Exercise 1: Network Discovery

```bash
# Using the Python toolkit
python day_fortyone.py
# Select Option 1: Network Discovery Scan

# Using Nmap (command line)
nmap -sn 192.168.1.0/24
nmap -A 192.168.1.1/24
nmap -p 1-1000 192.168.1.1
````

### Exercise 2: Service Detection

```bash
# Version detection with Nmap
nmap -sV 192.168.1.1

# Aggressive service detection
nmap -A -T4 192.168.1.1

# UDP service scanning
nmap -sU -p 53,161 192.168.1.1

# Using the Python toolkit
python -c "
from day41_network_security import NetworkScanner
scanner = NetworkScanner()
hosts = scanner.network_scan('192.168.1.0/24')
scanner.display_scan_results()
"
```

### Exercise 3: Packet Analysis

```bash
# Basic tcpdump usage
sudo tcpdump -i any
sudo tcpdump host 192.168.1.100
sudo tcpdump port 80
sudo tcpdump -w capture.pcap

# Using the Python toolkit
python day41_network_security.py
# Select Option 2: Packet Capture & Analysis
```

## Security Implementation Examples

### 1. Network Access Control

```python
# Simple port-based access control
ALLOWED_PORTS = {22, 80, 443, 993, 995}

def check_port_access(port: int) -> bool:
    return port in ALLOWED_PORTS

def validate_source_ip(source_ip: str) -> bool:
    # Allow only from trusted subnets
    trusted_subnets = ['192.168.1.0/24', '10.0.0.0/8']
    for subnet in trusted_subnets:
        if ipaddress.ip_address(source_ip) in ipaddress.ip_network(subnet):
            return True
    return False
```

### 2. Basic Intrusion Detection

```python
class IntrusionDetector:
    def __init__(self):
        self.suspicious_events = []
        self.known_scanners = set()
        self.port_scan_threshold = 10
        self.failed_auth_threshold = 5

    def detect_port_scan(self, source_ip: str, scanned_ports: List[int]):
        if len(scanned_ports) > self.port_scan_threshold:
            self.record_incident("Port Scan", source_ip, scanned_ports)
            self.known_scanners.add(source_ip)

    def detect_brute_force(self, source_ip: str, failed_attempts: int):
        if failed_attempts > self.failed_auth_threshold:
            self.record_incident("Brute Force Attempt", source_ip, failed_attempts)

    def detect_anomalous_traffic(self, packet):
        if packet.haslayer(scapy.TCP):
            # Detect SYN floods
            if packet[scapy.TCP].flags == 2:  # SYN packet
                self.check_syn_flood(packet[scapy.IP].src)
```

### 3. Security Logging and Monitoring

```python
import logging
from datetime import datetime

class SecurityLogger:
    def __init__(self, log_file='security.log'):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('NetworkSecurity')

    def log_security_event(self, event_type: str, source_ip: str, details: str, severity: str = "INFO"):
        log_message = f"{event_type} from {source_ip}: {details}"

        if severity == "HIGH":
            self.logger.error(log_message)
        elif severity == "MEDIUM":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        # Real-time console alert for high severity events
        if severity in ["HIGH", "MEDIUM"]:
            print(f"ALERT {datetime.now().strftime('%H:%M:%S')} - {log_message}")
```

### 4. Network Traffic Baseline

```python
def establish_baseline(duration: int = 300):
    """Capture normal traffic patterns for baseline analysis"""
    baseline_data = {
        'protocols': defaultdict(int),
        'source_ips': Counter(),
        'destination_ports': Counter(),
        'packet_sizes': [],
        'average_pps': 0  # packets per second
    }

    start_time = time.time()
    packet_count = 0

    def packet_handler(packet):
        nonlocal packet_count
        packet_count += 1

        if packet.haslayer(scapy.IP):
            baseline_data['protocols'][packet[scapy.IP].proto] += 1
            baseline_data['source_ips'][packet[scapy.IP].src] += 1

        if packet.haslayer(scapy.TCP):
            baseline_data['destination_ports'][packet[scapy.TCP].dport] += 1

        baseline_data['packet_sizes'].append(len(packet))

    # Capture traffic for specified duration
    scapy.sniff(prn=packet_handler, timeout=duration)

    # Calculate average packets per second
    baseline_data['average_pps'] = packet_count / duration

    return baseline_data
```

## Monitoring Setup Examples

### Simple Service Monitoring

```python
def monitor_service(host: str, port: int, check_interval: int = 60):
    """Monitor service availability with alerting"""
    consecutive_failures = 0
    failure_threshold = 3

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result != 0:
                consecutive_failures += 1
                print(f"Service {host}:{port} is DOWN (Failure #{consecutive_failures})")

                if consecutive_failures >= failure_threshold:
                    print(f"ALERT: Service {host}:{port} consistently unavailable!")
            else:
                if consecutive_failures > 0:
                    print(f"Service {host}:{port} is BACK UP")
                consecutive_failures = 0
                print(f"Service {host}:{port} is UP")

        except Exception as e:
            print(f"Monitoring error for {host}:{port}: {e}")

        time.sleep(check_interval)

# Example usage
monitor_service('192.168.1.1', 80)   # Web server
monitor_service('192.168.1.1', 22)   # SSH service
monitor_service('192.168.1.2', 443)  # HTTPS service
```

### Real-time Traffic Analysis

```python
def real_time_traffic_analysis(interface: str = None):
    """Real-time network traffic analysis with anomaly detection"""
    baseline = establish_baseline(60)  # 1-minute baseline

    def analyze_packet(packet):
        current_stats = {
            'protocols': Counter(),
            'source_ips': Counter(),
            'pps': 0
        }

        if packet.haslayer(scapy.IP):
            current_stats['protocols'][packet[scapy.IP].proto] += 1
            current_stats['source_ips'][packet[scapy.IP].src] += 1

            # Check for protocol anomalies
            for proto, count in current_stats['protocols'].items():
                baseline_count = baseline['protocols'].get(proto, 0)
                if count > baseline_count * 2:  # 100% increase
                    print(f"Anomaly: Unusual protocol {proto} traffic")

        # Check for new source IPs
        for ip in current_stats['source_ips']:
            if ip not in baseline['source_ips']:
                print(f"New host detected: {ip}")

    print("Starting real-time traffic analysis...")
    scapy.sniff(prn=analyze_packet, iface=interface)
```

## Security Testing Commands

### Network Mapping with Nmap

```bash
# Basic network discovery
nmap -sn 192.168.1.0/24

# Comprehensive scan with OS detection
nmap -A 192.168.1.1/24

# Stealth scanning
nmap -sS 192.168.1.1

# Version detection
nmap -sV 192.168.1.1

# Output to file
nmap -oN scan_results.txt 192.168.1.0/24
```

### Packet Analysis with tcpdump

```bash
# Capture all traffic on interface
sudo tcpdump -i any

# Capture specific host traffic
sudo tcpdump host 192.168.1.100

# Capture HTTP traffic
sudo tcpdump port 80

# Capture and display in ASCII
sudo tcpdump -A -i any

# Save capture to file
sudo tcpdump -w network_capture.pcap

# Read from capture file
tcpdump -r network_capture.pcap
```

### Using the Python Toolkit

```python
from day41_network_security import NetworkScanner, SimpleService

# Comprehensive network scan
scanner = NetworkScanner()
hosts = scanner.network_scan("192.168.1.0/24")
scanner.display_scan_results()

# Start security monitoring
scanner.start_security_monitoring(duration=600)  # 10 minutes

# Packet capture and analysis
scanner.start_packet_capture(count=500)

# Generate security report
report = scanner.generate_security_report()
```

## Security Best Practices

### Network Scanning Ethics

- Only scan networks you own or have explicit permission to test
- Use scanning tools responsibly and ethically
- Understand legal implications in your jurisdiction
- Respect network resources and avoid disruptive scanning techniques
- Schedule scans during off-peak hours for production networks

### Monitoring Considerations

- Implement proper access controls for monitoring data
- Encrypt sensitive monitoring data in transit and at rest
- Follow data retention policies and privacy regulations
- Use monitoring for security purposes, not surveillance
- Regularly review and update monitoring rules

### Operational Security

- Keep scanning and monitoring tools updated
- Use dedicated monitoring accounts with least privilege
- Implement proper log rotation and storage
- Regular security reviews of monitoring configurations
- Document all monitoring activities and procedures

## Security Monitoring Checklist

- [ ] Network topology documented and monitored
- [ ] Unauthorized device detection enabled
- [ ] Port scanning detection configured
- [ ] Service availability monitoring active
- [ ] Traffic baselines established for normal patterns
- [ ] Security event logging implemented
- [ ] Alerting configured for critical security events
- [ ] Regular security reviews and audits scheduled
- [ ] Incident response procedures documented
- [ ] Monitoring coverage includes all critical assets

## Learning Outcomes

After completing this module, you should be able to:

1. Perform comprehensive network reconnaissance using multiple tools
2. Analyze network traffic patterns and identify anomalies
3. Implement basic intrusion detection and monitoring systems
4. Understand and apply network security architecture principles
5. Conduct security-focused packet analysis
6. Generate and interpret network security reports
7. Apply ethical considerations to network scanning activities
8. Set up continuous security monitoring for networks

## Troubleshooting

### Common Issues

1. **Permission Errors**: Run with administrative privileges (sudo on Linux/macOS, Administrator on Windows)
2. **Scapy Import Errors**: Ensure Npcap is installed on Windows, libpcap on Linux
3. **No Packets Captured**: Check interface permissions and network connectivity
4. **ARP Scan Not Working**: Verify you're on the local network segment
5. **Performance Issues**: Reduce packet capture count or monitoring duration

### Platform-Specific Solutions

**Windows**:

- Install Npcap (not WinPcap) for Scapy compatibility
- Run PowerShell as Administrator
- Disable Windows Firewall temporarily for testing

**Linux**:

```bash
sudo setcap cap_net_raw=eip /usr/bin/python3
```

**macOS**:

- Grant Terminal network access in System Preferences
- Install Xcode command line tools if needed

## Next Steps

Continue your security learning journey with:

- **Advanced Network Security**: Firewall configurations, VPN setup
- **Wireless Security**: WiFi penetration testing and security
- **Cloud Network Security**: VPC, security groups, cloud monitoring
- **Incident Response**: Network forensic analysis and investigation

## Important Notes

- This toolkit is for educational and authorized testing purposes only
- Always obtain proper authorization before scanning any network
- Respect privacy and legal boundaries when conducting network analysis
- Keep security tools updated and follow responsible disclosure practices
- Document all testing activities and findings appropriately

## References

- Nmap Documentation: https://nmap.org/docs.html
- Scapy Documentation: https://scapy.readthedocs.io/
- Wireshark Learning Resources: https://www.wireshark.org/docs/
- Network Security Monitoring: https://www.sans.org/nsm/
- TCP/IP Guide: http://www.tcpipguide.com/

This module provides practical experience with network security fundamentals essential for understanding modern network defenses and monitoring strategies.

```

```
