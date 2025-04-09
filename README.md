# OneTask API

One Task is an AI-powered to-do application designed to support neurodivergent users with intelligent task management and personalized productivity tools.

## Features

- **AI Task Prioritization**: Intelligently organize tasks based on importance, deadlines, and user patterns
- **Smart Focus Mode**: Optimize task selection based on energy levels and available time
- **Workspaces**: Organize tasks into customizable workspaces for better context management
- **Real-time Collaboration**: WebSocket integration for collaborative workspaces
- **Neurodivergent-friendly Design**: Customizable interfaces with sensory-friendly options
- **Third-party Integrations**: Connect with popular tools like Google Calendar, Todoist, and GitHub
- **Comprehensive Gamification**: Achievement system, streaks, and customizable rewards
- **Detailed Analytics**: Productivity insights with AI-powered recommendations

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT-based with role-based access control
- **Real-time Features**: WebSockets for notifications and collaborative editing
- **AI Integration**: OpenAI API for task analysis and recommendations
- **Documentation**: Interactive OpenAPI docs (Swagger UI)

## Quick Start

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install .` (using pyproject.toml)
3. Set up environment variables: `cp .env.example .env`
4. Run the development server: `./run_dev_server.sh`

### Deployment Options

We provide multiple deployment guides for different user needs:

- **[Technical Deployment Guide](docs/deployment-guide.md)**: Comprehensive guide for experienced developers
- **[Simple Self-Hosting Guide](docs/simple-self-hosting-guide.md)**: Step-by-step instructions for non-technical users
- **[Docker Deployment Guide](docs/docker-deployment-guide.md)**: Easiest deployment method using Docker containers

### Production Deployment

For production deployment on Replit, use our optimized configuration:

1. Set required environment variables in Replit Secrets
2. Run the production server: `./production_server.sh`

## API Documentation

Once the server is running, access the interactive API documentation:

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## Testing

Run the API test script to verify functionality:

```bash
python test_api.py
```

## Developer Resources

- [Authentication Guide](./docs/authentication.md)
- [WebSocket API](./docs/websocket_api.md)
- [Integration Guide](./docs/integration-guide.md)
- [Developer Guide](./docs/developer-guide.md)

## License

MIT License

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.