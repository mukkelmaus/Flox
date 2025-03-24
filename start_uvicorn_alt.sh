#!/bin/bash
# Start Uvicorn server with the FastAPI application on port 8000

echo "Starting OneTask API with Uvicorn on port 8000"
echo "API documentation will be available at: http://localhost:8000/docs"

# Run Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000