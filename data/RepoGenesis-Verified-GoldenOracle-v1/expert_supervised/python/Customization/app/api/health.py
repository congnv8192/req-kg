"""
健康检查API路由
"""
from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter(tags=["健康检查"])


@router.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "个性化设置API"
    }
