"""
Network device simulator generating realistic network metrics and anomalies.
"""
import random
import math
import time
from typing import Dict, Any

class NetworkDeviceSimulator:
    def __init__(self, device_id: str, hostname: str, device_type: str = "switch", base_latency: float = 18.0, base_bandwidth: float = 30.0):
        self.device_id = device_id
        self.hostname = hostname
        self.device_type = device_type  # switch, router, firewall
        self.base_latency = base_latency
        self.base_bandwidth = base_bandwidth
        self.uptime_hours = random.uniform(100.0, 1500.0)
        self.active_fault: str | None = None
        self.fault_start_time: float | None = None
        self.step = random.uniform(0, 100)

    def set_fault(self, fault_type: str | None):
        self.active_fault = fault_type
        self.fault_start_time = time.time() if fault_type else None

    def tick(self, mode: str = "Normal") -> Dict[str, Any]:
        self.step += 0.2
        self.uptime_hours += 0.001

        # Periodic traffic variation
        wave = math.sin(self.step) * 10.0
        bandwidth = max(5.0, min(95.0, self.base_bandwidth + wave + random.gauss(0, 3.0)))
        latency = max(2.0, self.base_latency + (bandwidth * 0.2) + random.gauss(0, 1.5))
        packet_loss = max(0.0, min(0.2, random.gauss(0.02, 0.03)))
        cpu = max(10.0, min(70.0, 15.0 + (bandwidth * 0.4) + random.gauss(0, 2.0)))
        mem = max(20.0, min(65.0, 30.0 + random.gauss(0, 1.0)))
        disk = max(15.0, 25.0 + random.gauss(0, 0.5))
        throughput = round(bandwidth * 12.8, 2)
        processes = int(80 + (cpu * 0.3))
        response_time = round(latency * 1.2, 2)
        availability = 1.0
        conn_status = 1
        dns_status = 1

        # Mode adjustments
        if mode == "Warning":
            latency = max(latency, random.uniform(110.0, 185.0))
            packet_loss = max(packet_loss, random.uniform(1.5, 4.5))
            bandwidth = max(bandwidth, random.uniform(75.0, 88.0))
        elif mode == "Critical":
            latency = max(latency, random.uniform(210.0, 420.0))
            packet_loss = max(packet_loss, random.uniform(6.0, 18.0))
            bandwidth = max(bandwidth, random.uniform(89.0, 98.0))

        # Fault injections
        if self.active_fault == "Network Failure":
            availability = 0.0
            conn_status = 0
            packet_loss = 100.0
            latency = 0.0
            bandwidth = 0.0
            throughput = 0.0
        elif self.active_fault == "High Latency":
            latency = random.uniform(220.0, 450.0)
            response_time = latency * 1.5
        elif self.active_fault == "Packet Loss":
            packet_loss = random.uniform(6.5, 25.0)
        elif self.active_fault == "DNS Failure":
            dns_status = 0
            response_time = 250.0
        elif self.active_fault == "Server Overload":
            cpu = random.uniform(88.0, 97.0)
            bandwidth = random.uniform(85.0, 95.0)

        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "device_type": self.device_type,
            "cpu_utilization": round(cpu, 2),
            "memory_utilization": round(mem, 2),
            "disk_utilization": round(disk, 2),
            "server_uptime": round(self.uptime_hours, 2),
            "process_count": int(processes),
            "response_time": round(response_time, 2),
            "server_availability": round(availability, 2),
            "network_latency": round(latency, 2),
            "packet_loss": round(packet_loss, 2),
            "bandwidth_utilization": round(bandwidth, 2),
            "network_throughput": round(throughput, 2),
            "connection_status": int(conn_status),
            "dns_response_status": int(dns_status),
            "network_availability": round(availability, 2),
        }
