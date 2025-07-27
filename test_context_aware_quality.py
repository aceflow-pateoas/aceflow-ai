#!/usr/bin/env python3
"""
上下文感知质量评估测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from datetime import datetime, timedelta
from aceflow.pateoas.quality_assessment import (
    ContextAwareQualityAssessment, QualityDimension, QualityThreshold
)
from aceflow.pateoas.models import MemoryFragment, MemoryCategory


def test_context_aware_quality_assessment():
    """测试上下文感知质量评估"""
    
    print("=== 上下文感知质量评估测试 ===")
    
    # 创建质量评估器
    assessor = ContextAwareQualityAssessment()
    print("✓ 创建质量评估器")
    
    # 创建测试数据
    memories = [
        MemoryFragment(
            content="需求分析已完成，包含用户管理和权限控制",
            category=MemoryCategory.REQUIREMENT,
            importance=0.8,
            tags=["requirement", "user_management"]
        ),
        MemoryFragment(
            content="设计决策：采用微服务架构",
            category=MemoryCategory.DECISION,
            importance=0.9,
            tags=["design", "architecture", "microservice"]
        ),
        MemoryFragment(
            content="学习了Spring Boot框架的使用",
            category=MemoryCategory.LEARNING,
            importance=0.7,
            tags=["learning", "spring_boot"]
        ),
        MemoryFragment(
            content="发现了数据库连接问题，已解决",
            category=MemoryCategory.ISSUE,
            importance=0.6,
            tags=["issue", "database", "resolved"]
        ),
        MemoryFragment(
            content="代码审查发现了几个潜在问题",
            category=MemoryCategory.PATTERN,
            importance=0.5,
            tags=["review", "code_quality"]
        )
    ]
    
    # 测试场景1：经验丰富的团队，低复杂度项目
    print("\n场景1: 经验丰富的团队，低复杂度项目")
    
    quality_scores = {
        'completeness': 0.7,
        'accuracy': 0.8,
        'consistency': 0.6,
        'feasibility': 0.9
    }
    
    project_context = {
        'team_experience': 'senior',
        'complexity': 'low',
        'timeline': 'normal'
    }
    
    result1 = assessor.assess_quality_with_context(quality_scores, project_context, memories)
    
    print(f"  整体质量分数: {result1['overall_quality']['score']:.2f}")
    print(f"  质量等级: {result1['overall_quality']['quality_level']}")
    print(f"  置信度: {result1['overall_quality']['confidence']:.2f}")
    print(f"  是否达标: {result1['overall_quality']['meets_standard']}")
    
    print("  各维度评估:")
    for criteria, assessment in result1['quality_assessment'].items():
        print(f"    {criteria}: {assessment['score']:.2f} (调整: {assessment['context_adjustment']:+.2f})")
    
    print("  建议:")
    for rec in result1['recommendations'][:3]:
        print(f"    - {rec}")
    
    # 测试场景2：新手团队，高复杂度项目
    print("\n场景2: 新手团队，高复杂度项目")
    
    project_context2 = {
        'team_experience': 'junior',
        'complexity': 'high',
        'timeline': 'tight'
    }
    
    result2 = assessor.assess_quality_with_context(quality_scores, project_context2, memories)
    
    print(f"  整体质量分数: {result2['overall_quality']['score']:.2f}")
    print(f"  质量等级: {result2['overall_quality']['quality_level']}")
    print(f"  置信度: {result2['overall_quality']['confidence']:.2f}")
    
    print("  各维度评估:")
    for criteria, assessment in result2['quality_assessment'].items():
        print(f"    {criteria}: {assessment['score']:.2f} (调整: {assessment['context_adjustment']:+.2f})")
    
    print("  风险因素:")
    for risk in result2['risk_factors'][:3]:
        print(f"    - {risk}")
    
    # 测试场景3：时间压力大的项目
    print("\n场景3: 时间压力大的项目")
    
    # 添加时间压力相关的记忆
    urgent_memories = memories + [
        MemoryFragment(
            content="客户要求紧急交付，截止日期提前",
            category=MemoryCategory.ISSUE,
            importance=0.9,
            tags=["urgent", "deadline"]
        ),
        MemoryFragment(
            content="项目延期风险较高",
            category=MemoryCategory.ISSUE,
            importance=0.8,
            tags=["delay", "risk"]
        )
    ]
    
    project_context3 = {
        'team_experience': 'medium',
        'complexity': 'medium',
        'timeline': 'urgent'
    }
    
    result3 = assessor.assess_quality_with_context(quality_scores, project_context3, urgent_memories)
    
    print(f"  时间压力评估: {result3['context_analysis']['time_pressure']}")
    print(f"  整体质量分数: {result3['overall_quality']['score']:.2f}")
    
    print("  上下文洞察:")
    insights = result3['contextual_insights']
    print(f"    质量一致性: {insights['quality_trends']['quality_consistency']:.2f}")
    print(f"    上下文有利度: {insights['context_impact']['overall_context_favorability']:.2f}")
    
    if insights['improvement_priorities']:
        print("  改进优先级:")
        for priority in insights['improvement_priorities'][:2]:
            print(f"    - {priority['criteria']}: 优先级 {priority['priority_score']:.2f}")
    
    print("✓ 上下文感知质量评估测试完成")
    return True


def test_quality_trends():
    """测试质量趋势分析"""
    
    print("\n=== 质量趋势分析测试 ===")
    
    assessor = ContextAwareQualityAssessment()
    
    # 模拟多次评估以建立趋势
    base_scores = {'completeness': 0.6, 'accuracy': 0.7, 'consistency': 0.5}
    project_context = {'team_experience': 'medium', 'complexity': 'medium'}
    memories = []
    
    print("模拟5次质量评估...")
    
    for i in range(5):
        # 逐渐改进的分数
        improved_scores = {
            key: min(1.0, value + i * 0.05) 
            for key, value in base_scores.items()
        }
        
        result = assessor.assess_quality_with_context(improved_scores, project_context, memories)
        print(f"  评估 {i+1}: 整体分数 {result['overall_quality']['score']:.2f}")
    
    # 分析趋势
    trends = assessor.get_quality_trends()
    print(f"\n质量趋势分析:")
    print(f"  趋势: {trends['trend']}")
    if trends['trend'] != 'insufficient_data':
        print(f"  最近平均分: {trends['recent_average']:.2f}")
        print(f"  改进率: {trends['improvement_rate']:+.2f}")
    
    # 获取评估历史
    history = assessor.get_assessment_history(3)
    print(f"\n最近3次评估历史:")
    for i, entry in enumerate(history):
        print(f"  {i+1}. 分数: {entry['overall_score']:.2f}, 等级: {entry['quality_level']}")
    
    print("✓ 质量趋势分析测试完成")
    return True


def test_adaptive_thresholds():
    """测试自适应阈值调整"""
    
    print("\n=== 自适应阈值调整测试 ===")
    
    assessor = ContextAwareQualityAssessment()
    
    # 测试不同上下文下的阈值调整
    contexts = [
        {'team_experience': 'senior', 'complexity': 'low', 'name': '理想条件'},
        {'team_experience': 'junior', 'complexity': 'high', 'name': '挑战条件'},
        {'team_experience': 'medium', 'complexity': 'medium', 'name': '标准条件'}
    ]
    
    base_scores = {'completeness': 0.75, 'accuracy': 0.75, 'consistency': 0.75}
    memories = []
    
    for context in contexts:
        print(f"\n{context['name']}:")
        
        # 分析上下文
        context_analysis = assessor._analyze_project_context(context, memories)
        
        # 调整阈值
        adjusted_thresholds = assessor._adjust_quality_thresholds(context_analysis)
        
        print("  调整后的阈值:")
        for criteria, threshold in adjusted_thresholds.items():
            print(f"    {criteria}: {threshold:.2f}")
        
        # 评估质量
        result = assessor.assess_quality_with_context(base_scores, context, memories)
        
        print(f"  整体评估结果: {result['overall_quality']['quality_level']}")
        print(f"  达标维度数: {sum(1 for a in result['quality_assessment'].values() if a['meets_standard'])}")
    
    print("✓ 自适应阈值调整测试完成")
    return True


def test_context_analysis():
    """测试上下文分析功能"""
    
    print("\n=== 上下文分析测试 ===")
    
    assessor = ContextAwareQualityAssessment()
    
    # 创建不同类型的记忆来测试上下文分析
    diverse_memories = [
        MemoryFragment(
            content="项目成功交付", category=MemoryCategory.PATTERN,
            importance=0.9, tags=["success"]
        ),
        MemoryFragment(
            content="学习了新的测试框架", category=MemoryCategory.LEARNING,
            importance=0.7, tags=["learning", "testing"]
        ),
        MemoryFragment(
            content="发现性能问题需要优化", category=MemoryCategory.ISSUE,
            importance=0.8, tags=["performance", "optimize"]
        ),
        MemoryFragment(
            content="客户要求紧急修复", category=MemoryCategory.ISSUE,
            importance=0.9, tags=["urgent", "client"]
        ),
        MemoryFragment(
            content="代码需要重构以提高可维护性", category=MemoryCategory.PATTERN,
            importance=0.6, tags=["refactor", "maintainability"]
        )
    ]
    
    project_context = {'team_experience': 'medium', 'complexity': 'medium'}
    
    # 分析上下文
    context_analysis = assessor._analyze_project_context(project_context, diverse_memories)
    
    print("上下文分析结果:")
    print(f"  团队经验: {context_analysis['team_experience']}")
    print(f"  项目复杂度: {context_analysis['project_complexity']}")
    print(f"  时间压力: {context_analysis['time_pressure']}")
    print(f"  历史成功率: {context_analysis['historical_performance']['success_rate']:.2f}")
    print(f"  领域熟悉度: {context_analysis['domain_familiarity']:.2f}")
    print(f"  技术债务: {context_analysis['technical_debt']:.2f}")
    print(f"  利益相关者参与度: {context_analysis['stakeholder_involvement']:.2f}")
    
    print("✓ 上下文分析测试完成")
    return True


if __name__ == "__main__":
    print("=== 上下文感知质量评估系统测试 ===")
    
    try:
        # 运行所有测试
        test_context_aware_quality_assessment()
        test_quality_trends()
        test_adaptive_thresholds()
        test_context_analysis()
        
        print("\n=== 所有测试完成 ===")
        print("✓ 上下文感知质量评估功能正常")
        print("✓ 自适应阈值调整功能正常")
        print("✓ 质量趋势分析功能正常")
        print("✓ 上下文分析功能正常")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)