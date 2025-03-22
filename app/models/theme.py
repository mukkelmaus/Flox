from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Theme(Base):
    """
    Theme model for UI customization.
    """
    # Basic theme info
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Color scheme
    color_primary = Column(String(7), default="#007bff")  # Hex color code
    color_secondary = Column(String(7), default="#6c757d")
    color_accent = Column(String(7), default="#fd7e14")
    color_background = Column(String(7), default="#f8f9fa")
    color_text = Column(String(7), default="#212529")
    
    # Typography
    font_family = Column(String(100), default="'Inter', system-ui, sans-serif")
    
    # Icon set
    icon_set = Column(String(50), default="feather")
    
    # Ownership
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    is_system = Column(Boolean, default=False)
    
    # Additional theme properties can be added as needed
