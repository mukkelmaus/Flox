from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, get_current_active_superuser
from app.db.session import get_db
from app.models.user import User
from app.schemas.support import SupportTicket, SupportTicketCreate, SupportTicketUpdate

router = APIRouter()


@router.post("/tickets", response_model=SupportTicket, status_code=status.HTTP_201_CREATED)
def create_support_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_in: SupportTicketCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new support ticket.
    
    - **subject**: Ticket subject (required)
    - **description**: Detailed description of the issue (required)
    - **priority**: Priority level (low, medium, high, urgent)
    - **category**: Issue category (bug, feature_request, question, other)
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    # Create ticket
    ticket = SupportTicketModel(
        user_id=current_user.id,
        status="open",  # Default status for new tickets
        **ticket_in.dict(),
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return ticket


@router.get("/tickets", response_model=List[SupportTicket])
def read_support_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve support tickets for the current user.
    
    - **skip**: Number of tickets to skip (pagination)
    - **limit**: Maximum number of tickets to return
    - **status**: Filter by status (open, in_progress, resolved, closed)
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    query = db.query(SupportTicketModel).filter(SupportTicketModel.user_id == current_user.id)
    
    if status:
        query = query.filter(SupportTicketModel.status == status)
    
    tickets = query.order_by(SupportTicketModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return tickets


@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
def read_support_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get support ticket by ID.
    
    - **ticket_id**: Ticket ID
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Check if user can access this ticket
    if ticket.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this ticket",
        )
    
    return ticket


@router.put("/tickets/{ticket_id}", response_model=SupportTicket)
def update_support_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    ticket_in: SupportTicketUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a support ticket.
    
    - **ticket_id**: Ticket ID
    - **subject**: Ticket subject
    - **description**: Detailed description
    - **priority**: Priority level
    - **category**: Issue category
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Check if user can update this ticket
    if ticket.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this ticket",
        )
    
    # Ensure users can't update status directly (only admins)
    if "status" in ticket_in.dict(exclude_unset=True) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update ticket status",
        )
    
    # Update ticket fields
    ticket_data = ticket_in.dict(exclude_unset=True)
    for field, value in ticket_data.items():
        setattr(ticket, field, value)
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_support_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a support ticket.
    
    - **ticket_id**: Ticket ID
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Check if user can delete this ticket
    if ticket.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this ticket",
        )
    
    # Delete ticket
    db.delete(ticket)
    db.commit()


@router.get("/admin/tickets", response_model=List[SupportTicket])
def read_all_support_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_active_superuser),  # Admin only
) -> Any:
    """
    Admin endpoint to retrieve all support tickets.
    
    - **skip**: Number of tickets to skip (pagination)
    - **limit**: Maximum number of tickets to return
    - **status**: Filter by status (open, in_progress, resolved, closed)
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    query = db.query(SupportTicketModel)
    
    if status:
        query = query.filter(SupportTicketModel.status == status)
    
    tickets = query.order_by(SupportTicketModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return tickets


@router.put("/admin/tickets/{ticket_id}/status", response_model=SupportTicket)
def update_ticket_status(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    status: str,
    admin_notes: str = None,
    current_user: User = Depends(get_current_active_superuser),  # Admin only
) -> Any:
    """
    Admin endpoint to update ticket status.
    
    - **ticket_id**: Ticket ID
    - **status**: New status (open, in_progress, resolved, closed)
    - **admin_notes**: Optional admin notes
    """
    from app.models.support import SupportTicket as SupportTicketModel
    
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Validate status
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )
    
    # Update status and notes
    ticket.status = status
    if admin_notes:
        ticket.admin_notes = admin_notes
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return ticket
