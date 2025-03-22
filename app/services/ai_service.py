"""
AI service for the OneTask API.

This module handles interactions with AI services like OpenAI for features such as:
- Task breakdown
- Task analysis
- Productivity insights
- Smart task suggestions
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app import models, schemas
from app.core.config import settings

# Import OpenAI client
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Logger
logger = logging.getLogger(__name__)


async def break_down_task(task: models.Task) -> schemas.TaskBreakdown:
    """
    Use AI to break down a complex task into smaller subtasks.
    
    Args:
        task: Task to break down
        
    Returns:
        Task breakdown with subtasks and suggestions
    """
    if not settings.ENABLE_AI_FEATURES:
        logger.warning("AI features are disabled, returning empty breakdown")
        return schemas.TaskBreakdown(
            original_task=task,
            subtasks=[],
            suggestions="AI features are currently disabled."
        )
    
    try:
        # Prepare prompt for the AI
        prompt = f"""
        Please break down the following task into smaller, more manageable subtasks:
        
        Task Title: {task.title}
        Description: {task.description or 'No description provided'}
        Priority: {task.priority}
        Due Date: {task.due_date.isoformat() if task.due_date else 'No due date'}
        
        Guidelines:
        - Create 3-7 subtasks that would help complete this task
        - Each subtask should be clear and actionable
        - Subtasks should be in a logical sequence
        - Consider the task priority and due date when breaking it down
        - Provide a brief suggestion on how to approach this task effectively
        
        Return your response as a JSON object with the following structure:
        {{
            "subtasks": [
                {{"title": "Subtask 1", "description": "Details about subtask 1"}},
                {{"title": "Subtask 2", "description": "Details about subtask 2"}},
                ...
            ],
            "suggestions": "Your suggestions on how to approach the task effectively"
        }}
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in task management and productivity."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Create subtasks from the AI response
        subtasks = []
        for i, subtask_data in enumerate(result["subtasks"]):
            subtask = models.Task(
                title=subtask_data["title"],
                description=subtask_data.get("description", ""),
                status="todo",
                priority=task.priority,
                due_date=task.due_date,
                user_id=task.user_id,
                workspace_id=task.workspace_id,
                parent_id=task.id,
                order=i
            )
            subtasks.append(subtask)
        
        # Return task breakdown
        return schemas.TaskBreakdown(
            original_task=task,
            subtasks=subtasks,
            suggestions=result["suggestions"]
        )
    
    except Exception as e:
        logger.error(f"Error in break_down_task: {str(e)}")
        raise


async def generate_task_analysis(tasks: List[models.Task]) -> Dict[str, Any]:
    """
    Generate AI-powered analysis of user's tasks.
    
    Args:
        tasks: List of tasks to analyze
        
    Returns:
        Analysis results
    """
    if not settings.ENABLE_AI_FEATURES:
        logger.warning("AI features are disabled, returning empty analysis")
        return {
            "summary": "AI features are currently disabled.",
            "patterns": [],
            "recommendations": []
        }
    
    try:
        # Prepare tasks data for AI
        tasks_data = []
        for task in tasks:
            task_data = {
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "estimated_minutes": task.estimated_minutes,
                "actual_minutes": task.actual_minutes,
                "context_tags": task.context_tags,
            }
            tasks_data.append(task_data)
        
        # Prepare prompt for the AI
        prompt = f"""
        Please analyze the following tasks and provide productivity insights:
        
        Tasks: {json.dumps(tasks_data)}
        
        I need:
        1. A summary of task completion patterns
        2. Any noticeable patterns in productivity or task handling
        3. Recommendations for improving productivity
        
        Return your response as a JSON object with the following structure:
        {{
            "summary": "Overall summary of task patterns and productivity",
            "patterns": [
                "Pattern 1 description",
                "Pattern 2 description",
                ...
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                ...
            ]
        }}
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in productivity analysis and task management."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        return result
    
    except Exception as e:
        logger.error(f"Error in generate_task_analysis: {str(e)}")
        raise


async def generate_productivity_insights(tasks: List[models.Task], user: models.User) -> Dict[str, Any]:
    """
    Generate AI-powered productivity insights for the user.
    
    Args:
        tasks: List of user's tasks
        user: User object
        
    Returns:
        Productivity insights
    """
    if not settings.ENABLE_AI_FEATURES:
        logger.warning("AI features are disabled, returning empty insights")
        return {
            "optimal_hours": [],
            "focus_tips": [],
            "productivity_pattern": "AI features are currently disabled."
        }
    
    try:
        # Prepare tasks data for AI
        tasks_data = []
        for task in tasks:
            task_data = {
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "estimated_minutes": task.estimated_minutes,
                "actual_minutes": task.actual_minutes,
                "ai_energy_level": task.ai_energy_level,
                "context_tags": task.context_tags,
            }
            tasks_data.append(task_data)
        
        # Prepare user data
        user_data = {
            "time_zone": user.time_zone,
            "language": user.language
        }
        
        # Prepare prompt for the AI
        prompt = f"""
        Please analyze the following user's tasks and provide productivity insights:
        
        User: {json.dumps(user_data)}
        Tasks: {json.dumps(tasks_data)}
        
        I need:
        1. The user's optimal productive hours based on task completion times
        2. Focus tips tailored to the user's task patterns
        3. A description of the user's productivity pattern
        
        Return your response as a JSON object with the following structure:
        {{
            "optimal_hours": [
                {{"start_hour": 9, "end_hour": 11, "productivity_level": "high", "task_types": ["creative", "analytical"]}},
                {{"start_hour": 15, "end_hour": 17, "productivity_level": "medium", "task_types": ["administrative", "communication"]}}
            ],
            "focus_tips": [
                "Tip 1",
                "Tip 2",
                ...
            ],
            "productivity_pattern": "Description of the user's productivity pattern"
        }}
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in productivity analysis with expertise in helping neurodivergent individuals."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        return result
    
    except Exception as e:
        logger.error(f"Error in generate_productivity_insights: {str(e)}")
        raise


async def suggest_next_steps(task: models.Task, related_tasks: List[models.Task]) -> List[schemas.TaskCreate]:
    """
    Generate AI suggestions for next steps after completing a task.
    
    Args:
        task: Completed task
        related_tasks: List of related tasks for context
        
    Returns:
        List of suggested next tasks
    """
    if not settings.ENABLE_AI_FEATURES:
        logger.warning("AI features are disabled, returning empty next steps")
        return []
    
    try:
        # Prepare task data for AI
        task_data = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "context_tags": task.context_tags,
            "workspace_id": task.workspace_id,
        }
        
        # Prepare related tasks data
        related_tasks_data = []
        for related_task in related_tasks:
            related_task_data = {
                "title": related_task.title,
                "status": related_task.status,
                "priority": related_task.priority,
                "context_tags": related_task.context_tags,
            }
            related_tasks_data.append(related_task_data)
        
        # Prepare prompt for the AI
        prompt = f"""
        Please suggest next steps after completing the following task:
        
        Completed Task: {json.dumps(task_data)}
        Related Tasks (for context): {json.dumps(related_tasks_data)}
        
        I need:
        1. 3-5 potential follow-up tasks that would make sense to do next
        2. Each task should include a title, description, priority, and status
        3. The tasks should be logical next steps considering the completed task and related tasks
        
        Return your response as a JSON array with the following structure:
        [
            {{
                "title": "Next Task 1",
                "description": "Description of next task 1",
                "priority": "medium",
                "status": "todo",
                "context_tags": ["tag1", "tag2"]
            }},
            ...
        ]
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in task management and workflow optimization."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Convert to TaskCreate objects
        suggested_tasks = []
        for task_data in result:
            suggested_task = schemas.TaskCreate(
                title=task_data["title"],
                description=task_data.get("description", ""),
                priority=task_data.get("priority", "medium"),
                status=task_data.get("status", "todo"),
                context_tags=task_data.get("context_tags", []),
                workspace_id=task.workspace_id,
            )
            suggested_tasks.append(suggested_task)
        
        return suggested_tasks
    
    except Exception as e:
        logger.error(f"Error in suggest_next_steps: {str(e)}")
        raise