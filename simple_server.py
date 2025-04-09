"""
Direct server launch script for the FastAPI application using Uvicorn
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Floxari FastAPI server with Uvicorn...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)