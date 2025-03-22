import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash


def test_create_user(client):
    """Test user creation."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data


def test_authenticate_user(client, db_session, test_user):
    """Test user authentication."""
    login_data = {
        "username": test_user.username,
        "password": "password123"
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_read_users_me(client, token_headers):
    """Test reading current user information."""
    response = client.get("/api/v1/users/me", headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_update_user(client, token_headers):
    """Test updating user information."""
    update_data = {
        "full_name": "Updated Name",
        "bio": "This is my updated profile bio"
    }
    
    response = client.patch("/api/v1/users/me", json=update_data, headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["bio"] == update_data["bio"]


def test_create_user_with_existing_email(client, test_user):
    """Test that creating a user with an existing email fails."""
    user_data = {
        "email": test_user.email,  # Use existing email
        "username": "uniqueuser",
        "password": "password123",
        "full_name": "Unique User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    

def test_create_user_with_existing_username(client, test_user):
    """Test that creating a user with an existing username fails."""
    user_data = {
        "email": "unique@example.com",
        "username": test_user.username,  # Use existing username
        "password": "password123",
        "full_name": "Unique User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400


def test_failed_authentication(client):
    """Test authentication with invalid credentials."""
    login_data = {
        "username": "nonexistentuser",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 401


def test_change_password(client, token_headers):
    """Test changing user password."""
    change_data = {
        "current_password": "password123",
        "new_password": "newpassword123"
    }
    
    response = client.post("/api/v1/users/me/change-password", 
                        json=change_data, 
                        headers=token_headers)
    assert response.status_code == 200
    
    # Try to login with the new password
    login_data = {
        "username": "testuser",
        "password": "newpassword123"
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200