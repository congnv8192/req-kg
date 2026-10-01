"""
历史记录业务逻辑服务
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from datetime import datetime, timedelta

from ..models.database import SessionLocal
from ..models.models import History, HistoryCreate, HistoryResponse, PaginationParams, PaginationMeta


class HistoryService:
    """历史记录服务类"""

    @staticmethod
    def create_history(
        db: Session,
        user_id: str,
        history_data: HistoryCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> History:
        """创建历史记录"""
        history_id = str(uuid.uuid4())
        db_history = History(
            id=history_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            **history_data.dict()
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_user_history(
        db: Session,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        action: Optional[str] = None,
        content_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取用户历史记录"""
        # 构建查询条件
        query = db.query(History).filter(History.user_id == user_id)

        if action:
            query = query.filter(History.action == action)

        if content_type:
            query = query.filter(History.content_type == content_type)

        if session_id:
            query = query.filter(History.session_id == session_id)

        if start_date:
            query = query.filter(History.created_at >= start_date)

        if end_date:
            query = query.filter(History.created_at <= end_date)

        # 获取总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * limit
        history_records = query.order_by(desc(History.created_at)).offset(offset).limit(limit).all()

        # 计算分页信息
        pages = (total + limit - 1) // limit

        pagination = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            pages=pages
        )

        return {
            "history": history_records,
            "pagination": pagination.dict()
        }

    @staticmethod
    def delete_history(db: Session, user_id: str, history_id: str) -> bool:
        """删除单个历史记录"""
        history = db.query(History).filter(
            and_(History.id == history_id, History.user_id == user_id)
        ).first()

        if not history:
            return False

        db.delete(history)
        db.commit()
        return True

    @staticmethod
    def clear_user_history(db: Session, user_id: str) -> int:
        """清空用户所有历史记录"""
        deleted_count = db.query(History).filter(History.user_id == user_id).delete()
        db.commit()
        return deleted_count

    @staticmethod
    def get_history_by_id(db: Session, history_id: str) -> Optional[History]:
        """根据ID获取历史记录"""
        return db.query(History).filter(History.id == history_id).first()


# 便捷函数
def get_history_service() -> HistoryService:
    """获取历史记录服务实例"""
    return HistoryService()
