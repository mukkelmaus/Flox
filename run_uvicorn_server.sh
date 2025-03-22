#!/bin/bash
# Stop any existing Gunicorn processes
pkill -f gunicorn || true

# Run the FastAPI application with Uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload