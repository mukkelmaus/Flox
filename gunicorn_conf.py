"""
Gunicorn configuration file for a simple WSGI application
"""
import multiprocessing

# Socket Path
bind = "0.0.0.0:5000"

# Worker Options - use a single worker for Replit
workers = 1
worker_class = "sync"  # Use standard sync worker instead of UvicornWorker

# Timeout configurations
timeout = 120
keepalive = 5

# Logging Options
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Reload code when changed
reload = True
reload_extra_files = ["./app"]

# Specify the WSGI app path
wsgi_app = "wsgi_app:application"