from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class Notification(Base):
    """
    Notification model for user notifications.
    """
    # Basic notification info
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    
    # Notification type
    type = Column(
        Enum("task_reminder", "task_due", "system", "mention", "workspace", "other", name="notification_type"),
        default="other",
        nullable=False,
    )
    
    # Status
    read = Column(Boolean, default=False)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Related entity (e.g., task, workspace)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    data = Column(JSONB, nullable=True)


class NotificationSettings(Base):
    """
    User notification settings.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Channel preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    # Notification types
    task_reminders = Column(Boolean, default=True)
    task_due_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    
    # Custom preferences
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(Integer, nullable=True)  # Hours in 24h format
    quiet_hours_end = Column(Integer, nullable=True)  # Hours in 24h format
    
    # Custom settings
    settings = Column(JSONB, nullable=True)
