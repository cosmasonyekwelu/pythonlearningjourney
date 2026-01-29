# Day 41: Network Scanning & Monitoring

**Date:** November 1, 2025

## Learning Objective
To build advanced network security tools for discovering hosts, scanning open ports, and monitoring network traffic for potential threats.

## Concepts Covered
- **ARP Scanning**: Using Scapy to discover devices on a local area network (LAN).
- **Port Scanning**: Building a multi-threaded scanner to identify open TCP services.
- **Packet Sniffing**: Capturing and analyzing live network traffic to detect suspicious patterns.
- **Security Event Logging**: Automatically identifying events like SYN scans or unauthorized device connections.
- **Rich Visualization**: Using the `rich` library to create professional CLI tables and progress bars.

## Code Explanation
The `day_fortyone.py` script is a sophisticated security toolkit:
- **`NetworkScanner`**:
    - `arp_scan()`: Uses Scapy to send ARP broadcasts and map IPs to MAC addresses.
    - `port_scan_host()`: Checks common ports (22, 80, 443) and identifies running services.
    - `analyze_packets()`: Summarizes protocol distribution (TCP/UDP/ICMP) and identifies top "talkers" on the network.
- **`SecurityMonitoring`**: A continuous loop that alerts the user when a new host appears or a SYN scan is detected.
- **`SimpleService`**: A dummy TCP listener used to test the scanner's accuracy.

## How to Run
*Note: Some features require root/admin privileges.*
1. Install requirements: `pip install scapy rich netifaces`
2. Run the toolkit:
```bash
sudo python week_06/dayfortyone/day_fortyone.py
```
3. Choose "Network Discovery Scan" to map your local network.

## Reflection
Network security tools are the "eyes" of a security engineer. Combining low-level packet analysis with high-level reporting allows for a complete understanding of a network's attack surface.
