from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.task import Task, SubTask, TaskTag
from app.schemas.task import TaskCreate, TaskUpdate, TaskFocusMode
from app.websockets.notification_handlers import send_task_notification, broadcast_task_update


def get_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[Task]:
    """
    Get tasks for a user with optional filtering.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        workspace_id: Filter by workspace ID
        status: Filter by status
        priority: Filter by priority
        
    Returns:
        List of tasks
    """
    query = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_deleted == False,
        Task.parent_id == None,  # Only get top-level tasks
    )
    
    if workspace_id:
        query = query.filter(Task.workspace_id == workspace_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    # Order by priority (highest first) and due date (earliest first)
    query = query.order_by(
        Task.priority.desc(),
        Task.due_date.asc().nullslast(),
    )
    
    return query.offset(skip).limit(limit).all()


def get_task(
    db: Session,
    task_id: int,
    user_id: int,
) -> Optional[Task]:
    """
    Get a specific task by ID.
    
    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID
        
    Returns:
        Task or None if not found
    """
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.is_deleted == False,
    ).first()


async def create_task(
    db: Session,
    task_in: TaskCreate,
    user_id: int,
) -> Task:
    """
    Create a new task.
    
    Args:
        db: Database session
        task_in: Task data
        user_id: User ID
        
    Returns:
        Created task
    """
    # Extract tag IDs and new tag names
    tag_ids = []
    new_tags = []
    if task_in.tags:
        for tag in task_in.tags:
            if isinstance(tag, int):
                tag_ids.append(tag)
            elif isinstance(tag, str):
                new_tags.append(tag)
    
    # Create task object
    task_data = task_in.dict(exclude={"tags", "subtasks"})
    db_task = Task(user_id=user_id, **task_data)
    
    # Add existing tags
    if tag_ids:
        existing_tags = db.query(TaskTag).filter(
            TaskTag.id.in_(tag_ids),
            (TaskTag.user_id == user_id) | (TaskTag.is_system == True),
        ).all()
        db_task.tags.extend(existing_tags)
    
    # Create and add new tags
    for tag_name in new_tags:
        tag = TaskTag(name=tag_name, user_id=user_id)
        db.add(tag)
        db.flush()
        db_task.tags.append(tag)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Add subtasks if provided
    if task_in.subtasks:
        for subtask_data in task_in.subtasks:
            subtask = SubTask(
                task_id=db_task.id,
                **subtask_data.dict(),
            )
            db.add(subtask)
        
        db.commit()
        db.refresh(db_task)
    
    # Send real-time notification to the task owner
    await send_task_notification(
        db=db,
        user_id=user_id,
        task_id=db_task.id,
        task_title=db_task.title,
        action="created",
        workspace_id=db_task.workspace_id,
    )
    
    # If task is in a workspace, broadcast update to workspace members
    if db_task.workspace_id:
        await broadcast_task_update(
            db=db,
            task_id=db_task.id,
            task_title=db_task.title,
            action="created",
            workspace_id=db_task.workspace_id,
            actor_id=user_id,
            exclude_user_ids=[user_id]  # Don't send to the task creator
        )
    
    return db_task


async def update_task(
    db: Session,
    task: Task,
    task_in: TaskUpdate,
) -> Task:
    """
    Update a task.
    
    Args:
        db: Database session
        task: Task object to update
        task_in: Updated task data
        
    Returns:
        Updated task
    """
    # Handle tags if provided
    if task_in.tags is not None:
        # Clear existing tags
        task.tags = []
        
        # Add new tags
        tag_ids = []
        new_tags = []
        for tag in task_in.tags:
            if isinstance(tag, int):
                tag_ids.append(tag)
            elif isinstance(tag, str):
                new_tags.append(tag)
        
        # Add existing tags
        if tag_ids:
            existing_tags = db.query(TaskTag).filter(
                TaskTag.id.in_(tag_ids),
                (TaskTag.user_id == task.user_id) | (TaskTag.is_system == True),
            ).all()
            task.tags.extend(existing_tags)
        
        # Create and add new tags
        for tag_name in new_tags:
            tag = db.query(TaskTag).filter(
                TaskTag.name == tag_name,
                TaskTag.user_id == task.user_id,
            ).first()
            
            if not tag:
                tag = TaskTag(name=tag_name, user_id=task.user_id)
                db.add(tag)
                db.flush()
            
            task.tags.append(tag)
    
    # Update task status
    old_status = task.status
    new_status = task_in.status
    
    # Update task fields
    update_data = task_in.dict(exclude={"tags"}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Handle task completion
    if old_status != "done" and new_status == "done":
        task.completed_at = datetime.now()
    elif old_status == "done" and new_status != "done":
        task.completed_at = None
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Determine the notification action
    action = "updated"
    if old_status != "done" and new_status == "done":
        action = "completed"
    
    # Send real-time notification to the task owner
    await send_task_notification(
        db=db,
        user_id=task.user_id,
        task_id=task.id,
        task_title=task.title,
        action=action,
        workspace_id=task.workspace_id,
    )
    
    # If task is in a workspace, broadcast update to workspace members
    if task.workspace_id:
        await broadcast_task_update(
            db=db,
            task_id=task.id,
            task_title=task.title,
            action=action,
            workspace_id=task.workspace_id,
            actor_id=task.user_id,
            exclude_user_ids=[task.user_id]  # Don't send to the task owner
        )
    
    return task


async def delete_task(
    db: Session,
    task_id: int,
) -> None:
    """
    Soft delete a task.
    
    Args:
        db: Database session
        task_id: Task ID
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.is_deleted = True
        db.add(task)
        db.commit()
        
        # Send real-time notification to the task owner
        await send_task_notification(
            db=db,
            user_id=task.user_id,
            task_id=task.id,
            task_title=task.title,
            action="deleted",
            workspace_id=task.workspace_id,
        )
        
        # If task is in a workspace, broadcast update to workspace members
        if task.workspace_id:
            await broadcast_task_update(
                db=db,
                task_id=task.id,
                task_title=task.title,
                action="deleted",
                workspace_id=task.workspace_id,
                actor_id=task.user_id,
                exclude_user_ids=[task.user_id]  # Don't send to the task owner
            )


def prioritize_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
) -> List[Task]:
    """
    Automatically prioritize tasks based on various factors.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        workspace_id: Filter by workspace ID
        
    Returns:
        List of prioritized tasks
    """
    # Get incomplete tasks
    query = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_deleted == False,
        Task.status != "done",
        Task.parent_id == None,  # Only get top-level tasks
    )
    
    if workspace_id:
        query = query.filter(Task.workspace_id == workspace_id)
    
    tasks = query.all()
    
    # Calculate priority score for each task
    now = datetime.now()
    for task in tasks:
        score = 0
        
        # Factor 1: Due date proximity
        if task.due_date:
            days_until_due = (task.due_date - now).days
            if days_until_due < 0:  # Overdue
                score += 100
            elif days_until_due == 0:  # Due today
                score += 80
            elif days_until_due <= 2:  # Due in next 2 days
                score += 60
            elif days_until_due <= 7:  # Due in next week
                score += 40
            else:
                score += max(0, 30 - days_until_due * 0.5)  # Gradually decrease importance
        
        # Factor 2: Priority level
        if task.priority == "urgent":
            score += 100
        elif task.priority == "high":
            score += 75
        elif task.priority == "medium":
            score += 50
        else:  # low
            score += 25
        
        # Factor 3: Task complexity (if available)
        if task.ai_complexity_score:
            score += task.ai_complexity_score * 20  # Scale 0-5 to 0-100
        
        # Factor 4: Energy level match (if available)
        if task.ai_energy_level:
            # In a real implementation, we would match this with the user's current energy level
            # For now, we'll give a small boost to medium energy tasks
            if task.ai_energy_level == "medium":
                score += 10
            elif task.ai_energy_level == "low":
                score += 5
        
        # Store the calculated priority score
        task.ai_priority_score = score
    
    # Sort tasks by priority score (descending)
    prioritized_tasks = sorted(tasks, key=lambda t: t.ai_priority_score or 0, reverse=True)
    
    # Apply pagination
    return prioritized_tasks[skip:skip+limit]


def get_focus_mode_tasks(
    db: Session,
    user_id: int,
    context: Optional[str] = None,
    time_available: Optional[int] = None,
    energy_level: Optional[int] = None,
) -> TaskFocusMode:
    """
    Get tasks for focus mode based on context, time available, and energy level.
    
    Args:
        db: Database session
        user_id: User ID
        context: Current work context (e.g., "work", "personal", "study")
        time_available: Time available in minutes
        energy_level: Current energy level (1-5)
        
    Returns:
        Focus mode tasks
    """
    # Get incomplete tasks that are included in focus mode
    query = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_deleted == False,
        Task.status != "done",
        Task.focus_mode_included == True,
        Task.parent_id == None,  # Only get top-level tasks
    )
    
    # Filter by context if provided
    if context:
        query = query.filter(Task.context_tags.contains([context]))
    
    tasks = query.all()
    
    # Calculate task suitability for current focus session
    now = datetime.now()
    for task in tasks:
        suitability_score = 0
        
        # Factor 1: Due date urgency
        if task.due_date:
            hours_until_due = max(0, (task.due_date - now).total_seconds() / 3600)
            if hours_until_due <= 24:  # Due within 24 hours
                suitability_score += 100
            elif hours_until_due <= 72:  # Due within 3 days
                suitability_score += 75
            else:
                suitability_score += 50
        else:
            suitability_score += 25  # No due date
        
        # Factor 2: Priority
        if task.priority == "urgent":
            suitability_score += 100
        elif task.priority == "high":
            suitability_score += 75
        elif task.priority == "medium":
            suitability_score += 50
        else:  # low
            suitability_score += 25
        
        # Factor 3: Energy level match
        if energy_level is not None and task.ai_energy_level:
            energy_map = {"low": 1, "medium": 3, "high": 5}
            task_energy = energy_map.get(task.ai_energy_level, 3)
            
            # Perfect match gets highest score
            if task_energy == energy_level:
                suitability_score += 50
            # Small mismatch gets medium score
            elif abs(task_energy - energy_level) == 1:
                suitability_score += 25
            # Large mismatch gets lowest score
            else:
                suitability_score += 10
        
        # Factor 4: Time match
        if time_available is not None and task.estimated_minutes:
            # Prefer tasks that fit within the available time
            if task.estimated_minutes <= time_available:
                # Higher score for tasks that use time efficiently
                time_efficiency = task.estimated_minutes / time_available
                suitability_score += 50 * time_efficiency
            else:
                # Penalize tasks that don't fit in the available time
                suitability_score -= 25
        
        # Store the suitability score temporarily
        task.ai_priority_score = suitability_score
    
    # Sort tasks by suitability score
    sorted_tasks = sorted(tasks, key=lambda t: t.ai_priority_score or 0, reverse=True)
    
    # Prepare focus mode response
    current_task = sorted_tasks[0] if sorted_tasks else None
    next_tasks = sorted_tasks[1:5] if len(sorted_tasks) > 1 else []
    
    # Calculate estimated total time
    estimated_total_time = 0
    if current_task and current_task.estimated_minutes:
        estimated_total_time += current_task.estimated_minutes
    
    for task in next_tasks:
        if task.estimated_minutes:
            estimated_total_time += task.estimated_minutes
    
    return TaskFocusMode(
        current_task=current_task,
        next_tasks=next_tasks,
        estimated_total_time=estimated_total_time,
        context=context,
        energy_level=energy_level,
    )


async def mark_task_completed(
    db: Session,
    task: Task,
) -> Task:
    """
    Mark a task as completed.
    
    Args:
        db: Database session
        task: Task to mark as completed
        
    Returns:
        Updated task
    """
    task.status = "done"
    task.completed_at = datetime.now()
    
    # Update user statistics if task is completed
    from app.models.gamification import UserStats, UserStreak
    
    # Get or create user stats
    user_stats = db.query(UserStats).filter(
        UserStats.user_id == task.user_id
    ).first()
    
    if not user_stats:
        user_stats = UserStats(user_id=task.user_id)
        db.add(user_stats)
    
    # Update stats
    user_stats.tasks_completed += 1
    
    # Check if completed on time
    if task.due_date and task.completed_at <= task.due_date:
        user_stats.tasks_completed_on_time += 1
    
    # Update streak
    user_streak = db.query(UserStreak).filter(
        UserStreak.user_id == task.user_id
    ).first()
    
    if not user_streak:
        user_streak = UserStreak(
            user_id=task.user_id,
            current_streak=1,
            longest_streak=1,
            last_activity_date=datetime.now(),
            streak_start_date=datetime.now(),
        )
        db.add(user_streak)
    else:
        # Check if streak is continued
        today = datetime.now().date()
        if user_streak.last_activity_date:
            last_date = user_streak.last_activity_date.date()
            days_difference = (today - last_date).days
            
            if days_difference == 0:
                # Already recorded activity today
                pass
            elif days_difference == 1:
                # Streak continues
                user_streak.current_streak += 1
                if user_streak.current_streak > user_streak.longest_streak:
                    user_streak.longest_streak = user_streak.current_streak
            elif days_difference > 1:
                # Streak broken
                user_streak.current_streak = 1
                user_streak.streak_start_date = datetime.now()
        
        user_streak.last_activity_date = datetime.now()
    
    # Update user stats streak info
    user_stats.current_streak = user_streak.current_streak
    user_stats.longest_streak = user_streak.longest_streak
    
    db.add(task)
    db.add(user_stats)
    db.add(user_streak)
    db.commit()
    db.refresh(task)
    
    # Send real-time notification to the task owner
    await send_task_notification(
        db=db,
        user_id=task.user_id,
        task_id=task.id,
        task_title=task.title,
        action="completed",
        workspace_id=task.workspace_id,
    )
    
    # If task is in a workspace, broadcast update to workspace members
    if task.workspace_id:
        await broadcast_task_update(
            db=db,
            task_id=task.id,
            task_title=task.title,
            action="completed",
            workspace_id=task.workspace_id,
            actor_id=task.user_id,
            exclude_user_ids=[task.user_id]  # Don't send to the task owner
        )
    
    return task


def get_task_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Task]:
    """
    Get completed task history.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        
    Returns:
        List of completed tasks
    """
    query = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == "done",
        Task.is_deleted == False,
    )
    
    # Filter by date range
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Task.completed_at >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
            )
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(Task.completed_at <= end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
            )
    
    # Order by completion date (most recent first)
    query = query.order_by(Task.completed_at.desc())
    
    return query.offset(skip).limit(limit).all()
