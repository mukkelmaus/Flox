#!/usr/bin/env python3
"""
WebSocket client test script for the OneTask API.

This script tests the WebSocket endpoints for real-time features.
"""
import asyncio
import json
import sys
import websockets
import requests


async def test_notification_websocket(token):
    """
    Test the notification WebSocket endpoint.
    
    Args:
        token: JWT access token
    """
    uri = "ws://localhost:5000/ws/notifications?token=" + token
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to notification websocket!")
            
            # Keep the connection alive
            while True:
                await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")


async def test_tasks_websocket(token, workspace_id):
    """
    Test the tasks WebSocket endpoint.
    
    Args:
        token: JWT access token
        workspace_id: Workspace ID
    """
    uri = f"ws://localhost:5000/ws/tasks/{workspace_id}?token={token}"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to tasks websocket for workspace {workspace_id}!")
            
            # Keep the connection alive
            while True:
                await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")


async def test_realtime_api(token):
    """
    Test the realtime API endpoints.
    
    Args:
        token: JWT access token
    """
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:5000/api/v1/realtime"
    
    # Test system event
    print("Sending system event...")
    response = requests.post(
        f"{base_url}/events/system",
        json={
            "title": "Test System Event",
            "content": "This is a test system notification",
            "data": {"test": True}
        },
        headers=headers,
    )
    print(f"Response: {response.status_code}")
    print(response.json())
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Test task event
    print("\nSending task event...")
    response = requests.post(
        f"{base_url}/events/task",
        json={
            "task_id": 1,
            "title": "Test Task",
            "action": "updated",
            "data": {"test": True}
        },
        headers=headers,
    )
    print(f"Response: {response.status_code}")
    print(response.json())


async def main():
    """
    Main function.
    """
    if len(sys.argv) < 2:
        print("Usage: python websocket_client_test.py <access_token> [workspace_id]")
        return
    
    token = sys.argv[1]
    workspace_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if workspace_id:
        await asyncio.gather(
            test_notification_websocket(token),
            test_tasks_websocket(token, workspace_id),
            test_realtime_api(token),
        )
    else:
        await asyncio.gather(
            test_notification_websocket(token),
            test_realtime_api(token),
        )


if __name__ == "__main__":
    asyncio.run(main())