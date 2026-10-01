#!/usr/bin/env python3
"""
Utility functions for the RBAC Service
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup a logger with the given name and level"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


def validate_role_name(role_name: Any) -> tuple[bool, Optional[str]]:
    """
    Validate role name
    
    Returns: (is_valid, error_message)
    """
    if not isinstance(role_name, str):
        return False, "Role name must be a string"
    
    if not role_name or len(role_name) == 0:
        return False, "Role name cannot be empty"
    
    if len(role_name) > 255:
        return False, "Role name cannot exceed 255 characters"
    
    return True, None


def validate_permission_name(permission_name: Any) -> tuple[bool, Optional[str]]:
    """
    Validate permission name
    
    Returns: (is_valid, error_message)
    """
    if not isinstance(permission_name, str):
        return False, "Permission name must be a string"
    
    if not permission_name or len(permission_name) == 0:
        return False, "Permission name cannot be empty"
    
    if len(permission_name) > 255:
        return False, "Permission name cannot exceed 255 characters"
    
    return True, None


def validate_user_id(user_id: Any) -> tuple[bool, Optional[str]]:
    """
    Validate user ID
    
    Returns: (is_valid, error_message)
    """
    if not isinstance(user_id, str):
        return False, "User ID must be a string"
    
    if not user_id or len(user_id) == 0:
        return False, "User ID cannot be empty"
    
    if len(user_id) > 255:
        return False, "User ID cannot exceed 255 characters"
    
    return True, None


def validate_role_id(role_id: Any) -> tuple[bool, Optional[str]]:
    """
    Validate role ID
    
    Returns: (is_valid, error_message)
    """
    if not isinstance(role_id, str):
        return False, "Role ID must be a string"
    
    if not role_id or len(role_id) == 0:
        return False, "Role ID cannot be empty"
    
    return True, None


class APIResponse:
    """Helper class for API responses"""
    
    @staticmethod
    def success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a success response"""
        response = {"status": "success"}
        response.update(data)
        return response
    
    @staticmethod
    def error(message: str) -> Dict[str, Any]:
        """Create an error response"""
        return {
            "status": "error",
            "message": message
        }


def log_request(logger: logging.Logger, method: str, endpoint: str, data: Optional[Dict] = None):
    """Log an incoming request"""
    if data:
        logger.debug(f"{method} {endpoint} - Data: {json.dumps(data)}")
    else:
        logger.debug(f"{method} {endpoint}")


def log_response(logger: logging.Logger, method: str, endpoint: str, status: int, response: Dict):
    """Log an outgoing response"""
    logger.debug(f"{method} {endpoint} - Status: {status} - Response: {json.dumps(response)}")

