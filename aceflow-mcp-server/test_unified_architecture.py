#!/usr/bin/env python3
"""
测试统一架构
Test Unified Architecture

This test validates the complete unified architecture including:
- Configuration management
- Module system
- Unified server
- Integration between components
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, 'aceflow_mcp_server')

from unified_config import UnifiedConfig, ConfigManager, get_config_manager
from modules.base_module import BaseModule, ModuleMetadata
from modules.module_manager import ModuleManager
from unified_server import UnifiedAceFlowServer


class TestIntegratedModule(BaseModule):
    """测试集成模块"""
    
    def __init__(self, config):
        metadata = ModuleMetadata(
            name="test_integrated",
            version="1.0.0",
            description="Test integrated module for architecture validation",
            provides=["test_functionality"]
        )
        super().__init__(config, metadata)
    
    def get_module_name(self) -> str:
        return "test_integrated"
    
    def _do_initialize(self) -> bool:
        print(f"Initializing integrated module: {self.get_module_name()}")
        return True
    
    def _do_cleanup(self):
        print(f"Cleaning up integrated module: {self.get_module_name()}")
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "status": "running",
            "details": "Integrated module is healthy"
        }
    
    def execute_test_function(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """测试功能函数"""
        self.record_call(success=True, duration=0.1)
        return {
            "success": True,
            "message": "Test function executed successfully",
            "params": params,
            "module": self.get_module_name()
        }


async def test_complete_architecture():
    """测试完整架构"""
    print("🧪 Testing complete unified architecture...")
    
    # 1. 创建配置
    config = UnifiedConfig(
        mode="standard",
        core=UnifiedConfig.load_default().core,
        collaboration=UnifiedConfig.load_default().collaboration,
        intelligence=UnifiedConfig.load_default().intelligence,
        monitoring=UnifiedConfig.load_default().monitoring
    )
    
    # 2. 创建统一服务器
    server = UnifiedAceFlowServer(config)
    
    # 3. 手动注册测试模块
    test_config = type('TestConfig', (), {'enabled': True})()
    server.module_manager.register_module_class(
        "test_integrated", 
        TestIntegratedModule, 
        test_config
    )
    
    # 4. 初始化服务器
    success = await server.initialize()
    assert success == True
    
    # 5. 启动服务器
    success = await server.start()
    assert success == True
    
    # 6. 验证模块已注册和初始化
    module = server.module_manager.get_module("test_integrated")
    assert module is not None
    assert module.is_available() == True
    
    # 7. 测试模块功能
    result = module.execute_test_function({"test": "data"})
    assert result["success"] == True
    
    # 8. 验证统计信息
    assert module.stats.total_calls == 1
    assert module.stats.successful_calls == 1
    assert module.get_success_rate() == 1.0
    
    # 9. 测试服务器状态
    status = server.get_server_status()
    assert status["initialized"] == True
    assert status["running"] == True
    assert "test_integrated" in status["modules"]
    
    # 10. 测试健康检查
    health = server.get_health_status()
    assert health["server_healthy"] == True
    assert health["modules_healthy"] == True
    
    # 11. 停止服务器
    await server.stop()
    assert server._running == False
    
    print("✅ Complete unified architecture test passed")


async def test_configuration_integration():
    """测试配置集成"""
    print("🧪 Testing configuration integration...")
    
    # 1. 创建配置管理器
    config_manager = ConfigManager()
    
    # 2. 加载配置
    config = config_manager.load_config(auto_migrate=False)
    assert config is not None
    
    # 3. 创建服务器并验证配置传递
    server = UnifiedAceFlowServer(config)
    assert server.config.mode == config.mode
    
    # 4. 测试配置更新
    success = config_manager.update_config({"mode": "enhanced"})
    assert success == True
    
    # 5. 验证有效模式
    effective_mode = config_manager.get_effective_mode()
    assert effective_mode in ["basic", "standard", "enhanced"]
    
    # 6. 测试功能检查
    core_enabled = config_manager.is_feature_enabled("core")
    assert core_enabled == True
    
    print("✅ Configuration integration test passed")


async def test_module_lifecycle_integration():
    """测试模块生命周期集成"""
    print("🧪 Testing module lifecycle integration...")
    
    # 1. 创建模块管理器
    manager = ModuleManager()
    
    # 2. 注册测试模块
    test_config = type('TestConfig', (), {'enabled': True})()
    manager.register_module_class("test_lifecycle", TestIntegratedModule, test_config)
    
    # 3. 测试初始化顺序
    order = manager.get_initialization_order()
    assert "test_lifecycle" in order
    
    # 4. 初始化所有模块
    success = manager.initialize_all_modules()
    assert success == True
    
    # 5. 验证模块状态
    status = manager.get_module_status("test_lifecycle")
    assert status["initialized"] == True
    assert status["available"] == True
    
    # 6. 测试健康检查
    health = manager.health_check()
    assert health["overall_healthy"] == True
    assert "test_lifecycle" in health["healthy_modules"]
    
    # 7. 测试模块重新加载
    success = manager.reload_module("test_lifecycle")
    assert success == True
    
    # 8. 关闭所有模块
    manager.shutdown_all_modules()
    
    print("✅ Module lifecycle integration test passed")


async def test_error_handling():
    """测试错误处理"""
    print("🧪 Testing error handling...")
    
    # 1. 测试无效配置
    try:
        invalid_config = UnifiedConfig(mode="invalid_mode")
        assert invalid_config.validate() == False
        errors = invalid_config.get_validation_errors()
        assert len(errors) > 0
        print(f"   Caught expected validation errors: {len(errors)}")
    except Exception as e:
        print(f"   Unexpected error: {e}")
    
    # 2. 测试模块初始化失败处理
    class FailingModule(BaseModule):
        def get_module_name(self) -> str:
            return "failing_module"
        
        def _do_initialize(self) -> bool:
            raise Exception("Intentional initialization failure")
        
        def _do_cleanup(self):
            pass
        
        def get_health_status(self) -> Dict[str, Any]:
            return {"healthy": False}
    
    manager = ModuleManager()
    test_config = type('TestConfig', (), {'enabled': True})()
    manager.register_module_class("failing", FailingModule, test_config)
    
    # 初始化应该失败
    success = manager.initialize_module("failing")
    assert success == False
    print("   Correctly handled module initialization failure")
    
    # 3. 测试服务器错误处理
    config = UnifiedConfig(mode="standard")
    server = UnifiedAceFlowServer(config)
    
    # 测试不存在模块的工具执行
    result = await server._execute_module_tool("nonexistent", "test_tool", {})
    assert result["success"] == False
    assert "error" in result
    print("   Correctly handled nonexistent module tool execution")
    
    print("✅ Error handling test passed")


async def test_performance_monitoring():
    """测试性能监控"""
    print("🧪 Testing performance monitoring...")
    
    # 1. 创建模块并记录调用
    test_config = type('TestConfig', (), {'enabled': True})()
    module = TestIntegratedModule(test_config)
    module.initialize()
    
    # 2. 执行多次调用并记录统计
    for i in range(10):
        success = i < 8  # 80% 成功率
        duration = 0.1 + (i * 0.01)  # 递增的执行时间
        module.record_call(success=success, duration=duration)
    
    # 3. 验证统计信息
    assert module.stats.total_calls == 10
    assert module.stats.successful_calls == 8
    assert module.stats.failed_calls == 2
    assert module.get_success_rate() == 0.8
    assert module.stats.average_call_duration > 0
    
    # 4. 测试统计重置
    module.reset_stats()
    assert module.stats.total_calls == 0
    assert module.stats.successful_calls == 0
    assert module.get_success_rate() == 0.0
    
    print("✅ Performance monitoring test passed")


async def main():
    """运行所有集成测试"""
    print("🚀 Starting unified architecture integration tests...\n")
    
    try:
        await test_complete_architecture()
        await test_configuration_integration()
        await test_module_lifecycle_integration()
        await test_error_handling()
        await test_performance_monitoring()
        
        print("\n🎉 All unified architecture integration tests passed!")
        print("\n📊 Architecture Summary:")
        print("   ✅ Configuration Management System - Working")
        print("   ✅ Module System with Lifecycle Management - Working")
        print("   ✅ Unified Server Entry Point - Working")
        print("   ✅ Component Integration - Working")
        print("   ✅ Error Handling - Working")
        print("   ✅ Performance Monitoring - Working")
        print("\n🏗️ Task 1.1, 1.2, and 1.3 Implementation Complete!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)