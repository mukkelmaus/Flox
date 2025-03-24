#!/usr/bin/env python3
"""
OneTask API Test Script

This script tests the basic functionality of the OneTask API:
1. Creating a test user
2. Obtaining a JWT token
3. Accessing a protected endpoint
4. Testing various feature endpoints

Usage:
    python test_api.py

Environment variables:
    API_BASE_URL: Base URL of the API (default: http://localhost:5000)
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000")
API_V1 = f"{API_BASE_URL}/api/v1"
TEST_USER = {
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "username": f"testuser_{int(datetime.now().timestamp())}",
    "password": "SecurePassword123!",
    "full_name": "Test User"
}

# Helper functions
def print_response(response, label="Response"):
    """Print formatted API response"""
    print(f"\n{label} ({response.status_code}):")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def step(message):
    """Print a step message"""
    print(f"\n\033[1;34m{message}\033[0m")
    print("=" * len(message))

def success(message):
    """Print a success message"""
    print(f"\033[1;32m✓ {message}\033[0m")

def error(message):
    """Print an error message and exit"""
    print(f"\033[1;31m✗ {message}\033[0m")
    sys.exit(1)

# Global variables to store state
access_token = None
workspace_id = None

# Test API health
step("Testing API health")
try:
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response, "Health")
    if response.status_code == 200:
        success("API health check passed")
    else:
        error("API health check failed")
except Exception as e:
    error(f"API health check failed: {str(e)}")

# Test creating a user
step("Creating test user")
try:
    response = requests.post(
        f"{API_V1}/users/", 
        json=TEST_USER
    )
    print_response(response, "Create User")
    
    if response.status_code == 200:
        success("User created successfully")
    else:
        error(f"Failed to create user: {response.text}")
except Exception as e:
    error(f"User creation failed: {str(e)}")

# Test authentication
step("Testing authentication")
try:
    response = requests.post(
        f"{API_V1}/login/access-token", 
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_response(response, "Authentication")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        success("Authentication successful")
    else:
        error(f"Authentication failed: {response.text}")
except Exception as e:
    error(f"Authentication request failed: {str(e)}")

# Test accessing user info
step("Testing protected endpoint")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_V1}/users/me", headers=headers)
    print_response(response, "User Info")
    
    if response.status_code == 200:
        success("Protected endpoint access successful")
    else:
        error(f"Protected endpoint access failed: {response.text}")
except Exception as e:
    error(f"Protected endpoint request failed: {str(e)}")

# Test creating a workspace
step("Testing workspace creation")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{API_V1}/workspaces/", 
        json={"name": "Test Workspace", "description": "Test workspace for API testing"},
        headers=headers
    )
    print_response(response, "Create Workspace")
    
    if response.status_code == 200:
        workspace_data = response.json()
        workspace_id = workspace_data["id"]
        success("Workspace created successfully")
    else:
        error(f"Workspace creation failed: {response.text}")
except Exception as e:
    error(f"Workspace creation request failed: {str(e)}")

# Test creating a task
step("Testing task creation")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{API_V1}/tasks/", 
        json={
            "title": "Test Task",
            "description": "This is a test task created by the API test script",
            "priority": "medium",
            "workspace_id": workspace_id
        },
        headers=headers
    )
    print_response(response, "Create Task")
    
    if response.status_code == 200:
        task_data = response.json()
        task_id = task_data["id"]
        success("Task created successfully")
    else:
        error(f"Task creation failed: {response.text}")
except Exception as e:
    error(f"Task creation request failed: {str(e)}")

# Final summary
print("\n" + "=" * 50)
print("\033[1;32mAll tests passed successfully!\033[0m")
print("=" * 50)