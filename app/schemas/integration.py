from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, validator


class IntegrationBase(BaseModel):
    service: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None
    sync_frequency: int = 60  # in minutes
    
    @validator('service')
    def validate_service(cls, v):
        allowed = ['google_calendar', 'todoist', 'github', 'slack', 'trello', 'other']
        if v not in allowed:
            raise ValueError(f'Service must be one of: {", ".join(allowed)}')
        return v


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    sync_frequency: Optional[int] = None


class Integration(IntegrationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    
    class Config:  # Updated for Pydantic V2
        from_attributes = True


class IntegrationSync(BaseModel):
    synced: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
