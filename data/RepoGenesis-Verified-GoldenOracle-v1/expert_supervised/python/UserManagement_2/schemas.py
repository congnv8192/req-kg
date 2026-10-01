"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """User login request schema"""
    username: str
    password: str


class UserUpdateRequest(BaseModel):
    """User update request schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """User response schema"""
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    """User registration response schema"""
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class LoginResponse(BaseModel):
    """Login response schema"""
    success: bool
    message: str
    data: TokenResponse


class RegisterResponse(BaseModel):
    """Registration response schema"""
    success: bool
    message: str
    data: UserRegisterResponse


class GetUserResponse(BaseModel):
    """Get user response schema"""
    success: bool
    message: str
    data: UserResponse


class UpdateUserResponse(BaseModel):
    """Update user response schema"""
    success: bool
    message: str
    data: dict


class DeleteUserResponse(BaseModel):
    """Delete user response schema"""
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

