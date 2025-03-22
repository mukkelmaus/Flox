#!/bin/bash
# Run the prestart script to initialize the database and default data
./prestart.sh

# Start the application with Uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload