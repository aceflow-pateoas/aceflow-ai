"""
故障检测系统测试
Test Fault Detection System

测试故障检测、自动恢复和健康检查系统。
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch

from aceflow_mcp_server.recovery.fault_detector import (
    FaultDetectionSystem, FaultType, FaultSeverity,
    PerformanceFaultDetector, ExceptionFaultDetector, ConnectionFaultDetector
)
from aceflow_mcp_server.recovery.auto_recovery import (
    AutoRecoverySystem, RecoveryAction, RecoveryStatus,
    PerformanceRecoveryStrategy, MemoryRecoveryStrategy, ConnectionRecoveryStrategy
)
from aceflow_mcp_server.recovery.health_check import (
    HealthCheckSystem, HealthStatus, SystemHealthChecker,
    MemoryHealthChecker, ApplicationHealthChecker
)

class TestFaultDetectionSystem:
    """故障检测系统测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.fault_system = FaultDetectionSystem()

    def test_performance_fault_detection(self):
        """测试性能故障检测"""
        detector = PerformanceFaultDetector(
            response_time_threshold=2.0,
            cpu_threshold=70.0,
            memory_threshold=80.0
        )
        
        # 正常指标 - 不应触发故障
        normal_metrics = {
            'avg_response_time': 1.0,
            'cpu_usage': 50.0,
            'memory_usage': 60.0
        }
        fault = detector.detect(normal_metrics)
        assert fault is None
        
        # 响应时间过高 - 应触发故障
        slow_metrics = {
            'avg_response_time': 5.0,
            'cpu_usage': 50.0,
            'memory_usage': 60.0
        }
        fault = detector.detect(slow_metrics)
        assert fault is not None
        assert fault.fault_type == FaultType.PERFORMANCE_DEGRADATION
        assert fault.severity == FaultSeverity.HIGH
        
        # CPU使用率过高 - 应触发故障
        high_cpu_metrics = {
            'avg_response_time': 1.0,
            'cpu_usage': 85.0,
            'memory_usage': 60.0
        }
        fault = detector.detect(high_cpu_metrics)
        assert fault is not None
        assert fault.fault_type == FaultType.RESOURCE_EXHAUSTION
        assert "CPU usage" in fault.description

    def test_exception_fault_detection(self):
        """测试异常故障检测"""
        detector = ExceptionFaultDetector(
            exception_rate_threshold=5.0,
            time_window=60
        )
        
        # 正常异常数量 - 不应触发故障
        normal_metrics = {'exception_count': 2}
        fault = detector.detect(normal_metrics)
        assert fault is None
        
        # 快速触发多个异常检测以模拟高异常率
        for _ in range(8):
            detector.detect({'exception_count': 1})
        
        # 应该触发异常率故障
        fault = detector.detect({'exception_count': 1})
        assert fault is not None
        assert fault.fault_type == FaultType.EXCEPTION_THRESHOLD

    def test_connection_fault_detection(self):
        """测试连接故障检测"""
        detector = ConnectionFaultDetector(
            connection_failure_threshold=3,
            timeout_threshold=20.0
        )
        
        # 正常连接 - 不应触发故障
        normal_metrics = {
            'connection_failures': 0,
            'avg_timeout': 5.0
        }
        fault = detector.detect(normal_metrics)
        assert fault is None
        
        # 连接失败过多 - 应触发故障
        failure_metrics = {'connection_failures': 5}
        fault = detector.detect(failure_metrics)
        assert fault is not None
        assert fault.fault_type == FaultType.CONNECTION_FAILURE
        
        # 超时时间过长 - 应触发故障
        timeout_metrics = {
            'connection_failures': 0,
            'avg_timeout': 35.0
        }
        fault = detector.detect(timeout_metrics)
        assert fault is not None
        assert fault.fault_type == FaultType.TIMEOUT

    def test_fault_listener(self):
        """测试故障监听器"""
        detected_faults = []
        
        def fault_listener(fault):
            detected_faults.append(fault)
        
        self.fault_system.add_fault_listener(fault_listener)
        
        # 触发故障
        metrics = {
            'avg_response_time': 10.0,
            'cpu_usage': 50.0,
            'memory_usage': 60.0
        }
        faults = self.fault_system.detect_faults(metrics)
        
        assert len(faults) > 0
        assert len(detected_faults) > 0
        assert detected_faults[0].fault_type == FaultType.PERFORMANCE_DEGRADATION

    def test_fault_statistics(self):
        """测试故障统计"""
        # 触发一些故障
        metrics = {
            'avg_response_time': 10.0,
            'cpu_usage': 90.0,
            'memory_usage': 95.0
        }
        self.fault_system.detect_faults(metrics)
        
        stats = self.fault_system.get_fault_statistics()
        assert stats["total_faults"] > 0
        assert "fault_types" in stats
        assert "severity_distribution" in stats
        assert "recent_faults" in stats

class TestAutoRecoverySystem:
    """自动恢复系统测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.recovery_system = AutoRecoverySystem()

    def test_performance_recovery(self):
        """测试性能恢复策略"""
        strategy = self.recovery_system.get_strategy(PerformanceRecoveryStrategy)
        assert strategy is not None
        
        # 模拟缓存清理回调
        cache_cleared = False
        def clear_cache():
            nonlocal cache_cleared
            cache_cleared = True
        
        strategy.set_cache_clear_callback(clear_cache)
        
        # 创建性能故障事件
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent
        fault = FaultEvent(
            fault_type=FaultType.PERFORMANCE_DEGRADATION,
            severity=FaultSeverity.HIGH,
            timestamp=time.time(),
            component="performance",
            description="High response time",
            metrics={'avg_response_time': 10.0}
        )
        
        # 执行恢复
        result = self.recovery_system.handle_fault(fault)
        assert result is not None
        assert result.status == RecoveryStatus.SUCCESS
        assert result.action == RecoveryAction.CLEAR_CACHE
        assert cache_cleared

    def test_memory_recovery(self):
        """测试内存恢复策略"""
        strategy = self.recovery_system.get_strategy(MemoryRecoveryStrategy)
        assert strategy is not None
        
        # 模拟垃圾回收回调
        gc_called = False
        def trigger_gc():
            nonlocal gc_called
            gc_called = True
        
        strategy.set_gc_callback(trigger_gc)
        
        # 创建内存故障事件
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent
        fault = FaultEvent(
            fault_type=FaultType.MEMORY_LEAK,
            severity=FaultSeverity.CRITICAL,
            timestamp=time.time(),
            component="memory",
            description="Memory leak detected",
            metrics={'memory_usage': 98.0}
        )
        
        # 执行恢复
        result = self.recovery_system.handle_fault(fault)
        assert result is not None
        assert result.status == RecoveryStatus.SUCCESS
        assert result.action == RecoveryAction.GARBAGE_COLLECTION
        assert gc_called

    def test_connection_recovery(self):
        """测试连接恢复策略"""
        strategy = self.recovery_system.get_strategy(ConnectionRecoveryStrategy)
        assert strategy is not None
        
        # 模拟重连回调
        reconnected = False
        def reconnect():
            nonlocal reconnected
            reconnected = True
        
        strategy.set_reconnect_callback(reconnect)
        
        # 创建连接故障事件
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent
        fault = FaultEvent(
            fault_type=FaultType.CONNECTION_FAILURE,
            severity=FaultSeverity.HIGH,
            timestamp=time.time(),
            component="connections",
            description="Connection failures exceeded threshold",
            metrics={'connection_failures': 5}
        )
        
        # 执行恢复
        result = self.recovery_system.handle_fault(fault)
        assert result is not None
        assert result.status == RecoveryStatus.SUCCESS
        assert result.action == RecoveryAction.RECONNECT
        assert reconnected

    def test_recovery_cooldown(self):
        """测试恢复冷却期"""
        # 设置短的冷却期用于测试
        self.recovery_system.recovery_cooldown = 2
        
        # 创建故障事件
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent
        fault = FaultEvent(
            fault_type=FaultType.PERFORMANCE_DEGRADATION,
            severity=FaultSeverity.HIGH,
            timestamp=time.time(),
            component="performance",
            description="High response time",
            metrics={'avg_response_time': 10.0}
        )
        
        # 第一次恢复应该成功
        result1 = self.recovery_system.handle_fault(fault)
        assert result1 is not None
        
        # 立即再次尝试恢复应该被阻止（冷却期内）
        result2 = self.recovery_system.handle_fault(fault)
        assert result2 is None
        
        # 等待冷却期结束后应该可以再次恢复
        time.sleep(2.1)
        result3 = self.recovery_system.handle_fault(fault)
        assert result3 is not None

    def test_recovery_statistics(self):
        """测试恢复统计"""
        # 触发一些恢复
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent
        fault = FaultEvent(
            fault_type=FaultType.PERFORMANCE_DEGRADATION,
            severity=FaultSeverity.HIGH,
            timestamp=time.time(),
            component="performance",
            description="High response time",
            metrics={'avg_response_time': 10.0}
        )
        
        self.recovery_system.handle_fault(fault)
        
        stats = self.recovery_system.get_recovery_statistics()
        assert stats["total_recoveries"] > 0
        assert "success_rate" in stats
        assert "action_distribution" in stats
        assert "recent_recoveries" in stats

class TestHealthCheckSystem:
    """健康检查系统测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.health_system = HealthCheckSystem(check_interval=1)

    def teardown_method(self):
        """清理测试环境"""
        self.health_system.stop_monitoring()

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_health_check(self, mock_disk, mock_memory, mock_cpu):
        """测试系统健康检查"""
        # 模拟正常系统指标
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, available=1000000, total=2000000, used=1000000)
        mock_disk.return_value = Mock(percent=70.0, free=500000, total=1000000)
        
        checker = SystemHealthChecker()
        result = checker.check()
        
        assert result.status == HealthStatus.HEALTHY
        assert result.component == "system"
        assert "System healthy" in result.message
        assert result.metrics["cpu_percent"] == 50.0
        assert result.metrics["memory_percent"] == 60.0

    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    def test_memory_health_check(self, mock_swap, mock_memory):
        """测试内存健康检查"""
        # 模拟高内存使用率
        mock_memory.return_value = Mock(
            percent=90.0, 
            total=2000000, 
            available=200000, 
            used=1800000
        )
        mock_swap.return_value = Mock(percent=20.0, total=1000000, used=200000)
        
        checker = MemoryHealthChecker()
        result = checker.check()
        
        assert result.status == HealthStatus.WARNING
        assert result.component == "memory"
        assert "High memory usage" in result.message

    def test_application_health_check(self):
        """测试应用程序健康检查"""
        checker = ApplicationHealthChecker()
        
        # 添加健康检查函数
        def always_healthy():
            return True
        
        def always_unhealthy():
            return False
        
        checker.add_health_check(always_healthy)
        checker.add_health_check(always_unhealthy)
        
        # 添加指标收集器
        checker.add_metric_collector("test_metric", lambda: 42)
        
        result = checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.component == "application"
        assert "Failed checks" in result.message
        assert result.metrics["test_metric"] == 42

    def test_health_monitoring(self):
        """测试健康监控"""
        # 启动监控
        self.health_system.start_monitoring()
        assert self.health_system.running
        
        # 等待一个检查周期
        time.sleep(1.5)
        
        # 检查是否生成了健康报告
        report = self.health_system.get_health_report()
        assert "overall_status" in report
        assert "components" in report
        assert len(report["components"]) > 0
        
        # 停止监控
        self.health_system.stop_monitoring()
        assert not self.health_system.running

    def test_health_history(self):
        """测试健康历史记录"""
        # 运行一次健康检查
        self.health_system.run_checks()
        
        # 获取历史记录
        history = self.health_system.get_health_history(hours=1)
        assert len(history) > 0
        
        # 清空历史
        self.health_system.clear_history()
        history = self.health_system.get_health_history(hours=1)
        assert len(history) == 0

    def test_overall_health_status(self):
        """测试整体健康状态计算"""
        # 运行健康检查
        self.health_system.run_checks()
        
        # 获取整体状态
        overall_status = self.health_system.get_overall_health()
        assert isinstance(overall_status, HealthStatus)

if __name__ == "__main__":
    pytest.main([__file__])
