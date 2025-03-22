"""
Pydantic schemas for the OneTask API.

This module exports all schemas for easy imports elsewhere in the application.
"""

from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.task import (
    Task, TaskCreate, TaskUpdate, TaskWithSubtasks, SubTask, 
    SubTaskCreate, SubTaskUpdate, TaskTag, TaskTagCreate, 
    TaskTagUpdate, TaskBreakdown, TaskFocusMode
)
from app.schemas.workspace import (
    Workspace, WorkspaceCreate, WorkspaceUpdate, WorkspaceWithMembers,
    WorkspaceMember, WorkspaceMemberCreate, WorkspaceMemberUpdate, WorkspaceMemberResponse
)
from app.schemas.integration import (
    Integration, IntegrationCreate, IntegrationUpdate, IntegrationSync
)
from app.schemas.subscription import (
    Subscription, SubscriptionCreate, SubscriptionUpdate,
    SubscriptionPlan
)
from app.schemas.notification import (
    Notification, NotificationCreate, NotificationUpdate,
    NotificationSettings, NotificationSettingsUpdate
)
from app.schemas.gamification import (
    UserStats, UserAchievement, Achievement, UserStreak, LeaderboardEntry
)
from app.schemas.support import (
    SupportTicket, SupportTicketCreate, SupportTicketUpdate
)
from app.schemas.theme import (
    Theme, ThemeCreate, ThemeUpdate
)
from app.schemas.accessibility import (
    AccessibilitySettings, AccessibilitySettingsUpdate
)
from app.schemas.token import Token, TokenPayload