"""
数据访问控制器
Access Controller

实现基于角色的访问控制和速率限制，保护资源安全。
"""
from typing import Dict, Any, Optional, Set
import logging
import time

logger = logging.getLogger(__name__)

class AccessController:
    """
    数据访问控制器
    - 基于角色的访问权限
    - 速率限制
    """
    def __init__(self):
        self._user_roles: Dict[str, Set[str]] = {}
        self._resource_permissions: Dict[str, Set[str]] = {}
        self._access_log: Dict[str, list] = {}
        self._rate_limits: Dict[str, int] = {}
        self._rate_window: int = 60  # 秒
        logger.info("Access controller initialized")

    def set_user_roles(self, user_id: str, roles: Set[str]):
        self._user_roles[user_id] = roles

    def set_resource_permissions(self, resource: str, allowed_roles: Set[str]):
        self._resource_permissions[resource] = allowed_roles

    def check_permission(self, user_id: str, resource: str) -> bool:
        roles = self._user_roles.get(user_id, set())
        allowed = self._resource_permissions.get(resource, set())
        result = bool(roles & allowed)
        logger.debug(f"Permission check for {user_id} on {resource}: {result}")
        return result

    def enforce_rate_limiting(self, user_id: str, max_requests: int = 100) -> bool:
        now = int(time.time())
        window_start = now - self._rate_window
        log = self._access_log.setdefault(user_id, [])
        # 清理过期访问记录
        log = [t for t in log if t > window_start]
        self._access_log[user_id] = log
        if len(log) >= max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        log.append(now)
        return True

    def log_access_attempt(self, user_id: str, resource: str):
        logger.info(f"Access attempt: user={user_id}, resource={resource}")
