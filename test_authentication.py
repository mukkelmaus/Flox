#!/usr/bin/env python3
"""
Simple script to test authentication with the OneTask API.

This script tests the complete authentication flow:
1. Creating a user
2. Getting an access token
3. Using the token to access a protected endpoint
"""

import sys
import os
import json
import requests

# API URL - adjust as needed
API_URL = "http://localhost:5000/api/v1"

# Test user data
TEST_USER = {
    "email": "testauth@example.com",
    "username": "testauth",
    "password": "TestPassword123",
    "full_name": "Auth Test User"
}


def create_user():
    """Create a test user."""
    print("Creating test user...")
    response = requests.post(f"{API_URL}/users/", json=TEST_USER)
    if response.status_code == 200:
        print("✓ User created successfully")
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print("✓ User already exists (continuing)")
        return True
    else:
        print(f"✗ Failed to create user: {response.status_code}")
        print(response.text)
        return False


def get_token():
    """Get an access token for the test user."""
    print("\nGetting access token...")
    response = requests.post(
        f"{API_URL}/login/access-token",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✓ Token obtained successfully")
        return token
    else:
        print(f"✗ Failed to get token: {response.status_code}")
        print(response.text)
        return None


def test_protected_endpoint(token):
    """Test accessing a protected endpoint with the token."""
    print("\nTesting protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print("✓ Successfully accessed protected endpoint")
        print(f"User data: {json.dumps(user, indent=2)}")
        return True
    else:
        print(f"✗ Failed to access protected endpoint: {response.status_code}")
        print(response.text)
        return False


def main():
    """Run the authentication test."""
    print("=== OneTask API Authentication Test ===\n")
    
    if not create_user():
        return False
    
    token = get_token()
    if not token:
        return False
    
    if not test_protected_endpoint(token):
        return False
    
    print("\n✓ Authentication test completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)