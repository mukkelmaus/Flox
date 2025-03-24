# OneTask Backend API

OneTask is an AI-powered to-do application designed to help users — especially creatives, individuals with ADHD, and neurodivergent people — effectively organize, prioritize, and manage their tasks.

## Features

### Core Features

1. **Automatic Task Prioritization**: Logic and endpoints to prioritize tasks based on user-defined or AI-enhanced criteria.
2. **Focus Mode Support**: Endpoint filters to deliver only currently relevant tasks based on context or time sensitivity.
3. **AI-Assisted Planning**: Integrate AI to break down complex tasks into smaller subtasks and provide planning suggestions.
4. **Support for Multiple View Modes**: Backend structure supporting list, card, calendar, and Kanban representations.
5. **Task History Tracking**: Persistent storage and retrieval of completed task history.
6. **Third-Party Integration Layer**: Secure API endpoints and sync logic for services like Google Calendar and Todoist.
7. **User Theme Settings Endpoint**: Deliver theme configuration data for the frontend to apply user-specific themes.
8. **AI Analytics & Workflow Assistant**: AI-driven endpoints for task analysis and productivity guidance.
9. **Workspace & Team Management**: Multi-user workspaces with role-based access control.
10. **API-First Design for Cross-Platform Support**: All features accessible through clean, well-documented RESTful APIs.
11. **Customer Support Interface**: Endpoints to manage and log support queries.
12. **Subscription Management**: Backend logic to handle freemium/pro/org-tier features, payment hooks, and access restrictions.

### Additional Features

13. **Smart Notifications & Reminders**: Customizable reminder schedules with user preference storage.
14. **Gamification Tracking**: Track engagement, streaks, and reward progress server-side.
15. **Accessibility Settings**: API-level support for frontend rendering preferences (e.g., font size, color contrast settings).

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL database

### Environment Variables

The following environment variables should be set (see `.env.example` for reference):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `SESSION_SECRET`: Secret key for user sessions
- `OPENAI_API_KEY`: OpenAI API key for AI features (if using)
- `SERVER_HOST`: Base URL for the server (e.g., https://onetask.replit.app)
- `ENVIRONMENT`: "development" or "production"
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/onetask-api.git
cd onetask-api

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize the database
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

### Development

```bash
# Run the development server with hot reloading
python main_uvicorn.py
# or
./run_dev_server.sh
```

### Production Deployment

For production deployment, we use Gunicorn with Uvicorn workers:

```bash
# Run the production server
./production_server.sh
```

#### Deployment on Replit

OneTask API is designed to run seamlessly on Replit:

1. Create a new Replit from this repository
2. Set up the required environment variables in Replit Secrets
3. Deploy using the Replit deployment button

The server will automatically run with optimized production settings.

### API Documentation

When the server is running, you can access the API documentation at:

- Swagger UI: `/docs`
- OpenAPI JSON: `/api/v1/openapi.json`

### Testing

```bash
# Run tests
pytest

# Run specific test file
pytest tests/api/test_tasks.py
```

## Deployment Architecture

The OneTask API uses a tiered architecture for deployment:

1. **Application Tier**: FastAPI application with route definitions, business logic, and request handling
2. **ASGI Server**: Uvicorn for handling asynchronous requests
3. **Process Manager**: Gunicorn for process management and worker orchestration
4. **Database Tier**: PostgreSQL for data persistence

## Production Configuration

For production environments:

1. Use the `production_server.sh` script which properly configures Gunicorn with Uvicorn workers
2. Set `ENVIRONMENT=production` in your environment variables
3. Configure appropriate `ALLOWED_ORIGINS` for CORS security
4. Ensure database connection pooling is properly configured
5. Set proper timeouts and worker settings as needed

