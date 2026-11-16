"""
Script to launch Streamlit frontend dashboard.
"""
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    app_path = root / "frontend" / "app.py"
    print(f"Launching Streamlit NOC Dashboard from: {app_path}")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
