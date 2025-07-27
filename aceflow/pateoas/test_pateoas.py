"""
PATEOAS 系统测试脚本
验证核心功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pateoas.enhanced_engine import PATEOASEnhancedEngine
from pateoas.state_manager import StateContinuityManager
from pateoas.memory_system import ContextMemorySystem
from pateoas.flow_controller import AdaptiveFlowController
from pateoas.decision_gates import OptimizedDG1, OptimizedDG2


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试 PATEOAS 基本功能...")
    
    # 1. 测试增强引擎初始化
    print("\n1. 测试增强引擎初始化")
    engine = PATEOASEnhancedEngine(project_id="test_project")
    print("✅ 增强引擎初始化成功")
    
    # 2. 测试状态连续性
    print("\n2. 测试状态连续性")
    result1 = engine.process_with_state_awareness("开始新功能开发：用户认证系统")
    print(f"✅ 第一次交互完成，置信度: {result1['pateoas_enhancement']['confidence']:.2f}")
    
    result2 = engine.process_with_state_awareness("当前进度如何？")
    print(f"✅ 第二次交互完成，记忆片段数量: {len(result2['pateoas_enhancement']['relevant_memory'])}")
    
    # 3. 测试工作流模式推荐
    print("\n3. 测试工作流模式推荐")
    recommendation = engine.analyze_and_recommend(
        "开发一个复杂的电商系统",
        {"team_size": 8, "urgency": "high", "project_type": "web_application"}
    )
    print(f"✅ 推荐模式: {recommendation['mode_recommendation']['recommended_mode']}")
    print(f"   置信度: {recommendation['mode_recommendation']['confidence']:.2f}")
    
    # 4. 测试决策门评估
    print("\n4. 测试决策门评估")
    mock_state = {
        'user_stories': [
            {'role': 'user', 'feature': 'login', 'benefit': 'access', 'acceptance_criteria': ['test1']},
            {'role': 'admin', 'feature': 'manage', 'benefit': 'control', 'acceptance_criteria': ['test2']}
        ],
        'pending_tasks': [
            {'estimated_hours': 4},
            {'estimated_hours': 6}
        ],
        'test_cases': [
            {'related_story_id': 'story1'},
            {'related_story_id': 'story2'}
        ]
    }
    
    dg1_result = engine.evaluate_decision_gate('DG1', mock_state)
    print(f"✅ DG1 评估结果: {dg1_result['decision']}")
    print(f"   置信度: {dg1_result['confidence']:.2f}")
    
    # 5. 测试系统状态
    print("\n5. 测试系统状态")
    status = engine.get_pateoas_status()
    print(f"✅ 系统状态: {status['system_info']['status']}")
    print(f"   总交互次数: {status['performance_metrics']['total_interactions']}")
    print(f"   记忆总数: {status['memory_info']['total_memories']}")
    
    print("\n🎉 所有基本功能测试通过！")
    return True


def test_state_continuity():
    """测试状态连续性"""
    print("\n🧪 测试状态连续性...")
    
    state_manager = StateContinuityManager("test_continuity")
    
    # 添加记忆
    state_manager.add_memory("项目使用 FastAPI 框架", "decision", 0.8, ["FastAPI", "框架"])
    state_manager.add_memory("团队有5个人", "context", 0.6, ["团队", "规模"])
    
    # 添加下一步建议
    state_manager.add_next_action("continue", "开始需求分析", "aceflow run S1", 0.9)
    
    # 生成状态声明
    declaration = state_manager.generate_state_declaration()
    
    print(f"✅ 当前任务: {declaration['current_task']}")
    print(f"✅ 记忆片段数量: {len(declaration['memory_fragments'])}")
    print(f"✅ 下一步建议数量: {len(declaration['next_suggestions'])}")
    
    return True


def test_memory_system():
    """测试记忆系统"""
    print("\n🧪 测试记忆系统...")
    
    memory_system = ContextMemorySystem("test_memory")
    
    # 存储交互
    memory_system.store_interaction(
        "我们应该使用什么数据库？",
        {"recommendation": "PostgreSQL", "reasoning": "适合复杂查询"}
    )
    
    memory_system.store_interaction(
        "如何处理用户认证？",
        {"recommendation": "JWT + OAuth2", "reasoning": "安全且灵活"}
    )
    
    # 召回相关记忆
    relevant = memory_system.recall_relevant_context(
        "数据库设计问题",
        {"project_type": "web_api"}
    )
    
    print(f"✅ 相关记忆数量: {len(relevant)}")
    if relevant:
        print(f"✅ 最相关记忆: {relevant[0]['content'][:50]}...")
    
    # 获取统计信息
    stats = memory_system.get_memory_stats()
    print(f"✅ 总记忆数量: {stats['total_memories']}")
    
    return True


def test_flow_controller():
    """测试流程控制器"""
    print("\n🧪 测试流程控制器...")
    
    controller = AdaptiveFlowController()
    
    # 测试模式选择
    mode_result = controller.select_optimal_workflow_mode(
        "开发一个简单的博客系统",
        {"team_size": 2, "urgency": "normal"}
    )
    
    print(f"✅ 推荐模式: {mode_result['recommended_mode']}")
    print(f"✅ 置信度: {mode_result['confidence']:.2f}")
    
    # 测试决策制定
    decision = controller.decide_next_action(
        "我想检查项目状态",
        {"workflow_state": {"current_stage": "S2", "stage_progress": 60}},
        []
    )
    
    print(f"✅ 推荐行动: {decision['recommended_action'].description}")
    print(f"✅ 决策置信度: {decision['confidence']:.2f}")
    
    return True


def test_decision_gates():
    """测试决策门"""
    print("\n🧪 测试决策门...")
    
    # 测试 DG1
    dg1 = OptimizedDG1()
    
    test_state = {
        'user_stories': [
            {'role': 'user', 'feature': 'login', 'benefit': 'access', 'acceptance_criteria': ['valid login']},
            {'role': 'user', 'feature': 'logout', 'benefit': 'security', 'acceptance_criteria': ['clean logout']}
        ],
        'pending_tasks': [
            {'estimated_hours': 4},
            {'estimated_hours': 6},
            {'estimated_hours': 3}
        ],
        'test_cases': [
            {'related_story_id': 'story1'},
            {'related_story_id': 'story2'}
        ]
    }
    
    result = dg1.evaluate(test_state, {"urgency": "normal"}, {"success_rate": 0.85})
    
    print(f"✅ DG1 决策结果: {result['decision']}")
    print(f"✅ 置信度: {result['confidence']:.2f}")
    print(f"✅ 建议数量: {len(result['recommendations'])}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始 PATEOAS 系统全面测试")
    print("=" * 50)
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("状态连续性", test_state_continuity),
        ("记忆系统", test_memory_system),
        ("流程控制器", test_flow_controller),
        ("决策门", test_decision_gates)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 测试: {test_name}")
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！PATEOAS 系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)