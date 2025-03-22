from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class Integration(Base):
    """
    Third-party integration model.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Integration service
    service = Column(
        Enum("google_calendar", "todoist", "github", "slack", "trello", "other", name="integration_service"),
        nullable=False,
    )
    
    # Authentication
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Configuration
    config = Column(JSONB, nullable=True)
    
    # Sync info
    last_sync = Column(DateTime(timezone=True), nullable=True)
    sync_frequency = Column(Integer, default=60)  # in minutes
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
