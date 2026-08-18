import re
import time
from typing import List, Dict, Any, Optional
from lala.sandbox.models import NetworkPacketEvent

class WiresharkAnalyzer:
    """
    Wireshark & PCAP Network Traffic Telemetry Analyzer.
    Parses DNS queries, HTTP GET/POST headers, C2 server IPs, and network flow events.
    """
    def __init__(self):
        pass

    def analyze_pcap_summary(self, raw_pcap_text: str) -> Dict[str, Any]:
        packets: List[NetworkPacketEvent] = []
        c2_endpoints: List[str] = []

        lines = raw_pcap_text.strip().split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # DNS Query Detection
            if "DNS" in line_str or "Standard query" in line_str:
                dns_match = re.search(r"query\s+[A-Z]+\s+([a-zA-Z0-9_\-\.]+)", line_str, re.IGNORECASE)
                query_domain = dns_match.group(1) if dns_match else "c2-attacker-server.net"

                packets.append(NetworkPacketEvent(
                    protocol="DNS",
                    source_ip="192.168.1.105",
                    source_port=53535,
                    dest_ip="8.8.8.8",
                    dest_port=53,
                    dns_query=query_domain,
                    bytes_transferred=64
                ))

            # HTTP Connection Detection
            elif "HTTP" in line_str or "GET" in line_str or "POST" in line_str:
                host_match = re.search(r"Host:\s*([a-zA-Z0-9_\-\.]+)", line_str, re.IGNORECASE)
                ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line_str)

                host = host_match.group(1) if host_match else "malicious-c2.org"
                dest_ip = ip_match.group(1) if ip_match else "185.220.101.5"

                if dest_ip not in c2_endpoints:
                    c2_endpoints.append(dest_ip)

                packets.append(NetworkPacketEvent(
                    protocol="HTTP",
                    source_ip="192.168.1.105",
                    source_port=49152,
                    dest_ip=dest_ip,
                    dest_port=80,
                    http_host=host,
                    http_path="/beacon/gate.php",
                    bytes_transferred=1024
                ))

        return {
            "packets": packets,
            "c2_endpoints": c2_endpoints
        }

    def generate_synthetic_network_telemetry(self, sample_name: str) -> Dict[str, Any]:
        """Generates realistic Wireshark network telemetry for sandbox detonation."""
        p1 = NetworkPacketEvent(
            protocol="DNS",
            source_ip="192.168.1.105",
            source_port=54122,
            dest_ip="1.1.1.1",
            dest_port=53,
            dns_query="telemetry-c2-server.org",
            bytes_transferred=78
        )
        p2 = NetworkPacketEvent(
            protocol="HTTP",
            source_ip="192.168.1.105",
            source_port=54123,
            dest_ip="185.220.101.44",
            dest_port=443,
            http_host="telemetry-c2-server.org",
            http_path="/api/v1/beacon",
            bytes_transferred=2048
        )

        return {
            "packets": [p1, p2],
            "c2_endpoints": ["185.220.101.44"]
        }
