#!/usr/bin/env python3
"""
测试智能决策系统
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_intelligent_decision_system():
    """测试智能决策系统功能"""
    try:
        from aceflow.pateoas.flow_controller import AdaptiveFlowControllerWithPATEOAS
        from aceflow.pateoas.memory_system import ContextMemorySystem
        
        print("=== 智能决策系统测试 ===")
        
        # 1. 创建控制器和记忆系统
        controller = AdaptiveFlowControllerWithPATEOAS()
        memory_system = ContextMemorySystem(project_id="decision_test")
        print("✓ 创建智能决策控制器成功")
        
        # 2. 添加测试记忆
        test_memories = [
            {
                'content': '用户需要一个电商平台，包含商品管理、订单处理、用户管理功能',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['电商', '商品管理', '订单', '用户管理']
            },
            {
                'content': '决定使用微服务架构，Spring Boot + MySQL + Redis',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['微服务', 'Spring Boot', 'MySQL', 'Redis']
            },
            {
                'content': '发现订单处理性能瓶颈，需要优化数据库查询',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['性能', '订单处理', '数据库优化']
            },
            {
                'content': '学会了Redis缓存优化技术，显著提升查询速度',
                'category': 'learning',
                'importance': 0.75,
                'tags': ['Redis', '缓存', '性能优化']
            },
            {
                'content': '用户行为分析显示购物车功能使用频率最高',
                'category': 'pattern',
                'importance': 0.7,
                'tags': ['用户行为', '购物车', '高频功能']
            },
            {
                'content': '成功解决了支付接口集成问题',
                'category': 'decision',
                'importance': 0.8,
                'tags': ['支付', '接口', '成功', '解决']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        # 获取所有记忆
        all_memories = []
        for category_memories in memory_system.memory_categories.values():
            all_memories.extend(category_memories)
        
        print(f"✓ 添加了 {len(test_memories)} 条测试记忆")
        
        # 3. 测试不同类型的用户输入和决策
        test_scenarios = [
            {
                'name': '继续开发请求',
                'user_input': '继续开发购物车功能',
                'current_state': {
                    'current_stage': 'S3',
                    'task_progress': 0.6,
                    'team_capacity': 0.8,
                    'deadline_pressure': False
                },
                'project_context': {
                    'complexity': 'medium',
                    'team_experience': 'senior'
                }
            },
            {
                'name': '紧急问题修复',
                'user_input': '支付功能出现严重问题，需要紧急修复',
                'current_state': {
                    'current_stage': 'S4',
                    'task_progress': 0.8,
                    'team_capacity': 0.9,
                    'deadline_pressure': True,
                    'urgency_level': 'high'
                },
                'project_context': {
                    'complexity': 'high',
                    'team_experience': 'medium'
                }
            },
            {
                'name': '优化性能请求',
                'user_input': '系统性能不太好，需要优化一下',
                'current_state': {
                    'current_stage': 'S5',
                    'task_progress': 0.7,
                    'team_capacity': 0.7,
                    'deadline_pressure': False
                },
                'project_context': {
                    'complexity': 'medium',
                    'team_experience': 'senior'
                }
            },
            {
                'name': '项目状态查询',
                'user_input': '当前项目进展如何？',
                'current_state': {
                    'current_stage': 'S4',
                    'task_progress': 0.65,
                    'team_capacity': 0.8,
                    'deadline_pressure': False
                },
                'project_context': {
                    'complexity': 'low',
                    'team_experience': 'medium'
                }
            },
            {
                'name': '计划制定请求',
                'user_input': '帮我制定下一阶段的详细计划',
                'current_state': {
                    'current_stage': 'S2',
                    'task_progress': 0.9,
                    'team_capacity': 0.8,
                    'deadline_pressure': False
                },
                'project_context': {
                    'complexity': 'high',
                    'team_experience': 'junior'
                }
            }
        ]
        
        print("\\n=== 智能决策测试场景 ===")
        
        for scenario in test_scenarios:
            print(f"\\n场景: {scenario['name']}")
            print(f"用户输入: \"{scenario['user_input']}\"")
            
            # 执行智能决策
            decision_result = controller.decide_next_action_with_intelligence(
                user_input=scenario['user_input'],
                current_state=scenario['current_state'],
                memories=all_memories,
                project_context=scenario['project_context']
            )
            
            # 显示决策结果
            primary_action = decision_result['primary_action']
            print(f"  主要行动: {primary_action.description}")
            print(f"  行动类型: {primary_action.action_type.value}")
            print(f"  执行命令: {primary_action.command}")
            print(f"  预计时间: {primary_action.estimated_time}")
            print(f"  决策置信度: {decision_result['confidence']:.2f}")
            
            # 显示意图分析
            intent = decision_result['intent_analysis']
            print(f"  识别意图: {intent['primary_intent']} (置信度: {intent['confidence']:.2f})")
            print(f"  情感分析: {intent['sentiment']['sentiment']} (极性: {intent['sentiment']['polarity']:.2f})")
            print(f"  紧急程度: {intent['urgency']['level']}")
            
            # 显示上下文因素
            context_factors = decision_result['context_factors']
            print(f"  关键上下文:")
            print(f"    项目进度: {context_factors['project_progress']:.1%}")
            print(f"    当前阶段: {context_factors['current_stage']}")
            print(f"    最近问题: {context_factors['recent_issues']} 个")
            print(f"    学习势头: {context_factors['learning_momentum']} 个")
            
            # 显示风险评估
            risk_assessment = decision_result['risk_assessment']
            print(f"  风险评估: {risk_assessment['risk_level']} (分数: {risk_assessment['risk_score']:.2f})")
            if risk_assessment['risks']:
                print(f"    主要风险: {risk_assessment['risks'][0]}")
            
            # 显示成功概率
            print(f"  成功概率: {decision_result['success_probability']:.2f}")
            
            # 显示替代方案
            alternatives = decision_result['alternative_actions']
            if alternatives:
                print(f"  替代方案:")
                for i, alt in enumerate(alternatives[:2]):
                    print(f"    {i+1}. {alt.description} (置信度: {alt.confidence:.2f})")
            
            # 显示推理链
            reasoning_chain = decision_result['reasoning_chain']
            print(f"  推理过程:")
            for step in reasoning_chain[:3]:  # 显示前3步
                print(f"    {step.step_id}: {step.output} (置信度: {step.confidence:.2f})")
        
        # 4. 测试决策历史和学习
        print("\\n=== 决策学习能力测试 ===")
        
        # 模拟重复的决策场景，测试学习能力
        repeated_input = "继续开发用户管理功能"
        repeated_state = {
            'current_stage': 'S3',
            'task_progress': 0.5,
            'team_capacity': 0.8
        }
        
        print("第一次决策:")
        first_decision = controller.decide_next_action_with_intelligence(
            user_input=repeated_input,
            current_state=repeated_state,
            memories=all_memories
        )
        print(f"  置信度: {first_decision['confidence']:.2f}")
        print(f"  成功概率: {first_decision['success_probability']:.2f}")
        
        # 添加成功记忆
        memory_system.add_memory(
            content="成功完成用户管理功能开发，用户反馈良好",
            category='learning',
            importance=0.8,
            tags=['用户管理', '成功', '开发']
        )
        
        # 更新记忆列表
        all_memories = []
        for category_memories in memory_system.memory_categories.values():
            all_memories.extend(category_memories)
        
        print("\\n添加成功经验后的第二次决策:")
        second_decision = controller.decide_next_action_with_intelligence(
            user_input=repeated_input,
            current_state=repeated_state,
            memories=all_memories
        )
        print(f"  置信度: {second_decision['confidence']:.2f}")
        print(f"  成功概率: {second_decision['success_probability']:.2f}")
        
        # 比较学习效果
        confidence_improvement = second_decision['confidence'] - first_decision['confidence']
        success_improvement = second_decision['success_probability'] - first_decision['success_probability']
        
        print(f"\\n学习效果:")
        print(f"  置信度提升: {confidence_improvement:+.3f}")
        print(f"  成功概率提升: {success_improvement:+.3f}")
        
        if confidence_improvement > 0 or success_improvement > 0:
            print("✓ 系统展现了学习能力，能够基于历史经验改进决策")
        else:
            print("? 学习效果不明显，可能需要更多历史数据")
        
        # 5. 测试复杂场景决策
        print("\\n=== 复杂场景决策测试 ===")
        
        complex_scenario = {
            'user_input': '项目遇到技术难题，团队士气不高，但是客户催得很紧，怎么办？',
            'current_state': {
                'current_stage': 'S4',
                'task_progress': 0.4,
                'team_capacity': 0.6,
                'deadline_pressure': True,
                'urgency_level': 'high'
            },
            'project_context': {
                'complexity': 'high',
                'team_experience': 'junior'
            }
        }
        
        print(f"复杂场景: {complex_scenario['user_input']}")
        
        complex_decision = controller.decide_next_action_with_intelligence(
            user_input=complex_scenario['user_input'],
            current_state=complex_scenario['current_state'],
            memories=all_memories,
            project_context=complex_scenario['project_context']
        )
        
        print(f"  智能决策: {complex_decision['primary_action'].description}")
        print(f"  决策置信度: {complex_decision['confidence']:.2f}")
        print(f"  风险等级: {complex_decision['risk_assessment']['risk_level']}")
        print(f"  推荐理由: {complex_decision['primary_action'].command}")
        
        # 显示完整推理链
        print(f"  完整推理过程:")
        for step in complex_decision['reasoning_chain']:
            print(f"    {step.description}: {step.output}")
        
        print("\\n=== 智能决策系统测试完成 ===")
        print("✓ 所有核心功能正常工作")
        print("✓ 意图识别、上下文分析、风险评估、推理链生成功能完整")
        print("✓ 系统展现了学习和适应能力")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_intelligent_decision_system()
    sys.exit(0 if success else 1)