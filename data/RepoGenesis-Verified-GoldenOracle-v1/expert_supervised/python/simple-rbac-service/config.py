#!/usr/bin/env python3
"""
Configuration settings for the RBAC Service
"""

import os
from typing import Optional

# Server Configuration
SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", 8080))
DEBUG_MODE: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Flask Configuration
FLASK_ENV: str = os.getenv("FLASK_ENV", "production")

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Service Configuration
MAX_ROLE_NAME_LENGTH: int = 255
MAX_PERMISSION_NAME_LENGTH: int = 255
MAX_USER_ID_LENGTH: int = 255

# API Configuration
API_PREFIX: str = "/api"
API_VERSION: str = "1.0.0"


def get_config_summary() -> dict:
    """Get current configuration as a dictionary"""
    return {
        "host": SERVER_HOST,
        "port": SERVER_PORT,
        "debug": DEBUG_MODE,
        "env": FLASK_ENV,
        "log_level": LOG_LEVEL,
        "api_prefix": API_PREFIX,
        "api_version": API_VERSION,
    }

