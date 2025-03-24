#!/bin/bash
# Production server script for OneTask API
# This script runs the FastAPI app with Gunicorn and UvicornWorker for ASGI support

echo "Starting OneTask API in production mode (FastAPI + Gunicorn + UvicornWorker)"
echo "API documentation will be available at: http://localhost:5000/docs"

# Export necessary environment variables
export PYTHONPATH=.

# Run with Gunicorn and UvicornWorker
gunicorn --worker-class uvicorn.workers.UvicornWorker \
         --workers 4 \
         --bind 0.0.0.0:5000 \
         --log-level info \
         --timeout 120 \
         --graceful-timeout 60 \
         --keep-alive 5 \
         app.main:app