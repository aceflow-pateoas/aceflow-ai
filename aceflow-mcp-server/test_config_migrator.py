#!/usr/bin/env python3
"""
配置迁移器测试
Configuration Migrator Test
"""
import sys
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入生产代码
from aceflow_mcp_server.config.config_migrator import (
    ConfigurationMigrator, MigrationStrategy, MigrationStatus,
    migrate_aceflow_config, migrate_multiple_aceflow_configs, auto_discover_and_migrate
)
from aceflow_mcp_server.config.config_detector import ConfigurationDetector, ConfigType

def create_test_configs(temp_dir: Path) -> Dict[str, Path]:
    """创建测试配置文件"""
    config_files = {}
    
    # 1. 基础AceFlow配置
    basic_config = {
        "mcpServers": {
            "aceflow-server": {
                "command": "uvx",
                "args": ["aceflow-mcp-server@latest"],
                "env": {
                    "ACEFLOW_MODE": "basic",
                    "ENABLE_CACHING": "true"
                }
            }
        }
    }
    
    basic_file = temp_dir / "aceflow-basic.json"
    basic_file.write_text(json.dumps(basic_config, indent=2))
    config_files["basic"] = basic_file
    
    # 2. 增强AceFlow配置
    enhanced_config = {
        "mcpServers": {
            "aceflow-enhanced-server": {
                "command": "uvx",
                "args": ["aceflow-enhanced-mcp-server@latest"],
                "env": {
                    "ENABLE_COLLABORATION": "true",
                    "ENABLE_INTELLIGENCE": "true",
                    "ENABLE_MONITORING": "true"
                }
            }
        },
        "version": "1.5"
    }
    
    enhanced_file = temp_dir / "aceflow-enhanced.json"
    enhanced_file.write_text(json.dumps(enhanced_config, indent=2))
    config_files["enhanced"] = enhanced_file
    
    # 3. 已有的统一配置（用于测试合并）
    existing_unified = {
        "version": "1.8",
        "unified_mode": True,
        "mcpServers": {
            "existing-server": {
                "command": "python",
                "args": ["-m", "existing_server"]
            }
        },
        "module_config": {
            "core": {"enabled": True}
        }
    }
    
    existing_file = temp_dir / "existing-unified.json"
    existing_file.write_text(json.dumps(existing_unified, indent=2))
    config_files["existing_unified"] = existing_file
    
    return config_files

def test_basic_migration():
    """测试基础配置迁移"""
    print("🧪 Testing Basic Configuration Migration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        migrator = ConfigurationMigrator()
        
        # 迁移基础配置
        result = migrator.migrate_configuration(
            str(config_files["basic"]),
            strategy=MigrationStrategy.BACKUP_AND_REPLACE
        )
        
        # 验证迁移结果
        assert result.status == MigrationStatus.COMPLETED
        assert result.source_type == ConfigType.ACEFLOW_BASIC
        assert result.backup_file is not None
        assert Path(result.backup_file).exists()
        assert Path(result.target_file).exists()
        
        # 验证目标配置内容
        with open(result.target_file, 'r') as f:
            unified_config = json.load(f)
        
        assert unified_config["version"] == "2.0"
        assert unified_config["unified_mode"] == True
        assert unified_config["module_config"]["core"]["enabled"] == True
        assert unified_config["feature_flags"]["caching"] == True  # 从环境变量转换
        
        # 验证变更记录
        assert len(result.changes_made) > 0
        assert any("backup" in change.lower() for change in result.changes_made)
        assert any("unified config" in change.lower() for change in result.changes_made)
        
        print("  ✅ Basic configuration migration test passed")

def test_enhanced_migration():
    """测试增强配置迁移"""
    print("🧪 Testing Enhanced Configuration Migration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        migrator = ConfigurationMigrator()
        
        # 迁移增强配置
        result = migrator.migrate_configuration(
            str(config_files["enhanced"]),
            strategy=MigrationStrategy.CREATE_NEW
        )
        
        # 验证迁移结果
        assert result.status == MigrationStatus.COMPLETED
        assert result.source_type == ConfigType.ACEFLOW_ENHANCED
        assert result.backup_file is None  # CREATE_NEW策略不创建备份
        assert Path(result.target_file).exists()
        
        # 验证目标配置内容
        with open(result.target_file, 'r') as f:
            unified_config = json.load(f)
        
        assert unified_config["module_config"]["core"]["enabled"] == True
        assert unified_config["module_config"]["collaboration"]["enabled"] == True
        assert unified_config["module_config"]["intelligence"]["enabled"] == True
        assert unified_config["feature_flags"]["intelligent_recommendations"] == True
        
        print("  ✅ Enhanced configuration migration test passed")

def test_multiple_config_migration():
    """测试多配置文件迁移"""
    print("🧪 Testing Multiple Configuration Migration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        migrator = ConfigurationMigrator()
        
        # 迁移多个配置文件并合并
        source_files = [str(config_files["basic"]), str(config_files["enhanced"])]
        results = migrator.migrate_multiple_configurations(
            source_files,
            strategy=MigrationStrategy.BACKUP_AND_REPLACE,
            merge_into_single=True
        )
        
        # 应该只有一个结果（合并后的）
        assert len(results) == 1
        result = results[0]
        
        assert result.status == MigrationStatus.COMPLETED
        assert result.strategy == MigrationStrategy.MERGE
        assert Path(result.target_file).exists()
        
        # 验证合并后的配置
        with open(result.target_file, 'r') as f:
            unified_config = json.load(f)
        
        # 应该包含两个源配置的服务器
        mcp_servers = unified_config["mcpServers"]
        assert len(mcp_servers) >= 2  # 至少包含两个服务器配置
        
        # 应该启用所有模块（因为包含增强配置）
        assert unified_config["module_config"]["collaboration"]["enabled"] == True
        assert unified_config["module_config"]["intelligence"]["enabled"] == True
        
        # 验证迁移信息
        migration_info = unified_config["migration_info"]
        assert len(migration_info["source_configs"]) == 2
        
        print("  ✅ Multiple configuration migration test passed")

def test_migration_validation():
    """测试迁移验证功能"""
    print("🧪 Testing Migration Validation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        migrator = ConfigurationMigrator()
        
        # 迁移配置
        result = migrator.migrate_configuration(
            str(config_files["basic"]),
            strategy=MigrationStrategy.CREATE_NEW
        )
        
        # 验证迁移结果包含验证信息
        assert hasattr(result, 'validation_passed')
        assert hasattr(result, 'validation_errors')
        
        # 对于有效的迁移，验证应该通过
        if result.status == MigrationStatus.COMPLETED:
            assert result.validation_passed == True
            assert len(result.validation_errors) == 0
        
        print("  ✅ Migration validation test passed")

def test_migration_rollback():
    """测试迁移回滚功能"""
    print("🧪 Testing Migration Rollback...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        # 保存原始内容
        original_content = config_files["basic"].read_text()
        
        migrator = ConfigurationMigrator()
        
        # 执行迁移
        result = migrator.migrate_configuration(
            str(config_files["basic"]),
            strategy=MigrationStrategy.BACKUP_AND_REPLACE
        )
        
        assert result.status == MigrationStatus.COMPLETED
        migration_id = result.migration_id
        
        # 验证目标文件存在
        assert Path(result.target_file).exists()
        
        # 执行回滚
        rollback_success = migrator.rollback_migration(migration_id)
        assert rollback_success == True
        
        # 验证回滚结果
        assert result.status == MigrationStatus.ROLLED_BACK
        
        # 验证原始文件已恢复（如果有备份的话）
        if result.backup_file:
            restored_content = config_files["basic"].read_text()
            assert restored_content == original_content
        
        print("  ✅ Migration rollback test passed")

def test_migration_report():
    """测试迁移报告生成"""
    print("🧪 Testing Migration Report Generation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        migrator = ConfigurationMigrator()
        
        # 执行多个迁移
        migrator.migrate_configuration(str(config_files["basic"]))
        migrator.migrate_configuration(str(config_files["enhanced"]))
        
        # 生成报告
        report = migrator.get_migration_report()
        
        # 验证报告结构
        assert "summary" in report
        assert "total_migrations" in report
        assert "completed_migrations" in report
        assert "failed_migrations" in report
        assert "success_rate" in report
        assert "migrations" in report
        
        # 验证统计信息
        assert report["total_migrations"] == 2
        assert report["success_rate"] >= 0.0
        assert len(report["migrations"]) == 2
        
        # 验证迁移详情
        for migration in report["migrations"]:
            assert "migration_id" in migration
            assert "source_file" in migration
            assert "target_file" in migration
            assert "status" in migration
            assert "validation_passed" in migration
        
        print("  ✅ Migration report generation test passed")

def test_convenience_functions():
    """测试便利函数"""
    print("🧪 Testing Convenience Functions...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_files = create_test_configs(temp_path)
        
        # 测试单个配置迁移便利函数
        result = migrate_aceflow_config(
            str(config_files["basic"]),
            strategy=MigrationStrategy.CREATE_NEW
        )
        
        assert result.status == MigrationStatus.COMPLETED
        print("  ✅ migrate_aceflow_config test passed")
        
        # 测试多配置迁移便利函数
        source_files = [str(config_files["basic"]), str(config_files["enhanced"])]
        results = migrate_multiple_aceflow_configs(
            source_files,
            strategy=MigrationStrategy.CREATE_NEW,
            merge_into_single=True
        )
        
        assert len(results) == 1
        assert results[0].status == MigrationStatus.COMPLETED
        print("  ✅ migrate_multiple_aceflow_configs test passed")
        
        # 测试自动发现和迁移便利函数
        report = auto_discover_and_migrate(
            search_paths=[str(temp_path)],
            strategy=MigrationStrategy.CREATE_NEW
        )
        
        assert "auto_discovery" in report
        assert "total_configs_found" in report["auto_discovery"]
        print("  ✅ auto_discover_and_migrate test passed")

def test_error_handling():
    """测试错误处理"""
    print("🧪 Testing Error Handling...")
    
    migrator = ConfigurationMigrator()
    
    # 测试不存在的文件
    result = migrator.migrate_configuration("nonexistent_file.json")
    assert result.status == MigrationStatus.FAILED
    assert len(result.errors) > 0
    
    print("  ✅ Error handling test passed")

def main():
    """运行所有测试"""
    print("🚀 Starting Configuration Migrator tests...\n")
    
    try:
        test_basic_migration()
        test_enhanced_migration()
        test_multiple_config_migration()
        test_migration_validation()
        test_migration_rollback()
        test_migration_report()
        test_convenience_functions()
        test_error_handling()
        
        print("\n🎉 All Configuration Migrator tests passed!")
        print("\n📊 Configuration Migrator Summary:")
        print("   ✅ Basic Configuration Migration - Working")
        print("   ✅ Enhanced Configuration Migration - Working")
        print("   ✅ Multiple Configuration Merging - Working")
        print("   ✅ Migration Validation - Working")
        print("   ✅ Migration Rollback - Working")
        print("   ✅ Migration Reporting - Working")
        print("   ✅ Convenience Functions - Working")
        print("   ✅ Error Handling - Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration migrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🏗️ Task 7.2 - Configuration Auto-Migration Implementation Complete!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)