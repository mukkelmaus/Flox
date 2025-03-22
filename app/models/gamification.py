from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class Achievement(Base):
    """
    Achievement model for gamification.
    """
    # Basic info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Achievement details
    points = Column(Integer, default=0)
    icon = Column(String, nullable=True)
    
    # Requirements to unlock
    requirement_type = Column(String(50), nullable=False)  # e.g., "task_count", "streak"
    requirement_value = Column(Integer, nullable=False)  # e.g., 10 tasks, 7-day streak
    
    # Achievement level
    level = Column(Integer, default=1)  # For tiered achievements (bronze, silver, gold)
    
    # System achievement or custom
    is_system = Column(Boolean, default=True)
    workspace_id = Column(Integer, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserAchievement(Base):
    """
    User achievement tracking.
    """
    # Relationships
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievement.id", ondelete="CASCADE"), nullable=False)
    
    # Status
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(Float, default=0.0)  # For partially completed achievements
    
    # Additional data
    data = Column(JSONB, nullable=True)


class UserStats(Base):
    """
    User statistics for gamification.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Stats
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    # Task-related stats
    tasks_completed = Column(Integer, default=0)
    tasks_completed_on_time = Column(Integer, default=0)
    
    # Streak stats
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Efficiency stats
    average_task_completion_time = Column(Float, nullable=True)
    focus_time_minutes = Column(Integer, default=0)
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())


class UserStreak(Base):
    """
    User streak tracking.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Streak info
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Streak details
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    streak_start_date = Column(DateTime(timezone=True), nullable=True)
    
    # Last update
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
