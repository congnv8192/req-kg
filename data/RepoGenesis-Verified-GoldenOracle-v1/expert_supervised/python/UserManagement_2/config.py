"""
Configuration settings for the User Management service
"""

import os
from datetime import timedelta

class Settings:
    """Application settings"""
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8080))
    API_BASE_PATH = "/api/v1"
    
    # App Settings
    APP_NAME = "User Management Service"
    APP_VERSION = "1.0.0"
    
settings = Settings()

