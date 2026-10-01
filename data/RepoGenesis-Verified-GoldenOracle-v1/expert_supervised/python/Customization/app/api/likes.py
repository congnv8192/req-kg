"""
点赞API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.dependencies import get_db, get_current_user_id, get_current_user_id_optional
from ..models.models import (
    LikeCreate,
    LikeResponse,
    LikeStatsResponse,
    LikeHistoryResponse,
    ErrorResponse
)
from ..services.like_service import get_like_service

router = APIRouter(prefix="/likes", tags=["点赞管理"])


@router.post(
    "",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "数据验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def add_like(
    like_data: LikeCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """添加点赞或点踩"""
    try:
        like = get_like_service().create_like(db, user_id, like_data)
        return LikeResponse.from_orm(like)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加点赞失败: {str(e)}"
        )


@router.get(
    "/stats/{content_id}",
    response_model=LikeStatsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "内容不存在"}
    }
)
def get_like_stats(
    content_id: str,
    content_type: str = Query("post", description="内容类型"),
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """获取内容点赞统计"""
    try:
        stats = get_like_service().get_content_like_stats(
            db, content_id, content_type, user_id
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取点赞统计失败: {str(e)}"
        )


@router.get(
    "/history",
    response_model=LikeHistoryResponse,
    responses={
        422: {"model": ErrorResponse, "description": "参数验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def get_like_history(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=50, description="每页数量"),
    content_type: Optional[str] = Query(None, description="筛选内容类型"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取点赞历史"""
    try:
        result = get_like_service().get_user_like_history(
            db, user_id, page, limit, content_type
        )

        # 转换数据格式
        likes_response = [
            LikeResponse.from_orm(like) for like in result["likes"]
        ]

        return LikeHistoryResponse(
            likes=likes_response,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取点赞历史失败: {str(e)}"
        )
