import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models.integration import Integration


def create_test_integration(db_session, user_id, service="google_calendar"):
    """Create a test integration."""
    expiry = datetime.utcnow() + timedelta(days=30)
    integration = Integration(
        user_id=user_id,
        service=service,
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expiry=expiry,
        is_active=True,
        config={"sync_options": {"calendars": ["primary"]}}
    )
    db_session.add(integration)
    db_session.commit()
    db_session.refresh(integration)
    return integration


def test_read_available_integrations(client, token_headers):
    """Test retrieving available integrations."""
    response = client.get(
        "/api/v1/integrations/available",
        headers=token_headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Check for some expected integrations
    services = [item["service"] for item in data]
    assert "google_calendar" in services
    assert "todoist" in services
    assert "github" in services


def test_read_user_integrations(client, db_session, test_user, token_headers):
    """Test retrieving user's integrations."""
    # Create a few integrations
    create_test_integration(db_session, test_user.id, "google_calendar")
    create_test_integration(db_session, test_user.id, "todoist")
    
    response = client.get(
        "/api/v1/integrations/",
        headers=token_headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(integration["user_id"] == test_user.id for integration in data)
    
    # Check that we have one of each service
    services = [integration["service"] for integration in data]
    assert "google_calendar" in services
    assert "todoist" in services


def test_create_integration(client, token_headers):
    """Test creating an integration."""
    integration_data = {
        "service": "github",
        "access_token": "github_access_token",
        "refresh_token": "github_refresh_token",
        "token_expiry": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "config": {"repo_owner": "testuser", "repos": ["testrepo"]}
    }
    
    response = client.post(
        "/api/v1/integrations/",
        json=integration_data,
        headers=token_headers,
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["service"] == integration_data["service"]
    assert data["access_token"] == integration_data["access_token"]
    assert "id" in data
    assert "user_id" in data


def test_update_integration(client, db_session, test_user, token_headers):
    """Test updating an integration."""
    integration = create_test_integration(db_session, test_user.id)
    
    update_data = {
        "access_token": "updated_access_token",
        "config": {"sync_options": {"calendars": ["primary", "work"]}}
    }
    
    response = client.patch(
        f"/api/v1/integrations/{integration.id}",
        json=update_data,
        headers=token_headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["access_token"] == update_data["access_token"]
    assert data["config"] == update_data["config"]


def test_delete_integration(client, db_session, test_user, token_headers):
    """Test deleting an integration."""
    integration = create_test_integration(db_session, test_user.id)
    
    response = client.delete(
        f"/api/v1/integrations/{integration.id}",
        headers=token_headers,
    )
    assert response.status_code == 204
    
    # Verify integration is deleted
    response = client.get(
        f"/api/v1/integrations/{integration.id}",
        headers=token_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_sync_integration(client, db_session, test_user, token_headers):
    """Test syncing an integration."""
    integration = create_test_integration(db_session, test_user.id, "google_calendar")
    
    # Mock the sync function to avoid actual API calls
    with patch("app.api.api_v1.endpoints.integrations.sync_with_google_calendar") as mock_sync:
        # Create a mock return value
        mock_return = {
            "synced": [
                {"id": "task1", "title": "Task from Calendar", "type": "event"}
            ],
            "failed": []
        }
        mock_sync.return_value = mock_return
        
        # Make the request
        response = await client.post(
            f"/api/v1/integrations/{integration.id}/sync",
            headers=token_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "synced" in data
        assert len(data["synced"]) > 0