"""
Server startup file for FastAPI with uvicorn
"""
import logging
import uvicorn
from app.main import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting server with uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")