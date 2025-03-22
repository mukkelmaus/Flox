from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate,
    NotificationSettings,
    NotificationSettingsUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[Notification])
def read_notifications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    read: bool = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve user notifications.
    
    - **skip**: Number of notifications to skip (pagination)
    - **limit**: Maximum number of notifications to return
    - **read**: Filter by read status (true/false)
    """
    from app.models.notification import Notification as NotificationModel
    
    query = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id)
    
    if read is not None:
        query = query.filter(NotificationModel.read == read)
    
    notifications = query.order_by(NotificationModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications


@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
def create_notification(
    *,
    db: Session = Depends(get_db),
    notification_in: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a notification (typically used by the system, not users directly).
    
    - **title**: Notification title (required)
    - **content**: Notification content
    - **type**: Notification type (task_reminder, task_due, system, etc.)
    - **related_entity_id**: ID of the related entity (e.g., task ID)
    """
    from app.models.notification import Notification as NotificationModel
    
    # Create notification
    notification = NotificationModel(
        user_id=current_user.id,
        read=False,  # New notifications are unread by default
        **notification_in.dict(),
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.patch("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark a notification as read.
    
    - **notification_id**: Notification ID
    """
    from app.models.notification import Notification as NotificationModel
    
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id,
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    # Mark as read
    notification.read = True
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.patch("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark all user notifications as read.
    """
    from app.models.notification import Notification as NotificationModel
    
    # Get all unread notifications
    unread_notifications = db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.read == False,
    ).all()
    
    # Mark all as read
    for notification in unread_notifications:
        notification.read = True
        db.add(notification)
    
    db.commit()
    
    return {"message": f"Marked {len(unread_notifications)} notifications as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a notification.
    
    - **notification_id**: Notification ID
    """
    from app.models.notification import Notification as NotificationModel
    
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id,
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    # Delete notification
    db.delete(notification)
    db.commit()


@router.get("/settings", response_model=NotificationSettings)
def read_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's notification settings.
    """
    from app.models.notification import NotificationSettings as NotificationSettingsModel
    
    settings = db.query(NotificationSettingsModel).filter(
        NotificationSettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings if not found
        settings = NotificationSettingsModel(
            user_id=current_user.id,
            email_notifications=True,
            push_notifications=True,
            task_reminders=True,
            task_due_notifications=True,
            system_notifications=True,
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/settings", response_model=NotificationSettings)
def update_notification_settings(
    *,
    db: Session = Depends(get_db),
    settings_in: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update user's notification settings.
    
    - **email_notifications**: Enable/disable email notifications
    - **push_notifications**: Enable/disable push notifications
    - **task_reminders**: Enable/disable task reminder notifications
    - **task_due_notifications**: Enable/disable task due date notifications
    - **system_notifications**: Enable/disable system notifications
    """
    from app.models.notification import NotificationSettings as NotificationSettingsModel
    
    settings = db.query(NotificationSettingsModel).filter(
        NotificationSettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create settings if not found
        settings = NotificationSettingsModel(
            user_id=current_user.id,
            **settings_in.dict(),
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        return settings
    
    # Update settings fields
    settings_data = settings_in.dict(exclude_unset=True)
    for field, value in settings_data.items():
        setattr(settings, field, value)
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings
