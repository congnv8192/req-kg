"""
主应用文件
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.middleware import create_middleware, add_logging_middleware
from .api.router import router
from .models.database import init_db


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

    yield

    # 关闭时执行
    logger.info("应用关闭中...")


def create_application() -> FastAPI:
    """创建FastAPI应用"""

    # 创建应用实例
    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # 添加中间件
    create_middleware(app)
    add_logging_middleware(app)

    # 包含路由
    app.include_router(router)

    # 根路径处理
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "个性化设置API服务",
            "version": settings.project_version,
            "docs": "/docs"
        }

    # 自定义404处理
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc):
        """404错误处理"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"路径 {request.url.path} 不存在",
                "path": str(request.url.path)
            }
        )

    # 自定义500处理
    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc):
        """500错误处理"""
        logger.error(f"内部服务器错误: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "服务器内部错误，请稍后重试"
            }
        )

    # 自定义验证错误处理
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """参数验证错误处理"""
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "请求参数验证失败",
                "detail": [
                    {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
                    for err in exc.errors()
                ]
            }
        )

    return app


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers if not settings.api_reload else 1,
        log_level=settings.log_level.lower(),
        access_log=True
    )
