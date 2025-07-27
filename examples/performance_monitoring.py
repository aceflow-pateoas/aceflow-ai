"""
PATEOAS性能监控系统演示
展示任务6.3的完整功能
"""

import time
import json
from datetime import datetime
from aceflow.pateoas.enhanced_engine import PATEOASEnhancedEngine
from aceflow.pateoas.performance_monitor import PATEOASPerformanceMonitor


def demo_basic_performance_monitoring():
    """演示基础性能监控功能"""
    print("🎯 演示1: 基础性能监控功能")
    print("=" * 60)
    
    # 创建性能监控器
    monitor = PATEOASPerformanceMonitor("demo_project")
    
    print("📊 初始状态:")
    summary = monitor.get_performance_summary()
    print(f"  - 总请求数: {summary['current_metrics']['total_requests']}")
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    
    # 模拟一些操作
    print("\n🔄 模拟系统操作...")
    
    operations = [
        ("状态管理", "state_manager", 0.1),
        ("记忆检索", "memory_system", 0.2),
        ("决策处理", "flow_controller", 0.15),
        ("决策门评估", "decision_gates", 0.3)
    ]
    
    for desc, component, duration in operations:
        print(f"  执行 {desc}...")
        op_id = monitor.start_operation(f"demo_{component}")
        time.sleep(duration / 10)  # 缩短实际等待时间
        monitor.end_operation(op_id, component, True)
    
    # 记录质量指标
    monitor.record_decision_accuracy(0.88)
    monitor.record_user_satisfaction(0.92)
    monitor.record_memory_efficiency(0.85)
    
    print("\n📈 更新后的性能指标:")
    summary = monitor.get_performance_summary()
    print(f"  - 总请求数: {summary['current_metrics']['total_requests']}")
    print(f"  - 成功请求数: {summary['current_metrics']['successful_requests']}")
    print(f"  - 平均响应时间: {summary['current_metrics']['average_response_time']:.4f}s")
    print(f"  - 决策准确性: {summary['current_metrics']['decision_accuracy']:.2%}")
    print(f"  - 用户满意度: {summary['current_metrics']['user_satisfaction']:.2%}")
    print(f"  - 记忆效率: {summary['current_metrics']['memory_efficiency']:.2%}")
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    
    print("\n🔧 组件性能分析:")
    for comp_name, comp_perf in summary['component_performance'].items():
        print(f"  - {comp_name}:")
        print(f"    成功率: {comp_perf['success_rate']:.2%}")
        print(f"    平均时间: {comp_perf['average_time']:.4f}s")
        print(f"    调用次数: {comp_perf['total_calls']}")


def demo_alert_system():
    """演示警报系统"""
    print("\n\n🚨 演示2: 警报系统")
    print("=" * 60)
    
    monitor = PATEOASPerformanceMonitor("alert_demo")
    
    # 模拟正常状态
    print("📊 正常状态 - 无警报:")
    monitor.current_metrics.update({
        'average_response_time': 0.5,
        'total_requests': 100,
        'successful_requests': 95
    })
    
    alerts = monitor._check_alerts()
    print(f"  警报数量: {len(alerts)}")
    
    # 模拟问题状态
    print("\n⚠️ 问题状态 - 触发警报:")
    monitor.current_metrics.update({
        'average_response_time': 3.5,  # 超过关键阈值
        'total_requests': 100,
        'successful_requests': 55  # 低于关键阈值
    })
    
    alerts = monitor._check_alerts()
    print(f"  警报数量: {len(alerts)}")
    
    for alert in alerts:
        icon = "🔴" if alert['type'] == 'critical' else "🟡"
        print(f"  {icon} {alert['type'].upper()}: {alert['message']}")


def demo_performance_trends():
    """演示性能趋势分析"""
    print("\n\n📈 演示3: 性能趋势分析")
    print("=" * 60)
    
    monitor = PATEOASPerformanceMonitor("trend_demo")
    
    # 模拟递增趋势
    print("📊 生成递增性能趋势...")
    for i in range(15):
        value = 0.6 + (i * 0.02)  # 从0.6递增到0.88
        monitor._record_metric("response_quality", value, "performance", "ratio")
        time.sleep(0.001)
    
    # 模拟递减趋势
    print("📊 生成递减性能趋势...")
    for i in range(10):
        value = 0.9 - (i * 0.03)  # 从0.9递减到0.63
        monitor._record_metric("system_load", value, "resource", "ratio")
        time.sleep(0.001)
    
    # 分析趋势
    trends = monitor._analyze_performance_trends()
    
    print("\n📈 趋势分析结果:")
    for category, trend_info in trends.items():
        if isinstance(trend_info, dict):
            print(f"  - {category}:")
            print(f"    趋势: {trend_info['trend']}")
            print(f"    变化: {trend_info['change_percentage']:+.1f}%")
            print(f"    样本数: {trend_info['sample_size']}")


def demo_performance_report():
    """演示性能报告生成"""
    print("\n\n📄 演示4: 性能报告生成")
    print("=" * 60)
    
    monitor = PATEOASPerformanceMonitor("report_demo")
    
    # 添加一些测试数据
    print("📊 生成测试数据...")
    
    # 模拟组件操作
    components = ["state_manager", "memory_system", "flow_controller"]
    for comp in components:
        for _ in range(3):
            op_id = monitor.start_operation(f"demo_{comp}")
            time.sleep(0.01)
            monitor.end_operation(op_id, comp, True)
    
    # 记录质量指标
    monitor.record_decision_accuracy(0.87)
    monitor.record_user_satisfaction(0.91)
    monitor.record_memory_efficiency(0.83)
    
    # 生成报告
    print("\n📋 生成性能报告...")
    report = monitor.generate_performance_report()
    
    print(f"\n📊 报告摘要:")
    print(f"  - 项目ID: {report['project_id']}")
    print(f"  - 报告时间: {report['report_timestamp']}")
    print(f"  - 系统健康分数: {report['summary']['system_health']:.2f}")
    
    print(f"\n🔧 组件分析:")
    for comp_name, analysis in report['component_analysis'].items():
        print(f"  - {comp_name}:")
        print(f"    性能分数: {analysis['performance_score']:.2f}")
        print(f"    状态: {analysis['status']}")
        print(f"    使用频率: {analysis['usage_frequency']}")
    
    print(f"\n💡 优化建议:")
    for i, recommendation in enumerate(report['recommendations'][:3], 1):
        print(f"  {i}. {recommendation}")
    
    if not report['recommendations']:
        print("  当前系统性能良好，暂无优化建议")


def demo_enhanced_engine_integration():
    """演示增强引擎中的性能监控集成"""
    print("\n\n🔗 演示5: 增强引擎性能监控集成")
    print("=" * 60)
    
    engine = PATEOASEnhancedEngine("integration_demo")
    
    print("🚀 处理用户请求并监控性能...")
    
    # 模拟多个用户请求
    test_inputs = [
        "我想开始一个新的Web项目",
        "如何优化数据库查询性能？",
        "项目进度如何？需要调整计划吗？",
        "遇到了一个技术难题，需要帮助"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n📝 处理请求 {i}: {user_input[:20]}...")
        
        start_time = time.time()
        result = engine.process_with_state_awareness(
            user_input=user_input,
            current_context={'demo': True, 'request_id': i}
        )
        processing_time = time.time() - start_time
        
        print(f"  ⏱️ 处理时间: {processing_time:.4f}s")
        print(f"  🎯 置信度: {result.get('confidence', 0):.2f}")
        print(f"  🔄 替代方案数: {len(result.get('alternative_actions', []))}")
    
    # 获取性能摘要
    print(f"\n📊 整体性能摘要:")
    summary = engine.get_performance_summary()
    
    print(f"  - 总请求数: {summary['current_metrics']['total_requests']}")
    print(f"  - 成功率: {summary['current_metrics']['successful_requests'] / max(1, summary['current_metrics']['total_requests']):.2%}")
    print(f"  - 平均响应时间: {summary['current_metrics']['average_response_time']:.4f}s")
    print(f"  - 系统健康分数: {summary['system_health']:.2f}")
    
    # 显示组件性能
    print(f"\n🔧 组件性能排行:")
    component_perf = summary['component_performance']
    sorted_components = sorted(
        component_perf.items(),
        key=lambda x: x[1]['average_time']
    )
    
    for comp_name, perf in sorted_components:
        print(f"  - {comp_name}: {perf['average_time']:.4f}s (成功率: {perf['success_rate']:.2%})")


def demo_real_time_monitoring():
    """演示实时监控功能"""
    print("\n\n⏱️ 演示6: 实时监控功能")
    print("=" * 60)
    
    engine = PATEOASEnhancedEngine("realtime_demo")
    
    print("🔄 实时监控系统运行状态...")
    
    # 模拟持续的系统活动
    for round_num in range(3):
        print(f"\n📊 监控轮次 {round_num + 1}:")
        
        # 处理一些请求
        for i in range(2):
            result = engine.process_with_state_awareness(
                user_input=f"实时监控测试请求 {round_num + 1}-{i + 1}",
                current_context={'monitoring': True}
            )
        
        # 获取当前状态
        summary = engine.get_performance_summary()
        
        print(f"  当前时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  请求总数: {summary['current_metrics']['total_requests']}")
        print(f"  平均响应时间: {summary['current_metrics']['average_response_time']:.4f}s")
        print(f"  系统健康: {summary['system_health']:.2f}")
        
        # 检查警报
        alerts = summary['alerts']
        if alerts:
            print(f"  ⚠️ 活跃警报: {len(alerts)}")
            for alert in alerts[:2]:  # 只显示前2个
                print(f"    - {alert['message']}")
        else:
            print(f"  ✅ 系统运行正常")
        
        time.sleep(0.5)  # 短暂暂停


def main():
    """主演示函数"""
    print("🚀 PATEOAS性能监控系统完整演示")
    print("任务6.3 - 性能监控和指标功能展示")
    print("=" * 80)
    
    try:
        demo_basic_performance_monitoring()
        demo_alert_system()
        demo_performance_trends()
        demo_performance_report()
        demo_enhanced_engine_integration()
        demo_real_time_monitoring()
        
        print("\n\n🎉 演示完成！")
        print("\n📚 任务6.3功能总结:")
        print("  ✅ 性能监控器初始化和配置")
        print("  ✅ 操作计时和组件性能跟踪")
        print("  ✅ 决策准确性和用户满意度指标")
        print("  ✅ 记忆效率和系统健康评估")
        print("  ✅ 实时警报和阈值监控")
        print("  ✅ 性能趋势分析和预测")
        print("  ✅ 综合性能报告生成")
        print("  ✅ 增强引擎集成和自动监控")
        print("  ✅ 数据持久化和历史记录")
        print("  ✅ 实时监控和状态跟踪")
        
        print("\n💡 性能监控系统特点:")
        print("  • 全面的指标收集和分析")
        print("  • 智能警报和阈值管理")
        print("  • 组件级性能跟踪")
        print("  • 趋势分析和预测能力")
        print("  • 自动化报告生成")
        print("  • 与PATEOAS引擎无缝集成")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()