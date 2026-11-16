"""
Unified Launcher for AI-Powered NOC Incident Intelligence System.
Starts both the FastAPI backend and Streamlit dashboard concurrently with graceful signal handling.
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    python_bin = sys.executable

    print("=" * 70)
    print("🛡️  STARTING AI-POWERED NOC INCIDENT INTELLIGENCE SYSTEM")
    print("=" * 70)

    # 1. Start FastAPI Backend
    backend_script = root / "run_backend.py"
    print(f"[1/2] Launching FastAPI Backend Gateway (http://127.0.0.1:8000)...")
    backend_proc = subprocess.Popen(
        [python_bin, str(backend_script)],
        cwd=str(root)
    )

    # Allow backend to initialize database & ML models
    time.sleep(3)

    # 2. Start Streamlit Frontend
    frontend_script = root / "frontend" / "app.py"
    print(f"[2/2] Launching Streamlit NOC Dashboard (http://localhost:8501)...")
    frontend_proc = subprocess.Popen(
        [
            python_bin,
            "-m",
            "streamlit",
            "run",
            str(frontend_script),
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ],
        cwd=str(root)
    )

    print("\n" + "=" * 70)
    print("✅ NOC System is fully operational!")
    print("   • Dashboard URL:    http://localhost:8501")
    print("   • API Swagger Docs: http://127.0.0.1:8000/docs")
    print("   • API Health Probe: http://127.0.0.1:8000/api/health")
    print("   • Press Ctrl+C in this terminal to shut down all services safely.")
    print("=" * 70 + "\n")

    def signal_handler(sig, frame):
        print("\nInitiating graceful shutdown of NOC services...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
            frontend_proc.wait(timeout=3)
            backend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()
            backend_proc.kill()
        print("All processes stopped. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            # Check if any child died unexpectedly
            if backend_proc.poll() is not None:
                print(f"Backend process terminated with code {backend_proc.returncode}. Shutting down...")
                break
            if frontend_proc.poll() is not None:
                print(f"Frontend process terminated with code {frontend_proc.returncode}. Shutting down...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
