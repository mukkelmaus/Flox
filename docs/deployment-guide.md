# OneTask API Deployment Guide

This guide provides comprehensive instructions for deploying the OneTask API in various environments.

## Environment Setup

### Local Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/onetask-api.git
   cd onetask-api
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the development server:**
   ```bash
   ./run_dev_server.sh
   # or
   python main_uvicorn.py
   ```

### Replit Deployment

The OneTask API is optimized for Replit deployment:

1. **Set up environment variables:**
   - Add the following secrets in Replit's Secrets tab:
     - `SECRET_KEY`: JWT secret key
     - `SESSION_SECRET`: Session secret key 
     - `OPENAI_API_KEY`: (optional) For AI features
     - `ENVIRONMENT`: Set to "production"

2. **Configure the workflow:**
   - Use the existing workflow configuration which uses the `production_server.sh` script

3. **Deploy:**
   - Click the "Run" button to start the server
   - For permanent deployment, use Replit's deployment feature

## Deployment Scripts

The following deployment scripts are available:

### `run_dev_server.sh`
- Development server with hot reloading
- Uses Uvicorn directly
- Optimized for local development

### `production_server.sh`
- Production-ready server configuration
- Uses Gunicorn with Uvicorn workers
- Includes optimal worker settings and timeouts

### `prestart.sh`
- Pre-deployment checks and setup
- Automatically runs database initialization
- Validates environment variables
- Loads environment-specific configurations

## Configuration Files

### `.env.example`
- Template for local environment variables

### `.env.production`
- Production environment defaults
- Loaded when `ENVIRONMENT=production`

## Database Migration

Database migration is handled during the prestart script:

```bash
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

For more advanced migration needs, consider implementing Alembic.

## Health Monitoring

The API includes a health check endpoint at `/health` that monitors:
- API status
- Database connectivity
- Environment configuration

Use this endpoint for monitoring and alerting in production.

## Security Considerations

1. **JWT Tokens**: Set a strong `SECRET_KEY` in production
2. **CORS Settings**: Configure `ALLOWED_ORIGINS` to limit cross-origin requests
3. **Database Security**: Use unique, strong passwords for database access
4. **API Keys**: Store API keys (like `OPENAI_API_KEY`) securely using environment variables

## Production Optimization

For production deployment, consider the following optimizations:

1. **Worker Configuration**:
   - Adjust `--workers` based on available CPU (2-4 x number of cores)
   - Set appropriate `--timeout` for your workload

2. **Database Pooling**:
   - Adjust database connection pool settings in `app/db/session.py`

3. **Caching**:
   - Implement Redis caching for frequent API calls

4. **Rate Limiting**:
   - Add rate limiting middleware for public endpoints

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify `DATABASE_URL` is correct
   - Check database server is running
   - Ensure network connectivity and firewall settings

2. **Server Won't Start**:
   - Check port 5000 is available
   - Verify all dependencies are installed
   - Check log output for specific errors

3. **Authentication Issues**:
   - Verify `SECRET_KEY` is set correctly
   - Check JWT token expiration settings

### Logging

Logs are available:
- In the console when running locally
- In the Replit console when deployed on Replit

For more detailed logging, adjust the `LOG_LEVEL` environment variable.