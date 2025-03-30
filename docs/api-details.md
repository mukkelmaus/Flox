
# OneTask API Documentation

This document provides detailed information about all available API endpoints in the OneTask application.

## Base URL
All API endpoints are prefixed with `/api/v1`

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Login
- **POST** `/login/access-token`
  - Get JWT access token
  - Body: `{"username": "string", "password": "string"}`
  - Returns: `{"access_token": "string", "token_type": "bearer"}`

#### Test Token
- **POST** `/login/test-token`
  - Verify if token is valid
  - Requires: Authentication
  - Returns: Current user information

#### Refresh Token
- **POST** `/login/refresh-token`
  - Get new access token using refresh token
  - Body: `{"refresh_token": "string"}`
  - Returns: `{"access_token": "string", "token_type": "bearer"}`

### User Management

#### Create User
- **POST** `/users/`
  - Register new user
  - Body: `{"email": "string", "password": "string", "full_name": "string"}`
  - Returns: Created user object

#### Get Current User
- **GET** `/users/me`
  - Get current user's profile
  - Requires: Authentication
  - Returns: User profile object

#### Update Current User
- **PUT** `/users/me`
  - Update current user's profile
  - Requires: Authentication
  - Body: `{"email": "string", "full_name": "string"}`
  - Returns: Updated user object

#### Get User by ID
- **GET** `/users/{user_id}`
  - Get user profile by ID
  - Requires: Authentication
  - Returns: User profile object

#### Delete User
- **DELETE** `/users/{user_id}`
  - Delete user account
  - Requires: Authentication (Admin only)

### Task Management

#### List Tasks
- **GET** `/tasks/`
  - Get all tasks for current user
  - Requires: Authentication
  - Query params: 
    - `skip`: int (pagination offset)
    - `limit`: int (pagination limit)
    - `status`: string (filter by status)
  - Returns: List of task objects

#### Create Task
- **POST** `/tasks/`
  - Create new task
  - Requires: Authentication
  - Body: `{"title": "string", "description": "string", "due_date": "datetime"}`
  - Returns: Created task object

#### Get Task
- **GET** `/tasks/{task_id}`
  - Get task details
  - Requires: Authentication
  - Returns: Task object

#### Update Task
- **PUT** `/tasks/{task_id}`
  - Update task details
  - Requires: Authentication
  - Body: `{"title": "string", "description": "string", "status": "string"}`
  - Returns: Updated task object

#### Delete Task
- **DELETE** `/tasks/{task_id}`
  - Delete task
  - Requires: Authentication

### Workspace Management

#### List Workspaces
- **GET** `/workspaces/`
  - Get all workspaces for current user
  - Requires: Authentication
  - Returns: List of workspace objects

#### Create Workspace
- **POST** `/workspaces/`
  - Create new workspace
  - Requires: Authentication
  - Body: `{"name": "string", "description": "string"}`
  - Returns: Created workspace object

#### Get Workspace
- **GET** `/workspaces/{workspace_id}`
  - Get workspace details
  - Requires: Authentication
  - Returns: Workspace object

#### Update Workspace
- **PUT** `/workspaces/{workspace_id}`
  - Update workspace details
  - Requires: Authentication
  - Body: `{"name": "string", "description": "string"}`
  - Returns: Updated workspace object

#### Delete Workspace
- **DELETE** `/workspaces/{workspace_id}`
  - Delete workspace
  - Requires: Authentication

### AI Features

#### Analyze Task
- **POST** `/ai/analyze`
  - Analyze task content using AI
  - Requires: Authentication
  - Body: `{"task_id": "string", "content": "string"}`
  - Returns: Analysis results

#### Get Suggestions
- **POST** `/ai/suggest`
  - Get AI-powered task suggestions
  - Requires: Authentication
  - Body: `{"context": "string"}`
  - Returns: List of suggestions

#### Prioritize Tasks
- **POST** `/ai/prioritize`
  - Get AI-powered task prioritization
  - Requires: Authentication
  - Body: `{"task_ids": ["string"]}`
  - Returns: Prioritized task list

### Gamification

#### Get User Stats
- **GET** `/gamification/stats`
  - Get user's gamification statistics
  - Requires: Authentication
  - Returns: User stats object

#### Get User Streak
- **GET** `/gamification/streak`
  - Get user's current streak information
  - Requires: Authentication
  - Returns: Streak object

### WebSocket Endpoints

#### Task Updates
- **WS** `/ws/tasks`
  - Real-time task updates
  - Requires: Authentication via query parameter
  - Query params: `token=<your_jwt_token>`

#### Notifications
- **WS** `/ws/notifications`
  - Real-time user notifications
  - Requires: Authentication via query parameter
  - Query params: `token=<your_jwt_token>`

### Utility Endpoints

#### Health Check
- **GET** `/health`
  - Check system health status
  - Returns: Health check information

#### API Information
- **GET** `/`
  - Get API information
  - Returns: API metadata

#### API Documentation
- **GET** `/docs`
  - Interactive Swagger documentation
- **GET** `/redoc`
  - ReDoc documentation

## Error Responses

All endpoints follow a standard error response format:
```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
