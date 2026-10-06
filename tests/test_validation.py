import pytest
import re

def is_valid_email(email):
    if not email:
        return True # Optional field
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    if not phone:
        return False
    # Allow numbers, dashes, spaces, plus sign
    pattern = r'^[\d\s\-\+\(\)]{7,20}$'
    return bool(re.match(pattern, phone))

def test_email_validation():
    assert is_valid_email("doctor@carepoint.org") is True
    assert is_valid_email("patient.name@domain.co.in") is True
    assert is_valid_email("invalid-email-string") is False
    assert is_valid_email("") is True

def test_phone_validation():
    assert is_valid_phone("555-0100") is True
    assert is_valid_phone("+1 555 0199") is True
    assert is_valid_phone("123") is False
    assert is_valid_phone("") is False
