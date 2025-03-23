# WebSocket Integration Guide for OneTask

This guide provides detailed information for frontend developers to integrate with OneTask's real-time WebSocket features.

## Introduction

OneTask provides real-time updates through WebSocket connections for task management and notifications. This enables instant UI updates when tasks are created, updated, or completed, as well as delivering system notifications to users.

### Key Features

1. **Personal Notifications** - Receive personal notifications for tasks you own
2. **Workspace Broadcasts** - Real-time updates for all workspace members when tasks are created, updated, completed, or deleted
3. **Focus Session Collaboration** - Real-time updates for collaborative focus sessions

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

This WebSocket provides real-time updates for tasks within a specific workspace. All workspace members receive broadcasts when tasks are created, updated, completed, or deleted within the workspace.

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
  "task_id": 456,
  "task_title": "New Task",
  "workspace_id": 789,
  "timestamp": "2025-03-23T22:45:00.000Z",
  "actor_id": 101
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

## Workspace Broadcasts

The system now supports real-time workspace-specific broadcasts for collaborative task management:

### How Workspace Broadcasts Work

1. **Automatic Broadcasting** - Any task created, updated, completed, or deleted within a workspace is automatically broadcast to all workspace members
2. **Actor Exclusion** - The user who performed the action doesn't receive the broadcast (to avoid duplicate notifications)
3. **Task Context** - Each broadcast message includes the task ID, title, action performed, workspace ID, timestamp, and the ID of the user who performed the action

### Implementation Details

- When connected to the workspace tasks WebSocket, you'll receive broadcasts about all task activities in the workspace
- This enables real-time task boards and collaborative workspaces where all members can see changes as they happen
- Broadcasts are sent in addition to personal notifications, allowing for both personal task management and collaborative workspace views

### Integration Example

```javascript
// Connect to workspace task updates WebSocket
const token = getAuthToken();
const workspaceId = 789; // Your workspace ID
const workspaceSocket = new WebSocket(`wss://your-domain.com/api/v1/ws/workspaces/${workspaceId}/tasks?token=${token}`);

// Handle connection open
workspaceSocket.onopen = (event) => {
  console.log(`Connected to workspace ${workspaceId} task updates`);
};

// Handle incoming task update broadcasts
workspaceSocket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === "task_update") {
    // Process task update based on action
    switch (message.action) {
      case "created":
        // Add new task to workspace board
        addTaskToBoard(message.task_id, message.task_title, message.workspace_id);
        break;
      case "updated":
        // Update existing task on workspace board
        updateTaskOnBoard(message.task_id, message.task_title);
        break;
      case "completed":
        // Move task to completed section
        markTaskAsCompleted(message.task_id);
        break;
      case "deleted":
        // Remove task from workspace board
        removeTaskFromBoard(message.task_id);
        break;
    }
    
    // Show a toast notification about the action
    showActivityToast(`Task "${message.task_title}" was ${message.action} by a team member`);
  }
};

// Implement reconnection logic for robust WebSocket connections
workspaceSocket.onclose = (event) => {
  console.log(`Disconnected from workspace ${workspaceId} updates`);
  setTimeout(() => connectToWorkspace(workspaceId), 5000);
};
```

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