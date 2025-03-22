"""
AI-powered endpoints for the OneTask API.

These endpoints provide AI-enhanced features like:
- Task breakdown
- Task analysis
- Productivity insights
- Planning suggestions
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.services import ai_service, task_service
from app.utils.dependencies import verify_premium_access

router = APIRouter()


@router.post("/break-down-task", response_model=schemas.TaskBreakdown)
async def ai_break_down_task(
    *,
    db: Session = Depends(get_db),
    task_id: int = Body(...),
    current_user: models.User = Depends(get_current_active_user),
    _: None = Depends(verify_premium_access),
) -> Any:
    """
    AI-powered task breakdown into smaller subtasks.
    
    - Uses AI to break down a complex task into manageable subtasks
    - Provides suggestions for tackling the task more effectively
    - Requires premium access
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        breakdown = await ai_service.break_down_task(task)
        return breakdown
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/analyze-tasks", response_model=Dict[str, Any])
async def ai_analyze_tasks(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[str] = Body(None),
    end_date: Optional[str] = Body(None),
    workspace_id: Optional[int] = Body(None),
    current_user: models.User = Depends(get_current_active_user),
    _: None = Depends(verify_premium_access),
) -> Any:
    """
    AI-powered task analysis for productivity insights.
    
    - Analyzes task completion patterns, timing, and efficiency
    - Provides recommendations for improving productivity
    - Identifies potential bottlenecks and time sinks
    - Requires premium access
    """
    # Get tasks for the specified date range and workspace
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    tasks = task_service.get_task_history(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        **filters,
    )
    
    try:
        analysis = await ai_service.generate_task_analysis(tasks)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/productivity-insights", response_model=Dict[str, Any])
async def ai_productivity_insights(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    _: None = Depends(verify_premium_access),
) -> Any:
    """
    AI-powered productivity insights based on task history and patterns.
    
    - Provides personalized productivity patterns and insights
    - Suggests optimal working hours based on completion history
    - Recommends techniques for improving focus and productivity
    - Requires premium access
    """
    # Get all user's completed tasks for analysis
    tasks = task_service.get_task_history(
        db=db,
        user_id=current_user.id,
        limit=100,  # Analyze last 100 completed tasks
    )
    
    try:
        insights = await ai_service.generate_productivity_insights(tasks, current_user)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/{task_id}/suggest-next-steps", response_model=List[schemas.TaskCreate])
async def ai_suggest_next_steps(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    _: None = Depends(verify_premium_access),
) -> Any:
    """
    AI suggestions for next steps after completing a task.
    
    - Generates suggested follow-up tasks based on task completion
    - Provides context-aware recommendations
    - Can be directly used to create new tasks
    - Requires premium access
    """
    task = task_service.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get related tasks for context
    related_tasks = task_service.get_tasks(
        db=db,
        user_id=current_user.id,
        workspace_id=task.workspace_id,
        limit=10,
    )
    
    try:
        suggestions = await ai_service.suggest_next_steps(task, related_tasks)
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )