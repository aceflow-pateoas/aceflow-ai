#!/usr/bin/env python3
"""
简单的决策门测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_decision_gates_import():
    """测试决策门导入"""
    try:
        # 直接导入决策门模块
        import aceflow.pateoas.decision_gates as dg_module
        
        print("✓ 决策门模块导入成功")
        print(f"模块路径: {dg_module.__file__}")
        
        # 检查类是否存在
        classes_to_check = [
            'IntelligentDecisionGate',
            'OptimizedDG1', 
            'OptimizedDG2',
            'DecisionGateManager',
            'DecisionGateFactory'
        ]
        
        for class_name in classes_to_check:
            if hasattr(dg_module, class_name):
                print(f"✓ 找到类: {class_name}")
            else:
                print(f"✗ 缺少类: {class_name}")
        
        # 尝试创建实例
        dg1 = dg_module.OptimizedDG1()
        dg2 = dg_module.OptimizedDG2()
        manager = dg_module.DecisionGateManager()
        
        print(f"✓ DG1创建成功: {dg1.name}")
        print(f"✓ DG2创建成功: {dg2.name}")
        print(f"✓ 管理器创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_decision_gates_functionality():
    """测试决策门功能"""
    try:
        from aceflow.pateoas.decision_gates import OptimizedDG1, OptimizedDG2, DecisionGateManager
        from aceflow.pateoas.models import MemoryFragment, MemoryCategory
        from datetime import datetime
        
        print("\n=== 测试决策门功能 ===")
        
        # 创建测试数据
        current_state = {
            'task_progress': 0.7,
            'current_stage': 'S3'
        }
        
        project_context = {
            'complexity': 'medium',
            'team_experience': 'senior'
        }
        
        memories = [
            MemoryFragment(
                content="需求分析已完成",
                category=MemoryCategory.REQUIREMENT,
                importance=0.8,
                created_at=datetime.now(),
                tags=["requirement", "analysis"]
            ),
            MemoryFragment(
                content="设计决策已确定",
                category=MemoryCategory.DECISION,
                importance=0.9,
                created_at=datetime.now(),
                tags=["design", "architecture"]
            )
        ]
        
        # 测试DG1
        dg1 = OptimizedDG1()
        evaluation1 = dg1.evaluate(current_state, memories, project_context)
        
        print(f"DG1评估结果: {evaluation1.result.value}")
        print(f"DG1置信度: {evaluation1.confidence:.2f}")
        print(f"DG1总分: {evaluation1.score:.2f}")
        
        # 测试DG2
        dg2 = OptimizedDG2()
        evaluation2 = dg2.evaluate(current_state, memories, project_context)
        
        print(f"DG2评估结果: {evaluation2.result.value}")
        print(f"DG2置信度: {evaluation2.confidence:.2f}")
        print(f"DG2总分: {evaluation2.score:.2f}")
        
        # 测试管理器
        manager = DecisionGateManager()
        manager.register_gate(dg1)
        manager.register_gate(dg2)
        
        all_evaluations = manager.evaluate_all_gates(current_state, memories, project_context)
        
        print(f"\n管理器评估结果:")
        for gate_id, eval_result in all_evaluations.items():
            print(f"  {gate_id}: {eval_result.result.value} (置信度: {eval_result.confidence:.2f})")
        
        print("✓ 决策门功能测试成功")
        return True
        
    except Exception as e:
        print(f"✗ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 决策门简单测试 ===")
    
    # 测试导入
    import_success = test_decision_gates_import()
    
    if import_success:
        # 测试功能
        test_decision_gates_functionality()
    else:
        print("导入失败，跳过功能测试")
    
    print("\n=== 测试完成 ===")