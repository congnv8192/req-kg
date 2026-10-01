"""
历史记录API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from ..core.dependencies import get_db, get_current_user_id
from ..models.models import (
    HistoryCreate,
    HistoryResponse,
    HistoryListResponse,
    ErrorResponse
)
from ..services.history_service import get_history_service

router = APIRouter(prefix="/history", tags=["历史记录管理"])


@router.post(
    "",
    response_model=HistoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "数据验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def record_history(
    history_data: HistoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """记录用户操作历史"""
    try:
        # 获取客户端IP和User-Agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        history = get_history_service().create_history(
            db, user_id, history_data, ip_address, user_agent
        )
        return HistoryResponse.from_orm(history)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录历史失败: {str(e)}"
        )


@router.get(
    "",
    response_model=HistoryListResponse,
    responses={
        422: {"model": ErrorResponse, "description": "参数验证失败"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def get_history(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    action: Optional[str] = Query(None, description="筛选操作类型"),
    content_type: Optional[str] = Query(None, description="筛选内容类型"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    session_id: Optional[str] = Query(None, description="筛选会话ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取历史记录"""
    try:
        # 转换日期字符串为datetime对象
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                from datetime import datetime
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="开始日期格式无效，应为YYYY-MM-DD"
                )

        if end_date:
            try:
                from datetime import datetime
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="结束日期格式无效，应为YYYY-MM-DD"
                )

        result = get_history_service().get_user_history(
            db, user_id, page, limit, action, content_type,
            start_datetime, end_datetime, session_id
        )

        # 转换数据格式
        history_response = [
            HistoryResponse.from_orm(history) for history in result["history"]
        ]

        return HistoryListResponse(
            history=history_response,
            pagination=result["pagination"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录失败: {str(e)}"
        )


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "历史记录不存在"},
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def delete_history(
    history_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """删除单个历史记录"""
    try:
        success = get_history_service().delete_history(db, user_id, history_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史记录不存在"
            )

        return {"message": "历史记录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除历史记录失败: {str(e)}"
        )


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
def clear_history(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """清空所有历史记录"""
    try:
        deleted_count = get_history_service().clear_user_history(db, user_id)

        return {
            "message": "历史记录清空成功",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空历史记录失败: {str(e)}"
        )
