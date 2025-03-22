"""
User management endpoints for the OneTask API.
"""

from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import (
    get_current_active_superuser,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated superuser
        
    Returns:
        List of users
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    
    Args:
        db: Database session
        user_in: User data
        
    Returns:
        Created user
    """
    # Check if user with this email exists
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    # Check if user with this username exists
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )
    
    # Create new user
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user info
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    username: str = Body(None),
    profile_picture: str = Body(None),
    bio: str = Body(None),
    time_zone: str = Body(None),
    language: str = Body(None),
    active_theme_id: int = Body(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update user.
    
    Args:
        db: Database session
        password: New password
        full_name: New full name
        email: New email
        username: New username
        profile_picture: New profile picture
        bio: New bio
        time_zone: New time zone
        language: New language
        active_theme_id: New active theme ID
        current_user: Current authenticated user
        
    Returns:
        Updated user info
    """
    current_user_data = jsonable_encoder(current_user)
    
    # Prepare user update data
    user_in = schemas.UserUpdate(
        password=password,
        full_name=full_name,
        email=email,
        username=username,
        profile_picture=profile_picture,
        bio=bio,
        time_zone=time_zone,
        language=language,
        active_theme_id=active_theme_id,
    )
    
    user_data = user_in.model_dump(exclude_unset=True)
    
    # Check if email is being updated and if it already exists
    if "email" in user_data and user_data["email"] != current_user.email:
        user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username is being updated and if it already exists
    if "username" in user_data and user_data["username"] != current_user.username:
        user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Hash password if it's being updated
    if "password" in user_data and user_data["password"]:
        user_data["password_hash"] = get_password_hash(user_data["password"])
        del user_data["password"]
    
    # Update user with new data
    for field, value in user_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific user by id.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated superuser
        
    Returns:
        User info
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user.
    
    Args:
        db: Database session
        user_id: User ID
        user_in: Updated user data
        current_user: Current authenticated superuser
        
    Returns:
        Updated user info
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_data = user_in.model_dump(exclude_unset=True)
    
    # Check if email is being updated and if it already exists
    if "email" in user_data and user_data["email"] != user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username is being updated and if it already exists
    if "username" in user_data and user_data["username"] != user.username:
        existing_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Hash password if it's being updated
    if "password" in user_data and user_data["password"]:
        user_data["password_hash"] = get_password_hash(user_data["password"])
        del user_data["password"]
    
    # Update user with new data
    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/change-password", response_model=schemas.User)
def change_password(
    *,
    db: Session = Depends(get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Change password.
    
    Args:
        db: Database session
        current_password: Current password
        new_password: New password
        current_user: Current authenticated user
        
    Returns:
        Updated user info
    """
    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    # Update password
    current_user.password_hash = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user