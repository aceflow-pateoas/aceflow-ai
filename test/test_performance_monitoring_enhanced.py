"""
测试PATEOAS性能监控和指标系统 - 任务6.3
"""

import time
import json
from datetime import datetime, timedelta
from aceflow.pateoas.enhanced_engine import PATEOASEnhancedEngine
from aceflow.pateoas.performance_monitor import PATEOASPerformanceMonitor, PerformanceMetric


def test_performance_monitor_initialization():
    """测试性能监控器初始化"""
    print("🧪 测试性能监控器初始化")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 验证初始化状态
    assert monitor.project_id == "test_project"
    assert monitor.current_metrics['total_requests'] == 0
    assert monitor.current_metrics['successful_requests'] == 0
    assert len(monitor.component_performance) == 0
    
    print("✓ 性能监控器初始化正常")
    return True


def test_operation_timing():
    """测试操作计时功能"""
    print("\n⏱️ 测试操作计时功能")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 测试操作计时
    op_id = monitor.start_operation("test_operation")
    time.sleep(0.1)  # 模拟操作耗时
    monitor.end_operation(op_id, "test_component", success=True)
    
    # 验证组件性能记录
    assert "test_component" in monitor.component_performance
    comp_perf = monitor.component_performance["test_component"]
    assert comp_perf.total_calls == 1
    assert comp_perf.successful_calls == 1
    assert comp_perf.average_time > 0.05  # 应该大于50ms
    
    print(f"  - 组件调用次数: {comp_perf.total_calls}")
    print(f"  - 成功调用次数: {comp_perf.successful_calls}")
    print(f"  - 平均执行时间: {comp_perf.average_time:.4f}s")
    print(f"  - 成功率: {comp_perf.success_rate:.2%}")
    
    print("✓ 操作计时功能正常")
    return True


def test_metrics_recording():
    """测试指标记录功能"""
    print("\n📊 测试指标记录功能")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 记录各种指标
    monitor.record_decision_accuracy(0.85)
    monitor.record_user_satisfaction(0.9)
    monitor.record_memory_efficiency(0.75)
    
    # 验证指标记录
    assert monitor.current_metrics['decision_accuracy'] == 0.85
    assert monitor.current_metrics['user_satisfaction'] == 0.9
    assert monitor.current_metrics['memory_efficiency'] == 0.75
    
    # 验证指标历史
    assert len(monitor.metrics_history) >= 3
    
    print(f"  - 决策准确性: {monitor.current_metrics['decision_accuracy']:.2%}")
    print(f"  - 用户满意度: {monitor.current_metrics['user_satisfaction']:.2%}")
    print(f"  - 记忆效率: {monitor.current_metrics['memory_efficiency']:.2%}")
    print(f"  - 指标历史记录数: {len(monitor.metrics_history)}")
    
    print("✓ 指标记录功能正常")
    return True


def test_performance_summary():
    """测试性能摘要生成"""
    print("\n📋 测试性能摘要生成")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 添加一些测试数据
    op_id = monitor.start_operation("test_op")
    time.sleep(0.05)
    monitor.end_operation(op_id, "test_component", True)
    
    monitor.record_decision_accuracy(0.88)
    monitor.record_user_satisfaction(0.92)
    
    # 生成性能摘要
    summary = monitor.get_performance_summary()
    
    # 验证摘要内容
    assert 'current_metrics' in summary
    assert 'component_performance' in summary
    assert 'system_health' in summary
    assert 'alerts' in summary
    assert 'timestamp' in summary
    
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    print(f"  - 组件数量: {len(summary['component_performance'])}")
    print(f"  - 警报数量: {len(summary['alerts'])}")
    
    print("✓ 性能摘要生成正常")
    return True


def test_alert_system():
    """测试警报系统"""
    print("\n🚨 测试警报系统")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 模拟高响应时间触发警报
    monitor.current_metrics['average_response_time'] = 3.0  # 超过警告阈值
    monitor.current_metrics['total_requests'] = 10
    monitor.current_metrics['successful_requests'] = 6  # 60%成功率，低于警告阈值
    
    alerts = monitor._check_alerts()
    
    # 验证警报生成
    assert len(alerts) > 0
    
    response_time_alerts = [a for a in alerts if a['metric'] == 'response_time']
    success_rate_alerts = [a for a in alerts if a['metric'] == 'success_rate']
    
    assert len(response_time_alerts) > 0
    assert len(success_rate_alerts) > 0
    
    print(f"  - 总警报数: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['type'].upper()}: {alert['message']}")
    
    print("✓ 警报系统正常")
    return True


def test_performance_trends():
    """测试性能趋势分析"""
    print("\n📈 测试性能趋势分析")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 添加一系列指标模拟趋势
    for i in range(20):
        value = 0.5 + (i * 0.02)  # 递增趋势
        monitor._record_metric(f"test_metric", value, "performance", "ratio")
        time.sleep(0.001)  # 小延迟确保时间戳不同
    
    # 分析趋势
    trends = monitor._analyze_performance_trends()
    
    # 验证趋势分析
    assert 'performance' in trends or 'status' in trends
    
    if 'performance' in trends:
        trend_info = trends['performance']
        print(f"  - 性能趋势: {trend_info['trend']}")
        print(f"  - 变化百分比: {trend_info['change_percentage']:.1f}%")
        print(f"  - 样本数量: {trend_info['sample_size']}")
    else:
        print(f"  - 趋势分析状态: {trends['status']}")
    
    print("✓ 性能趋势分析正常")
    return True


def test_performance_report_generation():
    """测试性能报告生成"""
    print("\n📄 测试性能报告生成")
    
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 添加测试数据
    op_id = monitor.start_operation("report_test")
    time.sleep(0.02)
    monitor.end_operation(op_id, "report_component", True)
    
    monitor.record_decision_accuracy(0.87)
    monitor.record_user_satisfaction(0.91)
    monitor.record_memory_efficiency(0.83)
    
    # 生成报告
    report = monitor.generate_performance_report()
    
    # 验证报告结构
    required_sections = [
        'report_timestamp', 'project_id', 'summary', 
        'trends', 'recommendations', 'component_analysis'
    ]
    
    for section in required_sections:
        assert section in report, f"报告缺少 {section} 部分"
    
    print(f"  - 项目ID: {report['project_id']}")
    print(f"  - 报告时间: {report['report_timestamp']}")
    print(f"  - 建议数量: {len(report['recommendations'])}")
    print(f"  - 组件分析数量: {len(report['component_analysis'])}")
    
    # 显示部分建议
    if report['recommendations']:
        print("  - 性能建议:")
        for i, rec in enumerate(report['recommendations'][:3], 1):
            print(f"    {i}. {rec}")
    
    print("✓ 性能报告生成正常")
    return True


def test_enhanced_engine_integration():
    """测试增强引擎中的性能监控集成"""
    print("\n🔗 测试增强引擎性能监控集成")
    
    engine = PATEOASEnhancedEngine("test_integration")
    
    # 验证性能监控器已初始化
    assert hasattr(engine, 'performance_monitor')
    assert engine.performance_monitor.project_id == "test_integration"
    
    # 测试处理请求时的性能监控
    result = engine.process_with_state_awareness(
        user_input="测试性能监控集成",
        current_context={'test': True}
    )
    
    # 验证性能指标已更新
    assert engine.performance_metrics['total_requests'] > 0
    assert engine.performance_metrics['successful_requests'] > 0
    
    # 获取性能摘要
    summary = engine.get_performance_summary()
    assert 'current_metrics' in summary
    assert 'system_health' in summary
    
    print(f"  - 总请求数: {engine.performance_metrics['total_requests']}")
    print(f"  - 成功请求数: {engine.performance_metrics['successful_requests']}")
    print(f"  - 平均响应时间: {engine.performance_metrics['average_response_time']:.4f}s")
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    
    print("✓ 增强引擎性能监控集成正常")
    return True


def test_user_satisfaction_calculation():
    """测试用户满意度计算"""
    print("\n😊 测试用户满意度计算")
    
    engine = PATEOASEnhancedEngine("test_satisfaction")
    
    # 测试不同质量的结果
    test_results = [
        {
            'confidence': 0.9,
            'alternative_actions': [{'action': 'alt1'}, {'action': 'alt2'}],
            'reasoning_chain': [{'step': 1}, {'step': 2}, {'step': 3}]
        },
        {
            'confidence': 0.5,
            'alternative_actions': [],
            'reasoning_chain': [{'step': 1}]
        }
    ]
    
    for i, result in enumerate(test_results, 1):
        satisfaction = engine._calculate_user_satisfaction(result)
        print(f"  - 结果{i}满意度: {satisfaction:.2f}")
        assert 0.0 <= satisfaction <= 1.0
    
    print("✓ 用户满意度计算正常")
    return True


def test_memory_efficiency_calculation():
    """测试记忆效率计算"""
    print("\n🧠 测试记忆效率计算")
    
    engine = PATEOASEnhancedEngine("test_memory_efficiency")
    
    # 创建测试记忆
    from aceflow.pateoas.models import MemoryFragment, MemoryCategory
    
    memories = [
        MemoryFragment(
            content="高重要性记忆",
            category=MemoryCategory.LEARNING,
            importance=0.9
        ),
        MemoryFragment(
            content="中等重要性记忆",
            category=MemoryCategory.DECISION,
            importance=0.6
        ),
        MemoryFragment(
            content="低重要性记忆",
            category=MemoryCategory.PATTERN,
            importance=0.3
        )
    ]
    
    efficiency = engine._calculate_memory_efficiency(memories, "测试查询")
    
    print(f"  - 记忆数量: {len(memories)}")
    print(f"  - 记忆效率: {efficiency:.2f}")
    
    assert 0.0 <= efficiency <= 1.0
    
    print("✓ 记忆效率计算正常")
    return True


def test_performance_persistence():
    """测试性能数据持久化"""
    print("\n💾 测试性能数据持久化")
    
    monitor = PATEOASPerformanceMonitor("test_persistence")
    
    # 添加测试数据
    monitor.record_decision_accuracy(0.85)
    monitor.record_user_satisfaction(0.9)
    
    # 强制保存
    monitor._save_metrics_history()
    
    # 创建新的监控器实例，验证数据加载
    monitor2 = PATEOASPerformanceMonitor("test_persistence")
    
    # 验证数据已加载
    assert monitor2.current_metrics['decision_accuracy'] == 0.85
    assert monitor2.current_metrics['user_satisfaction'] == 0.9
    
    print(f"  - 加载的决策准确性: {monitor2.current_metrics['decision_accuracy']:.2f}")
    print(f"  - 加载的用户满意度: {monitor2.current_metrics['user_satisfaction']:.2f}")
    print(f"  - 历史记录数量: {len(monitor2.metrics_history)}")
    
    print("✓ 性能数据持久化正常")
    return True


def test_component_performance_analysis():
    """测试组件性能分析"""
    print("\n🔧 测试组件性能分析")
    
    monitor = PATEOASPerformanceMonitor("test_component_analysis")
    
    # 模拟不同组件的性能数据
    components = [
        ("state_manager", 0.1, True),
        ("memory_system", 0.2, True),
        ("flow_controller", 0.15, True),
        ("decision_gates", 0.3, False),  # 一次失败
        ("decision_gates", 0.25, True),
    ]
    
    for comp_name, exec_time, success in components:
        op_id = monitor.start_operation(f"test_{comp_name}")
        time.sleep(exec_time / 10)  # 缩短实际等待时间
        monitor.end_operation(op_id, comp_name, success)
    
    # 分析组件性能
    analysis = monitor._analyze_component_performance()
    
    print(f"  - 分析的组件数量: {len(analysis)}")
    
    for comp_name, comp_analysis in analysis.items():
        print(f"  - {comp_name}:")
        print(f"    性能分数: {comp_analysis['performance_score']:.2f}")
        print(f"    可靠性: {comp_analysis['reliability']:.2%}")
        print(f"    状态: {comp_analysis['status']}")
    
    print("✓ 组件性能分析正常")
    return True


if __name__ == "__main__":
    # 运行所有测试
    tests = [
        test_performance_monitor_initialization,
        test_operation_timing,
        test_metrics_recording,
        test_performance_summary,
        test_alert_system,
        test_performance_trends,
        test_performance_report_generation,
        test_enhanced_engine_integration,
        test_user_satisfaction_calculation,
        test_memory_efficiency_calculation,
        test_performance_persistence,
        test_component_performance_analysis
    ]
    
    success_count = 0
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 失败: {e}")
    
    if success_count == len(tests):
        print(f"\n✅ 任务6.3 - 性能监控和指标 测试通过 ({success_count}/{len(tests)})")
        print("🎯 功能验证:")
        print("  ✓ 性能监控器初始化和配置")
        print("  ✓ 操作计时和组件性能跟踪")
        print("  ✓ 决策准确性和用户满意度指标")
        print("  ✓ 记忆效率和系统健康评估")
        print("  ✓ 实时警报和阈值监控")
        print("  ✓ 性能趋势分析和预测")
        print("  ✓ 综合性能报告生成")
        print("  ✓ 增强引擎集成和自动监控")
        print("  ✓ 数据持久化和历史记录")
        print("  ✓ 组件级性能分析和优化建议")
    else:
        print(f"\n❌ 任务6.3 测试失败 ({success_count}/{len(tests)} 通过)")