"""
Subscription service for the OneTask API.

This module handles functionality related to user subscriptions,
including plan management, payment processing integration,
and subscription status checks.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.subscription import Subscription, SubscriptionPlan
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

# Configure logging
logger = logging.getLogger(__name__)


def get_available_plans(db: Session) -> List[SubscriptionPlan]:
    """
    Get a list of available subscription plans.
    
    Args:
        db: Database session
        
    Returns:
        List of subscription plans
    """
    return db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True,
        SubscriptionPlan.is_public == True
    ).all()


def get_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """
    Get a user's subscription.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User's subscription or None if not found
    """
    return db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()


def create_subscription(
    db: Session,
    subscription_in: SubscriptionCreate,
    user_id: int
) -> Subscription:
    """
    Create a new subscription.
    
    Args:
        db: Database session
        subscription_in: Subscription data
        user_id: User ID
        
    Returns:
        Created subscription
    """
    # Check if user already has a subscription
    existing_subscription = get_subscription(db, user_id)
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a subscription"
        )
    
    # Check if plan exists
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription_in.plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Calculate dates
    now = datetime.now()
    trial_end_date = now + timedelta(days=14)  # 14-day trial
    
    if plan.billing_interval == "monthly":
        next_billing_date = trial_end_date + timedelta(days=30)
    else:  # yearly
        next_billing_date = trial_end_date + timedelta(days=365)
    
    # Create payment method
    # In a real implementation, we would use a payment processor
    # like Stripe to create and validate the payment method
    
    # Create subscription
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        payment_method_id=subscription_in.payment_method_id,
        status="trial",
        start_date=now,
        trial_end_date=trial_end_date,
        next_billing_date=next_billing_date,
        billing_details={},
        additional_data={}
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Created subscription for user {user_id}: plan={plan.name}")
    
    return subscription


def update_subscription(
    db: Session,
    subscription: Subscription,
    subscription_in: SubscriptionUpdate
) -> Subscription:
    """
    Update a subscription.
    
    Args:
        db: Database session
        subscription: Subscription to update
        subscription_in: Updated subscription data
        
    Returns:
        Updated subscription
    """
    update_data = subscription_in.dict(exclude_unset=True)
    
    # If changing plan, validate the new plan
    if "plan_id" in update_data:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == update_data["plan_id"],
            SubscriptionPlan.is_active == True
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )
        
        # Calculate new billing date based on plan
        if plan.billing_interval == "monthly":
            subscription.next_billing_date = datetime.now() + timedelta(days=30)
        else:  # yearly
            subscription.next_billing_date = datetime.now() + timedelta(days=365)
    
    # Apply updates
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Updated subscription for user {subscription.user_id}")
    
    return subscription


def cancel_subscription(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    """
    Cancel a subscription.
    
    Args:
        db: Database session
        subscription: Subscription to cancel
        
    Returns:
        Updated subscription
    """
    # In a real implementation, we would also cancel the subscription
    # with the payment processor (e.g., Stripe)
    
    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.now()
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Cancelled subscription for user {subscription.user_id}")
    
    return subscription


def process_expired_subscriptions(db: Session) -> Dict[str, Any]:
    """
    Process expired subscriptions.
    
    Args:
        db: Database session
        
    Returns:
        Processing results
    """
    now = datetime.now()
    
    # Find trials that have ended
    expired_trials = db.query(Subscription).filter(
        Subscription.status == "trial",
        Subscription.trial_end_date < now
    ).all()
    
    # Find cancelled subscriptions that have reached their end date
    expired_cancelled = db.query(Subscription).filter(
        Subscription.status == "cancelled",
        Subscription.next_billing_date < now
    ).all()
    
    # Process expired trials
    for subscription in expired_trials:
        if subscription.payment_method_id:
            # Trial ended, convert to active subscription
            subscription.status = "active"
            subscription.next_billing_date = now + timedelta(days=30)  # Assuming monthly
        else:
            # No payment method, mark as expired
            subscription.status = "expired"
        
        db.add(subscription)
    
    # Process expired cancelled subscriptions
    for subscription in expired_cancelled:
        subscription.status = "expired"
        subscription.end_date = now
        db.add(subscription)
    
    db.commit()
    
    return {
        "trials_processed": len(expired_trials),
        "cancelled_processed": len(expired_cancelled)
    }


def check_feature_access(
    subscription: Optional[Subscription], 
    feature: str,
    db: Session = None
) -> bool:
    """
    Check if a user has access to a specific feature based on their subscription.
    
    Args:
        subscription: User's subscription
        feature: Feature to check access for
        db: Optional database session (for plan fetching)
        
    Returns:
        True if the user has access, False otherwise
    """
    if not subscription:
        # Free tier access
        free_features = ["tasks", "basic_overview"]
        return feature in free_features
    
    if subscription.status not in ["active", "trial"]:
        # Inactive subscription
        free_features = ["tasks", "basic_overview"]
        return feature in free_features
    
    # Get plan details if db session provided
    if db:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
        
        if not plan:
            # Plan not found, fall back to free tier
            free_features = ["tasks", "basic_overview"]
            return feature in free_features
        
        # Feature-specific checks
        if feature == "ai_features" and not plan.ai_features_enabled:
            return False
        
        if feature == "integrations" and not plan.integrations_enabled:
            return False
        
        if feature == "analytics" and not plan.analytics_enabled:
            return False
    
    # By default, if subscription is active, grant access
    return True