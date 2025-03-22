#!/bin/bash
# Start the FastAPI application with Gunicorn using Uvicorn workers
gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py wsgi:app