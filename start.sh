#!/bin/bash
# Script to start the FastAPI application
# Uses Gunicorn with Uvicorn workers to handle ASGI

# Default port is 5000
PORT=${PORT:-5000}

# Run prestart script for initialization
if [ -f prestart.sh ]; then
    echo "Running prestart.sh..."
    bash prestart.sh
fi

# Start the server with Gunicorn using Uvicorn workers
echo "Starting server with Gunicorn and Uvicorn workers..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT main:app --reload