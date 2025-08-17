#!/usr/bin/env python3
"""
协作模块集成测试
Collaboration Module Integration Test

This test validates the complete integration of the collaboration module
with the unified architecture.
"""

import sys
import os
import asyncio
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, 'aceflow_mcp_server')

from unified_config import UnifiedConfig, CollaborationConfig
from modules.collaboration_module import CollaborationModule
from modules.core_module import CoreModule
from modules.module_manager import ModuleManager
from unified_server import UnifiedAceFlowServer


async def test_collaboration_module_integration():
    """测试协作模块与统一架构的集成"""
    print("🧪 Testing collaboration module integration with unified architecture...")
    
    # 1. 创建统一配置
    config = UnifiedConfig(
        mode="enhanced",
        core=UnifiedConfig.load_default().core,
        collaboration=CollaborationConfig(enabled=True, confirmation_timeout=60, auto_confirm=False),
        intelligence=UnifiedConfig.load_default().intelligence,
        monitoring=UnifiedConfig.load_default().monitoring
    )
    
    # 2. 创建统一服务器
    server = UnifiedAceFlowServer(config)
    
    # 3. 手动注册核心模块和协作模块
    server.module_manager.register_module_class("core", CoreModule, config.core)
    server.module_manager.register_module_class("collaboration", CollaborationModule, config.collaboration)
    
    # 4. 初始化服务器
    success = await server.initialize()
    assert success == True
    
    # 5. 验证协作模块已注册和初始化
    collab_module = server.module_manager.get_module("collaboration")
    assert collab_module is not None
    assert collab_module.is_available() == True
    assert collab_module.get_module_name() == "collaboration"
    
    # 6. 测试协作模块功能
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 创建项目状态
            aceflow_dir = Path(temp_dir) / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            
            state_data = {
                "project": {"name": "integration_test", "mode": "ENHANCED"}
            }
            
            with open(aceflow_dir / "current_state.json", 'w') as f:
                json.dump(state_data, f)
            
            # 测试 aceflow_task_execute
            result = collab_module.aceflow_task_execute(
                task_id="integration_test_task",
                auto_confirm=False
            )
            assert result["success"] == True
            assert "request_id" in result
            
            # 测试 aceflow_respond
            request_id = result["request_id"]
            response_result = collab_module.aceflow_respond(
                request_id=request_id,
                response="yes, proceed with the task",
                user_id="integration_test_user"
            )
            assert response_result["success"] == True
            
            # 测试 aceflow_collaboration_status
            status_result = collab_module.aceflow_collaboration_status()
            assert status_result["success"] == True
            assert "collaboration_status" in status_result
            
        finally:
            os.chdir(original_cwd)
    
    # 7. 测试服务器状态
    status = server.get_server_status()
    assert status["initialized"] == True
    assert "collaboration" in status["modules"]
    assert status["modules"]["collaboration"]["available"] == True
    
    # 8. 测试健康检查
    health = server.get_health_status()
    assert health["server_healthy"] == True
    assert health["modules_healthy"] == True
    
    # 9. 停止服务器
    await server.stop()
    
    print("✅ Collaboration module integration test passed")


async def test_module_manager_with_collaboration():
    """测试模块管理器与协作模块的集成"""
    print("🧪 Testing module manager with collaboration module...")
    
    # 1. 创建模块管理器
    manager = ModuleManager()
    
    # 2. 注册核心模块和协作模块
    core_config = UnifiedConfig.load_default().core
    collab_config = CollaborationConfig(enabled=True)
    
    manager.register_module_class("core", CoreModule, core_config)
    manager.register_module_class("collaboration", CollaborationModule, collab_config)
    
    # 3. 初始化所有模块
    success = manager.initialize_all_modules()
    assert success == True
    
    # 4. 验证模块状态
    core_status = manager.get_module_status("core")
    collab_status = manager.get_module_status("collaboration")
    
    assert core_status["initialized"] == True
    assert collab_status["initialized"] == True
    assert collab_status["available"] == True
    
    # 5. 测试健康检查
    health = manager.health_check()
    assert health["overall_healthy"] == True
    assert "core" in health["healthy_modules"]
    assert "collaboration" in health["healthy_modules"]
    
    # 6. 测试依赖关系
    collab_module = manager.get_module("collaboration")
    assert collab_module is not None
    assert "core" in collab_module.get_required_dependencies()
    
    # 7. 关闭所有模块
    manager.shutdown_all_modules()
    
    print("✅ Module manager with collaboration module test passed")


async def test_core_collaboration_interaction():
    """测试核心模块与协作模块的交互"""
    print("🧪 Testing core and collaboration module interaction...")
    
    # 1. 创建模块管理器
    manager = ModuleManager()
    
    # 2. 注册模块
    core_config = UnifiedConfig.load_default().core
    collab_config = CollaborationConfig(enabled=True, auto_confirm=False)
    
    manager.register_module_class("core", CoreModule, core_config)
    manager.register_module_class("collaboration", CollaborationModule, collab_config)
    
    # 3. 初始化模块
    success = manager.initialize_all_modules()
    assert success == True
    
    # 4. 获取模块实例
    core_module = manager.get_module("core")
    collab_module = manager.get_module("collaboration")
    
    assert core_module is not None
    assert collab_module is not None
    
    # 5. 测试模块间的协作场景
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 使用核心模块初始化项目
            init_result = core_module.aceflow_init(
                mode="standard",
                project_name="collaboration_test"
            )
            assert init_result["success"] == True
            
            # 使用协作模块执行任务
            task_result = collab_module.aceflow_task_execute(
                task_id="test_interaction_task",
                auto_confirm=False
            )
            assert task_result["success"] == True
            assert "request_id" in task_result
            
            # 响应协作请求
            request_id = task_result["request_id"]
            response_result = collab_module.aceflow_respond(
                request_id=request_id,
                response="confirmed",
                user_id="test_user"
            )
            assert response_result["success"] == True
            
            # 检查协作状态
            status_result = collab_module.aceflow_collaboration_status()
            assert status_result["success"] == True
            
        finally:
            os.chdir(original_cwd)
    
    # 6. 关闭模块
    manager.shutdown_all_modules()
    
    print("✅ Core and collaboration module interaction test passed")


async def test_configuration_driven_collaboration():
    """测试配置驱动的协作功能"""
    print("🧪 Testing configuration-driven collaboration...")
    
    # 测试不同的协作配置
    test_configs = [
        {
            "name": "auto_confirm_enabled",
            "config": CollaborationConfig(enabled=True, auto_confirm=True, confirmation_timeout=30)
        },
        {
            "name": "manual_confirmation",
            "config": CollaborationConfig(enabled=True, auto_confirm=False, confirmation_timeout=300)
        },
        {
            "name": "full_interaction",
            "config": CollaborationConfig(enabled=True, interaction_level="full", confirmation_timeout=600)
        }
    ]
    
    for test_case in test_configs:
        print(f"  Testing {test_case['name']}...")
        
        # 创建协作模块
        collab_module = CollaborationModule(test_case["config"])
        success = collab_module.initialize()
        assert success == True
        
        # 验证配置传递
        health = collab_module.get_health_status()
        assert health["configuration"]["auto_confirm"] == test_case["config"].auto_confirm
        assert health["configuration"]["confirmation_timeout"] == test_case["config"].confirmation_timeout
        assert health["configuration"]["interaction_level"] == test_case["config"].interaction_level
        
        # 测试配置对行为的影响
        task_result = collab_module.aceflow_task_execute(
            task_id=f"config_test_{test_case['name']}",
            auto_confirm=False  # 使用模块配置的auto_confirm
        )
        
        if test_case["config"].auto_confirm:
            # 自动确认应该直接完成任务
            assert task_result["status"] == "completed"
        else:
            # 手动确认应该创建协作请求
            assert task_result["status"] == "pending_confirmation"
            assert "request_id" in task_result
        
        collab_module.cleanup()
    
    print("✅ Configuration-driven collaboration test passed")


async def test_collaboration_error_resilience():
    """测试协作模块的错误恢复能力"""
    print("🧪 Testing collaboration error resilience...")
    
    # 1. 创建协作模块
    config = CollaborationConfig(enabled=True)
    collab_module = CollaborationModule(config)
    collab_module.initialize()
    
    # 2. 测试各种错误场景
    error_scenarios = [
        {
            "name": "invalid_request_id",
            "action": lambda: collab_module.aceflow_respond("nonexistent_id", "yes"),
            "expected_success": False
        },
        {
            "name": "empty_response",
            "setup": lambda: collab_module._active_requests.update({"test_req": {"type": "test"}}),
            "action": lambda: collab_module.aceflow_respond("test_req", ""),
            "expected_success": False
        },
        {
            "name": "invalid_task_id",
            "action": lambda: collab_module.aceflow_task_execute(task_id="", auto_confirm=True),
            "expected_success": True  # 应该生成新的task_id
        }
    ]
    
    for scenario in error_scenarios:
        print(f"  Testing {scenario['name']}...")
        
        # 执行设置（如果有）
        if "setup" in scenario:
            scenario["setup"]()
        
        # 执行操作
        result = scenario["action"]()
        
        # 验证结果
        assert result["success"] == scenario["expected_success"]
        
        # 验证模块仍然健康
        health = collab_module.get_health_status()
        assert health["healthy"] == True
    
    # 3. 清理
    collab_module.cleanup()
    
    print("✅ Collaboration error resilience test passed")


async def test_collaboration_performance():
    """测试协作模块性能"""
    print("🧪 Testing collaboration performance...")
    
    # 1. 创建协作模块
    config = CollaborationConfig(enabled=True, auto_confirm=True)
    collab_module = CollaborationModule(config)
    collab_module.initialize()
    
    # 2. 执行多次操作测试性能
    num_operations = 10
    
    for i in range(num_operations):
        # 执行任务
        task_result = collab_module.aceflow_task_execute(
            task_id=f"perf_test_task_{i}",
            auto_confirm=True
        )
        assert task_result["success"] == True
        
        # 查询状态
        status_result = collab_module.aceflow_collaboration_status()
        assert status_result["success"] == True
    
    # 3. 验证统计信息
    assert collab_module.stats.total_calls >= num_operations * 2  # 每次循环2个调用
    assert collab_module.get_success_rate() > 0.8  # 至少80%成功率
    
    # 4. 获取性能信息
    info = collab_module.get_module_info()
    stats = info["stats"]
    
    assert stats["total_calls"] >= num_operations * 2
    assert stats["average_call_duration"] >= 0.0
    
    # 5. 清理
    collab_module.cleanup()
    
    print("✅ Collaboration performance test passed")


async def main():
    """运行所有集成测试"""
    print("🚀 Starting collaboration module integration tests...\n")
    
    try:
        await test_collaboration_module_integration()
        await test_module_manager_with_collaboration()
        await test_core_collaboration_interaction()
        await test_configuration_driven_collaboration()
        await test_collaboration_error_resilience()
        await test_collaboration_performance()
        
        print("\n🎉 All collaboration module integration tests passed!")
        print("\n📊 Integration Summary:")
        print("   ✅ Collaboration Module Integration - Working")
        print("   ✅ Module Manager Integration - Working")
        print("   ✅ Core-Collaboration Interaction - Working")
        print("   ✅ Configuration-Driven Collaboration - Working")
        print("   ✅ Error Resilience - Working")
        print("   ✅ Performance Testing - Working")
        print("\n🏗️ Task 2.2 - Collaboration Module (CollaborationModule) Implementation Complete!")
        print("\n🎯 Ready for Next Task: 2.3 - Implement Intelligence Module")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)