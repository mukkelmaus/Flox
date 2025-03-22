from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator


# WorkspaceMember schema
class WorkspaceMemberBase(BaseModel):
    role: str = "member"
    
    @validator('role')
    def validate_role(cls, v):
        allowed = ['admin', 'member', 'guest']
        if v not in allowed:
            raise ValueError(f'Role must be one of: {", ".join(allowed)}')
        return v


class WorkspaceMemberCreate(WorkspaceMemberBase):
    user_id: int


class WorkspaceMemberUpdate(BaseModel):
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        allowed = ['admin', 'member', 'guest']
        if v not in allowed:
            raise ValueError(f'Role must be one of: {", ".join(allowed)}')
        return v


class WorkspaceMember(WorkspaceMemberBase):
    workspace_id: int
    user_id: int
    joined_at: datetime
    last_active_at: Optional[datetime] = None
    permissions: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True


class WorkspaceMemberResponse(BaseModel):
    workspace_id: int
    user_id: int
    role: str
    username: str
    email: str
    full_name: Optional[str] = None


# Workspace schema
class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    settings: Optional[Dict[str, Any]] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class Workspace(WorkspaceBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class WorkspaceWithMembers(Workspace):
    members: List[WorkspaceMember] = []
