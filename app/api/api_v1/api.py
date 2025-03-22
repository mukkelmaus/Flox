"""
API router for the OneTask API.

This module registers all API endpoints under the appropriate prefixes.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    tasks,
    workspaces,
    ai,
    integrations,
    subscriptions,
    notifications,
    gamification,
    accessibility,
    support,
    themes,
    login,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(accessibility.router, prefix="/accessibility", tags=["accessibility"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])