# Deployment Guide

## Environment Setup

1. Configure environment variables in Replit Secrets:
   - `SECRET_KEY`: JWT secret key
   - `DATABASE_URL`: PostgreSQL connection string
   - `OPENAI_API_KEY`: (optional) For AI features

2. Initialize the database:
   ```bash
   python init_db.py
   ```

3. Production Configuration:
   - Update `.env` with production settings
   - Enable CORS for your frontend domain
   - Configure proper logging levels

## Deployment Steps

1. Click "Deploy" in Replit workspace
2. Choose "Production deployment"
3. Configure deployment settings
4. Deploy the application

## Health Monitoring

The API includes health check endpoints:
- `/health`: Basic server health
- `/api/v1/health`: Detailed system status

## Security Configuration

1. JWT Settings:
   - Set strong `SECRET_KEY` in Secrets
   - Configure token expiration in `app/core/config.py`

2. CORS Settings:
   - Configure allowed origins in `app/core/config.py`
   - Add your frontend domain to allowed origins


## Troubleshooting

Common issues and solutions:

1. Database Connection:
   - Verify DATABASE_URL is correct
   - Check database connectivity
   - Verify table migrations

2. Authentication Issues:
   - Check SECRET_KEY is set
   - Verify JWT token configuration
   - Test token endpoints

3. Frontend Connection:
   - Verify CORS settings
   - Test WebSocket connectivity
   - Use the test tools in `public/`