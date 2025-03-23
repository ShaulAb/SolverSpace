"""
test_validators.py
-----------------
Tests for username validation with security-first approach.
All non-Latin characters are rejected at format level for maximum security.
"""

import pytest
from solver_space.utils.validators import UsernameValidator

def test_valid_usernames():
    """Test valid usernames that meet all security requirements.
    Only Latin letters, numbers, and underscores allowed.
    """
    validator = UsernameValidator()
    valid_cases = [
        "valid_user_name",  # Standard valid username
        "abc",              # Minimum length
        "test_123",        # Letters, numbers, underscore
        "ValidMixedCase",  # Case sensitivity preserved
        "a" * 30,          # Maximum length
    ]
    
    for username in valid_cases:
        is_valid, error = validator.validate(username)
        assert is_valid, f"Username {username} should be valid but got error: {error}"

def test_invalid_formats():
    """Test rejection of unsafe username formats.
    This includes length, character set, and security violations.
    """
    validator = UsernameValidator()
    invalid_cases = [
        # Length violations
        ("ab", UsernameValidator.ERROR_LENGTH),                # Too short
        ("a" * 31, UsernameValidator.ERROR_LENGTH),           # Too long
        ("", UsernameValidator.ERROR_LENGTH),                 # Empty
        
        # Format violations (security-critical)
        ("123user", UsernameValidator.ERROR_FORMAT),          # No number at start
        ("_user", UsernameValidator.ERROR_FORMAT),            # No underscore at start
        ("user@name", UsernameValidator.ERROR_FORMAT),        # No special chars
        
        # Security violations (caught at format level)
        ("usеr", UsernameValidator.ERROR_FORMAT),            # Cyrillic 'е'
        ("раssword", UsernameValidator.ERROR_FORMAT),        # Cyrillic 'р'
        ("用户名", UsernameValidator.ERROR_FORMAT),           # Non-Latin script
        ("user名", UsernameValidator.ERROR_FORMAT),          # Mixed scripts
    ]
    
    for username, expected_error in invalid_cases:
        is_valid, error = validator.validate(username)
        assert not is_valid, f"Username {username} should be invalid"
        assert error == expected_error, f"Expected error '{expected_error}' but got '{error}'"

def test_reserved_words():
    """Test rejection of reserved usernames (security measure)."""
    validator = UsernameValidator()
    reserved_cases = [
        "admin",           # Administrative
        "administrator",   # Administrative
        "help",           # System reserved
        "support",        # System reserved
    ]
    
    for username in reserved_cases:
        is_valid, error = validator.validate(username)
        assert not is_valid, f"Username {username} should be invalid (reserved)"
        assert error == UsernameValidator.ERROR_RESERVED

def test_username_sanitization():
    """Test username sanitization for storage."""
    validator = UsernameValidator()
    sanitize_cases = [
        ("", "u"),                    # Empty to safe default
        ("User@Name", "User_Name"),   # Special chars to underscore
        ("123user", "u123user"),      # Safe prefix for number start
        ("user name", "user_name"),   # Space to underscore
        ("a" * 35, "a" * 30),        # Length truncation
        ("UPPER_CASE", "UPPER_CASE"), # Case preservation
        ("user.name", "user_name"),   # Dot to underscore
    ]
    
    for input_name, expected in sanitize_cases:
        result = validator.sanitize(input_name)
        assert result == expected, f"Expected '{expected}' but got '{result}'" 