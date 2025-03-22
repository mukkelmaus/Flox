import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.services.ai_service import break_down_task, generate_task_analysis


@pytest.mark.asyncio
async def test_ai_break_down_task(client, db_session, test_user, token_headers):
    """Test AI task breakdown endpoint."""
    # Create a test task
    from app.models.task import Task
    from tests.api.test_tasks import create_test_task
    
    task = create_test_task(db_session, test_user.id, "Complex Project")
    
    # Mock the AI service function to avoid actual API calls
    with patch("app.api.api_v1.endpoints.ai.break_down_task") as mock_break_down:
        # Create a mock return value
        mock_return = {
            "original_task": {
                "id": task.id,
                "title": task.title,
                "user_id": test_user.id
            },
            "subtasks": [
                {
                    "id": 101,
                    "title": "Research phase",
                    "user_id": test_user.id
                },
                {
                    "id": 102,
                    "title": "Implementation phase",
                    "user_id": test_user.id
                }
            ],
            "suggestions": "Split your work into smaller chunks for better focus."
        }
        mock_break_down.return_value = mock_return
        
        # Make the request
        response = await client.post(
            "/api/v1/ai/break-down-task/",
            json={"task_id": task.id},
            headers=token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "original_task" in data
        assert "subtasks" in data
        assert len(data["subtasks"]) > 0
        assert "suggestions" in data


@pytest.mark.asyncio
async def test_ai_analyze_tasks(client, db_session, test_user, token_headers):
    """Test AI task analysis endpoint."""
    # Create multiple test tasks
    from tests.api.test_tasks import create_test_task
    
    for i in range(5):
        create_test_task(db_session, test_user.id, f"Task {i}")
    
    # Mock the AI service function to avoid actual API calls
    with patch("app.api.api_v1.endpoints.ai.generate_task_analysis") as mock_analysis:
        # Create a mock return value
        mock_return = {
            "productivity_score": 85,
            "task_categories": {
                "work": 3,
                "personal": 2
            },
            "insights": [
                "You tend to complete work tasks faster than personal tasks",
                "Your productivity is highest on Mondays"
            ],
            "recommendations": [
                "Consider batching similar tasks together",
                "Schedule complex tasks during your peak energy times"
            ]
        }
        mock_analysis.return_value = mock_return
        
        # Make the request
        response = await client.post(
            "/api/v1/ai/analyze-tasks/",
            json={},
            headers=token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "productivity_score" in data
        assert "insights" in data
        assert "recommendations" in data


@pytest.mark.asyncio
async def test_ai_productivity_insights(client, db_session, test_user, token_headers):
    """Test AI productivity insights endpoint."""
    # Create multiple test tasks with different completion times
    from app.models.task import Task
    from tests.api.test_tasks import create_test_task
    
    for i in range(3):
        task = create_test_task(db_session, test_user.id, f"Completed Task {i}")
        # Mark as completed
        task.status = "done"
        task.completed_at = datetime.utcnow()
        db_session.commit()
    
    # Mock the AI service function to avoid actual API calls
    with patch("app.api.api_v1.endpoints.ai.generate_productivity_insights") as mock_insights:
        # Create a mock return value
        mock_return = {
            "productivity_trends": {
                "weekly_completion_rate": [5, 7, 4, 6, 8],
                "peak_productivity_days": ["Monday", "Thursday"]
            },
            "task_patterns": {
                "most_productive_category": "work",
                "least_productive_category": "admin"
            },
            "suggestions": [
                "You're most productive in the morning",
                "Consider delegating administrative tasks"
            ]
        }
        mock_insights.return_value = mock_return
        
        # Make the request
        response = await client.post(
            "/api/v1/ai/productivity-insights/",
            json={"days": 30},
            headers=token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "productivity_trends" in data
        assert "suggestions" in data