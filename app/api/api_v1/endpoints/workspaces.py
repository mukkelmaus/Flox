from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.schemas.workspace import (
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceMemberResponse,
)

router = APIRouter()


@router.get("/", response_model=List[Workspace])
def read_workspaces(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve workspaces the current user is a member of.
    
    - **skip**: Number of workspaces to skip (pagination)
    - **limit**: Maximum number of workspaces to return
    """
    # Get workspace IDs the user is a member of
    workspace_memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == current_user.id)
        .all()
    )
    
    workspace_ids = [membership.workspace_id for membership in workspace_memberships]
    
    # Get workspaces with these IDs
    from app.models.workspace import Workspace as WorkspaceModel
    
    workspaces = (
        db.query(WorkspaceModel)
        .filter(WorkspaceModel.id.in_(workspace_ids))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return workspaces


@router.post("/", response_model=Workspace, status_code=status.HTTP_201_CREATED)
def create_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new workspace.
    
    - **name**: Workspace name (required)
    - **description**: Workspace description
    """
    from app.models.workspace import Workspace as WorkspaceModel
    
    workspace = WorkspaceModel(
        name=workspace_in.name,
        description=workspace_in.description,
        owner_id=current_user.id,
    )
    
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    # Add creator as an admin member
    workspace_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="admin",
    )
    
    db.add(workspace_member)
    db.commit()
    
    return workspace


@router.get("/{workspace_id}", response_model=Workspace)
def read_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get workspace by ID.
    
    - **workspace_id**: Workspace ID
    """
    from app.models.workspace import Workspace as WorkspaceModel
    
    # Check if user is a member of this workspace
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or you don't have access",
        )
    
    workspace = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    return workspace


@router.put("/{workspace_id}", response_model=Workspace)
def update_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    workspace_in: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a workspace.
    
    - **workspace_id**: Workspace ID
    - **name**: Workspace name
    - **description**: Workspace description
    """
    from app.models.workspace import Workspace as WorkspaceModel
    
    # Check if user is an admin of this workspace
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.role == "admin",
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this workspace",
        )
    
    workspace = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    # Update workspace fields
    if workspace_in.name is not None:
        workspace.name = workspace_in.name
    if workspace_in.description is not None:
        workspace.description = workspace_in.description
    
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a workspace.
    
    - **workspace_id**: Workspace ID
    """
    from app.models.workspace import Workspace as WorkspaceModel
    
    # Check if user is the owner of this workspace
    workspace = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this workspace",
        )
    
    # Delete workspace
    db.delete(workspace)
    db.commit()


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
def read_workspace_members(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get workspace members.
    
    - **workspace_id**: Workspace ID
    """
    # Check if user is a member of this workspace
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )
    
    # Get all workspace members with user information
    members = (
        db.query(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .filter(WorkspaceMember.workspace_id == workspace_id)
        .all()
    )
    
    result = []
    for member, user in members:
        result.append(
            {
                "user_id": user.id,
                "workspace_id": member.workspace_id,
                "role": member.role,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
            }
        )
    
    return result


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
def add_workspace_member(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    member_in: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add a member to workspace.
    
    - **workspace_id**: Workspace ID
    - **user_id**: User ID to add
    - **role**: Role (member, admin)
    """
    # Check if current user is an admin of this workspace
    admin_membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.role == "admin",
        )
        .first()
    )
    
    if not admin_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add members to this workspace",
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == member_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if user is already a member
    existing_membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == member_in.user_id,
        )
        .first()
    )
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace",
        )
    
    # Add workspace member
    workspace_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_in.user_id,
        role=member_in.role,
    )
    
    db.add(workspace_member)
    db.commit()
    
    return {
        "user_id": user.id,
        "workspace_id": workspace_id,
        "role": member_in.role,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@router.put("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
def update_workspace_member(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    user_id: int,
    member_in: WorkspaceMemberUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a workspace member's role.
    
    - **workspace_id**: Workspace ID
    - **user_id**: User ID to update
    - **role**: New role (member, admin)
    """
    # Check if current user is an admin of this workspace
    admin_membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.role == "admin",
        )
        .first()
    )
    
    if not admin_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update members in this workspace",
        )
    
    # Get membership to update
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this workspace",
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update role
    membership.role = member_in.role
    
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    return {
        "user_id": user.id,
        "workspace_id": workspace_id,
        "role": membership.role,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def remove_workspace_member(
    *,
    db: Session = Depends(get_db),
    workspace_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Remove a member from workspace.
    
    - **workspace_id**: Workspace ID
    - **user_id**: User ID to remove
    """
    from app.models.workspace import Workspace as WorkspaceModel
    
    # Check if current user is an admin of this workspace or is removing themselves
    has_permission = False
    if current_user.id == user_id:  # Users can remove themselves
        has_permission = True
    else:
        admin_membership = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == current_user.id,
                WorkspaceMember.role == "admin",
            )
            .first()
        )
        if admin_membership:
            has_permission = True
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove members from this workspace",
        )
    
    # Get workspace to check if user is owner
    workspace = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    # Prevent removing the workspace owner
    if workspace.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove the workspace owner",
        )
    
    # Get membership to remove
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this workspace",
        )
    
    # Remove membership
    db.delete(membership)
    db.commit()
