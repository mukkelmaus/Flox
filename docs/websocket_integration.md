# WebSocket Integration Guide

This document provides guidance for frontend developers to integrate with OneTask's WebSocket functionality for real-time updates.

## Overview

OneTask provides WebSocket endpoints for:
- Real-time notifications
- Task updates in a workspace
- Focus session collaboration
- Gamification events (achievements, streaks, level-ups)

## Connection URLs

### Notifications WebSocket

```
ws://<server-url>/ws/notifications?token=<access-token>
```

### Task Updates WebSocket (Workspace-specific)

```
ws://<server-url>/ws/tasks/<workspace_id>?token=<access-token>
```

### Focus Session WebSocket

```
ws://<server-url>/ws/focus/<session_id>?token=<access-token>
```

## Authentication

All WebSocket connections require authentication using a valid JWT token. Pass the token as a query parameter:

```javascript
const token = "your-jwt-token";
const socket = new WebSocket(`ws://server-url/ws/notifications?token=${token}`);
```

## Message Format

### Incoming Messages (From Server)

All messages are sent as JSON with the following structure:

```json
{
  "type": "message_type",
  "data": {
    // Message-specific data
  }
}
```

### Message Types and Data Structure

#### Notification Messages

```json
{
  "type": "notification",
  "notification_id": 123,
  "title": "Notification Title",
  "content": "Notification content",
  "notification_type": "task",
  "related_entity_type": "task",
  "related_entity_id": 456,
  "created_at": "2023-01-01T12:00:00",
  "data": {
    // Additional notification data
  }
}
```

#### Task Update Messages

```json
{
  "type": "task_update",
  "task_id": 123,
  "title": "Task Title",
  "action": "created|updated|completed|deleted",
  "workspace_id": 456,
  "actor_id": 789,
  "timestamp": "2023-01-01T12:00:00",
  "data": {
    // Additional task data
  }
}
```

#### Achievement Messages

```json
{
  "type": "achievement_unlocked",
  "notification_id": 123,
  "title": "Achievement Unlocked!",
  "content": "You've unlocked the 'Achievement Name' achievement and earned 50 points!",
  "notification_type": "achievement",
  "related_entity_type": "achievement",
  "related_entity_id": 456,
  "created_at": "2023-01-01T12:00:00",
  "data": {
    "achievement_id": 456,
    "achievement_name": "Achievement Name",
    "achievement_description": "Achievement description",
    "points": 50,
    "icon": "achievement_icon_name",
    "level": 1
  }
}
```

```json
{
  "type": "achievement_progress",
  "notification_id": 123,
  "title": "Achievement Progress",
  "content": "You're 50% of the way to unlocking 'Achievement Name'!",
  "notification_type": "achievement_progress",
  "related_entity_type": "achievement",
  "related_entity_id": 456,
  "created_at": "2023-01-01T12:00:00",
  "data": {
    "achievement_id": 456,
    "achievement_name": "Achievement Name",
    "progress": 0.5,
    "progress_percent": 50,
    "icon": "achievement_icon_name"
  }
}
```

#### Streak Messages

```json
{
  "type": "streak_update",
  "notification_id": 123,
  "title": "Streak Continued",
  "content": "You've maintained your streak for 5 consecutive days!",
  "notification_type": "streak",
  "created_at": "2023-01-01T12:00:00",
  "data": {
    "current_streak": 5,
    "is_milestone": false
  }
}
```

#### Level Up Messages

```json
{
  "type": "level_up",
  "notification_id": 123,
  "title": "Level Up!",
  "content": "Congratulations! You've reached level 5!",
  "notification_type": "level_up",
  "created_at": "2023-01-01T12:00:00",
  "data": {
    "new_level": 5
  }
}
```

## Handling Connection Errors and Reconnection

Frontend clients should implement reconnection logic to handle cases where the WebSocket connection is lost. Here's a simple example:

```javascript
function connect() {
  const token = "your-jwt-token";
  const socket = new WebSocket(`ws://server-url/ws/notifications?token=${token}`);
  
  socket.onopen = () => {
    console.log("WebSocket connection established");
  };
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle the message based on its type
    switch (data.type) {
      case "notification":
        handleNotification(data);
        break;
      case "task_update":
        handleTaskUpdate(data);
        break;
      case "achievement_unlocked":
        handleAchievementUnlocked(data);
        break;
      case "streak_update":
        handleStreakUpdate(data);
        break;
      case "level_up":
        handleLevelUp(data);
        break;
      // Handle other message types
    }
  };
  
  socket.onclose = () => {
    console.log("WebSocket connection closed. Reconnecting...");
    // Reconnect after a delay (e.g., 2 seconds)
    setTimeout(connect, 2000);
  };
  
  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    socket.close();
  };
}

// Start the connection
connect();
```

## Example: Displaying Gamification Notifications

Here's an example of how to display gamification notifications when received:

```javascript
function handleAchievementUnlocked(data) {
  // Display a toast or notification with achievement information
  showToast({
    title: data.title,
    message: data.content,
    icon: data.data.icon,
    type: "achievement"
  });
  
  // Update UI to reflect new points or level
  updateUserPoints(data.data.points);
  
  // Add the achievement to the user's achievement collection
  addToAchievementCollection(data.data.achievement_id);
}

function handleStreakUpdate(data) {
  // Display a streak notification
  showToast({
    title: data.title,
    message: data.content,
    type: "streak"
  });
  
  // Update streak display in UI
  updateStreakCounter(data.data.current_streak);
  
  // If it's a milestone, perhaps display a special animation
  if (data.data.is_milestone) {
    playStreakMilestoneAnimation();
  }
}

function handleLevelUp(data) {
  // Display a level up celebration
  showLevelUpAnimation(data.data.new_level);
  
  // Update level indicator in UI
  updateUserLevel(data.data.new_level);
  
  // Maybe play a sound
  playLevelUpSound();
}
```

## Common Issues and Troubleshooting

### Connection Failures

- Ensure the JWT token is valid and not expired
- Check that the WebSocket server URL is correct
- Verify you're using the correct WebSocket endpoint for your needs

### Message Handling Errors

- Always wrap message handlers in try/catch blocks to prevent errors from disrupting the connection
- Validate message data before processing
- Log unexpected message formats for debugging

## Further Help

For additional assistance or to report issues with the WebSocket API, please contact the backend development team or open an issue in the project repository.