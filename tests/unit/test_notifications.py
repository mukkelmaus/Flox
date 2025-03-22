"""
Tests for notification features.
"""

import pytest
from datetime import datetime, timedelta

from app.models.notification import Notification, NotificationSettings
from app.schemas.notification import NotificationCreate
from app.services.notification_service import (
    get_notifications,
    create_notification,
    mark_notification_read,
    mark_all_read,
    get_notification_settings,
    update_notification_settings
)


def test_get_notifications(db_session):
    """Test getting notifications."""
    # Create test notifications
    user_id = 999
    
    notifications = [
        Notification(
            title="Test Notification 1",
            content="This is a test notification",
            type="system",
            user_id=user_id,
            read=False,
            created_at=datetime.now() - timedelta(hours=2)
        ),
        Notification(
            title="Test Notification 2",
            content="This is another test notification",
            type="task_reminder",
            user_id=user_id,
            read=True,
            created_at=datetime.now() - timedelta(hours=1),
            read_at=datetime.now() - timedelta(minutes=30)
        ),
        Notification(
            title="Test Notification 3",
            content="This is a third test notification",
            type="task_due",
            user_id=user_id,
            read=False,
            created_at=datetime.now()
        )
    ]
    
    for notification in notifications:
        db_session.add(notification)
    db_session.commit()
    
    # Test getting all notifications
    all_notifications = get_notifications(db_session, user_id)
    assert len(all_notifications) == 3
    assert all_notifications[0].title == "Test Notification 3"  # Most recent first
    
    # Test getting only unread notifications
    unread_notifications = get_notifications(db_session, user_id, unread_only=True)
    assert len(unread_notifications) == 2
    
    # Test pagination
    paginated_notifications = get_notifications(db_session, user_id, skip=1, limit=1)
    assert len(paginated_notifications) == 1
    assert paginated_notifications[0].title == "Test Notification 2"


def test_create_notification(db_session):
    """Test creating a notification."""
    user_id = 999
    
    # Create default notification settings
    settings = NotificationSettings(user_id=user_id)
    db_session.add(settings)
    db_session.commit()
    
    # Create a notification
    notification_in = NotificationCreate(
        title="New Notification",
        content="This is a new notification",
        type="system"
    )
    
    notification = create_notification(db_session, notification_in, user_id)
    assert notification is not None
    assert notification.title == "New Notification"
    assert notification.content == "This is a new notification"
    assert notification.user_id == user_id
    assert notification.read is False
    
    # Test notification with disabled type
    settings.system_notifications = False
    db_session.add(settings)
    db_session.commit()
    
    notification = create_notification(db_session, notification_in, user_id)
    assert notification is None


def test_mark_notification_read(db_session):
    """Test marking a notification as read."""
    user_id = 999
    
    # Create a test notification
    notification = Notification(
        title="Test Notification",
        content="This is a test notification",
        type="system",
        user_id=user_id,
        read=False
    )
    db_session.add(notification)
    db_session.commit()
    
    # Mark notification as read
    updated_notification = mark_notification_read(db_session, notification.id, user_id)
    assert updated_notification.read is True
    assert updated_notification.read_at is not None
    
    # Try to mark it as read again (should return the notification but not change it)
    read_at = updated_notification.read_at
    updated_notification = mark_notification_read(db_session, notification.id, user_id)
    assert updated_notification.read is True
    assert updated_notification.read_at == read_at


def test_mark_all_read(db_session):
    """Test marking all notifications as read."""
    user_id = 999
    
    # Create test notifications
    notifications = [
        Notification(
            title="Test Notification 1",
            content="This is a test notification",
            type="system",
            user_id=user_id,
            read=False
        ),
        Notification(
            title="Test Notification 2",
            content="This is another test notification",
            type="task_reminder",
            user_id=user_id,
            read=False
        )
    ]
    
    for notification in notifications:
        db_session.add(notification)
    db_session.commit()
    
    # Mark all notifications as read
    result = mark_all_read(db_session, user_id)
    assert result["success"] is True
    assert result["count"] == 2
    
    # Check that all notifications are read
    unread_notifications = get_notifications(db_session, user_id, unread_only=True)
    assert len(unread_notifications) == 0


def test_get_notification_settings(db_session):
    """Test getting notification settings."""
    user_id = 999
    
    # Test with a user that doesn't have settings yet
    settings = get_notification_settings(db_session, user_id)
    assert settings is not None
    assert settings.user_id == user_id
    assert settings.email_notifications is True
    assert settings.push_notifications is True
    assert settings.task_reminders is True
    
    # Test with existing settings
    existing_settings = NotificationSettings(
        user_id=1000,
        email_notifications=False,
        push_notifications=True,
        task_reminders=False,
        quiet_hours_enabled=True,
        quiet_hours_start=22,  # 10 PM
        quiet_hours_end=7  # 7 AM
    )
    db_session.add(existing_settings)
    db_session.commit()
    
    retrieved_settings = get_notification_settings(db_session, 1000)
    assert retrieved_settings is not None
    assert retrieved_settings.user_id == 1000
    assert retrieved_settings.email_notifications is False
    assert retrieved_settings.push_notifications is True
    assert retrieved_settings.task_reminders is False
    assert retrieved_settings.quiet_hours_enabled is True
    assert retrieved_settings.quiet_hours_start == 22
    assert retrieved_settings.quiet_hours_end == 7


def test_update_notification_settings(db_session):
    """Test updating notification settings."""
    user_id = 999
    
    # Get default settings
    settings = get_notification_settings(db_session, user_id)
    
    # Update settings
    updated_settings = update_notification_settings(
        db_session,
        settings,
        {
            "email_notifications": False,
            "push_notifications": False,
            "quiet_hours_enabled": True,
            "quiet_hours_start": 23,
            "quiet_hours_end": 8
        }
    )
    
    assert updated_settings.email_notifications is False
    assert updated_settings.push_notifications is False
    assert updated_settings.quiet_hours_enabled is True
    assert updated_settings.quiet_hours_start == 23
    assert updated_settings.quiet_hours_end == 8
    
    # Check that task_reminders wasn't changed
    assert updated_settings.task_reminders is True