"""
主路由配置
"""
from fastapi import APIRouter

from .favorites import router as favorites_router
from .likes import router as likes_router
from .history import router as history_router
from .health import router as health_router

# 创建主路由
router = APIRouter()

# 包含子路由
router.include_router(favorites_router, prefix="/api/v1")
router.include_router(likes_router, prefix="/api/v1")
router.include_router(history_router, prefix="/api/v1")
router.include_router(health_router)
