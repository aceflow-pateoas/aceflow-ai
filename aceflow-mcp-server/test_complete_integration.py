#!/usr/bin/env python3
"""
完整集成测试
Complete Integration Test

This test validates the complete integration of the core module
with the unified architecture.
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, 'aceflow_mcp_server')

from unified_config import UnifiedConfig, CoreConfig
from modules.core_module import CoreModule
from modules.module_manager import ModuleManager
from unified_server import UnifiedAceFlowServer


async def test_core_module_integration():
    """测试核心模块与统一架构的集成"""
    print("🧪 Testing core module integration with unified architecture...")
    
    # 1. 创建统一配置
    config = UnifiedConfig(
        mode="standard",
        core=CoreConfig(enabled=True, default_mode="standard", auto_advance=False),
        collaboration=UnifiedConfig.load_default().collaboration,
        intelligence=UnifiedConfig.load_default().intelligence,
        monitoring=UnifiedConfig.load_default().monitoring
    )
    
    # 2. 创建统一服务器
    server = UnifiedAceFlowServer(config)
    
    # 3. 手动注册核心模块
    server.module_manager.register_module_class(
        "core", 
        CoreModule, 
        config.core
    )
    
    # 4. 初始化服务器
    success = await server.initialize()
    assert success == True
    
    # 5. 验证核心模块已注册和初始化
    core_module = server.module_manager.get_module("core")
    assert core_module is not None
    assert core_module.is_available() == True
    assert core_module.get_module_name() == "core"
    
    # 6. 测试核心模块功能
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 测试 aceflow_init
            result = core_module.aceflow_init(
                mode="standard",
                project_name="integration_test"
            )
            assert result["success"] == True
            
            # 测试 aceflow_stage
            result = core_module.aceflow_stage(action="status")
            assert "success" in result
            
            # 测试 aceflow_validate
            result = core_module.aceflow_validate(mode="basic")
            assert "success" in result
            
        finally:
            os.chdir(original_cwd)
    
    # 7. 测试服务器状态
    status = server.get_server_status()
    assert status["initialized"] == True
    assert "core" in status["modules"]
    assert status["modules"]["core"]["available"] == True
    
    # 8. 测试健康检查
    health = server.get_health_status()
    assert health["server_healthy"] == True
    assert health["modules_healthy"] == True
    
    # 9. 停止服务器
    await server.stop()
    
    print("✅ Core module integration test passed")


async def test_module_manager_with_core():
    """测试模块管理器与核心模块的集成"""
    print("🧪 Testing module manager with core module...")
    
    # 1. 创建模块管理器
    manager = ModuleManager()
    
    # 2. 注册核心模块
    core_config = CoreConfig(enabled=True)
    manager.register_module_class("core", CoreModule, core_config)
    
    # 3. 初始化所有模块
    success = manager.initialize_all_modules()
    assert success == True
    
    # 4. 验证模块状态
    status = manager.get_module_status("core")
    assert status["initialized"] == True
    assert status["available"] == True
    assert status["healthy"] == True
    
    # 5. 测试健康检查
    health = manager.health_check()
    assert health["overall_healthy"] == True
    assert "core" in health["healthy_modules"]
    
    # 6. 测试模块功能
    core_module = manager.get_module("core")
    assert core_module is not None
    
    # 7. 关闭所有模块
    manager.shutdown_all_modules()
    
    print("✅ Module manager with core module test passed")


async def test_configuration_integration():
    """测试配置与核心模块的集成"""
    print("🧪 Testing configuration integration with core module...")
    
    # 1. 创建不同的配置
    configs = [
        UnifiedConfig(mode="basic", core=CoreConfig(enabled=True, default_mode="minimal")),
        UnifiedConfig(mode="standard", core=CoreConfig(enabled=True, default_mode="standard")),
        UnifiedConfig(mode="enhanced", core=CoreConfig(enabled=True, default_mode="complete"))
    ]
    
    for config in configs:
        # 2. 创建核心模块
        core_module = CoreModule(config.core)
        
        # 3. 初始化模块
        success = core_module.initialize()
        assert success == True
        
        # 4. 验证配置传递
        assert core_module.config.enabled == config.core.enabled
        assert core_module.config.default_mode == config.core.default_mode
        
        # 5. 清理
        core_module.cleanup()
    
    print("✅ Configuration integration test passed")


async def test_error_resilience():
    """测试错误恢复能力"""
    print("🧪 Testing error resilience...")
    
    # 1. 创建配置
    config = CoreConfig(enabled=True)
    
    # 2. 创建核心模块
    core_module = CoreModule(config)
    core_module.initialize()
    
    # 3. 测试错误处理
    try:
        # 测试无效参数
        result = core_module.aceflow_init(mode="invalid_mode")
        # 应该优雅处理错误
        assert "success" in result
        
        # 测试无效操作
        result = core_module.aceflow_stage(action="invalid_action")
        assert result["success"] == False
        assert "error" in result
        
        # 验证模块仍然健康
        health = core_module.get_health_status()
        assert health["healthy"] == True
        
    except Exception as e:
        # 如果有异常，确保模块仍然可用
        assert core_module.is_available() == True
    
    # 4. 清理
    core_module.cleanup()
    
    print("✅ Error resilience test passed")


async def test_performance_tracking():
    """测试性能跟踪"""
    print("🧪 Testing performance tracking...")
    
    # 1. 创建核心模块
    config = CoreConfig(enabled=True)
    core_module = CoreModule(config)
    core_module.initialize()
    
    # 2. 执行多次操作
    for i in range(5):
        result = core_module.aceflow_stage(action="status")
    
    # 3. 验证统计信息
    assert core_module.stats.total_calls >= 5
    assert core_module.get_success_rate() >= 0.0
    
    # 4. 获取模块信息
    info = core_module.get_module_info()
    assert "stats" in info
    assert info["stats"]["total_calls"] >= 5
    
    # 5. 清理
    core_module.cleanup()
    
    print("✅ Performance tracking test passed")


async def main():
    """运行所有集成测试"""
    print("🚀 Starting complete integration tests...\n")
    
    try:
        await test_core_module_integration()
        await test_module_manager_with_core()
        await test_configuration_integration()
        await test_error_resilience()
        await test_performance_tracking()
        
        print("\n🎉 All complete integration tests passed!")
        print("\n📊 Integration Summary:")
        print("   ✅ Core Module Integration - Working")
        print("   ✅ Module Manager Integration - Working")
        print("   ✅ Configuration Integration - Working")
        print("   ✅ Error Resilience - Working")
        print("   ✅ Performance Tracking - Working")
        print("\n🏗️ Task 2.1 - Core Module (CoreModule) Implementation Complete!")
        print("\n🎯 Ready for Next Task: 2.2 - Implement Collaboration Module")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)