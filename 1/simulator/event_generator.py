"""
Event generator managing simulation modes and manual fault injection.
"""
import random
import time
from typing import Dict, Any, Optional

class EventGenerator:
    SUPPORTED_FAULTS = [
        "Server Overload",
        "Network Failure",
        "High Latency",
        "Packet Loss",
        "DNS Failure",
        "Disk Capacity Issue",
        "Memory Exhaustion",
    ]

    MODES = ["Normal", "Warning", "Critical", "Random"]

    def __init__(self):
        self.current_mode = "Normal"
        self.active_injections: Dict[str, Dict[str, Any]] = {}  # device_id -> fault info
        self.last_random_injection_time = time.time()
        self.random_injection_interval = 25  # seconds

    def set_mode(self, mode: str):
        if mode in self.MODES:
            self.current_mode = mode
            if mode == "Normal":
                self.active_injections.clear()

    def trigger_fault(self, fault_type: str, device_id: str, duration_seconds: int = 120):
        if fault_type in self.SUPPORTED_FAULTS:
            self.active_injections[device_id] = {
                "fault_type": fault_type,
                "start_time": time.time(),
                "duration": duration_seconds
            }

    def clear_fault(self, device_id: str):
        if device_id in self.active_injections:
            del self.active_injections[device_id]

    def get_active_fault(self, device_id: str) -> Optional[str]:
        if device_id in self.active_injections:
            info = self.active_injections[device_id]
            # Check duration
            if time.time() - info["start_time"] > info["duration"]:
                del self.active_injections[device_id]
                return None
            return info["fault_type"]
        return None

    def tick_random_mode(self, available_device_ids: list[str]):
        if self.current_mode != "Random":
            return

        now = time.time()
        if now - self.last_random_injection_time > self.random_injection_interval:
            self.last_random_injection_time = now
            target_device = random.choice(available_device_ids)
            fault = random.choice(self.SUPPORTED_FAULTS)
            self.trigger_fault(fault, target_device, duration_seconds=60)
