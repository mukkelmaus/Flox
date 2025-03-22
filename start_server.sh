#!/bin/bash

# Start the application using Uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload