from typing import Optional
from pydantic import BaseModel, validator


class ThemeBase(BaseModel):
    name: str
    description: Optional[str] = None
    color_primary: str = "#007bff"
    color_secondary: str = "#6c757d"
    color_accent: str = "#fd7e14"
    color_background: str = "#f8f9fa"
    color_text: str = "#212529"
    font_family: str = "'Inter', system-ui, sans-serif"
    icon_set: str = "feather"
    
    @validator('color_primary', 'color_secondary', 'color_accent', 'color_background', 'color_text')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color code (e.g., #007bff)')
        return v


class ThemeCreate(ThemeBase):
    pass


class ThemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_accent: Optional[str] = None
    color_background: Optional[str] = None
    color_text: Optional[str] = None
    font_family: Optional[str] = None
    icon_set: Optional[str] = None
    
    @validator('color_primary', 'color_secondary', 'color_accent', 'color_background', 'color_text')
    def validate_color(cls, v):
        if v is not None and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex color code (e.g., #007bff)')
        return v


class Theme(ThemeBase):
    id: int
    user_id: Optional[int] = None
    is_system: bool
    
    class Config:
        orm_mode = True
