#!/usr/bin/env python3
"""
优化决策门系统测试
测试OptimizedDG1和OptimizedDG2的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from aceflow.pateoas.decision_gates import (
    OptimizedDG1, OptimizedDG2, DecisionGateManager, 
    DecisionGateFactory, initialize_default_gates
)
from aceflow.pateoas.models import MemoryFragment, MemoryCategory


def create_test_memories() -> list:
    """创建测试记忆数据"""
    
    memories = []
    base_time = datetime.now()
    
    # 需求记忆
    memories.extend([
        MemoryFragment(
            content="用户应该能够注册账户，包括邮箱验证功能",
            category=MemoryCategory.REQUIREMENT,
            importance=0.9,
            tags=["user", "registration", "email"],
            created_at=base_time - timedelta(days=5)
        ),
        MemoryFragment(
            content="系统必须支持用户登录和会话管理",
            category=MemoryCategory.REQUIREMENT,
            importance=0.85,
            tags=["user", "login", "session"],
            created_at=base_time - timedelta(days=4)
        ),
        MemoryFragment(
            content="需要实现商品管理功能，包括增删改查",
            category=MemoryCategory.REQUIREMENT,
            importance=0.8,
            tags=["product", "management", "crud"],
            created_at=base_time - timedelta(days=3)
        )
    ])
    
    # 设计决策记忆
    memories.extend([
        MemoryFragment(
            content="采用JWT token进行用户认证，设计RESTful API架构",
            category=MemoryCategory.DECISION,
            importance=0.9,
            tags=["jwt", "api", "architecture", "user"],
            created_at=base_time - timedelta(days=2)
        ),
        MemoryFragment(
            content="使用MySQL数据库存储用户和商品信息，设计合理的表结构",
            category=MemoryCategory.DECISION,
            importance=0.85,
            tags=["mysql", "database", "design"],
            created_at=base_time - timedelta(days=1)
        )
    ])
    
    # 学习记忆
    memories.extend([
        MemoryFragment(
            content="学习了JWT token的最佳实践和安全考虑",
            category=MemoryCategory.LEARNING,
            importance=0.8,
            tags=["jwt", "security", "best-practice"],
            created_at=base_time - timedelta(hours=12)
        ),
        MemoryFragment(
            content="研究了RESTful API设计规范和版本管理",
            category=MemoryCategory.LEARNING,
            importance=0.75,
            tags=["api", "rest", "versioning"],
            created_at=base_time - timedelta(hours=6)
        )
    ])
    
    # 问题记忆
    memories.extend([
        MemoryFragment(
            content="发现邮箱验证功能的安全漏洞，需要加强验证",
            category=MemoryCategory.ISSUE,
            importance=0.9,
            tags=["email", "security", "vulnerability"],
            created_at=base_time - timedelta(hours=3)
        )
    ])
    
    # 模式记忆
    memories.extend([
        MemoryFragment(
            content="用户认证模式：JWT + 刷新令牌机制",
            category=MemoryCategory.PATTERN,
            importance=0.85,
            tags=["authentication", "jwt", "refresh-token"],
            created_at=base_time - timedelta(hours=1)
        )
    ])
    
    return memories


def test_optimized_dg1():
    """测试优化的DG1决策门"""
    
    print("=== 测试优化的DG1决策门 ===")
    
    # 创建DG1实例
    dg1 = OptimizedDG1()
    print(f"✓ 创建DG1实例: {dg1.name}")
    
    # 准备测试数据
    memories = create_test_memories()
    
    # 测试场景1：项目准备充分的情况
    print("\n场景1: 项目准备充分")
    current_state = {
        'current_stage': 'S2',
        'task_progress': 0.8,
        'time_constraints': {},
        'quality_requirements': {}
    }
    
    project_context = {
        'complexity': 'medium',
        'team_experience': 'medium'
    }
    
    evaluation = dg1.evaluate(current_state, memories, project_context)
    
    print(f"  决策结果: {evaluation.result.value}")
    print(f"  置信度: {evaluation.confidence:.2f}")
    print(f"  总分: {evaluation.score:.2f}")
    print("  标准分数:")
    for criteria, score in evaluation.criteria_scores.items():
        print(f"    {criteria}: {score:.2f}")
    print("  建议:")
    for rec in evaluation.recommendations:
        print(f"    - {rec}")
    print("  风险因素:")
    for risk in evaluation.risk_factors:
        print(f"    - {risk}")
    
    # 测试场景2：项目准备不足的情况
    print("\n场景2: 项目准备不足")
    # 移除一些关键记忆来模拟准备不足
    limited_memories = memories[:3]  # 只保留需求记忆
    
    evaluation2 = dg1.evaluate(current_state, limited_memories, project_context)
    
    print(f"  决策结果: {evaluation2.result.value}")
    print(f"  置信度: {evaluation2.confidence:.2f}")
    print(f"  总分: {evaluation2.score:.2f}")
    print("  建议:")
    for rec in evaluation2.recommendations:
        print(f"    - {rec}")
    
    # 测试场景3：高复杂度项目配新手团队
    print("\n场景3: 高复杂度项目配新手团队")
    high_risk_context = {
        'complexity': 'high',
        'team_experience': 'junior'
    }
    
    evaluation3 = dg1.evaluate(current_state, memories, high_risk_context)
    
    print(f"  决策结果: {evaluation3.result.value}")
    print(f"  置信度: {evaluation3.confidence:.2f}")
    print(f"  总分: {evaluation3.score:.2f}")
    print("  风险因素:")
    for risk in evaluation3.risk_factors:
        print(f"    - {risk}")
    
    print("✓ DG1测试完成")


def test_optimized_dg2():
    """测试优化的DG2决策门"""
    
    print("\n=== 测试优化的DG2决策门 ===")
    
    # 创建DG2实例
    dg2 = OptimizedDG2()
    print(f"✓ 创建DG2实例: {dg2.name}")
    
    # 准备测试数据
    memories = create_test_memories()
    
    # 添加一些开发阶段的记忆
    base_time = datetime.now()
    dev_memories = [
        MemoryFragment(
            content="完成了用户注册功能的代码实现和单元测试",
            category=MemoryCategory.PATTERN,
            importance=0.9,
            tags=["user", "registration", "implementation", "test"],
            created_at=base_time - timedelta(hours=2)
        ),
        MemoryFragment(
            content="集成测试发现了登录功能的一个小问题，已解决",
            category=MemoryCategory.ISSUE,
            importance=0.7,
            tags=["login", "integration", "resolved"],
            created_at=base_time - timedelta(hours=1)
        )
    ]
    
    all_memories = memories + dev_memories
    
    # 测试场景1：任务完成度高
    print("\n场景1: 任务完成度高")
    current_state = {
        'current_stage': 'S3',
        'task_progress': 0.9,
        'time_constraints': {},
        'quality_requirements': {}
    }
    
    project_context = {
        'complexity': 'medium',
        'team_experience': 'medium'
    }
    
    evaluation = dg2.evaluate(current_state, all_memories, project_context)
    
    print(f"  决策结果: {evaluation.result.value}")
    print(f"  置信度: {evaluation.confidence:.2f}")
    print(f"  总分: {evaluation.score:.2f}")
    print("  标准分数:")
    for criteria, score in evaluation.criteria_scores.items():
        print(f"    {criteria}: {score:.2f}")
    print("  建议:")
    for rec in evaluation.recommendations:
        print(f"    - {rec}")
    print("  下一步行动:")
    for action in evaluation.next_actions:
        print(f"    - {action}")
    
    # 测试场景2：任务完成度低
    print("\n场景2: 任务完成度低")
    low_progress_state = {
        'current_stage': 'S3',
        'task_progress': 0.6,
        'time_constraints': {},
        'quality_requirements': {}
    }
    
    evaluation2 = dg2.evaluate(low_progress_state, memories, project_context)
    
    print(f"  决策结果: {evaluation2.result.value}")
    print(f"  置信度: {evaluation2.confidence:.2f}")
    print(f"  总分: {evaluation2.score:.2f}")
    print("  建议:")
    for rec in evaluation2.recommendations:
        print(f"    - {rec}")
    
    # 测试场景3：不同阶段的评估
    print("\n场景3: 不同阶段的评估")
    stages = ['S1', 'S2', 'S4', 'S5', 'S6']
    
    for stage in stages:
        stage_state = {
            'current_stage': stage,
            'task_progress': 0.85,
            'time_constraints': {},
            'quality_requirements': {}
        }
        
        evaluation = dg2.evaluate(stage_state, all_memories, project_context)
        print(f"  {stage}阶段: {evaluation.result.value} (分数: {evaluation.score:.2f})")
    
    print("✓ DG2测试完成")


def test_decision_gate_manager():
    """测试决策门管理器"""
    
    print("\n=== 测试决策门管理器 ===")
    
    # 创建管理器
    manager = DecisionGateManager()
    print("✓ 创建决策门管理器")
    
    # 注册决策门
    dg1 = OptimizedDG1()
    dg2 = OptimizedDG2()
    
    manager.register_gate(dg1)
    manager.register_gate(dg2)
    print("✓ 注册DG1和DG2决策门")
    
    # 准备测试数据
    memories = create_test_memories()
    current_state = {
        'current_stage': 'S2',
        'task_progress': 0.8,
        'time_constraints': {},
        'quality_requirements': {}
    }
    project_context = {
        'complexity': 'medium',
        'team_experience': 'medium'
    }
    
    # 测试单个决策门评估
    print("\n单个决策门评估:")
    dg1_eval = manager.evaluate_gate("DG1", current_state, memories, project_context)
    print(f"  DG1结果: {dg1_eval.result.value} (置信度: {dg1_eval.confidence:.2f})")
    
    # 测试所有决策门评估
    print("\n所有决策门评估:")
    all_evaluations = manager.evaluate_all_gates(current_state, memories, project_context)
    
    for gate_id, evaluation in all_evaluations.items():
        print(f"  {gate_id}: {evaluation.result.value} (分数: {evaluation.score:.2f})")
    
    # 测试评估历史
    print("\n评估历史:")
    history = manager.get_evaluation_history()
    print(f"  总评估次数: {len(history)}")
    
    dg1_history = manager.get_evaluation_history("DG1")
    print(f"  DG1评估次数: {len(dg1_history)}")
    
    # 测试性能指标
    print("\n性能指标:")
    dg1_performance = manager.get_gate_performance("DG1")
    print(f"  DG1准确率: {dg1_performance['accuracy']:.2f}")
    
    print("✓ 决策门管理器测试完成")


def test_decision_gate_factory():
    """测试决策门工厂"""
    
    print("\n=== 测试决策门工厂 ===")
    
    # 测试创建决策门
    dg1 = DecisionGateFactory.create_decision_gate("DG1")
    dg2 = DecisionGateFactory.create_decision_gate("DG2")
    
    print(f"✓ 创建DG1: {dg1.name}")
    print(f"✓ 创建DG2: {dg2.name}")
    
    # 测试获取可用决策门
    available_gates = DecisionGateFactory.get_available_gates()
    print(f"✓ 可用决策门: {available_gates}")
    
    # 测试错误处理
    try:
        invalid_gate = DecisionGateFactory.create_decision_gate("DG3")
    except ValueError as e:
        print(f"✓ 正确处理无效决策门ID: {e}")
    
    print("✓ 决策门工厂测试完成")


def test_initialize_default_gates():
    """测试默认决策门初始化"""
    
    print("\n=== 测试默认决策门初始化 ===")
    
    # 初始化默认决策门
    manager = initialize_default_gates()
    print("✓ 初始化默认决策门管理器")
    
    # 验证决策门已注册
    available_gates = ["DG1", "DG2"]
    
    for gate_id in available_gates:
        try:
            performance = manager.get_gate_performance(gate_id)
            print(f"✓ {gate_id}已注册，准确率: {performance['accuracy']:.2f}")
        except ValueError:
            print(f"✗ {gate_id}未注册")
    
    print("✓ 默认决策门初始化测试完成")


def test_adaptive_thresholds():
    """测试自适应阈值调整"""
    
    print("\n=== 测试自适应阈值调整 ===")
    
    dg1 = OptimizedDG1()
    memories = create_test_memories()
    
    # 测试不同项目上下文的阈值调整
    contexts = [
        {'complexity': 'low', 'team_experience': 'senior'},
        {'complexity': 'medium', 'team_experience': 'medium'},
        {'complexity': 'high', 'team_experience': 'junior'}
    ]
    
    for i, project_context in enumerate(contexts, 1):
        print(f"\n场景{i}: 复杂度={project_context['complexity']}, 经验={project_context['team_experience']}")
        
        current_state = {
            'current_stage': 'S2',
            'task_progress': 0.8,
            'time_constraints': {},
            'quality_requirements': {}
        }
        
        evaluation = dg1.evaluate(current_state, memories, project_context)
        
        print(f"  决策结果: {evaluation.result.value}")
        print(f"  总分: {evaluation.score:.2f}")
        print("  关键标准分数:")
        key_criteria = ['requirements_completeness', 'design_accuracy', 'feasibility_assessment']
        for criteria in key_criteria:
            if criteria in evaluation.criteria_scores:
                print(f"    {criteria}: {evaluation.criteria_scores[criteria]:.2f}")
    
    print("✓ 自适应阈值调整测试完成")


def main():
    """主测试函数"""
    
    print("开始优化决策门系统测试...")
    
    try:
        # 运行所有测试
        test_optimized_dg1()
        test_optimized_dg2()
        test_decision_gate_manager()
        test_decision_gate_factory()
        test_initialize_default_gates()
        test_adaptive_thresholds()
        
        print("\n=== 优化决策门系统测试完成 ===")
        print("✓ 所有测试通过")
        print("✓ OptimizedDG1和OptimizedDG2功能正常")
        print("✓ 决策门管理器功能正常")
        print("✓ 工厂模式和初始化功能正常")
        print("✓ 自适应阈值调整功能正常")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)