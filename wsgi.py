"""
WSGI wrapper for FastAPI application for Gunicorn+Uvicorn compatibility.
"""
from app.main import app

# This is to make the file compatible with Gunicorn+Uvicorn workers
# When using Gunicorn, it should be run with: 
# gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 wsgi:app

# When running directly with Uvicorn, use:
# uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")