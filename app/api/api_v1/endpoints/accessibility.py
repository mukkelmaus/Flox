from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.accessibility import (
    AccessibilitySettings,
    AccessibilitySettingsUpdate,
)

router = APIRouter()


@router.get("/settings", response_model=AccessibilitySettings)
def read_accessibility_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's accessibility settings.
    """
    from app.models.accessibility import AccessibilitySettings as AccessibilitySettingsModel
    
    settings = db.query(AccessibilitySettingsModel).filter(
        AccessibilitySettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings if not found
        settings = AccessibilitySettingsModel(
            user_id=current_user.id,
            font_size="medium",
            high_contrast=False,
            reduced_motion=False,
            screen_reader_optimized=False,
            keyboard_shortcuts_enabled=True,
            dyslexia_friendly_font=False,
            custom_settings={},
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/settings", response_model=AccessibilitySettings)
def update_accessibility_settings(
    *,
    db: Session = Depends(get_db),
    settings_in: AccessibilitySettingsUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update user's accessibility settings.
    
    - **font_size**: Font size preference (small, medium, large, x-large)
    - **high_contrast**: Enable high contrast mode
    - **reduced_motion**: Reduce motion in animations
    - **screen_reader_optimized**: Optimize for screen readers
    - **keyboard_shortcuts_enabled**: Enable keyboard shortcuts
    - **dyslexia_friendly_font**: Use dyslexia-friendly font
    - **custom_settings**: Additional custom settings (JSON)
    """
    from app.models.accessibility import AccessibilitySettings as AccessibilitySettingsModel
    
    settings = db.query(AccessibilitySettingsModel).filter(
        AccessibilitySettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create settings if not found
        settings = AccessibilitySettingsModel(
            user_id=current_user.id,
            **settings_in.dict(),
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        return settings
    
    # Update settings fields
    settings_data = settings_in.dict(exclude_unset=True)
    for field, value in settings_data.items():
        setattr(settings, field, value)
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings


@router.get("/adhd-profile", response_model=Dict[str, Any])
def read_adhd_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's ADHD-specific profile settings.
    """
    from app.models.accessibility import ADHDProfile as ADHDProfileModel
    
    profile = db.query(ADHDProfileModel).filter(
        ADHDProfileModel.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile if not found
        profile = ADHDProfileModel(
            user_id=current_user.id,
            focus_mode_duration=25,
            break_duration=5,
            task_chunking_enabled=True,
            visual_timers_enabled=True,
            dopamine_boosts_enabled=True,
            distraction_blocking_level="medium",
            custom_settings={},
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return {
        "user_id": profile.user_id,
        "focus_mode_duration": profile.focus_mode_duration,
        "break_duration": profile.break_duration,
        "task_chunking_enabled": profile.task_chunking_enabled,
        "visual_timers_enabled": profile.visual_timers_enabled,
        "dopamine_boosts_enabled": profile.dopamine_boosts_enabled,
        "distraction_blocking_level": profile.distraction_blocking_level,
        "custom_settings": profile.custom_settings,
    }


@router.put("/adhd-profile", response_model=Dict[str, Any])
def update_adhd_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: dict,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update user's ADHD-specific profile settings.
    
    - **focus_mode_duration**: Focus session duration in minutes
    - **break_duration**: Break duration in minutes
    - **task_chunking_enabled**: Enable automatic task chunking
    - **visual_timers_enabled**: Use visual timers for tasks
    - **dopamine_boosts_enabled**: Enable dopamine boost rewards
    - **distraction_blocking_level**: Distraction blocking level (low, medium, high)
    - **custom_settings**: Additional custom settings (JSON)
    """
    from app.models.accessibility import ADHDProfile as ADHDProfileModel
    
    profile = db.query(ADHDProfileModel).filter(
        ADHDProfileModel.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile if not found
        profile = ADHDProfileModel(
            user_id=current_user.id,
            **profile_in,
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
    else:
        # Update profile fields
        for field, value in profile_in.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return {
        "user_id": profile.user_id,
        "focus_mode_duration": profile.focus_mode_duration,
        "break_duration": profile.break_duration,
        "task_chunking_enabled": profile.task_chunking_enabled,
        "visual_timers_enabled": profile.visual_timers_enabled,
        "dopamine_boosts_enabled": profile.dopamine_boosts_enabled,
        "distraction_blocking_level": profile.distraction_blocking_level,
        "custom_settings": profile.custom_settings,
    }
