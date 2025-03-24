#!/bin/bash
# Production server startup script for OneTask API
# This script uses the optimal Gunicorn configuration for production deployment

# Set environment variables for production
export ENVIRONMENT=production

# Use Gunicorn with Uvicorn worker for FastAPI
exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 180 \
  --keepalive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --graceful-timeout 60 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --forwarded-allow-ips="*" \
  "wsgi:application"