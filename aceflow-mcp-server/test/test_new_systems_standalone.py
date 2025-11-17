"""
新系统独立测试
Test New Systems Standalone

独立测试新实现的系统，不依赖现有的MCP框架。
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import tempfile
import time
from unittest.mock import Mock, patch

def test_cache_manager_standalone():
    """独立测试缓存管理器"""
    try:
        from aceflow_mcp_server.performance.cache import CacheManager
        
        cache = CacheManager()
        
        # 基本缓存操作
        cache.set("test_key", "test_value", ttl=60)
        assert cache.get("test_key") == "test_value"
        assert cache.size() == 1
        
        # TTL测试（使用短时间）
        cache.set("short_key", "short_value", ttl=0.1)
        time.sleep(0.2)
        assert cache.get("short_key") is None
        
        # 统计测试
        stats = cache.get_statistics()
        assert stats["total_sets"] >= 2
        assert stats["total_gets"] >= 2
        
        print("✓ Cache Manager test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Cache Manager import failed: {e}")
        return False

def test_performance_monitor_standalone():
    """独立测试性能监控器"""
    try:
        from aceflow_mcp_server.performance.monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # 装饰器测试
        @monitor.monitor_execution
        def test_function():
            time.sleep(0.01)
            return "test_result"
        
        result = test_function()
        assert result == "test_result"
        
        # 统计测试
        stats = monitor.get_statistics()
        assert "test_function" in stats["function_stats"]
        
        print("✓ Performance Monitor test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Performance Monitor import failed: {e}")
        return False

def test_error_handler_standalone():
    """独立测试错误处理器"""
    try:
        from aceflow_mcp_server.error_handling.error_handler import ErrorHandler
        
        handler = ErrorHandler()
        
        # 装饰器测试
        @handler.handle_errors
        def failing_function():
            raise ValueError("Test error")
        
        # 应该不抛出异常
        result = failing_function()
        assert result is None  # 错误处理器应返回None
        
        # 检查错误记录
        stats = handler.get_statistics()
        assert stats["total_errors"] >= 1
        
        print("✓ Error Handler test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Error Handler import failed: {e}")
        return False

def test_input_validator_standalone():
    """独立测试输入验证器"""
    try:
        from aceflow_mcp_server.security.input_validator import InputValidator
        
        validator = InputValidator()
        
        # SQL注入测试
        safe_sql = "SELECT * FROM users WHERE id = 123"
        unsafe_sql = "SELECT * FROM users WHERE id = 1; DROP TABLE users; --"
        
        safe_result = validator.validate_sql_injection(safe_sql)
        unsafe_result = validator.validate_sql_injection(unsafe_sql)
        
        assert safe_result.is_valid
        assert not unsafe_result.is_valid
        
        # XSS测试
        safe_input = "Normal text input"
        xss_input = "<script>alert('XSS')</script>"
        
        safe_xss = validator.validate_xss(safe_input)
        unsafe_xss = validator.validate_xss(xss_input)
        
        assert safe_xss.is_valid
        assert not unsafe_xss.is_valid
        
        print("✓ Input Validator test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Input Validator import failed: {e}")
        return False

def test_audit_logger_standalone():
    """独立测试审计日志器"""
    try:
        from aceflow_mcp_server.security.audit_logger import AuditLogger, AuditLevel, AuditCategory
        
        temp_dir = tempfile.mkdtemp()
        log_file = os.path.join(temp_dir, "test_audit.log")
        
        logger = AuditLogger(log_file=log_file)
        
        # 记录事件
        logger.log_authentication("test_user", "login", "success")
        logger.log_data_access("test_user", "database", "read", "success")
        
        # 检查事件
        events = logger.query_events(user_id="test_user")
        assert len(events) == 2
        
        # 检查统计
        stats = logger.get_statistics()
        assert stats["total_events"] == 2
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("✓ Audit Logger test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Audit Logger import failed: {e}")
        return False

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
@patch('psutil.disk_usage')
def test_health_checker_standalone(mock_disk, mock_memory, mock_cpu):
    """独立测试健康检查器"""
    try:
        from aceflow_mcp_server.recovery.health_check import HealthCheckSystem, HealthStatus
        
        # 模拟系统指标
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, available=1000000, total=2000000, used=1000000)
        mock_disk.return_value = Mock(percent=70.0, free=500000, total=1000000)
        
        health_system = HealthCheckSystem()
        
        # 运行健康检查
        results = health_system.run_checks()
        assert len(results) > 0
        
        # 获取整体状态
        overall_status = health_system.get_overall_health()
        assert isinstance(overall_status, HealthStatus)
        
        # 获取报告
        report = health_system.get_health_report()
        assert "overall_status" in report
        assert "components" in report
        
        print("✓ Health Checker test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Health Checker import failed: {e}")
        return False

def test_fault_detector_standalone():
    """独立测试故障检测器"""
    try:
        from aceflow_mcp_server.recovery.fault_detector import FaultDetectionSystem, FaultType
        
        fault_system = FaultDetectionSystem()
        
        # 模拟故障指标
        metrics = {
            'avg_response_time': 10.0,  # 高响应时间
            'cpu_usage': 90.0,          # 高CPU使用率
            'memory_usage': 85.0        # 高内存使用率
        }
        
        # 检测故障
        faults = fault_system.detect_faults(metrics)
        assert len(faults) > 0
        
        # 检查故障类型
        fault_types = [fault.fault_type for fault in faults]
        assert FaultType.PERFORMANCE_DEGRADATION in fault_types or FaultType.RESOURCE_EXHAUSTION in fault_types
        
        # 获取统计
        stats = fault_system.get_fault_statistics()
        assert stats["total_faults"] > 0
        
        print("✓ Fault Detector test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Fault Detector import failed: {e}")
        return False

def test_auto_recovery_standalone():
    """独立测试自动恢复系统"""
    try:
        from aceflow_mcp_server.recovery.auto_recovery import AutoRecoverySystem, RecoveryStatus
        from aceflow_mcp_server.recovery.fault_detector import FaultEvent, FaultType, FaultSeverity
        
        recovery_system = AutoRecoverySystem()
        
        # 创建模拟故障
        fault = FaultEvent(
            fault_type=FaultType.PERFORMANCE_DEGRADATION,
            severity=FaultSeverity.HIGH,
            timestamp=time.time(),
            component="test_component",
            description="Test fault",
            metrics={"test_metric": 100}
        )
        
        # 尝试恢复
        result = recovery_system.handle_fault(fault)
        
        # 检查结果（可能为None如果没有合适的策略）
        if result:
            assert result.status in [RecoveryStatus.SUCCESS, RecoveryStatus.FAILED]
        
        # 获取统计
        stats = recovery_system.get_recovery_statistics()
        assert "total_recoveries" in stats
        
        print("✓ Auto Recovery test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Auto Recovery import failed: {e}")
        return False

def run_all_tests():
    """运行所有独立测试"""
    print("🔧 Running standalone tests for new systems...\n")
    
    tests = [
        test_cache_manager_standalone,
        test_performance_monitor_standalone,
        test_error_handler_standalone,
        test_input_validator_standalone,
        test_audit_logger_standalone,
        test_health_checker_standalone,
        test_fault_detector_standalone,
        test_auto_recovery_standalone,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All new systems are working correctly!")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the implementations.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
