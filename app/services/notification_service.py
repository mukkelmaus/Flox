"""
Notification service for the OneTask API.

This module handles creating, retrieving, and marking notifications as read.
It also provides functionality for scheduled reminders and notification
preference management.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.notification import Notification, NotificationSettings
from app.models.task import Task
from app.schemas.notification import NotificationCreate

# Configure logging
logger = logging.getLogger(__name__)


def get_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
) -> List[Notification]:
    """
    Get notifications for a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        unread_only: Whether to return only unread notifications
        
    Returns:
        List of notifications
    """
    query = db.query(Notification).filter(
        Notification.user_id == user_id
    )
    
    if unread_only:
        query = query.filter(Notification.read == False)
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def create_notification(
    db: Session,
    notification_in: NotificationCreate,
    user_id: int
) -> Notification:
    """
    Create a new notification.
    
    Args:
        db: Database session
        notification_in: Notification data
        user_id: User ID
        
    Returns:
        Created notification
    """
    # Check user notification settings
    settings = get_notification_settings(db, user_id)
    
    # Skip creation if notifications of this type are disabled
    if notification_in.type == "task_reminder" and not settings.task_reminders:
        logger.info(f"Skipping task reminder notification for user {user_id}, reminders disabled")
        return None
    
    if notification_in.type == "task_due" and not settings.task_due_notifications:
        logger.info(f"Skipping task due notification for user {user_id}, due notifications disabled")
        return None
    
    if notification_in.type == "system" and not settings.system_notifications:
        logger.info(f"Skipping system notification for user {user_id}, system notifications disabled")
        return None
    
    # Check quiet hours
    if settings.quiet_hours_enabled and settings.quiet_hours_start is not None and settings.quiet_hours_end is not None:
        current_hour = datetime.now().hour
        quiet_start = settings.quiet_hours_start
        quiet_end = settings.quiet_hours_end
        
        # Handle midnight crossing
        if quiet_start <= quiet_end:
            is_quiet_hours = quiet_start <= current_hour < quiet_end
        else:
            is_quiet_hours = current_hour >= quiet_start or current_hour < quiet_end
        
        if is_quiet_hours:
            logger.info(f"Skipping notification for user {user_id}, currently in quiet hours")
            return None
    
    # Create notification
    notification = Notification(
        title=notification_in.title,
        content=notification_in.content,
        type=notification_in.type,
        related_entity_type=notification_in.related_entity_type,
        related_entity_id=notification_in.related_entity_id,
        data=notification_in.data,
        user_id=user_id,
        read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    logger.info(f"Created notification for user {user_id}: {notification.title}")
    
    return notification


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> Notification:
    """
    Mark a notification as read.
    
    Args:
        db: Database session
        notification_id: Notification ID
        user_id: User ID
        
    Returns:
        Updated notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if notification and not notification.read:
        notification.read = True
        notification.read_at = datetime.now()
        db.add(notification)
        db.commit()
        db.refresh(notification)
    
    return notification


def mark_all_read(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Mark all notifications for a user as read.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Result with count of notifications marked read
    """
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).all()
    
    count = 0
    for notification in notifications:
        notification.read = True
        notification.read_at = datetime.now()
        db.add(notification)
        count += 1
    
    db.commit()
    
    return {"success": True, "count": count}


def get_notification_settings(db: Session, user_id: int) -> NotificationSettings:
    """
    Get a user's notification settings.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User's notification settings
    """
    settings = db.query(NotificationSettings).filter(
        NotificationSettings.user_id == user_id
    ).first()
    
    if not settings:
        # Create default settings
        settings = NotificationSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


def update_notification_settings(
    db: Session,
    settings: NotificationSettings,
    settings_in: Dict[str, Any]
) -> NotificationSettings:
    """
    Update a user's notification settings.
    
    Args:
        db: Database session
        settings: Notification settings to update
        settings_in: Updated settings data
        
    Returns:
        Updated notification settings
    """
    # Update fields
    for field, value in settings_in.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings


def create_due_reminders(db: Session) -> Dict[str, Any]:
    """
    Create reminders for tasks that are due soon.
    
    Args:
        db: Database session
        
    Returns:
        Result with counts of reminders created
    """
    now = datetime.now()
    
    # Find tasks due within the next 24 hours
    tomorrow = now + timedelta(hours=24)
    
    due_tasks = db.query(Task).filter(
        Task.due_date.between(now, tomorrow),
        Task.status != "done",
        Task.is_deleted == False
    ).all()
    
    # Create notifications for each task
    created_count = 0
    for task in due_tasks:
        # Check if a notification already exists for this task's due date
        existing = db.query(Notification).filter(
            Notification.user_id == task.user_id,
            Notification.type == "task_due",
            Notification.related_entity_type == "task",
            Notification.related_entity_id == task.id,
            Notification.data["due_reminder_sent"].astext.cast(bool) == True
        ).first()
        
        if existing:
            continue
        
        # Calculate time until due
        time_until_due = task.due_date - now
        hours_until_due = time_until_due.total_seconds() / 3600
        
        if hours_until_due <= 1:
            time_text = "in less than an hour"
        else:
            time_text = f"in about {int(hours_until_due)} hours"
        
        # Create notification
        notification_in = NotificationCreate(
            title=f"Task Due Soon: {task.title}",
            content=f"Your task '{task.title}' is due {time_text}.",
            type="task_due",
            related_entity_type="task",
            related_entity_id=task.id,
            data={"due_reminder_sent": True, "hours_until_due": hours_until_due}
        )
        
        notification = create_notification(db, notification_in, task.user_id)
        if notification:
            created_count += 1
    
    return {"success": True, "reminders_created": created_count}


def create_task_start_reminders(db: Session) -> Dict[str, Any]:
    """
    Create reminders for tasks that are scheduled to start soon.
    
    Args:
        db: Database session
        
    Returns:
        Result with counts of reminders created
    """
    now = datetime.now()
    
    # Find tasks scheduled to start within the next hour
    one_hour_later = now + timedelta(hours=1)
    
    upcoming_tasks = db.query(Task).filter(
        Task.start_date.between(now, one_hour_later),
        Task.status != "done",
        Task.is_deleted == False
    ).all()
    
    # Create notifications for each task
    created_count = 0
    for task in upcoming_tasks:
        # Check if a notification already exists for this task's start time
        existing = db.query(Notification).filter(
            Notification.user_id == task.user_id,
            Notification.type == "task_reminder",
            Notification.related_entity_type == "task",
            Notification.related_entity_id == task.id,
            Notification.data["start_reminder_sent"].astext.cast(bool) == True
        ).first()
        
        if existing:
            continue
        
        # Calculate time until start
        time_until_start = task.start_date - now
        minutes_until_start = time_until_start.total_seconds() / 60
        
        if minutes_until_start <= 15:
            time_text = "in less than 15 minutes"
        elif minutes_until_start <= 30:
            time_text = "in about 30 minutes"
        else:
            time_text = "in about an hour"
        
        # Create notification
        notification_in = NotificationCreate(
            title=f"Task Starting Soon: {task.title}",
            content=f"Your task '{task.title}' is scheduled to start {time_text}.",
            type="task_reminder",
            related_entity_type="task",
            related_entity_id=task.id,
            data={"start_reminder_sent": True, "minutes_until_start": minutes_until_start}
        )
        
        notification = create_notification(db, notification_in, task.user_id)
        if notification:
            created_count += 1
    
    return {"success": True, "reminders_created": created_count}