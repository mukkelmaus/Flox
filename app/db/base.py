# Import all models to ensure they are registered with SQLAlchemy
from app.db.base_class import Base
from app.models.user import User
from app.models.task import Task, TaskTag, SubTask
from app.models.workspace import Workspace, WorkspaceMember
from app.models.theme import Theme
from app.models.support import SupportTicket
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.notification import Notification, NotificationSettings
from app.models.integration import Integration
from app.models.gamification import UserStats, UserAchievement, Achievement, UserStreak
from app.models.accessibility import AccessibilitySettings, ADHDProfile
