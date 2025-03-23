"""
Task management endpoints for the OneTask API.

These endpoints handle CRUD operations for tasks, as well as advanced features like:
- Task prioritization
- Task breakdown
- Focus mode filtering
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.services import ai_service, task_service
from app.utils.dependencies import verify_premium_access

router = APIRouter()


@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    
    - Support filtering by workspace, status, and priority
    - Pagination with skip and limit parameters
    """
    tasks = task_service.get_tasks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        workspace_id=workspace_id,
        status=status,
        priority=priority,
    )
    return tasks


@router.post("/", response_model=schemas.Task)
async def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new task.
    
    - All fields in the TaskCreate schema can be provided
    - User ID is automatically added based on authentication
    - Notifications are sent via WebSocket when task is created
    """
    task = await task_service.create_task(db=db, task_in=task_in, user_id=current_user.id)
    return task


@router.get("/{task_id}", response_model=schemas.TaskWithSubtasks)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific task by ID.
    
    - Includes subtasks in the response
    - Only accessible if the task belongs to the current user
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a task.
    
    - Any fields in the TaskUpdate schema can be provided
    - Only fields that are provided will be updated
    - Only accessible if the task belongs to the current user
    - Notifications are sent via WebSocket when task is updated
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await task_service.update_task(db=db, task=task, task_in=task_in)
    return task


@router.delete("/{task_id}", response_model=schemas.Task)
async def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a task.
    
    - Soft delete (is_deleted flag is set to True)
    - Task can still be recovered if needed
    - Only accessible if the task belongs to the current user
    - Notifications are sent via WebSocket when task is deleted
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await task_service.delete_task(db=db, task_id=task_id)
    return task


@router.post("/prioritize", response_model=List[schemas.Task])
def prioritize_tasks(
    *,
    db: Session = Depends(get_db),
    workspace_id: Optional[int] = Body(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Automatically prioritize tasks based on various factors.
    
    - Uses AI to analyze task importance, deadlines, and user patterns
    - Optionally filter by workspace
    - Returns a prioritized list of tasks
    """
    tasks = task_service.prioritize_tasks(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id,
    )
    return tasks


@router.post("/{task_id}/complete", response_model=schemas.Task)
async def mark_task_completed(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Mark a task as completed.
    
    - Sets status to "done" and records completion timestamp
    - Updates task history
    - Only accessible if the task belongs to the current user
    - Notifications are sent via WebSocket when task is completed
    - Updates gamification stats and streaks
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await task_service.mark_task_completed(db=db, task=task)
    return task


@router.get("/focus-mode", response_model=schemas.TaskFocusMode)
def get_focus_mode_tasks(
    *,
    db: Session = Depends(get_db),
    context: Optional[str] = Query(None, description="Current work context (e.g., 'work', 'personal', 'study')"),
    time_available: Optional[int] = Query(None, description="Time available in minutes"),
    energy_level: Optional[int] = Query(None, ge=1, le=5, description="Current energy level (1-5)"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get tasks for focus mode based on context, time available, and energy level.
    
    - Provides a manageable set of tasks for the current focus session
    - Filters tasks based on user's context, available time, and energy level
    - Returns a primary task and a queue of next tasks
    """
    focus_mode = task_service.get_focus_mode_tasks(
        db=db,
        user_id=current_user.id,
        context=context,
        time_available=time_available,
        energy_level=energy_level,
    )
    return focus_mode


@router.get("/history", response_model=List[schemas.Task])
def get_task_history(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get completed task history.
    
    - Returns completed tasks within the specified date range
    - Supports pagination
    - Only returns tasks that belong to the current user
    """
    tasks = task_service.get_task_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    return tasks