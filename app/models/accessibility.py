from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base_class import Base


class AccessibilitySettings(Base):
    """
    User accessibility settings.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Visual preferences
    font_size = Column(
        Enum("small", "medium", "large", "x-large", name="font_size"),
        default="medium",
        nullable=False,
    )
    high_contrast = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    
    # Screen reader
    screen_reader_optimized = Column(Boolean, default=False)
    
    # Keyboard
    keyboard_shortcuts_enabled = Column(Boolean, default=True)
    
    # Reading
    dyslexia_friendly_font = Column(Boolean, default=False)
    
    # Custom settings
    custom_settings = Column(JSONB, nullable=True)


class ADHDProfile(Base):
    """
    ADHD-specific user profile settings.
    """
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Focus mode settings
    focus_mode_duration = Column(Integer, default=25)  # in minutes
    break_duration = Column(Integer, default=5)  # in minutes
    
    # Task preferences
    task_chunking_enabled = Column(Boolean, default=True)
    visual_timers_enabled = Column(Boolean, default=True)
    
    # Motivation
    dopamine_boosts_enabled = Column(Boolean, default=True)
    
    # Distraction management
    distraction_blocking_level = Column(
        Enum("low", "medium", "high", name="distraction_level"),
        default="medium",
        nullable=False,
    )
    
    # Custom settings
    custom_settings = Column(JSONB, nullable=True)
