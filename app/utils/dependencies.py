from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan


def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Optional[Subscription]:
    """
    Get the current user's subscription.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Subscription or None if not found
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
    ).first()
    
    return subscription


def verify_premium_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Verify that the user has premium access.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If the user doesn't have premium access
    """
    # Check for superuser access
    if current_user.is_superuser:
        return
    
    # Get user's subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Premium subscription required for this feature",
        )
    
    # Verify subscription has access to premium features
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription.plan_id,
    ).first()
    
    if not plan or not plan.ai_features_enabled:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Your current plan doesn't include access to premium features",
        )


def verify_integration_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Verify that the user has access to integration features.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If the user doesn't have integration access
    """
    # Check feature flag
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Integration features are currently disabled",
        )
    
    # Check for superuser access
    if current_user.is_superuser:
        return
    
    # Get user's subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription required for integration features",
        )
    
    # Verify subscription has access to integration features
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription.plan_id,
    ).first()
    
    if not plan or not plan.integrations_enabled:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Your current plan doesn't include access to integration features",
        )
