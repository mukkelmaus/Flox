"""
Tests for the security module.
"""

import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings


def test_create_access_token():
    """Test creating an access token."""
    # Test with default expiration
    subject = "test-subject"
    token = create_access_token(subject)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == subject
    assert "exp" in payload
    
    # Test with custom expiration
    expires = timedelta(minutes=30)
    token = create_access_token(subject, expires_delta=expires)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == subject
    assert "exp" in payload


def test_password_hash():
    """Test password hashing and verification."""
    password = "test-password"
    hashed = get_password_hash(password)
    
    # Verify the hashed password
    assert verify_password(password, hashed)
    
    # Test with wrong password
    assert not verify_password("wrong-password", hashed)
    
    # Test with empty strings
    empty_hash = get_password_hash("")
    assert verify_password("", empty_hash)
    assert not verify_password("something", empty_hash)