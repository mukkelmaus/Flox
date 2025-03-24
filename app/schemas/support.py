from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator


class SupportTicketBase(BaseModel):
    subject: str
    description: str
    priority: str = "medium"
    category: str = "other"
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high', 'urgent']
        if v not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        allowed = ['bug', 'feature_request', 'question', 'other']
        if v not in allowed:
            raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed = ['low', 'medium', 'high', 'urgent']
            if v not in allowed:
                raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            allowed = ['bug', 'feature_request', 'question', 'other']
            if v not in allowed:
                raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed = ['open', 'in_progress', 'resolved', 'closed']
            if v not in allowed:
                raise ValueError(f'Status must be one of: {", ".join(allowed)}')
        return v


class SupportTicket(SupportTicketBase):
    id: int
    user_id: int
    status: str
    assigned_to: Optional[int] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:  # Updated for Pydantic V2
        from_attributes = True
