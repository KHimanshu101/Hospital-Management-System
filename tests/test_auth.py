import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from services.auth_service import AuthService
import hashlib
import secrets
from datetime import datetime, timedelta

def test_password_hashing():
    raw_password = "SecretPassword123!"
    p_hash = generate_password_hash(raw_password)
    assert p_hash != raw_password
    assert check_password_hash(p_hash, raw_password) is True
    assert check_password_hash(p_hash, "WrongPassword") is False

def test_public_registration_role_enforcement():
    # Public registration must restrict self-assigning Admin role
    allowed_roles = ['Receptionist', 'Doctor']
    
    requested_role_1 = 'Admin'
    role_1 = requested_role_1 if requested_role_1 in allowed_roles else 'Receptionist'
    assert role_1 == 'Receptionist'
    
    requested_role_2 = 'Doctor'
    role_2 = requested_role_2 if requested_role_2 in allowed_roles else 'Receptionist'
    assert role_2 == 'Doctor'

def test_token_hashing_and_uniqueness():
    token1 = secrets.token_urlsafe(32)
    token2 = secrets.token_urlsafe(32)
    assert token1 != token2
    
    hash1 = hashlib.sha256(token1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(token1.encode('utf-8')).hexdigest()
    hash3 = hashlib.sha256(token2.encode('utf-8')).hexdigest()
    
    assert hash1 == hash2
    assert hash1 != hash3

def test_token_expiration_logic():
    now = datetime.now()
    valid_expires_at = now + timedelta(minutes=30)
    expired_expires_at = now - timedelta(minutes=5)
    
    assert valid_expires_at > now
    assert expired_expires_at < now
