#!/bin/bash
# Prestart script for OneTask API
# This script runs before the production server starts

# Environment Detection
echo "Detecting environment..."
env=${ENVIRONMENT:-production}
echo "Environment: $env"

# Load environment variables
if [ "$env" = "production" ]; then
  echo "Loading production environment variables..."
  if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | xargs)
    echo "Production environment variables loaded"
  else
    echo "Warning: .env.production file not found"
  fi
else
  echo "Loading development environment variables..."
  if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Development environment variables loaded"
  else
    echo "Warning: .env file not found"
  fi
fi

# Check database connection
echo "Checking database connection..."
python -c "from app.db.session import SessionLocal; s = SessionLocal(); s.execute('SELECT 1'); s.close()" || { echo "Database connection failed"; exit 1; }
echo "Database connection successful"

# Run database migrations if needed
echo "Running database setup (if needed)..."
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)" || { echo "Database setup failed"; exit 1; }
echo "Database setup completed"

# Validating environment
echo "Validating environment..."
python -c "from app.core.config import settings; print(f'API version: {settings.VERSION}, Environment: {settings.ENVIRONMENT}')" || { echo "Environment validation failed"; exit 1; }
echo "Environment validated successfully"

echo "Prestart completed successfully"