"""
Gunicorn entry point for the FastAPI application

This is a simple WSGI wrapper for the FastAPI application 
to make it compatible with the Replit workflow system.

For production, use the wsgi.py file with the Uvicorn worker.
"""
# Direct import of the app for simplified testing in Replit
from wsgi import app