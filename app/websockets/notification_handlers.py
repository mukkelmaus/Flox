"""
Notification handlers for WebSocket real-time features.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification
from app.websockets.connection_manager import manager


async def send_task_notification(
    db: Session,
    user_id: int,
    task_id: int,
    task_title: str,
    action: str,
    workspace_id: Optional[int] = None,
    actor_id: Optional[int] = None,
):
    """
    Send a task-related notification.
    
    Args:
        db: Database session
        user_id: User ID to notify
        task_id: Task ID
        task_title: Task title
        action: Action performed (created, updated, completed, etc.)
        workspace_id: Optional workspace ID
        actor_id: Optional ID of the user who performed the action
    """
    # Create notification in the database
    notification_data = NotificationCreate(
        title=f"Task {action}",
        content=f"Task '{task_title}' was {action}.",
        type="task",
        related_entity_type="task",
        related_entity_id=task_id,
        data={
            "task_id": task_id,
            "action": action,
            "workspace_id": workspace_id,
            "actor_id": actor_id
        }
    )
    
    notification = create_notification(db, notification_data, user_id)
    
    # Send real-time notification via WebSocket
    await manager.send_personal_message(
        {
            "type": "notification",
            "notification_id": notification.id,
            "title": notification.title,
            "content": notification.content,
            "notification_type": notification.type,
            "related_entity_type": notification.related_entity_type,
            "related_entity_id": notification.related_entity_id,
            "created_at": notification.created_at.isoformat(),
            "data": notification.data
        },
        user_id
    )


async def send_workspace_notification(
    db: Session,
    workspace_id: int,
    title: str,
    content: str,
    notification_type: str = "workspace",
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    data: Optional[Dict[str, Any]] = None,
    exclude_user_ids: Optional[List[int]] = None,
):
    """
    Send a notification to all members of a workspace.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        title: Notification title
        content: Notification content
        notification_type: Notification type
        related_entity_type: Optional related entity type
        related_entity_id: Optional related entity ID
        data: Optional additional data
        exclude_user_ids: Optional list of user IDs to exclude
    """
    from app.models.workspace import WorkspaceMember, Workspace
    
    exclude_user_ids = exclude_user_ids or []
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return
    
    # Get workspace owner and members
    owner_id = workspace.owner_id
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()
    
    user_ids = [owner_id] + [member.user_id for member in members]
    
    # Remove excluded users
    user_ids = [user_id for user_id in user_ids if user_id not in exclude_user_ids]
    
    # Create and send notifications to all members
    for user_id in user_ids:
        notification_data = NotificationCreate(
            title=title,
            content=content,
            type=notification_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            data=data or {}
        )
        
        notification = create_notification(db, notification_data, user_id)
        
        # Send real-time notification via WebSocket
        await manager.send_personal_message(
            {
                "type": "notification",
                "notification_id": notification.id,
                "title": notification.title,
                "content": notification.content,
                "notification_type": notification.type,
                "related_entity_type": notification.related_entity_type,
                "related_entity_id": notification.related_entity_id,
                "created_at": notification.created_at.isoformat(),
                "data": notification.data
            },
            user_id
        )


async def send_system_notification(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    data: Optional[Dict[str, Any]] = None,
):
    """
    Send a system notification to a user.
    
    Args:
        db: Database session
        user_id: User ID
        title: Notification title
        content: Notification content
        data: Optional additional data
    """
    notification_data = NotificationCreate(
        title=title,
        content=content,
        type="system",
        data=data or {}
    )
    
    notification = create_notification(db, notification_data, user_id)
    
    # Send real-time notification via WebSocket
    await manager.send_personal_message(
        {
            "type": "notification",
            "notification_id": notification.id,
            "title": notification.title,
            "content": notification.content,
            "notification_type": notification.type,
            "created_at": notification.created_at.isoformat(),
            "data": notification.data
        },
        user_id
    )