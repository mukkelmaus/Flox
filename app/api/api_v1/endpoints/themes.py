from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.theme import Theme, ThemeCreate, ThemeUpdate

router = APIRouter()


@router.get("/", response_model=List[Theme])
def read_themes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve themes.
    
    - **skip**: Number of themes to skip (pagination)
    - **limit**: Maximum number of themes to return
    """
    from app.models.theme import Theme as ThemeModel
    
    # Get system themes (available to all users)
    system_themes = db.query(ThemeModel).filter(
        ThemeModel.is_system == True
    ).all()
    
    # Get user's custom themes
    user_themes = db.query(ThemeModel).filter(
        ThemeModel.user_id == current_user.id,
        ThemeModel.is_system == False,
    ).offset(skip).limit(limit).all()
    
    return system_themes + user_themes


@router.post("/", response_model=Theme, status_code=status.HTTP_201_CREATED)
def create_theme(
    *,
    db: Session = Depends(get_db),
    theme_in: ThemeCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new theme.
    
    - **name**: Theme name (required)
    - **description**: Theme description
    - **color_primary**: Primary color (hex)
    - **color_secondary**: Secondary color (hex)
    - **color_accent**: Accent color (hex)
    - **color_background**: Background color (hex)
    - **color_text**: Text color (hex)
    - **font_family**: Font family
    - **icon_set**: Icon set name
    """
    from app.models.theme import Theme as ThemeModel
    
    # Check if a theme with the same name already exists for this user
    existing_theme = db.query(ThemeModel).filter(
        ThemeModel.user_id == current_user.id,
        ThemeModel.name == theme_in.name,
    ).first()
    
    if existing_theme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A theme with this name already exists",
        )
    
    # Create theme
    theme = ThemeModel(
        user_id=current_user.id,
        is_system=False,
        **theme_in.dict(),
    )
    
    db.add(theme)
    db.commit()
    db.refresh(theme)
    
    return theme


@router.get("/{theme_id}", response_model=Theme)
def read_theme(
    *,
    db: Session = Depends(get_db),
    theme_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get theme by ID.
    
    - **theme_id**: Theme ID
    """
    from app.models.theme import Theme as ThemeModel
    
    theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    
    # Check if user has access to this theme
    if not theme.is_system and theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this theme",
        )
    
    return theme


@router.put("/{theme_id}", response_model=Theme)
def update_theme(
    *,
    db: Session = Depends(get_db),
    theme_id: int,
    theme_in: ThemeUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a theme.
    
    - **theme_id**: Theme ID
    - **name**: Theme name
    - **description**: Theme description
    - **color_primary**: Primary color (hex)
    - **color_secondary**: Secondary color (hex)
    - **color_accent**: Accent color (hex)
    - **color_background**: Background color (hex)
    - **color_text**: Text color (hex)
    - **font_family**: Font family
    - **icon_set**: Icon set name
    """
    from app.models.theme import Theme as ThemeModel
    
    theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    
    # Check if user has permission to update this theme
    if theme.is_system or theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this theme",
        )
    
    # Update theme fields
    theme_data = theme_in.dict(exclude_unset=True)
    for field, value in theme_data.items():
        setattr(theme, field, value)
    
    db.add(theme)
    db.commit()
    db.refresh(theme)
    
    return theme


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_theme(
    *,
    db: Session = Depends(get_db),
    theme_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a theme.
    
    - **theme_id**: Theme ID
    """
    from app.models.theme import Theme as ThemeModel
    
    theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    
    # Check if user has permission to delete this theme
    if theme.is_system or theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this theme",
        )
    
    # Delete theme
    db.delete(theme)
    db.commit()


@router.get("/current", response_model=Theme)
def get_current_theme(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's active theme.
    """
    # Get the user's current theme preference
    if not current_user.active_theme_id:
        # Return default theme if user doesn't have one set
        from app.models.theme import Theme as ThemeModel
        
        default_theme = db.query(ThemeModel).filter(
            ThemeModel.is_system == True,
            ThemeModel.name == "Default",
        ).first()
        
        if not default_theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Default theme not found",
            )
        
        return default_theme
    
    # Get user's active theme
    from app.models.theme import Theme as ThemeModel
    
    theme = db.query(ThemeModel).filter(ThemeModel.id == current_user.active_theme_id).first()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active theme not found",
        )
    
    return theme


@router.post("/set-active/{theme_id}", response_model=dict)
def set_active_theme(
    *,
    db: Session = Depends(get_db),
    theme_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Set a theme as the user's active theme.
    
    - **theme_id**: Theme ID to set as active
    """
    from app.models.theme import Theme as ThemeModel
    
    # Check if theme exists
    theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    
    # Check if user has access to this theme
    if not theme.is_system and theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to use this theme",
        )
    
    # Update user's active theme
    current_user.active_theme_id = theme_id
    
    db.add(current_user)
    db.commit()
    
    return {"message": f"Theme '{theme.name}' set as active"}
