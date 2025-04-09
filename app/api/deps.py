"""
Dependencies for API endpoints.

This module contains dependencies used across API endpoints,
such as database session and user authentication.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.db.session import SessionLocal
from app.services import subscription_service

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_db() -> Generator:
    """
    Dependency for database session.
    
    Yields:
        Session: Database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Get the current authenticated user.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.sub).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Get the current active superuser.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    
    return current_user


def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Optional[models.Subscription]:
    """
    Get the current user's subscription.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Subscription or None if not found
    """
    return subscription_service.get_subscription(db, current_user.id)


def verify_premium_access(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    current_subscription: Optional[models.Subscription] = Depends(get_current_subscription),
) -> None:
    """
    Verify that the user has premium access.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        current_subscription: Current user's subscription
        
    Raises:
        HTTPException: If the user doesn't have premium access
    """
    if not subscription_service.check_feature_access(current_subscription, "premium", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a premium subscription"
        )


def verify_ai_access(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    current_subscription: Optional[models.Subscription] = Depends(get_current_subscription),
) -> None:
    """
    Verify that the user has access to AI features.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        current_subscription: Current user's subscription
        
    Raises:
        HTTPException: If the user doesn't have AI feature access
    """
    if not subscription_service.check_feature_access(current_subscription, "ai_features", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a subscription with AI features enabled"
        )


def verify_integration_access(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    current_subscription: Optional[models.Subscription] = Depends(get_current_subscription),
) -> None:
    """
    Verify that the user has access to integration features.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        current_subscription: Current user's subscription
        
    Raises:
        HTTPException: If the user doesn't have integration access
    """
    if not subscription_service.check_feature_access(current_subscription, "integrations", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a subscription with integrations enabled"
        )


def verify_analytics_access(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    current_subscription: Optional[models.Subscription] = Depends(get_current_subscription),
) -> None:
    """
    Verify that the user has access to analytics features.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        current_subscription: Current user's subscription
        
    Raises:
        HTTPException: If the user doesn't have analytics access
    """
    if not subscription_service.check_feature_access(current_subscription, "analytics", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a subscription with analytics enabled"
        )
from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from redis import Redis
import time

rate_limit_redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)

async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    """Advanced rate limiting by IP and user"""
    ip = request.client.host
    key = f"rate_limit:{ip}"
    
    try:
        current = rate_limit_redis.incr(key)
        if current == 1:
            rate_limit_redis.expire(key, window)
        
        if current > limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
    except:
        # Fallback if Redis is unavailable
        pass
