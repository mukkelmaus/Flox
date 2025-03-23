"""
Real-time events API endpoints for the OneTask application.

These endpoints handle real-time event broadcasting and subscription management.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.websockets.notification_handlers import (
    send_task_notification,
    send_workspace_notification,
    send_system_notification,
)

router = APIRouter()


@router.post("/events/task", status_code=status.HTTP_202_ACCEPTED)
async def broadcast_task_event(
    task_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Broadcast a task-related event to relevant users.
    
    Args:
        task_data: Task data including task_id, title, action, workspace_id, and target_user_ids
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Status message
    """
    # Required fields
    if "task_id" not in task_data or "title" not in task_data or "action" not in task_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: task_id, title, action",
        )
    
    # Optional fields
    workspace_id = task_data.get("workspace_id")
    target_user_ids = task_data.get("target_user_ids", [])
    
    # If target_user_ids is empty, only notify the current user
    if not target_user_ids:
        target_user_ids = [current_user.id]
    
    # Send notifications to all target users
    for user_id in target_user_ids:
        await send_task_notification(
            db=db,
            user_id=user_id,
            task_id=task_data["task_id"],
            task_title=task_data["title"],
            action=task_data["action"],
            workspace_id=workspace_id,
            actor_id=current_user.id,
        )
    
    return {"status": "notifications sent", "recipient_count": len(target_user_ids)}


@router.post("/events/workspace", status_code=status.HTTP_202_ACCEPTED)
async def broadcast_workspace_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Broadcast a workspace-related event to all members.
    
    Args:
        event_data: Event data including workspace_id, title, content, type, etc.
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Status message
    """
    # Required fields
    if "workspace_id" not in event_data or "title" not in event_data or "content" not in event_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: workspace_id, title, content",
        )
    
    # Optional fields
    notification_type = event_data.get("type", "workspace")
    related_entity_type = event_data.get("related_entity_type")
    related_entity_id = event_data.get("related_entity_id")
    data = event_data.get("data", {})
    exclude_user_ids = event_data.get("exclude_user_ids", [])
    
    # Verify the user has access to the workspace
    from app.models.workspace import Workspace, WorkspaceMember
    workspace = db.query(Workspace).filter(Workspace.id == event_data["workspace_id"]).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    # Check if the user is the owner or a member
    is_owner = workspace.owner_id == current_user.id
    is_member = False
    
    if not is_owner:
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == event_data["workspace_id"],
            WorkspaceMember.user_id == current_user.id,
        ).first()
        is_member = member is not None
    
    if not is_owner and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )
    
    # Send notification to all workspace members
    await send_workspace_notification(
        db=db,
        workspace_id=event_data["workspace_id"],
        title=event_data["title"],
        content=event_data["content"],
        notification_type=notification_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        data=data,
        exclude_user_ids=exclude_user_ids,
    )
    
    return {"status": "workspace notification sent"}


@router.post("/events/system", status_code=status.HTTP_202_ACCEPTED)
async def send_system_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Send a system event notification to a user.
    
    Args:
        event_data: Event data including user_id, title, content, and data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Status message
    """
    # Required fields
    if "title" not in event_data or "content" not in event_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: title, content",
        )
    
    # Optional fields
    user_id = event_data.get("user_id", current_user.id)
    data = event_data.get("data", {})
    
    # Only admins can send system notifications to other users
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can send system notifications to other users",
        )
    
    # Send system notification
    await send_system_notification(
        db=db,
        user_id=user_id,
        title=event_data["title"],
        content=event_data["content"],
        data=data,
    )
    
    return {"status": "system notification sent"}