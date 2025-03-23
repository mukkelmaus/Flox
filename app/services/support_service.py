"""
Support service for the OneTask API.

This module handles functionality related to customer support tickets,
including ticket creation, updates, and status tracking.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.support import SupportTicket
from app.models.user import User
from app.schemas.support import SupportTicketCreate, SupportTicketUpdate

# Configure logging
logger = logging.getLogger(__name__)


def get_tickets(
    db: Session,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    is_admin: bool = False,
) -> List[SupportTicket]:
    """
    Get support tickets with optional filtering.
    
    Args:
        db: Database session
        user_id: Optional user ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status to filter by
        priority: Optional priority to filter by
        category: Optional category to filter by
        is_admin: Whether the requester is an admin
        
    Returns:
        List of support tickets
    """
    query = db.query(SupportTicket)
    
    # Filter by user if not admin or explicitly requested
    if not is_admin or user_id:
        query = query.filter(SupportTicket.user_id == user_id)
    
    # Apply additional filters
    if status:
        query = query.filter(SupportTicket.status == status)
    
    if priority:
        query = query.filter(SupportTicket.priority == priority)
    
    if category:
        query = query.filter(SupportTicket.category == category)
    
    # Sort by priority and created date
    query = query.order_by(
        SupportTicket.priority.desc(),
        desc(SupportTicket.created_at)
    )
    
    return query.offset(skip).limit(limit).all()


def get_ticket(
    db: Session,
    ticket_id: int,
    user_id: Optional[int] = None,
    is_admin: bool = False,
) -> Optional[SupportTicket]:
    """
    Get a specific support ticket.
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        user_id: Optional user ID for access control
        is_admin: Whether the requester is an admin
        
    Returns:
        Support ticket or None if not found
    """
    query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
    
    # Only admins can view other users' tickets
    if not is_admin and user_id:
        query = query.filter(SupportTicket.user_id == user_id)
    
    return query.first()


def create_ticket(
    db: Session,
    ticket_in: SupportTicketCreate,
    user_id: int,
) -> SupportTicket:
    """
    Create a new support ticket.
    
    Args:
        db: Database session
        ticket_in: Ticket data
        user_id: User ID
        
    Returns:
        Created ticket
    """
    ticket = SupportTicket(
        user_id=user_id,
        subject=ticket_in.subject,
        description=ticket_in.description,
        priority=ticket_in.priority,
        category=ticket_in.category,
        status="open",  # All new tickets start as open
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Created support ticket {ticket.id} for user {user_id}")
    
    return ticket


def update_ticket(
    db: Session,
    ticket: SupportTicket,
    ticket_in: SupportTicketUpdate,
    is_admin: bool = False,
) -> SupportTicket:
    """
    Update a support ticket.
    
    Args:
        db: Database session
        ticket: Ticket to update
        ticket_in: Updated ticket data
        is_admin: Whether the updater is an admin
        
    Returns:
        Updated ticket
    """
    update_data = ticket_in.dict(exclude_unset=True)
    
    # Only admins can update certain fields
    if not is_admin:
        admin_fields = ["assigned_to", "admin_notes", "status"]
        for field in admin_fields:
            if field in update_data:
                del update_data[field]
    
    # Handle status changes
    old_status = ticket.status
    new_status = update_data.get("status", old_status)
    
    # If resolving the ticket, record the resolved time
    if old_status != "resolved" and new_status == "resolved":
        ticket.resolved_at = datetime.now()
    elif old_status == "resolved" and new_status != "resolved":
        ticket.resolved_at = None
    
    # Update ticket fields
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    # Update the updated_at timestamp
    ticket.updated_at = datetime.now()
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Updated support ticket {ticket.id}")
    
    return ticket


def assign_ticket(
    db: Session,
    ticket: SupportTicket,
    admin_id: int,
) -> SupportTicket:
    """
    Assign a support ticket to an admin.
    
    Args:
        db: Database session
        ticket: Ticket to assign
        admin_id: Admin user ID
        
    Returns:
        Updated ticket
    """
    ticket.assigned_to = admin_id
    
    if ticket.status == "open":
        ticket.status = "in_progress"
    
    ticket.updated_at = datetime.now()
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Assigned support ticket {ticket.id} to admin {admin_id}")
    
    return ticket


def add_admin_note(
    db: Session,
    ticket: SupportTicket,
    note: str,
) -> SupportTicket:
    """
    Add an admin note to a support ticket.
    
    Args:
        db: Database session
        ticket: Ticket to update
        note: Admin note
        
    Returns:
        Updated ticket
    """
    if ticket.admin_notes:
        # Append to existing notes with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticket.admin_notes = f"{ticket.admin_notes}\n\n{timestamp}:\n{note}"
    else:
        # First note
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticket.admin_notes = f"{timestamp}:\n{note}"
    
    ticket.updated_at = datetime.now()
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Added admin note to support ticket {ticket.id}")
    
    return ticket


def resolve_ticket(
    db: Session,
    ticket: SupportTicket,
    resolution_note: Optional[str] = None,
) -> SupportTicket:
    """
    Resolve a support ticket.
    
    Args:
        db: Database session
        ticket: Ticket to resolve
        resolution_note: Optional resolution note
        
    Returns:
        Updated ticket
    """
    ticket.status = "resolved"
    ticket.resolved_at = datetime.now()
    ticket.updated_at = datetime.now()
    
    if resolution_note:
        # Add resolution note
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resolution = f"{timestamp} - RESOLUTION:\n{resolution_note}"
        
        if ticket.admin_notes:
            ticket.admin_notes = f"{ticket.admin_notes}\n\n{resolution}"
        else:
            ticket.admin_notes = resolution
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Resolved support ticket {ticket.id}")
    
    return ticket


def close_ticket(
    db: Session,
    ticket: SupportTicket,
) -> SupportTicket:
    """
    Close a support ticket.
    
    Args:
        db: Database session
        ticket: Ticket to close
        
    Returns:
        Updated ticket
    """
    ticket.status = "closed"
    ticket.updated_at = datetime.now()
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Closed support ticket {ticket.id}")
    
    return ticket


def reopen_ticket(
    db: Session,
    ticket: SupportTicket,
    reason: Optional[str] = None,
) -> SupportTicket:
    """
    Reopen a closed or resolved support ticket.
    
    Args:
        db: Database session
        ticket: Ticket to reopen
        reason: Optional reason for reopening
        
    Returns:
        Updated ticket
    """
    ticket.status = "open"
    ticket.resolved_at = None
    ticket.updated_at = datetime.now()
    
    if reason:
        # Add reopening reason
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reopen_note = f"{timestamp} - REOPENED:\n{reason}"
        
        if ticket.admin_notes:
            ticket.admin_notes = f"{ticket.admin_notes}\n\n{reopen_note}"
        else:
            ticket.admin_notes = reopen_note
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"Reopened support ticket {ticket.id}")
    
    return ticket


def get_ticket_statistics(
    db: Session,
    user_id: Optional[int] = None,
    is_admin: bool = False,
) -> Dict[str, Any]:
    """
    Get statistics about support tickets.
    
    Args:
        db: Database session
        user_id: Optional user ID for filtering
        is_admin: Whether the requester is an admin
        
    Returns:
        Statistics dictionary
    """
    # Base query
    base_query = db.query(SupportTicket)
    
    # Filter by user if not admin or explicitly requested
    if not is_admin or user_id:
        base_query = base_query.filter(SupportTicket.user_id == user_id)
    
    # Total tickets
    total_tickets = base_query.count()
    
    # Tickets by status
    open_tickets = base_query.filter(SupportTicket.status == "open").count()
    in_progress_tickets = base_query.filter(SupportTicket.status == "in_progress").count()
    resolved_tickets = base_query.filter(SupportTicket.status == "resolved").count()
    closed_tickets = base_query.filter(SupportTicket.status == "closed").count()
    
    # Tickets by priority
    urgent_tickets = base_query.filter(SupportTicket.priority == "urgent").count()
    high_tickets = base_query.filter(SupportTicket.priority == "high").count()
    medium_tickets = base_query.filter(SupportTicket.priority == "medium").count()
    low_tickets = base_query.filter(SupportTicket.priority == "low").count()
    
    # Tickets by category
    bug_tickets = base_query.filter(SupportTicket.category == "bug").count()
    feature_request_tickets = base_query.filter(SupportTicket.category == "feature_request").count()
    question_tickets = base_query.filter(SupportTicket.category == "question").count()
    other_tickets = base_query.filter(SupportTicket.category == "other").count()
    
    return {
        "total_tickets": total_tickets,
        "by_status": {
            "open": open_tickets,
            "in_progress": in_progress_tickets,
            "resolved": resolved_tickets,
            "closed": closed_tickets
        },
        "by_priority": {
            "urgent": urgent_tickets,
            "high": high_tickets,
            "medium": medium_tickets,
            "low": low_tickets
        },
        "by_category": {
            "bug": bug_tickets,
            "feature_request": feature_request_tickets,
            "question": question_tickets,
            "other": other_tickets
        }
    }