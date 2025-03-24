"""
WSGI wrapper for FastAPI application for Gunicorn+Uvicorn compatibility.

This module provides the necessary integration between Gunicorn and Uvicorn 
to run FastAPI application in a production environment.
"""
import logging
import os
from uvicorn.workers import UvicornWorker
from app.main import app as application

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Using the Uvicorn worker method in Gunicorn
class FastAPIWorker(UvicornWorker):
    """
    Customized Uvicorn worker class for FastAPI
    
    This worker class is optimized for FastAPI applications running 
    under Gunicorn with Uvicorn workers.
    """
    CONFIG_KWARGS = {
        "app": "app.main:app",
        "log_level": os.environ.get("LOG_LEVEL", "info"),
        "timeout_keep_alive": 30,
        "loop": "auto",
        "http": "h11",
        "lifespan": "on",
        "proxy_headers": True,
    }

# Export the app for Gunicorn
app = application

# Log the initialization
logger.info("WSGI Application initialized with FastAPI")

if __name__ == "__main__":
    # Run directly with Uvicorn (not through Gunicorn)
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"Starting OneTask API directly with Uvicorn on port {port}")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port, 
        log_level="info", 
        reload=os.environ.get("ENVIRONMENT", "").lower() == "development"
    )