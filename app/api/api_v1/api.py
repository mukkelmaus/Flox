"""
API router for the OneTask API.

This module registers all API endpoints under the appropriate prefixes.
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    users, tasks, login, workspaces, 
    notifications, integrations, ai
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])