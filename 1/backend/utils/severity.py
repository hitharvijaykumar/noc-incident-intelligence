"""
Severity calculation engine for NOC Incident Intelligence System.
"""
from typing import Dict, Any, Optional

def calculate_severity(
    category: str,
    metrics: Dict[str, Any],
    is_anomaly: bool = False,
    anomaly_score: float = 0.0,
    consecutive_violations: int = 1,
    affected_device_count: int = 1
) -> str:
    """
    Computes operational incident severity based on metric thresholds, device availability,
    incident classification, anomaly indicators, and blast radius.

    Severity Levels:
    - CRITICAL: Outage, server down, severe exhaustion, multiple devices failing.
    - HIGH: Serious degradation, high packet loss, severe latency, sustained overload.
    - MEDIUM: Moderate degradation, warning-level metrics, recurring anomalies.
    - LOW: Minor abnormality, isolated anomaly, informational.
    """
    cpu = metrics.get("cpu_utilization", 0.0)
    mem = metrics.get("memory_utilization", 0.0)
    disk = metrics.get("disk_utilization", 0.0)
    latency = metrics.get("network_latency", 0.0)
    packet_loss = metrics.get("packet_loss", 0.0)
    server_avail = metrics.get("server_availability", 1.0)
    net_avail = metrics.get("network_availability", 1.0)
    conn_status = metrics.get("connection_status", 1)
    dns_status = metrics.get("dns_response_status", 1)

    # 1. Immediate Critical Conditions
    if server_avail <= 0.0 or net_avail <= 0.0 or conn_status == 0:
        return "CRITICAL"
    
    if category == "Network Failure":
        return "CRITICAL"

    if cpu >= 95.0 or mem >= 95.0 or disk >= 95.0:
        return "CRITICAL"

    if packet_loss >= 15.0 or latency >= 350.0:
        return "CRITICAL"

    # Multi-device blast radius escalation
    if affected_device_count >= 3:
        return "CRITICAL"

    # 2. High Severity Conditions
    if category in ["Server Overload", "Memory Exhaustion", "Disk Capacity Issue"]:
        if cpu >= 85.0 or mem >= 90.0 or disk >= 90.0:
            return "HIGH"

    if category in ["Packet Loss", "High Latency"]:
        if packet_loss >= 5.0 or latency >= 200.0:
            return "HIGH"

    if category == "DNS Failure" and dns_status == 0:
        return "HIGH"

    if consecutive_violations >= 3:
        if cpu >= 80.0 or mem >= 85.0 or latency >= 150.0:
            return "HIGH"

    # 3. Medium Severity Conditions
    if cpu >= 70.0 or mem >= 75.0 or disk >= 80.0 or latency >= 100.0 or packet_loss >= 1.0:
        return "MEDIUM"

    if is_anomaly and anomaly_score < -0.15:
        return "MEDIUM"

    # 4. Low Severity
    if is_anomaly:
        return "LOW"

    return "LOW"
