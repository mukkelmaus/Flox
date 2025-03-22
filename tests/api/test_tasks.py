import pytest
from datetime import datetime, timedelta
from typing import Dict

from app.models.task import Task


def create_test_task(db_session, user_id, title="Test Task"):
    """Create a test task."""
    task = Task(
        title=title,
        description="Test task description",
        status="todo",
        priority="medium",
        user_id=user_id,
        due_date=datetime.utcnow() + timedelta(days=1),
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


def test_read_tasks(client, db_session, test_user, token_headers):
    """Test retrieving tasks."""
    # Create a few tasks
    for i in range(3):
        create_test_task(db_session, test_user.id, f"Test Task {i}")
    
    # Get tasks
    response = client.get("/api/v1/tasks/", headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all(task["user_id"] == test_user.id for task in data)


def test_create_task(client, token_headers):
    """Test creating a task."""
    task_data = {
        "title": "New Task",
        "description": "New task description",
        "status": "todo",
        "priority": "high",
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
    }
    
    response = client.post("/api/v1/tasks/", json=task_data, headers=token_headers)
    assert response.status_code == 201
    
    created_task = response.json()
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] == task_data["description"]
    assert created_task["priority"] == task_data["priority"]


def test_read_task(client, db_session, test_user, token_headers):
    """Test retrieving a specific task."""
    task = create_test_task(db_session, test_user.id)
    
    response = client.get(f"/api/v1/tasks/{task.id}", headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task.title
    assert data["user_id"] == test_user.id


def test_update_task(client, db_session, test_user, token_headers):
    """Test updating a task."""
    task = create_test_task(db_session, test_user.id)
    
    update_data = {
        "title": "Updated Task",
        "status": "in_progress",
    }
    
    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json=update_data,
        headers=token_headers,
    )
    assert response.status_code == 200
    
    updated_task = response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["description"] == task.description  # Should not change


def test_delete_task(client, db_session, test_user, token_headers):
    """Test deleting a task."""
    task = create_test_task(db_session, test_user.id)
    
    response = client.delete(f"/api/v1/tasks/{task.id}", headers=token_headers)
    assert response.status_code == 204
    
    # Verify task is deleted or soft-deleted
    response = client.get(f"/api/v1/tasks/{task.id}", headers=token_headers)
    assert response.status_code == 404


def test_cannot_access_other_users_tasks(client, db_session, test_user, test_superuser, token_headers, superuser_token_headers):
    """Test that a user cannot access another user's tasks."""
    # Create a task for the superuser
    task = create_test_task(db_session, test_superuser.id, "Superuser Task")
    
    # Regular user should not be able to access it
    response = client.get(f"/api/v1/tasks/{task.id}", headers=token_headers)
    assert response.status_code == 404
    
    # But the superuser can access tasks created by the regular user
    regular_user_task = create_test_task(db_session, test_user.id, "Regular User Task")
    response = client.get(f"/api/v1/tasks/{regular_user_task.id}", headers=superuser_token_headers)
    assert response.status_code == 200