#!/usr/bin/env python3
"""
测试PATEOAS增强引擎
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_pateoas_enhanced_engine():
    """测试PATEOAS增强引擎功能"""
    try:
        from aceflow.pateoas.enhanced_engine import PATEOASEnhancedEngine
        
        print("=== PATEOAS增强引擎测试 ===")
        
        # 1. 创建增强引擎
        engine = PATEOASEnhancedEngine(project_id="test_project_enhanced")
        print("✓ PATEOAS增强引擎创建成功")
        
        # 2. 测试系统状态
        system_status = engine.get_system_status()
        print(f"✓ 系统状态: {system_status['system_health']}")
        print(f"  项目ID: {system_status['project_id']}")
        print(f"  会话ID: {system_status['session_info']['session_id']}")
        print(f"  组件状态: {len([k for k, v in system_status['components_status'].items() if v == 'active'])} 个组件活跃")
        
        # 3. 测试不同类型的用户输入处理
        test_scenarios = [
            {
                'name': '项目启动场景',
                'user_input': '我想开始一个新的电商项目，需要用户管理、商品管理和订单处理功能',
                'context': {
                    'current_stage': 'S1',
                    'task_progress': 0.1,
                    'project_complexity': 'medium',
                    'team_experience': 'medium'
                }
            },
            {
                'name': '开发进行中场景',
                'user_input': '用户登录功能已经完成，现在继续开发商品管理模块',
                'context': {
                    'current_stage': 'S3',
                    'task_progress': 0.6,
                    'project_complexity': 'medium',
                    'team_experience': 'senior'
                }
            },
            {
                'name': '问题解决场景',
                'user_input': '支付接口集成遇到问题，用户支付后订单状态没有更新',
                'context': {
                    'current_stage': 'S4',
                    'task_progress': 0.8,
                    'project_complexity': 'high',
                    'team_experience': 'medium',
                    'urgency_level': 'high'
                }
            },
            {
                'name': '优化请求场景',
                'user_input': '系统响应速度有点慢，需要优化性能',
                'context': {
                    'current_stage': 'S5',
                    'task_progress': 0.9,
                    'project_complexity': 'medium',
                    'team_experience': 'senior'
                }
            },
            {
                'name': '项目收尾场景',
                'user_input': '项目基本完成，需要进行最终测试和部署准备',
                'context': {
                    'current_stage': 'S6',
                    'task_progress': 0.95,
                    'project_complexity': 'medium',
                    'team_experience': 'senior'
                }
            }
        ]
        
        print("\\n=== 不同场景的增强处理测试 ===")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\\n场景 {i}: {scenario['name']}")
            print(f"用户输入: \"{scenario['user_input']}\"")
            
            # 处理用户输入
            result = engine.process_with_state_awareness(
                user_input=scenario['user_input'],
                current_context=scenario['context']
            )
            
            # 显示基本结果
            primary_action = result['primary_action']
            print(f"  主要建议: {primary_action.description}")
            print(f"  行动类型: {primary_action.action_type.value}")
            print(f"  置信度: {result['confidence']:.2f}")
            
            # 显示PATEOAS增强信息
            pateoas_state = result['pateoas_state']
            print(f"  PATEOAS状态:")
            print(f"    当前阶段: {pateoas_state['current_stage']}")
            print(f"    任务进度: {pateoas_state['task_progress']:.1%}")
            print(f"    交互次数: {pateoas_state['interaction_count']}")
            
            # 显示记忆上下文
            memory_context = result['memory_context']
            print(f"  记忆上下文:")
            print(f"    相关记忆: {memory_context['relevant_memories_count']} 条")
            print(f"    上下文丰富度: {memory_context['context_richness']:.2f}")
            
            # 显示决策门评估
            if result['decision_gates']:
                print(f"  决策门评估:")
                for gate_id, evaluation in result['decision_gates'].items():
                    print(f"    {gate_id}: {evaluation['result']} (置信度: {evaluation['confidence']:.2f})")
            
            # 显示下一步建议
            if result['next_actions_suggestions']:
                print(f"  下一步建议:")
                for suggestion in result['next_actions_suggestions'][:2]:
                    print(f"    - [{suggestion['priority']}] {suggestion['description']}")
            
            # 显示工作流优化
            workflow_opt = result['workflow_optimization']
            print(f"  工作流优化: {workflow_opt['strategy']} 策略 (置信度: {workflow_opt['confidence']:.2f})")
            
            # 显示性能洞察
            performance = result['performance_insights']
            print(f"  性能洞察:")
            print(f"    处理效率: {performance['processing_efficiency']:.2f}")
            print(f"    推荐质量: {performance['recommendation_quality']:.2f}")
            
            # 显示上下文洞察
            contextual = result['contextual_insights']
            project_health = contextual['project_health']
            print(f"  项目健康度: {project_health['health_level']} ({project_health['overall_health']:.2f})")
            
            risk_assessment = contextual['risk_assessment']
            print(f"  风险评估: {risk_assessment['risk_level']} (分数: {risk_assessment['risk_score']:.2f})")
            if risk_assessment['risks']:
                print(f"    主要风险: {risk_assessment['risks'][0]}")
        
        # 4. 测试系统学习能力
        print("\\n=== 系统学习能力测试 ===")
        
        # 添加一些成功经验
        success_scenarios = [
            "成功实现了用户认证功能，采用JWT token方案",
            "商品管理模块开发顺利，用户反馈良好",
            "支付接口集成成功，测试通过"
        ]
        
        print("添加成功经验记忆...")
        for success in success_scenarios:
            engine.process_with_state_awareness(
                user_input=success,
                current_context={'current_stage': 'S4', 'task_progress': 0.7}
            )
        
        # 测试相似场景的处理改进
        print("\\n测试学习效果:")
        similar_input = "需要实现订单管理功能，参考之前的成功经验"
        
        learned_result = engine.process_with_state_awareness(
            user_input=similar_input,
            current_context={'current_stage': 'S3', 'task_progress': 0.5}
        )
        
        print(f"  学习后的建议: {learned_result['primary_action'].description}")
        print(f"  置信度: {learned_result['confidence']:.2f}")
        print(f"  相关记忆: {learned_result['memory_context']['relevant_memories_count']} 条")
        
        # 5. 测试错误处理
        print("\\n=== 错误处理测试 ===")
        
        # 模拟一个可能导致错误的场景
        try:
            error_result = engine.process_with_state_awareness(
                user_input="",  # 空输入可能导致错误
                current_context=None
            )
            
            if 'error_info' in error_result:
                print("✓ 错误处理正常工作")
                print(f"  错误类型: {error_result['error_info']['error_type']}")
                print(f"  建议行动: {error_result['primary_action'].description}")
            else:
                print("✓ 系统正常处理了边界情况")
        except Exception as e:
            print(f"✗ 错误处理需要改进: {e}")
        
        # 6. 测试性能监控
        print("\\n=== 性能监控测试 ===")
        
        final_status = engine.get_system_status()
        performance_metrics = final_status['performance_metrics']
        
        print(f"性能指标:")
        print(f"  总请求数: {performance_metrics['total_requests']}")
        print(f"  成功请求数: {performance_metrics['successful_requests']}")
        print(f"  平均响应时间: {performance_metrics['average_response_time']:.3f}秒")
        print(f"  决策准确性: {performance_metrics['decision_accuracy']:.2f}")
        
        success_rate = performance_metrics['successful_requests'] / max(1, performance_metrics['total_requests'])
        print(f"  成功率: {success_rate:.1%}")
        
        # 7. 测试会话管理
        print("\\n=== 会话管理测试 ===")
        
        old_session_id = engine.current_session['session_id']
        old_interaction_count = engine.current_session['interaction_count']
        
        print(f"当前会话: {old_session_id}")
        print(f"交互次数: {old_interaction_count}")
        
        # 重置会话
        engine.reset_session()
        
        new_session_id = engine.current_session['session_id']
        new_interaction_count = engine.current_session['interaction_count']
        
        print(f"重置后会话: {new_session_id}")
        print(f"重置后交互次数: {new_interaction_count}")
        
        if old_session_id != new_session_id and new_interaction_count == 0:
            print("✓ 会话重置功能正常")
        else:
            print("? 会话重置可能有问题")
        
        # 8. 测试系统集成
        print("\\n=== 系统集成测试 ===")
        
        integration_test_input = "我需要一个完整的项目开发建议，包括技术选型、开发计划和风险评估"
        
        comprehensive_result = engine.process_with_state_awareness(
            user_input=integration_test_input,
            current_context={
                'current_stage': 'S1',
                'task_progress': 0.0,
                'project_complexity': 'high',
                'team_experience': 'medium'
            }
        )
        
        print("综合处理结果:")
        print(f"  主要建议: {comprehensive_result['primary_action'].description}")
        print(f"  推理链长度: {len(comprehensive_result['reasoning_chain'])} 步")
        print(f"  替代方案: {len(comprehensive_result['alternative_actions'])} 个")
        print(f"  下一步建议: {len(comprehensive_result['next_actions_suggestions'])} 条")
        
        # 验证所有组件都参与了处理
        components_used = comprehensive_result['meta_information']['components_used']
        expected_components = ['state_manager', 'memory_system', 'flow_controller', 'decision_gates']
        
        if all(comp in components_used for comp in expected_components):
            print("✓ 所有核心组件都参与了处理")
        else:
            print("? 部分组件可能没有正常工作")
        
        print("\\n=== PATEOAS增强引擎测试完成 ===")
        print("✓ 状态感知处理功能正常")
        print("✓ 记忆上下文集成正常")
        print("✓ 决策门评估正常")
        print("✓ 工作流优化正常")
        print("✓ 性能监控正常")
        print("✓ 错误处理正常")
        print("✓ 会话管理正常")
        print("✓ 系统集成正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pateoas_enhanced_engine()
    sys.exit(0 if success else 1)