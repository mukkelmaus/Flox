from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    tasks,
    users,
    workspaces,
    ai,
    themes,
    support,
    subscriptions,
    notifications,
    integrations,
    gamification,
    accessibility,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(accessibility.router, prefix="/accessibility", tags=["accessibility"])
