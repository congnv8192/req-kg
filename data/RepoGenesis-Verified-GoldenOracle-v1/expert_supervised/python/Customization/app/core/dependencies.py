"""
依赖注入管理
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import redis
import json
from datetime import datetime, timedelta

from .config import settings
from ..models.database import SessionLocal


# 安全相关依赖
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """数据库会话依赖"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """Redis连接依赖"""
    return redis.from_url(settings.redis_url)


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """
    验证JWT令牌
    """
    if not credentials:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        return None


def get_current_user_id(user_id: Optional[str] = Depends(verify_token)) -> str:
    """
    获取当前用户ID（必需认证）
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证或认证已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_user_id_optional(user_id: Optional[str] = Depends(verify_token)) -> Optional[str]:
    """
    获取当前用户ID（可选认证）
    """
    return user_id


# 缓存相关依赖
def get_cache() -> redis.Redis:
    """获取缓存连接"""
    return get_redis()


# 健康检查依赖
def get_health_checker():
    """健康检查依赖"""
    def check_health():
        # 这里可以添加实际的健康检查逻辑
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    return check_health
