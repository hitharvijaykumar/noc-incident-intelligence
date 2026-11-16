"""
Script to launch FastAPI backend server.
"""
import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print(f"Starting NOC Backend on http://{settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )
