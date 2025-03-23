"""
Support endpoints for the OneTask API.

These endpoints handle creating, reading, updating, and managing support tickets.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import support_service

router = APIRouter()


@router.get("/", response_model=List[schemas.SupportTicket])
def read_tickets(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    Retrieve support tickets.
    
    - Regular users can only see their own tickets
    - Admins can see all tickets
    - Results can be filtered by status, priority, and category
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    tickets = support_service.get_tickets(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        is_admin=is_admin,
    )
    
    return tickets


@router.post("/", response_model=schemas.SupportTicket)
def create_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_in: schemas.SupportTicketCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create a new support ticket.
    
    - Users can create tickets with different priorities and categories
    - All tickets start with 'open' status
    """
    ticket = support_service.create_ticket(
        db=db,
        ticket_in=ticket_in,
        user_id=current_user.id,
    )
    
    return ticket


@router.get("/statistics", response_model=Dict[str, Any])
def get_ticket_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get statistics about support tickets.
    
    - Regular users see stats for their own tickets
    - Admins see stats for all tickets
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    stats = support_service.get_ticket_statistics(
        db=db,
        user_id=user_id,
        is_admin=is_admin,
    )
    
    return stats


@router.get("/{ticket_id}", response_model=schemas.SupportTicket)
def read_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to get"),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get a specific support ticket by ID.
    
    - Regular users can only access their own tickets
    - Admins can access any ticket
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    ticket = support_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id,
        is_admin=is_admin,
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=schemas.SupportTicket)
def update_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to update"),
    ticket_in: schemas.SupportTicketUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update a support ticket.
    
    - Regular users can update basic ticket information
    - Admins can update all fields including status and assignment
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    ticket = support_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id,
        is_admin=is_admin,
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    updated_ticket = support_service.update_ticket(
        db=db,
        ticket=ticket,
        ticket_in=ticket_in,
        is_admin=is_admin,
    )
    
    return updated_ticket


@router.post("/{ticket_id}/assign", response_model=schemas.SupportTicket)
def assign_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to assign"),
    admin_id: int = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Assign a support ticket to an admin.
    
    - Only admins can assign tickets
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign tickets",
        )
    
    ticket = support_service.get_ticket(db=db, ticket_id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Verify that the assignee exists and is an admin
    admin = db.query(models.User).filter(
        models.User.id == admin_id,
        models.User.is_superuser == True,
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID",
        )
    
    updated_ticket = support_service.assign_ticket(
        db=db,
        ticket=ticket,
        admin_id=admin_id,
    )
    
    return updated_ticket


@router.post("/{ticket_id}/note", response_model=schemas.SupportTicket)
def add_admin_note(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to add a note to"),
    note: str = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Add an admin note to a support ticket.
    
    - Only admins can add admin notes
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add admin notes",
        )
    
    ticket = support_service.get_ticket(db=db, ticket_id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    updated_ticket = support_service.add_admin_note(
        db=db,
        ticket=ticket,
        note=note,
    )
    
    return updated_ticket


@router.post("/{ticket_id}/resolve", response_model=schemas.SupportTicket)
def resolve_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to resolve"),
    resolution_note: Optional[str] = Body(None, embed=True),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Resolve a support ticket.
    
    - Only admins can resolve tickets
    - An optional resolution note can be provided
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to resolve tickets",
        )
    
    ticket = support_service.get_ticket(db=db, ticket_id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    if ticket.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already resolved",
        )
    
    updated_ticket = support_service.resolve_ticket(
        db=db,
        ticket=ticket,
        resolution_note=resolution_note,
    )
    
    return updated_ticket


@router.post("/{ticket_id}/close", response_model=schemas.SupportTicket)
def close_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to close"),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Close a support ticket.
    
    - Both users and admins can close tickets
    - Users can only close their own tickets
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    ticket = support_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id,
        is_admin=is_admin,
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    updated_ticket = support_service.close_ticket(
        db=db,
        ticket=ticket,
    )
    
    return updated_ticket


@router.post("/{ticket_id}/reopen", response_model=schemas.SupportTicket)
def reopen_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_id: int = Path(..., title="The ID of the ticket to reopen"),
    reason: Optional[str] = Body(None, embed=True),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Reopen a closed or resolved support ticket.
    
    - Both users and admins can reopen tickets
    - Users can only reopen their own tickets
    - An optional reason can be provided
    """
    is_admin = current_user.is_superuser
    user_id = None if is_admin else current_user.id
    
    ticket = support_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id,
        is_admin=is_admin,
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    if ticket.status not in ["closed", "resolved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket must be closed or resolved to reopen",
        )
    
    updated_ticket = support_service.reopen_ticket(
        db=db,
        ticket=ticket,
        reason=reason,
    )
    
    return updated_ticket