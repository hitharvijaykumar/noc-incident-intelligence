"""
Main infrastructure simulator coordinating all simulated nodes, networks, and event injections.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from simulator.server_simulator import ServerSimulator
from simulator.network_simulator import NetworkDeviceSimulator
from simulator.event_generator import EventGenerator
from backend.models import Device, MetricHistory
from backend.database import SessionLocal
from backend.utils.logger import logger

DEFAULT_DEVICES = [
    # 10 Simulated Servers
    {"id": "srv-web-01", "hostname": "web-lb-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.11", "location": "DC-US-EAST", "base_cpu": 35.0, "base_mem": 45.0, "base_disk": 55.0},
    {"id": "srv-web-02", "hostname": "web-lb-02.noc.corp", "device_type": "server", "ip_address": "192.0.2.12", "location": "DC-US-EAST", "base_cpu": 38.0, "base_mem": 42.0, "base_disk": 52.0},
    {"id": "srv-app-01", "hostname": "api-gateway-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.21", "location": "DC-US-EAST", "base_cpu": 45.0, "base_mem": 60.0, "base_disk": 48.0},
    {"id": "srv-app-02", "hostname": "api-worker-02.noc.corp", "device_type": "server", "ip_address": "192.0.2.22", "location": "DC-US-WEST", "base_cpu": 40.0, "base_mem": 58.0, "base_disk": 46.0},
    {"id": "srv-db-primary", "hostname": "db-primary-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.31", "location": "DC-US-EAST", "base_cpu": 52.0, "base_mem": 72.0, "base_disk": 78.0},
    {"id": "srv-db-replica", "hostname": "db-replica-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.32", "location": "DC-US-WEST", "base_cpu": 32.0, "base_mem": 65.0, "base_disk": 76.0},
    {"id": "srv-cache-01", "hostname": "cache-redis-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.41", "location": "DC-US-EAST", "base_cpu": 25.0, "base_mem": 68.0, "base_disk": 35.0},
    {"id": "srv-cache-02", "hostname": "cache-redis-02.noc.corp", "device_type": "server", "ip_address": "192.0.2.42", "location": "DC-US-WEST", "base_cpu": 28.0, "base_mem": 64.0, "base_disk": 34.0},
    {"id": "srv-queue-01", "hostname": "msg-rabbit-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.51", "location": "DC-EU-CENTRAL", "base_cpu": 42.0, "base_mem": 54.0, "base_disk": 62.0},
    {"id": "srv-auth-01", "hostname": "auth-oauth-01.noc.corp", "device_type": "server", "ip_address": "192.0.2.61", "location": "DC-US-EAST", "base_cpu": 30.0, "base_mem": 48.0, "base_disk": 40.0},

    # 5 Simulated Network Devices
    {"id": "net-core-rtr-01", "hostname": "core-rtr-01.noc.net", "device_type": "router", "ip_address": "198.51.100.1", "location": "DC-US-EAST", "base_latency": 12.0, "base_bandwidth": 45.0},
    {"id": "net-dist-sw-01", "hostname": "dist-sw-01.noc.net", "device_type": "switch", "ip_address": "198.51.100.10", "location": "DC-US-EAST", "base_latency": 15.0, "base_bandwidth": 35.0},
    {"id": "net-dist-sw-02", "hostname": "dist-sw-02.noc.net", "device_type": "switch", "ip_address": "198.51.100.20", "location": "DC-US-WEST", "base_latency": 22.0, "base_bandwidth": 40.0},
    {"id": "net-edge-fw-01", "hostname": "edge-fw-01.noc.net", "device_type": "firewall", "ip_address": "198.51.100.254", "location": "DC-US-EAST", "base_latency": 18.0, "base_bandwidth": 55.0},
    {"id": "net-dns-gw-01", "hostname": "dns-resolver-01.noc.net", "device_type": "router", "ip_address": "198.51.100.53", "location": "DC-EU-CENTRAL", "base_latency": 28.0, "base_bandwidth": 25.0},
]

class InfrastructureSimulator:
    def __init__(self):
        self.event_generator = EventGenerator()
        self.server_sims: Dict[str, ServerSimulator] = {}
        self.network_sims: Dict[str, NetworkDeviceSimulator] = {}
        self.device_meta: Dict[str, Dict[str, Any]] = {}
        self._init_simulators()

    def _init_simulators(self):
        for dev in DEFAULT_DEVICES:
            self.device_meta[dev["id"]] = dev
            if dev["device_type"] == "server":
                self.server_sims[dev["id"]] = ServerSimulator(
                    device_id=dev["id"],
                    hostname=dev["hostname"],
                    base_cpu=dev["base_cpu"],
                    base_mem=dev["base_mem"],
                    base_disk=dev["base_disk"]
                )
            else:
                self.network_sims[dev["id"]] = NetworkDeviceSimulator(
                    device_id=dev["id"],
                    hostname=dev["hostname"],
                    device_type=dev["device_type"],
                    base_latency=dev["base_latency"],
                    base_bandwidth=dev["base_bandwidth"]
                )

    def seed_devices_in_db(self):
        """Ensure all 15 default devices exist in the database."""
        db = SessionLocal()
        try:
            for dev in DEFAULT_DEVICES:
                existing = db.query(Device).filter(Device.id == dev["id"]).first()
                if not existing:
                    new_dev = Device(
                        id=dev["id"],
                        hostname=dev["hostname"],
                        device_type=dev["device_type"],
                        ip_address=dev["ip_address"],
                        status="ONLINE",
                        location=dev["location"],
                        last_heartbeat=datetime.now(timezone.utc),
                        health_status="HEALTHY"
                    )
                    db.add(new_dev)
            db.commit()
            logger.info("Default infrastructure devices seeded into database.")
        except Exception as e:
            db.rollback()
            logger.error("Failed to seed devices in database: %s", e)
        finally:
            db.close()

    def set_mode(self, mode: str):
        self.event_generator.set_mode(mode)
        logger.info("Simulation mode set to: %s", mode)

    def trigger_incident(self, incident_type: str, device_id: Optional[str] = None):
        if not device_id:
            # Pick a suitable device based on incident type
            if incident_type in ["Server Overload", "Memory Exhaustion", "Disk Capacity Issue"]:
                device_id = "srv-app-01"
            elif incident_type == "DNS Failure":
                device_id = "net-dns-gw-01"
            elif incident_type in ["Network Failure", "Packet Loss", "High Latency"]:
                device_id = "net-core-rtr-01"
            else:
                device_id = "srv-web-01"

        self.event_generator.trigger_fault(incident_type, device_id)
        logger.info("Manual fault '%s' triggered on device '%s'", incident_type, device_id)
        return device_id

    def clear_incident(self, device_id: str):
        self.event_generator.clear_fault(device_id)

    def tick_all(self) -> List[Dict[str, Any]]:
        """
        Executes one simulation step across all 15 devices.
        Returns a list of raw metric dictionaries.
        """
        all_ids = list(self.device_meta.keys())
        self.event_generator.tick_random_mode(all_ids)
        current_mode = self.event_generator.current_mode

        snapshot = []

        # Servers
        for dev_id, sim in self.server_sims.items():
            active_fault = self.event_generator.get_active_fault(dev_id)
            sim.set_fault(active_fault)
            metrics = sim.tick(mode=current_mode)
            snapshot.append(metrics)

        # Network devices
        for dev_id, sim in self.network_sims.items():
            active_fault = self.event_generator.get_active_fault(dev_id)
            sim.set_fault(active_fault)
            metrics = sim.tick(mode=current_mode)
            snapshot.append(metrics)

        return snapshot

simulator_instance = InfrastructureSimulator()
