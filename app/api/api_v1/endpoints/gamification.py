from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gamification import (
    UserAchievement,
    UserStats,
    LeaderboardEntry,
    UserStreak,
)

router = APIRouter()


@router.get("/stats", response_model=UserStats)
def read_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's gamification stats.
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    from app.models.gamification import UserStats as UserStatsModel
    
    # Get or create user stats
    user_stats = db.query(UserStatsModel).filter(
        UserStatsModel.user_id == current_user.id
    ).first()
    
    if not user_stats:
        # Create default stats for new users
        user_stats = UserStatsModel(
            user_id=current_user.id,
            points=0,
            level=1,
            tasks_completed=0,
            current_streak=0,
            longest_streak=0,
        )
        
        db.add(user_stats)
        db.commit()
        db.refresh(user_stats)
    
    return user_stats


@router.get("/achievements", response_model=List[UserAchievement])
def read_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's achievements.
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    from app.models.gamification import UserAchievement as UserAchievementModel
    
    achievements = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == current_user.id
    ).all()
    
    return achievements


@router.get("/streak", response_model=UserStreak)
def read_user_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's current streak information.
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    from app.models.gamification import UserStreak as UserStreakModel
    
    streak = db.query(UserStreakModel).filter(
        UserStreakModel.user_id == current_user.id
    ).first()
    
    if not streak:
        # Create default streak for new users
        streak = UserStreakModel(
            user_id=current_user.id,
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
        )
        
        db.add(streak)
        db.commit()
        db.refresh(streak)
    
    return streak


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def read_leaderboard(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the global leaderboard.
    
    - **limit**: Number of top users to return
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    from app.models.gamification import UserStats as UserStatsModel
    
    # Get top users by points
    leaderboard = (
        db.query(UserStatsModel, User)
        .join(User, UserStatsModel.user_id == User.id)
        .order_by(UserStatsModel.points.desc())
        .limit(limit)
        .all()
    )
    
    result = []
    for stats, user in leaderboard:
        result.append({
            "user_id": user.id,
            "username": user.username,
            "points": stats.points,
            "level": stats.level,
            "tasks_completed": stats.tasks_completed,
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
        })
    
    return result


@router.get("/workspace-leaderboard/{workspace_id}", response_model=List[LeaderboardEntry])
def read_workspace_leaderboard(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the leaderboard for a specific workspace.
    
    - **workspace_id**: Workspace ID
    - **limit**: Number of top users to return
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    # Check if user is a member of this workspace
    from app.models.workspace import WorkspaceMember
    
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )
    
    # Get workspace members
    workspace_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()
    
    member_ids = [m.user_id for m in workspace_members]
    
    from app.models.gamification import UserStats as UserStatsModel
    
    # Get top users by points
    leaderboard = (
        db.query(UserStatsModel, User)
        .join(User, UserStatsModel.user_id == User.id)
        .filter(UserStatsModel.user_id.in_(member_ids))
        .order_by(UserStatsModel.points.desc())
        .limit(limit)
        .all()
    )
    
    result = []
    for stats, user in leaderboard:
        result.append({
            "user_id": user.id,
            "username": user.username,
            "points": stats.points,
            "level": stats.level,
            "tasks_completed": stats.tasks_completed,
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
        })
    
    return result


@router.get("/progress", response_model=Dict[str, Any])
def read_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's progress information, including level progress and available achievements.
    """
    if not settings.ENABLE_GAMIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gamification features are disabled",
        )
    
    from app.models.gamification import UserStats as UserStatsModel
    from app.models.gamification import UserAchievement as UserAchievementModel
    from app.models.gamification import Achievement as AchievementModel
    
    # Get user stats
    user_stats = db.query(UserStatsModel).filter(
        UserStatsModel.user_id == current_user.id
    ).first()
    
    if not user_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User stats not found",
        )
    
    # Calculate level progress
    next_level_points = user_stats.level * 100  # Simple formula, can be adjusted
    points_needed = next_level_points - user_stats.points
    level_progress = (user_stats.points / next_level_points) * 100 if next_level_points > 0 else 0
    
    # Get user achievements
    user_achievements = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == current_user.id
    ).all()
    
    user_achievement_ids = [a.achievement_id for a in user_achievements]
    
    # Get all available achievements
    all_achievements = db.query(AchievementModel).all()
    
    achieved = []
    available = []
    
    for achievement in all_achievements:
        if achievement.id in user_achievement_ids:
            achieved.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "points": achievement.points,
                "icon": achievement.icon,
            })
        else:
            available.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "points": achievement.points,
                "icon": achievement.icon,
            })
    
    return {
        "current_level": user_stats.level,
        "current_points": user_stats.points,
        "next_level_points": next_level_points,
        "points_needed": points_needed,
        "level_progress": level_progress,
        "achievements": {
            "achieved": achieved,
            "available": available,
        },
    }
