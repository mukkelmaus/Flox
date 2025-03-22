#!/bin/bash

# Use uvicorn directly with the --factory flag to use app factory pattern
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload