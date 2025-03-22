from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator


class SubscriptionPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int  # in cents
    currency: str = "USD"
    billing_interval: str = "monthly"
    features: Optional[List[str]] = None
    max_workspaces: int = 1
    max_members_per_workspace: int = 1
    max_tasks: int = 0  # 0 means unlimited
    ai_features_enabled: bool = False
    integrations_enabled: bool = False
    analytics_enabled: bool = False
    
    @validator('billing_interval')
    def validate_billing_interval(cls, v):
        allowed = ['monthly', 'yearly']
        if v not in allowed:
            raise ValueError(f'Billing interval must be one of: {", ".join(allowed)}')
        return v


class SubscriptionPlan(SubscriptionPlanBase):
    id: int
    is_active: bool
    is_public: bool
    
    class Config:
        orm_mode = True


class SubscriptionBase(BaseModel):
    plan_id: int
    payment_method_id: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    payment_method_id: Optional[str] = None


class Subscription(SubscriptionBase):
    id: int
    user_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    billing_details: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
