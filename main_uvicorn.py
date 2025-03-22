"""
Direct server launcher for FastAPI using Uvicorn

This script bypasses Gunicorn and launches Uvicorn directly,
which is the recommended way to run FastAPI in development.
"""
import uvicorn

if __name__ == "__main__":
    # Run the server directly with Uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)