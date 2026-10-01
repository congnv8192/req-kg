"""
点赞业务逻辑服务
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime

from ..models.database import SessionLocal
from ..models.models import Like, LikeCreate, LikeResponse, LikeStatsResponse, PaginationParams, PaginationMeta


class LikeService:
    """点赞服务类"""

    @staticmethod
    def create_like(db: Session, user_id: str, like_data: LikeCreate) -> Like:
        """创建或更新点赞"""
        # 检查是否已存在该用户的点赞记录
        existing = db.query(Like).filter(
            and_(
                Like.user_id == user_id,
                Like.content_id == like_data.content_id,
                Like.content_type == like_data.content_type
            )
        ).first()

        if existing:
            # 更新现有记录
            existing.action = like_data.action
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        # 创建新点赞记录
        like_id = str(uuid.uuid4())
        db_like = Like(
            id=like_id,
            user_id=user_id,
            **like_data.dict()
        )
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like

    @staticmethod
    def get_content_like_stats(db: Session, content_id: str, content_type: str, user_id: Optional[str] = None) -> LikeStatsResponse:
        """获取内容点赞统计"""
        # 获取所有点赞记录
        likes = db.query(Like).filter(
            and_(Like.content_id == content_id, Like.content_type == content_type)
        ).all()

        # 计算统计数据
        total_likes = sum(1 for like in likes if like.action == "like")
        total_unlikes = sum(1 for like in likes if like.action == "unlike")

        # 获取当前用户的点赞状态
        user_action = None
        if user_id:
            user_like = db.query(Like).filter(
                and_(
                    Like.user_id == user_id,
                    Like.content_id == content_id,
                    Like.content_type == content_type
                )
            ).first()
            if user_like:
                user_action = user_like.action

        return LikeStatsResponse(
            content_id=content_id,
            content_type=content_type,
            total_likes=total_likes,
            total_unlikes=total_unlikes,
            user_action=user_action
        )

    @staticmethod
    def get_user_like_history(
        db: Session,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取用户点赞历史"""
        # 构建查询条件
        query = db.query(Like).filter(Like.user_id == user_id)

        if content_type:
            query = query.filter(Like.content_type == content_type)

        # 获取总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * limit
        likes = query.order_by(desc(Like.created_at)).offset(offset).limit(limit).all()

        # 计算分页信息
        pages = (total + limit - 1) // limit

        pagination = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            pages=pages
        )

        return {
            "likes": likes,
            "pagination": pagination.dict()
        }

    @staticmethod
    def delete_like(db: Session, user_id: str, content_id: str, content_type: str) -> bool:
        """删除点赞记录"""
        like = db.query(Like).filter(
            and_(
                Like.user_id == user_id,
                Like.content_id == content_id,
                Like.content_type == content_type
            )
        ).first()

        if not like:
            return False

        db.delete(like)
        db.commit()
        return True


# 便捷函数
def get_like_service() -> LikeService:
    """获取点赞服务实例"""
    return LikeService()
