"""
Gunicorn configuration file for FastAPI production deployment
"""
import multiprocessing
import os

# Socket Path
bind = "0.0.0.0:5000"

# Worker Options 
workers = 1  # Single worker for Replit
worker_class = "uvicorn.workers.UvicornWorker"  # Use Uvicorn worker for FastAPI

# Process naming
proc_name = "onetask-api"
pythonpath = "."

# Timeout configurations
timeout = 180  # Extended timeout for AI operations
keepalive = 5

# Logging Options
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True
logger_class = "gunicorn.glogging.Logger"

# Running environment
raw_env = [
    f"ENVIRONMENT={os.environ.get('ENVIRONMENT', 'production')}",
]

# Security settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Production stability
graceful_timeout = 60
max_requests = 1000
max_requests_jitter = 50

# WSGI app
wsgi_app = "wsgi:application"