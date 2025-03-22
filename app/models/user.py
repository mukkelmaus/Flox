from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    """
    User model for authentication and user information.
    """
    __allow_unmapped__ = True  # Allow legacy-style column declarations without Mapped[]
    
    # Basic user info
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Theme preference
    active_theme_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Optional user profile fields
    profile_picture = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    time_zone = Column(String, nullable=True)
    language = Column(String, nullable=True)
