import re
from typing import Any, ClassVar, Dict

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.
    
    Provides:
    - Automatic __tablename__ generation
    - Primary key id column
    """
    
    # Remove problematic type annotation for id
    __name__: ClassVar[str]
    __allow_unmapped__ = True  # Allow legacy-style column declarations without Mapped[]
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Convert CamelCase class name to snake_case table name.
        
        Example:
            UserProfile -> user_profile
        """
        # Convert CamelCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name
    
    # Common primary key for all models
    id = Column(Integer, primary_key=True, index=True)
