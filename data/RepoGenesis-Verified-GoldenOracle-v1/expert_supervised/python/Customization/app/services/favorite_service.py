"""
收藏业务逻辑服务
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime

from ..models.database import SessionLocal
from ..models.models import Favorite, FavoriteCreate, FavoriteResponse, PaginationParams, PaginationMeta


class FavoriteService:
    """收藏服务类"""

    @staticmethod
    def create_favorite(db: Session, user_id: str, favorite_data: FavoriteCreate) -> Favorite:
        """创建收藏"""
        # 检查是否已存在相同收藏
        existing = db.query(Favorite).filter(
            and_(
                Favorite.user_id == user_id,
                Favorite.content_id == favorite_data.content_id,
                Favorite.content_type == favorite_data.content_type
            )
        ).first()

        if existing:
            # 更新现有收藏的时间戳
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        # 创建新收藏
        favorite_id = str(uuid.uuid4())
        db_favorite = Favorite(
            id=favorite_id,
            user_id=user_id,
            **favorite_data.dict()
        )
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return db_favorite

    @staticmethod
    def get_user_favorites(
        db: Session,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        content_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取用户收藏列表"""
        # 构建查询条件
        query = db.query(Favorite).filter(Favorite.user_id == user_id)

        if content_type:
            query = query.filter(Favorite.content_type == content_type)

        if category:
            query = query.filter(Favorite.category == category)

        # 获取总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * limit
        favorites = query.order_by(desc(Favorite.created_at)).offset(offset).limit(limit).all()

        # 计算分页信息
        pages = (total + limit - 1) // limit

        pagination = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            pages=pages
        )

        return {
            "favorites": favorites,
            "pagination": pagination.dict()
        }

    @staticmethod
    def delete_favorite(db: Session, user_id: str, favorite_id: str) -> bool:
        """删除收藏"""
        favorite = db.query(Favorite).filter(
            and_(Favorite.id == favorite_id, Favorite.user_id == user_id)
        ).first()

        if not favorite:
            return False

        db.delete(favorite)
        db.commit()
        return True

    @staticmethod
    def get_favorite_by_id(db: Session, favorite_id: str) -> Optional[Favorite]:
        """根据ID获取收藏"""
        return db.query(Favorite).filter(Favorite.id == favorite_id).first()


# 便捷函数
def get_favorite_service() -> FavoriteService:
    """获取收藏服务实例"""
    return FavoriteService()
