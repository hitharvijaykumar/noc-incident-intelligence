"""
Unit tests for Infrastructure Simulator.
"""
import pytest
from simulator.server_simulator import ServerSimulator
from simulator.network_simulator import NetworkDeviceSimulator
from simulator.event_generator import EventGenerator
from simulator.infrastructure_simulator import InfrastructureSimulator

def test_server_simulator_normal_metrics():
    server = ServerSimulator("test-srv-01", "test-srv-01.noc.corp", base_cpu=30.0, base_mem=40.0)
    metrics = server.tick(mode="Normal")

    assert metrics["device_id"] == "test-srv-01"
    assert metrics["device_type"] == "server"
    assert 5.0 <= metrics["cpu_utilization"] <= 75.0
    assert 10.0 <= metrics["memory_utilization"] <= 80.0
    assert metrics["server_availability"] == 1.0
    assert metrics["connection_status"] == 1
    assert metrics["dns_response_status"] == 1

def test_server_simulator_fault_injection():
    server = ServerSimulator("test-srv-02", "test-srv-02.noc.corp")
    server.set_fault("Server Overload")
    metrics = server.tick(mode="Normal")

    assert metrics["cpu_utilization"] >= 85.0
    assert metrics["process_count"] >= 300

def test_network_simulator_normal_and_failure():
    net_dev = NetworkDeviceSimulator("test-net-01", "test-rtr-01.noc.net", device_type="router")
    metrics_normal = net_dev.tick(mode="Normal")

    assert metrics_normal["network_availability"] == 1.0
    assert metrics_normal["connection_status"] == 1
    assert metrics_normal["packet_loss"] < 1.0

    net_dev.set_fault("Network Failure")
    metrics_fail = net_dev.tick(mode="Normal")

    assert metrics_fail["network_availability"] == 0.0
    assert metrics_fail["connection_status"] == 0
    assert metrics_fail["packet_loss"] == 100.0

def test_event_generator_modes_and_triggers():
    gen = EventGenerator()
    assert gen.current_mode == "Normal"

    gen.set_mode("Critical")
    assert gen.current_mode == "Critical"

    gen.trigger_fault("High Latency", "srv-app-01", duration_seconds=60)
    assert gen.get_active_fault("srv-app-01") == "High Latency"

    gen.clear_fault("srv-app-01")
    assert gen.get_active_fault("srv-app-01") is None

def test_infrastructure_simulator_tick_all():
    sim = InfrastructureSimulator()
    snapshot = sim.tick_all()

    assert len(snapshot) == 15
    server_count = sum(1 for m in snapshot if m["device_type"] == "server")
    network_count = sum(1 for m in snapshot if m["device_type"] in ["switch", "router", "firewall"])

    assert server_count == 10
    assert network_count == 5
