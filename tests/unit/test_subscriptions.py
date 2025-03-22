"""
Tests for subscription management features.
"""

import pytest
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription import Subscription, SubscriptionPlan
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.services.subscription_service import (
    get_available_plans,
    get_subscription,
    create_subscription,
    update_subscription,
    cancel_subscription,
    check_feature_access
)


def test_get_available_plans(db_session):
    """Test getting available subscription plans."""
    # Create test plans
    plans = [
        SubscriptionPlan(
            name="Free",
            description="Free tier",
            price=0,
            currency="USD",
            billing_interval="monthly",
            max_workspaces=1,
            max_members_per_workspace=1,
            ai_features_enabled=False,
            integrations_enabled=False,
            analytics_enabled=False,
            is_active=True,
            is_public=True
        ),
        SubscriptionPlan(
            name="Pro",
            description="Pro tier",
            price=999,  # $9.99
            currency="USD",
            billing_interval="monthly",
            max_workspaces=5,
            max_members_per_workspace=10,
            ai_features_enabled=True,
            integrations_enabled=True,
            analytics_enabled=True,
            is_active=True,
            is_public=True
        ),
        SubscriptionPlan(
            name="Hidden Plan",
            description="Not public",
            price=4999,  # $49.99
            currency="USD",
            billing_interval="monthly",
            max_workspaces=10,
            max_members_per_workspace=50,
            ai_features_enabled=True,
            integrations_enabled=True,
            analytics_enabled=True,
            is_active=True,
            is_public=False  # Not public
        ),
        SubscriptionPlan(
            name="Inactive Plan",
            description="Not active",
            price=1999,  # $19.99
            currency="USD",
            billing_interval="monthly",
            max_workspaces=5,
            max_members_per_workspace=10,
            ai_features_enabled=True,
            integrations_enabled=True,
            analytics_enabled=True,
            is_active=False,  # Not active
            is_public=True
        )
    ]
    
    for plan in plans:
        db_session.add(plan)
    db_session.commit()
    
    # Get available plans
    available_plans = get_available_plans(db_session)
    
    # Should only return active and public plans
    assert len(available_plans) == 2
    plan_names = [plan.name for plan in available_plans]
    assert "Free" in plan_names
    assert "Pro" in plan_names
    assert "Hidden Plan" not in plan_names
    assert "Inactive Plan" not in plan_names


def test_get_subscription(db_session):
    """Test getting a user's subscription."""
    user_id = 999
    
    # Test when user has no subscription
    subscription = get_subscription(db_session, user_id)
    assert subscription is None
    
    # Create a subscription
    db_subscription = Subscription(
        user_id=user_id,
        plan_id=1,
        status="active",
        start_date=datetime.now() - timedelta(days=30),
        next_billing_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(db_subscription)
    db_session.commit()
    
    # Test getting the subscription
    subscription = get_subscription(db_session, user_id)
    assert subscription is not None
    assert subscription.user_id == user_id
    assert subscription.plan_id == 1
    assert subscription.status == "active"


def test_create_subscription(db_session):
    """Test creating a subscription."""
    user_id = 999
    
    # Create a test plan
    plan = SubscriptionPlan(
        name="Test Plan",
        description="Test plan",
        price=999,  # $9.99
        currency="USD",
        billing_interval="monthly",
        max_workspaces=5,
        max_members_per_workspace=10,
        ai_features_enabled=True,
        integrations_enabled=True,
        analytics_enabled=True,
        is_active=True,
        is_public=True
    )
    db_session.add(plan)
    db_session.commit()
    
    # Create a subscription
    subscription_in = SubscriptionCreate(
        plan_id=plan.id,
        payment_method_id="pm_test_123456"
    )
    
    subscription = create_subscription(db_session, subscription_in, user_id)
    assert subscription is not None
    assert subscription.user_id == user_id
    assert subscription.plan_id == plan.id
    assert subscription.payment_method_id == "pm_test_123456"
    assert subscription.status == "trial"
    assert subscription.trial_end_date is not None
    assert subscription.next_billing_date is not None
    
    # Test creating a subscription when the user already has one
    with pytest.raises(HTTPException) as excinfo:
        create_subscription(db_session, subscription_in, user_id)
    assert excinfo.value.status_code == 400
    assert "already has a subscription" in str(excinfo.value.detail)
    
    # Test creating a subscription with a non-existent plan
    user_id = 1000  # Different user
    subscription_in.plan_id = 999  # Non-existent plan
    
    with pytest.raises(HTTPException) as excinfo:
        create_subscription(db_session, subscription_in, user_id)
    assert excinfo.value.status_code == 404
    assert "plan not found" in str(excinfo.value.detail).lower()


def test_update_subscription(db_session):
    """Test updating a subscription."""
    user_id = 999
    
    # Create test plans
    plans = [
        SubscriptionPlan(
            name="Basic Plan",
            description="Basic plan",
            price=999,  # $9.99
            currency="USD",
            billing_interval="monthly",
            is_active=True
        ),
        SubscriptionPlan(
            name="Premium Plan",
            description="Premium plan",
            price=1999,  # $19.99
            currency="USD",
            billing_interval="monthly",
            is_active=True
        )
    ]
    
    for plan in plans:
        db_session.add(plan)
    db_session.commit()
    
    # Create a subscription
    subscription = Subscription(
        user_id=user_id,
        plan_id=plans[0].id,
        payment_method_id="pm_test_123456",
        status="active",
        start_date=datetime.now() - timedelta(days=30),
        next_billing_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(subscription)
    db_session.commit()
    
    # Update subscription
    subscription_in = SubscriptionUpdate(
        plan_id=plans[1].id,
        payment_method_id="pm_test_789012"
    )
    
    updated_subscription = update_subscription(db_session, subscription, subscription_in)
    assert updated_subscription.plan_id == plans[1].id
    assert updated_subscription.payment_method_id == "pm_test_789012"
    
    # Test updating with a non-existent plan
    subscription_in = SubscriptionUpdate(plan_id=999)  # Non-existent plan
    
    with pytest.raises(HTTPException) as excinfo:
        update_subscription(db_session, subscription, subscription_in)
    assert excinfo.value.status_code == 404
    assert "plan not found" in str(excinfo.value.detail).lower()


def test_cancel_subscription(db_session):
    """Test cancelling a subscription."""
    user_id = 999
    
    # Create a subscription
    subscription = Subscription(
        user_id=user_id,
        plan_id=1,
        status="active",
        start_date=datetime.now() - timedelta(days=30),
        next_billing_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(subscription)
    db_session.commit()
    
    # Cancel subscription
    cancelled_subscription = cancel_subscription(db_session, subscription)
    assert cancelled_subscription.status == "cancelled"
    assert cancelled_subscription.cancelled_at is not None


def test_check_feature_access(db_session):
    """Test checking feature access based on subscription."""
    user_id = 999
    
    # Create a test plan
    plan = SubscriptionPlan(
        name="Test Plan",
        description="Test plan",
        price=999,  # $9.99
        currency="USD",
        billing_interval="monthly",
        ai_features_enabled=True,
        integrations_enabled=False,
        analytics_enabled=True,
        is_active=True
    )
    db_session.add(plan)
    db_session.commit()
    
    # Create a subscription
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status="active",
        start_date=datetime.now() - timedelta(days=30),
        next_billing_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(subscription)
    db_session.commit()
    
    # Test feature access
    assert check_feature_access(subscription, "ai_features", db_session) is True
    assert check_feature_access(subscription, "integrations", db_session) is False
    assert check_feature_access(subscription, "analytics", db_session) is True
    assert check_feature_access(subscription, "tasks", db_session) is True  # Always allowed
    
    # Test with inactive subscription
    subscription.status = "expired"
    db_session.add(subscription)
    db_session.commit()
    
    assert check_feature_access(subscription, "ai_features", db_session) is False
    assert check_feature_access(subscription, "tasks", db_session) is True  # Always allowed
    
    # Test with no subscription
    assert check_feature_access(None, "ai_features", db_session) is False
    assert check_feature_access(None, "tasks", db_session) is True  # Always allowed