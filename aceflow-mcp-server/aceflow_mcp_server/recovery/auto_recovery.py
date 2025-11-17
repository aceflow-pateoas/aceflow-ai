"""
自动恢复器
Auto Recovery

实现自动故障恢复机制，当检测到故障时自动执行恢复策略。
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import threading
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .fault_detector import FaultEvent, FaultType, FaultSeverity

logger = logging.getLogger(__name__)

class RecoveryAction(Enum):
    """恢复动作"""
    RESTART_COMPONENT = "restart_component"
    CLEAR_CACHE = "clear_cache"
    INCREASE_RESOURCES = "increase_resources"
    THROTTLE_REQUESTS = "throttle_requests"
    FALLBACK_MODE = "fallback_mode"
    CIRCUIT_BREAKER = "circuit_breaker"
    GARBAGE_COLLECTION = "garbage_collection"
    RECONNECT = "reconnect"
    ALERT_ADMIN = "alert_admin"
    GRACEFUL_SHUTDOWN = "graceful_shutdown"

class RecoveryStatus(Enum):
    """恢复状态"""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"

@dataclass
class RecoveryResult:
    """恢复结果"""
    action: RecoveryAction
    status: RecoveryStatus
    timestamp: float
    duration: float
    message: str
    metrics_before: Dict[str, Any]
    metrics_after: Optional[Dict[str, Any]] = None

class RecoveryStrategy(ABC):
    """恢复策略基类"""
    
    @abstractmethod
    def can_handle(self, fault: FaultEvent) -> bool:
        """判断是否能处理该故障"""
        pass
    
    @abstractmethod
    def recover(self, fault: FaultEvent) -> RecoveryResult:
        """执行恢复操作"""
        pass

class PerformanceRecoveryStrategy(RecoveryStrategy):
    """性能恢复策略"""
    
    def __init__(self):
        self.cache_clear_callback: Optional[Callable] = None
        self.throttle_callback: Optional[Callable] = None

    def can_handle(self, fault: FaultEvent) -> bool:
        """判断是否能处理性能故障"""
        return fault.fault_type in [
            FaultType.PERFORMANCE_DEGRADATION,
            FaultType.RESOURCE_EXHAUSTION
        ]

    def recover(self, fault: FaultEvent) -> RecoveryResult:
        """执行性能恢复"""
        start_time = time.time()
        
        try:
            if fault.fault_type == FaultType.PERFORMANCE_DEGRADATION:
                # 清理缓存
                if self.cache_clear_callback:
                    self.cache_clear_callback()
                
                result = RecoveryResult(
                    action=RecoveryAction.CLEAR_CACHE,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Cache cleared to improve performance",
                    metrics_before=fault.metrics
                )
                
            elif fault.fault_type == FaultType.RESOURCE_EXHAUSTION:
                # 启用请求节流
                if self.throttle_callback:
                    self.throttle_callback(True)
                
                result = RecoveryResult(
                    action=RecoveryAction.THROTTLE_REQUESTS,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Request throttling enabled to reduce resource usage",
                    metrics_before=fault.metrics
                )
            
            logger.info(f"Performance recovery completed: {result.message}")
            return result
            
        except Exception as e:
            return RecoveryResult(
                action=RecoveryAction.CLEAR_CACHE,
                status=RecoveryStatus.FAILED,
                timestamp=start_time,
                duration=time.time() - start_time,
                message=f"Performance recovery failed: {str(e)}",
                metrics_before=fault.metrics
            )

    def set_cache_clear_callback(self, callback: Callable):
        """设置缓存清理回调"""
        self.cache_clear_callback = callback

    def set_throttle_callback(self, callback: Callable):
        """设置节流回调"""
        self.throttle_callback = callback

class MemoryRecoveryStrategy(RecoveryStrategy):
    """内存恢复策略"""
    
    def __init__(self):
        self.gc_callback: Optional[Callable] = None

    def can_handle(self, fault: FaultEvent) -> bool:
        """判断是否能处理内存故障"""
        return fault.fault_type == FaultType.MEMORY_LEAK

    def recover(self, fault: FaultEvent) -> RecoveryResult:
        """执行内存恢复"""
        start_time = time.time()
        
        try:
            # 强制垃圾回收
            if self.gc_callback:
                self.gc_callback()
            else:
                import gc
                gc.collect()
            
            result = RecoveryResult(
                action=RecoveryAction.GARBAGE_COLLECTION,
                status=RecoveryStatus.SUCCESS,
                timestamp=start_time,
                duration=time.time() - start_time,
                message="Garbage collection triggered to free memory",
                metrics_before=fault.metrics
            )
            
            logger.info(f"Memory recovery completed: {result.message}")
            return result
            
        except Exception as e:
            return RecoveryResult(
                action=RecoveryAction.GARBAGE_COLLECTION,
                status=RecoveryStatus.FAILED,
                timestamp=start_time,
                duration=time.time() - start_time,
                message=f"Memory recovery failed: {str(e)}",
                metrics_before=fault.metrics
            )

    def set_gc_callback(self, callback: Callable):
        """设置垃圾回收回调"""
        self.gc_callback = callback

class ConnectionRecoveryStrategy(RecoveryStrategy):
    """连接恢复策略"""
    
    def __init__(self):
        self.reconnect_callback: Optional[Callable] = None
        self.circuit_breaker_callback: Optional[Callable] = None

    def can_handle(self, fault: FaultEvent) -> bool:
        """判断是否能处理连接故障"""
        return fault.fault_type in [
            FaultType.CONNECTION_FAILURE,
            FaultType.TIMEOUT
        ]

    def recover(self, fault: FaultEvent) -> RecoveryResult:
        """执行连接恢复"""
        start_time = time.time()
        
        try:
            if fault.fault_type == FaultType.CONNECTION_FAILURE:
                # 重新连接
                if self.reconnect_callback:
                    self.reconnect_callback()
                
                result = RecoveryResult(
                    action=RecoveryAction.RECONNECT,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Connection re-established",
                    metrics_before=fault.metrics
                )
                
            elif fault.fault_type == FaultType.TIMEOUT:
                # 启用断路器
                if self.circuit_breaker_callback:
                    self.circuit_breaker_callback(True)
                
                result = RecoveryResult(
                    action=RecoveryAction.CIRCUIT_BREAKER,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Circuit breaker activated to handle timeouts",
                    metrics_before=fault.metrics
                )
            
            logger.info(f"Connection recovery completed: {result.message}")
            return result
            
        except Exception as e:
            return RecoveryResult(
                action=RecoveryAction.RECONNECT,
                status=RecoveryStatus.FAILED,
                timestamp=start_time,
                duration=time.time() - start_time,
                message=f"Connection recovery failed: {str(e)}",
                metrics_before=fault.metrics
            )

    def set_reconnect_callback(self, callback: Callable):
        """设置重连回调"""
        self.reconnect_callback = callback

    def set_circuit_breaker_callback(self, callback: Callable):
        """设置断路器回调"""
        self.circuit_breaker_callback = callback

class CriticalFaultStrategy(RecoveryStrategy):
    """严重故障恢复策略"""
    
    def __init__(self):
        self.alert_callback: Optional[Callable] = None
        self.shutdown_callback: Optional[Callable] = None

    def can_handle(self, fault: FaultEvent) -> bool:
        """判断是否为严重故障"""
        return fault.severity == FaultSeverity.CRITICAL

    def recover(self, fault: FaultEvent) -> RecoveryResult:
        """处理严重故障"""
        start_time = time.time()
        
        try:
            # 发送管理员告警
            if self.alert_callback:
                self.alert_callback(fault)
            
            # 如果是数据损坏，执行优雅关闭
            if fault.fault_type == FaultType.DATA_CORRUPTION:
                if self.shutdown_callback:
                    self.shutdown_callback()
                
                return RecoveryResult(
                    action=RecoveryAction.GRACEFUL_SHUTDOWN,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Graceful shutdown initiated due to data corruption",
                    metrics_before=fault.metrics
                )
            else:
                return RecoveryResult(
                    action=RecoveryAction.ALERT_ADMIN,
                    status=RecoveryStatus.SUCCESS,
                    timestamp=start_time,
                    duration=time.time() - start_time,
                    message="Administrator alerted about critical fault",
                    metrics_before=fault.metrics
                )
                
        except Exception as e:
            return RecoveryResult(
                action=RecoveryAction.ALERT_ADMIN,
                status=RecoveryStatus.FAILED,
                timestamp=start_time,
                duration=time.time() - start_time,
                message=f"Critical fault handling failed: {str(e)}",
                metrics_before=fault.metrics
            )

    def set_alert_callback(self, callback: Callable):
        """设置告警回调"""
        self.alert_callback = callback

    def set_shutdown_callback(self, callback: Callable):
        """设置关闭回调"""
        self.shutdown_callback = callback

class AutoRecoverySystem:
    """自动恢复系统"""
    
    def __init__(self):
        self.strategies: List[RecoveryStrategy] = []
        self.recovery_history: List[RecoveryResult] = []
        self.recovery_enabled = True
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5分钟冷却期
        self.fault_recovery_count: Dict[str, int] = {}
        self.last_recovery_time: Dict[str, float] = {}
        self._lock = threading.Lock()
        
        # 默认恢复策略
        self.add_strategy(PerformanceRecoveryStrategy())
        self.add_strategy(MemoryRecoveryStrategy())
        self.add_strategy(ConnectionRecoveryStrategy())
        self.add_strategy(CriticalFaultStrategy())
        
        logger.info("Auto recovery system initialized")

    def add_strategy(self, strategy: RecoveryStrategy):
        """添加恢复策略"""
        self.strategies.append(strategy)
        logger.debug(f"Added recovery strategy: {strategy.__class__.__name__}")

    def remove_strategy(self, strategy_class: type):
        """移除恢复策略"""
        self.strategies = [s for s in self.strategies if not isinstance(s, strategy_class)]
        logger.debug(f"Removed recovery strategy: {strategy_class.__name__}")

    def handle_fault(self, fault: FaultEvent) -> Optional[RecoveryResult]:
        """处理故障"""
        if not self.recovery_enabled:
            logger.debug("Auto recovery is disabled")
            return None
        
        fault_key = f"{fault.fault_type.value}:{fault.component}"
        
        # 检查冷却期
        if self._is_in_cooldown(fault_key):
            logger.debug(f"Fault {fault_key} is in cooldown period")
            return None
        
        # 检查恢复次数限制
        if self._has_exceeded_max_attempts(fault_key):
            logger.warning(f"Max recovery attempts exceeded for fault {fault_key}")
            return None
        
        # 找到合适的恢复策略
        for strategy in self.strategies:
            if strategy.can_handle(fault):
                try:
                    logger.info(f"Attempting recovery for fault: {fault.fault_type.value}")
                    result = strategy.recover(fault)
                    
                    # 记录恢复结果
                    self._record_recovery(fault_key, result)
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Recovery strategy {strategy.__class__.__name__} failed: {e}")
                    continue
        
        logger.warning(f"No recovery strategy found for fault: {fault.fault_type.value}")
        return None

    def _is_in_cooldown(self, fault_key: str) -> bool:
        """检查是否在冷却期"""
        last_time = self.last_recovery_time.get(fault_key, 0)
        return time.time() - last_time < self.recovery_cooldown

    def _has_exceeded_max_attempts(self, fault_key: str) -> bool:
        """检查是否超过最大尝试次数"""
        count = self.fault_recovery_count.get(fault_key, 0)
        return count >= self.max_recovery_attempts

    def _record_recovery(self, fault_key: str, result: RecoveryResult):
        """记录恢复结果"""
        with self._lock:
            self.recovery_history.append(result)
            
            # 更新恢复计数和时间
            if result.status == RecoveryStatus.SUCCESS:
                self.fault_recovery_count[fault_key] = 0  # 成功时重置计数
            else:
                self.fault_recovery_count[fault_key] = self.fault_recovery_count.get(fault_key, 0) + 1
            
            self.last_recovery_time[fault_key] = result.timestamp
            
            # 保持最近500个恢复记录
            if len(self.recovery_history) > 500:
                self.recovery_history = self.recovery_history[-500:]

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """获取恢复统计"""
        with self._lock:
            if not self.recovery_history:
                return {
                    "total_recoveries": 0,
                    "success_rate": 0.0,
                    "action_distribution": {},
                    "recent_recoveries": []
                }
            
            total_recoveries = len(self.recovery_history)
            successful_recoveries = sum(1 for r in self.recovery_history if r.status == RecoveryStatus.SUCCESS)
            success_rate = successful_recoveries / total_recoveries * 100
            
            # 按动作类型统计
            action_distribution = {}
            for result in self.recovery_history:
                action = result.action.value
                action_distribution[action] = action_distribution.get(action, 0) + 1
            
            # 最近的恢复记录
            recent_recoveries = sorted(self.recovery_history, key=lambda x: x.timestamp, reverse=True)[:10]
            recent_recovery_data = [
                {
                    "action": result.action.value,
                    "status": result.status.value,
                    "timestamp": result.timestamp,
                    "duration": result.duration,
                    "message": result.message
                }
                for result in recent_recoveries
            ]
            
            return {
                "total_recoveries": total_recoveries,
                "success_rate": success_rate,
                "action_distribution": action_distribution,
                "recent_recoveries": recent_recovery_data,
                "enabled": self.recovery_enabled
            }

    def clear_recovery_history(self):
        """清空恢复历史"""
        with self._lock:
            self.recovery_history.clear()
            self.fault_recovery_count.clear()
            self.last_recovery_time.clear()
        logger.info("Recovery history cleared")

    def enable_recovery(self):
        """启用自动恢复"""
        self.recovery_enabled = True
        logger.info("Auto recovery enabled")

    def disable_recovery(self):
        """禁用自动恢复"""
        self.recovery_enabled = False
        logger.info("Auto recovery disabled")

    def is_recovery_enabled(self) -> bool:
        """检查自动恢复是否启用"""
        return self.recovery_enabled

    def get_strategy(self, strategy_class: type) -> Optional[RecoveryStrategy]:
        """获取指定类型的恢复策略"""
        for strategy in self.strategies:
            if isinstance(strategy, strategy_class):
                return strategy
        return None
