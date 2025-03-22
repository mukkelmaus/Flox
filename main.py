"""
Gunicorn/Uvicorn adapter for the FastAPI application

This module detects whether it's being run by Gunicorn or directly and
provides the appropriate interface accordingly.
"""
import json
import sys
import os
import logging
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Check if FastAPI is available
try:
    import fastapi
    import uvicorn
    FASTAPI_AVAILABLE = True
    logger.info("FastAPI and Uvicorn are available, attempting to import FastAPI app")
    
    # Try to import the FastAPI app
    try:
        from app.main import app as fastapi_app
        logger.info("Successfully imported FastAPI app")
    except ImportError as e:
        logger.error(f"Failed to import FastAPI app: {e}")
        FASTAPI_AVAILABLE = False
except ImportError:
    logger.warning("FastAPI or Uvicorn not available, falling back to simple WSGI app")
    FASTAPI_AVAILABLE = False

# Detect if we're running under Gunicorn
def is_running_under_gunicorn():
    return 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '').lower()

# Basic WSGI application for Gunicorn fallback
def simple_app(environ, start_response):
    """Simple WSGI application that returns static responses"""
    path = environ.get('PATH_INFO', '')
    
    # Handle health check
    if path == '/health':
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'OK']
    
    # Handle root path
    if path == '/':
        response_body = json.dumps({
            "status": "ok", 
            "message": "OneTask API is running. FastAPI mode: " + 
                      ("ENABLED" if FASTAPI_AVAILABLE else "DISABLED") +
                      ". Running under Gunicorn: " + 
                      ("YES" if is_running_under_gunicorn() else "NO")
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ])
        return [response_body]
    
    # For all other paths, return a notice
    response_body = json.dumps({
        "status": "error", 
        "message": "Direct API access not available in this mode."
    }).encode('utf-8')
    start_response('503 Service Unavailable', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
    ])
    return [response_body]

# Create a WSGI-to-ASGI adapter for FastAPI
class WSGItoASGIAdapter:
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
        self.asgi_is_loaded = False
        
    def __call__(self, environ, start_response):
        # Simple routes are handled directly
        path = environ.get('PATH_INFO', '')
        
        if path == '/health' or path == '/':
            return simple_app(environ, start_response)
        
        # For all other routes, we need ASGI
        if not FASTAPI_AVAILABLE:
            return simple_app(environ, start_response)
        
        # Try to use the ASGI app through a bridging layer
        try:
            from uvicorn.middleware.wsgi import WSGIMiddleware
            wsgi_app = WSGIMiddleware(self.asgi_app)
            return wsgi_app(environ, start_response)
        except ImportError:
            logger.error("Failed to import WSGIMiddleware")
            return simple_app(environ, start_response)

# Determine which app to expose
if FASTAPI_AVAILABLE:
    try:
        logger.info("Using FastAPI application with adapter")
        app = WSGItoASGIAdapter(fastapi_app)
    except Exception as e:
        logger.error(f"Failed to initialize adapter: {e}")
        app = simple_app
else:
    logger.info("Using simple WSGI application")
    app = simple_app

if __name__ == "__main__":
    # When run directly, use Uvicorn to serve the FastAPI app
    import uvicorn
    logger.info("Starting OneTask API with Uvicorn (ASGI mode)")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)