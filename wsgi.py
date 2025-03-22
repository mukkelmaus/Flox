"""
WSGI wrapper for FastAPI application for Gunicorn+Uvicorn compatibility.
"""
from uvicorn.workers import UvicornWorker
from app.main import app as application

# Using the Uvicorn worker method in Gunicorn
class FastAPIWorker(UvicornWorker):
    """
    Customized Uvicorn worker class for FastAPI
    """
    CONFIG_KWARGS = {
        "app": "app.main:app",
        "log_level": "info",
        "timeout_keep_alive": 30,
        "loop": "auto"
    }

# Export the app for Gunicorn
app = application

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, log_level="info")