import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.task import Task, SubTask
from app.models.user import User
from app.schemas.task import TaskBreakdown, TaskCreate

# Configure logging
logger = logging.getLogger(__name__)

# Import OpenAI
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def break_down_task(task: Task) -> TaskBreakdown:
    """
    Use AI to break down a complex task into smaller subtasks.
    
    Args:
        task: Task to break down
        
    Returns:
        Task breakdown with subtasks and suggestions
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        )
    
    try:
        # Prepare task data for the prompt
        task_data = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": [tag.name for tag in task.tags] if task.tags else [],
        }
        
        # Create prompt
        prompt = f"""
        I'd like you to break down the following task into smaller, more manageable subtasks. 
        This is for a neurodivergent user who may benefit from clearer, more actionable steps.
        
        Task: {json.dumps(task_data, indent=2)}
        
        Please break this down into 3-7 smaller subtasks, each with:
        1. A clear, specific title
        2. Appropriate priority level (low, medium, high, urgent)
        3. Estimated time to complete (in minutes)
        
        Also provide brief suggestions on how to approach this task effectively, especially for someone with ADHD or other neurodivergent traits.
        
        Format your response as JSON with the following structure:
        {{
            "subtasks": [
                {{
                    "title": "Subtask title",
                    "priority": "medium",
                    "estimated_minutes": 30
                }}
            ],
            "suggestions": "Brief helpful suggestions for approaching this task"
        }}
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in task management and productivity for neurodivergent individuals."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Create subtasks from the AI response
        subtasks = []
        for subtask_data in result["subtasks"]:
            # Create a new Task object (which will be a subtask)
            subtask = Task(
                title=subtask_data["title"],
                priority=subtask_data["priority"],
                estimated_minutes=subtask_data.get("estimated_minutes", None),
                user_id=task.user_id,
                workspace_id=task.workspace_id,
                parent_id=task.id,
                status="todo",
            )
            subtasks.append(subtask)
        
        return TaskBreakdown(
            original_task=task,
            subtasks=subtasks,
            suggestions=result["suggestions"]
        )
        
    except Exception as e:
        logger.error(f"Error in AI task breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process AI task breakdown: {str(e)}",
        )


async def generate_task_analysis(tasks: List[Task]) -> Dict[str, Any]:
    """
    Generate AI-powered analysis of user's tasks.
    
    Args:
        tasks: List of tasks to analyze
        
    Returns:
        Analysis results
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        )
    
    try:
        # Prepare task data for the prompt
        task_data = []
        for task in tasks:
            task_data.append({
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "estimated_minutes": task.estimated_minutes,
                "actual_minutes": task.actual_minutes,
                "tags": [tag.name for tag in task.tags] if task.tags else [],
            })
        
        # Create prompt
        prompt = f"""
        Please analyze the following task data for a user and provide insights:
        
        Task Data: {json.dumps(task_data, indent=2)}
        
        Please provide the following analysis:
        1. Productivity patterns (when tasks are completed, efficiency, etc.)
        2. Task completion rate and time management
        3. Priority management (how well they handle high vs. low priority tasks)
        4. Key challenges identified from the task data
        5. Recommendations for improvement
        
        Format your response as a JSON object with these sections.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI productivity analyst specialized in helping neurodivergent individuals optimize their task management."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error in AI task analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process AI task analysis: {str(e)}",
        )


async def generate_productivity_insights(tasks: List[Task], user: User) -> Dict[str, Any]:
    """
    Generate AI-powered productivity insights for the user.
    
    Args:
        tasks: List of user's tasks
        user: User object
        
    Returns:
        Productivity insights
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        )
    
    try:
        # Prepare task data for the prompt
        completed_tasks = [t for t in tasks if t.status == "done"]
        ongoing_tasks = [t for t in tasks if t.status != "done"]
        
        completed_on_time = sum(1 for t in completed_tasks if t.due_date and t.completed_at <= t.due_date)
        completed_late = sum(1 for t in completed_tasks if t.due_date and t.completed_at > t.due_date)
        
        # Calculate efficiency metrics
        estimation_accuracy = []
        for task in completed_tasks:
            if task.estimated_minutes and task.actual_minutes:
                accuracy = task.actual_minutes / task.estimated_minutes
                estimation_accuracy.append(accuracy)
        
        avg_accuracy = sum(estimation_accuracy) / len(estimation_accuracy) if estimation_accuracy else None
        
        # Prepare metrics
        metrics = {
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "completion_rate": len(completed_tasks) / len(tasks) if tasks else 0,
            "completed_on_time": completed_on_time,
            "completed_late": completed_late,
            "on_time_rate": completed_on_time / len(completed_tasks) if completed_tasks else 0,
            "estimation_accuracy": avg_accuracy,
        }
        
        # Create prompt
        prompt = f"""
        Please analyze the following productivity data for a user and provide personalized insights:
        
        Productivity Metrics: {json.dumps(metrics, indent=2)}
        
        The user has {len(ongoing_tasks)} ongoing tasks and {len(completed_tasks)} completed tasks.
        
        Please provide the following insights for a user who may have ADHD or be neurodivergent:
        1. Strengths in their current productivity
        2. Areas for improvement
        3. Personalized suggestions for better task management
        4. Specific techniques that might help with focus and completion
        5. A motivational message
        
        Format your response as a JSON object with these sections.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI productivity coach specialized in supporting neurodivergent individuals."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Add metrics to the result
        result["metrics"] = metrics
        
        return result
        
    except Exception as e:
        logger.error(f"Error in AI productivity insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate productivity insights: {str(e)}",
        )


async def suggest_next_steps(task: Task, related_tasks: List[Task]) -> List[TaskCreate]:
    """
    Generate AI suggestions for next steps after completing a task.
    
    Args:
        task: Completed task
        related_tasks: List of related tasks for context
        
    Returns:
        List of suggested next tasks
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        )
    
    try:
        # Prepare task data for the prompt
        task_data = {
            "title": task.title,
            "description": task.description,
            "tags": [tag.name for tag in task.tags] if task.tags else [],
            "workspace_id": task.workspace_id,
        }
        
        related_data = []
        for related_task in related_tasks:
            related_data.append({
                "title": related_task.title,
                "status": related_task.status,
                "priority": related_task.priority,
            })
        
        # Create prompt
        prompt = f"""
        The user has completed the following task:
        
        Task: {json.dumps(task_data, indent=2)}
        
        Here are some related tasks for context:
        {json.dumps(related_data, indent=2)}
        
        Based on the completed task and context, suggest 2-3 potential next tasks that would be logical follow-ups.
        
        For each suggested task, provide:
        1. Title
        2. Brief description
        3. Suggested priority (low, medium, high)
        4. Estimated time to complete (in minutes)
        5. Any relevant tags
        
        Format your response as a JSON array of task objects.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI productivity assistant that helps users maintain momentum by suggesting logical next steps."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Convert the result to TaskCreate objects
        suggested_tasks = []
        for suggestion in result:
            task_create = TaskCreate(
                title=suggestion["title"],
                description=suggestion.get("description", ""),
                priority=suggestion.get("priority", "medium"),
                estimated_minutes=suggestion.get("estimated_minutes", None),
                context_tags=suggestion.get("tags", []),
                workspace_id=task.workspace_id,
            )
            suggested_tasks.append(task_create)
        
        return suggested_tasks
        
    except Exception as e:
        logger.error(f"Error in AI next steps suggestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suggest next steps: {str(e)}",
        )
