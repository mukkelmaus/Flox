"""
ASGI application for Gunicorn+Uvicorn compatibility

This file serves as the entry point for Gunicorn when using UvicornWorker.
"""
import uvicorn

# Import the FastAPI app
from app.main import app

# Create a callable for Gunicorn
# This won't be called directly with UvicornWorker, but is needed
# for configuration and discovery
application = app

if __name__ == "__main__":
    # For direct execution without Gunicorn
    uvicorn.run("asgi:application", host="0.0.0.0", port=5000, reload=True)