from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskFocusMode,
    TaskWithSubtasks,
)
from app.services.task_service import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
    prioritize_tasks,
    get_focus_mode_tasks,
    mark_task_completed,
    get_task_history,
)

router = APIRouter()


@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    
    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return
    - **workspace_id**: Filter by workspace ID
    - **status**: Filter by status (todo, in_progress, done)
    - **priority**: Filter by priority (low, medium, high, urgent)
    """
    tasks = get_tasks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        workspace_id=workspace_id,
        status=status,
        priority=priority,
    )
    return tasks


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_new_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new task.
    
    - **title**: Task title (required)
    - **description**: Detailed description
    - **due_date**: Due date (ISO format)
    - **priority**: Priority level (low, medium, high, urgent)
    - **status**: Task status (todo, in_progress, done)
    - **tags**: List of tags
    - **workspace_id**: Workspace ID
    """
    task = create_task(db=db, task_in=task_in, user_id=current_user.id)
    return task


@router.get("/prioritize", response_model=List[Task])
def get_prioritized_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get automatically prioritized tasks based on various factors.
    
    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return
    - **workspace_id**: Filter by workspace ID
    """
    tasks = prioritize_tasks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        workspace_id=workspace_id,
    )
    return tasks


@router.get("/focus", response_model=TaskFocusMode)
def get_focus_mode(
    db: Session = Depends(get_db),
    context: Optional[str] = Query(None, description="Current work context"),
    time_available: Optional[int] = Query(None, description="Time available in minutes"),
    energy_level: Optional[int] = Query(None, description="Energy level (1-5)"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get focus mode tasks based on context, time available, and energy level.
    
    - **context**: Current work context (e.g., "work", "personal", "study")
    - **time_available**: Time available in minutes
    - **energy_level**: Current energy level (1-5)
    """
    focus_tasks = get_focus_mode_tasks(
        db=db,
        user_id=current_user.id,
        context=context,
        time_available=time_available,
        energy_level=energy_level,
    )
    return focus_tasks


@router.get("/history", response_model=List[Task])
def read_task_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve completed task history.
    
    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return
    - **start_date**: Start date (ISO format)
    - **end_date**: End date (ISO format)
    """
    tasks = get_task_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    return tasks


@router.get("/{task_id}", response_model=TaskWithSubtasks)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get task by ID.
    
    - **task_id**: Task ID
    """
    task = get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=Task)
def update_task_endpoint(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a task.
    
    - **task_id**: Task ID
    - **title**: Task title
    - **description**: Detailed description
    - **due_date**: Due date (ISO format)
    - **priority**: Priority level (low, medium, high, urgent)
    - **status**: Task status (todo, in_progress, done)
    - **tags**: List of tags
    """
    task = get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    updated_task = update_task(db=db, task=task, task_in=task_in)
    return updated_task


@router.patch("/{task_id}/complete", response_model=Task)
def mark_task_as_completed(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark a task as completed.
    
    - **task_id**: Task ID
    """
    task = get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    completed_task = mark_task_completed(db=db, task=task)
    return completed_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_task_endpoint(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a task.
    
    - **task_id**: Task ID
    """
    task = get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    delete_task(db=db, task_id=task_id)
