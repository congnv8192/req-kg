"""
中间件配置
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .config import settings

logger = logging.getLogger(__name__)


def create_middleware(app):
    """创建和配置中间件"""

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # 可信主机中间件（生产环境启用）
    if hasattr(settings, 'trusted_hosts') and settings.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts,
        )


from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # 记录请求开始
        logger.info(
            f"请求开始: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求完成
            logger.info(
                f"请求完成: {request.method} {request.url.path} "
                f"status={response.status_code} time={process_time:.3f}s"
            )

            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"请求异常: {request.method} {request.url.path} "
                f"error={str(e)} time={process_time:.3f}s"
            )
            raise


def add_logging_middleware(app):
    """添加日志中间件"""
    app.add_middleware(LoggingMiddleware)
