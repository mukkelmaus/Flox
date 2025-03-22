from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, Task, TaskBreakdown
from app.services.ai_service import (
    break_down_task,
    generate_task_analysis,
    generate_productivity_insights,
    suggest_next_steps,
)

router = APIRouter()


@router.post("/break-down-task", response_model=TaskBreakdown)
async def ai_break_down_task(
    *,
    db: Session = Depends(get_db),
    task_id: int = Body(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    AI-powered task breakdown into smaller subtasks.
    
    - **task_id**: ID of the task to break down
    """
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are disabled",
        )
    
    # Get task from database
    from app.models.task import Task as TaskModel
    
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Use AI service to break down the task
    breakdown = await break_down_task(task)
    return breakdown


@router.post("/analyze-tasks", response_model=dict)
async def ai_analyze_tasks(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[str] = Body(None),
    end_date: Optional[str] = Body(None),
    workspace_id: Optional[int] = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    AI-powered task analysis for productivity insights.
    
    - **start_date**: Start date for analysis (ISO format)
    - **end_date**: End date for analysis (ISO format)
    - **workspace_id**: Limit analysis to a specific workspace
    """
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are disabled",
        )
    
    # Get user's tasks for the specified time period
    from app.models.task import Task as TaskModel
    import datetime
    
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    
    if start_date:
        try:
            start_datetime = datetime.datetime.fromisoformat(start_date)
            query = query.filter(TaskModel.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)",
            )
    
    if end_date:
        try:
            end_datetime = datetime.datetime.fromisoformat(end_date)
            query = query.filter(TaskModel.created_at <= end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)",
            )
    
    if workspace_id:
        query = query.filter(TaskModel.workspace_id == workspace_id)
    
    tasks = query.all()
    
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found for the specified criteria",
        )
    
    # Generate insights using AI
    analysis = await generate_task_analysis(tasks)
    return analysis


@router.post("/productivity-insights", response_model=dict)
async def ai_productivity_insights(
    *,
    db: Session = Depends(get_db),
    days: Optional[int] = Body(30),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    AI-powered productivity insights and suggestions based on task history.
    
    - **days**: Number of days to include in the analysis (default: 30)
    """
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are disabled",
        )
    
    # Get user's tasks for the specified time period
    from app.models.task import Task as TaskModel
    import datetime
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    tasks = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.created_at >= start_date,
    ).all()
    
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found for the specified time period",
        )
    
    # Generate productivity insights
    insights = await generate_productivity_insights(tasks, current_user)
    return insights


@router.post("/next-steps", response_model=List[TaskCreate])
async def ai_suggest_next_steps(
    *,
    db: Session = Depends(get_db),
    task_id: int = Body(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get AI suggestions for next steps after completing a task.
    
    - **task_id**: ID of the completed task
    """
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are disabled",
        )
    
    # Get task from database
    from app.models.task import Task as TaskModel
    
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Ensure task is completed
    if task.status != "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task must be completed to get next step suggestions",
        )
    
    # Get related tasks for context
    related_tasks = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.id != task_id,
        TaskModel.workspace_id == task.workspace_id,
    ).limit(10).all()
    
    # Generate next step suggestions
    next_steps = await suggest_next_steps(task, related_tasks)
    return next_steps
