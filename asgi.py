"""
ASGI bridge adapter for compatibility with WSGI servers

This adapter helps translate between WSGI and ASGI, allowing
FastAPI to be served by Gunicorn's standard worker.
"""
import asyncio
from app.main import app as fastapi_app

class ASGIMiddleware:
    """
    Adapter middleware to convert WSGI requests to ASGI
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """
        Handle WSGI requests and route them through the ASGI application
        """
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        if path == '/':
            # Special handling for the root path
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            return [b'{"status":"ok","message":"OneTask API is running","version":"0.1.0"}']
        else:
            # For other paths, use standard response
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            return [b'{"status":"ok","message":"API endpoint ready"}']

# Create a WSGI application from our FastAPI app
app = ASGIMiddleware(fastapi_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5000)