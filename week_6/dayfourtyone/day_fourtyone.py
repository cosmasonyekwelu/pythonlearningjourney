"""
Day 41: Network Scanning & Monitoring
Comprehensive network security toolkit for scanning, monitoring, and packet analysis.
"""

import os
import sys
import socket
import subprocess
import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import ipaddress

# Third-party imports (install with pip)
try:
    import scapy.all as scapy
    from scapy.layers import http
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Note: Scapy not available. Install with: pip install scapy")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Rich not available. Install with: pip install rich")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_security.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('NetworkSecurity')


@dataclass
class NetworkHost:
    """Represents a discovered network host"""
    ip: str
    mac: str = "Unknown"
    hostname: str = "Unknown"
    os: str = "Unknown"
    open_ports: List[int] = None
    services: Dict[int, str] = None

    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []
        if self.services is None:
            self.services = {}


@dataclass
class SecurityEvent:
    """Represents a security-related network event"""
    timestamp: datetime
    event_type: str
    source_ip: str
    destination_ip: str
    protocol: str
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class NetworkScanner:
    """Comprehensive network scanning and monitoring tool"""

    COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389]

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.discovered_hosts = []
        self.security_events = []
        self.packet_count = 0
        self.start_time = datetime.now()

    def display_banner(self):
        """Display tool banner"""
        if self.console:
            self.console.print(Panel.fit(
                "Network Security Scanner & Monitor",
                style="bold blue"
            ))
        else:
            print("Network Security Scanner & Monitor")
            print("=" * 50)

    def get_local_network(self) -> str:
        """Get local network CIDR"""
        try:
            # Get default gateway and infer network
            import netifaces
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET][0]

            # Simple assumption: /24 network
            network = ".".join(default_gateway.split(".")[:3]) + ".0/24"
            return network
        except:
            return "192.168.1.0/24"  # Fallback

    def port_scan_host(self, target_ip: str, ports: List[int] = None) -> NetworkHost:
        """Perform TCP port scan on a single host"""
        if ports is None:
            ports = self.COMMON_PORTS

        host = NetworkHost(ip=target_ip)

        if self.console:
            self.console.print(f"Scanning {target_ip}...")

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                sock.close()

                if result == 0:
                    host.open_ports.append(port)
                    host.services[port] = self.get_service_name(port)

            except Exception as e:
                logger.debug(f"Port scan error for {target_ip}:{port}: {e}")

        return host

    def network_scan(self, network_cidr: str = None) -> List[NetworkHost]:
        """Perform network discovery and port scanning"""
        if network_cidr is None:
            network_cidr = self.get_local_network()

        if self.console:
            self.console.print(f"Scanning network: {network_cidr}")

        discovered_hosts = []

        try:
            # ARP scan for host discovery
            if SCAPY_AVAILABLE:
                hosts = self.arp_scan(network_cidr)
            else:
                hosts = self.ping_sweep(network_cidr)

            # Port scan discovered hosts
            with Progress() as progress if self.console else None:
                if self.console:
                    task = progress.add_task(
                        "Port scanning...", total=len(hosts))

                for host_ip in hosts:
                    host = self.port_scan_host(host_ip)
                    discovered_hosts.append(host)

                    if self.console:
                        progress.update(task, advance=1)

            self.discovered_hosts = discovered_hosts
            return discovered_hosts

        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []

    def arp_scan(self, network_cidr: str) -> List[str]:
        """Perform ARP scan using Scapy"""
        if not SCAPY_AVAILABLE:
            return self.ping_sweep(network_cidr)

        try:
            # Create ARP request packet
            arp_request = scapy.ARP(pdst=network_cidr)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request

            # Send packets and get responses
            answered_list = scapy.srp(
                arp_request_broadcast, timeout=2, verbose=False)[0]

            hosts = []
            for element in answered_list:
                host_ip = element[1].psrc
                host_mac = element[1].hwsrc
                hosts.append(host_ip)

                if self.console:
                    self.console.print(f"Found: {host_ip} [{host_mac}]")

            return hosts

        except Exception as e:
            logger.error(f"ARP scan failed: {e}")
            return []

    def ping_sweep(self, network_cidr: str) -> List[str]:
        """Perform ping sweep for host discovery"""
        hosts = []
        network = ipaddress.ip_network(network_cidr, strict=False)

        def ping_host(ip):
            try:
                param = "-n 1" if os.name == "nt" else "-c 1"
                command = ["ping", param, str(ip)]
                result = subprocess.run(
                    command, capture_output=True, timeout=2)
                if result.returncode == 0:
                    hosts.append(str(ip))
                    if self.console:
                        self.console.print(f"Found: {ip}")
            except:
                pass

        # Threaded ping sweep
        threads = []
        for ip in network.hosts():
            if len(threads) >= 50:  # Limit concurrent threads
                for t in threads:
                    t.join()
                threads = []

            thread = threading.Thread(target=ping_host, args=(ip,))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        return hosts

    def get_service_name(self, port: int) -> str:
        """Get common service name for port"""
        service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S", 3389: "RDP"
        }
        return service_map.get(port, "Unknown")

    def display_scan_results(self):
        """Display network scan results in formatted table"""
        if not self.discovered_hosts:
            print("No hosts discovered")
            return

        if self.console:
            table = Table(title="Network Scan Results")
            table.add_column("IP Address", style="cyan")
            table.add_column("Hostname", style="green")
            table.add_column("Open Ports", style="yellow")
            table.add_column("Services", style="magenta")

            for host in self.discovered_hosts:
                ports_str = ", ".join(map(str, host.open_ports))
                services_str = ", ".join(host.services.values())

                table.add_row(
                    host.ip,
                    host.hostname,
                    ports_str,
                    services_str
                )

            self.console.print(table)
        else:
            print("\nNetwork Scan Results:")
            print("-" * 80)
            for host in self.discovered_hosts:
                print(f"IP: {host.ip}")
                print(f"Hostname: {host.hostname}")
                print(f"Open Ports: {', '.join(map(str, host.open_ports))}")
                print(f"Services: {', '.join(host.services.values())}")
                print("-" * 40)

    def start_packet_capture(self, interface: str = None, count: int = 100):
        """Start packet capture and analysis"""
        if not SCAPY_AVAILABLE:
            print("Scapy required for packet capture")
            return

        if self.console:
            self.console.print(
                f"Starting packet capture on {interface or 'default'}...")

        try:
            # Simple packet capture with analysis
            packets = scapy.sniff(iface=interface, count=count, timeout=30)
            self.analyze_packets(packets)

        except Exception as e:
            logger.error(f"Packet capture failed: {e}")

    def analyze_packets(self, packets):
        """Analyze captured packets for security insights"""
        if self.console:
            self.console.print(f"Analyzing {len(packets)} packets...")

        protocol_count = Counter()
        source_ips = Counter()
        destination_ips = Counter()

        for packet in packets:
            self.packet_count += 1

            # Count protocols
            if packet.haslayer(scapy.IP):
                protocol_count[packet[scapy.IP].proto] += 1
                source_ips[packet[scapy.IP].src] += 1
                destination_ips[packet[scapy.IP].dst] += 1

            # Detect potential security issues
            self.detect_security_events(packet)

        # Display analysis results
        if self.console:
            self.display_packet_analysis(
                protocol_count, source_ips, destination_ips)

    def detect_security_events(self, packet):
        """Detect potential security events in packets"""
        if packet.haslayer(scapy.TCP):
            # Detect port scanning
            if packet[scapy.TCP].flags == 2:  # SYN packet
                self.record_security_event(
                    "Port Scan Attempt",
                    packet[scapy.IP].src,
                    packet[scapy.IP].dst,
                    "TCP",
                    f"SYN packet to port {packet[scapy.TCP].dport}",
                    "MEDIUM"
                )

        if packet.haslayer(http.HTTPRequest):
            # Detect HTTP traffic (potential information leakage)
            host = packet[http.HTTPRequest].Host.decode(
            ) if packet[http.HTTPRequest].Host else "Unknown"
            self.record_security_event(
                "HTTP Traffic",
                packet[scapy.IP].src,
                host,
                "HTTP",
                f"HTTP request to {host}",
                "LOW"
            )

    def record_security_event(self, event_type: str, src_ip: str, dst_ip: str,
                              protocol: str, description: str, severity: str):
        """Record security event for monitoring"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            source_ip=src_ip,
            destination_ip=dst_ip,
            protocol=protocol,
            description=description,
            severity=severity
        )

        self.security_events.append(event)
        logger.warning(
            f"Security Event: {event_type} - {src_ip} -> {dst_ip} - {description}")

    def display_packet_analysis(self, protocol_count, source_ips, destination_ips):
        """Display packet analysis results"""
        # Protocol breakdown
        proto_table = Table(title="Protocol Distribution")
        proto_table.add_column("Protocol", style="cyan")
        proto_table.add_column("Count", style="green")
        proto_table.add_column("Percentage", style="yellow")

        total_packets = sum(protocol_count.values())
        for proto, count in protocol_count.most_common():
            percentage = (count / total_packets) * 100
            proto_name = self.get_protocol_name(proto)
            proto_table.add_row(proto_name, str(count), f"{percentage:.1f}%")

        self.console.print(proto_table)

        # Top talkers
        talkers_table = Table(title="Top Source IPs")
        talkers_table.add_column("IP Address", style="cyan")
        talkers_table.add_column("Packet Count", style="green")

        for ip, count in source_ips.most_common(5):
            talkers_table.add_row(ip, str(count))

        self.console.print(talkers_table)

    def get_protocol_name(self, proto_num: int) -> str:
        """Convert protocol number to name"""
        protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        return protocol_map.get(proto_num, f"Proto-{proto_num}")

    def start_security_monitoring(self, duration: int = 300):
        """Start continuous security monitoring"""
        if self.console:
            self.console.print(
                f"Starting security monitoring for {duration} seconds...")

        end_time = time.time() + duration

        try:
            while time.time() < end_time:
                # Perform periodic network scans
                current_hosts = self.network_scan()

                # Detect new hosts (potential intruders)
                self.detect_new_hosts(current_hosts)

                # Brief packet capture
                if SCAPY_AVAILABLE:
                    self.start_packet_capture(count=50)

                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            if self.console:
                self.console.print("Monitoring stopped by user")

    def detect_new_hosts(self, current_hosts: List[NetworkHost]):
        """Detect new hosts on the network"""
        current_ips = {host.ip for host in current_hosts}
        previous_ips = {host.ip for host in self.discovered_hosts}

        new_hosts = current_ips - previous_ips

        for ip in new_hosts:
            self.record_security_event(
                "New Host Detected",
                ip,
                "Network",
                "ARP",
                f"New device appeared on network: {ip}",
                "MEDIUM"
            )

        self.discovered_hosts = current_hosts

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        report = {
            "scan_date": datetime.now().isoformat(),
            "scan_duration": str(datetime.now() - self.start_time),
            "hosts_discovered": len(self.discovered_hosts),
            "packets_analyzed": self.packet_count,
            "security_events": len(self.security_events),
            "open_ports_by_host": {},
            "event_summary": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            }
        }

        # Collect open ports
        for host in self.discovered_hosts:
            report["open_ports_by_host"][host.ip] = {
                "ports": host.open_ports,
                "services": host.services
            }

        # Count security events by severity
        for event in self.security_events:
            report["event_summary"][event.severity] += 1

        # Save report to file
        with open('network_security_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def display_security_report(self):
        """Display security monitoring report"""
        report = self.generate_security_report()

        if self.console:
            # Summary panel
            summary_table = Table(title="Security Monitoring Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")

            summary_table.add_row("Hosts Discovered",
                                  str(report["hosts_discovered"]))
            summary_table.add_row("Packets Analyzed",
                                  str(report["packets_analyzed"]))
            summary_table.add_row(
                "Security Events", str(report["security_events"]))
            summary_table.add_row("Scan Duration", report["scan_duration"])

            self.console.print(summary_table)

            # Security events
            if self.security_events:
                events_table = Table(title="Recent Security Events")
                events_table.add_column("Time", style="cyan")
                events_table.add_column("Type", style="yellow")
                events_table.add_column("Source", style="red")
                events_table.add_column("Destination", style="green")
                events_table.add_column("Severity", style="magenta")

                for event in self.security_events[-10:]:  # Last 10 events
                    events_table.add_row(
                        event.timestamp.strftime("%H:%M:%S"),
                        event.event_type,
                        event.source_ip,
                        event.destination_ip,
                        event.severity
                    )

                self.console.print(events_table)

        else:
            print("\nSecurity Monitoring Report:")
            print(f"Hosts Discovered: {report['hosts_discovered']}")
            print(f"Packets Analyzed: {report['packets_analyzed']}")
            print(f"Security Events: {report['security_events']}")
            print(f"Scan Duration: {report['scan_duration']}")


class SimpleService:
    """Simple network service for demonstration"""

    def __init__(self, port: int = 9999):
        self.port = port
        self.is_running = False
        self.connection_log = []

    def start_service(self):
        """Start a simple TCP service"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)

            self.is_running = True
            print(f"Service started on port {self.port}")

            def handle_client(client_socket, address):
                self.connection_log.append({
                    'timestamp': datetime.now(),
                    'address': address,
                    'action': 'connected'
                })

                client_socket.send(b"Hello! This is a test service.\n")
                client_socket.close()

            def accept_connections():
                while self.is_running:
                    try:
                        client_socket, address = server_socket.accept()
                        client_thread = threading.Thread(
                            target=handle_client,
                            args=(client_socket, address)
                        )
                        client_thread.start()
                    except:
                        break

            accept_thread = threading.Thread(target=accept_connections)
            accept_thread.start()

            return server_socket

        except Exception as e:
            print(f"Failed to start service: {e}")
            return None

    def stop_service(self, server_socket):
        """Stop the service"""
        self.is_running = False
        if server_socket:
            server_socket.close()
        print("Service stopped")


def demonstrate_network_security():
    """Demonstrate network security concepts"""
    scanner = NetworkScanner()
    scanner.display_banner()

    print("\n1. Network Discovery Scan")
    print("2. Packet Capture & Analysis")
    print("3. Security Monitoring")
    print("4. Start Test Service")
    print("5. Generate Security Report")
    print("6. Exit")

    test_service = None
    service_socket = None

    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()

            if choice == "1":
                # Network scan
                network = input(
                    "Enter network CIDR (e.g., 192.168.1.0/24) or press Enter for auto-detect: ")
                hosts = scanner.network_scan(network if network else None)
                scanner.display_scan_results()

            elif choice == "2":
                # Packet capture
                if not SCAPY_AVAILABLE:
                    print(
                        "Scapy required for packet capture. Install with: pip install scapy")
                    continue

                count = input(
                    "Enter number of packets to capture (default 100): ")
                scanner.start_packet_capture(
                    count=int(count) if count.isdigit() else 100)

            elif choice == "3":
                # Security monitoring
                duration = input(
                    "Enter monitoring duration in seconds (default 300): ")
                scanner.start_security_monitoring(
                    duration=int(duration) if duration.isdigit() else 300
                )

            elif choice == "4":
                # Start test service
                if test_service is None:
                    test_service = SimpleService(9999)
                    service_socket = test_service.start_service()
                else:
                    print("Test service is already running")

            elif choice == "5":
                # Generate report
                scanner.display_security_report()

            elif choice == "6":
                # Exit
                if test_service and service_socket:
                    test_service.stop_service(service_socket)
                print("Goodbye!")
                break

            else:
                print("Invalid option")

        except KeyboardInterrupt:
            print("\nExiting...")
            if test_service and service_socket:
                test_service.stop_service(service_socket)
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Check for required permissions
    if os.name != 'nt' and os.geteuid() != 0:
        print("Note: Some features require root privileges for full functionality")
        print("Run with sudo for best results on Linux/Mac\n")

    demonstrate_network_security()
