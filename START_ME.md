# OneTask API - Server Guide

## Development Mode

For full FastAPI functionality with Swagger UI and all API endpoints, use Uvicorn directly:

```bash
python main_uvicorn.py
```

This will start the server in development mode with auto-reload on code changes, and all FastAPI features will be accessible.

## Production Mode

For production deployment, Gunicorn is configured to run the application:

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

Note that due to ASGI/WSGI compatibility issues, the FastAPI endpoints will not be accessible in this mode. This mode is provided for compatibility with platforms that only support WSGI servers.

## Understanding the Issue

FastAPI is an ASGI framework while Gunicorn is a WSGI server. Without the use of an ASGI worker (e.g., UvicornWorker), there's an incompatibility that prevents some FastAPI features from working correctly.

### Solutions

1. For development: Always use `python main_uvicorn.py`
2. For production with all features: Use Gunicorn with UvicornWorker:
   ```bash
   gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 app.main:app
   ```
3. For compatibility with WSGI-only platforms: The current setup with limited functionality

## API Documentation

When running in development mode with Uvicorn, the API documentation is available at:
- http://localhost:5000/docs