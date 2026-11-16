"""
Server simulator generating realistic performance metrics and anomalies.
"""
import random
import math
import time
from typing import Dict, Any

class ServerSimulator:
    def __init__(self, device_id: str, hostname: str, base_cpu: float = 35.0, base_mem: float = 45.0, base_disk: float = 50.0):
        self.device_id = device_id
        self.hostname = hostname
        self.base_cpu = base_cpu
        self.base_mem = base_mem
        self.base_disk = base_disk
        self.uptime_hours = random.uniform(24.0, 720.0)
        self.process_count = random.randint(110, 190)
        self.active_fault: str | None = None
        self.fault_start_time: float | None = None
        self.step = random.uniform(0, 100)

    def set_fault(self, fault_type: str | None):
        self.active_fault = fault_type
        self.fault_start_time = time.time() if fault_type else None

    def tick(self, mode: str = "Normal") -> Dict[str, Any]:
        self.step += 0.2
        self.uptime_hours += 0.001

        # Base diurnal rhythm + noise
        rhythm = math.sin(self.step) * 8.0
        jitter = random.gauss(0, 2.5)

        cpu = max(5.0, min(99.0, self.base_cpu + rhythm + jitter))
        mem = max(10.0, min(99.0, self.base_mem + (rhythm * 0.4) + random.gauss(0, 1.0)))
        disk = max(10.0, min(99.0, self.base_disk + (self.step * 0.005) + random.gauss(0, 0.2)))
        processes = int(max(50, self.process_count + (cpu * 0.5) + random.randint(-5, 5)))
        response_time = max(2.0, (cpu * 0.8) + (mem * 0.3) + random.gauss(0, 3.0))
        availability = 1.0
        conn_status = 1
        dns_status = 1
        latency = max(5.0, 15.0 + random.gauss(0, 2.0))
        packet_loss = max(0.0, min(0.3, random.gauss(0.05, 0.05)))
        bandwidth = max(5.0, min(95.0, (cpu * 0.6) + random.gauss(0, 4.0)))

        # Mode influences
        if mode == "Warning":
            cpu = max(cpu, random.uniform(72.0, 83.0))
            mem = max(mem, random.uniform(76.0, 88.0))
            disk = max(disk, random.uniform(81.0, 88.0))
            response_time += 45.0
        elif mode == "Critical":
            cpu = max(cpu, random.uniform(88.0, 99.0))
            mem = max(mem, random.uniform(92.0, 98.0))
            disk = max(disk, random.uniform(91.0, 97.0))
            response_time += 150.0

        # Inject Active Faults
        if self.active_fault == "Server Overload":
            cpu = random.uniform(88.0, 98.5)
            processes = random.randint(350, 600)
            response_time = random.uniform(180.0, 450.0)
        elif self.active_fault == "Memory Exhaustion":
            mem = random.uniform(91.0, 98.8)
            response_time = random.uniform(120.0, 300.0)
        elif self.active_fault == "Disk Capacity Issue":
            disk = random.uniform(92.0, 99.2)
        elif self.active_fault == "Server Downtime" or self.active_fault == "Network Failure":
            availability = 0.0
            conn_status = 0
            response_time = 0.0
            cpu = 0.0
            mem = 0.0
            packet_loss = 100.0
        elif self.active_fault == "High Latency":
            latency = random.uniform(220.0, 480.0)
            response_time += 200.0
        elif self.active_fault == "Packet Loss":
            packet_loss = random.uniform(6.0, 22.0)
        elif self.active_fault == "DNS Failure":
            dns_status = 0
            response_time += 100.0

        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "device_type": "server",
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
            "network_throughput": round(bandwidth * 10.5, 2),
            "connection_status": int(conn_status),
            "dns_response_status": int(dns_status),
            "network_availability": round(availability, 2),
        }
