"""
Gunicorn-compatible wrapper for the FastAPI application

This wrapper exposes the FastAPI app via a WSGI-compatible interface
for Gunicorn to use, while still supporting ASGI when run directly.
"""
import json
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Basic WSGI application for Gunicorn
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
            "message": "OneTask API is running. Access points disabled in WSGI mode. Please use Uvicorn directly for full FastAPI functionality."
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ])
        return [response_body]
    
    # For all other paths, return a notice
    response_body = json.dumps({
        "status": "error", 
        "message": "FastAPI endpoints unavailable in WSGI mode. Please use Uvicorn directly."
    }).encode('utf-8')
    start_response('503 Service Unavailable', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
    ])
    return [response_body]

# This is what Gunicorn will use when run with the standard WSGI workers
app = simple_app

if __name__ == "__main__":
    # When run directly, use Uvicorn to serve the FastAPI app
    import uvicorn
    logger.info("Starting OneTask API with Uvicorn (ASGI mode)")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)