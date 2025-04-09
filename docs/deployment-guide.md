# OneTask API Deployment Guide

> **For Non-Technical Users:** We've created simplified guides:
> - [Simple Self-Hosting Guide](./simple-self-hosting-guide.md) - Step by step instructions for hosting on your own server
> - [Docker Deployment Guide](./docker-deployment-guide.md) - Easiest method using Docker containers
> - [Frontend Connection Guide](./frontend-connection-guide.md) - Testing and connecting your frontend after deployment

## Environment Setup

1. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Configure environment variables:**
   Required variables:
   - `SECRET_KEY`: JWT secret key
   - `ENVIRONMENT`: "development" or "production"
   - `DATABASE_URL`: PostgreSQL connection string
   - `OPENAI_API_KEY`: (optional) For AI features

3. **Start the server:**

   Development mode (with auto-reload):
   ```bash
   ./run_dev_server.sh
   ```

   Production mode:
   ```bash
   ./production_server.sh
   ```

## Server Configuration

### Development Server (Uvicorn)
- Auto-reload enabled
- Full FastAPI functionality
- Interactive API documentation available
- Recommended for development

### Production Server (Gunicorn + Uvicorn workers)
- Optimized for production workloads
- Multiple worker processes
- Enhanced stability and performance
- Proper error handling


## Health Monitoring

The API includes health check endpoints:
- `/health`: Basic server health
- `/api/v1/health`: Detailed system status

## Security Configuration

1. **JWT Configuration**:
   - Set strong `SECRET_KEY` in production
   - Configure token expiration in `app/core/config.py`

2. **CORS Settings**:
   - Configure allowed origins in `app/core/config.py`
   - Default allows application frontend origin

3. **Database Security**:
   - Use strong database passwords
   - Configure connection pooling appropriately

## Production Optimization

1. **Worker Configuration**:
   ```python
   # gunicorn_conf.py
   workers = 4  # Adjust based on available CPU
   worker_class = "uvicorn.workers.UvicornWorker"
   ```

2. **Database Pooling**:
   Configured in `app/db/session.py`

3. **Caching**:
   - Implement caching for frequent API calls
   - Configure Redis if needed

## Troubleshooting

Common issues and solutions:

1. **Database Connection Errors**:
   - Verify `DATABASE_URL` is correct
   - Check database server is running
   - Verify network connectivity

2. **Server Start Issues**:
   - Check port 5000 availability
   - Verify all dependencies are installed
   - Check log output for errors

3. **Authentication Issues**:
   - Verify `SECRET_KEY` is set
   - Check JWT token settings
   
4. **Frontend Connection Issues**:
   - Check CORS settings for your frontend domain
   - Use the included test tools in `public/api_connection_test.html`
   - Follow the [Frontend Connection Guide](./frontend-connection-guide.md) for detailed troubleshooting 
   - For WebSocket issues, ensure your proxy is correctly configured

## Logging

Logging configuration in `app/core/config.py`:
- Development: Detailed logging
- Production: Error-focused logging

Access logs through standard output or configured log handlers.