# OneTask API

OneTask is an AI-powered task management API designed to provide intelligent task organization and management capabilities. This backend focuses on core functionality while leaving UI concerns to the frontend.

## Core Features

- Task Management with AI Prioritization
- User Authentication & Authorization
- Workspace Organization
- Real-time Notifications via WebSockets
- External Service Integrations
- Comprehensive API Documentation

## Technology Stack

- Backend Framework: FastAPI
- Database: PostgreSQL
- Authentication: JWT-based
- Real-time: WebSocket Support
- AI Integration: OpenAI API
- Documentation: OpenAPI/Swagger

## Quick Start

1. Set required environment variables in `.env`
2. Initialize database: `python init_db.py`
3. Start the server: Click the Run button or use workflow "Start FastAPI"

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Development

The project follows a clean architecture with:

```
app/
├── api/          # API endpoints
├── core/         # Core configuration
├── db/           # Database setup
├── models/       # Database models
├── schemas/      # Data validation
└── services/     # Business logic
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Deployment

Deploy directly on Replit:
1. Click the "Deploy" button
2. Choose "Production deployment"
3. Configure environment variables
4. Deploy the application

## Resources

- [API Details](./api-details.md)
- [Authentication Guide](./authentication.md)
- [Developer Guide](./developer-guide.md)
- [WebSocket API](./websocket_api.md)