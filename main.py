# Import the FastAPI app
from app.main import app

# This file serves as the entry point for running the application
# The variable name 'app' is what both Uvicorn and Gunicorn look for by default

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)