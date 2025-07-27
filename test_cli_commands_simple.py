"""
简化的PATEOAS CLI命令测试（不依赖click）
"""

import sys
import os
from aceflow.pateoas.cli_commands import PATEOASCLIManager


def test_cli_manager_basic():
    """测试CLI管理器基本功能"""
    print("🧪 测试CLI管理器基本功能")
    
    try:
        # 测试CLI管理器初始化
        manager = PATEOASCLIManager("test_cli_project")
        print(f"  ✓ CLI管理器初始化成功 (项目ID: {manager.project_id})")
        
        # 测试组件延迟初始化
        engine = manager.engine
        print("  ✓ 引擎组件初始化成功")
        
        state_manager = manager.state_manager
        print("  ✓ 状态管理器组件初始化成功")
        
        memory_system = manager.memory_system
        print("  ✓ 记忆系统组件初始化成功")
        
        performance_monitor = manager.performance_monitor
        print("  ✓ 性能监控器组件初始化成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI管理器测试失败: {e}")
        return False


def test_status_functionality():
    """测试状态功能"""
    print("\n📊 测试状态功能")
    
    try:
        manager = PATEOASCLIManager("status_test")
        
        # 获取系统状态
        current_state = manager.state_manager.get_current_state_optimized()
        print("  ✓ 获取当前状态成功")
        
        # 获取性能统计
        performance_stats = manager.performance_monitor.get_performance_summary()
        print("  ✓ 获取性能统计成功")
        
        # 获取记忆统计
        memory_stats = manager.memory_system.get_performance_report()
        print("  ✓ 获取记忆统计成功")
        
        # 验证状态数据结构
        assert 'workflow_state' in current_state
        assert 'current_metrics' in performance_stats
        assert 'performance_stats' in memory_stats
        
        print("  ✓ 状态数据结构验证通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 状态功能测试失败: {e}")
        return False


def test_memory_functionality():
    """测试记忆功能"""
    print("\n🧠 测试记忆功能")
    
    try:
        manager = PATEOASCLIManager("memory_test")
        
        # 添加测试记忆
        memory_id = manager.memory_system.add_memory_optimized(
            "CLI测试记忆内容",
            "learning",
            0.8,
            ["cli", "test", "memory"]
        )
        print(f"  ✓ 添加记忆成功 (ID: {memory_id[:20]}...)")
        
        # 搜索记忆
        results = manager.memory_system.search_memories_optimized(
            "CLI测试", limit=5
        )
        print(f"  ✓ 搜索记忆成功 (找到 {len(results)} 个结果)")
        
        # 获取记忆统计
        stats = manager.memory_system.get_performance_report()
        print(f"  ✓ 获取记忆统计成功 (总向量: {stats['index_stats']['total_vectors']})")
        
        # 优化记忆
        manager.memory_system.optimize_indices()
        print("  ✓ 记忆优化成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 记忆功能测试失败: {e}")
        return False


def test_performance_functionality():
    """测试性能功能"""
    print("\n📈 测试性能功能")
    
    try:
        manager = PATEOASCLIManager("performance_test")
        
        # 获取性能报告
        report = manager.performance_monitor.generate_performance_report()
        print("  ✓ 生成性能报告成功")
        
        # 验证报告结构
        assert 'report_timestamp' in report
        assert 'summary' in report
        assert 'recommendations' in report
        
        print("  ✓ 性能报告结构验证通过")
        
        # 运行基准测试
        benchmark = manager.memory_system.benchmark_performance(10)
        print(f"  ✓ 基准测试成功 (性能等级: {benchmark['performance_grade']})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 性能功能测试失败: {e}")
        return False


def test_recovery_functionality():
    """测试恢复功能"""
    print("\n🔄 测试恢复功能")
    
    try:
        manager = PATEOASCLIManager("recovery_test")
        
        # 获取恢复统计
        stats = manager.engine.recovery_strategy.get_recovery_statistics()
        print("  ✓ 获取恢复统计成功")
        
        # 测试恢复策略
        test_error = TimeoutError("Test timeout error")
        context = {
            'user_input': 'CLI测试',
            'system_state': {'test': True}
        }
        
        result = manager.engine.recovery_strategy.analyze_and_recover(
            test_error, context, 'cli_test'
        )
        
        print(f"  ✓ 恢复策略测试成功 (策略: {result['recommended_strategy'].strategy.value})")
        
        # 验证恢复结果结构
        assert 'error_pattern' in result
        assert 'recommended_strategy' in result
        assert 'recovery_type' in result
        
        print("  ✓ 恢复结果结构验证通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 恢复功能测试失败: {e}")
        return False


def test_config_functionality():
    """测试配置功能"""
    print("\n⚙️ 测试配置功能")
    
    try:
        manager = PATEOASCLIManager("config_test")
        
        # 获取配置
        config = manager.config
        print("  ✓ 获取配置成功")
        
        # 验证配置属性
        assert hasattr(config, 'memory_storage_path')
        assert hasattr(config, 'state_storage_path')
        
        print("  ✓ 配置属性验证通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置功能测试失败: {e}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n🔗 测试集成功能")
    
    try:
        manager = PATEOASCLIManager("integration_test")
        
        # 测试完整的工作流
        # 1. 添加记忆
        memory_id = manager.memory_system.add_memory_optimized(
            "集成测试记忆", "learning", 0.9, ["integration", "test"]
        )
        
        # 2. 处理请求
        result = manager.engine.process_with_state_awareness(
            "集成测试请求",
            {'test': True}
        )
        
        # 3. 获取状态
        state = manager.state_manager.get_current_state_optimized()
        
        # 4. 获取性能统计
        perf_stats = manager.performance_monitor.get_performance_summary()
        
        print("  ✓ 完整工作流测试成功")
        print(f"  - 记忆ID: {memory_id[:20]}...")
        print(f"  - 处理置信度: {result['confidence']:.2f}")
        print(f"  - 系统健康: {perf_stats['system_health']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 集成功能测试失败: {e}")
        return False


def test_cli_commands_structure():
    """测试CLI命令结构"""
    print("\n🏗️ 测试CLI命令结构")
    
    try:
        from aceflow.pateoas.cli_commands import pateoas_cli
        
        # 验证CLI组存在
        assert pateoas_cli is not None
        print("  ✓ CLI组定义存在")
        
        # 验证CLI组是click组
        assert hasattr(pateoas_cli, 'commands')
        print("  ✓ CLI组结构正确")
        
        # 验证主要命令存在
        expected_commands = ['status', 'memory', 'performance', 'recovery', 'config']
        for cmd in expected_commands:
            assert cmd in pateoas_cli.commands
            print(f"  ✓ {cmd} 命令定义存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI命令结构测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行所有测试
    tests = [
        test_cli_manager_basic,
        test_status_functionality,
        test_memory_functionality,
        test_performance_functionality,
        test_recovery_functionality,
        test_config_functionality,
        test_integration,
        test_cli_commands_structure
    ]
    
    success_count = 0
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 失败: {e}")
    
    if success_count == len(tests):
        print(f"\n✅ 任务9.1 - PATEOAS CLI命令 测试通过 ({success_count}/{len(tests)})")
        print("🎯 功能验证:")
        print("  ✓ pateoas-status command for state visibility")
        print("  ✓ pateoas-memory command for memory management")
        print("  ✓ pateoas-performance command for performance monitoring")
        print("  ✓ pateoas-recovery command for recovery management")
        print("  ✓ pateoas-config command for configuration")
        print("  ✓ CLI manager and component integration")
        print("  ✓ Complete workflow testing")
        print("  ✓ CLI command structure validation")
    else:
        print(f"\n❌ 任务9.1 测试失败 ({success_count}/{len(tests)} 通过)")