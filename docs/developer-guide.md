# OneTask Developer Guide

This guide provides comprehensive information for developers working on the OneTask backend. It covers the architecture, development workflows, and instructions for extending functionality.

## Architecture Overview

OneTask follows a modular architecture with clear separation of concerns:

```
app/
├── api/               # API layer with endpoints and route definitions
│   └── api_v1/        # API version 1
│       ├── api.py     # Main router
│       └── endpoints/ # API endpoints by resource
├── core/              # Core functionality and configuration
├── db/                # Database setup and session management
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic schemas for request/response validation
├── services/          # Business logic layer
└── utils/             # Utility functions and helpers
```

### Key Components

1. **API Layer**: Contains API endpoints organized by feature area. Each endpoint file typically corresponds to a specific resource (e.g., tasks, users).

2. **Models Layer**: Contains SQLAlchemy ORM models representing database tables.

3. **Schemas Layer**: Contains Pydantic models for request/response validation and documentation.

4. **Services Layer**: Contains business logic for each feature area, separated from the API endpoints.

5. **Core**: Contains configuration, security, and other core functionality.

6. **DB**: Manages database connections and session handling.

## Key Features

OneTask includes the following key features:

### 1. Authentication and User Management

- JWT-based authentication
- User registration, login, and profile management
- Password hashing and verification
- Role-based access control

### 2. Task Management

- CRUD operations for tasks
- Task categorization with tags
- Task prioritization with AI enhancement
- Subtasks and task breakdown
- Task history tracking

### 3. Focus Mode

- Context-aware task filtering
- Energy level and time matching
- Priority-based task suggestions

### 4. AI Integration

- Task breakdown with OpenAI
- Task analysis and productivity insights
- Smart task suggestions

### 5. Third-Party Integrations

- Google Calendar integration
- Todoist integration
- GitHub integration
- OAuth flow for connection management

### 6. Workspace and Team Management

- Workspace creation and management
- Member invitations and role management
- Access control within workspaces

### 7. Subscription Management

- Subscription plans and billing
- Feature access control
- Trial and payment processing

### 8. Gamification

- Achievement tracking
- Streaks and user statistics
- Points and levels

### 9. Notifications

- Task reminders and due date notifications
- System notifications
- Notification preferences

## Development Workflow

### Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   pip install .
   ```
   This installs all dependencies defined in pyproject.toml.
3. Set environment variables (see `.env.example`)
4. Run migrations:
   ```
   alembic upgrade head
   ```
5. Start the development server:
   ```
   python -m uvicorn app.main:app --reload
   ```

### Code Organization

When adding a new feature, follow these steps:

1. Add database models in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Add business logic in `app/services/`
4. Add API endpoints in `app/api/api_v1/endpoints/`
5. Register endpoints in `app/api/api_v1/api.py`
6. Add tests in `tests/`

### Testing

We use pytest for testing. Tests are organized by type:

- `tests/unit/`: Unit tests for individual components
- `tests/api/`: API integration tests
- `tests/conftest.py`: Common fixtures and utilities

Run tests with:

```
pytest
```

Run a specific test file:

```
pytest tests/api/test_tasks.py
```

### Database Migrations

We use Alembic for database migrations. To create a new migration:

```
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```
alembic upgrade head
```

## Extending OneTask

### Adding a New Feature

To add a new feature to OneTask:

1. **Plan**: Determine the database schema, API endpoints, and business logic needed.

2. **Models**: Create SQLAlchemy models in `app/models/`. Example:

   ```python
   from sqlalchemy import Column, Integer, String, ForeignKey
   from sqlalchemy.orm import relationship
   
   from app.db.base_class import Base
   
   class FeatureModel(Base):
       """New feature model."""
       name = Column(String, nullable=False)
       description = Column(String, nullable=True)
       user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
       
       user = relationship("User", back_populates="features")
   ```

3. **Schemas**: Create Pydantic models in `app/schemas/`. Example:

   ```python
   from typing import Optional
   from pydantic import BaseModel
   
   class FeatureBase(BaseModel):
       name: str
       description: Optional[str] = None
   
   class FeatureCreate(FeatureBase):
       pass
   
   class FeatureUpdate(BaseModel):
       name: Optional[str] = None
       description: Optional[str] = None
   
   class Feature(FeatureBase):
       id: int
       user_id: int
       
       class Config:
           orm_mode = True
   ```

4. **Services**: Add business logic in `app/services/`. Example:

   ```python
   from typing import List, Optional
   from sqlalchemy.orm import Session
   
   from app.models.feature import FeatureModel
   from app.schemas.feature import FeatureCreate, FeatureUpdate
   
   def get_features(db: Session, user_id: int) -> List[FeatureModel]:
       return db.query(FeatureModel).filter(FeatureModel.user_id == user_id).all()
   
   def create_feature(db: Session, feature_in: FeatureCreate, user_id: int) -> FeatureModel:
       feature = FeatureModel(**feature_in.dict(), user_id=user_id)
       db.add(feature)
       db.commit()
       db.refresh(feature)
       return feature
   ```

5. **API Endpoints**: Create endpoints in `app/api/api_v1/endpoints/`. Example:

   ```python
   from typing import List
   
   from fastapi import APIRouter, Depends, HTTPException, status
   from sqlalchemy.orm import Session
   
   from app import models, schemas
   from app.api import deps
   from app.services import feature_service
   
   router = APIRouter()
   
   @router.get("/", response_model=List[schemas.Feature])
   def read_features(
       db: Session = Depends(deps.get_db),
       current_user: models.User = Depends(deps.get_current_active_user),
   ):
       """
       Retrieve features.
       """
       features = feature_service.get_features(db, current_user.id)
       return features
   
   @router.post("/", response_model=schemas.Feature)
   def create_feature(
       *,
       db: Session = Depends(deps.get_db),
       feature_in: schemas.FeatureCreate,
       current_user: models.User = Depends(deps.get_current_active_user),
   ):
       """
       Create new feature.
       """
       feature = feature_service.create_feature(db, feature_in, current_user.id)
       return feature
   ```

6. **Register Endpoints**: Add your router to `app/api/api_v1/api.py`:

   ```python
   from app.api.api_v1.endpoints import feature
   
   api_router.include_router(feature.router, prefix="/features", tags=["features"])
   ```

7. **Tests**: Add tests in `tests/`. Example:

   ```python
   def test_create_feature(client, token_headers):
       response = client.post(
           "/api/v1/features/",
           headers=token_headers,
           json={"name": "Test Feature", "description": "Test Description"},
       )
       assert response.status_code == 200
       data = response.json()
       assert data["name"] == "Test Feature"
       assert data["description"] == "Test Description"
   ```

### Implementing an Integration

To add a new third-party integration:

1. Add the integration to `get_available_integrations()` in `app/services/integration_service.py`.

2. Implement OAuth flow by adding a case to `get_integration_auth_url()`.

3. Implement the sync function for the new integration.

4. Add the integration endpoints to `app/api/api_v1/endpoints/integrations.py`.

Example sync function:

```python
async def sync_with_new_service(
    db: Session, 
    integration: Integration,
    user: User,
) -> Dict[str, Any]:
    """
    Sync tasks with the new service.
    
    Args:
        db: Database session
        integration: Integration
        user: User
        
    Returns:
        Sync results
    """
    logger.info(f"Syncing with New Service for user {user.id}")
    
    try:
        # Check if token is expired and refresh if needed
        if integration.token_expiry and integration.token_expiry < datetime.now():
            success = await refresh_access_token(db, integration)
            if not success:
                return {
                    "status": "error",
                    "error": "Failed to refresh access token",
                    "items_synced": 0,
                    "last_sync": integration.last_sync,
                }
        
        # Implement integration-specific logic here
        # ...
        
        # Update last_sync time
        integration.last_sync = datetime.now()
        db.add(integration)
        db.commit()
        
        return {
            "status": "success",
            "items_synced": items_synced,
            "last_sync": integration.last_sync,
        }
        
    except Exception as e:
        logger.error(f"Error syncing with New Service: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "items_synced": 0,
            "last_sync": integration.last_sync,
        }
```

### Adding AI Features

To implement a new AI feature:

1. Create a new function in `app/services/ai_service.py`.
2. Implement the OpenAI API call with appropriate prompts and response handling.
3. Add error handling and fallbacks.
4. Create an API endpoint to expose the feature.

Example AI service function:

```python
async def generate_task_recommendations(user: models.User, context: str) -> List[Dict[str, Any]]:
    """
    Generate AI task recommendations based on user context.
    
    Args:
        user: User object
        context: Context for recommendations
        
    Returns:
        List of task recommendations
    """
    if not settings.ENABLE_AI_FEATURES:
        logger.warning("AI features are disabled, returning empty recommendations")
        return []
    
    try:
        # Prepare prompt for the AI
        prompt = f"""
        Please suggest relevant tasks for a user based on the following context:
        
        User Information:
        - Username: {user.username}
        - Context: {context}
        
        Provide 3-5 task suggestions that would be relevant for this context.
        
        Return your response as a JSON array with the following structure:
        [
            {{
                "title": "Task Title",
                "description": "Task description",
                "priority": "medium",
                "estimated_minutes": 30
            }},
            ...
        ]
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o"
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in productivity and task management."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        recommendations = json.loads(content)
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating task recommendations: {str(e)}")
        raise
```

## Using Feature Flags

OneTask uses feature flags to manage feature access based on subscriptions. These are controlled through the `check_feature_access` function in `app/services/subscription_service.py`.

To implement a feature that respects subscription tiers:

1. Add a check for the feature access in your API endpoint:

```python
from app.services.subscription_service import check_feature_access
from app.utils.dependencies import get_current_subscription

@router.post("/premium-feature", response_model=schemas.PremiumFeatureResponse)
def use_premium_feature(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    current_subscription: Optional[models.Subscription] = Depends(get_current_subscription),
):
    """
    Use a premium feature.
    """
    # Check if user has access to this feature
    if not check_feature_access(current_subscription, "premium_feature", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a premium subscription."
        )
    
    # Implement premium feature
    ...
```

2. Or use the provided dependency:

```python
from app.utils.dependencies import verify_premium_access

@router.post("/ai-feature", response_model=schemas.AIFeatureResponse)
def use_ai_feature(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    _: None = Depends(verify_premium_access),
):
    """
    Use an AI feature (premium only).
    """
    # Feature implementation goes here
    ...
```

## Deployment

OneTask supports different deployment modes:

### 1. Development Mode

Running with Uvicorn directly for development:

```
python -m uvicorn app.main:app --reload
```

### 2. Production Mode

Running with Gunicorn and Uvicorn workers:

```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker
```

### 3. Replit Compatibility Mode

The application automatically detects if it's running in Replit and provides a simplified WSGI interface for compatibility.

### Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection URL
- `SECRET_KEY`: Secret key for JWT tokens
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SERVER_HOST`: Server hostname for callback URLs

## Contributing

We welcome contributions to OneTask! Please follow our guidelines:

1. Create an issue or use an existing one
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Add tests for your changes
6. Run the tests: `pytest`
7. Submit a pull request

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check that PostgreSQL is running
   - Verify the `DATABASE_URL` environment variable
   - Ensure the database exists and is accessible

2. **Authentication Issues**:
   - Check that the `SECRET_KEY` is set
   - Verify that tokens are being sent correctly
   - Check token expiration time

3. **AI Feature Issues**:
   - Verify the `OPENAI_API_KEY` is set and valid
   - Check `ENABLE_AI_FEATURES` is set to `True`
   - Look for error logs from the OpenAI client

4. **Integration Issues**:
   - Check that OAuth callback URLs are correctly configured
   - Verify that tokens are being refreshed properly
   - Check integration configuration

### Logging

We use Python's standard logging module. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Contacting Support

For urgent issues or questions, contact the OneTask development team at [dev@onetask.example.com].