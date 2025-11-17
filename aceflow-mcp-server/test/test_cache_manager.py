"""
统一缓存管理器测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aceflow_mcp_server.performance.cache import CacheManager
import time

def test_cache_basic():
    cache = CacheManager()
    cache.set('key1', 'value1', ttl=0.1)
    assert cache.get('key1') == 'value1'
    time.sleep(0.2)
    assert cache.get('key1') is None
    cache.set('key2', 'value2')
    assert cache.get('key2') == 'value2'
    cache.delete('key2')
    assert cache.get('key2') is None
    print("Cache basic test passed.")

def test_cache_stats():
    cache = CacheManager()
    cache.set('a', 1)
    cache.set('b', 2, ttl=0.05)
    time.sleep(0.1)
    cache.cleanup()
    stats = cache.get_stats()
    print("Cache stats:", stats)

if __name__ == "__main__":
    test_cache_basic()
    test_cache_stats()
