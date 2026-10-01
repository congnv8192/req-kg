"""
数据模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, Dict, Any

from .database import Base


class Favorite(Base):
    """收藏模型"""
    __tablename__ = "favorites"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    content_id = Column(String, index=True, nullable=False)
    content_type = Column(String, nullable=False)  # post, article, product, video
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, content_id={self.content_id})>"


class Like(Base):
    """点赞模型"""
    __tablename__ = "likes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    content_id = Column(String, index=True, nullable=False)
    content_type = Column(String, nullable=False)  # post, article, product, video
    action = Column(String, nullable=False)  # like, unlike
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Like(id={self.id}, user_id={self.user_id}, content_id={self.content_id}, action={self.action})>"


class History(Base):
    """历史记录模型"""
    __tablename__ = "history"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)  # view, search, share, download
    content_id = Column(String, index=True, nullable=True)
    content_type = Column(String, nullable=True)  # post, article, product, video
    meta_info = Column(JSON, nullable=True)  # 额外信息
    session_id = Column(String, index=True, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, action={self.action})>"


# Pydantic模型用于API响应
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class FavoriteCreate(BaseModel):
    """收藏创建模型"""
    content_id: str = Field(..., description="内容唯一标识")
    content_type: Literal["post", "article", "product", "video"] = Field(..., description="内容类型: post|article|product|video")
    category: Optional[str] = Field(None, description="收藏分类标签")


class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    id: str
    user_id: str
    content_id: str
    content_type: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """收藏列表响应模型"""
    favorites: List[FavoriteResponse]
    pagination: Dict[str, Any]


class LikeCreate(BaseModel):
    """点赞创建模型"""
    content_id: str = Field(..., description="内容唯一标识")
    content_type: Literal["post", "article", "product", "video"] = Field(..., description="内容类型: post|article|product|video")
    action: Literal["like", "unlike"] = Field(..., description="操作类型: like|unlike")


class LikeResponse(BaseModel):
    """点赞响应模型"""
    id: str
    user_id: str
    content_id: str
    content_type: str
    action: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LikeStatsResponse(BaseModel):
    """点赞统计响应模型"""
    content_id: str
    content_type: str
    total_likes: int
    total_unlikes: int
    user_action: Optional[str]  # 当前用户的点赞状态


class LikeHistoryResponse(BaseModel):
    """点赞历史响应模型"""
    likes: List[LikeResponse]
    pagination: Dict[str, Any]


class HistoryCreate(BaseModel):
    """历史记录创建模型"""
    action: Literal["view", "search", "share", "download"] = Field(..., description="操作类型: view|search|share|download")
    content_id: Optional[str] = Field(None, description="相关内容ID")
    content_type: Optional[str] = Field(None, description="内容类型")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="额外信息")
    session_id: Optional[str] = Field(None, description="会话标识")


class HistoryResponse(BaseModel):
    """历史记录响应模型"""
    id: str
    user_id: str
    action: str
    content_id: Optional[str]
    content_type: Optional[str]
    meta_info: Optional[Dict[str, Any]]
    session_id: Optional[str]
    created_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """历史记录列表响应模型"""
    history: List[HistoryResponse]
    pagination: Dict[str, Any]


# 分页查询模型
class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginationMeta(BaseModel):
    """分页元信息模型"""
    page: int
    limit: int
    total: int
    pages: int


# 错误响应模型
class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
