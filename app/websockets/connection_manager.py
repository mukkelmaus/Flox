"""
WebSocket connection manager for real-time features.
"""
from typing import Dict, List, Set, Optional
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections for real-time features.
    """
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Active connections by workspace_id
        self.workspace_connections: Dict[int, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, workspace_id: Optional[int] = None):
        """
        Connect a WebSocket for a user.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            workspace_id: Optional workspace ID
        """
        await websocket.accept()
        
        # Initialize if this is the first connection for the user
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            
        # Add connection to the user's connections
        self.active_connections[user_id].append(websocket)
        
        # If workspace_id is provided, add the user to the workspace
        if workspace_id:
            if workspace_id not in self.workspace_connections:
                self.workspace_connections[workspace_id] = set()
            self.workspace_connections[workspace_id].add(user_id)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect a WebSocket for a user.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        # Remove the connection from the user's connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # If this was the last connection for the user, clean up
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Remove user from all workspaces
                for workspace_id, users in self.workspace_connections.items():
                    if user_id in users:
                        users.remove(user_id)
                
                # Clean up empty workspaces
                workspace_ids_to_remove = []
                for workspace_id, users in self.workspace_connections.items():
                    if not users:
                        workspace_ids_to_remove.append(workspace_id)
                
                for workspace_id in workspace_ids_to_remove:
                    del self.workspace_connections[workspace_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """
        Send a message to a specific user.
        
        Args:
            message: Message to send
            user_id: User ID
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)
    
    async def broadcast_to_workspace(self, message: dict, workspace_id: int):
        """
        Broadcast a message to all users in a workspace.
        
        Args:
            message: Message to send
            workspace_id: Workspace ID
        """
        if workspace_id in self.workspace_connections:
            for user_id in self.workspace_connections[workspace_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected users.
        
        Args:
            message: Message to send
        """
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)


# Global connection manager instance
manager = ConnectionManager()