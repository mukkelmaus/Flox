#!/bin/bash

# Script to run before starting the application
echo "Running prestart script..."

# Create database tables
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

# Create default themes
python -c "
from app.db.session import SessionLocal
from app.models.theme import Theme

db = SessionLocal()

# Check if default theme exists
default_theme = db.query(Theme).filter(Theme.name == 'Default', Theme.is_system == True).first()
if not default_theme:
    # Create default theme
    default_theme = Theme(
        name='Default',
        description='Default light theme',
        color_primary='#007bff',
        color_secondary='#6c757d',
        color_accent='#fd7e14',
        color_background='#f8f9fa',
        color_text='#212529',
        font_family=\"'Inter', system-ui, sans-serif\",
        icon_set='feather',
        is_system=True,
    )
    db.add(default_theme)

# Check if dark theme exists
dark_theme = db.query(Theme).filter(Theme.name == 'Dark', Theme.is_system == True).first()
if not dark_theme:
    # Create dark theme
    dark_theme = Theme(
        name='Dark',
        description='Default dark theme',
        color_primary='#007bff',
        color_secondary='#6c757d',
        color_accent='#fd7e14',
        color_background='#212529',
        color_text='#f8f9fa',
        font_family=\"'Inter', system-ui, sans-serif\",
        icon_set='feather',
        is_system=True,
    )
    db.add(dark_theme)

# Check if high contrast theme exists
high_contrast_theme = db.query(Theme).filter(Theme.name == 'High Contrast', Theme.is_system == True).first()
if not high_contrast_theme:
    # Create high contrast theme
    high_contrast_theme = Theme(
        name='High Contrast',
        description='High contrast theme for better visibility',
        color_primary='#0066cc',
        color_secondary='#000000',
        color_accent='#ff8800',
        color_background='#ffffff',
        color_text='#000000',
        font_family=\"'Inter', system-ui, sans-serif\",
        icon_set='feather',
        is_system=True,
    )
    db.add(high_contrast_theme)

# Check if focus theme exists
focus_theme = db.query(Theme).filter(Theme.name == 'Focus', Theme.is_system == True).first()
if not focus_theme:
    # Create focus theme
    focus_theme = Theme(
        name='Focus',
        description='Minimalist theme for focus mode',
        color_primary='#555555',
        color_secondary='#333333',
        color_accent='#99cc00',
        color_background='#f5f5f5',
        color_text='#333333',
        font_family=\"'Inter', system-ui, sans-serif\",
        icon_set='feather',
        is_system=True,
    )
    db.add(focus_theme)

db.commit()
db.close()
"

# Create default subscription plans
python -c "
from app.db.session import SessionLocal
from app.models.subscription import SubscriptionPlan

db = SessionLocal()

# Check if free plan exists
free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == 'Free').first()
if not free_plan:
    # Create free plan
    free_plan = SubscriptionPlan(
        name='Free',
        description='Basic features for personal task management',
        price=0,
        currency='USD',
        billing_interval='monthly',
        features=['Basic task management', 'Focus mode', 'Single workspace'],
        max_workspaces=1,
        max_members_per_workspace=1,
        max_tasks=100,
        ai_features_enabled=False,
        integrations_enabled=False,
        analytics_enabled=False,
        is_active=True,
        is_public=True,
    )
    db.add(free_plan)

# Check if pro plan exists
pro_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == 'Pro').first()
if not pro_plan:
    # Create pro plan
    pro_plan = SubscriptionPlan(
        name='Pro',
        description='Advanced features for individuals',
        price=999,  # $9.99
        currency='USD',
        billing_interval='monthly',
        features=[
            'Advanced task management', 
            'Focus mode', 
            'Multiple workspaces',
            'AI task breakdown',
            'AI productivity insights',
            'Task history',
            'Basic integrations',
        ],
        max_workspaces=5,
        max_members_per_workspace=1,
        max_tasks=0,  # Unlimited
        ai_features_enabled=True,
        integrations_enabled=True,
        analytics_enabled=True,
        is_active=True,
        is_public=True,
    )
    db.add(pro_plan)

# Check if team plan exists
team_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == 'Team').first()
if not team_plan:
    # Create team plan
    team_plan = SubscriptionPlan(
        name='Team',
        description='Collaborative features for teams',
        price=1999,  # $19.99
        currency='USD',
        billing_interval='monthly',
        features=[
            'All Pro features',
            'Team workspaces',
            'Role-based access control',
            'Team analytics',
            'All integrations',
            'Priority support',
        ],
        max_workspaces=10,
        max_members_per_workspace=10,
        max_tasks=0,  # Unlimited
        ai_features_enabled=True,
        integrations_enabled=True,
        analytics_enabled=True,
        is_active=True,
        is_public=True,
    )
    db.add(team_plan)

# Check if enterprise plan exists
enterprise_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == 'Enterprise').first()
if not enterprise_plan:
    # Create enterprise plan
    enterprise_plan = SubscriptionPlan(
        name='Enterprise',
        description='Advanced features for organizations',
        price=4999,  # $49.99
        currency='USD',
        billing_interval='monthly',
        features=[
            'All Team features',
            'Unlimited workspaces',
            'Unlimited team members',
            'Advanced security',
            'Custom integrations',
            'Dedicated support',
            'SLA guarantees',
        ],
        max_workspaces=0,  # Unlimited
        max_members_per_workspace=0,  # Unlimited
        max_tasks=0,  # Unlimited
        ai_features_enabled=True,
        integrations_enabled=True,
        analytics_enabled=True,
        is_active=True,
        is_public=True,
    )
    db.add(enterprise_plan)

db.commit()
db.close()
"

# Create default achievements
python -c "
from app.db.session import SessionLocal
from app.models.gamification import Achievement

db = SessionLocal()

# Default achievements
achievements = [
    {
        'name': 'Getting Started',
        'description': 'Complete your first task',
        'points': 10,
        'icon': 'award',
        'requirement_type': 'task_count',
        'requirement_value': 1,
        'level': 1,
        'is_system': True,
    },
    {
        'name': 'Task Master',
        'description': 'Complete 10 tasks',
        'points': 50,
        'icon': 'check-circle',
        'requirement_type': 'task_count',
        'requirement_value': 10,
        'level': 1,
        'is_system': True,
    },
    {
        'name': 'Productivity Pro',
        'description': 'Complete 50 tasks',
        'points': 100,
        'icon': 'star',
        'requirement_type': 'task_count',
        'requirement_value': 50,
        'level': 2,
        'is_system': True,
    },
    {
        'name': 'First Streak',
        'description': 'Maintain a 3-day streak',
        'points': 30,
        'icon': 'trending-up',
        'requirement_type': 'streak',
        'requirement_value': 3,
        'level': 1,
        'is_system': True,
    },
    {
        'name': 'Consistent Achiever',
        'description': 'Maintain a 7-day streak',
        'points': 75,
        'icon': 'trending-up',
        'requirement_type': 'streak',
        'requirement_value': 7,
        'level': 2,
        'is_system': True,
    },
    {
        'name': 'Organization Wizard',
        'description': 'Create 5 different tags for your tasks',
        'points': 25,
        'icon': 'tag',
        'requirement_type': 'tag_count',
        'requirement_value': 5,
        'level': 1,
        'is_system': True,
    },
]

# Add achievements if they don't exist
for achievement_data in achievements:
    existing = db.query(Achievement).filter(
        Achievement.name == achievement_data['name'],
        Achievement.is_system == True
    ).first()
    
    if not existing:
        achievement = Achievement(**achievement_data)
        db.add(achievement)

db.commit()
db.close()
"

echo "Prestart script completed."
