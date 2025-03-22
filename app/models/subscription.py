from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func

from app.db.base_class import Base


class SubscriptionPlan(Base):
    """
    Subscription plan model.
    """
    # Basic plan info
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    price = Column(Integer, nullable=False)  # In cents
    currency = Column(String(3), default="USD")
    billing_interval = Column(
        Enum("monthly", "yearly", name="billing_interval"),
        default="monthly",
        nullable=False,
    )
    
    # Features
    features = Column(ARRAY(String), nullable=True)
    
    # Limits
    max_workspaces = Column(Integer, default=1)
    max_members_per_workspace = Column(Integer, default=1)
    max_tasks = Column(Integer, default=0)  # 0 means unlimited
    
    # Feature flags
    ai_features_enabled = Column(Boolean, default=False)
    integrations_enabled = Column(Boolean, default=False)
    analytics_enabled = Column(Boolean, default=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)


class Subscription(Base):
    """
    User subscription model.
    """
    # Relationships
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan_id = Column(Integer, ForeignKey("subscription_plan.id"), nullable=False)
    
    # Payment info
    payment_method_id = Column(String, nullable=True)
    
    # Subscription status
    status = Column(
        Enum("active", "cancelled", "expired", "trial", name="subscription_status"),
        default="active",
        nullable=False,
    )
    
    # Dates
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Billing info
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    billing_details = Column(JSONB, nullable=True)
    
    # Additional data
    additional_data = Column(JSONB, nullable=True)
