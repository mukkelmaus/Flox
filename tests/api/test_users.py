"""
Tests for user endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.core.security import verify_password


def test_create_user(client: TestClient):
    """Test user creation."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Password123",
        "full_name": "New User"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned


def test_authenticate_user(client: TestClient, db_session: Session, test_user: models.User):
    """Test user authentication."""
    login_data = {
        "username": test_user.email,  # Can login with email
        "password": "password"  # From test_user fixture
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Check with username
    login_data = {
        "username": test_user.username,  # Can login with username too
        "password": "password"
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_read_users_me(client: TestClient, token_headers: dict):
    """Test reading current user information."""
    response = client.get("/api/v1/users/me", headers=token_headers)
    assert response.status_code == 200
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data
    assert "username" in user_data


def test_update_user(client: TestClient, token_headers: dict):
    """Test updating user information."""
    data = {"full_name": "Updated Name"}
    response = client.put("/api/v1/users/me", json=data, headers=token_headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["full_name"] == "Updated Name"


def test_create_user_with_existing_email(client: TestClient, test_user: models.User):
    """Test that creating a user with an existing email fails."""
    user_data = {
        "email": test_user.email,
        "username": "differentuser",
        "password": "password123"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"].lower()


def test_create_user_with_existing_username(client: TestClient, test_user: models.User):
    """Test that creating a user with an existing username fails."""
    user_data = {
        "email": "different@example.com",
        "username": test_user.username,
        "password": "password123"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "username already exists" in response.json()["detail"].lower()


def test_failed_authentication(client: TestClient):
    """Test authentication with invalid credentials."""
    # Non-existent user
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password"
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 401
    
    # Wrong password
    login_data = {
        "username": "test@example.com",  # From test_user fixture
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 401


def test_change_password(client: TestClient, token_headers: dict):
    """Test changing user password."""
    data = {
        "current_password": "password",
        "new_password": "newpassword123"
    }
    response = client.post("/api/v1/users/change-password", json=data, headers=token_headers)
    assert response.status_code == 200
    
    # Test login with new password
    user_data = response.json()
    login_data = {
        "username": user_data["email"],
        "password": "newpassword123"
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()