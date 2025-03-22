from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, get_current_active_superuser
from app.db.session import get_db
from app.models.user import User
from app.schemas.subscription import (
    Subscription,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionPlan,
)

router = APIRouter()


@router.get("/plans", response_model=List[SubscriptionPlan])
def read_subscription_plans(
    db: Session = Depends(get_db),
) -> Any:
    """
    Retrieve available subscription plans.
    """
    from app.models.subscription import SubscriptionPlan as SubscriptionPlanModel
    
    plans = db.query(SubscriptionPlanModel).all()
    return plans


@router.get("/my-subscription", response_model=Subscription)
def read_user_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user's subscription.
    """
    from app.models.subscription import Subscription as SubscriptionModel
    
    subscription = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    return subscription


@router.post("/subscribe", response_model=Subscription, status_code=status.HTTP_201_CREATED)
def create_subscription(
    *,
    db: Session = Depends(get_db),
    subscription_in: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create or update a subscription for the current user.
    
    - **plan_id**: Subscription plan ID (required)
    - **payment_method_id**: Payment method ID (required for paid plans)
    """
    # Check if plan exists
    from app.models.subscription import SubscriptionPlan as SubscriptionPlanModel
    from app.models.subscription import Subscription as SubscriptionModel
    
    plan = db.query(SubscriptionPlanModel).filter(
        SubscriptionPlanModel.id == subscription_in.plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )
    
    # Check if user already has a subscription
    existing_subscription = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == current_user.id
    ).first()
    
    if existing_subscription:
        # Update existing subscription
        existing_subscription.plan_id = subscription_in.plan_id
        if subscription_in.payment_method_id:
            existing_subscription.payment_method_id = subscription_in.payment_method_id
        
        db.add(existing_subscription)
        db.commit()
        db.refresh(existing_subscription)
        
        return existing_subscription
    
    # Create new subscription
    subscription = SubscriptionModel(
        user_id=current_user.id,
        plan_id=subscription_in.plan_id,
        payment_method_id=subscription_in.payment_method_id,
        status="active",
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.put("/my-subscription", response_model=Subscription)
def update_user_subscription(
    *,
    db: Session = Depends(get_db),
    subscription_in: SubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user's subscription.
    
    - **plan_id**: New subscription plan ID
    - **payment_method_id**: New payment method ID
    """
    from app.models.subscription import Subscription as SubscriptionModel
    
    subscription = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    if subscription_in.plan_id is not None:
        # Check if plan exists
        from app.models.subscription import SubscriptionPlan as SubscriptionPlanModel
        
        plan = db.query(SubscriptionPlanModel).filter(
            SubscriptionPlanModel.id == subscription_in.plan_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found",
            )
        
        subscription.plan_id = subscription_in.plan_id
    
    if subscription_in.payment_method_id is not None:
        subscription.payment_method_id = subscription_in.payment_method_id
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.post("/cancel-subscription", response_model=dict)
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel the current user's subscription.
    """
    from app.models.subscription import Subscription as SubscriptionModel
    
    subscription = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    # Update subscription status
    subscription.status = "cancelled"
    
    db.add(subscription)
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}


@router.post("/admin/plans", response_model=SubscriptionPlan, status_code=status.HTTP_201_CREATED)
def create_subscription_plan(
    *,
    db: Session = Depends(get_db),
    plan_in: dict,
    current_user: User = Depends(get_current_active_superuser),  # Admin only
) -> Any:
    """
    Admin endpoint to create a new subscription plan.
    
    - **name**: Plan name (required)
    - **description**: Plan description
    - **price**: Plan price in cents (required)
    - **billing_interval**: Billing interval (monthly, yearly)
    - **features**: List of features included in the plan
    """
    from app.models.subscription import SubscriptionPlan as SubscriptionPlanModel
    
    # Check if plan with the same name already exists
    existing_plan = db.query(SubscriptionPlanModel).filter(
        SubscriptionPlanModel.name == plan_in["name"]
    ).first()
    
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A plan with this name already exists",
        )
    
    # Create plan
    plan = SubscriptionPlanModel(**plan_in)
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return plan


@router.get("/admin/subscriptions", response_model=List[Subscription])
def read_all_subscriptions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_active_superuser),  # Admin only
) -> Any:
    """
    Admin endpoint to retrieve all subscriptions.
    
    - **skip**: Number of subscriptions to skip (pagination)
    - **limit**: Maximum number of subscriptions to return
    - **status**: Filter by status (active, cancelled, expired)
    """
    from app.models.subscription import Subscription as SubscriptionModel
    
    query = db.query(SubscriptionModel)
    
    if status:
        query = query.filter(SubscriptionModel.status == status)
    
    subscriptions = query.offset(skip).limit(limit).all()
    
    return subscriptions
