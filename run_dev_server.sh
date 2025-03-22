#!/bin/bash
# Development server script for OneTask API
# This script runs the FastAPI app directly with Uvicorn

echo "Starting OneTask API in development mode (FastAPI + Uvicorn)"
echo "API documentation will be available at: http://localhost:5000/docs"

# Export necessary environment variables
export PYTHONPATH=.

# Run with uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload