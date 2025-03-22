from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class SupportTicket(Base):
    """
    Support ticket model for customer support.
    """
    # Basic ticket info
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Status and category
    status = Column(
        Enum("open", "in_progress", "resolved", "closed", name="ticket_status"),
        default="open",
        nullable=False,
    )
    priority = Column(
        Enum("low", "medium", "high", "urgent", name="ticket_priority"),
        default="medium",
        nullable=False,
    )
    category = Column(
        Enum("bug", "feature_request", "question", "other", name="ticket_category"),
        default="other",
        nullable=False,
    )
    
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Admin fields
    assigned_to = Column(Integer, ForeignKey("user.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
