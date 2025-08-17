#!/usr/bin/env python3
"""
资源路由和缓存系统测试
Resource Routing and Caching System Test
"""
import sys
import os
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
import hashlib

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import logging
import datetime

logger = logging.getLogger(__name__)

# 权限级别枚举
class AccessLevel(Enum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    SYSTEM = "system"

# 缓存策略枚举
class CacheStrategy(Enum):
    NO_CACHE = "no_cache"
    SHORT_TERM = "short_term"  # 5分钟
    MEDIUM_TERM = "medium_term"  # 30分钟
    LONG_TERM = "long_term"  # 2小时
    PERSISTENT = "persistent"  # 24小时

# 资源路由配置
@dataclass
class ResourceRoute:
    """资源路由配置"""
    resource_type: str
    handler: Callable
    access_level: AccessLevel = AccessLevel.PUBLIC
    cache_strategy: CacheStrategy = CacheStrategy.MEDIUM_TERM
    rate_limit: Optional[int] = None  # 每分钟请求限制
    dependencies: List[str] = None  # 依赖的其他资源
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

# 访问控制器
class AccessController:
    """资源访问控制器"""
    
    def __init__(self):
        self.user_permissions = {}
        self.rate_limits = {}
        self.access_logs = []
    
    def set_user_permissions(self, user_id: str, permissions: List[AccessLevel]):
        """设置用户权限"""
        self.user_permissions[user_id] = permissions
    
    def check_access(self, user_id: str, required_level: AccessLevel) -> bool:
        """检查访问权限"""
        if required_level == AccessLevel.PUBLIC:
            return True
        
        user_permissions = self.user_permissions.get(user_id, [])
        
        # 权限层级检查
        permission_hierarchy = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.AUTHENTICATED: 1,
            AccessLevel.ADMIN: 2,
            AccessLevel.SYSTEM: 3
        }
        
        required_level_value = permission_hierarchy[required_level]
        user_max_level = max([permission_hierarchy[p] for p in user_permissions], default=0)
        
        return user_max_level >= required_level_value
    
    def check_rate_limit(self, user_id: str, resource_type: str, limit: int) -> bool:
        """检查速率限制"""
        current_time = time.time()
        key = f"{user_id}:{resource_type}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # 清理过期的请求记录（1分钟前）
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if current_time - timestamp < 60
        ]
        
        # 检查是否超过限制
        if len(self.rate_limits[key]) >= limit:
            return False
        
        # 记录当前请求
        self.rate_limits[key].append(current_time)
        return True
    
    def log_access(self, user_id: str, resource_type: str, success: bool, **kwargs):
        """记录访问日志"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "resource_type": resource_type,
            "success": success,
            **kwargs
        }
        self.access_logs.append(log_entry)
        
        # 保持最近1000条记录
        if len(self.access_logs) > 1000:
            self.access_logs = self.access_logs[-1000:]

# 智能缓存管理器
class SmartCacheManager:
    """智能缓存管理器"""
    
    def __init__(self):
        self.cache_data = {}
        self.cache_metadata = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        
        # 缓存策略配置
        self.strategy_config = {
            CacheStrategy.NO_CACHE: {"ttl": 0, "max_size": 0},
            CacheStrategy.SHORT_TERM: {"ttl": 300, "max_size": 100},  # 5分钟
            CacheStrategy.MEDIUM_TERM: {"ttl": 1800, "max_size": 200},  # 30分钟
            CacheStrategy.LONG_TERM: {"ttl": 7200, "max_size": 50},  # 2小时
            CacheStrategy.PERSISTENT: {"ttl": 86400, "max_size": 20}  # 24小时
        }
    
    def _generate_cache_key(self, resource_type: str, resource_id: str, **params) -> str:
        """生成缓存键"""
        # 创建参数的哈希值以确保唯一性
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{resource_type}:{resource_id}:{param_hash}"
    
    def get(self, resource_type: str, resource_id: str, strategy: CacheStrategy, **params) -> Optional[Any]:
        """获取缓存数据"""
        if strategy == CacheStrategy.NO_CACHE:
            return None
        
        cache_key = self._generate_cache_key(resource_type, resource_id, **params)
        
        if cache_key not in self.cache_data:
            self.cache_stats["misses"] += 1
            return None
        
        metadata = self.cache_metadata[cache_key]
        current_time = time.time()
        
        # 检查是否过期
        if current_time - metadata["created_at"] > metadata["ttl"]:
            self._evict(cache_key)
            self.cache_stats["misses"] += 1
            return None
        
        # 更新访问时间
        metadata["last_accessed"] = current_time
        metadata["access_count"] += 1
        
        self.cache_stats["hits"] += 1
        return self.cache_data[cache_key]
    
    def set(self, resource_type: str, resource_id: str, data: Any, strategy: CacheStrategy, **params):
        """设置缓存数据"""
        if strategy == CacheStrategy.NO_CACHE:
            return
        
        cache_key = self._generate_cache_key(resource_type, resource_id, **params)
        config = self.strategy_config[strategy]
        
        # 检查缓存大小限制
        if len(self.cache_data) >= config["max_size"]:
            self._evict_lru(strategy)
        
        current_time = time.time()
        
        self.cache_data[cache_key] = data
        self.cache_metadata[cache_key] = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "strategy": strategy,
            "created_at": current_time,
            "last_accessed": current_time,
            "access_count": 1,
            "ttl": config["ttl"],
            "size": len(json.dumps(data)) if isinstance(data, (dict, list)) else len(str(data))
        }
        
        self.cache_stats["size"] = len(self.cache_data)
    
    def _evict(self, cache_key: str):
        """移除指定缓存项"""
        if cache_key in self.cache_data:
            del self.cache_data[cache_key]
            del self.cache_metadata[cache_key]
            self.cache_stats["evictions"] += 1
            self.cache_stats["size"] = len(self.cache_data)
    
    def _evict_lru(self, strategy: CacheStrategy):
        """移除最少使用的缓存项"""
        # 找到相同策略的最少使用项
        candidates = [
            (key, meta) for key, meta in self.cache_metadata.items()
            if meta["strategy"] == strategy
        ]
        
        if not candidates:
            return
        
        # 按最后访问时间排序，移除最旧的
        lru_key = min(candidates, key=lambda x: x[1]["last_accessed"])[0]
        self._evict(lru_key)
    
    def clear_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, metadata in self.cache_metadata.items():
            if current_time - metadata["created_at"] > metadata["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._evict(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / max(1, total_requests)
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "strategy_distribution": self._get_strategy_distribution()
        }
    
    def _get_strategy_distribution(self) -> Dict[str, int]:
        """获取缓存策略分布"""
        distribution = {}
        for metadata in self.cache_metadata.values():
            strategy = metadata["strategy"].value
            distribution[strategy] = distribution.get(strategy, 0) + 1
        return distribution

# 资源路由器
class ResourceRouter:
    """资源路由器"""
    
    def __init__(self):
        self.routes = {}
        self.access_controller = AccessController()
        self.cache_manager = SmartCacheManager()
        self.performance_monitor = PerformanceMonitor()
        
        # 注册默认路由
        self._register_default_routes()
    
    def register_route(self, route: ResourceRoute):
        """注册资源路由"""
        self.routes[route.resource_type] = route
        logger.info(f"Registered route for resource type: {route.resource_type}")
    
    def _register_default_routes(self):
        """注册默认路由"""
        default_routes = [
            ResourceRoute(
                resource_type="project_state",
                handler=self._handle_project_state,
                access_level=AccessLevel.AUTHENTICATED,
                cache_strategy=CacheStrategy.MEDIUM_TERM,
                rate_limit=60
            ),
            ResourceRoute(
                resource_type="workflow_config",
                handler=self._handle_workflow_config,
                access_level=AccessLevel.PUBLIC,
                cache_strategy=CacheStrategy.LONG_TERM,
                rate_limit=30
            ),
            ResourceRoute(
                resource_type="stage_guide",
                handler=self._handle_stage_guide,
                access_level=AccessLevel.PUBLIC,
                cache_strategy=CacheStrategy.LONG_TERM,
                rate_limit=30
            ),
            ResourceRoute(
                resource_type="system_metrics",
                handler=self._handle_system_metrics,
                access_level=AccessLevel.ADMIN,
                cache_strategy=CacheStrategy.SHORT_TERM,
                rate_limit=10
            )
        ]
        
        for route in default_routes:
            self.register_route(route)
    
    async def get_resource(self, resource_type: str, resource_id: str = "default", 
                          user_id: str = "anonymous", **params) -> Dict[str, Any]:
        """获取资源"""
        start_time = time.time()
        
        try:
            # 检查路由是否存在
            if resource_type not in self.routes:
                raise ValueError(f"Unknown resource type: {resource_type}")
            
            route = self.routes[resource_type]
            
            # 检查访问权限
            if not self.access_controller.check_access(user_id, route.access_level):
                raise PermissionError(f"Access denied for resource: {resource_type}")
            
            # 检查速率限制
            if route.rate_limit and not self.access_controller.check_rate_limit(
                user_id, resource_type, route.rate_limit
            ):
                raise Exception(f"Rate limit exceeded for resource: {resource_type}")
            
            # 尝试从缓存获取
            cached_data = self.cache_manager.get(resource_type, resource_id, route.cache_strategy, **params)
            if cached_data is not None:
                self.access_controller.log_access(user_id, resource_type, True, cache_hit=True)
                self.performance_monitor.record_request(resource_type, time.time() - start_time, True, True)
                return cached_data
            
            # 从处理器获取数据
            resource_data = await route.handler(resource_id, **params)
            
            # 缓存数据
            self.cache_manager.set(resource_type, resource_id, resource_data, route.cache_strategy, **params)
            
            # 记录访问日志
            self.access_controller.log_access(user_id, resource_type, True, cache_hit=False)
            self.performance_monitor.record_request(resource_type, time.time() - start_time, True, False)
            
            return resource_data
            
        except Exception as e:
            # 记录失败访问
            self.access_controller.log_access(user_id, resource_type, False, error=str(e))
            self.performance_monitor.record_request(resource_type, time.time() - start_time, False, False)
            raise
    
    # 默认资源处理器
    async def _handle_project_state(self, resource_id: str, **params) -> Dict[str, Any]:
        """处理项目状态资源"""
        # 模拟异步数据获取
        await asyncio.sleep(0.1)
        
        return {
            "project": {
                "id": resource_id,
                "name": f"Project {resource_id}",
                "status": "active",
                "current_stage": "implementation",
                "quality_score": 0.85,
                "last_updated": datetime.datetime.now().isoformat()
            },
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "cache_strategy": "medium_term",
                "access_level": "authenticated"
            }
        }
    
    async def _handle_workflow_config(self, resource_id: str, **params) -> Dict[str, Any]:
        """处理工作流配置资源"""
        await asyncio.sleep(0.05)
        
        return {
            "workflow": {
                "id": resource_id,
                "name": "Standard AceFlow Workflow",
                "version": "1.0.0",
                "stages": ["initialization", "planning", "implementation", "testing", "deployment"]
            },
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "cache_strategy": "long_term",
                "access_level": "public"
            }
        }
    
    async def _handle_stage_guide(self, resource_id: str, **params) -> Dict[str, Any]:
        """处理阶段指导资源"""
        await asyncio.sleep(0.03)
        
        return {
            "stage": resource_id,
            "title": f"{resource_id.title()} Guide",
            "description": f"Guidance for {resource_id} stage",
            "steps": [
                {"step": 1, "title": "Step 1", "description": "First step"},
                {"step": 2, "title": "Step 2", "description": "Second step"}
            ],
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "cache_strategy": "long_term",
                "access_level": "public"
            }
        }
    
    async def _handle_system_metrics(self, resource_id: str, **params) -> Dict[str, Any]:
        """处理系统指标资源"""
        await asyncio.sleep(0.02)
        
        return {
            "system": {
                "cpu_usage": 0.45,
                "memory_usage": 0.67,
                "disk_usage": 0.23,
                "active_connections": 15
            },
            "cache_stats": self.cache_manager.get_stats(),
            "performance_stats": self.performance_monitor.get_stats(),
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "cache_strategy": "short_term",
                "access_level": "admin"
            }
        }
    
    def get_router_stats(self) -> Dict[str, Any]:
        """获取路由器统计信息"""
        return {
            "registered_routes": len(self.routes),
            "route_types": list(self.routes.keys()),
            "cache_stats": self.cache_manager.get_stats(),
            "performance_stats": self.performance_monitor.get_stats(),
            "access_logs_count": len(self.access_controller.access_logs)
        }

# 性能监控器
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_stats = {}
        self.global_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "total_response_time": 0.0
        }
    
    def record_request(self, resource_type: str, response_time: float, success: bool, cache_hit: bool):
        """记录请求性能"""
        if resource_type not in self.request_stats:
            self.request_stats[resource_type] = {
                "count": 0,
                "success_count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "cache_hits": 0
            }
        
        stats = self.request_stats[resource_type]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["min_time"] = min(stats["min_time"], response_time)
        stats["max_time"] = max(stats["max_time"], response_time)
        
        if success:
            stats["success_count"] += 1
            self.global_stats["successful_requests"] += 1
        else:
            self.global_stats["failed_requests"] += 1
        
        if cache_hit:
            stats["cache_hits"] += 1
            self.global_stats["cache_hits"] += 1
        
        self.global_stats["total_requests"] += 1
        self.global_stats["total_response_time"] += response_time
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        resource_stats = {}
        
        for resource_type, stats in self.request_stats.items():
            avg_time = stats["total_time"] / max(1, stats["count"])
            success_rate = stats["success_count"] / max(1, stats["count"])
            cache_hit_rate = stats["cache_hits"] / max(1, stats["count"])
            
            resource_stats[resource_type] = {
                "count": stats["count"],
                "success_rate": success_rate,
                "avg_response_time": avg_time,
                "min_response_time": stats["min_time"] if stats["min_time"] != float('inf') else 0,
                "max_response_time": stats["max_time"],
                "cache_hit_rate": cache_hit_rate
            }
        
        global_avg_time = self.global_stats["total_response_time"] / max(1, self.global_stats["total_requests"])
        global_success_rate = self.global_stats["successful_requests"] / max(1, self.global_stats["total_requests"])
        global_cache_hit_rate = self.global_stats["cache_hits"] / max(1, self.global_stats["total_requests"])
        
        return {
            "global": {
                "total_requests": self.global_stats["total_requests"],
                "success_rate": global_success_rate,
                "avg_response_time": global_avg_time,
                "cache_hit_rate": global_cache_hit_rate
            },
            "by_resource": resource_stats
        }

# Mock classes for testing
class MockConfig:
    def __init__(self):
        self.data = {"test": True}
    
    def get(self, key, default=None):
        return self.data.get(key, default)

class MockModuleManager:
    def __init__(self):
        self.modules = {}
    
    def get_module(self, name):
        return self.modules.get(name)

class MockUsageMonitor:
    def __init__(self):
        self.records = []
    
    def record_resource_access(self, **kwargs):
        self.records.append(kwargs)

# 测试函数
async def test_resource_routing():
    """测试资源路由功能"""
    print("🧪 Testing Resource Routing...")
    
    router = ResourceRouter()
    
    # 设置用户权限
    router.access_controller.set_user_permissions("user1", [AccessLevel.AUTHENTICATED])
    router.access_controller.set_user_permissions("admin1", [AccessLevel.ADMIN])
    
    # 测试1: 基本资源获取
    print("  Testing basic resource retrieval...")
    resource = await router.get_resource("project_state", "test-project", "user1")
    assert "project" in resource
    assert resource["project"]["id"] == "test-project"
    print("  ✅ Basic resource retrieval test passed")
    
    # 测试2: 缓存功能
    print("  Testing cache functionality...")
    # 第二次请求应该命中缓存
    start_time = time.time()
    resource2 = await router.get_resource("project_state", "test-project", "user1")
    end_time = time.time()
    
    # 缓存命中应该更快
    assert end_time - start_time < 0.01  # 应该很快，因为是缓存
    print("  ✅ Cache functionality test passed")
    
    # 测试3: 权限控制
    print("  Testing access control...")
    try:
        # 匿名用户尝试访问需要认证的资源
        await router.get_resource("project_state", "test-project", "anonymous")
        assert False, "Should have raised PermissionError"
    except PermissionError:
        pass  # 预期的异常
    
    # 管理员访问系统指标
    metrics = await router.get_resource("system_metrics", "default", "admin1")
    assert "system" in metrics
    print("  ✅ Access control test passed")
    
    # 测试4: 速率限制
    print("  Testing rate limiting...")
    # 快速发送多个请求来测试速率限制
    requests_sent = 0
    rate_limited = False
    
    for i in range(15):  # 超过系统指标的限制(10)
        try:
            await router.get_resource("system_metrics", "default", "admin1")
            requests_sent += 1
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                rate_limited = True
                break
    
    assert rate_limited, "Rate limiting should have been triggered"
    print("  ✅ Rate limiting test passed")
    
    print("🎉 All Resource Routing tests passed!")
    return True

async def test_smart_cache():
    """测试智能缓存功能"""
    print("🧪 Testing Smart Cache...")
    
    cache = SmartCacheManager()
    
    # 测试1: 基本缓存操作
    print("  Testing basic cache operations...")
    test_data = {"test": "data", "timestamp": time.time()}
    
    # 设置缓存
    cache.set("test_resource", "test_id", test_data, CacheStrategy.SHORT_TERM)
    
    # 获取缓存
    cached_data = cache.get("test_resource", "test_id", CacheStrategy.SHORT_TERM)
    assert cached_data == test_data
    print("  ✅ Basic cache operations test passed")
    
    # 测试2: 缓存过期
    print("  Testing cache expiration...")
    # 设置一个很短的TTL用于测试
    cache.strategy_config[CacheStrategy.SHORT_TERM]["ttl"] = 1  # 1秒
    
    cache.set("expire_test", "test_id", test_data, CacheStrategy.SHORT_TERM)
    
    # 立即获取应该成功
    cached_data = cache.get("expire_test", "test_id", CacheStrategy.SHORT_TERM)
    assert cached_data == test_data
    
    # 等待过期
    await asyncio.sleep(1.1)
    
    # 现在应该返回None
    cached_data = cache.get("expire_test", "test_id", CacheStrategy.SHORT_TERM)
    assert cached_data is None
    print("  ✅ Cache expiration test passed")
    
    # 测试3: 缓存统计
    print("  Testing cache statistics...")
    stats = cache.get_stats()
    assert "hits" in stats
    assert "misses" in stats
    assert "hit_rate" in stats
    print("  ✅ Cache statistics test passed")
    
    print("🎉 All Smart Cache tests passed!")
    return True

async def test_performance_monitoring():
    """测试性能监控功能"""
    print("🧪 Testing Performance Monitoring...")
    
    monitor = PerformanceMonitor()
    
    # 记录一些测试请求
    monitor.record_request("test_resource", 0.1, True, False)
    monitor.record_request("test_resource", 0.05, True, True)  # 缓存命中
    monitor.record_request("test_resource", 0.2, False, False)  # 失败请求
    monitor.record_request("other_resource", 0.15, True, False)
    
    # 获取统计信息
    stats = monitor.get_stats()
    
    # 验证全局统计
    assert stats["global"]["total_requests"] == 4
    assert stats["global"]["success_rate"] == 0.75  # 3/4
    assert stats["global"]["cache_hit_rate"] == 0.25  # 1/4
    
    # 验证资源级统计
    test_resource_stats = stats["by_resource"]["test_resource"]
    assert test_resource_stats["count"] == 3
    assert test_resource_stats["success_rate"] == 2/3
    assert test_resource_stats["cache_hit_rate"] == 1/3
    
    print("🎉 All Performance Monitoring tests passed!")
    return True

async def main():
    """运行所有测试"""
    print("🚀 Starting Resource Routing and Caching System tests...\n")
    
    try:
        await test_smart_cache()
        await test_performance_monitoring()
        await test_resource_routing()
        
        print("\n🎉 All Resource Routing and Caching System tests passed!")
        print("\n📊 Resource Routing and Caching System Summary:")
        print("   ✅ Smart Cache Management - Working")
        print("   ✅ Performance Monitoring - Working")
        print("   ✅ Resource Routing - Working")
        print("   ✅ Access Control - Working")
        print("   ✅ Rate Limiting - Working")
        print("   ✅ Cache Strategies - Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Resource routing and caching test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🏗️ Task 5.3 - Resource Routing and Caching Implementation Complete!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)