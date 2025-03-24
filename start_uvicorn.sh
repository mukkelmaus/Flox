#!/bin/bash
# Start the FastAPI application with Uvicorn directly

echo "Starting OneTask API with Uvicorn"
echo "API documentation will be available at: http://localhost:5000/docs"

# Run with uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000