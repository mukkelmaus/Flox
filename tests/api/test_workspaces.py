import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.workspace import Workspace, WorkspaceMember


def create_test_workspace(db_session, owner_id, name="Test Workspace"):
    """Create a test workspace."""
    workspace = Workspace(
        name=name,
        description="Test workspace description",
        is_private=False,
        owner_id=owner_id,
    )
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)
    return workspace


def test_create_workspace(client, token_headers):
    """Test creating a workspace."""
    workspace_data = {
        "name": "New Workspace",
        "description": "A workspace for testing",
        "is_private": True,
    }
    
    response = client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=token_headers,
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == workspace_data["name"]
    assert data["description"] == workspace_data["description"]
    assert data["is_private"] == workspace_data["is_private"]


def test_read_workspaces(client, db_session, test_user, token_headers):
    """Test retrieving workspaces."""
    # Create a few workspaces
    for i in range(3):
        create_test_workspace(db_session, test_user.id, f"Workspace {i}")
    
    # Get workspaces
    response = client.get("/api/v1/workspaces/", headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all(workspace["owner_id"] == test_user.id for workspace in data)


def test_read_workspace(client, db_session, test_user, token_headers):
    """Test retrieving a specific workspace."""
    workspace = create_test_workspace(db_session, test_user.id)
    
    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers=token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == workspace.id
    assert data["name"] == workspace.name
    assert data["owner_id"] == test_user.id


def test_update_workspace(client, db_session, test_user, token_headers):
    """Test updating a workspace."""
    workspace = create_test_workspace(db_session, test_user.id)
    
    update_data = {
        "name": "Updated Workspace",
        "description": "Updated description",
    }
    
    response = client.patch(
        f"/api/v1/workspaces/{workspace.id}",
        json=update_data,
        headers=token_headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_workspace(client, db_session, test_user, token_headers):
    """Test deleting a workspace."""
    workspace = create_test_workspace(db_session, test_user.id)
    
    response = client.delete(f"/api/v1/workspaces/{workspace.id}", headers=token_headers)
    assert response.status_code == 204
    
    # Verify workspace is deleted
    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers=token_headers)
    assert response.status_code == 404


def test_add_workspace_member(client, db_session, test_user, test_superuser, token_headers):
    """Test adding a member to a workspace."""
    workspace = create_test_workspace(db_session, test_user.id)
    
    member_data = {
        "user_id": test_superuser.id,
        "role": "member",
    }
    
    response = client.post(
        f"/api/v1/workspaces/{workspace.id}/members",
        json=member_data,
        headers=token_headers,
    )
    assert response.status_code == 201
    
    # Verify member was added
    response = client.get(
        f"/api/v1/workspaces/{workspace.id}/members",
        headers=token_headers,
    )
    assert response.status_code == 200
    
    members = response.json()
    assert len(members) == 1
    assert members[0]["user_id"] == test_superuser.id
    assert members[0]["role"] == "member"


def test_remove_workspace_member(client, db_session, test_user, test_superuser, token_headers):
    """Test removing a member from a workspace."""
    workspace = create_test_workspace(db_session, test_user.id)
    
    # Add a member first
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=test_superuser.id,
        role="member",
    )
    db_session.add(member)
    db_session.commit()
    
    # Now remove the member
    response = client.delete(
        f"/api/v1/workspaces/{workspace.id}/members/{test_superuser.id}",
        headers=token_headers,
    )
    assert response.status_code == 204
    
    # Verify member was removed
    response = client.get(
        f"/api/v1/workspaces/{workspace.id}/members",
        headers=token_headers,
    )
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 0