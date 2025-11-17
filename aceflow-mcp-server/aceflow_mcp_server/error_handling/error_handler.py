"""
统一错误处理系统
Unified Error Handling System

提供统一的错误分类、错误恢复、优雅降级和错误日志记录机制。
"""

import logging
import traceback
import time
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
import threading
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    CRITICAL = "critical"    # 系统级错误，需要立即处理
    HIGH = "high"           # 高严重度错误，影响主要功能
    MEDIUM = "medium"       # 中等错误，影响部分功能
    LOW = "low"            # 轻微错误，不影响主要功能
    INFO = "info"          # 信息性错误，仅记录


class ErrorCategory(Enum):
    """错误分类"""
    CONFIGURATION = "configuration"     # 配置错误
    MODULE_LOADING = "module_loading"   # 模块加载错误
    DEPENDENCY = "dependency"           # 依赖错误
    VALIDATION = "validation"           # 验证错误
    EXECUTION = "execution"             # 执行错误
    NETWORK = "network"                 # 网络错误
    PERMISSION = "permission"           # 权限错误
    RESOURCE = "resource"               # 资源错误
    TIMEOUT = "timeout"                 # 超时错误
    UNKNOWN = "unknown"                 # 未知错误


@dataclass
class ErrorContext:
    """错误上下文信息"""
    module_name: Optional[str] = None
    function_name: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """错误记录"""
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: str
    context: ErrorContext
    traceback_info: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0


class RecoveryStrategy:
    """错误恢复策略"""
    
    def __init__(self, name: str, recovery_func: Callable, max_retries: int = 3):
        self.name = name
        self.recovery_func = recovery_func
        self.max_retries = max_retries
    
    def attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """
        尝试错误恢复
        
        Args:
            error_record: 错误记录
            
        Returns:
            恢复是否成功
        """
        try:
            success = self.recovery_func(error_record)
            if success:
                logger.info(f"Error recovery successful using strategy: {self.name}")
            return success
        except Exception as e:
            logger.error(f"Error recovery failed for strategy {self.name}: {e}")
            return False


class ErrorHandler:
    """
    统一错误处理器
    
    提供错误分类、记录、恢复和降级处理功能。
    """
    
    def __init__(self):
        self._error_records: Dict[str, ErrorRecord] = {}
        self._recovery_strategies: Dict[ErrorCategory, List[RecoveryStrategy]] = {}
        self._degradation_handlers: Dict[ErrorCategory, Callable] = {}
        self._error_listeners: List[Callable[[ErrorRecord], None]] = []
        self._lock = threading.Lock()
        self._error_counter = 0
        
        # 统计信息
        self._stats = {
            "total_errors": 0,
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "errors_by_category": {category.value: 0 for category in ErrorCategory},
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        
        logger.info("Error handler initialized")
    
    def register_recovery_strategy(
        self, 
        category: ErrorCategory, 
        strategy: RecoveryStrategy
    ):
        """
        注册错误恢复策略
        
        Args:
            category: 错误分类
            strategy: 恢复策略
        """
        if category not in self._recovery_strategies:
            self._recovery_strategies[category] = []
        
        self._recovery_strategies[category].append(strategy)
        logger.info(f"Registered recovery strategy '{strategy.name}' for category {category.value}")
    
    def register_degradation_handler(
        self, 
        category: ErrorCategory, 
        handler: Callable
    ):
        """
        注册降级处理器
        
        Args:
            category: 错误分类
            handler: 降级处理函数
        """
        self._degradation_handlers[category] = handler
        logger.info(f"Registered degradation handler for category {category.value}")
    
    def add_error_listener(self, listener: Callable[[ErrorRecord], None]):
        """
        添加错误监听器
        
        Args:
            listener: 错误监听函数
        """
        self._error_listeners.append(listener)
        logger.info("Added error listener")
    
    def handle_error(
        self, 
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        attempt_recovery: bool = True
    ) -> ErrorRecord:
        """
        处理错误
        
        Args:
            exception: 异常对象
            severity: 错误严重程度
            category: 错误分类
            context: 错误上下文
            attempt_recovery: 是否尝试恢复
            
        Returns:
            错误记录
        """
        with self._lock:
            self._error_counter += 1
            error_id = f"ERR_{int(time.time())}_{self._error_counter}"
        
        # 创建错误记录
        error_record = ErrorRecord(
            error_id=error_id,
            timestamp=time.time(),
            severity=severity,
            category=category,
            message=str(exception),
            details=repr(exception),
            context=context or ErrorContext(),
            traceback_info=traceback.format_exc()
        )
        
        # 记录错误
        self._record_error(error_record)
        
        # 通知监听器
        self._notify_listeners(error_record)
        
        # 尝试恢复
        if attempt_recovery:
            self._attempt_recovery(error_record)
        
        # 如果恢复失败，尝试降级处理
        if not error_record.recovery_successful:
            self._attempt_degradation(error_record)
        
        return error_record
    
    def _record_error(self, error_record: ErrorRecord):
        """记录错误到存储"""
        with self._lock:
            self._error_records[error_record.error_id] = error_record
            
            # 更新统计信息
            self._stats["total_errors"] += 1
            self._stats["errors_by_severity"][error_record.severity.value] += 1
            self._stats["errors_by_category"][error_record.category.value] += 1
        
        # 记录到日志
        log_level = self._get_log_level(error_record.severity)
        logger.log(log_level, 
            f"Error {error_record.error_id}: [{error_record.category.value}] "
            f"{error_record.message}"
        )
    
    def _notify_listeners(self, error_record: ErrorRecord):
        """通知错误监听器"""
        for listener in self._error_listeners:
            try:
                listener(error_record)
            except Exception as e:
                logger.warning(f"Error listener failed: {e}")
    
    def _attempt_recovery(self, error_record: ErrorRecord):
        """尝试错误恢复"""
        strategies = self._recovery_strategies.get(error_record.category, [])
        
        for strategy in strategies:
            if error_record.retry_count >= strategy.max_retries:
                continue
            
            error_record.recovery_attempted = True
            error_record.retry_count += 1
            
            with self._lock:
                self._stats["recovery_attempts"] += 1
            
            success = strategy.attempt_recovery(error_record)
            if success:
                error_record.recovery_successful = True
                with self._lock:
                    self._stats["successful_recoveries"] += 1
                break
    
    def _attempt_degradation(self, error_record: ErrorRecord):
        """尝试降级处理"""
        handler = self._degradation_handlers.get(error_record.category)
        if handler:
            try:
                handler(error_record)
                logger.info(f"Applied degradation handling for error {error_record.error_id}")
            except Exception as e:
                logger.error(f"Degradation handling failed: {e}")
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        level_mapping = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.INFO: logging.DEBUG
        }
        return level_mapping.get(severity, logging.INFO)
    
    def get_error_record(self, error_id: str) -> Optional[ErrorRecord]:
        """获取错误记录"""
        return self._error_records.get(error_id)
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """获取最近的错误记录"""
        sorted_errors = sorted(
            self._error_records.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_errors[:count]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        with self._lock:
            return self._stats.copy()
    
    def clear_old_errors(self, max_age_hours: float = 24):
        """清理旧的错误记录"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self._lock:
            to_remove = [
                error_id for error_id, record in self._error_records.items()
                if record.timestamp < cutoff_time
            ]
            
            for error_id in to_remove:
                del self._error_records[error_id]
        
        if to_remove:
            logger.info(f"Cleared {len(to_remove)} old error records")


def error_handler_decorator(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.EXECUTION,
    context_func: Optional[Callable[[], ErrorContext]] = None,
    reraise: bool = False
):
    """
    错误处理装饰器
    
    Args:
        severity: 错误严重程度
        category: 错误分类
        context_func: 上下文生成函数
        reraise: 是否重新抛出异常
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = context_func() if context_func else ErrorContext(
                    function_name=func.__name__
                )
                
                error_handler = get_error_handler()
                error_record = error_handler.handle_error(
                    exception=e,
                    severity=severity,
                    category=category,
                    context=context
                )
                
                if reraise:
                    raise
                
                return None
        return wrapper
    return decorator


# 全局错误处理器实例
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器实例"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def reset_error_handler():
    """重置全局错误处理器实例"""
    global _global_error_handler
    _global_error_handler = None


# 常用的恢复策略
def create_retry_strategy(name: str, max_retries: int = 3) -> RecoveryStrategy:
    """创建重试策略"""
    def retry_func(error_record: ErrorRecord) -> bool:
        # 简单的重试逻辑，实际使用时应该更复杂
        return error_record.retry_count < max_retries
    
    return RecoveryStrategy(name, retry_func, max_retries)


def create_fallback_strategy(name: str, fallback_func: Callable) -> RecoveryStrategy:
    """创建回退策略"""
    def recovery_func(error_record: ErrorRecord) -> bool:
        try:
            fallback_func(error_record)
            return True
        except Exception:
            return False
    
    return RecoveryStrategy(name, recovery_func, 1)


# 在ErrorHandler类中添加装饰器方法
def _add_decorator_methods():
    """为ErrorHandler类添加装饰器方法"""
    import functools
    
    def handle_errors(self, func):
        """装饰器：处理函数执行中的错误"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 处理错误
                context = ErrorContext(
                    module=func.__module__,
                    function=func.__name__,
                    args=str(args),
                    kwargs=str(kwargs)
                )
                
                self.handle_error(
                    exception=e,
                    context=context,
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.RUNTIME_ERROR
                )
                
                # 返回None或抛出异常，根据配置决定
                return None
        
        return wrapper
    
    def monitor_errors(self, category: ErrorCategory = ErrorCategory.EXECUTION):
        """装饰器：监控函数错误并分类"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = ErrorContext(
                        module=func.__module__,
                        function=func.__name__,
                        args=str(args),
                        kwargs=str(kwargs)
                    )
                    
                    self.handle_error(
                        exception=e,
                        context=context,
                        severity=ErrorSeverity.MEDIUM,
                        category=category,
                        attempt_recovery=True
                    )
                    raise  # 重新抛出异常
            
            return wrapper
        return decorator
    
    # 将方法绑定到ErrorHandler类
    ErrorHandler.handle_errors = handle_errors
    ErrorHandler.monitor_errors = monitor_errors

# 执行绑定
_add_decorator_methods()
