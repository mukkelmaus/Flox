from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class UserStatsBase(BaseModel):
    points: int = 0
    level: int = 1
    tasks_completed: int = 0
    tasks_completed_on_time: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    average_task_completion_time: Optional[float] = None
    focus_time_minutes: int = 0


class UserStats(UserStatsBase):
    id: int
    user_id: int
    last_updated: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class UserAchievementBase(BaseModel):
    achievement_id: int
    progress: float = 0.0
    data: Optional[Dict[str, Any]] = None


class UserAchievement(UserAchievementBase):
    id: int
    user_id: int
    unlocked_at: datetime
    
    class Config:
        orm_mode = True


class AchievementBase(BaseModel):
    name: str
    description: Optional[str] = None
    points: int = 0
    icon: Optional[str] = None
    requirement_type: str
    requirement_value: int
    level: int = 1
    is_system: bool = True
    workspace_id: Optional[int] = None


class Achievement(AchievementBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class UserStreakBase(BaseModel):
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    streak_start_date: Optional[datetime] = None


class UserStreak(UserStreakBase):
    id: int
    user_id: int
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    points: int
    level: int
    tasks_completed: int
    current_streak: int
    longest_streak: int
