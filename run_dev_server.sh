#!/bin/bash
# Development server startup script for OneTask API

# Set environment variables for development
export ENVIRONMENT=development

# Use Uvicorn with hot reloading for development
exec uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload --log-level debug