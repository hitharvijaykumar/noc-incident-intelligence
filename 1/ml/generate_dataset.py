"""
Synthetic labeled dataset generator for NOC incident intelligence.
Generates at least 10,000 realistic rows across 8 operational classes.
"""
import os
import random
import numpy as np
import pandas as pd
from pathlib import Path
from backend.config import settings
from backend.utils.logger import logger

FEATURES = [
    "cpu_utilization",
    "memory_utilization",
    "disk_utilization",
    "network_latency",
    "packet_loss",
    "bandwidth_utilization",
    "server_availability",
    "dns_response_status",
    "response_time",
    "connection_status",
    "process_count",
]

TARGET = "incident_type"

CLASSES = [
    "Normal",
    "Server Overload",
    "Memory Exhaustion",
    "Disk Capacity Issue",
    "Network Failure",
    "High Latency",
    "Packet Loss",
    "DNS Failure",
]

def generate_synthetic_dataset(n_samples: int = 12000, output_path: Path = None) -> pd.DataFrame:
    """
    Generates realistic, physically-correlated synthetic metrics for NOC training.
    """
    np.random.seed(settings.RANDOM_SEED)
    random.seed(settings.RANDOM_SEED)

    if output_path is None:
        output_path = settings.DATA_DIR / "training_data.csv"

    # Number of samples per class
    # Allocate ~30% to Normal, and ~10% to each of the 7 incident types
    normal_count = int(n_samples * 0.30)
    incident_count = (n_samples - normal_count) // 7

    rows = []

    def make_normal(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(35, 12), 5, 68))
            mem = float(np.clip(np.random.normal(45, 12), 10, 72))
            disk = float(np.clip(np.random.normal(50, 14), 10, 78))
            latency = float(np.clip(np.random.normal(25, 12), 3, 90))
            packet_loss = float(np.clip(np.random.exponential(0.1), 0.0, 0.95))
            bw = float(np.clip(cpu * 0.5 + np.random.normal(15, 8), 5, 75))
            avail = 1.0
            dns = 1
            conn = 1
            proc = int(np.clip(120 + cpu * 0.6 + np.random.normal(0, 10), 80, 220))
            resp = float(np.clip(latency * 0.9 + cpu * 0.4 + np.random.normal(5, 3), 3, 75))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Normal"
            })

    def make_server_overload(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(91, 4), 85, 99.5))
            mem = float(np.clip(np.random.normal(68, 12), 40, 88))
            disk = float(np.clip(np.random.normal(55, 15), 20, 85))
            latency = float(np.clip(np.random.normal(45, 15), 15, 110))
            packet_loss = float(np.clip(np.random.exponential(0.3), 0.0, 2.0))
            bw = float(np.clip(np.random.normal(70, 12), 40, 95))
            avail = 1.0
            dns = 1
            conn = 1
            proc = int(np.clip(np.random.normal(420, 60), 280, 700))
            resp = float(np.clip(cpu * 1.8 + np.random.normal(50, 20), 120, 500))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Server Overload"
            })

    def make_memory_exhaustion(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(65, 15), 25, 88))
            mem = float(np.clip(np.random.normal(94, 3), 90, 99.5))
            disk = float(np.clip(np.random.normal(58, 14), 20, 85))
            latency = float(np.clip(np.random.normal(40, 15), 10, 100))
            packet_loss = float(np.clip(np.random.exponential(0.2), 0.0, 1.5))
            bw = float(np.clip(np.random.normal(50, 15), 15, 80))
            avail = 1.0
            dns = 1
            conn = 1
            proc = int(np.clip(np.random.normal(260, 40), 150, 450))
            resp = float(np.clip(mem * 1.5 + np.random.normal(40, 15), 100, 380))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Memory Exhaustion"
            })

    def make_disk_capacity(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(40, 12), 15, 75))
            mem = float(np.clip(np.random.normal(52, 14), 20, 80))
            disk = float(np.clip(np.random.normal(94, 2.5), 90.1, 99.8))
            latency = float(np.clip(np.random.normal(30, 12), 5, 85))
            packet_loss = float(np.clip(np.random.exponential(0.1), 0.0, 1.0))
            bw = float(np.clip(np.random.normal(40, 15), 10, 75))
            avail = 1.0
            dns = 1
            conn = 1
            proc = int(np.clip(np.random.normal(150, 25), 90, 240))
            resp = float(np.clip(disk * 0.8 + np.random.normal(10, 5), 20, 150))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Disk Capacity Issue"
            })

    def make_network_failure(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(10, 5), 0, 30))
            mem = float(np.clip(np.random.normal(30, 8), 5, 50))
            disk = float(np.clip(np.random.normal(45, 12), 10, 70))
            latency = 0.0
            packet_loss = 100.0
            bw = 0.0
            avail = 0.0
            dns = 0
            conn = 0
            proc = int(np.clip(np.random.normal(80, 15), 40, 120))
            resp = 0.0
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Network Failure"
            })

    def make_high_latency(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(42, 12), 15, 75))
            mem = float(np.clip(np.random.normal(50, 12), 20, 75))
            disk = float(np.clip(np.random.normal(48, 12), 15, 75))
            latency = float(np.clip(np.random.normal(260, 45), 200, 550))
            packet_loss = float(np.clip(np.random.exponential(0.6), 0.0, 3.5))
            bw = float(np.clip(np.random.normal(82, 10), 60, 98))
            avail = 1.0
            dns = 1
            conn = 1
            proc = int(np.clip(np.random.normal(160, 25), 100, 250))
            resp = float(np.clip(latency * 1.3 + np.random.normal(20, 10), 220, 650))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "High Latency"
            })

    def make_packet_loss(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(45, 14), 15, 78))
            mem = float(np.clip(np.random.normal(50, 12), 20, 75))
            disk = float(np.clip(np.random.normal(45, 12), 15, 75))
            latency = float(np.clip(np.random.normal(90, 30), 25, 180))
            packet_loss = float(np.clip(np.random.normal(12.0, 4.0), 5.1, 35.0))
            bw = float(np.clip(np.random.normal(65, 15), 25, 92))
            avail = 1.0
            dns = 1 if np.random.rand() > 0.1 else 0
            conn = 1
            proc = int(np.clip(np.random.normal(150, 25), 90, 230))
            resp = float(np.clip(latency * 1.5 + packet_loss * 5.0, 60, 320))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "Packet Loss"
            })

    def make_dns_failure(n):
        for _ in range(n):
            cpu = float(np.clip(np.random.normal(38, 12), 12, 70))
            mem = float(np.clip(np.random.normal(46, 12), 18, 72))
            disk = float(np.clip(np.random.normal(46, 12), 15, 72))
            latency = float(np.clip(np.random.normal(70, 25), 20, 160))
            packet_loss = float(np.clip(np.random.exponential(0.3), 0.0, 2.5))
            bw = float(np.clip(np.random.normal(35, 15), 10, 75))
            avail = 1.0
            dns = 0  # DNS failure indicator
            conn = 1
            proc = int(np.clip(np.random.normal(140, 20), 85, 210))
            resp = float(np.clip(np.random.normal(240, 40), 120, 450))
            rows.append({
                "cpu_utilization": round(cpu, 2),
                "memory_utilization": round(mem, 2),
                "disk_utilization": round(disk, 2),
                "network_latency": round(latency, 2),
                "packet_loss": round(packet_loss, 2),
                "bandwidth_utilization": round(bw, 2),
                "server_availability": avail,
                "dns_response_status": dns,
                "response_time": round(resp, 2),
                "connection_status": conn,
                "process_count": proc,
                "incident_type": "DNS Failure"
            })

    make_normal(normal_count)
    make_server_overload(incident_count)
    make_memory_exhaustion(incident_count)
    make_disk_capacity(incident_count)
    make_network_failure(incident_count)
    make_high_latency(incident_count)
    make_packet_loss(incident_count)
    make_dns_failure(incident_count)

    df = pd.DataFrame(rows)
    # Shuffle
    df = df.sample(frac=1.0, random_state=settings.RANDOM_SEED).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Generated %d synthetic rows saved to %s", len(df), output_path)
    return df

if __name__ == "__main__":
    generate_synthetic_dataset(12000)
