"""
Tests for third-party integration features.
"""

import pytest
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.user import User
from app.services.integration_service import (
    get_available_integrations,
    get_integration_auth_url,
    handle_oauth_callback,
    refresh_access_token,
    sync_with_google_calendar
)


def test_get_available_integrations():
    """Test getting available integrations."""
    integrations = get_available_integrations()
    
    # Check that we have expected integrations
    integration_ids = [i["id"] for i in integrations]
    assert "google_calendar" in integration_ids
    assert "todoist" in integration_ids
    assert "github" in integration_ids
    
    # Check that each integration has the required fields
    for integration in integrations:
        assert "id" in integration
        assert "name" in integration
        assert "description" in integration
        assert "auth_type" in integration
        assert "icon" in integration
        assert "enabled" in integration
        assert "scopes" in integration
        assert "setup_instructions" in integration


@pytest.mark.asyncio
async def test_get_integration_auth_url():
    """Test getting integration authorization URL."""
    # Test valid service
    auth_info = await get_integration_auth_url("google_calendar", 999)
    assert "auth_url" in auth_info
    assert "state" in auth_info
    assert "service" in auth_info
    assert auth_info["service"] == "google_calendar"
    assert "user_999_google_calendar_" in auth_info["state"]
    
    # Test invalid service
    with pytest.raises(HTTPException) as excinfo:
        await get_integration_auth_url("invalid_service", 999)
    assert excinfo.value.status_code == 400
    assert "not supported" in str(excinfo.value.detail).lower()


@pytest.mark.asyncio
async def test_handle_oauth_callback(db_session):
    """Test handling OAuth callback."""
    user_id = 999
    service = "google_calendar"
    code = "test_auth_code"
    state = f"user_{user_id}_{service}_{datetime.now().timestamp()}"
    
    # Test new integration
    result = await handle_oauth_callback(db_session, code, state, service, user_id)
    assert result["status"] == "success"
    assert service in result["message"]
    assert "integration_id" in result
    
    # Get the integration from database
    integration = db_session.query(Integration).filter(
        Integration.id == result["integration_id"]
    ).first()
    
    assert integration is not None
    assert integration.user_id == user_id
    assert integration.service == service
    assert integration.is_active is True
    
    # Test updating existing integration
    updated_result = await handle_oauth_callback(db_session, code, state, service, user_id)
    assert updated_result["status"] == "success"
    assert "updated" in updated_result["message"]
    assert updated_result["integration_id"] == integration.id


@pytest.mark.asyncio
async def test_refresh_access_token(db_session):
    """Test refreshing access token."""
    user_id = 999
    service = "google_calendar"
    
    # Create an integration with expired token
    integration = Integration(
        user_id=user_id,
        service=service,
        access_token="old_access_token",
        refresh_token="refresh_token",
        token_expiry=datetime.now() - timedelta(hours=1),
        is_active=True
    )
    db_session.add(integration)
    db_session.commit()
    
    # Refresh token
    success = await refresh_access_token(db_session, integration)
    assert success is True
    
    # Check that token was updated
    db_session.refresh(integration)
    assert integration.access_token != "old_access_token"
    assert integration.token_expiry > datetime.now()


@pytest.mark.asyncio
async def test_sync_with_google_calendar(db_session):
    """Test syncing with Google Calendar."""
    user_id = 999
    
    # Create a user
    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    
    # Create an integration
    integration = Integration(
        user_id=user_id,
        service="google_calendar",
        access_token="valid_access_token",
        refresh_token="refresh_token",
        token_expiry=datetime.now() + timedelta(hours=1),
        is_active=True,
        config={"calendar_ids": ["primary"]}
    )
    db_session.add(integration)
    db_session.commit()
    
    # Sync with Google Calendar
    result = await sync_with_google_calendar(db_session, integration, user)
    assert result["status"] == "success"
    assert "items_synced" in result
    assert "last_sync" in result
    
    # Check that last_sync was updated
    db_session.refresh(integration)
    assert integration.last_sync is not None
    
    # Test with expired token
    integration.token_expiry = datetime.now() - timedelta(hours=1)
    db_session.add(integration)
    db_session.commit()
    
    # Mock failing to refresh token
    old_refresh_token = refresh_access_token
    
    async def mock_refresh_token(*args, **kwargs):
        return False
    
    # Replace the function temporarily
    from app.services import integration_service
    integration_service.refresh_access_token = mock_refresh_token
    
    # Try syncing with expired token
    result = await sync_with_google_calendar(db_session, integration, user)
    assert result["status"] == "error"
    assert "token" in result["error"].lower()
    
    # Restore the original function
    integration_service.refresh_access_token = old_refresh_token