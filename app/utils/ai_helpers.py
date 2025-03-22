import json
import logging
from typing import Dict, Any, List

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Import OpenAI
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def enhance_task_with_ai(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance a task with AI suggestions and metadata.
    
    Args:
        task_data: Task data
        
    Returns:
        Enhanced task data with AI suggestions
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured, skipping AI enhancement")
        return task_data
    
    try:
        prompt = f"""
        Please analyze this task and provide helpful metadata:
        
        Task: {json.dumps(task_data, indent=2)}
        
        Provide the following:
        1. An energy level estimate (low, medium, high)
        2. A complexity score (1-5)
        3. Suggestions for breaking down the task if it seems complex
        4. A recommended time block to work on this task (morning, afternoon, evening)
        
        Format your response as a JSON object.
        """
        
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps with task analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Update task data with AI suggestions
        task_data["ai_energy_level"] = result.get("energy_level", "medium")
        task_data["ai_complexity_score"] = result.get("complexity_score", 3)
        task_data["ai_suggestions"] = {
            "breakdown": result.get("breakdown_suggestions", []),
            "recommended_time_block": result.get("recommended_time_block", "morning"),
        }
        
        return task_data
        
    except Exception as e:
        logger.error(f"Error in AI task enhancement: {str(e)}")
        return task_data


async def categorize_tasks_with_ai(tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize tasks using AI.
    
    Args:
        tasks: List of task data
        
    Returns:
        Categorized tasks
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured, skipping AI categorization")
        return {"uncategorized": tasks}
    
    try:
        prompt = f"""
        Please categorize these tasks into logical groups:
        
        Tasks: {json.dumps(tasks, indent=2)}
        
        Group them into categories that would make sense for a neurodivergent user.
        Try to use categories like "Quick Wins", "Deep Focus", "Creative", "Administrative", etc.
        
        Format your response as a JSON object where keys are category names and values are arrays of task indices.
        """
        
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps with task organization."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Organize tasks by categories
        categorized = {}
        for category, indices in result.items():
            categorized[category] = [tasks[i] for i in indices if i < len(tasks)]
        
        return categorized
        
    except Exception as e:
        logger.error(f"Error in AI task categorization: {str(e)}")
        return {"uncategorized": tasks}


async def generate_dopamine_boost_message() -> str:
    """
    Generate a motivational message for dopamine boost.
    
    Returns:
        Motivational message
    """
    if not settings.OPENAI_API_KEY:
        return "Great job completing your task! 🎉"
    
    try:
        prompt = """
        Generate a short, uplifting message to congratulate a user with ADHD for completing a task.
        Make it positive, motivational, and dopamine-inducing. Keep it under 100 characters.
        """
        
        response = openai_client.chat.completions.create(
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a motivational coach who understands neurodivergent needs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.8,
        )
        
        message = response.choices[0].message.content.strip()
        return message
        
    except Exception as e:
        logger.error(f"Error generating dopamine boost message: {str(e)}")
        return "Great job completing your task! 🎉"
