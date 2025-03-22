import pytest
from jose import jwt
from datetime import datetime, timedelta

from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings


def test_create_access_token():
    """Test creating an access token."""
    data = {"sub": "123"}
    expires_delta = timedelta(minutes=15)
    
    token = create_access_token(data["sub"], expires_delta=expires_delta)
    assert token
    
    # Decode token and verify contents
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == data["sub"]
    
    # Check expiration time is set correctly
    exp_time = datetime.fromtimestamp(payload["exp"])
    now = datetime.utcnow()
    assert (exp_time - now).total_seconds() > (expires_delta.total_seconds() - 10)


def test_password_hash():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    
    # Hashed password should be different from original
    assert hashed_password != password
    
    # Should verify correctly
    assert verify_password(password, hashed_password)
    
    # Wrong password should fail
    assert not verify_password("wrongpassword", hashed_password)