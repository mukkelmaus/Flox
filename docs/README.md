# OneTask API Documentation

Welcome to the OneTask API documentation. This repository contains detailed information about the OneTask API, its endpoints, and how to use them.

## Introduction

OneTask is an AI-powered to-do application designed specifically for creatives, individuals with ADHD, and neurodivergent people. It helps users effectively organize, prioritize, and manage their tasks with AI assistance.

## Contents

The documentation is organized into the following sections:

- [Authentication](authentication.md) - Details about the authentication system
- [Authentication Implementation](auth-implementation.md) - Technical details of the auth implementation
- [Developer Guide](developer-guide.md) - Guide for developers working on the project

## Getting Started

### Authentication

To use the OneTask API, you'll need to authenticate. The API uses JWT (JSON Web Tokens) for authentication. Here's a quick overview of the authentication flow:

1. Register a new user:
   ```
   POST /api/v1/users/
   {
     "email": "user@example.com",
     "username": "username",
     "password": "password",
     "full_name": "User Name"
   }
   ```

2. Obtain an access token:
   ```
   POST /api/v1/login/access-token
   Form data:
   - username: user@example.com (or username)
   - password: password
   ```

3. Use the token in subsequent requests:
   ```
   GET /api/v1/users/me
   Headers:
   - Authorization: Bearer <your_token>
   ```

For more details, see the [Authentication documentation](authentication.md).

### API Endpoints

The API is organized into the following main sections:

- `/api/v1/users/` - User management
- `/api/v1/tasks/` - Task management
- `/api/v1/workspaces/` - Workspace management
- `/api/v1/ai/` - AI-powered features
- `/api/v1/integrations/` - Third-party integrations

Each section has its own set of endpoints for creating, reading, updating, and deleting resources.

## Running the API

The API can be run in two modes:

1. Development mode (Uvicorn/ASGI):
   ```bash
   ./run_dev_server.sh
   ```
   This provides full FastAPI functionality, including interactive documentation.

2. Production mode (Gunicorn/WSGI):
   ```bash
   ./start.sh
   ```
   This is optimized for production use, particularly on Replit.

## API Documentation

When running in development mode, interactive API documentation is available at:

- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Technical Details

The API is built with:

- FastAPI - Modern, high-performance web framework
- SQLAlchemy - SQL toolkit and ORM
- Pydantic - Data validation and settings management
- PostgreSQL - Relational database
- JSON Web Tokens - Stateless authentication
- OpenAI API - AI-powered features

For more information, see the [Developer Guide](developer-guide.md).