from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Workspace(Base):
    """
    Workspace model for team collaboration.
    """
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Workspace settings
    is_private = Column(Boolean, default=False)
    settings = Column(JSONB, nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    

class WorkspaceMember(Base):
    """
    WorkspaceMember model for managing workspace membership.
    """
    # Foreign keys
    workspace_id = Column(Integer, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Role within workspace
    role = Column(
        Enum("admin", "member", "guest", name="workspace_role"),
        default="member",
        nullable=False,
    )
    
    # Permissions (custom JSON object for fine-grained control)
    permissions = Column(JSONB, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")
