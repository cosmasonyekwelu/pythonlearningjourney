"""
Day 41: Network Scanning & Monitoring
Comprehensive network security toolkit for scanning, monitoring, and packet analysis.
"""

from __future__ import annotations

import os
import sys
import socket
import subprocess
import threading
import time
import json
import logging
from contextlib import closing
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import Counter
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------- Optional third-party deps ----------------------------

SCAPY_AVAILABLE = False
HTTP_LAYER_AVAILABLE = False
try:
    import scapy.all as scapy  # type: ignore
    from scapy.layers import http as scapy_http  # type: ignore
    SCAPY_AVAILABLE = True
    HTTP_LAYER_AVAILABLE = hasattr(scapy_http, "HTTPRequest")
except Exception:
    print("Note: Scapy not available. Install with: pip install scapy")

RICH_AVAILABLE = False
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    RICH_AVAILABLE = True
except Exception:
    print("Note: Rich not available. Install with: pip install rich")

# ---------------------------- Logging ----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(
        "network_security.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("NetworkSecurity")

# ---------------------------- Models ----------------------------


@dataclass
class NetworkHost:
    """Represents a discovered network host"""
    ip: str
    mac: str = "Unknown"
    hostname: str = "Unknown"
    os: str = "Unknown"
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)


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

# ---------------------------- Core Scanner ----------------------------


class NetworkScanner:
    """Comprehensive network scanning and monitoring tool"""

    COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389]

    def __init__(self) -> None:
        self.console: Optional[Console] = Console() if RICH_AVAILABLE else None
        self.discovered_hosts: List[NetworkHost] = []
        self.security_events: List[SecurityEvent] = []
        self.packet_count: int = 0
        self.start_time: datetime = datetime.now()

    # ---------- UI ----------

    def display_banner(self) -> None:
        if self.console:
            self.console.print(
                Panel.fit("Network Security Scanner & Monitor", style="bold blue"))
        else:
            print("Network Security Scanner & Monitor")
            print("=" * 50)

    # ---------- Helpers ----------

    def get_local_network(self) -> str:
        """Try to infer local IPv4 network; fallback to 192.168.1.0/24."""
        try:
            import netifaces  # type: ignore
            gateways = netifaces.gateways()
            default_gw = gateways.get("default", {}).get(netifaces.AF_INET)
            if default_gw:
                gw_ip = default_gw[0]
                cidr = ".".join(gw_ip.split(".")[:3]) + ".0/24"
                return cidr
        except Exception:
            pass
        return "192.168.1.0/24"

    @staticmethod
    def get_service_name(port: int) -> str:
        service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S", 3389: "RDP",
        }
        return service_map.get(port, "Unknown")

    @staticmethod
    def get_protocol_name(proto_num: int) -> str:
        protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        return protocol_map.get(proto_num, f"Proto-{proto_num}")

    # ---------- Host discovery & port scan ----------

    def port_scan_host(self, target_ip: str, ports: Optional[List[int]] = None, timeout: float = 0.8) -> NetworkHost:
        if ports is None:
            ports = self.COMMON_PORTS

        host = NetworkHost(ip=target_ip)

        for port in ports:
            try:
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.settimeout(timeout)
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        host.open_ports.append(port)
                        host.services[port] = self.get_service_name(port)
            except Exception as e:
                logger.debug(f"Port scan error for {target_ip}:{port}: {e}")

        # Try reverse DNS (non-fatal)
        try:
            host.hostname = socket.gethostbyaddr(target_ip)[0]
        except Exception:
            pass

        return host

    def arp_scan(self, network_cidr: str) -> List[str]:
        """Perform ARP scan using Scapy if available; else fallback to ping sweep."""
        if not SCAPY_AVAILABLE:
            return self.ping_sweep(network_cidr)

        try:
            arp_request = scapy.ARP(pdst=network_cidr)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = scapy.srp(
                arp_request_broadcast, timeout=2, verbose=False)[0]

            hosts: List[str] = []
            for sent, received in answered_list:
                host_ip = received.psrc
                host_mac = received.hwsrc
                hosts.append(host_ip)
                if self.console:
                    self.console.print(f"Found: {host_ip} [{host_mac}]")
            return hosts
        except Exception as e:
            logger.error(f"ARP scan failed: {e}")
            return []

    def ping_sweep(self, network_cidr: str, max_workers: int = 64) -> List[str]:
        """Thread-pooled ping sweep for host discovery (cross-platform)."""
        hosts: List[str] = []
        network = ipaddress.ip_network(network_cidr, strict=False)

        # Windows uses -n, Unix uses -c; also add a short timeout
        is_windows = os.name == "nt"
        count_flag = ["-n", "1"] if is_windows else ["-c", "1"]
        # ms vs seconds
        timeout_flag = ["-w", "1000"] if is_windows else ["-W", "1"]

        def ping_one(ip: str) -> Optional[str]:
            try:
                cmd = ["ping", *count_flag, *timeout_flag, ip]
                result = subprocess.run(cmd, capture_output=True, timeout=2)
                if result.returncode == 0:
                    return ip
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(ping_one, str(
                ip)): ip for ip in network.hosts()}
            for fut in as_completed(futures):
                out = fut.result()
                if out:
                    hosts.append(out)
                    if self.console:
                        self.console.print(f"Found: {out}")

        return hosts

    def network_scan(self, network_cidr: Optional[str] = None) -> List[NetworkHost]:
        """Perform discovery then port scan on discovered hosts."""
        if network_cidr is None:
            network_cidr = self.get_local_network()

        if self.console:
            self.console.print(f"Scanning network: {network_cidr}")

        try:
            hosts_ips = self.arp_scan(
                network_cidr) if SCAPY_AVAILABLE else self.ping_sweep(network_cidr)

            discovered: List[NetworkHost] = []
            if RICH_AVAILABLE and self.console:
                with Progress() as progress:
                    task = progress.add_task(
                        "Port scanning...", total=len(hosts_ips) or 1)
                    for ip in hosts_ips:
                        host = self.port_scan_host(ip)
                        discovered.append(host)
                        progress.update(task, advance=1)
            else:
                for ip in hosts_ips:
                    host = self.port_scan_host(ip)
                    discovered.append(host)

            self.discovered_hosts = discovered
            return discovered
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []

    # ---------- Packet capture & analysis ----------

    def start_packet_capture(self, interface: Optional[str] = None, count: int = 100) -> None:
        if not SCAPY_AVAILABLE:
            print("Scapy required for packet capture")
            return
        if self.console:
            self.console.print(
                f"Starting packet capture on {interface or 'default'}...")

        try:
            packets = scapy.sniff(iface=interface, count=count, timeout=30)
            self.analyze_packets(packets)
        except Exception as e:
            logger.error(f"Packet capture failed: {e}")

    def analyze_packets(self, packets: Any) -> None:
        if self.console:
            self.console.print(f"Analyzing {len(packets)} packets...")

        protocol_count: Counter[int] = Counter()
        source_ips: Counter[str] = Counter()
        destination_ips: Counter[str] = Counter()

        for packet in packets:
            self.packet_count += 1

            if hasattr(packet, "haslayer") and packet.haslayer(getattr(scapy, "IP", None)):
                ip_layer = packet[scapy.IP]
                protocol_count[ip_layer.proto] += 1
                source_ips[ip_layer.src] += 1
                destination_ips[ip_layer.dst] += 1

            self.detect_security_events(packet)

        if self.console:
            self.display_packet_analysis(
                protocol_count, source_ips, destination_ips)

    def detect_security_events(self, packet: Any) -> None:
        if not hasattr(packet, "haslayer"):
            return

        # SYN detection (potential scan)
        if SCAPY_AVAILABLE and packet.haslayer(getattr(scapy, "TCP", None)) and packet.haslayer(getattr(scapy, "IP", None)):
            try:
                tcp = packet[scapy.TCP]
                ip_ = packet[scapy.IP]
                # TCP flags: 0x02 == SYN
                if getattr(tcp, "flags", 0) == 0x02:
                    self.record_security_event(
                        "Port Scan Attempt",
                        ip_.src,
                        ip_.dst,
                        "TCP",
                        f"SYN packet to port {tcp.dport}",
                        "MEDIUM",
                    )
            except Exception:
                pass

        # HTTP request visibility
        if SCAPY_AVAILABLE and HTTP_LAYER_AVAILABLE and packet.haslayer(scapy_http.HTTPRequest) and packet.haslayer(scapy.IP):
            try:
                host_bytes = packet[scapy_http.HTTPRequest].Host
                host_str = host_bytes.decode() if isinstance(
                    host_bytes, (bytes, bytearray)) else (host_bytes or "Unknown")
                ip_ = packet[scapy.IP]
                self.record_security_event(
                    "HTTP Traffic",
                    ip_.src,
                    str(host_str),
                    "HTTP",
                    f"HTTP request to {host_str}",
                    "LOW",
                )
            except Exception:
                pass

    def record_security_event(self, event_type: str, src_ip: str, dst_ip: str,
                              protocol: str, description: str, severity: str) -> None:
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            source_ip=src_ip,
            destination_ip=dst_ip,
            protocol=protocol,
            description=description,
            severity=severity,
        )
        self.security_events.append(event)
        logger.warning(
            f"Security Event: {event_type} - {src_ip} -> {dst_ip} - {description} [{severity}]")

    # ---------- Displays ----------

    def display_scan_results(self) -> None:
        if not self.discovered_hosts:
            print("No hosts discovered")
            return

        if self.console and RICH_AVAILABLE:
            table = Table(title="Network Scan Results")
            table.add_column("IP Address", style="cyan")
            table.add_column("Hostname", style="green")
            table.add_column("Open Ports", style="yellow")
            table.add_column("Services", style="magenta")

            for host in self.discovered_hosts:
                ports_str = ", ".join(map(str, host.open_ports)) or "-"
                services_str = ", ".join(host.services.get(
                    p, "Unknown") for p in host.open_ports) or "-"
                table.add_row(host.ip, host.hostname, ports_str, services_str)

            self.console.print(table)
        else:
            print("\nNetwork Scan Results:")
            print("-" * 80)
            for host in self.discovered_hosts:
                print(f"IP: {host.ip}")
                print(f"Hostname: {host.hostname}")
                print(
                    f"Open Ports: {', '.join(map(str, host.open_ports)) or '-'}")
                if host.open_ports:
                    print("Services:", ", ".join(host.services.get(
                        p, 'Unknown') for p in host.open_ports))
                print("-" * 40)

    def display_packet_analysis(self, protocol_count: Counter[int], source_ips: Counter[str],
                                destination_ips: Counter[str]) -> None:
        if not (self.console and RICH_AVAILABLE):
            # Minimal stdout fallback
            total = sum(protocol_count.values())
            print("\nProtocol Distribution:")
            for proto, cnt in protocol_count.most_common():
                name = self.get_protocol_name(proto)
                pct = (cnt / total * 100) if total else 0
                print(f"- {name}: {cnt} ({pct:.1f}%)")
            print("\nTop Source IPs:")
            for ip, cnt in source_ips.most_common(5):
                print(f"- {ip}: {cnt}")
            return

        # Rich tables
        proto_table = Table(title="Protocol Distribution")
        proto_table.add_column("Protocol", style="cyan")
        proto_table.add_column("Count", style="green")
        proto_table.add_column("Percentage", style="yellow")

        total_packets = sum(protocol_count.values()) or 1
        for proto, count in protocol_count.most_common():
            percentage = (count / total_packets) * 100
            proto_name = self.get_protocol_name(proto)
            proto_table.add_row(proto_name, str(count), f"{percentage:.1f}%")

        self.console.print(proto_table)

        talkers_table = Table(title="Top Source IPs")
        talkers_table.add_column("IP Address", style="cyan")
        talkers_table.add_column("Packet Count", style="green")
        for ip, count in source_ips.most_common(5):
            talkers_table.add_row(ip, str(count))
        self.console.print(talkers_table)

    # ---------- Monitoring & Reporting ----------

    def detect_new_hosts(self, current_hosts: List[NetworkHost]) -> None:
        current_ips = {host.ip for host in current_hosts}
        previous_ips = {host.ip for host in self.discovered_hosts}
        new_ips = current_ips - previous_ips

        for ip in new_ips:
            self.record_security_event(
                "New Host Detected",
                ip,
                "Network",
                "ARP",
                f"New device appeared on network: {ip}",
                "MEDIUM",
            )

        self.discovered_hosts = current_hosts

    def start_security_monitoring(self, duration: int = 300) -> None:
        if self.console:
            self.console.print(
                f"Starting security monitoring for {duration} seconds...")

        end_time = time.time() + duration
        try:
            while time.time() < end_time:
                current_hosts = self.network_scan()
                self.detect_new_hosts(current_hosts)
                if SCAPY_AVAILABLE:
                    self.start_packet_capture(count=50)
                time.sleep(30)  # Adjust cadence as needed
        except KeyboardInterrupt:
            if self.console:
                self.console.print("Monitoring stopped by user")

    def generate_security_report(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "scan_date": datetime.now().isoformat(),
            "scan_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "hosts_discovered": len(self.discovered_hosts),
            "packets_analyzed": self.packet_count,
            "security_events": len(self.security_events),
            "open_ports_by_host": {},
            "event_summary": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }

        for host in self.discovered_hosts:
            report["open_ports_by_host"][host.ip] = {
                "hostname": host.hostname,
                "ports": host.open_ports,
                "services": host.services,
            }

        for event in self.security_events:
            report["event_summary"][event.severity] = report["event_summary"].get(
                event.severity, 0) + 1

        with open("network_security_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def display_security_report(self) -> None:
        report = self.generate_security_report()

        if self.console and RICH_AVAILABLE:
            summary_table = Table(title="Security Monitoring Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            summary_table.add_row("Hosts Discovered",
                                  str(report["hosts_discovered"]))
            summary_table.add_row("Packets Analyzed",
                                  str(report["packets_analyzed"]))
            summary_table.add_row(
                "Security Events", str(report["security_events"]))
            summary_table.add_row("Scan Duration (s)",
                                  f"{report['scan_duration_seconds']:.0f}")
            self.console.print(summary_table)

            if self.security_events:
                events_table = Table(title="Recent Security Events")
                events_table.add_column("Time", style="cyan")
                events_table.add_column("Type", style="yellow")
                events_table.add_column("Source", style="red")
                events_table.add_column("Destination", style="green")
                events_table.add_column("Severity", style="magenta")

                for event in self.security_events[-10:]:
                    events_table.add_row(
                        event.timestamp.strftime("%H:%M:%S"),
                        event.event_type,
                        event.source_ip,
                        event.destination_ip,
                        event.severity,
                    )
                self.console.print(events_table)
        else:
            print("\nSecurity Monitoring Report:")
            print(f"Hosts Discovered: {report['hosts_discovered']}")
            print(f"Packets Analyzed: {report['packets_analyzed']}")
            print(f"Security Events: {report['security_events']}")
            print(f"Scan Duration (s): {report['scan_duration_seconds']:.0f}")

# ---------------------------- Simple demo service ----------------------------


class SimpleService:
    """Simple TCP service for demonstration"""

    def __init__(self, port: int = 9999):
        self.port = port
        self.is_running = False
        self.connection_log: List[Dict[str, Any]] = []
        self._accept_thread: Optional[threading.Thread] = None

    def start_service(self) -> Optional[socket.socket]:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", self.port))
            server_socket.listen(5)
            self.is_running = True
            print(f"Service started on port {self.port}")

            def handle_client(client_socket: socket.socket, address: Tuple[str, int]) -> None:
                try:
                    self.connection_log.append(
                        {"timestamp": datetime.now().isoformat(
                        ), "address": address, "action": "connected"}
                    )
                    client_socket.send(b"Hello! This is a test service.\n")
                except Exception as e:
                    logger.debug(f"Client handler error: {e}")
                finally:
                    try:
                        client_socket.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    client_socket.close()

            def accept_loop() -> None:
                while self.is_running:
                    try:
                        client_socket, address = server_socket.accept()
                        t = threading.Thread(target=handle_client, args=(
                            client_socket, address), daemon=True)
                        t.start()
                    except OSError:
                        break
                    except Exception as e:
                        logger.debug(f"Accept error: {e}")
                        break

            self._accept_thread = threading.Thread(
                target=accept_loop, daemon=True)
            self._accept_thread.start()
            return server_socket

        except Exception as e:
            print(f"Failed to start service: {e}")
            return None

    def stop_service(self, server_socket: Optional[socket.socket]) -> None:
        self.is_running = False
        if server_socket:
            try:
                server_socket.close()
            except Exception:
                pass
        if self._accept_thread and self._accept_thread.is_alive():
            self._accept_thread.join(timeout=1.0)
        print("Service stopped")

# ---------------------------- CLI Demo ----------------------------


def demonstrate_network_security() -> None:
    scanner = NetworkScanner()
    scanner.display_banner()

    print("\n1. Network Discovery Scan")
    print("2. Packet Capture & Analysis")
    print("3. Security Monitoring")
    print("4. Start Test Service")
    print("5. Generate Security Report")
    print("6. Exit")

    test_service: Optional[SimpleService] = None
    service_socket: Optional[socket.socket] = None

    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()

            if choice == "1":
                network = input(
                    "Enter network CIDR (e.g., 192.168.1.0/24) or press Enter for auto-detect: ").strip()
                scanner.network_scan(network if network else None)
                scanner.display_scan_results()

            elif choice == "2":
                if not SCAPY_AVAILABLE:
                    print(
                        "Scapy required for packet capture. Install with: pip install scapy")
                    continue
                count = input(
                    "Enter number of packets to capture (default 100): ").strip()
                scanner.start_packet_capture(
                    count=int(count) if count.isdigit() else 100)

            elif choice == "3":
                duration = input(
                    "Enter monitoring duration in seconds (default 300): ").strip()
                scanner.start_security_monitoring(duration=int(
                    duration) if duration.isdigit() else 300)

            elif choice == "4":
                if test_service is None:
                    test_service = SimpleService(9999)
                    service_socket = test_service.start_service()
                else:
                    print("Test service is already running")

            elif choice == "5":
                scanner.display_security_report()
                print('Report saved to "network_security_report.json"')

            elif choice == "6":
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

# ---------------------------- Entrypoint ----------------------------


if __name__ == "__main__":
    try:
        if os.name != "nt":
            # On Windows, os.geteuid() is not available.
            if hasattr(os, "geteuid") and os.geteuid() != 0:
                print(
                    "Note: Some features require root privileges for full functionality")
                print("Run with sudo for best results on Linux/Mac\n")
    except Exception:
        pass

    demonstrate_network_security()
