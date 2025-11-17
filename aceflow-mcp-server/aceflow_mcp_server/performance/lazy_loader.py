"""
懒加载管理器
Lazy Loading Manager

实现模块的按需加载、预加载和智能缓存机制，优化启动时间和内存使用。
"""

import asyncio
import time
import threading
from typing import Dict, List, Set, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, Future
import weakref

logger = logging.getLogger(__name__)


class LoadStrategy(Enum):
    """加载策略"""
    LAZY = "lazy"                    # 懒加载：首次使用时加载
    PRELOAD = "preload"              # 预加载：启动时异步加载
    EAGER = "eager"                  # 立即加载：启动时同步加载
    CONDITIONAL = "conditional"       # 条件加载：基于配置决定


class LoadPriority(Enum):
    """加载优先级"""
    CRITICAL = 1     # 关键模块，最高优先级
    HIGH = 2         # 高优先级
    NORMAL = 3       # 正常优先级
    LOW = 4          # 低优先级
    BACKGROUND = 5   # 后台加载


@dataclass
class LoadingProfile:
    """加载配置文件"""
    strategy: LoadStrategy = LoadStrategy.LAZY
    priority: LoadPriority = LoadPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[Callable[[], bool]] = None
    timeout_seconds: float = 30.0
    retry_count: int = 3
    cache_ttl_seconds: Optional[float] = None


@dataclass
class LoadingStats:
    """加载统计信息"""
    module_name: str
    load_started_at: Optional[float] = None
    load_completed_at: Optional[float] = None
    load_duration: float = 0.0
    load_attempts: int = 0
    last_access_time: Optional[float] = None
    access_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage_mb: float = 0.0


class LazyLoader:
    """
    懒加载管理器
    
    提供智能的模块加载策略，包括：
    - 按需懒加载
    - 智能预加载
    - 加载优先级管理
    - 依赖关系处理
    - 性能监控和统计
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 模块加载器注册表
        self._loaders: Dict[str, Callable[[], Any]] = {}
        self._profiles: Dict[str, LoadingProfile] = {}
        
        # 加载状态管理
        self._loaded_modules: Dict[str, Any] = {}
        self._loading_futures: Dict[str, Future] = {}
        self._loading_locks: Dict[str, threading.Lock] = {}
        
        # 统计信息
        self._stats: Dict[str, LoadingStats] = {}
        
        # 缓存管理
        self._cache_refs: Dict[str, weakref.ref] = {}
        
        # 预加载管理
        self._preload_queue: List[str] = []
        self._preload_running = False
        
        logger.info("Lazy loader initialized")
    
    def register_loader(
        self,
        module_name: str,
        loader_func: Callable[[], Any],
        profile: Optional[LoadingProfile] = None
    ):
        """
        注册模块加载器
        
        Args:
            module_name: 模块名称
            loader_func: 加载函数
            profile: 加载配置
        """
        self._loaders[module_name] = loader_func
        self._profiles[module_name] = profile or LoadingProfile()
        self._stats[module_name] = LoadingStats(module_name=module_name)
        self._loading_locks[module_name] = threading.Lock()
        
        logger.debug(f"Registered loader for module: {module_name}")
        
        # 根据策略决定是否立即处理
        strategy = self._profiles[module_name].strategy
        if strategy == LoadStrategy.EAGER:
            self.load_module(module_name)
        elif strategy == LoadStrategy.PRELOAD:
            self._schedule_preload(module_name)
    
    def load_module(self, module_name: str, force_reload: bool = False) -> Any:
        """
        加载模块
        
        Args:
            module_name: 模块名称
            force_reload: 是否强制重新加载
            
        Returns:
            加载的模块实例
        """
        # 更新访问统计
        stats = self._stats.get(module_name)
        if stats:
            stats.last_access_time = time.time()
            stats.access_count += 1
        
        # 检查是否已加载
        if not force_reload and module_name in self._loaded_modules:
            if stats:
                stats.cache_hits += 1
            return self._loaded_modules[module_name]
        
        if stats:
            stats.cache_misses += 1
        
        # 检查是否正在加载
        if module_name in self._loading_futures:
            future = self._loading_futures[module_name]
            if not future.done():
                logger.info(f"Waiting for module '{module_name}' to complete loading...")
                try:
                    timeout = self._profiles[module_name].timeout_seconds
                    return future.result(timeout=timeout)
                except Exception as e:
                    logger.error(f"Failed to wait for module '{module_name}': {e}")
                    raise
        
        # 使用锁防止并发加载
        with self._loading_locks[module_name]:
            # 双重检查
            if not force_reload and module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            return self._do_load_module(module_name)
    
    def _do_load_module(self, module_name: str) -> Any:
        """
        执行模块加载
        
        Args:
            module_name: 模块名称
            
        Returns:
            加载的模块实例
        """
        if module_name not in self._loaders:
            raise ValueError(f"No loader registered for module: {module_name}")
        
        stats = self._stats[module_name]
        profile = self._profiles[module_name]
        loader = self._loaders[module_name]
        
        # 检查条件加载
        if profile.condition and not profile.condition():
            logger.info(f"Skipping module '{module_name}' due to condition check")
            return None
        
        # 检查依赖
        self._ensure_dependencies(module_name)
        
        logger.info(f"Loading module: {module_name}")
        start_time = time.time()
        stats.load_started_at = start_time
        stats.load_attempts += 1
        
        try:
            # 执行加载
            module = loader()
            
            # 记录统计信息
            end_time = time.time()
            stats.load_completed_at = end_time
            stats.load_duration = end_time - start_time
            
            # 缓存模块
            self._loaded_modules[module_name] = module
            
            # 创建弱引用用于缓存管理
            if profile.cache_ttl_seconds:
                self._cache_refs[module_name] = weakref.ref(module)
            
            logger.info(f"Module '{module_name}' loaded successfully in {stats.load_duration:.3f}s")
            return module
            
        except Exception as e:
            logger.error(f"Failed to load module '{module_name}': {e}")
            # 重试机制
            if stats.load_attempts < profile.retry_count:
                logger.info(f"Retrying to load module '{module_name}' (attempt {stats.load_attempts + 1})")
                time.sleep(0.1)  # 短暂延迟
                return self._do_load_module(module_name)
            else:
                raise
    
    def _ensure_dependencies(self, module_name: str):
        """
        确保依赖模块已加载
        
        Args:
            module_name: 模块名称
        """
        profile = self._profiles[module_name]
        for dep in profile.dependencies:
            if dep not in self._loaded_modules:
                logger.info(f"Loading dependency '{dep}' for module '{module_name}'")
                self.load_module(dep)
    
    def _schedule_preload(self, module_name: str):
        """
        调度预加载
        
        Args:
            module_name: 模块名称
        """
        if module_name not in self._preload_queue:
            priority = self._profiles[module_name].priority
            
            # 按优先级插入队列
            inserted = False
            for i, existing_module in enumerate(self._preload_queue):
                existing_priority = self._profiles[existing_module].priority
                if priority.value < existing_priority.value:
                    self._preload_queue.insert(i, module_name)
                    inserted = True
                    break
            
            if not inserted:
                self._preload_queue.append(module_name)
        
        # 启动预加载处理器
        if not self._preload_running:
            self._start_preload_processor()
    
    def _start_preload_processor(self):
        """启动预加载处理器"""
        if self._preload_running:
            return
        
        self._preload_running = True
        
        def preload_worker():
            """预加载工作线程"""
            while self._preload_queue and self._preload_running:
                module_name = self._preload_queue.pop(0)
                try:
                    if module_name not in self._loaded_modules:
                        future = self._executor.submit(self._do_load_module, module_name)
                        self._loading_futures[module_name] = future
                        logger.info(f"Started preloading module: {module_name}")
                except Exception as e:
                    logger.error(f"Preload failed for module '{module_name}': {e}")
            
            self._preload_running = False
        
        threading.Thread(target=preload_worker, daemon=True).start()
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
        获取模块（懒加载）
        
        Args:
            module_name: 模块名称
            
        Returns:
            模块实例或None
        """
        try:
            return self.load_module(module_name)
        except Exception as e:
            logger.error(f"Failed to get module '{module_name}': {e}")
            return None
    
    def unload_module(self, module_name: str):
        """
        卸载模块
        
        Args:
            module_name: 模块名称
        """
        if module_name in self._loaded_modules:
            module = self._loaded_modules.pop(module_name)
            
            # 清理缓存引用
            if module_name in self._cache_refs:
                del self._cache_refs[module_name]
            
            # 调用模块清理方法（如果有的话）
            if hasattr(module, 'cleanup'):
                try:
                    module.cleanup()
                except Exception as e:
                    logger.warning(f"Module cleanup failed for '{module_name}': {e}")
            
            logger.info(f"Unloaded module: {module_name}")
    
    def preload_all(self):
        """预加载所有配置为预加载的模块"""
        for module_name, profile in self._profiles.items():
            if profile.strategy == LoadStrategy.PRELOAD:
                self._schedule_preload(module_name)
    
    def get_loading_stats(self) -> Dict[str, LoadingStats]:
        """获取加载统计信息"""
        return self._stats.copy()
    
    def get_loaded_modules(self) -> List[str]:
        """获取已加载的模块列表"""
        return list(self._loaded_modules.keys())
    
    def is_module_loaded(self, module_name: str) -> bool:
        """检查模块是否已加载"""
        return module_name in self._loaded_modules
    
    def cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        to_remove = []
        
        for module_name, ref in self._cache_refs.items():
            profile = self._profiles[module_name]
            stats = self._stats[module_name]
            
            # 检查TTL
            if (profile.cache_ttl_seconds and 
                stats.last_access_time and 
                current_time - stats.last_access_time > profile.cache_ttl_seconds):
                to_remove.append(module_name)
            # 检查弱引用
            elif ref() is None:
                to_remove.append(module_name)
        
        for module_name in to_remove:
            self.unload_module(module_name)
    
    def shutdown(self):
        """关闭懒加载器"""
        self._preload_running = False
        
        # 关闭线程池
        self._executor.shutdown(wait=True)
        
        # 清理所有模块
        for module_name in list(self._loaded_modules.keys()):
            self.unload_module(module_name)
        
        logger.info("Lazy loader shutdown completed")


# 全局懒加载器实例
_global_lazy_loader: Optional[LazyLoader] = None


def get_lazy_loader() -> LazyLoader:
    """获取全局懒加载器实例"""
    global _global_lazy_loader
    if _global_lazy_loader is None:
        _global_lazy_loader = LazyLoader()
    return _global_lazy_loader


def reset_lazy_loader():
    """重置全局懒加载器实例"""
    global _global_lazy_loader
    if _global_lazy_loader:
        _global_lazy_loader.shutdown()
    _global_lazy_loader = None
