# OneTask Real-time API Documentation

## Overview

The OneTask API provides real-time capabilities through WebSocket connections and RESTful endpoints. This document explains how to use these features to implement real-time notifications and updates in your frontend application.

## WebSocket Endpoints

### Notifications WebSocket

This WebSocket provides real-time notifications for the authenticated user.

```
WebSocket URL: ws://<host>/ws/notifications
```

**Authentication:** Include the JWT token as a query parameter:

```
ws://<host>/ws/notifications?token=<your_jwt_token>
```

**Received Message Format:**

```json
{
  "type": "notification",
  "notification_id": 123,
  "title": "Notification Title",
  "content": "Notification content text",
  "notification_type": "task",
  "related_entity_type": "task",
  "related_entity_id": 456,
  "created_at": "2025-03-23T22:40:01.352Z",
  "data": {
    "task_id": 456,
    "action": "updated",
    "workspace_id": 789,
    "actor_id": 101
  }
}
```

### Workspace Tasks WebSocket

This WebSocket provides real-time updates for tasks in a specific workspace.

```
WebSocket URL: ws://<host>/ws/tasks/<workspace_id>
```

**Authentication:** Include the JWT token as a query parameter:

```
ws://<host>/ws/tasks/<workspace_id>?token=<your_jwt_token>
```

**Received Message Format:**

The message format is the same as the notifications WebSocket, but filtered to only include task-related events for the specified workspace.

### Focus Session WebSocket

This WebSocket provides real-time updates for collaborative focus sessions.

```
WebSocket URL: ws://<host>/ws/focus-session/<session_id>
```

**Authentication:** Include the JWT token as a query parameter:

```
ws://<host>/ws/focus-session/<session_id>?token=<your_jwt_token>
```

**Received Message Format:**

```json
{
  "type": "focus_session_update",
  "session_id": "123",
  "sender_id": 101,
  "data": {
    // Session-specific data
  }
}
```

## RESTful Real-time Events API

The API also provides RESTful endpoints to send real-time events to users.

### Send Task Event

```
POST /api/v1/realtime/events/task
```

**Request Body:**

```json
{
  "task_id": 456,
  "title": "Task Title",
  "action": "updated",
  "workspace_id": 789,
  "target_user_ids": [101, 102]
}
```

| Field | Description |
|-------|-------------|
| task_id | ID of the task |
| title | Title of the task |
| action | Action performed on the task (created, updated, completed, deleted) |
| workspace_id | (Optional) ID of the workspace |
| target_user_ids | (Optional) List of user IDs to notify. If empty, only notifies the current user. |

**Response:**

```json
{
  "status": "notifications sent",
  "recipient_count": 2
}
```

### Send Workspace Event

```
POST /api/v1/realtime/events/workspace
```

**Request Body:**

```json
{
  "workspace_id": 789,
  "title": "Workspace Update",
  "content": "The workspace has been updated.",
  "type": "workspace",
  "related_entity_type": "workspace",
  "related_entity_id": 789,
  "data": {},
  "exclude_user_ids": [101]
}
```

| Field | Description |
|-------|-------------|
| workspace_id | ID of the workspace |
| title | Title of the notification |
| content | Content of the notification |
| type | (Optional) Type of notification (default: "workspace") |
| related_entity_type | (Optional) Type of related entity |
| related_entity_id | (Optional) ID of related entity |
| data | (Optional) Additional data |
| exclude_user_ids | (Optional) List of user IDs to exclude from notification |

**Response:**

```json
{
  "status": "workspace notification sent"
}
```

### Send System Event

```
POST /api/v1/realtime/events/system
```

**Request Body:**

```json
{
  "title": "System Notification",
  "content": "Important system message.",
  "user_id": 101,
  "data": {}
}
```

| Field | Description |
|-------|-------------|
| title | Title of the notification |
| content | Content of the notification |
| user_id | (Optional) User ID to notify. If not provided, notifies the current user. |
| data | (Optional) Additional data |

**Response:**

```json
{
  "status": "system notification sent"
}
```

## Implementation Examples

### Frontend (JavaScript)

```javascript
// Connect to notifications WebSocket
const token = "your_jwt_token";
const notificationSocket = new WebSocket(`ws://localhost:5000/ws/notifications?token=${token}`);

notificationSocket.onopen = () => {
  console.log('Connected to notification websocket');
};

notificationSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notification received:', data);
  
  // Handle notification (e.g., display in UI)
  showNotification(data.title, data.content, data.notification_type);
};

notificationSocket.onclose = () => {
  console.log('Disconnected from notification websocket');
};

// Send a task event
async function sendTaskEvent(taskId, title, action) {
  const response = await fetch('/api/v1/realtime/events/task', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      task_id: taskId,
      title: title,
      action: action
    })
  });
  
  const result = await response.json();
  console.log('Event sent:', result);
}
```

### Backend (Python)

```python
from app.websockets.notification_handlers import send_task_notification

# Send a task notification from your API endpoint
@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Update task in database
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "completed"
    task.completed_at = datetime.now()
    db.commit()
    
    # Send real-time notification
    await send_task_notification(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
        task_title=task.title,
        action="completed",
        workspace_id=task.workspace_id,
    )
    
    return {"status": "success"}
```

## Testing

You can test the WebSocket functionality using:

1. The included `websocket_client_test.py` script:
   ```
   python websocket_client_test.py <your_jwt_token> [workspace_id]
   ```

2. The included `websocket_test.html` page - open in a browser, enter your JWT token, and test sending/receiving events.

## Integration with Task Service

To automatically send real-time updates when tasks are created, updated, or deleted, the task service has been updated to use the notification handlers. For example:

```python
# In app/services/task_service.py
from app.websockets.notification_handlers import send_task_notification

async def mark_task_completed(db: Session, task: Task) -> Task:
    """Mark a task as completed."""
    task.status = "completed"
    task.completed_at = datetime.now()
    db.commit()
    
    # Send real-time notification
    await send_task_notification(
        db=db,
        user_id=task.user_id,
        task_id=task.id,
        task_title=task.title,
        action="completed",
        workspace_id=task.workspace_id,
    )
    
    return task
```

## Best Practices

1. **Handle Connection Errors:** Implement reconnection logic in the frontend to handle connection drops.

2. **Authenticate WebSocket Connections:** Always include the JWT token when connecting to WebSocket endpoints.

3. **Message Format Consistency:** Maintain consistent message formats between WebSocket and API endpoints.

4. **Performance Considerations:** Be selective about what events trigger notifications to avoid overwhelming users.

5. **Fallback Mechanism:** Implement polling as a fallback if WebSocket connections fail.