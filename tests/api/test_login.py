"""
Tests for login endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.core.security import get_password_hash


def test_login_access_token(client: TestClient, db_session: Session, test_user: models.User):
    """Test login and token generation."""
    login_data = {
        "username": test_user.email,
        "password": "password",  # This matches the test_user fixture
    }
    r = client.post("/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_login_access_token_with_username(client: TestClient, db_session: Session, test_user: models.User):
    """Test login with username instead of email."""
    login_data = {
        "username": test_user.username,
        "password": "password",  # This matches the test_user fixture
    }
    r = client.post("/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_login_access_token_with_wrong_password(client: TestClient, db_session: Session, test_user: models.User):
    """Test login with wrong password."""
    login_data = {
        "username": test_user.email,
        "password": "wrong-password",
    }
    r = client.post("/login/access-token", data=login_data)
    assert r.status_code == 401
    assert "Incorrect username or password" in r.json()["detail"]


def test_login_access_token_with_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password",
    }
    r = client.post("/login/access-token", data=login_data)
    assert r.status_code == 401
    assert "Incorrect username or password" in r.json()["detail"]


def test_login_access_token_with_inactive_user(client: TestClient, db_session: Session):
    """Test login with inactive user."""
    # Create inactive user
    inactive_user = models.User(
        email="inactive@example.com",
        username="inactive",
        password_hash=get_password_hash("password"),
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    login_data = {
        "username": "inactive@example.com",
        "password": "password",
    }
    r = client.post("/login/access-token", data=login_data)
    assert r.status_code == 401
    assert "Inactive user" in r.json()["detail"]


def test_test_token(client: TestClient, token_headers: dict):
    """Test the token test endpoint."""
    r = client.post("/login/test-token", headers=token_headers)
    assert r.status_code == 200
    user = r.json()
    assert "id" in user
    assert "email" in user
    assert "username" in user


def test_test_token_without_token(client: TestClient):
    """Test the token test endpoint without a token."""
    r = client.post("/login/test-token")
    assert r.status_code == 401
    assert "Not authenticated" in r.json()["detail"]