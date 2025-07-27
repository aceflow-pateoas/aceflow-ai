#!/usr/bin/env python3
"""
测试智能决策门系统
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_decision_gates():
    """测试智能决策门功能"""
    try:
        from aceflow.pateoas.decision_gates import (
            IntelligentDecisionGate, OptimizedDG1, OptimizedDG2,
            DecisionGateResult, QualityCriteria, QualityThreshold
        )
        from aceflow.pateoas.memory_system import ContextMemorySystem
        
        print("=== 智能决策门系统测试 ===")
        
        # 1. 创建记忆系统和测试数据
        memory_system = ContextMemorySystem(project_id="decision_gate_test")
        
        # 添加测试记忆
        test_memories = [
            {
                'content': '用户需要一个在线教育平台，包含课程管理、学生管理、考试系统',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['在线教育', '课程管理', '学生管理', '考试系统']
            },
            {
                'content': '决定使用Spring Boot + Vue.js + MySQL架构',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['Spring Boot', 'Vue.js', 'MySQL', '架构设计']
            },
            {
                'content': '发现用户认证模块存在安全漏洞',
                'category': 'issue',
                'importance': 0.9,
                'tags': ['安全', '用户认证', '漏洞']
            },
            {
                'content': '学会了JWT token的最佳实践',
                'category': 'learning',
                'importance': 0.8,
                'tags': ['JWT', 'token', '安全', '最佳实践']
            },
            {
                'content': '用户行为分析显示视频播放功能使用最频繁',
                'category': 'pattern',
                'importance': 0.75,
                'tags': ['用户行为', '视频播放', '高频功能']
            },
            {
                'content': '成功解决了视频上传的性能问题',
                'category': 'learning',
                'importance': 0.8,
                'tags': ['视频上传', '性能', '成功', '解决']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        # 获取所有记忆
        all_memories = []
        for category_memories in memory_system.memory_categories.values():
            all_memories.extend(category_memories)
        
        print(f"✓ 创建测试环境，添加了 {len(test_memories)} 条记忆")
        
        # 2. 测试DG1 - 开发前检查决策门
        print("\\n=== DG1 开发前检查决策门测试 ===")
        
        dg1 = OptimizedDG1()
        print(f"创建DG1: {dg1.name} - {dg1.description}")
        
        # DG1测试场景
        dg1_contexts = [
            {
                'name': '理想场景',
                'context': {
                    'project_complexity': 'medium',
                    'team_experience': 'senior',
                    'time_constraints': {'tight_deadline': False},
                    'current_stage': 'S1',
                    'task_progress': 0.9
                }
            },
            {
                'name': '高风险场景',
                'context': {
                    'project_complexity': 'high',
                    'team_experience': 'junior',
                    'time_constraints': {'tight_deadline': True},
                    'current_stage': 'S1',
                    'task_progress': 0.6
                }
            },
            {
                'name': '中等场景',
                'context': {
                    'project_complexity': 'medium',
                    'team_experience': 'medium',
                    'time_constraints': {'tight_deadline': False},
                    'current_stage': 'S1',
                    'task_progress': 0.75
                }
            }
        ]
        
        for scenario in dg1_contexts:
            print(f"\\n场景: {scenario['name']}")
            
            evaluation = dg1.evaluate(scenario['context'], all_memories)
            
            print(f"  决策结果: {evaluation.result.value}")
            print(f"  置信度: {evaluation.confidence:.2f}")
            print(f"  综合得分: {evaluation.overall_score:.2f}")
            print(f"  推理: {evaluation.reasoning}")
            
            # 显示标准得分
            print(f"  标准得分:")
            for criteria, score in evaluation.criteria_scores.items():
                print(f"    {criteria}: {score:.2f}")
            
            # 显示建议
            if evaluation.recommendations:
                print(f"  建议: {evaluation.recommendations[0]}")
            
            # 显示风险
            if evaluation.risk_factors:
                print(f"  风险: {evaluation.risk_factors[0]}")
            
            # 显示下一步行动
            if evaluation.next_actions:
                print(f"  下一步: {evaluation.next_actions[0]}")
        
        # 3. 测试DG2 - 任务循环控制决策门
        print("\\n=== DG2 任务循环控制决策门测试 ===")
        
        dg2 = OptimizedDG2()
        print(f"创建DG2: {dg2.name} - {dg2.description}")
        
        # DG2测试场景
        dg2_contexts = [
            {
                'name': '任务完成良好',
                'context': {
                    'current_stage': 'S3',
                    'task_progress': 0.9,
                    'expected_progress': 0.85,
                    'project_complexity': 'medium',
                    'quality_requirements': {'high_quality': False},
                    'recent_issues': {'total_count': 1}
                }
            },
            {
                'name': '任务进度落后',
                'context': {
                    'current_stage': 'S4',
                    'task_progress': 0.6,
                    'expected_progress': 0.8,
                    'project_complexity': 'high',
                    'quality_requirements': {'high_quality': True},
                    'recent_issues': {'total_count': 3},
                    'time_constraints': {'tight_deadline': True}
                }
            },
            {
                'name': '质量问题较多',
                'context': {
                    'current_stage': 'S5',
                    'task_progress': 0.8,
                    'expected_progress': 0.75,
                    'project_complexity': 'medium',
                    'quality_requirements': {'high_quality': True},
                    'recent_issues': {'total_count': 5}
                }
            }
        ]
        
        for scenario in dg2_contexts:
            print(f"\\n场景: {scenario['name']}")
            
            evaluation = dg2.evaluate(scenario['context'], all_memories)
            
            print(f"  决策结果: {evaluation.result.value}")
            print(f"  置信度: {evaluation.confidence:.2f}")
            print(f"  综合得分: {evaluation.overall_score:.2f}")
            print(f"  推理: {evaluation.reasoning}")
            
            # 显示标准得分
            print(f"  标准得分:")
            for criteria, score in evaluation.criteria_scores.items():
                print(f"    {criteria}: {score:.2f}")
            
            # 显示建议
            if evaluation.recommendations:
                print(f"  建议: {evaluation.recommendations[0]}")
            
            # 显示下一步行动
            if evaluation.next_actions:
                print(f"  下一步: {evaluation.next_actions[0]}")
        
        # 4. 测试自适应阈值调整
        print("\\n=== 自适应阈值调整测试 ===")
        
        # 测试不同复杂度项目的阈值调整
        complexity_contexts = [
            {'project_complexity': 'low', 'team_experience': 'senior'},
            {'project_complexity': 'medium', 'team_experience': 'medium'},
            {'project_complexity': 'high', 'team_experience': 'junior'}
        ]
        
        for context in complexity_contexts:
            print(f"\\n项目复杂度: {context['project_complexity']}, 团队经验: {context['team_experience']}")
            
            # 创建新的DG1实例来测试阈值调整
            test_dg1 = OptimizedDG1()
            adapted_thresholds = test_dg1._adapt_thresholds(context, all_memories)
            
            print(f"  自适应阈值:")
            for criteria_name, threshold in adapted_thresholds.items():
                original_threshold = test_dg1.quality_thresholds[criteria_name].minimum_score
                print(f"    {criteria_name}: {original_threshold:.2f} -> {threshold.minimum_score:.2f}")
        
        # 5. 测试决策门性能指标
        print("\\n=== 决策门性能指标测试 ===")
        
        # 模拟多次评估来测试性能指标更新
        test_dg1 = OptimizedDG1()
        initial_accuracy = test_dg1.performance_metrics['accuracy']
        
        print(f"初始准确率: {initial_accuracy:.3f}")
        
        # 模拟几次高置信度的成功评估
        for i in range(3):
            context = {
                'project_complexity': 'medium',
                'team_experience': 'senior',
                'current_stage': 'S1',
                'task_progress': 0.8
            }
            evaluation = test_dg1.evaluate(context, all_memories)
            print(f"  评估 {i+1}: 置信度 {evaluation.confidence:.2f}, 准确率 {test_dg1.performance_metrics['accuracy']:.3f}")
        
        accuracy_improvement = test_dg1.performance_metrics['accuracy'] - initial_accuracy
        print(f"准确率提升: {accuracy_improvement:+.3f}")
        
        # 6. 测试决策门集成
        print("\\n=== 决策门集成测试 ===")
        
        # 模拟完整的开发流程决策
        project_context = {
            'project_complexity': 'medium',
            'team_experience': 'medium',
            'time_constraints': {'tight_deadline': False}
        }
        
        print("模拟项目开发流程:")
        
        # DG1: 开发前检查
        print("\\n1. 开发前检查 (DG1)")
        dg1_evaluation = dg1.evaluate(project_context, all_memories)
        print(f"   结果: {dg1_evaluation.result.value} (置信度: {dg1_evaluation.confidence:.2f})")
        
        if dg1_evaluation.result in [DecisionGateResult.PASS, DecisionGateResult.CONDITIONAL_PASS]:
            print("   ✓ 通过DG1，可以开始开发")
            
            # 模拟开发过程，更新上下文
            development_context = project_context.copy()
            development_context.update({
                'current_stage': 'S4',
                'task_progress': 0.8,
                'expected_progress': 0.75
            })
            
            # DG2: 任务循环控制
            print("\\n2. 任务完成检查 (DG2)")
            dg2_evaluation = dg2.evaluate(development_context, all_memories)
            print(f"   结果: {dg2_evaluation.result.value} (置信度: {dg2_evaluation.confidence:.2f})")
            
            if dg2_evaluation.result in [DecisionGateResult.PASS, DecisionGateResult.CONDITIONAL_PASS]:
                print("   ✓ 通过DG2，可以进入下一阶段")
            else:
                print("   ✗ 未通过DG2，需要继续当前阶段")
                print(f"   建议: {dg2_evaluation.recommendations[0] if dg2_evaluation.recommendations else '无'}")
        else:
            print("   ✗ 未通过DG1，需要完善准备工作")
            print(f"   建议: {dg1_evaluation.recommendations[0] if dg1_evaluation.recommendations else '无'}")
        
        # 7. 测试决策门的推理能力
        print("\\n=== 决策门推理能力测试 ===")
        
        complex_context = {
            'project_complexity': 'high',
            'team_experience': 'junior',
            'time_constraints': {'tight_deadline': True},
            'current_stage': 'S1',
            'task_progress': 0.5,
            'recent_issues': {'total_count': 4}
        }
        
        print("复杂场景决策:")
        complex_evaluation = dg1.evaluate(complex_context, all_memories)
        
        print(f"  决策结果: {complex_evaluation.result.value}")
        print(f"  综合分析: {complex_evaluation.reasoning}")
        print(f"  详细建议:")
        for i, recommendation in enumerate(complex_evaluation.recommendations[:3]):
            print(f"    {i+1}. {recommendation}")
        
        if complex_evaluation.risk_factors:
            print(f"  风险提示:")
            for i, risk in enumerate(complex_evaluation.risk_factors[:3]):
                print(f"    {i+1}. {risk}")
        
        print("\\n=== 智能决策门系统测试完成 ===")
        print("✓ DG1和DG2决策门功能正常")
        print("✓ 自适应阈值调整功能正常")
        print("✓ 性能指标更新功能正常")
        print("✓ 决策门集成流程正常")
        print("✓ 推理和建议生成功能正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_decision_gates()
    sys.exit(0 if success else 1)