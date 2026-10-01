"""
通用工具函数
"""
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """获取当前时间戳"""
    return datetime.now(timezone.utc)


def validate_content_type(content_type: str) -> bool:
    """验证内容类型"""
    valid_types = ["post", "article", "product", "video"]
    return content_type in valid_types


def validate_action_type(action: str) -> bool:
    """验证操作类型"""
    valid_actions = {
        "like": ["like", "unlike"],
        "history": ["view", "search", "share", "download"]
    }

    for actions in valid_actions.values():
        if action in actions:
            return True
    return False


def format_pagination_meta(page: int, limit: int, total: int) -> Dict[str, Any]:
    """格式化分页元信息"""
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages
    }


def sanitize_string(value: str, max_length: int = 255) -> str:
    """清理字符串，去除空白字符并限制长度"""
    if not value:
        return ""

    # 去除首尾空白
    cleaned = value.strip()

    # 限制长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def is_valid_uuid(value: str) -> bool:
    """验证UUID格式"""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def get_client_ip(request) -> Optional[str]:
    """获取客户端真实IP"""
    # 检查X-Forwarded-For头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 取第一个IP（最原始的客户端IP）
        return forwarded_for.split(",")[0].strip()

    # 检查X-Real-IP头
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 直接获取客户端IP
    if request.client:
        return request.client.host

    return None
