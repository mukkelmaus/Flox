import logging
import httpx
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.integration import Integration
from app.models.task import Task, TaskTag
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


def get_available_integrations() -> List[Dict[str, Any]]:
    """
    Get a list of available third-party integrations.
    
    Returns:
        List of available integrations with details
    """
    return [
        {
            "id": "google_calendar",
            "name": "Google Calendar",
            "description": "Sync tasks with Google Calendar events",
            "auth_type": "oauth2",
            "icon": "calendar",
            "enabled": True,
            "scopes": ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"],
            "setup_instructions": "Sign in with Google and allow access to your calendar."
        },
        {
            "id": "todoist",
            "name": "Todoist",
            "description": "Import tasks from Todoist",
            "auth_type": "oauth2",
            "icon": "check-square",
            "enabled": True,
            "scopes": ["task:read", "data:read"],
            "setup_instructions": "Connect your Todoist account to import tasks."
        },
        {
            "id": "github",
            "name": "GitHub",
            "description": "Create tasks from GitHub issues",
            "auth_type": "oauth2",
            "icon": "github",
            "enabled": True,
            "scopes": ["repo"],
            "setup_instructions": "Connect your GitHub account and select repositories to monitor."
        },
        {
            "id": "slack",
            "name": "Slack",
            "description": "Create tasks from Slack messages",
            "auth_type": "oauth2",
            "icon": "slack",
            "enabled": True,
            "scopes": ["chat:read", "chat:write"],
            "setup_instructions": "Add the OneTask app to your Slack workspace."
        },
        {
            "id": "trello",
            "name": "Trello",
            "description": "Sync with Trello boards and cards",
            "auth_type": "oauth2",
            "icon": "trello",
            "enabled": True,
            "scopes": ["read", "write"],
            "setup_instructions": "Connect your Trello account and select boards to sync."
        },
    ]


async def get_integration_auth_url(service: str, user_id: int) -> Dict[str, Any]:
    """
    Get OAuth authorization URL for the requested service.
    
    Args:
        service: Service name
        user_id: User ID
        
    Returns:
        Dict with auth_url and state
    """
    # In a real implementation, we would generate proper OAuth URLs for each service
    # with appropriate scopes and state parameters
    
    # Check if the service is supported
    available_integrations = get_available_integrations()
    integration = next((i for i in available_integrations if i["id"] == service), None)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration '{service}' is not supported"
        )
    
    # Mock auth URL generation
    if service == "google_calendar":
        scopes = "+".join(integration["scopes"])
        state = f"user_{user_id}_{service}_{datetime.now().timestamp()}"
        redirect_uri = f"{settings.SERVER_HOST}/api/v1/integrations/oauth/callback"
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
            f"&response_type=code"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        
        return {
            "auth_url": auth_url,
            "state": state,
            "service": service
        }
    
    elif service == "todoist":
        scopes = ",".join(integration["scopes"])
        state = f"user_{user_id}_{service}_{datetime.now().timestamp()}"
        redirect_uri = f"{settings.SERVER_HOST}/api/v1/integrations/oauth/callback"
        
        auth_url = (
            f"https://todoist.com/oauth/authorize"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )
        
        return {
            "auth_url": auth_url,
            "state": state,
            "service": service
        }
    
    elif service == "github":
        scopes = " ".join(integration["scopes"])
        state = f"user_{user_id}_{service}_{datetime.now().timestamp()}"
        redirect_uri = f"{settings.SERVER_HOST}/api/v1/integrations/oauth/callback"
        
        auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )
        
        return {
            "auth_url": auth_url,
            "state": state,
            "service": service
        }
    
    else:
        # Generic mock URL for other services
        state = f"user_{user_id}_{service}_{datetime.now().timestamp()}"
        redirect_uri = f"{settings.SERVER_HOST}/api/v1/integrations/oauth/callback"
        
        auth_url = (
            f"https://auth.example.com/{service}/authorize"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
        
        return {
            "auth_url": auth_url,
            "state": state,
            "service": service
        }


async def handle_oauth_callback(
    db: Session,
    code: str,
    state: str,
    service: str,
    user_id: int
) -> Dict[str, Any]:
    """
    Handle OAuth callback and create integration.
    
    Args:
        db: Database session
        code: Authorization code
        state: State parameter
        service: Service name
        user_id: User ID
        
    Returns:
        Newly created integration
    """
    # Validate state parameter to prevent CSRF
    # In a real implementation, we would verify the state parameter
    # against a stored value to prevent CSRF attacks
    
    try:
        # Mock token exchange
        # In a real implementation, we would exchange the authorization code
        # for an access token and refresh token using the appropriate API
        
        # Mock tokens
        access_token = f"mock_access_token_{service}_{user_id}"
        refresh_token = f"mock_refresh_token_{service}_{user_id}"
        token_expiry = datetime.now() + timedelta(hours=1)
        
        # Check if integration already exists
        existing_integration = db.query(Integration).filter(
            Integration.user_id == user_id,
            Integration.service == service
        ).first()
        
        if existing_integration:
            # Update existing integration
            existing_integration.access_token = access_token
            existing_integration.refresh_token = refresh_token
            existing_integration.token_expiry = token_expiry
            existing_integration.is_active = True
            db.add(existing_integration)
            db.commit()
            db.refresh(existing_integration)
            
            return {
                "status": "success",
                "message": f"{service} integration updated successfully",
                "integration_id": existing_integration.id
            }
        else:
            # Create new integration
            integration = Integration(
                user_id=user_id,
                service=service,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry,
                is_active=True,
                config={},  # Default empty config
            )
            
            db.add(integration)
            db.commit()
            db.refresh(integration)
            
            return {
                "status": "success",
                "message": f"{service} integration created successfully",
                "integration_id": integration.id
            }
    
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing OAuth callback: {str(e)}"
        )


async def refresh_access_token(db: Session, integration: Integration) -> bool:
    """
    Refresh the access token for an integration.
    
    Args:
        db: Database session
        integration: Integration to refresh
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # In a real implementation, we would use the refresh token
        # to get a new access token from the service's API
        
        # Mock successful refresh
        integration.access_token = f"new_mock_access_token_{integration.service}_{integration.user_id}"
        integration.token_expiry = datetime.now() + timedelta(hours=1)
        
        db.add(integration)
        db.commit()
        
        return True
    
    except Exception as e:
        logger.error(f"Error refreshing access token: {str(e)}")
        return False


async def sync_with_google_calendar(
    db: Session, 
    integration: Integration,
    user: User,
) -> Dict[str, Any]:
    """
    Sync tasks with Google Calendar.
    
    Args:
        db: Database session
        integration: Google Calendar integration
        user: User
        
    Returns:
        Sync results
    """
    logger.info(f"Syncing with Google Calendar for user {user.id}")
    
    try:
        # Check if token is expired and refresh if needed
        if integration.token_expiry and integration.token_expiry < datetime.now():
            logger.info(f"Access token expired, refreshing for user {user.id}")
            success = await refresh_access_token(db, integration)
            if not success:
                return {
                    "status": "error",
                    "error": "Failed to refresh access token",
                    "items_synced": 0,
                    "last_sync": integration.last_sync,
                }
        
        # In a real implementation, we would use the Google Calendar API client
        # to fetch events and create tasks from them
        
        # Mock implementation to demonstrate structure
        
        # 1. Get calendar config from integration settings
        calendar_ids = integration.config.get("calendar_ids", ["primary"])
        time_min = datetime.now().isoformat() + "Z"
        time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        
        # 2. Use a proper API client to make requests
        # Mock request and response
        events = [
            {
                "id": "event1",
                "summary": "Important Meeting",
                "description": "Discuss project timeline",
                "start": {"dateTime": (datetime.now() + timedelta(days=2)).isoformat()},
                "end": {"dateTime": (datetime.now() + timedelta(days=2, hours=1)).isoformat()},
            },
            {
                "id": "event2",
                "summary": "Project Deadline",
                "description": "Submit final deliverables",
                "start": {"dateTime": (datetime.now() + timedelta(days=5)).isoformat()},
                "end": {"dateTime": (datetime.now() + timedelta(days=5, hours=2)).isoformat()},
            }
        ]
        
        # 3. Create tasks from events
        items_synced = 0
        for event in events:
            # Check if this event already has a task
            existing_task = db.query(Task).filter(
                Task.user_id == user.id,
                Task.custom_metadata.contains({"google_calendar_event_id": event["id"]})
            ).first()
            
            if existing_task:
                # Update existing task
                due_date = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                
                # Calculate estimated duration in minutes
                start_time = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                duration_minutes = int((end_time - start_time).total_seconds() / 60)
                
                task_update = TaskUpdate(
                    title=event["summary"],
                    description=event.get("description", ""),
                    due_date=due_date,
                    estimated_minutes=duration_minutes
                )
                
                for field, value in task_update.dict(exclude_unset=True).items():
                    setattr(existing_task, field, value)
                
                existing_task.custom_metadata["google_calendar_last_sync"] = datetime.now().isoformat()
                db.add(existing_task)
            
            else:
                # Create new task
                due_date = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                
                # Calculate estimated duration in minutes
                start_time = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                duration_minutes = int((end_time - start_time).total_seconds() / 60)
                
                # Get or create calendar tag
                calendar_tag = db.query(TaskTag).filter(
                    TaskTag.name == "Google Calendar",
                    (TaskTag.user_id == user.id) | (TaskTag.is_system == True)
                ).first()
                
                if not calendar_tag:
                    calendar_tag = TaskTag(
                        name="Google Calendar", 
                        color="#4285F4",
                        user_id=user.id
                    )
                    db.add(calendar_tag)
                    db.flush()
                
                # Create task
                new_task = Task(
                    title=event["summary"],
                    description=event.get("description", ""),
                    status="todo",
                    priority="medium",
                    due_date=due_date,
                    estimated_minutes=duration_minutes,
                    user_id=user.id,
                    custom_metadata={
                        "google_calendar_event_id": event["id"],
                        "google_calendar_last_sync": datetime.now().isoformat()
                    }
                )
                
                db.add(new_task)
                db.flush()
                
                # Add tag
                new_task.tags.append(calendar_tag)
            
            items_synced += 1
        
        # Update integration last_sync time
        integration.last_sync = datetime.now()
        db.add(integration)
        db.commit()
        
        return {
            "status": "success",
            "items_synced": items_synced,
            "last_sync": integration.last_sync,
        }
        
    except Exception as e:
        logger.error(f"Error syncing with Google Calendar: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "items_synced": 0,
            "last_sync": integration.last_sync,
        }


async def sync_with_todoist(
    db: Session, 
    integration: Integration,
    user: User,
) -> Dict[str, Any]:
    """
    Sync tasks with Todoist.
    
    Args:
        db: Database session
        integration: Todoist integration
        user: User
        
    Returns:
        Sync results
    """
    logger.info(f"Syncing with Todoist for user {user.id}")
    
    try:
        # Check if token is expired and refresh if needed
        if integration.token_expiry and integration.token_expiry < datetime.now():
            logger.info(f"Access token expired, refreshing for user {user.id}")
            success = await refresh_access_token(db, integration)
            if not success:
                return {
                    "status": "error",
                    "error": "Failed to refresh access token",
                    "items_synced": 0,
                    "last_sync": integration.last_sync,
                }
        
        # In a real implementation, we would use the Todoist API
        # to fetch tasks and sync them with our system
        
        # Mock implementation to demonstrate structure
        
        # 1. Get project config from integration settings
        project_ids = integration.config.get("project_ids", [])
        
        # 2. Use a proper API client to make requests
        # Mock request and response
        todoist_tasks = [
            {
                "id": "task1",
                "content": "Prepare presentation",
                "description": "Create slides for the monthly meeting",
                "due": {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")},
                "priority": 3,  # Todoist priority (1=low to 4=high)
                "project_id": "project1"
            },
            {
                "id": "task2",
                "content": "Review code PR",
                "description": "Check the new feature implementation",
                "due": {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                "priority": 4,  # Todoist priority (1=low to 4=high)
                "project_id": "project2"
            }
        ]
        
        # 3. Create tasks from Todoist tasks
        items_synced = 0
        for todoist_task in todoist_tasks:
            # Check if this Todoist task already has a corresponding task
            existing_task = db.query(Task).filter(
                Task.user_id == user.id,
                Task.custom_metadata.contains({"todoist_task_id": todoist_task["id"]})
            ).first()
            
            # Map Todoist priority to our priority
            priority_map = {1: "low", 2: "medium", 3: "high", 4: "urgent"}
            task_priority = priority_map.get(todoist_task["priority"], "medium")
            
            # Parse due date
            due_date = None
            if todoist_task.get("due") and todoist_task["due"].get("date"):
                due_date = datetime.strptime(todoist_task["due"]["date"], "%Y-%m-%d")
            
            if existing_task:
                # Update existing task
                task_update = TaskUpdate(
                    title=todoist_task["content"],
                    description=todoist_task.get("description", ""),
                    priority=task_priority,
                    due_date=due_date
                )
                
                for field, value in task_update.dict(exclude_unset=True).items():
                    setattr(existing_task, field, value)
                
                existing_task.custom_metadata["todoist_last_sync"] = datetime.now().isoformat()
                db.add(existing_task)
            
            else:
                # Get or create Todoist tag
                todoist_tag = db.query(TaskTag).filter(
                    TaskTag.name == "Todoist",
                    (TaskTag.user_id == user.id) | (TaskTag.is_system == True)
                ).first()
                
                if not todoist_tag:
                    todoist_tag = TaskTag(
                        name="Todoist", 
                        color="#E44332",
                        user_id=user.id
                    )
                    db.add(todoist_tag)
                    db.flush()
                
                # Create task
                new_task = Task(
                    title=todoist_task["content"],
                    description=todoist_task.get("description", ""),
                    status="todo",
                    priority=task_priority,
                    due_date=due_date,
                    user_id=user.id,
                    custom_metadata={
                        "todoist_task_id": todoist_task["id"],
                        "todoist_project_id": todoist_task["project_id"],
                        "todoist_last_sync": datetime.now().isoformat()
                    }
                )
                
                db.add(new_task)
                db.flush()
                
                # Add tag
                new_task.tags.append(todoist_tag)
            
            items_synced += 1
        
        # Update integration last_sync time
        integration.last_sync = datetime.now()
        db.add(integration)
        db.commit()
        
        return {
            "status": "success",
            "items_synced": items_synced,
            "last_sync": integration.last_sync,
        }
        
    except Exception as e:
        logger.error(f"Error syncing with Todoist: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "items_synced": 0,
            "last_sync": integration.last_sync,
        }


async def sync_with_github(
    db: Session, 
    integration: Integration,
    user: User,
) -> Dict[str, Any]:
    """
    Sync tasks with GitHub issues.
    
    Args:
        db: Database session
        integration: GitHub integration
        user: User
        
    Returns:
        Sync results
    """
    logger.info(f"Syncing with GitHub for user {user.id}")
    
    try:
        # Check if token is expired and refresh if needed
        if integration.token_expiry and integration.token_expiry < datetime.now():
            logger.info(f"Access token expired, refreshing for user {user.id}")
            success = await refresh_access_token(db, integration)
            if not success:
                return {
                    "status": "error",
                    "error": "Failed to refresh access token",
                    "items_synced": 0,
                    "last_sync": integration.last_sync,
                }
        
        # In a real implementation, we would use the GitHub API
        # to fetch issues and sync them with tasks
        
        # Mock implementation to demonstrate structure
        
        # 1. Get repository config from integration settings
        repos = integration.config.get("repositories", [])
        
        # 2. Use a proper API client to make requests
        # Mock request and response
        github_issues = [
            {
                "id": 12345,
                "number": 42,
                "title": "Fix navigation bug",
                "body": "The navigation menu doesn't work correctly on mobile",
                "state": "open",
                "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "html_url": "https://github.com/user/repo/issues/42",
                "repository": {
                    "name": "repo",
                    "full_name": "user/repo"
                },
                "labels": [
                    {"name": "bug", "color": "d73a4a"},
                    {"name": "priority-high", "color": "b60205"}
                ]
            },
            {
                "id": 12346,
                "number": 43,
                "title": "Add dark mode support",
                "body": "Implement a dark mode theme option",
                "state": "open",
                "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "html_url": "https://github.com/user/repo/issues/43",
                "repository": {
                    "name": "repo",
                    "full_name": "user/repo"
                },
                "labels": [
                    {"name": "enhancement", "color": "a2eeef"},
                    {"name": "good first issue", "color": "7057ff"}
                ]
            }
        ]
        
        # 3. Create tasks from GitHub issues
        items_synced = 0
        for issue in github_issues:
            # Check if this GitHub issue already has a corresponding task
            existing_task = db.query(Task).filter(
                Task.user_id == user.id,
                Task.custom_metadata.contains({"github_issue_id": str(issue["id"])})
            ).first()
            
            # Determine priority based on labels
            priority = "medium"  # Default
            for label in issue["labels"]:
                if "priority" in label["name"].lower():
                    if "high" in label["name"].lower() or "urgent" in label["name"].lower():
                        priority = "high"
                    elif "critical" in label["name"].lower():
                        priority = "urgent"
            
            # Create task description with issue details
            description = f"{issue['body']}\n\nGitHub Issue: {issue['html_url']}\nRepository: {issue['repository']['full_name']}\nIssue #{issue['number']}"
            
            if existing_task:
                # Update existing task
                task_update = TaskUpdate(
                    title=issue["title"],
                    description=description,
                    priority=priority,
                    status="todo" if issue["state"] == "open" else "done"
                )
                
                for field, value in task_update.dict(exclude_unset=True).items():
                    setattr(existing_task, field, value)
                
                existing_task.custom_metadata["github_last_sync"] = datetime.now().isoformat()
                existing_task.custom_metadata["github_updated_at"] = issue["updated_at"]
                db.add(existing_task)
            
            else:
                # Get or create GitHub tag
                github_tag = db.query(TaskTag).filter(
                    TaskTag.name == "GitHub",
                    (TaskTag.user_id == user.id) | (TaskTag.is_system == True)
                ).first()
                
                if not github_tag:
                    github_tag = TaskTag(
                        name="GitHub", 
                        color="#2da44e",
                        user_id=user.id
                    )
                    db.add(github_tag)
                    db.flush()
                
                # Create label tags
                label_tags = []
                for label in issue["labels"]:
                    label_name = f"gh:{label['name']}"
                    label_tag = db.query(TaskTag).filter(
                        TaskTag.name == label_name,
                        TaskTag.user_id == user.id
                    ).first()
                    
                    if not label_tag:
                        label_tag = TaskTag(
                            name=label_name,
                            color=f"#{label['color']}",
                            user_id=user.id
                        )
                        db.add(label_tag)
                        db.flush()
                    
                    label_tags.append(label_tag)
                
                # Create task
                new_task = Task(
                    title=issue["title"],
                    description=description,
                    status="todo" if issue["state"] == "open" else "done",
                    priority=priority,
                    user_id=user.id,
                    custom_metadata={
                        "github_issue_id": str(issue["id"]),
                        "github_repo": issue["repository"]["full_name"],
                        "github_issue_number": issue["number"],
                        "github_issue_url": issue["html_url"],
                        "github_created_at": issue["created_at"],
                        "github_updated_at": issue["updated_at"],
                        "github_last_sync": datetime.now().isoformat()
                    }
                )
                
                db.add(new_task)
                db.flush()
                
                # Add tags
                new_task.tags.append(github_tag)
                for tag in label_tags:
                    new_task.tags.append(tag)
            
            items_synced += 1
        
        # Update integration last_sync time
        integration.last_sync = datetime.now()
        db.add(integration)
        db.commit()
        
        return {
            "status": "success",
            "items_synced": items_synced,
            "last_sync": integration.last_sync,
        }
        
    except Exception as e:
        logger.error(f"Error syncing with GitHub: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "items_synced": 0,
            "last_sync": integration.last_sync,
        }
