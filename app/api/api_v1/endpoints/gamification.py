"""
Gamification API endpoints for the OneTask API.

This module provides endpoints for gamification features like achievements,
user statistics, streaks, and leaderboards.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.gamification import (
    Achievement,
    LeaderboardEntry,
    UserAchievement,
    UserStats,
    UserStreak,
)
from app.services.gamification_service import (
    get_available_achievements,
    get_leaderboard,
    get_user_achievements,
    get_user_stats,
    get_user_streak,
    update_streak,
)

router = APIRouter()


@router.get("/stats", response_model=UserStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserStats:
    """
    Get the current user's gamification stats.
    """
    return get_user_stats(db, current_user.id)


@router.get("/streak", response_model=UserStreak)
async def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserStreak:
    """
    Get the current user's streak information.
    """
    return get_user_streak(db, current_user.id)


@router.post("/streak/update", response_model=UserStreak)
async def update_user_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserStreak:
    """
    Update the current user's streak.
    This should be called whenever a user completes a task or performs
    another action that should count towards their streak.
    """
    return await update_streak(db, current_user.id)


@router.get("/achievements", response_model=List[Achievement])
async def get_all_achievements(
    workspace_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Achievement]:
    """
    Get all available achievements.
    
    Parameters:
    - workspace_id: Optional workspace ID for workspace-specific achievements
    """
    return get_available_achievements(db, workspace_id)


@router.get("/achievements/user", response_model=List[UserAchievement])
async def get_user_achievement_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[UserAchievement]:
    """
    Get the current user's achievement progress.
    """
    return get_user_achievements(db, current_user.id)


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_user_leaderboard(
    workspace_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[LeaderboardEntry]:
    """
    Get the user leaderboard.
    
    Parameters:
    - workspace_id: Optional workspace ID for workspace-specific leaderboard
    - limit: Maximum number of entries to return (default: 10)
    """
    return get_leaderboard(db, limit, workspace_id)


@router.post("/achievements/check", response_model=Dict[str, Any])
async def check_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Check and update achievements for the current user.
    
    This endpoint triggers a manual check of all achievements for the user
    and updates their progress. This is useful for testing or when achievements
    might not have been properly updated during normal operation.
    """
    from app.services.gamification_service import check_achievements
    return await check_achievements(db, current_user.id)


@router.post("/points/award", response_model=Dict[str, Any])
async def award_user_points(
    points_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Award points to the current user.
    
    Parameters:
    - points: Number of points to award
    - reason: Reason for the points
    """
    from app.services.gamification_service import award_points
    
    points = points_data.get("points", 10)
    reason = points_data.get("reason", "Manual points award")
    
    return await award_points(db, current_user.id, points, reason)