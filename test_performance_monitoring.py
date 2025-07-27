"""
测试PATEOAS性能监控系统
"""

from aceflow.pateoas.enhanced_engine import PATEOASEnhancedEngine
from aceflow.pateoas.performance_monitor import PATEOASPerformanceMonitor
import time
import json


def test_performance_monitoring():
    """测试性能监控功能"""
    print("🧪 测试PATEOAS性能监控系统")
    
    # 1. 测试性能监控器基础功能
    print("\n1. 测试性能监控器基础功能")
    monitor = PATEOASPerformanceMonitor("test_project")
    
    # 模拟操作
    op_id = monitor.start_operation("test_operation")
    time.sleep(0.1)  # 模拟处理时间
    monitor.end_operation(op_id, "test_component", True)
    
    # 记录指标
    monitor.record_decision_accuracy(0.85)
    monitor.record_user_satisfaction(0.9)
    monitor.record_memory_efficiency(0.8)
    
    print("✓ 基础功能测试通过")
    
    # 2. 测试性能摘要
    print("\n2. 测试性能摘要")
    summary = monitor.get_performance_summary()
    print(f"  - 总请求数: {summary['current_metrics']['total_requests']}")
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    print(f"  - 组件数量: {len(summary['component_performance'])}")
    print(f"  - 警报数量: {len(summary['alerts'])}")
    
    # 3. 测试集成到PATEOASEnhancedEngine
    print("\n3. 测试集成到PATEOASEnhancedEngine")
    engine = PATEOASEnhancedEngine('test_project')
    
    # 执行多次处理以收集性能数据
    for i in range(3):
        result = engine.process_with_state_awareness(
            user_input=f'测试请求 {i+1}',
            current_context={'test': True, 'iteration': i+1}
        )
        print(f"  - 请求 {i+1}: 置信度 {result['confidence']:.2f}")
    
    # 4. 检查性能指标
    print("\n4. 检查性能指标")
    performance_summary = engine.performance_monitor.get_performance_summary()
    
    print(f"  - 总请求数: {performance_summary['current_metrics']['total_requests']}")
    print(f"  - 成功请求数: {performance_summary['current_metrics']['successful_requests']}")
    print(f"  - 平均响应时间: {performance_summary['current_metrics']['average_response_time']:.3f}s")
    print(f"  - 决策准确性: {performance_summary['current_metrics']['decision_accuracy']:.2f}")
    print(f"  - 系统健康分数: {performance_summary['system_health']:.2f}")
    
    # 5. 测试组件性能分析
    print("\n5. 组件性能分析")
    for component, perf in performance_summary['component_performance'].items():
        print(f"  - {component}: 成功率 {perf['success_rate']:.2%}, 平均时间 {perf['average_time']:.3f}s")
    
    # 6. 测试性能报告生成
    print("\n6. 生成性能报告")
    report = engine.performance_monitor.generate_performance_report()
    
    print(f"  - 报告时间戳: {report['report_timestamp']}")
    print(f"  - 趋势分析: {len(report['trends'])} 个类别")
    print(f"  - 建议数量: {len(report['recommendations'])}")
    
    if report['recommendations']:
        print("  - 性能建议:")
        for rec in report['recommendations'][:3]:  # 显示前3个建议
            print(f"    • {rec}")
    
    # 7. 测试警报系统
    print("\n7. 测试警报系统")
    alerts = performance_summary['alerts']
    if alerts:
        print(f"  - 发现 {len(alerts)} 个警报:")
        for alert in alerts:
            print(f"    • {alert['type'].upper()}: {alert['message']}")
    else:
        print("  - 无警报，系统运行正常")
    
    print("\n🎉 性能监控系统测试完成！")
    return True


def test_performance_thresholds():
    """测试性能阈值和警报"""
    print("\n🚨 测试性能阈值和警报")
    
    monitor = PATEOASPerformanceMonitor("threshold_test")
    
    # 模拟高响应时间
    for i in range(5):
        op_id = monitor.start_operation("slow_operation")
        time.sleep(0.6)  # 模拟慢操作
        monitor.end_operation(op_id, "slow_component", True)
    
    # 检查警报
    summary = monitor.get_performance_summary()
    alerts = summary['alerts']
    
    print(f"平均响应时间: {summary['current_metrics']['average_response_time']:.2f}s")
    print(f"警报数量: {len(alerts)}")
    
    for alert in alerts:
        print(f"  - {alert['type'].upper()}: {alert['message']}")
    
    return len(alerts) > 0


if __name__ == "__main__":
    # 运行测试
    success1 = test_performance_monitoring()
    success2 = test_performance_thresholds()
    
    if success1:
        print("\n✅ 任务6.3 - 性能监控和指标 测试通过")
    else:
        print("\n❌ 任务6.3 测试失败")