#!/usr/bin/env python3
"""
Simple script to test authentication with the OneTask API on port 8000.

This script tests the complete authentication flow:
1. Creating a user
2. Getting an access token
3. Using the token to access a protected endpoint
"""

import json
import os
import sys
import requests

# API base URL - Use port 8000 for Uvicorn
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")

def create_user():
    """Create a test user."""
    print("Creating test user...")
    url = f"{API_BASE_URL}/api/v1/users/"
    
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("User created successfully!")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "already exists" in e.response.text:
            print("User already exists, continuing with login...")
            return {"username": data["username"]}
        print(f"Error creating user: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating user: {e}")
        sys.exit(1)

def get_token():
    """Get an access token for the test user."""
    print("Getting access token...")
    url = f"{API_BASE_URL}/api/v1/login/access-token"
    
    data = {
        "username": "test@example.com",  # Can use email or username
        "password": "testpassword123"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        print(f"Token response: {json.dumps(token_data, indent=2)}")
        print("Token obtained successfully!")
        return token_data["access_token"]
    except requests.exceptions.HTTPError as e:
        print(f"Error getting token: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting token: {e}")
        sys.exit(1)

def test_protected_endpoint(token):
    """Test accessing a protected endpoint with the token."""
    print("Testing protected endpoint (getting current user)...")
    url = f"{API_BASE_URL}/api/v1/users/me"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        print("Successfully accessed protected endpoint!")
        print(f"Current user: {json.dumps(user_data, indent=2)}")
        return user_data
    except requests.exceptions.HTTPError as e:
        print(f"Error accessing protected endpoint: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        sys.exit(1)
    except Exception as e:
        print(f"Error accessing protected endpoint: {e}")
        sys.exit(1)

def main():
    """Run the authentication test."""
    print("=== OneTask API Authentication Test (Port 8000) ===")
    
    # Step 1: Create a user
    user = create_user()
    
    # Step 2: Get access token
    token = get_token()
    
    # Step 3: Test accessing a protected endpoint
    user_data = test_protected_endpoint(token)
    
    print("\n=== Authentication Test Successful! ===")
    print(f"Authenticated as: {user_data.get('username', 'Unknown')}")
    print(f"User ID: {user_data.get('id', 'Unknown')}")
    print(f"Email: {user_data.get('email', 'Unknown')}")
    
if __name__ == "__main__":
    main()