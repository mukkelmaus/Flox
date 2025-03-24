from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, validator, Field


# SubTask schema
class SubTaskBase(BaseModel):
    title: str
    is_completed: bool = False
    order: int = 0


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    order: Optional[int] = None


class SubTask(SubTaskBase):
    id: int
    task_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:  # Updated for Pydantic V2
        from_attributes = True


# TaskTag schema
class TaskTagBase(BaseModel):
    name: str
    color: str = "#007bff"


class TaskTagCreate(TaskTagBase):
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    is_system: bool = False


class TaskTagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TaskTag(TaskTagBase):
    id: int
    user_id: Optional[int] = None
    workspace_id: Optional[int] = None
    is_system: bool
    
    class Config:  # Updated for Pydantic V2
        from_attributes = True


# Task schema
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    ai_energy_level: Optional[str] = None
    context_tags: Optional[List[str]] = None
    attention_level_required: Optional[str] = None
    focus_mode_included: bool = True
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    workspace_id: Optional[int] = None
    parent_id: Optional[int] = None
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'Status must be one of: {", ".join(allowed)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high', 'urgent']
        if v not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v
    
    @validator('ai_energy_level')
    def validate_energy_level(cls, v):
        if v is not None:
            allowed = ['low', 'medium', 'high']
            if v not in allowed:
                raise ValueError(f'Energy level must be one of: {", ".join(allowed)}')
        return v
    
    @validator('attention_level_required')
    def validate_attention_level(cls, v):
        if v is not None:
            allowed = ['low', 'medium', 'high']
            if v not in allowed:
                raise ValueError(f'Attention level must be one of: {", ".join(allowed)}')
        return v


class TaskCreate(TaskBase):
    tags: Optional[List[Union[int, str]]] = None  # Can be tag IDs or new tag names
    subtasks: Optional[List[SubTaskCreate]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    ai_energy_level: Optional[str] = None
    context_tags: Optional[List[str]] = None
    attention_level_required: Optional[str] = None
    focus_mode_included: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    workspace_id: Optional[int] = None
    parent_id: Optional[int] = None
    tags: Optional[List[Union[int, str]]] = None


class Task(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    ai_priority_score: Optional[float] = None
    ai_complexity_score: Optional[float] = None
    ai_suggestions: Optional[Dict[str, Any]] = None
    actual_minutes: Optional[int] = None
    tags: List[TaskTag] = []
    
    class Config:  # Updated for Pydantic V2
        from_attributes = True


class TaskWithSubtasks(Task):
    subtasks: List[SubTask] = []


class TaskBreakdown(BaseModel):
    original_task: Task
    subtasks: List[Task]
    suggestions: Optional[str] = None


class TaskFocusMode(BaseModel):
    current_task: Optional[Task] = None
    next_tasks: List[Task]
    estimated_total_time: int
    context: Optional[str] = None
    energy_level: Optional[int] = None
