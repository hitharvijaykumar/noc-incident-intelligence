"""
Initialize database tables and seed initial infrastructure devices.
"""
from backend.database import init_db
from simulator.infrastructure_simulator import simulator_instance
from backend.services.monitoring_service import monitoring_service

def setup():
    print("Initializing SQLite database tables...")
    init_db()
    print("Seeding infrastructure nodes (10 servers, 5 network devices)...")
    simulator_instance.seed_devices_in_db()
    print("Seeding baseline metrics...")
    for _ in range(3):
        monitoring_service.step_once()
    print("Database initialization complete.")

if __name__ == "__main__":
    setup()
