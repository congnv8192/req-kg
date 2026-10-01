"""
API routes for user management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    ErrorResponse
)
from security import (
    create_access_token,
    get_current_user_id,
    hash_password
)
from config import settings
import crud

router = APIRouter(prefix=settings.API_BASE_PATH, tags=["users"])


@router.post("/users/register", status_code=201)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if username already exists
    if crud.user_exists_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Username already exists",
                "error_code": "USERNAME_EXISTS"
            }
        )
    
    # Check if email already exists
    if crud.user_exists_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Email already exists",
                "error_code": "EMAIL_EXISTS"
            }
        )
    
    # Create user
    db_user = crud.create_user(db, user_data)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user_id": db_user.user_id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "created_at": db_user.created_at.isoformat()
        }
    }


@router.post("/users/login")
async def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Login user"""
    # Authenticate user
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid username or password",
                "error_code": "INVALID_CREDENTIALS"
            }
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.user_id}
    )
    
    expires_in = settings.JWT_EXPIRATION_HOURS * 3600
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user information"""
    # Check if user is trying to access their own data or another user's data
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Access denied",
                "error_code": "ACCESS_DENIED"
            }
        )
    
    # Get user
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )
    
    return {
        "success": True,
        "message": "User information retrieved",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else user.created_at.isoformat()
        }
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update user information"""
    # Check if user is trying to update their own data or another user's data
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Access denied",
                "error_code": "ACCESS_DENIED"
            }
        )
    
    # Check if email is already in use by another user
    if update_data.email:
        existing_user = crud.get_user_by_email(db, update_data.email)
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Email already in use",
                    "error_code": "EMAIL_EXISTS"
                }
            )
    
    # Update user
    user = crud.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )
    
    return {
        "success": True,
        "message": "User information updated",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "updated_at": user.updated_at.isoformat()
        }
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete user"""
    # Check if user is trying to delete their own account or another user's account
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Access denied",
                "error_code": "ACCESS_DENIED"
            }
        )
    
    # Delete user
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )
    
    return {
        "success": True,
        "message": "User deleted successfully"
    }


@router.delete("/users/cleanup")
async def cleanup_users(db: Session = Depends(get_db)):
    """Clean up all users (for testing)"""
    db.query(User).delete()
    db.commit()
    return {
        "success": True,
        "message": "All users cleaned up"
    }

