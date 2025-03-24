"""
Gamification service for the OneTask API.

This module handles gamification features like achievements, 
user statistics, streaks, and leaderboards.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.gamification import Achievement, UserAchievement, UserStats, UserStreak
from app.models.task import Task
from app.models.user import User
from app.schemas.gamification import LeaderboardEntry

# Configure logging
logger = logging.getLogger(__name__)


def get_user_stats(db: Session, user_id: int) -> UserStats:
    """
    Get a user's statistics.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User stats
    """
    # Get or create user stats
    stats = db.query(UserStats).filter(
        UserStats.user_id == user_id
    ).first()
    
    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return stats


def get_user_streak(db: Session, user_id: int) -> UserStreak:
    """
    Get a user's streak information.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User streak
    """
    # Get or create user streak
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user_id
    ).first()
    
    if not streak:
        streak = UserStreak(
            user_id=user_id,
            current_streak=0,
            longest_streak=0
        )
        db.add(streak)
        db.commit()
        db.refresh(streak)
    
    return streak


def get_available_achievements(db: Session, workspace_id: Optional[int] = None) -> List[Achievement]:
    """
    Get a list of available achievements.
    
    Args:
        db: Database session
        workspace_id: Optional workspace ID for workspace-specific achievements
        
    Returns:
        List of achievements
    """
    query = db.query(Achievement).filter(
        Achievement.is_system == True
    )
    
    if workspace_id:
        # Also include workspace-specific achievements
        query = query.union(
            db.query(Achievement).filter(
                Achievement.workspace_id == workspace_id
            )
        )
    
    return query.order_by(Achievement.level, Achievement.name).all()


def get_user_achievements(db: Session, user_id: int) -> List[UserAchievement]:
    """
    Get a user's achievements.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of user achievements
    """
    return db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()


def update_achievement_progress(
    db: Session,
    user_id: int,
    achievement_id: int,
    progress: float,
    unlock: bool = False
) -> UserAchievement:
    """
    Update a user's progress on an achievement.
    
    Args:
        db: Database session
        user_id: User ID
        achievement_id: Achievement ID
        progress: Progress value (0.0 to 1.0)
        unlock: Whether to unlock the achievement
        
    Returns:
        Updated user achievement
    """
    # Get or create user achievement
    user_achievement = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if not user_achievement:
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            progress=0.0,
            data={}
        )
    
    # Update progress
    user_achievement.progress = min(1.0, max(0.0, progress))
    
    # If unlocking or progress is complete, set unlocked_at
    if unlock or user_achievement.progress >= 1.0:
        if not user_achievement.unlocked_at:
            user_achievement.unlocked_at = datetime.now()
            
            # Award points to user stats
            achievement = db.query(Achievement).get(achievement_id)
            if achievement:
                stats = get_user_stats(db, user_id)
                stats.points += achievement.points
                db.add(stats)
    
    db.add(user_achievement)
    db.commit()
    db.refresh(user_achievement)
    
    return user_achievement


async def check_achievements(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Check and update achievements for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Results of achievement checks
    """
    # Import here to avoid circular imports
    from app.websockets.notification_handlers import (
        send_achievement_notification,
        send_achievement_progress_notification
    )
    
    # Get user stats
    stats = get_user_stats(db, user_id)
    
    # Get all achievements
    achievements = get_available_achievements(db)
    
    # Check each achievement for progress
    unlocked = []
    updated = []
    
    for achievement in achievements:
        progress = 0.0
        data = {}
        should_unlock = False
        
        # Calculate progress based on achievement type
        if achievement.requirement_type == "task_count":
            current = stats.tasks_completed
            target = achievement.requirement_value
            progress = min(1.0, current / target) if target > 0 else 0.0
            data = {"current": current, "target": target}
            
        elif achievement.requirement_type == "streak":
            current = stats.longest_streak
            target = achievement.requirement_value
            progress = min(1.0, current / target) if target > 0 else 0.0
            data = {"current": current, "target": target}
            
        elif achievement.requirement_type == "on_time_completion":
            if stats.tasks_completed > 0:
                ratio = stats.tasks_completed_on_time / stats.tasks_completed
                target = achievement.requirement_value / 100  # Convert percentage to ratio
                progress = min(1.0, ratio / target) if target > 0 else 0.0
                data = {
                    "current": stats.tasks_completed_on_time,
                    "total": stats.tasks_completed,
                    "ratio": ratio,
                    "target_ratio": target
                }
                
        elif achievement.requirement_type == "focus_time":
            current = stats.focus_time_minutes
            target = achievement.requirement_value
            progress = min(1.0, current / target) if target > 0 else 0.0
            data = {"current": current, "target": target}
        
        # Get previous achievement progress to detect newly unlocked or progress updates
        previous_achievement = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id
        ).first()
        
        previous_progress = previous_achievement.progress if previous_achievement else 0.0
        was_previously_unlocked = previous_achievement and previous_achievement.unlocked_at is not None
        
        # Update achievement progress
        user_achievement = update_achievement_progress(
            db, user_id, achievement.id, progress
        )
        
        # Check if newly unlocked (unlocked during this check)
        newly_unlocked = user_achievement.unlocked_at and progress >= 1.0 and not was_previously_unlocked
        
        if newly_unlocked:
            # Achievement was just unlocked
            unlocked.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "points": achievement.points,
                "icon": achievement.icon
            })
            
            # Send WebSocket notification for achievement unlock
            await send_achievement_notification(
                db, user_id, achievement.id, achievement.points
            )
            
        elif progress > 0 and progress > previous_progress:
            # Achievement progress was updated
            updated.append({
                "id": achievement.id,
                "name": achievement.name,
                "progress": progress,
                "data": data
            })
            
            # Send WebSocket notification for achievement progress update if it's a milestone
            await send_achievement_progress_notification(
                db, user_id, achievement.id, progress
            )
    
    return {
        "unlocked": unlocked,
        "updated": updated,
        "total_achievements": len(achievements),
        "total_points": stats.points
    }


async def update_streak(db: Session, user_id: int) -> UserStreak:
    """
    Update a user's streak.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Updated user streak
    """
    # Import here to avoid circular imports
    from app.websockets.notification_handlers import send_streak_notification
    
    # Get user streak
    streak = get_user_streak(db, user_id)
    old_streak = streak.current_streak
    
    # Calculate streak state
    today = datetime.now().date()
    if not streak.last_activity_date:
        # First activity
        streak.current_streak = 1
        streak.longest_streak = 1
        streak.last_activity_date = datetime.now()
        streak.streak_start_date = datetime.now()
    else:
        last_date = streak.last_activity_date.date()
        days_difference = (today - last_date).days
        
        if days_difference == 0:
            # Already recorded activity today
            pass
        elif days_difference == 1:
            # Streak continues
            streak.current_streak += 1
            streak.last_activity_date = datetime.now()
            
            # Update longest streak if needed
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        elif days_difference > 1:
            # Streak broken
            streak.current_streak = 1
            streak.last_activity_date = datetime.now()
            streak.streak_start_date = datetime.now()
    
    # Update streak
    streak.updated_at = datetime.now()
    db.add(streak)
    
    # Update user stats
    stats = get_user_stats(db, user_id)
    stats.current_streak = streak.current_streak
    stats.longest_streak = streak.longest_streak
    db.add(stats)
    
    db.commit()
    db.refresh(streak)
    
    # Send streak notification if streak increased
    if streak.current_streak > old_streak:
        # Check if this is a milestone streak (3, 7, 14, 30 days)
        milestone_streaks = [3, 7, 14, 30, 60, 90, 180, 365]
        is_milestone = streak.current_streak in milestone_streaks
        
        # Send the streak notification
        await send_streak_notification(
            db, user_id, streak.current_streak, is_milestone
        )
        
        # Check achievements after streak update
        await check_achievements(db, user_id)
    
    return streak


def get_leaderboard(
    db: Session, 
    limit: int = 10, 
    workspace_id: Optional[int] = None
) -> List[LeaderboardEntry]:
    """
    Get a leaderboard of users.
    
    Args:
        db: Database session
        limit: Maximum number of entries to return
        workspace_id: Optional workspace ID for workspace-specific leaderboard
        
    Returns:
        List of leaderboard entries
    """
    if workspace_id:
        # Get members of the workspace
        from app.models.workspace import WorkspaceMember
        member_ids = db.query(WorkspaceMember.user_id).filter(
            WorkspaceMember.workspace_id == workspace_id
        ).all()
        member_ids = [m[0] for m in member_ids]
        
        # Get stats for these members
        leaderboard_data = db.query(
            UserStats.user_id,
            User.username,
            UserStats.points,
            UserStats.level,
            UserStats.tasks_completed,
            UserStats.current_streak,
            UserStats.longest_streak
        ).join(
            User, User.id == UserStats.user_id
        ).filter(
            UserStats.user_id.in_(member_ids)
        ).order_by(
            desc(UserStats.points),
            desc(UserStats.tasks_completed)
        ).limit(limit).all()
    else:
        # Global leaderboard
        leaderboard_data = db.query(
            UserStats.user_id,
            User.username,
            UserStats.points,
            UserStats.level,
            UserStats.tasks_completed,
            UserStats.current_streak,
            UserStats.longest_streak
        ).join(
            User, User.id == UserStats.user_id
        ).order_by(
            desc(UserStats.points),
            desc(UserStats.tasks_completed)
        ).limit(limit).all()
    
    # Convert to schema
    leaderboard = []
    for entry in leaderboard_data:
        leaderboard.append(LeaderboardEntry(
            user_id=entry[0],
            username=entry[1],
            points=entry[2],
            level=entry[3],
            tasks_completed=entry[4],
            current_streak=entry[5],
            longest_streak=entry[6]
        ))
    
    return leaderboard


def award_points(db: Session, user_id: int, points: int, reason: str) -> Dict[str, Any]:
    """
    Award points to a user.
    
    Args:
        db: Database session
        user_id: User ID
        points: Number of points to award
        reason: Reason for the points
        
    Returns:
        Updated user stats
    """
    # Get user stats
    stats = get_user_stats(db, user_id)
    
    # Award points
    stats.points += points
    
    # Calculate level (simplified example)
    level_thresholds = [0, 100, 300, 600, 1000, 1500, 2500, 4000, 6000, 10000]
    new_level = 1
    
    for i, threshold in enumerate(level_thresholds):
        if stats.points >= threshold:
            new_level = i + 1
    
    # Check for level up
    level_up = new_level > stats.level
    stats.level = new_level
    
    db.add(stats)
    db.commit()
    db.refresh(stats)
    
    return {
        "success": True,
        "points_added": points,
        "total_points": stats.points,
        "level": stats.level,
        "level_up": level_up,
        "reason": reason
    }