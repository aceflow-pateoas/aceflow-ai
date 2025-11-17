"""
故障恢复模块
Recovery Module

提供全面的故障检测、自动恢复和健康监控功能。
"""

from .fault_detector import (
    FaultDetector, 
    FaultType, 
    FaultSeverity, 
    FaultEvent,
    FaultDetectionSystem,
    PerformanceFaultDetector,
    ExceptionFaultDetector,
    ConnectionFaultDetector
)

from .auto_recovery import (
    RecoveryStrategy,
    RecoveryAction,
    RecoveryStatus,
    RecoveryResult,
    AutoRecoverySystem,
    PerformanceRecoveryStrategy,
    MemoryRecoveryStrategy,
    ConnectionRecoveryStrategy,
    CriticalFaultStrategy
)

from .health_check import (
    HealthChecker,
    HealthStatus,
    ComponentType,
    HealthCheckResult,
    HealthCheckSystem,
    SystemHealthChecker,
    MemoryHealthChecker,
    ApplicationHealthChecker,
    NetworkHealthChecker
)

__all__ = [
    'FaultDetector',
    'FaultType',
    'FaultSeverity', 
    'FaultEvent',
    'FaultDetectionSystem',
    'PerformanceFaultDetector',
    'ExceptionFaultDetector',
    'ConnectionFaultDetector',
    'RecoveryStrategy',
    'RecoveryAction',
    'RecoveryStatus',
    'RecoveryResult',
    'AutoRecoverySystem',
    'PerformanceRecoveryStrategy',
    'MemoryRecoveryStrategy',
    'ConnectionRecoveryStrategy',
    'CriticalFaultStrategy',
    'HealthChecker',
    'HealthStatus',
    'ComponentType',
    'HealthCheckResult',
    'HealthCheckSystem',
    'SystemHealthChecker',
    'MemoryHealthChecker',
    'ApplicationHealthChecker',
    'NetworkHealthChecker'
]
