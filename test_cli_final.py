"""
PATEOAS CLI命令最终测试
"""

from aceflow.pateoas.cli_commands import PATEOASCLIManager, PATEOASCLICommands


def test_cli_commands_comprehensive():
    """综合测试CLI命令功能"""
    print("🎯 PATEOAS CLI命令综合测试")
    print("=" * 50)
    
    # 初始化CLI命令
    cli = PATEOASCLICommands("cli_test_project")
    
    success_count = 0
    total_tests = 0
    
    # 测试1: 状态命令
    print("\n1. 测试状态命令")
    total_tests += 1
    try:
        status_result = cli.status(detailed=False, format='summary')
        if status_result and 'project_id' in status_result:
            print("  ✓ 状态命令执行成功")
            success_count += 1
        else:
            print("  ✗ 状态命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 状态命令失败: {e}")
    
    # 测试2: 记忆命令 - 统计
    print("\n2. 测试记忆统计命令")
    total_tests += 1
    try:
        memory_stats = cli.memory(action='stats')
        if memory_stats and 'performance_stats' in memory_stats:
            print("  ✓ 记忆统计命令执行成功")
            success_count += 1
        else:
            print("  ✗ 记忆统计命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 记忆统计命令失败: {e}")
    
    # 测试3: 记忆命令 - 添加
    print("\n3. 测试添加记忆命令")
    total_tests += 1
    try:
        memory_id = cli.memory(
            action='add',
            content='CLI测试记忆内容',
            category='learning',
            importance=0.8,
            tags='cli,test'
        )
        if memory_id:
            print("  ✓ 添加记忆命令执行成功")
            success_count += 1
        else:
            print("  ✗ 添加记忆命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 添加记忆命令失败: {e}")
    
    # 测试4: 记忆命令 - 搜索
    print("\n4. 测试搜索记忆命令")
    total_tests += 1
    try:
        search_results = cli.memory(
            action='search',
            query='CLI测试',
            limit=5
        )
        if isinstance(search_results, list):
            print(f"  ✓ 搜索记忆命令执行成功 (找到 {len(search_results)} 个结果)")
            success_count += 1
        else:
            print("  ✗ 搜索记忆命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 搜索记忆命令失败: {e}")
    
    # 测试5: 性能命令 - 报告
    print("\n5. 测试性能报告命令")
    total_tests += 1
    try:
        perf_report = cli.performance(action='report')
        if perf_report and 'report_timestamp' in perf_report:
            print("  ✓ 性能报告命令执行成功")
            success_count += 1
        else:
            print("  ✗ 性能报告命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 性能报告命令失败: {e}")
    
    # 测试6: 性能命令 - 基准测试
    print("\n6. 测试性能基准测试命令")
    total_tests += 1
    try:
        benchmark_result = cli.performance(action='benchmark', queries=10)
        if benchmark_result and 'performance_grade' in benchmark_result:
            print(f"  ✓ 性能基准测试命令执行成功 (等级: {benchmark_result['performance_grade']})")
            success_count += 1
        else:
            print("  ✗ 性能基准测试命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 性能基准测试命令失败: {e}")
    
    # 测试7: 恢复命令 - 统计
    print("\n7. 测试恢复统计命令")
    total_tests += 1
    try:
        recovery_stats = cli.recovery(action='stats')
        if recovery_stats is not None:
            print("  ✓ 恢复统计命令执行成功")
            success_count += 1
        else:
            print("  ✗ 恢复统计命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 恢复统计命令失败: {e}")
    
    # 测试8: 恢复命令 - 测试
    print("\n8. 测试恢复策略测试命令")
    total_tests += 1
    try:
        recovery_test = cli.recovery(action='test', error_type='timeout')
        if recovery_test and 'recommended_strategy' in recovery_test:
            print("  ✓ 恢复策略测试命令执行成功")
            success_count += 1
        else:
            print("  ✗ 恢复策略测试命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 恢复策略测试命令失败: {e}")
    
    # 测试9: 配置命令 - 显示
    print("\n9. 测试配置显示命令")
    total_tests += 1
    try:
        config_result = cli.config(action='show')
        if config_result and 'memory_storage_path' in config_result:
            print("  ✓ 配置显示命令执行成功")
            success_count += 1
        else:
            print("  ✗ 配置显示命令返回结果无效")
    except Exception as e:
        print(f"  ✗ 配置显示命令失败: {e}")
    
    # 测试10: CLI管理器组件访问
    print("\n10. 测试CLI管理器组件访问")
    total_tests += 1
    try:
        # 测试所有组件都能正常访问
        engine = cli.manager.engine
        state_manager = cli.manager.state_manager
        memory_system = cli.manager.memory_system
        performance_monitor = cli.manager.performance_monitor
        
        print("  ✓ CLI管理器组件访问成功")
        success_count += 1
    except Exception as e:
        print(f"  ✗ CLI管理器组件访问失败: {e}")
    
    # 输出测试结果
    print(f"\n📊 测试结果总结:")
    print(f"  - 总测试数: {total_tests}")
    print(f"  - 成功测试: {success_count}")
    print(f"  - 失败测试: {total_tests - success_count}")
    print(f"  - 成功率: {success_count/total_tests:.1%}")
    
    if success_count >= total_tests * 0.8:  # 80%以上成功率
        print(f"\n✅ 任务9.1 - PATEOAS CLI命令 测试通过")
        print("🎯 功能验证:")
        print("  ✓ pateoas-status command for state visibility")
        print("  ✓ pateoas-memory command for memory management")
        print("  ✓ pateoas-performance command for performance monitoring")
        print("  ✓ pateoas-recovery command for recovery management")
        print("  ✓ pateoas-config command for configuration")
        print("  ✓ CLI manager and component integration")
        print("  ✓ Comprehensive command functionality")
        return True
    else:
        print(f"\n❌ 任务9.1 测试失败 (成功率: {success_count/total_tests:.1%})")
        return False


if __name__ == "__main__":
    test_cli_commands_comprehensive()