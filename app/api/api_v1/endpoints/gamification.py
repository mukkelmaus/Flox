"""
Gamification endpoints for the OneTask API.

This module handles endpoints for achievements, streaks, and user stats.
"""

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import gamification_service

router = APIRouter()


@router.get("/stats", response_model=schemas.UserStats)
def get_user_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the current user's stats.
    """
    return gamification_service.get_user_stats(db, current_user.id)


@router.get("/streaks", response_model=schemas.UserStreak)
def get_user_streak(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the current user's streak information.
    """
    return gamification_service.get_user_streak(db, current_user.id)


@router.post("/streaks/update", response_model=schemas.UserStreak)
def update_streak(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update the current user's streak.
    """
    return gamification_service.update_streak(db, current_user.id)


@router.get("/achievements", response_model=List[schemas.Achievement])
def get_available_achievements(
    workspace_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get available achievements.
    
    Optionally filter by workspace ID for workspace-specific achievements.
    """
    return gamification_service.get_available_achievements(db, workspace_id)


@router.get("/achievements/user", response_model=List[schemas.UserAchievement])
def get_user_achievements(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the current user's achievements.
    """
    return gamification_service.get_user_achievements(db, current_user.id)


@router.post("/achievements/check", response_model=Dict[str, Any])
def check_achievements(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Check and update achievements for the current user.
    
    Returns newly unlocked achievements, if any.
    """
    return gamification_service.check_achievements(db, current_user.id)


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    workspace_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the leaderboard.
    
    Optionally filter by workspace ID for workspace-specific leaderboard.
    """
    return gamification_service.get_leaderboard(db, limit, workspace_id)