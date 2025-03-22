from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.integration import (
    Integration,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationSync,
)
from app.services.integration_service import (
    sync_with_google_calendar,
    sync_with_todoist,
    get_available_integrations,
)

router = APIRouter()


@router.get("/available", response_model=List[Dict[str, Any]])
def read_available_integrations(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get available third-party integrations.
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    return get_available_integrations()


@router.get("/", response_model=List[Integration])
def read_user_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve user's connected integrations.
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    from app.models.integration import Integration as IntegrationModel
    
    integrations = db.query(IntegrationModel).filter(
        IntegrationModel.user_id == current_user.id
    ).all()
    
    return integrations


@router.post("/", response_model=Integration, status_code=status.HTTP_201_CREATED)
def create_integration(
    *,
    db: Session = Depends(get_db),
    integration_in: IntegrationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Connect a new third-party integration.
    
    - **service**: Service name (google_calendar, todoist, etc.)
    - **access_token**: OAuth access token
    - **refresh_token**: OAuth refresh token
    - **token_expiry**: Token expiry timestamp
    - **config**: Additional configuration (JSON)
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    from app.models.integration import Integration as IntegrationModel
    
    # Check if integration already exists
    existing_integration = db.query(IntegrationModel).filter(
        IntegrationModel.user_id == current_user.id,
        IntegrationModel.service == integration_in.service,
    ).first()
    
    if existing_integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration with {integration_in.service} already exists",
        )
    
    # Create integration
    integration = IntegrationModel(
        user_id=current_user.id,
        **integration_in.dict(),
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return integration


@router.put("/{integration_id}", response_model=Integration)
def update_integration(
    *,
    db: Session = Depends(get_db),
    integration_id: int,
    integration_in: IntegrationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an integration's configuration.
    
    - **integration_id**: Integration ID
    - **access_token**: OAuth access token
    - **refresh_token**: OAuth refresh token
    - **token_expiry**: Token expiry timestamp
    - **config**: Additional configuration (JSON)
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    from app.models.integration import Integration as IntegrationModel
    
    integration = db.query(IntegrationModel).filter(
        IntegrationModel.id == integration_id,
        IntegrationModel.user_id == current_user.id,
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Update integration fields
    integration_data = integration_in.dict(exclude_unset=True)
    for field, value in integration_data.items():
        setattr(integration, field, value)
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_integration(
    *,
    db: Session = Depends(get_db),
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Disconnect a third-party integration.
    
    - **integration_id**: Integration ID
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    from app.models.integration import Integration as IntegrationModel
    
    integration = db.query(IntegrationModel).filter(
        IntegrationModel.id == integration_id,
        IntegrationModel.user_id == current_user.id,
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Delete integration
    db.delete(integration)
    db.commit()


@router.post("/sync", response_model=IntegrationSync)
async def sync_integrations(
    db: Session = Depends(get_db),
    service: str = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Sync data with third-party integrations.
    
    - **service**: Specific service to sync (optional)
    """
    if not settings.ENABLE_THIRD_PARTY_INTEGRATIONS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Third-party integrations are disabled",
        )
    
    from app.models.integration import Integration as IntegrationModel
    
    # Get integrations to sync
    query = db.query(IntegrationModel).filter(IntegrationModel.user_id == current_user.id)
    if service:
        query = query.filter(IntegrationModel.service == service)
    
    integrations = query.all()
    
    if not integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No integrations found",
        )
    
    # Sync each integration
    results = {
        "synced": [],
        "failed": [],
    }
    
    for integration in integrations:
        try:
            if integration.service == "google_calendar":
                sync_result = await sync_with_google_calendar(db, integration, current_user)
                results["synced"].append({
                    "service": "google_calendar",
                    "items_synced": sync_result["items_synced"],
                    "last_sync": sync_result["last_sync"],
                })
                
            elif integration.service == "todoist":
                sync_result = await sync_with_todoist(db, integration, current_user)
                results["synced"].append({
                    "service": "todoist",
                    "items_synced": sync_result["items_synced"],
                    "last_sync": sync_result["last_sync"],
                })
                
            else:
                results["failed"].append({
                    "service": integration.service,
                    "error": "Unsupported integration service",
                })
                
        except Exception as e:
            results["failed"].append({
                "service": integration.service,
                "error": str(e),
            })
    
    return results
