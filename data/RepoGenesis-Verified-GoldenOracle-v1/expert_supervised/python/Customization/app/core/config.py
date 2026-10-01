"""
应用配置管理
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用设置"""

    # API配置
    api_host: str = Field(default="0.0.0.0", description="API服务主机地址")
    api_port: int = Field(default=8082, description="API服务端口")
    api_reload: bool = Field(default=False, description="是否开启热重载")
    api_workers: int = Field(default=1, description="工作进程数")

    # 安全配置
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间")

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./customization.db",
        description="数据库连接URL"
    )
    database_pool_size: int = Field(default=10, description="数据库连接池大小")
    database_max_overflow: int = Field(default=20, description="数据库连接池最大溢出")

    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379", description="Redis连接URL")
    redis_pool_size: int = Field(default=10, description="Redis连接池大小")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )

    # 跨域配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的跨域源"
    )
    cors_allow_credentials: bool = Field(default=True, description="是否允许携带凭证")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="允许的HTTP方法"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="允许的HTTP头"
    )

    # 文件上传配置
    max_upload_size: int = Field(default=10485760, description="最大上传文件大小（字节）")
    allowed_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif"],
        description="允许的文件扩展名"
    )

    # 分页配置
    default_page_size: int = Field(default=20, description="默认分页大小")
    max_page_size: int = Field(default=100, description="最大分页大小")

    # 缓存配置
    cache_ttl: int = Field(default=300, description="缓存过期时间（秒）")

    # 健康检查配置
    health_check_path: str = Field(default="/health", description="健康检查路径")

    # 项目信息
    project_name: str = Field(default="个性化设置API", description="项目名称")
    project_description: str = Field(default="用户个性化功能管理微服务", description="项目描述")
    project_version: str = Field(default="1.0.0", description="项目版本")

    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局设置实例
settings = Settings()
