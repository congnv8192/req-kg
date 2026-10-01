"""
Input validation utilities for User Management Service
"""
import re
import phonenumbers
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_username(username):
    """
    Validate username
    - Length: 3-50 characters
    - Characters: alphanumeric and underscore only
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    # Check alphanumeric and underscore only
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None


def validate_email(email):
    """
    Validate email address
    - Valid email format according to RFC 5322
    """
    if not email:
        return False, "Email is required"
    
    try:
        valid = validate_email_lib(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password):
    """
    Validate password
    - Minimum 8 characters
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
        
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
        
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
        
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
        
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_full_name(full_name):
    """
    Validate full name
    - Length: 1-100 characters
    """
    if not full_name:
        return False, "Full name is required"
    
    # Strip whitespace
    full_name = full_name.strip()
    
    if len(full_name) == 0:
        return False, "Full name cannot be empty or whitespace only"
    
    if len(full_name) > 100:
        return False, "Full name must not exceed 100 characters"
    
    return True, None


def validate_phone(phone):
    """
    Validate phone number
    - Optional field
    - Supports international format
    """
    if not phone:
        return True, None
    
    try:
        # Try to parse phone number
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed):
            return False, "Invalid phone number format"
        return True, None
    except phonenumbers.NumberParseException:
        return False, "Invalid phone number format"


def validate_role(role):
    """
    Validate role
    - Must be one of: user, admin, moderator
    """
    valid_roles = ['user', 'admin', 'moderator']
    if role not in valid_roles:
        return False, f"Role must be one of: {', '.join(valid_roles)}"
    return True, None


def validate_status(status):
    """
    Validate status
    - Must be one of: active, inactive, suspended
    """
    valid_statuses = ['active', 'inactive', 'suspended']
    if status not in valid_statuses:
        return False, f"Status must be one of: {', '.join(valid_statuses)}"
    return True, None


def validate_pagination(page, limit):
    """
    Validate pagination parameters
    """
    try:
        page = int(page) if page else 1
        limit = int(limit) if limit else 10
    except (ValueError, TypeError):
        return False, "Page and limit must be integers", None, None
    
    if page < 1:
        return False, "Page must be at least 1", None, None
    
    if limit < 1:
        return False, "Limit must be at least 1", None, None
    
    if limit > 100:
        limit = 100  # Cap at 100
    
    return True, None, page, limit

