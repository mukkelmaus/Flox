"""
Gunicorn configuration file for FastAPI application
"""
from multiprocessing import cpu_count

# Socket Path
bind = "0.0.0.0:5000"

# Worker Options
workers = cpu_count() + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "debug"
accesslog = "-"
errorlog = "-"

# Reload code when changed
reload = True