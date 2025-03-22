"""
Tests for gamification features.
"""

import pytest
from datetime import datetime, timedelta

from app.models.gamification import Achievement, UserAchievement, UserStats, UserStreak
from app.services.gamification_service import (
    get_user_stats, 
    get_user_streak, 
    update_achievement_progress,
    update_streak,
    award_points
)

def test_get_user_stats(db_session):
    """Test getting user stats."""
    # Test with a user that doesn't have stats yet
    stats = get_user_stats(db_session, 999)
    assert stats is not None
    assert stats.user_id == 999
    assert stats.points == 0
    assert stats.level == 1
    assert stats.tasks_completed == 0
    
    # Test with existing stats
    existing_stats = UserStats(
        user_id=1000,
        points=100,
        level=2,
        tasks_completed=5,
        tasks_completed_on_time=3,
        current_streak=2,
        longest_streak=3,
        focus_time_minutes=60
    )
    db_session.add(existing_stats)
    db_session.commit()
    
    retrieved_stats = get_user_stats(db_session, 1000)
    assert retrieved_stats is not None
    assert retrieved_stats.user_id == 1000
    assert retrieved_stats.points == 100
    assert retrieved_stats.level == 2
    assert retrieved_stats.tasks_completed == 5
    assert retrieved_stats.tasks_completed_on_time == 3
    assert retrieved_stats.current_streak == 2
    assert retrieved_stats.longest_streak == 3
    assert retrieved_stats.focus_time_minutes == 60


def test_get_user_streak(db_session):
    """Test getting user streak."""
    # Test with a user that doesn't have streak yet
    streak = get_user_streak(db_session, 999)
    assert streak is not None
    assert streak.user_id == 999
    assert streak.current_streak == 0
    assert streak.longest_streak == 0
    
    # Test with existing streak
    existing_streak = UserStreak(
        user_id=1000,
        current_streak=3,
        longest_streak=5,
        last_activity_date=datetime.now() - timedelta(days=1),
        streak_start_date=datetime.now() - timedelta(days=3)
    )
    db_session.add(existing_streak)
    db_session.commit()
    
    retrieved_streak = get_user_streak(db_session, 1000)
    assert retrieved_streak is not None
    assert retrieved_streak.user_id == 1000
    assert retrieved_streak.current_streak == 3
    assert retrieved_streak.longest_streak == 5


def test_update_achievement_progress(db_session):
    """Test updating achievement progress."""
    # Create a test achievement
    achievement = Achievement(
        name="Test Achievement",
        description="A test achievement",
        points=10,
        icon="test-icon",
        requirement_type="task_count",
        requirement_value=5,
        level=1,
        is_system=True
    )
    db_session.add(achievement)
    db_session.commit()
    
    # Test updating progress (not completed)
    user_achievement = update_achievement_progress(
        db_session,
        user_id=999,
        achievement_id=achievement.id,
        progress=0.5
    )
    
    assert user_achievement.user_id == 999
    assert user_achievement.achievement_id == achievement.id
    assert user_achievement.progress == 0.5
    assert user_achievement.unlocked_at is None
    
    # Test completing achievement
    user_achievement = update_achievement_progress(
        db_session,
        user_id=999,
        achievement_id=achievement.id,
        progress=1.0
    )
    
    assert user_achievement.progress == 1.0
    assert user_achievement.unlocked_at is not None
    
    # Check that points were awarded
    stats = get_user_stats(db_session, 999)
    assert stats.points == 10


def test_update_streak(db_session):
    """Test updating user streak."""
    # Create initial streak
    user_id = 999
    streak = get_user_streak(db_session, user_id)
    assert streak.current_streak == 0
    
    # Update streak for the first time
    updated_streak = update_streak(db_session, user_id)
    assert updated_streak.current_streak == 1
    assert updated_streak.longest_streak == 1
    assert updated_streak.last_activity_date is not None
    
    # Update streak again on the same day (should not change)
    updated_streak = update_streak(db_session, user_id)
    assert updated_streak.current_streak == 1
    assert updated_streak.longest_streak == 1
    
    # Manually set last activity to yesterday to simulate consecutive day
    updated_streak.last_activity_date = datetime.now() - timedelta(days=1)
    db_session.add(updated_streak)
    db_session.commit()
    
    # Update streak (should increment)
    updated_streak = update_streak(db_session, user_id)
    assert updated_streak.current_streak == 2
    assert updated_streak.longest_streak == 2
    
    # Manually set last activity to 2 days ago to simulate streak break
    updated_streak.last_activity_date = datetime.now() - timedelta(days=2)
    db_session.add(updated_streak)
    db_session.commit()
    
    # Update streak (should reset to 1)
    updated_streak = update_streak(db_session, user_id)
    assert updated_streak.current_streak == 1
    assert updated_streak.longest_streak == 2  # Longest remains at 2


def test_award_points(db_session):
    """Test awarding points to a user."""
    user_id = 999
    stats = get_user_stats(db_session, user_id)
    initial_points = stats.points
    
    # Award points
    result = award_points(db_session, user_id, 50, "Completed a difficult task")
    
    assert result["success"] is True
    assert result["points_added"] == 50
    assert result["total_points"] == initial_points + 50
    
    # Check that the stats were updated
    updated_stats = get_user_stats(db_session, user_id)
    assert updated_stats.points == initial_points + 50