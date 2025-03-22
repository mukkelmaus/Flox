from typing import Optional, Dict, Any
from pydantic import BaseModel, validator


class AccessibilitySettingsBase(BaseModel):
    font_size: str = "medium"
    high_contrast: bool = False
    reduced_motion: bool = False
    screen_reader_optimized: bool = False
    keyboard_shortcuts_enabled: bool = True
    dyslexia_friendly_font: bool = False
    custom_settings: Optional[Dict[str, Any]] = None
    
    @validator('font_size')
    def validate_font_size(cls, v):
        allowed = ['small', 'medium', 'large', 'x-large']
        if v not in allowed:
            raise ValueError(f'Font size must be one of: {", ".join(allowed)}')
        return v


class AccessibilitySettingsUpdate(BaseModel):
    font_size: Optional[str] = None
    high_contrast: Optional[bool] = None
    reduced_motion: Optional[bool] = None
    screen_reader_optimized: Optional[bool] = None
    keyboard_shortcuts_enabled: Optional[bool] = None
    dyslexia_friendly_font: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None
    
    @validator('font_size')
    def validate_font_size(cls, v):
        if v is not None:
            allowed = ['small', 'medium', 'large', 'x-large']
            if v not in allowed:
                raise ValueError(f'Font size must be one of: {", ".join(allowed)}')
        return v


class AccessibilitySettings(AccessibilitySettingsBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True
