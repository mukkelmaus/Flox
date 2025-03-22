from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator


class NotificationBase(BaseModel):
    title: str
    content: Optional[str] = None
    type: str = "other"
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    
    @validator('type')
    def validate_type(cls, v):
        allowed = ['task_reminder', 'task_due', 'system', 'mention', 'workspace', 'other']
        if v not in allowed:
            raise ValueError(f'Type must be one of: {", ".join(allowed)}')
        return v


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class NotificationSettingsBase(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    task_reminders: bool = True
    task_due_notifications: bool = True
    system_notifications: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class NotificationSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    task_reminders: Optional[bool] = None
    task_due_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class NotificationSettings(NotificationSettingsBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True
