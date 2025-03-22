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

# Create a modified simple app that provides helpful info for API endpoints
def advanced_simple_app(environ, start_response):
    """Enhanced WSGI application that provides more helpful responses"""
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
    
    # Special helpful message for the docs endpoint
    if path == '/docs':
        response_body = json.dumps({
            "status": "info", 
            "message": "Swagger UI is only available when running with Uvicorn directly.",
            "instructions": "To access the full API documentation and functionality, run the application with: python -m uvicorn app.main:app --host 0.0.0.0 --port 5000"
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ])
        return [response_body]
    
    # For all API endpoints
    if path.startswith('/api/'):
        response_body = json.dumps({
            "status": "info", 
            "message": "API endpoints are only available when running with Uvicorn directly.",
            "instructions": "To access the full API functionality, run the application with: python -m uvicorn app.main:app --host 0.0.0.0 --port 5000"
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ])
        return [response_body]
    
    # For all other paths, return a notice
    response_body = json.dumps({
        "status": "error", 
        "message": "Direct API access not available in this mode.",
        "instructions": "To access the full API functionality, run the application with: python -m uvicorn app.main:app --host 0.0.0.0 --port 5000"
    }).encode('utf-8')
    start_response('404 Not Found', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
    ])
    return [response_body]

# Determine which app to expose
if FASTAPI_AVAILABLE:
    try:
        logger.info("Using enhanced simple app with FastAPI notices")
        app = advanced_simple_app
    except Exception as e:
        logger.error(f"Failed to initialize advanced app: {e}")
        app = simple_app
else:
    logger.info("Using simple WSGI application")
    app = simple_app

if __name__ == "__main__":
    # When run directly, use Uvicorn to serve the FastAPI app
    import uvicorn
    logger.info("Starting OneTask API with Uvicorn (ASGI mode)")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)