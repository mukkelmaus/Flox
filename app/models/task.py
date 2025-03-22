from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Table, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


# Association table for many-to-many relationship between Tasks and TaskTags
task_tags = Table(
    "task_tag_association",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("task_tag.id", ondelete="CASCADE"), primary_key=True),
)


class Task(Base):
    """
    Task model for storing task information.
    """
    # Basic task info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum("todo", "in_progress", "done", name="task_status"),
        default="todo",
        nullable=False,
    )
    priority = Column(
        Enum("low", "medium", "high", "urgent", name="task_priority"),
        default="medium",
        nullable=False,
    )
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Time estimations
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)
    
    # AI fields
    ai_priority_score = Column(Float, nullable=True)
    ai_complexity_score = Column(Float, nullable=True)
    ai_energy_level = Column(
        Enum("low", "medium", "high", name="energy_level"),
        nullable=True,
    )
    ai_suggestions = Column(JSONB, nullable=True)
    
    # Parent-child relationship for subtasks
    parent_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=True)
    children = relationship("Task", 
                           cascade="all, delete-orphan",
                           backref="parent",
                           remote_side="Task.id",
                           lazy="joined")
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspace.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSONB, nullable=True)
    
    # Context fields for neurodivergent-friendly features
    context_tags = Column(ARRAY(String), nullable=True)
    focus_mode_included = Column(Boolean, default=True)
    attention_level_required = Column(
        Enum("low", "medium", "high", name="attention_level"),
        nullable=True,
    )
    
    # Custom metadata for flexibility
    custom_metadata = Column(JSONB, nullable=True)
    
    # Relationships
    tags = relationship("TaskTag", secondary=task_tags, back_populates="tasks")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    

class SubTask(Base):
    """
    SubTask model for smaller components of a task.
    """
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship
    task = relationship("Task", back_populates="subtasks")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class TaskTag(Base):
    """
    TaskTag model for categorizing tasks.
    """
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), default="#007bff")  # Hex color code
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=True)
    is_system = Column(Boolean, default=False)
    
    # Relationships
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
