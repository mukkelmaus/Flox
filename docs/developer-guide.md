# OneTask Developer Guide

This guide provides essential information for developers working on the OneTask application.

## Architecture Overview

OneTask is built with a modular architecture using FastAPI for the backend REST API. The application follows these design principles:

- **Separation of Concerns**: Code is organized into models, schemas, services, and API endpoints
- **Dependency Injection**: FastAPI's dependency system is used extensively
- **Data Validation**: Pydantic models ensure data consistency
- **Authentication**: JWT-based authentication with role-based access control

## Project Structure

```
app/
├── api/             # API routes
│   └── api_v1/      # API version 1
│       ├── api.py   # Main router
│       └── endpoints/  # Specific endpoint modules
├── core/            # Core application components
│   ├── config.py    # Configuration settings
│   └── security.py  # Authentication and security
├── db/              # Database connection and session management
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas for validation and serialization
├── services/        # Business logic and services
└── utils/           # Utility functions and helpers
```

## Getting Started

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see Configuration section)
4. Run database migrations: `alembic upgrade head`
5. Start the server: `python -m run_dev_server.sh`

### Configuration

The application uses environment variables for configuration:

- `SECRET_KEY`: Secret key for JWT token generation
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: API key for OpenAI integration
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 60 * 24 * 8)

### Development Server

For development, use the Uvicorn server which provides hot reloading:

```bash
./run_dev_server.sh
```

The API will be available at http://localhost:5000 with full documentation at http://localhost:5000/docs.

For deployment on Replit, the application automatically uses Gunicorn with a simpler WSGI interface.

## Authentication Implementation

### Backend Components

The authentication system is implemented with the following components:

- `app/core/security.py`: Contains functions for JWT token generation, password hashing, and user extraction from tokens
- `app/api/api_v1/endpoints/login.py`: Provides endpoints for token generation and verification
- `app/api/api_v1/endpoints/users.py`: User registration and management

### Testing Authentication

To test authentication:

1. Create a user with a POST request to `/api/v1/users/`
2. Generate a token with a POST to `/api/v1/login/access-token`
3. Use the token in subsequent requests in the Authorization header: `Bearer <token>`

## Testing

The application uses pytest for testing:

```bash
pytest
```

For specific test categories:

```bash
pytest tests/api/  # Test API endpoints
pytest tests/unit/  # Test utility functions and services
```

## User Model

The User model provides these important fields:

- `id`: Unique identifier
- `username`: Unique username (alphanumeric)
- `email`: User's email address (must be unique)
- `password_hash`: Hashed password
- `full_name`: Optional full name
- `is_active`: Whether the user is active
- `is_superuser`: Whether the user has superuser privileges
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Adding New Features

When adding new features, follow these steps:

1. Add SQLAlchemy models in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Create API endpoints in `app/api/api_v1/endpoints/`
5. Register new router in `app/api/api_v1/api.py`
6. Write tests for new functionality

## Code Style and Standards

Follow these guidelines for consistent code:

- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Use black for code formatting
- Follow PEP 8 conventions
- Write unit tests for all functionality