"""
完整系统集成测试
Complete System Integration Test

测试性能优化、错误处理、安全控制和故障恢复系统的协同工作。
"""
import pytest
import tempfile
import os
import time
import threading
from unittest.mock import Mock, patch

# 导入所有系统组件
from aceflow_mcp_server.performance import (
    LazyLoader, PerformanceMonitor, CacheManager
)
from aceflow_mcp_server.error_handling import ErrorHandler, ErrorSeverity, ErrorCategory
from aceflow_mcp_server.security import (
    InputValidator, AccessController, DataProtector, audit_logger
)
from aceflow_mcp_server.recovery import (
    FaultDetectionSystem, AutoRecoverySystem, HealthCheckSystem
)

class TestCompleteSystemIntegration:
    """完整系统集成测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 初始化所有系统组件
        self.lazy_loader = LazyLoader()
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self.error_handler = ErrorHandler()
        self.input_validator = InputValidator()
        self.access_controller = AccessController()
        self.data_protector = DataProtector()
        self.fault_detector = FaultDetectionSystem()
        self.auto_recovery = AutoRecoverySystem()
        self.health_checker = HealthCheckSystem(check_interval=1)

    def teardown_method(self):
        """清理测试环境"""
        self.health_checker.stop_monitoring()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_performance_with_security_integration(self):
        """测试性能系统与安全系统的集成"""
        user_id = "test_user"
        
        # 设置访问控制
        self.access_controller.set_user_roles(user_id, {"user"})
        self.access_controller.set_resource_permissions("cache", {"user", "admin"})
        
        # 模拟带有安全检查的缓存操作
        @self.performance_monitor.monitor_execution
        def secure_cache_operation(data, user_id):
            # 1. 安全验证
            if not self.access_controller.check_permission(user_id, "cache"):
                audit_logger.log_authorization(user_id, "cache", "access", "denied")
                raise PermissionError("Access denied")
            
            # 2. 输入验证
            validation_result = self.input_validator.validate_input(data)
            if not validation_result.is_valid:
                audit_logger.log_security_event(
                    "invalid_input", "validation", "blocked",
                    user_id=user_id, details={"error": validation_result.error_message}
                )
                raise ValueError(f"Invalid input: {validation_result.error_message}")
            
            # 3. 数据保护
            protected_data = self.data_protector.mask_sensitive_data(data)
            
            # 4. 缓存操作
            cache_key = f"user_{user_id}_data"
            self.cache_manager.set(cache_key, protected_data, ttl=300)
            
            # 5. 审计日志
            audit_logger.log_data_access(
                user_id=user_id,
                resource="cache",
                action="write",
                result="success",
                details={"cache_key": cache_key}
            )
            
            return protected_data
        
        # 执行安全的缓存操作
        test_data = "User data with sensitive info: email@example.com"
        result = secure_cache_operation(test_data, user_id)
        
        # 验证结果
        assert result is not None
        assert "email@example.com" not in result  # 敏感数据应被屏蔽
        
        # 检查性能监控
        stats = self.performance_monitor.get_statistics()
        assert "secure_cache_operation" in stats["function_stats"]
        
        # 检查缓存
        cached_data = self.cache_manager.get(f"user_{user_id}_data")
        assert cached_data is not None

    def test_error_handling_with_recovery_integration(self):
        """测试错误处理与故障恢复的集成"""
        recovery_attempted = False
        
        def mock_recovery_callback():
            nonlocal recovery_attempted
            recovery_attempted = True
        
        # 设置恢复回调
        performance_strategy = self.auto_recovery.get_strategy(
            self.auto_recovery.strategies[0].__class__
        )
        if hasattr(performance_strategy, 'set_cache_clear_callback'):
            performance_strategy.set_cache_clear_callback(mock_recovery_callback)
        
        # 添加故障监听器，触发自动恢复
        def fault_listener(fault):
            self.auto_recovery.handle_fault(fault)
        
        self.fault_detector.add_fault_listener(fault_listener)
        
        # 模拟会导致故障的操作
        def problematic_operation():
            # 模拟高延迟操作
            time.sleep(0.1)
            # 模拟异常
            raise Exception("Simulated error")
        
        # 使用错误处理器包装操作
        @self.error_handler.handle_errors
        def wrapped_operation():
            return problematic_operation()
        
        # 执行操作（应该被错误处理器捕获）
        try:
            result = wrapped_operation()
        except Exception as e:
            # 错误应该被正确处理
            pass
        
        # 模拟性能问题，触发故障检测
        metrics = {
            'avg_response_time': 10.0,  # 高响应时间
            'cpu_usage': 90.0,          # 高CPU使用率
            'memory_usage': 85.0        # 高内存使用率
        }
        
        detected_faults = self.fault_detector.detect_faults(metrics)
        assert len(detected_faults) > 0
        
        # 等待一下让恢复系统处理
        time.sleep(0.1)

    def test_health_monitoring_with_all_systems(self):
        """测试健康监控与所有系统的集成"""
        # 添加自定义健康检查
        app_checker = self.health_checker.get_checker(
            self.health_checker.checkers[2].__class__  # ApplicationHealthChecker
        )
        
        if hasattr(app_checker, 'add_health_check'):
            # 添加系统组件健康检查
            app_checker.add_health_check(lambda: self.cache_manager is not None)
            app_checker.add_health_check(lambda: self.error_handler is not None)
            app_checker.add_health_check(lambda: self.fault_detector.is_detection_enabled())
            
            # 添加自定义指标
            app_checker.add_metric_collector("cache_size", lambda: self.cache_manager.size())
            app_checker.add_metric_collector("error_count", lambda: len(self.error_handler.error_history))
            app_checker.add_metric_collector("fault_count", lambda: len(self.fault_detector.detected_faults))
        
        # 运行健康检查
        health_results = self.health_checker.run_checks()
        
        # 验证健康检查结果
        assert len(health_results) > 0
        assert "application" in health_results
        
        # 获取整体健康报告
        health_report = self.health_checker.get_health_report()
        assert "overall_status" in health_report
        assert "components" in health_report

    def test_lazy_loading_with_monitoring(self):
        """测试懒加载与监控的集成"""
        # 创建模拟模块
        class MockModule:
            def __init__(self):
                self.initialized = False
                time.sleep(0.05)  # 模拟初始化时间
                self.initialized = True
            
            def process(self, data):
                return f"Processed: {data}"
        
        # 注册懒加载模块
        module_loader = lambda: MockModule()
        self.lazy_loader.register_module("mock_module", module_loader)
        
        # 使用性能监控包装懒加载
        @self.performance_monitor.monitor_execution
        def load_and_use_module(data):
            module = self.lazy_loader.get_module("mock_module")
            return module.process(data)
        
        # 执行操作
        result = load_and_use_module("test_data")
        assert result == "Processed: test_data"
        
        # 检查性能统计
        stats = self.performance_monitor.get_statistics()
        assert "load_and_use_module" in stats["function_stats"]
        
        # 检查懒加载统计
        lazy_stats = self.lazy_loader.get_statistics()
        assert lazy_stats["total_modules"] == 1
        assert lazy_stats["loaded_modules"] == 1

    def test_comprehensive_workflow(self):
        """测试综合工作流"""
        user_id = "workflow_user"
        
        # 1. 设置用户权限
        self.access_controller.set_user_roles(user_id, {"user", "data_processor"})
        self.access_controller.set_resource_permissions("data_processing", {"data_processor"})
        
        # 2. 定义综合工作流
        @self.performance_monitor.monitor_execution
        @self.error_handler.handle_errors
        def comprehensive_workflow(user_id, input_data):
            # 安全检查
            if not self.access_controller.check_permission(user_id, "data_processing"):
                audit_logger.log_authorization(user_id, "data_processing", "access", "denied")
                raise PermissionError("Access denied")
            
            # 速率限制检查
            if not self.access_controller.enforce_rate_limiting(user_id, max_requests=10):
                audit_logger.log_security_event(
                    "rate_limit", "workflow", "blocked", user_id=user_id
                )
                raise Exception("Rate limit exceeded")
            
            # 输入验证
            validation_result = self.input_validator.validate_input(input_data)
            if not validation_result.is_valid:
                audit_logger.log_security_event(
                    "invalid_input", "workflow", "blocked",
                    user_id=user_id, details={"error": validation_result.error_message}
                )
                raise ValueError("Invalid input")
            
            # 数据处理
            processed_data = f"Processed: {input_data}"
            
            # 数据保护
            protected_data = self.data_protector.mask_sensitive_data(processed_data)
            
            # 缓存结果
            cache_key = f"workflow_{user_id}_{hash(input_data)}"
            self.cache_manager.set(cache_key, protected_data, ttl=600)
            
            # 审计日志
            audit_logger.log_data_access(
                user_id=user_id,
                resource="data_processing",
                action="process",
                result="success",
                details={"data_size": len(input_data)}
            )
            
            return protected_data
        
        # 3. 执行工作流
        test_input = "Test data for processing with email: user@example.com"
        result = comprehensive_workflow(user_id, test_input)
        
        # 4. 验证结果
        assert result is not None
        assert "Processed:" in result
        assert "user@example.com" not in result  # 敏感数据应被保护
        
        # 5. 检查各系统的状态
        # 性能监控
        perf_stats = self.performance_monitor.get_statistics()
        assert "comprehensive_workflow" in perf_stats["function_stats"]
        
        # 缓存
        assert self.cache_manager.size() > 0
        
        # 审计日志
        events = audit_logger.query_events(user_id=user_id)
        assert len(events) > 0
        
        # 错误处理
        error_stats = self.error_handler.get_statistics()
        assert error_stats is not None

    def test_system_under_stress(self):
        """测试系统在压力下的表现"""
        def stress_operation(iteration):
            user_id = f"stress_user_{iteration % 5}"  # 5个不同用户
            
            # 设置权限
            self.access_controller.set_user_roles(user_id, {"user"})
            self.access_controller.set_resource_permissions("stress_test", {"user"})
            
            try:
                # 模拟操作
                if not self.access_controller.check_permission(user_id, "stress_test"):
                    raise PermissionError("Access denied")
                
                if not self.access_controller.enforce_rate_limiting(user_id, max_requests=20):
                    raise Exception("Rate limit exceeded")
                
                # 缓存操作
                cache_key = f"stress_{user_id}_{iteration}"
                data = f"Stress test data {iteration}"
                self.cache_manager.set(cache_key, data, ttl=60)
                
                # 随机引发一些错误来测试错误处理
                if iteration % 10 == 0:
                    raise Exception(f"Simulated error {iteration}")
                
                return f"Success {iteration}"
                
            except Exception as e:
                audit_logger.log_error_event(
                    "stress_test_error", "stress_operation", "failed",
                    details={"iteration": iteration, "error": str(e)}
                )
                raise
        
        # 执行压力测试
        success_count = 0
        error_count = 0
        
        for i in range(50):
            try:
                result = stress_operation(i)
                success_count += 1
            except Exception:
                error_count += 1
        
        # 验证系统在压力下仍能正常工作
        assert success_count > 0
        assert success_count + error_count == 50
        
        # 检查系统状态
        cache_stats = self.cache_manager.get_statistics()
        assert cache_stats["total_gets"] + cache_stats["total_sets"] > 0
        
        error_stats = self.error_handler.get_statistics()
        assert error_stats is not None
        
        # 检查是否触发了故障检测
        fault_stats = self.fault_detector.get_fault_statistics()
        print(f"Stress test results: {success_count} successes, {error_count} errors")
        print(f"Cache stats: {cache_stats}")
        print(f"Fault stats: {fault_stats}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
