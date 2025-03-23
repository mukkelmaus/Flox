"""
WebSocket endpoints for real-time features.
"""
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.websockets.connection_manager import manager
from app.api.deps import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login/access-token")


async def get_current_user_ws(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from a WebSocket connection.
    
    Args:
        websocket: WebSocket connection
        token: JWT token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        WebSocketDisconnect: If authentication fails
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    
    return user


@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time notifications.
    
    Args:
        websocket: WebSocket connection
        token: JWT token
        db: Database session
    """
    try:
        user = await get_current_user_ws(websocket, token, db)
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                # Just keep the connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id)
    except WebSocketDisconnect:
        # Authentication failed, connection already closed
        pass


@router.websocket("/ws/tasks/{workspace_id}")
async def tasks_websocket(
    websocket: WebSocket,
    workspace_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time task updates in a workspace.
    
    Args:
        websocket: WebSocket connection
        workspace_id: Workspace ID
        token: JWT token
        db: Database session
    """
    try:
        user = await get_current_user_ws(websocket, token, db)
        
        # Check if user has access to the workspace
        from app.models.workspace import Workspace, WorkspaceMember
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
        
        # Owner always has access
        has_access = workspace.owner_id == user.id
        
        # Check membership if not owner
        if not has_access:
            member = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id
            ).first()
            has_access = member is not None
        
        if not has_access:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
        
        # Connect to workspace
        await manager.connect(websocket, user.id, workspace_id)
        
        try:
            while True:
                # Just keep the connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id)
    except WebSocketDisconnect:
        # Authentication failed, connection already closed
        pass


@router.websocket("/ws/focus-session/{session_id}")
async def focus_session_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for focus session updates and collaboration.
    
    Args:
        websocket: WebSocket connection
        session_id: Focus session ID
        token: JWT token
        db: Database session
    """
    try:
        user = await get_current_user_ws(websocket, token, db)
        
        # TODO: Validate focus session and user access
        
        # Connect to focus session
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                # Process messages for collaborative features
                data = await websocket.receive_json()
                
                # Echo back to all connected clients
                # In a real implementation, you would process and validate the data
                await manager.broadcast_to_workspace(
                    {
                        "type": "focus_session_update",
                        "session_id": session_id,
                        "sender_id": user.id,
                        "data": data
                    },
                    int(session_id)  # Assuming session_id maps to a workspace
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id)
    except WebSocketDisconnect:
        # Authentication failed, connection already closed
        pass