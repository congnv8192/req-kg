"""
CRUD operations for user management
"""

from datetime import datetime
from sqlalchemy.orm import Session
from models import User
from schemas import UserRegisterRequest, UserUpdateRequest
from security import hash_password, verify_password


def create_user(db: Session, user_data: UserRegisterRequest) -> User:
    """Create a new user"""
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate user"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def update_user(db: Session, user_id: int, update_data: UserUpdateRequest) -> User:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True


def user_exists_by_username(db: Session, username: str) -> bool:
    """Check if username exists"""
    return db.query(User).filter(User.username == username).first() is not None


def user_exists_by_email(db: Session, email: str) -> bool:
    """Check if email exists"""
    return db.query(User).filter(User.email == email).first() is not None

