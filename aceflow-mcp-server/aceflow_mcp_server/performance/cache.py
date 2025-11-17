"""
统一缓存管理器
Unified Cache Manager

支持配置数据缓存、状态数据缓存、智能缓存策略和失效机制。
"""
import time
import threading
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheItem:
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl

class CacheManager:
    """
    统一缓存管理器
    - 支持配置和状态数据缓存
    - 智能缓存策略
    - 缓存失效机制
    """
    def __init__(self):
        self._cache: Dict[str, CacheItem] = {}
        self._lock = threading.Lock()
        self._stats = {
            'total_sets': 0,
            'total_gets': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        logger.info("Cache manager initialized")

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        with self._lock:
            self._cache[key] = CacheItem(value, ttl)
            self._stats['total_sets'] += 1
            logger.debug(f"Cache set: {key}")

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._stats['total_gets'] += 1
            item = self._cache.get(key)
            if item and not item.is_expired():
                self._stats['cache_hits'] += 1
                logger.debug(f"Cache hit: {key}")
                return item.value
            if item:
                logger.debug(f"Cache expired: {key}")
                del self._cache[key]
            self._stats['cache_misses'] += 1
            logger.debug(f"Cache miss: {key}")
            return None

    def delete(self, key: str):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache deleted: {key}")

    def cleanup(self):
        with self._lock:
            expired = [k for k, v in self._cache.items() if v.is_expired()]
            for k in expired:
                del self._cache[k]
                logger.debug(f"Cache cleaned: {k}")

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_items': len(self._cache),
                'expired_items': sum(1 for v in self._cache.values() if v.is_expired()),
                **self._stats
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Alias for get_stats for consistency"""
        return self.get_stats()
    
    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)
