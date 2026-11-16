"""
Configuration management for NOC Incident Intelligence System.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Settings
    APP_NAME: str = "AI-Powered NOC Incident Intelligence System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "ml" / "saved_models"
    DATABASE_PATH: Path = BASE_DIR / "data" / "noc_database.db"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'noc_database.db'}"

    # Simulation Settings
    SIMULATION_INTERVAL_SECONDS: int = 3
    SIMULATION_MAX_HISTORY_PER_DEVICE: int = 200

    # ML Settings
    RANDOM_SEED: int = 42
    ANOMALY_CONTAMINATION: float = 0.05
    N_CLUSTERS: int = 4

    # Threshold Rules
    CPU_NORMAL_MAX: float = 70.0
    CPU_WARNING_MAX: float = 85.0

    MEMORY_NORMAL_MAX: float = 75.0
    MEMORY_WARNING_MAX: float = 90.0

    DISK_NORMAL_MAX: float = 80.0
    DISK_WARNING_MAX: float = 90.0

    LATENCY_NORMAL_MAX: float = 100.0  # ms
    LATENCY_WARNING_MAX: float = 200.0

    PACKET_LOSS_NORMAL_MAX: float = 1.0  # %
    PACKET_LOSS_WARNING_MAX: float = 5.0

    BANDWIDTH_WARNING_MAX: float = 85.0
    BANDWIDTH_CRITICAL_MAX: float = 95.0

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
