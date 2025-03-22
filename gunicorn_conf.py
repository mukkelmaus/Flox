"""
Gunicorn configuration file
"""
from multiprocessing import cpu_count

# Socket Path
bind = "0.0.0.0:5000"

# Worker Options
workers = cpu_count() + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Reload code when changed
reload = True