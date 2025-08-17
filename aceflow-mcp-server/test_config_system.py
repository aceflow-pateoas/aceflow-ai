#!/usr/bin/env python3
"""
测试统一配置管理系统
Test Unified Configuration Management System
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import sys
sys.path.insert(0, 'aceflow_mcp_server')
from aceflow_mcp_server.unified_config import (
    UnifiedConfig, ConfigSource, ConfigManager, 
    detect_legacy_config, auto_migrate_config, load_unified_config, get_config_manager
)


def test_default_config():
    """测试默认配置"""
    print("🧪 Testing default configuration...")
    
    config = UnifiedConfig.load_default()
    
    assert config.mode == "standard"
    assert config.core.enabled == True
    assert config.collaboration.enabled == False
    assert config.intelligence.enabled == False
    assert config.monitoring.enabled == True
    
    # 测试验证
    assert config.validate() == True
    assert len(config.get_validation_errors()) == 0
    
    print("✅ Default configuration test passed")


def test_config_validation():
    """测试配置验证"""
    print("🧪 Testing configuration validation...")
    
    # 测试无效模式
    config = UnifiedConfig(mode="invalid_mode")
    assert config.validate() == False
    assert len(config.get_validation_errors()) > 0
    
    # 测试无效质量阈值
    config = UnifiedConfig()
    config.core.quality_threshold = 1.5
    assert config.validate() == False
    
    # 测试无效超时时间
    config = UnifiedConfig()
    config.collaboration.confirmation_timeout = -1
    assert config.validate() == False
    
    print("✅ Configuration validation test passed")


def test_config_from_dict():
    """测试从字典创建配置"""
    print("🧪 Testing configuration from dictionary...")
    
    config_data = {
        "mode": "enhanced",
        "core": {
            "auto_advance": True,
            "quality_threshold": 0.9
        },
        "collaboration": {
            "enabled": True,
            "confirmation_timeout": 600
        },
        "intelligence": {
            "enabled": True,
            "intent_recognition": True
        }
    }
    
    config = UnifiedConfig.from_dict(config_data)
    
    assert config.mode == "enhanced"
    assert config.core.auto_advance == True
    assert config.core.quality_threshold == 0.9
    assert config.collaboration.enabled == True
    assert config.collaboration.confirmation_timeout == 600
    assert config.intelligence.enabled == True
    assert config.intelligence.intent_recognition == True
    
    print("✅ Configuration from dictionary test passed")


def test_config_manager():
    """测试配置管理器"""
    print("🧪 Testing configuration manager...")
    
    manager = ConfigManager()
    
    # 测试加载默认配置
    config = manager.load_config(auto_migrate=False)
    assert config.mode == "standard"
    
    # 测试获取配置
    same_config = manager.get_config()
    assert same_config.mode == config.mode
    
    # 测试更新配置
    success = manager.update_config({"mode": "enhanced", "collaboration_enabled": True})
    assert success == True
    
    updated_config = manager.get_config()
    assert updated_config.mode == "enhanced"
    assert updated_config.collaboration.enabled == True
    
    # 测试有效模式
    effective_mode = manager.get_effective_mode()
    assert effective_mode in ["basic", "standard", "enhanced"]
    
    # 测试功能检查
    assert manager.is_feature_enabled("collaboration") == True
    assert manager.is_feature_enabled("core") == True
    
    # 测试配置摘要
    summary = manager.get_config_summary()
    assert "mode" in summary
    assert "effective_mode" in summary
    assert "features" in summary
    assert "validation_status" in summary
    
    print("✅ Configuration manager test passed")


def test_legacy_detection():
    """测试旧配置检测"""
    print("🧪 Testing legacy configuration detection...")
    
    # 这个测试不会创建实际文件，只是测试函数不会崩溃
    legacy_info = detect_legacy_config()
    
    assert isinstance(legacy_info, dict)
    assert "type" in legacy_info
    assert "found" in legacy_info
    assert legacy_info["type"] in ["basic", "standard", "enhanced", "unified"]
    
    print("✅ Legacy configuration detection test passed")


def test_global_config_manager():
    """测试全局配置管理器"""
    print("🧪 Testing global configuration manager...")
    
    manager1 = get_config_manager()
    manager2 = get_config_manager()
    
    # 应该是同一个实例
    assert manager1 is manager2
    
    print("✅ Global configuration manager test passed")


def main():
    """运行所有测试"""
    print("🚀 Starting configuration system tests...\n")
    
    try:
        test_default_config()
        test_config_validation()
        test_config_from_dict()
        test_config_manager()
        test_legacy_detection()
        test_global_config_manager()
        
        print("\n🎉 All configuration system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)