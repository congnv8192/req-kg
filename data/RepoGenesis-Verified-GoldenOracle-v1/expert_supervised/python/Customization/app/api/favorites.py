"""
收藏API路由
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.dependencies import get_db, get_current_user_id
from ..models.models import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteListResponse,
    ErrorResponse
)
from ..services.favorite_service import get_favorite_service

router = APIRouter(prefix="/favorites", tags=["收藏管理"])


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "数据验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def add_favorite(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """添加收藏"""
    try:
        favorite = get_favorite_service().create_favorite(db, user_id, favorite_data)
        return FavoriteResponse.from_orm(favorite)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加收藏失败: {str(e)}"
        )


@router.get(
    "",
    response_model=FavoriteListResponse,
    responses={
        422: {"model": ErrorResponse, "description": "参数验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def get_favorites(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    content_type: Optional[str] = Query(None, description="筛选内容类型"),
    category: Optional[str] = Query(None, description="筛选分类标签"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取收藏列表"""
    try:
        result = get_favorite_service().get_user_favorites(
            db, user_id, page, limit, content_type, category
        )

        # 转换数据格式
        favorites_response = [
            FavoriteResponse.from_orm(favorite) for favorite in result["favorites"]
        ]

        return FavoriteListResponse(
            favorites=favorites_response,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏列表失败: {str(e)}"
        )


@router.delete(
    "/{favorite_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "收藏不存在"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def delete_favorite(
    favorite_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """删除收藏"""
    try:
        success = get_favorite_service().delete_favorite(db, user_id, favorite_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏不存在"
            )

        return {"message": "收藏删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除收藏失败: {str(e)}"
        )
