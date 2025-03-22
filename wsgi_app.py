"""
WSGI wrapper for FastAPI application for Gunicorn compatibility.

Provides a simple WSGI application to handle basic routes.
"""
import json

# Create a simple WSGI application with only basic functionality
def simple_app(environ, start_response):
    """Simple WSGI application for health checks and basic routes"""
    path = environ.get('PATH_INFO', '')
    
    # Handle health check
    if path == '/health':
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'OK']
    
    # Handle root path
    if path == '/':
        response_body = json.dumps({
            "status": "ok", 
            "message": "OneTask API is running. Please use /docs for API documentation."
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ])
        return [response_body]
    
    # For all other paths, return a 404
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

# This is what gunicorn will use
application = simple_app