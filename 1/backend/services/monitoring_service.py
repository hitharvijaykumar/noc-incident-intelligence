"""
Real-time infrastructure monitoring service orchestrating data ingestion, ML scoring, and alert/incident generation.
"""
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.config import settings
from backend.database import SessionLocal
from backend.models import MetricHistory, Device, MLPrediction
from backend.services.alert_service import alert_service
from backend.services.incident_service import incident_service
from ml.prediction import prediction_service
from simulator.infrastructure_simulator import simulator_instance
from backend.utils.logger import logger

class MonitoringService:
    def __init__(self):
        self._is_running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.interval_seconds = settings.SIMULATION_INTERVAL_SECONDS
        self.last_tick_time: Optional[datetime] = None
        self.tick_count = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        with self._lock:
            if self._is_running:
                logger.info("Monitoring service is already running.")
                return

            self._is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="NOC-Monitoring-Worker")
            self._thread.start()
            logger.info("Background monitoring service started with interval %ds.", self.interval_seconds)

    def stop(self):
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            self._stop_event.set()
            logger.info("Monitoring service stopping...")
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            logger.info("Monitoring service stopped gracefully.")

    def step_once(self) -> int:
        """
        Executes one monitoring step synchronously across all devices.
        Returns the number of processed devices.
        """
        db = SessionLocal()
        processed = 0
        try:
            # 1. Collect simulated metrics snapshot
            snapshot = simulator_instance.tick_all()
            now = datetime.now(timezone.utc)
            self.last_tick_time = now

            for metric_data in snapshot:
                device_id = metric_data["device_id"]
                hostname = metric_data.get("hostname", device_id)

                # 2. Persist MetricHistory
                history_record = MetricHistory(
                    device_id=device_id,
                    timestamp=now,
                    cpu_utilization=metric_data["cpu_utilization"],
                    memory_utilization=metric_data["memory_utilization"],
                    disk_utilization=metric_data["disk_utilization"],
                    server_uptime=metric_data["server_uptime"],
                    process_count=metric_data["process_count"],
                    response_time=metric_data["response_time"],
                    server_availability=metric_data["server_availability"],
                    network_latency=metric_data["network_latency"],
                    packet_loss=metric_data["packet_loss"],
                    bandwidth_utilization=metric_data["bandwidth_utilization"],
                    network_throughput=metric_data["network_throughput"],
                    connection_status=metric_data["connection_status"],
                    dns_response_status=metric_data["dns_response_status"],
                    network_availability=metric_data["network_availability"],
                )
                db.add(history_record)

                # Update Device last_heartbeat
                dev = db.query(Device).filter(Device.id == device_id).first()
                if dev:
                    dev.last_heartbeat = now

                # 3. Rule-based alert detection
                active_alerts = alert_service.evaluate_metrics(db, metric_data)

                # 4. ML Unified Prediction (RF, Isolation Forest, KMeans)
                try:
                    ml_pred = prediction_service.predict(metric_data)

                    # Persist ML Prediction
                    pred_record = MLPrediction(
                        timestamp=now,
                        device_id=device_id,
                        predicted_category=ml_pred["predicted_incident_type"],
                        confidence_score=ml_pred["classification_confidence"],
                        anomaly_score=ml_pred["anomaly_score"],
                        is_anomaly=ml_pred["is_anomaly"],
                        cluster_id=ml_pred["cluster_id"],
                        cluster_interpretation=ml_pred["cluster_interpretation"],
                        recommended_severity=ml_pred["recommended_severity"],
                    )
                    db.add(pred_record)

                    # 5. Incident Intelligence & Correlation
                    incident_service.process_telemetry_incident(
                        db=db,
                        device_id=device_id,
                        hostname=hostname,
                        metrics=metric_data,
                        ml_prediction=ml_pred,
                        active_alerts=active_alerts,
                    )
                except Exception as ml_err:
                    logger.debug("ML prediction skipped: %s", ml_err)

                processed += 1

            db.commit()
            self.tick_count += 1
            return processed
        except Exception as e:
            db.rollback()
            logger.error("Error during monitoring step: %s", e)
            return 0
        finally:
            db.close()

    def _run_loop(self):
        while self._is_running and not self._stop_event.is_set():
            start_time = time.time()
            self.step_once()
            elapsed = time.time() - start_time
            sleep_time = max(0.1, self.interval_seconds - elapsed)
            if self._stop_event.wait(timeout=sleep_time):
                break

monitoring_service = MonitoringService()
