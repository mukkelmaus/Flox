# WebSocket Integration Guide for OneTask

This guide provides detailed information for frontend developers to integrate with OneTask's real-time WebSocket features.

## Introduction

OneTask provides real-time updates through WebSocket connections for task management and notifications. This enables instant UI updates when tasks are created, updated, or completed, as well as delivering system notifications to users.

## Available WebSocket Endpoints

The following WebSocket endpoints are available for real-time features:

### 1. Notifications WebSocket

**Endpoint:** `/api/v1/ws/notifications`

This WebSocket provides real-time notifications for general system events and task updates.

**Authentication:** Required through token parameter

**Example connection:**
```javascript
const token = "your_auth_token";
const socket = new WebSocket(`wss://your-domain.com/api/v1/ws/notifications?token=${token}`);
```

**Message Format:**
```json
{
  "type": "notification",
  "data": {
    "id": 123,
    "title": "Task Completed",
    "content": "You've completed 'Project Proposal'",
    "created_at": "2025-03-23T14:30:00Z",
    "read": false,
    "related_entity_type": "task",
    "related_entity_id": 456
  }
}
```

### 2. Task Updates WebSocket

**Endpoint:** `/api/v1/ws/workspaces/{workspace_id}/tasks`

This WebSocket provides real-time updates for tasks within a specific workspace.

**Authentication:** Required through token parameter

**Example connection:**
```javascript
const token = "your_auth_token";
const workspaceId = 789;
const socket = new WebSocket(`wss://your-domain.com/api/v1/ws/workspaces/${workspaceId}/tasks?token=${token}`);
```

**Message Format:**
```json
{
  "type": "task_update",
  "action": "created", // or "updated", "deleted", "completed"
  "data": {
    "id": 456,
    "title": "New Task",
    "description": "Task description",
    "status": "todo",
    "priority": "high",
    "due_date": "2025-04-01T12:00:00Z",
    "workspace_id": 789,
    "user_id": 101
  }
}
```

### 3. Focus Session WebSocket

**Endpoint:** `/api/v1/ws/focus-sessions/{session_id}`

This WebSocket provides real-time updates for collaborative focus sessions.

**Authentication:** Required through token parameter

**Example connection:**
```javascript
const token = "your_auth_token";
const sessionId = "focus-123";
const socket = new WebSocket(`wss://your-domain.com/api/v1/ws/focus-sessions/${sessionId}?token=${token}`);
```

**Message Format:**
```json
{
  "type": "focus_update",
  "action": "participant_joined", // or "participant_left", "status_change", etc.
  "data": {
    "session_id": "focus-123",
    "user": {
      "id": 101,
      "username": "johndoe"
    },
    "status": "active",
    "current_task_id": 456
  }
}
```

## Integration Example

Here's a simple example of how to integrate with the notifications WebSocket:

```javascript
// Establish WebSocket connection
const token = getAuthToken(); // Get token from your auth system
const notificationSocket = new WebSocket(`wss://your-domain.com/api/v1/ws/notifications?token=${token}`);

// Handle connection open
notificationSocket.onopen = (event) => {
  console.log("Connected to notifications WebSocket");
};

// Handle incoming messages
notificationSocket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === "notification") {
    // Display notification in UI
    showNotification(message.data);
  }
};

// Handle errors
notificationSocket.onerror = (error) => {
  console.error("WebSocket error:", error);
};

// Handle connection close
notificationSocket.onclose = (event) => {
  console.log("Disconnected from notifications WebSocket");
  
  // Optional: Implement reconnection logic
  setTimeout(reconnectWebSocket, 5000);
};

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
  if (notificationSocket) {
    notificationSocket.close();
  }
});
```

## Task-Specific Notifications

The system will automatically send notifications for the following task events:

1. **Task Created** - When a new task is assigned to a user
2. **Task Updated** - When a task's details are modified
3. **Task Completed** - When a task is marked as completed
4. **Task Deleted** - When a task is deleted (soft delete)

Each notification includes information about the task and the action performed.

## Best Practices

1. **Error Handling**: Implement robust error handling and reconnection logic
2. **Message Queuing**: If needed, implement client-side message queuing for offline support
3. **Authentication**: Always include the authentication token in your WebSocket connection
4. **Performance**: Close unused WebSocket connections to conserve resources
5. **Testing**: Test WebSocket connections with different network conditions

## Additional Resources

For testing the WebSocket connections, you can use the included test scripts:
- `websocket_client_test.py` - Python test script for WebSocket connections
- `websocket_test.html` - HTML/JavaScript test page for WebSocket connections

## Troubleshooting

Common issues:

1. **Authentication Failures**: Ensure your token is valid and properly included in the URL
2. **Connection Timeouts**: The server may close idle connections after a period of inactivity
3. **Message Format Errors**: Ensure you're sending properly formatted JSON