#!/usr/bin/env python3
"""
PATEOAS配置管理系统增强测试
测试配置管理的完整功能，包括功能开关、渐进式部署和配置验证
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from aceflow.pateoas.config_manager import (
    PATEOASConfigManager,
    PATEOASConfig,
    FeatureConfig,
    FeatureFlag,
    DeploymentStage,
    get_pateoas_config_manager,
    is_feature_enabled,
    get_pateoas_config
)


def test_config_manager_initialization():
    """测试配置管理器初始化"""
    print("🧪 测试配置管理器初始化...")
    
    # 创建临时配置目录
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        
        # 初始化配置管理器
        config_manager = PATEOASConfigManager(config_dir)
        
        # 验证初始化
        assert config_manager.config_dir == config_dir
        assert config_manager.main_config is not None
        assert len(config_manager.feature_configs) > 0
        
        # 验证默认功能配置
        expected_features = [
            'state_continuity', 'memory_system', 'adaptive_flow',
            'decision_gates', 'performance_monitoring', 'exception_handling'
        ]
        
        for feature in expected_features:
            assert feature in config_manager.feature_configs
            assert config_manager.is_feature_enabled(feature)
        
        print("✅ 配置管理器初始化测试通过")


def test_feature_flag_management():
    """测试功能开关管理"""
    print("🧪 测试功能开关管理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 测试功能启用/禁用
        feature_name = "test_feature"
        feature_config = FeatureConfig(
            name=feature_name,
            enabled=True,
            flag=FeatureFlag.ENABLED,
            description="测试功能",
            rollout_percentage=50.0
        )
        
        # 添加功能配置
        config_manager.add_feature_config(feature_config)
        assert feature_name in config_manager.feature_configs
        
        # 测试功能启用状态
        # 由于rollout_percentage=50%，不同用户可能有不同结果
        user1_enabled = config_manager.is_feature_enabled(feature_name, "user1")
        user2_enabled = config_manager.is_feature_enabled(feature_name, "user2")
        
        print(f"  用户1启用状态: {user1_enabled}")
        print(f"  用户2启用状态: {user2_enabled}")
        
        # 测试100%部署
        config_manager.update_feature_config(feature_name, rollout_percentage=100.0)
        assert config_manager.is_feature_enabled(feature_name, "user1")
        assert config_manager.is_feature_enabled(feature_name, "user2")
        
        # 测试0%部署
        config_manager.update_feature_config(feature_name, rollout_percentage=0.0)
        assert not config_manager.is_feature_enabled(feature_name, "user1")
        assert not config_manager.is_feature_enabled(feature_name, "user2")
        
        # 测试功能禁用
        config_manager.update_feature_config(feature_name, enabled=False)
        assert not config_manager.is_feature_enabled(feature_name, "user1")
        
        print("✅ 功能开关管理测试通过")


def test_deployment_stage_management():
    """测试部署阶段管理"""
    print("🧪 测试部署阶段管理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 创建仅在特定阶段可用的功能
        feature_name = "production_only_feature"
        feature_config = FeatureConfig(
            name=feature_name,
            enabled=True,
            flag=FeatureFlag.ENABLED,
            description="仅生产环境功能",
            deployment_stages=[DeploymentStage.PRODUCTION],
            rollout_percentage=100.0
        )
        
        config_manager.add_feature_config(feature_config)
        
        # 在开发阶段测试
        config_manager.set_deployment_stage(DeploymentStage.DEVELOPMENT)
        assert not config_manager.is_feature_enabled(feature_name)
        
        # 在生产阶段测试
        config_manager.set_deployment_stage(DeploymentStage.PRODUCTION)
        assert config_manager.is_feature_enabled(feature_name)
        
        # 测试多阶段功能
        multi_stage_feature = "multi_stage_feature"
        multi_feature_config = FeatureConfig(
            name=multi_stage_feature,
            enabled=True,
            flag=FeatureFlag.ENABLED,
            description="多阶段功能",
            deployment_stages=[DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
            rollout_percentage=100.0
        )
        
        config_manager.add_feature_config(multi_feature_config)
        
        # 在开发阶段不可用
        config_manager.set_deployment_stage(DeploymentStage.DEVELOPMENT)
        assert not config_manager.is_feature_enabled(multi_stage_feature)
        
        # 在测试阶段可用
        config_manager.set_deployment_stage(DeploymentStage.TESTING)
        assert config_manager.is_feature_enabled(multi_stage_feature)
        
        # 在生产阶段可用
        config_manager.set_deployment_stage(DeploymentStage.PRODUCTION)
        assert config_manager.is_feature_enabled(multi_stage_feature)
        
        print("✅ 部署阶段管理测试通过")


def test_gradual_rollout():
    """测试渐进式部署"""
    print("🧪 测试渐进式部署...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 创建50%部署的功能
        feature_name = "gradual_feature"
        feature_config = FeatureConfig(
            name=feature_name,
            enabled=True,
            flag=FeatureFlag.ENABLED,
            description="渐进式部署功能",
            rollout_percentage=50.0
        )
        
        config_manager.add_feature_config(feature_config)
        
        # 测试多个用户的启用状态
        enabled_count = 0
        total_users = 100
        
        for i in range(total_users):
            user_id = f"user_{i}"
            if config_manager.is_feature_enabled(feature_name, user_id):
                enabled_count += 1
        
        # 验证启用比例接近50%（允许一定误差）
        enabled_percentage = enabled_count / total_users * 100
        print(f"  实际启用比例: {enabled_percentage:.1f}%")
        
        # 允许±10%的误差
        assert 40 <= enabled_percentage <= 60, f"启用比例 {enabled_percentage}% 不在预期范围内"
        
        # 测试一致性：同一用户多次查询应该得到相同结果
        test_user = "consistent_user"
        first_result = config_manager.is_feature_enabled(feature_name, test_user)
        
        for _ in range(10):
            assert config_manager.is_feature_enabled(feature_name, test_user) == first_result
        
        print("✅ 渐进式部署测试通过")


def test_config_validation():
    """测试配置验证"""
    print("🧪 测试配置验证...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 测试有效配置
        validation_result = config_manager.validate_config()
        assert validation_result['valid']
        assert len(validation_result['errors']) == 0
        
        # 测试无效配置
        config_manager.update_main_config(state_cache_size=-1)
        validation_result = config_manager.validate_config()
        assert not validation_result['valid']
        assert len(validation_result['errors']) > 0
        assert any('状态缓存大小必须大于0' in error for error in validation_result['errors'])
        
        # 修复配置
        config_manager.update_main_config(state_cache_size=1000)
        validation_result = config_manager.validate_config()
        assert validation_result['valid']
        
        # 测试功能依赖
        dependent_feature = FeatureConfig(
            name="dependent_feature",
            enabled=True,
            dependencies=["nonexistent_feature"]
        )
        config_manager.add_feature_config(dependent_feature)
        
        validation_result = config_manager.validate_config()
        assert len(validation_result['errors']) > 0
        
        print("✅ 配置验证测试通过")


def test_config_persistence():
    """测试配置持久化"""
    print("🧪 测试配置持久化...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        
        # 创建第一个配置管理器实例
        config_manager1 = PATEOASConfigManager(config_dir)
        
        # 修改配置
        config_manager1.update_main_config(debug_mode=True, log_level="DEBUG")
        
        # 添加自定义功能
        custom_feature = FeatureConfig(
            name="custom_feature",
            enabled=True,
            description="自定义功能",
            rollout_percentage=75.0
        )
        config_manager1.add_feature_config(custom_feature)
        
        # 设置用户配置
        config_manager1.set_user_config("theme", "dark")
        config_manager1.set_user_config("notifications", True)
        
        # 创建第二个配置管理器实例（应该加载保存的配置）
        config_manager2 = PATEOASConfigManager(config_dir)
        
        # 验证主配置
        assert config_manager2.main_config.debug_mode == True
        assert config_manager2.main_config.log_level == "DEBUG"
        
        # 验证功能配置
        assert "custom_feature" in config_manager2.feature_configs
        custom_feature_loaded = config_manager2.get_feature_config("custom_feature")
        assert custom_feature_loaded.rollout_percentage == 75.0
        assert custom_feature_loaded.description == "自定义功能"
        
        # 验证用户配置
        assert config_manager2.get_user_config("theme") == "dark"
        assert config_manager2.get_user_config("notifications") == True
        
        print("✅ 配置持久化测试通过")


def test_config_export_import():
    """测试配置导出导入"""
    print("🧪 测试配置导出导入...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir1 = Path(temp_dir) / "config1"
        config_dir2 = Path(temp_dir) / "config2"
        export_file = Path(temp_dir) / "exported_config.json"
        
        # 创建源配置管理器
        source_manager = PATEOASConfigManager(config_dir1)
        
        # 修改配置
        source_manager.update_main_config(
            debug_mode=True,
            log_level="DEBUG",
            state_cache_size=2000
        )
        
        # 添加自定义功能
        custom_feature = FeatureConfig(
            name="export_test_feature",
            enabled=True,
            description="导出测试功能",
            rollout_percentage=60.0,
            flag=FeatureFlag.EXPERIMENTAL
        )
        source_manager.add_feature_config(custom_feature)
        
        # 设置用户配置
        source_manager.set_user_config("export_test", "success")
        
        # 导出配置
        exported_config = source_manager.export_config(include_user_config=True)
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(exported_config, f, ensure_ascii=False, indent=2)
        
        # 创建目标配置管理器
        target_manager = PATEOASConfigManager(config_dir2)
        
        # 导入配置
        with open(export_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        success = target_manager.import_config(import_data, merge=False)
        assert success
        
        # 验证导入结果
        assert target_manager.main_config.debug_mode == True
        assert target_manager.main_config.log_level == "DEBUG"
        assert target_manager.main_config.state_cache_size == 2000
        
        # 验证功能配置
        imported_feature = target_manager.get_feature_config("export_test_feature")
        assert imported_feature is not None
        assert imported_feature.rollout_percentage == 60.0
        assert imported_feature.flag == FeatureFlag.EXPERIMENTAL
        
        # 验证用户配置
        assert target_manager.get_user_config("export_test") == "success"
        
        print("✅ 配置导出导入测试通过")


def test_global_config_functions():
    """测试全局配置函数"""
    print("🧪 测试全局配置函数...")
    
    # 测试全局配置管理器
    global_manager = get_pateoas_config_manager()
    assert global_manager is not None
    
    # 测试全局配置获取
    global_config = get_pateoas_config()
    assert global_config is not None
    assert isinstance(global_config, PATEOASConfig)
    
    # 测试全局功能检查
    # 这些是默认启用的功能
    assert is_feature_enabled("state_continuity")
    assert is_feature_enabled("memory_system")
    assert is_feature_enabled("adaptive_flow")
    
    print("✅ 全局配置函数测试通过")


def test_feature_rollout_status():
    """测试功能部署状态"""
    print("🧪 测试功能部署状态...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 获取部署状态
        rollout_status = config_manager.get_feature_rollout_status()
        
        # 验证状态结构
        assert isinstance(rollout_status, dict)
        assert len(rollout_status) > 0
        
        for feature_name, status in rollout_status.items():
            assert 'enabled' in status
            assert 'flag' in status
            assert 'rollout_percentage' in status
            assert 'deployment_stages' in status
            assert 'available_in_current_stage' in status
            assert 'enabled_for_current_user' in status
            
            assert isinstance(status['enabled'], bool)
            assert isinstance(status['rollout_percentage'], (int, float))
            assert isinstance(status['deployment_stages'], list)
        
        # 测试不同部署阶段的状态
        config_manager.set_deployment_stage(DeploymentStage.DEVELOPMENT)
        dev_status = config_manager.get_feature_rollout_status()
        
        config_manager.set_deployment_stage(DeploymentStage.PRODUCTION)
        prod_status = config_manager.get_feature_rollout_status()
        
        # 验证状态变化
        for feature_name in dev_status:
            if feature_name in prod_status:
                # 某些功能可能在不同阶段有不同的可用性
                dev_available = dev_status[feature_name]['available_in_current_stage']
                prod_available = prod_status[feature_name]['available_in_current_stage']
                print(f"  {feature_name}: 开发={dev_available}, 生产={prod_available}")
        
        print("✅ 功能部署状态测试通过")


def test_config_reset():
    """测试配置重置"""
    print("🧪 测试配置重置...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "pateoas_config"
        config_manager = PATEOASConfigManager(config_dir)
        
        # 修改配置
        config_manager.update_main_config(debug_mode=True, log_level="DEBUG")
        config_manager.set_user_config("test_key", "test_value")
        
        # 添加自定义功能
        custom_feature = FeatureConfig(name="reset_test_feature", enabled=True)
        config_manager.add_feature_config(custom_feature)
        
        # 验证修改生效
        assert config_manager.main_config.debug_mode == True
        assert config_manager.get_user_config("test_key") == "test_value"
        assert "reset_test_feature" in config_manager.feature_configs
        
        # 重置配置
        config_manager.reset_to_defaults()
        
        # 验证重置结果
        assert config_manager.main_config.debug_mode == False  # 默认值
        assert config_manager.get_user_config("test_key") is None
        assert "reset_test_feature" not in config_manager.feature_configs
        
        # 验证默认功能仍然存在
        assert "state_continuity" in config_manager.feature_configs
        assert "memory_system" in config_manager.feature_configs
        
        print("✅ 配置重置测试通过")


def run_comprehensive_config_test():
    """运行综合配置管理测试"""
    print("🚀 开始PATEOAS配置管理综合测试")
    print("=" * 60)
    
    try:
        # 基础功能测试
        test_config_manager_initialization()
        test_feature_flag_management()
        test_deployment_stage_management()
        test_gradual_rollout()
        
        # 高级功能测试
        test_config_validation()
        test_config_persistence()
        test_config_export_import()
        
        # 全局功能测试
        test_global_config_functions()
        test_feature_rollout_status()
        test_config_reset()
        
        print("\n" + "=" * 60)
        print("🎉 所有配置管理测试通过！")
        print("\n📊 测试总结:")
        print("  ✅ 配置管理器初始化")
        print("  ✅ 功能开关管理")
        print("  ✅ 部署阶段管理")
        print("  ✅ 渐进式部署")
        print("  ✅ 配置验证")
        print("  ✅ 配置持久化")
        print("  ✅ 配置导出导入")
        print("  ✅ 全局配置函数")
        print("  ✅ 功能部署状态")
        print("  ✅ 配置重置")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_config_test()
    exit(0 if success else 1)