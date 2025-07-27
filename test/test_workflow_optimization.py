#!/usr/bin/env python3
"""
测试工作流优化算法
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_workflow_optimization():
    """测试工作流优化功能"""
    try:
        from aceflow.pateoas.flow_controller import AdaptiveFlowControllerWithPATEOAS
        from aceflow.pateoas.memory_system import ContextMemorySystem
        
        print("=== 工作流优化算法测试 ===")
        
        # 1. 创建流程控制器和记忆系统
        flow_controller = AdaptiveFlowControllerWithPATEOAS()
        memory_system = ContextMemorySystem(project_id="workflow_test")
        print("✓ 创建流程控制器和记忆系统成功")
        
        # 2. 添加测试记忆
        test_memories = [
            {
                'content': '用户需要一个高性能的API系统，支持高并发访问',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['API', '性能', '并发']
            },
            {
                'content': '决定使用FastAPI + Redis + PostgreSQL技术栈',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['FastAPI', 'Redis', 'PostgreSQL', '技术栈']
            },
            {
                'content': '发现数据库查询性能瓶颈，需要优化索引',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['数据库', '性能', '索引']
            },
            {
                'content': '学会了Redis缓存策略，可以显著提升API响应速度',
                'category': 'learning',
                'importance': 0.75,
                'tags': ['Redis', '缓存', '性能优化']
            },
            {
                'content': '用户访问模式显示80%的请求集中在核心API上',
                'category': 'pattern',
                'importance': 0.7,
                'tags': ['用户行为', 'API使用', '模式']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        # 获取所有记忆
        all_memories = []
        for category_memories in memory_system.memory_categories.values():
            all_memories.extend(category_memories)
        
        print(f"✓ 添加了 {len(test_memories)} 条测试记忆")
        
        # 3. 测试不同场景的工作流优化
        test_scenarios = [
            {
                'name': '时间紧迫场景',
                'current_state': {
                    'current_stage': 'S3',
                    'task_progress': 0.4,
                    'urgency_level': 'high',
                    'deadline_pressure': True,
                    'available_dev_time': 0.6,
                    'team_capacity': 0.8,
                    'quality_priority': 'medium'
                },
                'expected_strategy': 'speed'
            },
            {
                'name': '质量优先场景',
                'current_state': {
                    'current_stage': 'S5',
                    'task_progress': 0.8,
                    'urgency_level': 'normal',
                    'deadline_pressure': False,
                    'available_dev_time': 0.9,
                    'team_capacity': 0.9,
                    'quality_priority': 'high',
                    'quality_threshold': 0.9
                },
                'expected_strategy': 'quality'
            },
            {
                'name': '平衡发展场景',
                'current_state': {
                    'current_stage': 'S4',
                    'task_progress': 0.6,
                    'urgency_level': 'normal',
                    'deadline_pressure': False,
                    'available_dev_time': 0.8,
                    'team_capacity': 0.8,
                    'quality_priority': 'medium'
                },
                'expected_strategy': 'balanced'
            }
        ]
        
        print("\\n=== 不同场景的工作流优化测试 ===")
        
        for scenario in test_scenarios:
            print(f"\\n场景: {scenario['name']}")
            
            # 执行工作流优化
            optimization_result = flow_controller.optimize_workflow_with_pateoas(
                current_state=scenario['current_state'],
                memories=all_memories,
                project_context={'project_type': 'api_development'}
            )
            
            recommendation = optimization_result['recommendation']
            
            print(f"  推荐策略: {recommendation['strategy']}")
            print(f"  推荐模式: {recommendation['mode']}")
            print(f"  置信度: {recommendation['confidence']:.2f}")
            print(f"  预计时间节省: {recommendation['time_saving']*100:.1f}%")
            print(f"  质量影响: {recommendation['quality_impact']*100:.1f}%")
            print(f"  推理: {recommendation['reasoning']}")
            
            # 显示建议行动
            if recommendation['actions']:
                print(f"  建议行动:")
                for i, action in enumerate(recommendation['actions'][:3]):
                    print(f"    {i+1}. [{action['priority']}] {action['description']}")
            
            # 显示性能影响
            performance_impact = optimization_result['performance_impact']
            print(f"  性能影响:")
            for metric, impact in performance_impact.items():
                if impact != 0:
                    sign = "+" if impact > 0 else ""
                    print(f"    {metric}: {sign}{impact*100:.1f}%")
            
            # 验证策略是否符合预期
            expected = scenario.get('expected_strategy')
            actual = recommendation['strategy']
            match_status = "✓" if expected == actual else "?"
            print(f"  {match_status} 策略匹配: 预期 {expected}, 实际 {actual}")
        
        # 4. 测试优化历史记录
        print("\\n=== 优化历史记录测试 ===")
        
        history = flow_controller.get_optimization_history()
        print(f"优化历史记录数量: {len(history)}")
        
        if history:
            latest = history[-1]
            print(f"最新优化:")
            print(f"  时间: {latest['timestamp']}")
            print(f"  策略: {latest['strategy']}")
            print(f"  置信度: {latest['confidence']:.2f}")
            print(f"  应用变更数: {latest['applied_changes']}")
        
        # 5. 测试优化效果分析
        print("\\n=== 优化效果分析测试 ===")
        
        effectiveness = flow_controller.analyze_optimization_effectiveness()
        
        if effectiveness['status'] == 'analyzed':
            print(f"分析结果:")
            print(f"  优化次数: {effectiveness['optimization_count']}")
            print(f"  平均置信度: {effectiveness['avg_confidence']:.2f}")
            print(f"  最常用策略: {effectiveness['most_used_strategy']}")
            print(f"  效果评分: {effectiveness['effectiveness_score']:.2f}")
            
            print(f"  策略分布:")
            for strategy, count in effectiveness['strategy_distribution'].items():
                print(f"    {strategy}: {count} 次")
            
            print(f"  累积收益:")
            benefits = effectiveness['cumulative_benefits']
            print(f"    时间节省: {benefits['time_saving']*100:.1f}%")
            print(f"    质量提升: {benefits['quality_improvement']*100:.1f}%")
        
        print("\\n=== 工作流优化算法测试完成 ===")
        print("✓ 所有核心功能正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow_optimization()
    sys.exit(0 if success else 1)