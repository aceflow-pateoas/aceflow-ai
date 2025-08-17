#!/usr/bin/env python3
"""
测试模块系统
Test Module System
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, 'aceflow_mcp_server')

from aceflow_mcp_server.modules.base_module import BaseModule, ModuleState, ModuleMetadata
from aceflow_mcp_server.modules.module_manager import ModuleManager


class TestCoreModule(BaseModule):
    """测试核心模块"""
    
    def get_module_name(self) -> str:
        return "test_core"
    
    def _do_initialize(self) -> bool:
        print(f"Initializing {self.get_module_name()}")
        return True
    
    def _do_cleanup(self):
        print(f"Cleaning up {self.get_module_name()}")
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "status": "running",
            "details": "Core module is healthy"
        }


class TestCollaborationModule(BaseModule):
    """测试协作模块"""
    
    def __init__(self, config):
        metadata = ModuleMetadata(
            name="test_collaboration",
            version="1.0.0",
            description="Test collaboration module",
            dependencies=["test_core"],
            provides=["collaboration"]
        )
        super().__init__(config, metadata)
    
    def get_module_name(self) -> str:
        return "test_collaboration"
    
    def _do_initialize(self) -> bool:
        print(f"Initializing {self.get_module_name()}")
        return True
    
    def _do_cleanup(self):
        print(f"Cleaning up {self.get_module_name()}")
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "status": "running",
            "details": "Collaboration module is healthy"
        }


class TestIntelligenceModule(BaseModule):
    """测试智能模块"""
    
    def __init__(self, config):
        metadata = ModuleMetadata(
            name="test_intelligence",
            version="1.0.0",
            description="Test intelligence module",
            dependencies=["test_core"],
            optional_dependencies=["test_collaboration"],
            provides=["intelligence"]
        )
        super().__init__(config, metadata)
    
    def get_module_name(self) -> str:
        return "test_intelligence"
    
    def _do_initialize(self) -> bool:
        print(f"Initializing {self.get_module_name()}")
        return True
    
    def _do_cleanup(self):
        print(f"Cleaning up {self.get_module_name()}")
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "status": "running",
            "details": "Intelligence module is healthy"
        }


class TestConfig:
    """测试配置类"""
    def __init__(self, enabled=True):
        self.enabled = enabled


def test_base_module():
    """测试基础模块"""
    print("🧪 Testing base module...")
    
    config = TestConfig()
    module = TestCoreModule(config)
    
    # 测试初始状态
    assert module.state == ModuleState.UNINITIALIZED
    assert module.enabled == True
    assert module.initialized == False
    assert module.is_available() == False
    
    # 测试初始化
    success = module.initialize()
    assert success == True
    assert module.state == ModuleState.READY
    assert module.initialized == True
    assert module.is_available() == True
    
    # 测试健康检查
    assert module.is_healthy() == True
    
    # 测试统计
    module.record_call(success=True, duration=0.1)
    assert module.stats.total_calls == 1
    assert module.stats.successful_calls == 1
    assert module.get_success_rate() == 1.0
    
    # 测试清理
    module.cleanup()
    assert module.state == ModuleState.SHUTDOWN
    assert module.initialized == False
    
    print("✅ Base module test passed")


def test_module_dependencies():
    """测试模块依赖"""
    print("🧪 Testing module dependencies...")
    
    config = TestConfig()
    
    # 创建有依赖的模块
    collab_module = TestCollaborationModule(config)
    
    # 测试依赖信息
    dependencies = collab_module.get_required_dependencies()
    assert "test_core" in dependencies
    
    # 测试依赖解决
    assert collab_module.are_dependencies_resolved() == False
    
    collab_module.mark_dependency_resolved("test_core")
    assert collab_module.are_dependencies_resolved() == True
    
    print("✅ Module dependencies test passed")


def test_module_manager():
    """测试模块管理器"""
    print("🧪 Testing module manager...")
    
    manager = ModuleManager()
    config = TestConfig()
    
    # 注册模块类
    manager.register_module_class("test_core", TestCoreModule, config)
    manager.register_module_class("test_collaboration", TestCollaborationModule, config)
    manager.register_module_class("test_intelligence", TestIntelligenceModule, config)
    
    # 测试模块列表
    modules = manager.list_modules()
    assert "test_core" in modules
    assert "test_collaboration" in modules
    assert "test_intelligence" in modules
    
    # 测试初始化顺序
    order = manager.get_initialization_order()
    print(f"Initialization order: {order}")
    
    # core应该在collaboration之前
    core_index = order.index("test_core")
    collab_index = order.index("test_collaboration")
    assert core_index < collab_index
    
    # 测试模块获取（懒加载）
    core_module = manager.get_module("test_core")
    assert core_module is not None
    assert core_module.get_module_name() == "test_core"
    
    # 测试模块初始化
    success = manager.initialize_module("test_collaboration")
    assert success == True
    
    # 测试模块状态
    status = manager.get_module_status("test_core")
    assert status["name"] == "test_core"
    assert status["initialized"] == True
    
    # 测试健康检查
    health = manager.health_check()
    assert health["overall_healthy"] == True
    assert "test_core" in health["healthy_modules"]
    
    # 测试关闭
    manager.shutdown_all_modules()
    
    print("✅ Module manager test passed")


def test_module_lifecycle():
    """测试模块生命周期"""
    print("🧪 Testing module lifecycle...")
    
    manager = ModuleManager()
    config = TestConfig()
    
    # 注册模块
    manager.register_module_class("test_core", TestCoreModule, config)
    
    # 测试初始化
    success = manager.initialize_module("test_core")
    assert success == True
    
    # 测试重新加载
    success = manager.reload_module("test_core")
    assert success == True
    
    # 测试配置更新
    new_config = TestConfig(enabled=False)
    success = manager.update_module_config("test_core", new_config)
    assert success == True
    
    # 测试关闭
    manager.shutdown_module("test_core")
    
    print("✅ Module lifecycle test passed")


def test_disabled_module():
    """测试禁用模块"""
    print("🧪 Testing disabled module...")
    
    config = TestConfig(enabled=False)
    module = TestCoreModule(config)
    
    # 测试禁用模块的初始化
    success = module.initialize()
    assert success == True  # 初始化成功，但模块被禁用
    assert module.state == ModuleState.DISABLED
    assert module.is_available() == False
    
    print("✅ Disabled module test passed")


def main():
    """运行所有测试"""
    print("🚀 Starting module system tests...\n")
    
    try:
        test_base_module()
        test_module_dependencies()
        test_module_manager()
        test_module_lifecycle()
        test_disabled_module()
        
        print("\n🎉 All module system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)