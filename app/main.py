import datetime
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from app.api.api_v1.api import api_router
from app.websockets.endpoints import router as websocket_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,
    redoc_url=None,
)

# Set CORS settings for production
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
if allowed_origins:
    # Parse comma-separated origins from environment variable
    origins = [origin.strip() for origin in allowed_origins.split(",")]
    logger.info(f"CORS enabled for specific origins: {origins}")
else:
    # Fallback to defaults
    origins = [
        settings.SERVER_HOST,
        "https://onetask.replit.app",
        "https://*.replit.app"
    ]
    logger.info(f"CORS enabled with default origins: {origins}")

# In development mode, allow all origins
if settings.ENVIRONMENT.lower() == "development":
    origins = ["*"]
    logger.info("CORS enabled for all origins (development mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "User-Agent"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(websocket_router)

# Mount static files directory
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI with OneTask branding
    """
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/api/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """
    Returns the OpenAPI schema as JSON
    """
    return JSONResponse(
        get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            routes=app.routes,
        )
    )


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "documentation": f"{settings.SERVER_HOST}/docs",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    from app.db.session import SessionLocal
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "ok",
            "database": "unknown"
        }
    }
    
    # Check database connection
    db = SessionLocal()
    try:
        # Execute simple query to verify database connection
        db.execute("SELECT 1")
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = str(e)
    finally:
        db.close()
        
    return health_status


if __name__ == "__main__":
    import uvicorn
    
    # We take the port from environment if available
    port = int(os.environ.get("PORT", 5000))
    
    # Development settings
    if settings.ENVIRONMENT.lower() == "development":
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
    # Production settings
    else:
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=port,
            workers=1,
            proxy_headers=True,
            forwarded_allow_ips="*",
            log_level="info"
        )
