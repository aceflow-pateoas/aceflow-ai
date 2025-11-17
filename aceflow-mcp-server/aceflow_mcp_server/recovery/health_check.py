"""
健康检查器
Health Checker

定期检查系统健康状态，提供系统状态监控和报告。
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import threading
import psutil
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ComponentType(Enum):
    """组件类型"""
    SYSTEM = "system"
    DATABASE = "database"
    CACHE = "cache"
    NETWORK = "network"
    STORAGE = "storage"
    MEMORY = "memory"
    CPU = "cpu"
    APPLICATION = "application"

@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    component_type: ComponentType
    status: HealthStatus
    timestamp: float
    response_time: float
    message: str
    metrics: Dict[str, Any]
    details: Optional[Dict[str, Any]] = None

class HealthChecker(ABC):
    """健康检查器基类"""
    
    @abstractmethod
    def check(self) -> HealthCheckResult:
        """执行健康检查"""
        pass

class SystemHealthChecker(HealthChecker):
    """系统健康检查器"""
    
    def __init__(self):
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0

    def check(self) -> HealthCheckResult:
        """检查系统健康状态"""
        start_time = time.time()
        
        try:
            # 获取系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 计算健康状态
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > self.cpu_threshold:
                if cpu_percent > 95:
                    status = HealthStatus.CRITICAL
                else:
                    status = HealthStatus.WARNING
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > self.memory_threshold:
                if memory.percent > 95:
                    status = HealthStatus.CRITICAL
                else:
                    status = max(status, HealthStatus.WARNING)
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > self.disk_threshold:
                if disk.percent > 98:
                    status = HealthStatus.CRITICAL
                else:
                    status = max(status, HealthStatus.WARNING)
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            message = "System healthy" if not issues else "; ".join(issues)
            
            return HealthCheckResult(
                component="system",
                component_type=ComponentType.SYSTEM,
                status=status,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=message,
                metrics={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="system",
                component_type=ComponentType.SYSTEM,
                status=HealthStatus.UNKNOWN,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=f"System health check failed: {str(e)}",
                metrics={}
            )

class MemoryHealthChecker(HealthChecker):
    """内存健康检查器"""
    
    def __init__(self):
        self.warning_threshold = 80.0
        self.critical_threshold = 95.0

    def check(self) -> HealthCheckResult:
        """检查内存健康状态"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 计算健康状态
            status = HealthStatus.HEALTHY
            message = "Memory usage normal"
            
            if memory.percent > self.critical_threshold:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory.percent:.1f}%"
            elif memory.percent > self.warning_threshold:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory.percent:.1f}%"
            
            # 检查交换空间
            if swap.percent > 50:
                status = max(status, HealthStatus.WARNING)
                message += f"; High swap usage: {swap.percent:.1f}%"
            
            return HealthCheckResult(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=status,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=message,
                metrics={
                    "memory_percent": memory.percent,
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_used": memory.used,
                    "swap_percent": swap.percent,
                    "swap_total": swap.total,
                    "swap_used": swap.used
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.UNKNOWN,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=f"Memory health check failed: {str(e)}",
                metrics={}
            )

class ApplicationHealthChecker(HealthChecker):
    """应用程序健康检查器"""
    
    def __init__(self):
        self.health_checks: List[Callable[[], bool]] = []
        self.custom_metrics: Dict[str, Callable[[], Any]] = {}

    def add_health_check(self, check_func: Callable[[], bool]):
        """添加健康检查函数"""
        self.health_checks.append(check_func)

    def add_metric_collector(self, name: str, collector_func: Callable[[], Any]):
        """添加指标收集器"""
        self.custom_metrics[name] = collector_func

    def check(self) -> HealthCheckResult:
        """检查应用程序健康状态"""
        start_time = time.time()
        
        try:
            status = HealthStatus.HEALTHY
            failed_checks = []
            metrics = {}
            
            # 执行健康检查
            for i, check_func in enumerate(self.health_checks):
                try:
                    if not check_func():
                        failed_checks.append(f"check_{i}")
                        status = HealthStatus.UNHEALTHY
                except Exception as e:
                    failed_checks.append(f"check_{i}_error: {str(e)}")
                    status = HealthStatus.UNHEALTHY
            
            # 收集自定义指标
            for name, collector_func in self.custom_metrics.items():
                try:
                    metrics[name] = collector_func()
                except Exception as e:
                    logger.error(f"Failed to collect metric {name}: {e}")
                    metrics[name] = None
            
            message = "Application healthy" if not failed_checks else f"Failed checks: {', '.join(failed_checks)}"
            
            return HealthCheckResult(
                component="application",
                component_type=ComponentType.APPLICATION,
                status=status,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="application",
                component_type=ComponentType.APPLICATION,
                status=HealthStatus.UNKNOWN,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=f"Application health check failed: {str(e)}",
                metrics={}
            )

class NetworkHealthChecker(HealthChecker):
    """网络健康检查器"""
    
    def __init__(self):
        self.endpoints: List[str] = []
        self.timeout = 5.0

    def add_endpoint(self, endpoint: str):
        """添加检查端点"""
        self.endpoints.append(endpoint)

    def check(self) -> HealthCheckResult:
        """检查网络健康状态"""
        start_time = time.time()
        
        try:
            import socket
            
            status = HealthStatus.HEALTHY
            failed_endpoints = []
            response_times = []
            
            for endpoint in self.endpoints:
                try:
                    if ":" in endpoint:
                        host, port = endpoint.split(":", 1)
                        port = int(port)
                    else:
                        host = endpoint
                        port = 80
                    
                    sock_start = time.time()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.timeout)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    sock_time = time.time() - sock_start
                    
                    if result == 0:
                        response_times.append(sock_time)
                    else:
                        failed_endpoints.append(endpoint)
                        status = HealthStatus.UNHEALTHY
                        
                except Exception as e:
                    failed_endpoints.append(f"{endpoint}: {str(e)}")
                    status = HealthStatus.UNHEALTHY
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            message = "Network connectivity normal" if not failed_endpoints else f"Failed endpoints: {', '.join(failed_endpoints)}"
            
            return HealthCheckResult(
                component="network",
                component_type=ComponentType.NETWORK,
                status=status,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=message,
                metrics={
                    "endpoints_checked": len(self.endpoints),
                    "endpoints_failed": len(failed_endpoints),
                    "avg_response_time": avg_response_time,
                    "response_times": response_times
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="network",
                component_type=ComponentType.NETWORK,
                status=HealthStatus.UNKNOWN,
                timestamp=start_time,
                response_time=time.time() - start_time,
                message=f"Network health check failed: {str(e)}",
                metrics={}
            )

class HealthCheckSystem:
    """健康检查系统"""
    
    def __init__(self, check_interval: int = 60):
        self.checkers: List[HealthChecker] = []
        self.check_interval = check_interval
        self.last_results: Dict[str, HealthCheckResult] = {}
        self.health_history: List[HealthCheckResult] = []
        self.enabled = True
        self.running = False
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        
        # 默认健康检查器
        self.add_checker(SystemHealthChecker())
        self.add_checker(MemoryHealthChecker())
        self.add_checker(ApplicationHealthChecker())
        self.add_checker(NetworkHealthChecker())
        
        logger.info("Health check system initialized")

    def add_checker(self, checker: HealthChecker):
        """添加健康检查器"""
        self.checkers.append(checker)
        logger.debug(f"Added health checker: {checker.__class__.__name__}")

    def remove_checker(self, checker_class: type):
        """移除健康检查器"""
        self.checkers = [c for c in self.checkers if not isinstance(c, checker_class)]
        logger.debug(f"Removed health checker: {checker_class.__name__}")

    def run_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        if not self.enabled:
            return {}
        
        results = {}
        
        for checker in self.checkers:
            try:
                result = checker.check()
                results[result.component] = result
                
                with self._lock:
                    self.last_results[result.component] = result
                    self.health_history.append(result)
                    
                    # 保持最近1000个检查结果
                    if len(self.health_history) > 1000:
                        self.health_history = self.health_history[-1000:]
                
                logger.debug(f"Health check for {result.component}: {result.status.value}")
                
            except Exception as e:
                logger.error(f"Health checker {checker.__class__.__name__} failed: {e}")
        
        return results

    def get_overall_health(self) -> HealthStatus:
        """获取整体健康状态"""
        with self._lock:
            if not self.last_results:
                return HealthStatus.UNKNOWN
            
            statuses = [result.status for result in self.last_results.values()]
            
            if HealthStatus.CRITICAL in statuses:
                return HealthStatus.CRITICAL
            elif HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            elif HealthStatus.WARNING in statuses:
                return HealthStatus.WARNING
            elif HealthStatus.HEALTHY in statuses:
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.UNKNOWN

    def get_health_report(self) -> Dict[str, Any]:
        """获取健康报告"""
        with self._lock:
            overall_status = self.get_overall_health()
            
            components = {}
            for component, result in self.last_results.items():
                components[component] = {
                    "status": result.status.value,
                    "message": result.message,
                    "timestamp": result.timestamp,
                    "response_time": result.response_time,
                    "metrics": result.metrics
                }
            
            # 统计信息
            status_counts = {}
            for status in HealthStatus:
                status_counts[status.value] = sum(
                    1 for result in self.last_results.values() 
                    if result.status == status
                )
            
            return {
                "overall_status": overall_status.value,
                "components": components,
                "status_distribution": status_counts,
                "last_check_time": max(
                    (result.timestamp for result in self.last_results.values()),
                    default=0
                ),
                "enabled": self.enabled,
                "running": self.running
            }

    def start_monitoring(self):
        """开始监控"""
        if self.running:
            logger.warning("Health monitoring is already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._thread.start()
        logger.info(f"Health monitoring started with {self.check_interval}s interval")

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Health monitoring stopped")

    def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                self.run_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(self.check_interval)

    def get_health_history(self, hours: int = 24) -> List[HealthCheckResult]:
        """获取健康历史"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            return [result for result in self.health_history if result.timestamp > cutoff_time]

    def clear_history(self):
        """清空历史记录"""
        with self._lock:
            self.health_history.clear()
            self.last_results.clear()
        logger.info("Health check history cleared")

    def enable(self):
        """启用健康检查"""
        self.enabled = True
        logger.info("Health checking enabled")

    def disable(self):
        """禁用健康检查"""
        self.enabled = False
        logger.info("Health checking disabled")

    def is_enabled(self) -> bool:
        """检查健康检查是否启用"""
        return self.enabled

    def get_checker(self, checker_class: type) -> Optional[HealthChecker]:
        """获取指定类型的健康检查器"""
        for checker in self.checkers:
            if isinstance(checker, checker_class):
                return checker
        return None
