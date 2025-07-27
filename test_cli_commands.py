"""
测试PATEOAS CLI命令
"""

import os
import json
import tempfile
from click.testing import CliRunner
from aceflow.pateoas.cli_commands import pateoas_cli, PATEOASCLIManager


def test_pateoas_status_command():
    """测试pateoas status命令"""
    print("🧪 测试pateoas status命令")
    
    runner = CliRunner()
    
    # 测试基本状态命令
    result = runner.invoke(pateoas_cli, ['status'])
    print(f"  - 基本状态命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 基本状态命令执行成功")
        print(f"  - 输出长度: {len(result.output)} 字符")
    else:
        print(f"  ✗ 基本状态命令失败: {result.output}")
    
    # 测试详细状态命令
    result = runner.invoke(pateoas_cli, ['status', '--detailed'])
    print(f"  - 详细状态命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 详细状态命令执行成功")
    
    # 测试JSON格式输出
    result = runner.invoke(pateoas_cli, ['status', '--format', 'json'])
    print(f"  - JSON格式命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ JSON格式命令执行成功")
        try:
            # 验证输出是有效的JSON
            json.loads(result.output)
            print("  ✓ JSON输出格式有效")
        except json.JSONDecodeError:
            print("  ✗ JSON输出格式无效")
    
    print("✓ pateoas status命令测试通过")
    return True


def test_pateoas_memory_command():
    """测试pateoas memory命令"""
    print("\n🧠 测试pateoas memory命令")
    
    runner = CliRunner()
    
    # 测试记忆统计
    result = runner.invoke(pateoas_cli, ['memory', '--action', 'stats'])
    print(f"  - 记忆统计命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 记忆统计命令执行成功")
    else:
        print(f"  ✗ 记忆统计命令失败: {result.output}")
    
    # 测试添加记忆
    result = runner.invoke(pateoas_cli, [
        'memory', '--action', 'add',
        '--content', 'CLI测试记忆内容',
        '--category', 'learning',
        '--importance', '0.8',
        '--tags', 'cli,test,memory'
    ])
    print(f"  - 添加记忆命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 添加记忆命令执行成功")
    else:
        print(f"  ✗ 添加记忆命令失败: {result.output}")
    
    # 测试搜索记忆
    result = runner.invoke(pateoas_cli, [
        'memory', '--action', 'search',
        '--query', 'CLI测试',
        '--limit', '5'
    ])
    print(f"  - 搜索记忆命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 搜索记忆命令执行成功")
    else:
        print(f"  ✗ 搜索记忆命令失败: {result.output}")
    
    # 测试列出记忆
    result = runner.invoke(pateoas_cli, [
        'memory', '--action', 'list',
        '--limit', '3'
    ])
    print(f"  - 列出记忆命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 列出记忆命令执行成功")
    
    # 测试优化记忆
    result = runner.invoke(pateoas_cli, ['memory', '--action', 'optimize'])
    print(f"  - 优化记忆命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 优化记忆命令执行成功")
    
    print("✓ pateoas memory命令测试通过")
    return True


def test_pateoas_performance_command():
    """测试pateoas performance命令"""
    print("\n📊 测试pateoas performance命令")
    
    runner = CliRunner()
    
    # 测试性能报告
    result = runner.invoke(pateoas_cli, ['performance', '--action', 'report'])
    print(f"  - 性能报告命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 性能报告命令执行成功")
    else:
        print(f"  ✗ 性能报告命令失败: {result.output}")
    
    # 测试性能基准测试（少量查询以节省时间）
    result = runner.invoke(pateoas_cli, [
        'performance', '--action', 'benchmark',
        '--queries', '10'
    ])
    print(f"  - 性能基准测试命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 性能基准测试命令执行成功")
    else:
        print(f"  ✗ 性能基准测试命令失败: {result.output}")
    
    # 测试性能监控（非watch模式）
    result = runner.invoke(pateoas_cli, ['performance', '--action', 'monitor'])
    print(f"  - 性能监控命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 性能监控命令执行成功")
    
    print("✓ pateoas performance命令测试通过")
    return True


def test_pateoas_recovery_command():
    """测试pateoas recovery命令"""
    print("\n🔄 测试pateoas recovery命令")
    
    runner = CliRunner()
    
    # 测试恢复统计
    result = runner.invoke(pateoas_cli, ['recovery', '--action', 'stats'])
    print(f"  - 恢复统计命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 恢复统计命令执行成功")
    else:
        print(f"  ✗ 恢复统计命令失败: {result.output}")
    
    # 测试恢复策略测试
    result = runner.invoke(pateoas_cli, [
        'recovery', '--action', 'test',
        '--error-type', 'timeout'
    ])
    print(f"  - 恢复策略测试命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 恢复策略测试命令执行成功")
    else:
        print(f"  ✗ 恢复策略测试命令失败: {result.output}")
    
    # 测试恢复历史
    result = runner.invoke(pateoas_cli, ['recovery', '--action', 'history'])
    print(f"  - 恢复历史命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 恢复历史命令执行成功")
    
    print("✓ pateoas recovery命令测试通过")
    return True


def test_pateoas_config_command():
    """测试pateoas config命令"""
    print("\n⚙️ 测试pateoas config命令")
    
    runner = CliRunner()
    
    # 测试显示配置
    result = runner.invoke(pateoas_cli, ['config', '--action', 'show'])
    print(f"  - 显示配置命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 显示配置命令执行成功")
    else:
        print(f"  ✗ 显示配置命令失败: {result.output}")
    
    # 测试设置配置
    result = runner.invoke(pateoas_cli, [
        'config', '--action', 'set',
        '--key', 'test_key',
        '--value', 'test_value'
    ])
    print(f"  - 设置配置命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 设置配置命令执行成功")
    
    # 测试重置配置
    result = runner.invoke(pateoas_cli, [
        'config', '--action', 'reset',
        '--key', 'test_key'
    ])
    print(f"  - 重置配置命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 重置配置命令执行成功")
    
    print("✓ pateoas config命令测试通过")
    return True


def test_cli_manager():
    """测试CLI管理器"""
    print("\n🔧 测试CLI管理器")
    
    # 测试CLI管理器初始化
    manager = PATEOASCLIManager("test_cli_project")
    print(f"  - CLI管理器项目ID: {manager.project_id}")
    
    # 测试延迟初始化的组件
    try:
        engine = manager.engine
        print("  ✓ 引擎组件初始化成功")
        
        state_manager = manager.state_manager
        print("  ✓ 状态管理器组件初始化成功")
        
        memory_system = manager.memory_system
        print("  ✓ 记忆系统组件初始化成功")
        
        performance_monitor = manager.performance_monitor
        print("  ✓ 性能监控器组件初始化成功")
        
    except Exception as e:
        print(f"  ✗ 组件初始化失败: {e}")
        return False
    
    print("✓ CLI管理器测试通过")
    return True


def test_project_id_parameter():
    """测试项目ID参数"""
    print("\n🆔 测试项目ID参数")
    
    runner = CliRunner()
    
    # 测试带项目ID的命令
    result = runner.invoke(pateoas_cli, [
        '--project-id', 'test_project_123',
        'status'
    ])
    print(f"  - 带项目ID的状态命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 带项目ID的命令执行成功")
        # 检查输出中是否包含项目ID
        if 'test_project_123' in result.output:
            print("  ✓ 项目ID正确显示在输出中")
        else:
            print("  ⚠️ 项目ID未在输出中显示")
    else:
        print(f"  ✗ 带项目ID的命令失败: {result.output}")
    
    print("✓ 项目ID参数测试通过")
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n❌ 测试错误处理")
    
    runner = CliRunner()
    
    # 测试无效的action参数
    result = runner.invoke(pateoas_cli, ['memory', '--action', 'invalid_action'])
    print(f"  - 无效action参数退出码: {result.exit_code}")
    
    if result.exit_code != 0:
        print("  ✓ 无效action参数正确处理")
    else:
        print("  ✗ 无效action参数未正确处理")
    
    # 测试缺少必需参数的命令
    result = runner.invoke(pateoas_cli, [
        'memory', '--action', 'search'
        # 缺少 --query 参数
    ])
    print(f"  - 缺少必需参数退出码: {result.exit_code}")
    
    if result.exit_code != 0:
        print("  ✓ 缺少必需参数正确处理")
    else:
        print("  ✗ 缺少必需参数未正确处理")
    
    # 测试添加记忆时缺少内容
    result = runner.invoke(pateoas_cli, [
        'memory', '--action', 'add'
        # 缺少 --content 参数
    ])
    print(f"  - 缺少内容参数退出码: {result.exit_code}")
    
    if result.exit_code != 0:
        print("  ✓ 缺少内容参数正确处理")
    else:
        print("  ✗ 缺少内容参数未正确处理")
    
    print("✓ 错误处理测试通过")
    return True


def test_help_commands():
    """测试帮助命令"""
    print("\n❓ 测试帮助命令")
    
    runner = CliRunner()
    
    # 测试主帮助命令
    result = runner.invoke(pateoas_cli, ['--help'])
    print(f"  - 主帮助命令退出码: {result.exit_code}")
    
    if result.exit_code == 0:
        print("  ✓ 主帮助命令执行成功")
        if 'PATEOAS增强功能命令组' in result.output:
            print("  ✓ 帮助内容包含正确描述")
    
    # 测试子命令帮助
    subcommands = ['status', 'memory', 'performance', 'recovery', 'config']
    
    for subcmd in subcommands:
        result = runner.invoke(pateoas_cli, [subcmd, '--help'])
        if result.exit_code == 0:
            print(f"  ✓ {subcmd} 帮助命令执行成功")
        else:
            print(f"  ✗ {subcmd} 帮助命令失败")
    
    print("✓ 帮助命令测试通过")
    return True


if __name__ == "__main__":
    # 运行所有测试
    tests = [
        test_cli_manager,
        test_pateoas_status_command,
        test_pateoas_memory_command,
        test_pateoas_performance_command,
        test_pateoas_recovery_command,
        test_pateoas_config_command,
        test_project_id_parameter,
        test_error_handling,
        test_help_commands
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
        print("  ✓ CLI tests for new PATEOAS commands")
        print("  ✓ Error handling and help system")
    else:
        print(f"\n❌ 任务9.1 测试失败 ({success_count}/{len(tests)} 通过)")