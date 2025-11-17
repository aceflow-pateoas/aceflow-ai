"""
故障检测器
Fault Detector

检测系统异常和故障，为自动恢复提供支持。
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import threading
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class FaultType(Enum):
    """故障类型"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_LEAK = "memory_leak"
    CONNECTION_FAILURE = "connection_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    EXCEPTION_THRESHOLD = "exception_threshold"
    TIMEOUT = "timeout"
    DEADLOCK = "deadlock"
    DATA_CORRUPTION = "data_corruption"

class FaultSeverity(Enum):
    """故障严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FaultEvent:
    """故障事件"""
    fault_type: FaultType
    severity: FaultSeverity
    timestamp: float
    component: str
    description: str
    metrics: Dict[str, Any]
    threshold_violated: Optional[str] = None

class FaultDetector(ABC):
    """故障检测器基类"""
    
    @abstractmethod
    def detect(self, metrics: Dict[str, Any]) -> Optional[FaultEvent]:
        """检测故障"""
        pass

class PerformanceFaultDetector(FaultDetector):
    """性能故障检测器"""
    
    def __init__(self, response_time_threshold: float = 5.0, 
                 cpu_threshold: float = 80.0, memory_threshold: float = 85.0):
        self.response_time_threshold = response_time_threshold
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def detect(self, metrics: Dict[str, Any]) -> Optional[FaultEvent]:
        """检测性能故障"""
        timestamp = time.time()
        
        # 检查响应时间
        avg_response_time = metrics.get('avg_response_time', 0)
        if avg_response_time > self.response_time_threshold:
            return FaultEvent(
                fault_type=FaultType.PERFORMANCE_DEGRADATION,
                severity=FaultSeverity.HIGH if avg_response_time > self.response_time_threshold * 2 else FaultSeverity.MEDIUM,
                timestamp=timestamp,
                component="performance",
                description=f"Average response time {avg_response_time:.2f}s exceeds threshold {self.response_time_threshold}s",
                metrics=metrics,
                threshold_violated="response_time"
            )
        
        # 检查CPU使用率
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > self.cpu_threshold:
            return FaultEvent(
                fault_type=FaultType.RESOURCE_EXHAUSTION,
                severity=FaultSeverity.HIGH if cpu_usage > 95 else FaultSeverity.MEDIUM,
                timestamp=timestamp,
                component="cpu",
                description=f"CPU usage {cpu_usage:.1f}% exceeds threshold {self.cpu_threshold}%",
                metrics=metrics,
                threshold_violated="cpu_usage"
            )
        
        # 检查内存使用率
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > self.memory_threshold:
            return FaultEvent(
                fault_type=FaultType.MEMORY_LEAK if memory_usage > 95 else FaultType.RESOURCE_EXHAUSTION,
                severity=FaultSeverity.CRITICAL if memory_usage > 95 else FaultSeverity.HIGH,
                timestamp=timestamp,
                component="memory",
                description=f"Memory usage {memory_usage:.1f}% exceeds threshold {self.memory_threshold}%",
                metrics=metrics,
                threshold_violated="memory_usage"
            )
        
        return None

class ExceptionFaultDetector(FaultDetector):
    """异常故障检测器"""
    
    def __init__(self, exception_rate_threshold: float = 10.0, time_window: int = 60):
        self.exception_rate_threshold = exception_rate_threshold
        self.time_window = time_window
        self.exception_history: List[float] = []

    def detect(self, metrics: Dict[str, Any]) -> Optional[FaultEvent]:
        """检测异常故障"""
        timestamp = time.time()
        exception_count = metrics.get('exception_count', 0)
        
        # 添加当前异常数量到历史记录
        self.exception_history.append(timestamp)
        
        # 清理过期记录
        cutoff_time = timestamp - self.time_window
        self.exception_history = [t for t in self.exception_history if t > cutoff_time]
        
        # 计算异常率
        exception_rate = len(self.exception_history) / self.time_window * 60  # 每分钟异常数
        
        if exception_rate > self.exception_rate_threshold:
            return FaultEvent(
                fault_type=FaultType.EXCEPTION_THRESHOLD,
                severity=FaultSeverity.HIGH if exception_rate > self.exception_rate_threshold * 2 else FaultSeverity.MEDIUM,
                timestamp=timestamp,
                component="exceptions",
                description=f"Exception rate {exception_rate:.1f}/min exceeds threshold {self.exception_rate_threshold}/min",
                metrics={"exception_rate": exception_rate, "exception_count": exception_count},
                threshold_violated="exception_rate"
            )
        
        return None

class ConnectionFaultDetector(FaultDetector):
    """连接故障检测器"""
    
    def __init__(self, connection_failure_threshold: int = 5, timeout_threshold: float = 30.0):
        self.connection_failure_threshold = connection_failure_threshold
        self.timeout_threshold = timeout_threshold
        self.failure_count = 0

    def detect(self, metrics: Dict[str, Any]) -> Optional[FaultEvent]:
        """检测连接故障"""
        timestamp = time.time()
        
        # 检查连接失败
        connection_failures = metrics.get('connection_failures', 0)
        if connection_failures > 0:
            self.failure_count += connection_failures
            
        if self.failure_count >= self.connection_failure_threshold:
            fault = FaultEvent(
                fault_type=FaultType.CONNECTION_FAILURE,
                severity=FaultSeverity.HIGH,
                timestamp=timestamp,
                component="connections",
                description=f"Connection failures {self.failure_count} exceed threshold {self.connection_failure_threshold}",
                metrics=metrics,
                threshold_violated="connection_failures"
            )
            self.failure_count = 0  # 重置计数器
            return fault
        
        # 检查超时
        avg_timeout = metrics.get('avg_timeout', 0)
        if avg_timeout > self.timeout_threshold:
            return FaultEvent(
                fault_type=FaultType.TIMEOUT,
                severity=FaultSeverity.MEDIUM,
                timestamp=timestamp,
                component="timeouts",
                description=f"Average timeout {avg_timeout:.2f}s exceeds threshold {self.timeout_threshold}s",
                metrics=metrics,
                threshold_violated="timeout"
            )
        
        return None

class FaultDetectionSystem:
    """故障检测系统"""
    
    def __init__(self):
        self.detectors: List[FaultDetector] = []
        self.fault_listeners: List[Callable[[FaultEvent], None]] = []
        self.detected_faults: List[FaultEvent] = []
        self.detection_enabled = True
        self._lock = threading.Lock()
        
        # 默认检测器
        self.add_detector(PerformanceFaultDetector())
        self.add_detector(ExceptionFaultDetector())
        self.add_detector(ConnectionFaultDetector())
        
        logger.info("Fault detection system initialized")

    def add_detector(self, detector: FaultDetector):
        """添加故障检测器"""
        self.detectors.append(detector)
        logger.debug(f"Added fault detector: {detector.__class__.__name__}")

    def remove_detector(self, detector_class: type):
        """移除故障检测器"""
        self.detectors = [d for d in self.detectors if not isinstance(d, detector_class)]
        logger.debug(f"Removed fault detector: {detector_class.__name__}")

    def add_fault_listener(self, listener: Callable[[FaultEvent], None]):
        """添加故障监听器"""
        self.fault_listeners.append(listener)

    def detect_faults(self, metrics: Dict[str, Any]) -> List[FaultEvent]:
        """检测故障"""
        if not self.detection_enabled:
            return []
        
        detected_faults = []
        
        for detector in self.detectors:
            try:
                fault = detector.detect(metrics)
                if fault:
                    detected_faults.append(fault)
                    self._record_fault(fault)
                    self._notify_listeners(fault)
            except Exception as e:
                logger.error(f"Error in fault detector {detector.__class__.__name__}: {e}")
        
        return detected_faults

    def _record_fault(self, fault: FaultEvent):
        """记录故障"""
        with self._lock:
            self.detected_faults.append(fault)
            
            # 保持最近1000个故障记录
            if len(self.detected_faults) > 1000:
                self.detected_faults = self.detected_faults[-1000:]
        
        logger.warning(f"Fault detected: {fault.fault_type.value} in {fault.component} - {fault.description}")

    def _notify_listeners(self, fault: FaultEvent):
        """通知监听器"""
        for listener in self.fault_listeners:
            try:
                listener(fault)
            except Exception as e:
                logger.error(f"Error notifying fault listener: {e}")

    def get_fault_history(self, hours: int = 24) -> List[FaultEvent]:
        """获取故障历史"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            return [fault for fault in self.detected_faults if fault.timestamp > cutoff_time]

    def get_fault_statistics(self) -> Dict[str, Any]:
        """获取故障统计"""
        with self._lock:
            if not self.detected_faults:
                return {
                    "total_faults": 0,
                    "fault_types": {},
                    "severity_distribution": {},
                    "recent_faults": []
                }
            
            # 按类型统计
            fault_types = {}
            for fault in self.detected_faults:
                fault_type = fault.fault_type.value
                fault_types[fault_type] = fault_types.get(fault_type, 0) + 1
            
            # 按严重程度统计
            severity_distribution = {}
            for fault in self.detected_faults:
                severity = fault.severity.value
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # 最近的故障
            recent_faults = sorted(self.detected_faults, key=lambda x: x.timestamp, reverse=True)[:10]
            recent_fault_data = [
                {
                    "type": fault.fault_type.value,
                    "severity": fault.severity.value,
                    "component": fault.component,
                    "description": fault.description,
                    "timestamp": fault.timestamp
                }
                for fault in recent_faults
            ]
            
            return {
                "total_faults": len(self.detected_faults),
                "fault_types": fault_types,
                "severity_distribution": severity_distribution,
                "recent_faults": recent_fault_data
            }

    def clear_fault_history(self):
        """清空故障历史"""
        with self._lock:
            self.detected_faults.clear()
        logger.info("Fault history cleared")

    def enable_detection(self):
        """启用故障检测"""
        self.detection_enabled = True
        logger.info("Fault detection enabled")

    def disable_detection(self):
        """禁用故障检测"""
        self.detection_enabled = False
        logger.info("Fault detection disabled")

    def is_detection_enabled(self) -> bool:
        """检查故障检测是否启用"""
        return self.detection_enabled
