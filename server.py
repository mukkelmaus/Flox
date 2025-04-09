"""
Direct server launch script for the FastAPI application

This script bypasses Gunicorn entirely and uses Uvicorn directly,
which is the recommended way to run FastAPI applications.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting Floxari FastAPI server with Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")