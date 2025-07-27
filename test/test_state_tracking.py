#!/usr/bin/env python3
"""
测试状态连续性管理器的状态跟踪功能
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

from aceflow.pateoas.state_manager import StateContinuityManager
from aceflow.pateoas.models import MemoryCategory, ActionType


def test_state_tracking():
    """测试状态跟踪功能"""
    print("=== 测试状态连续性管理器 ===")
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp()
    print(f"使用临时目录: {temp_dir}")
    
    try:
        # 初始化状态管理器
        manager = StateContinuityManager(project_id="test_project")
        
        # 测试1: 初始状态
        print("\n1. 测试初始状态")
        initial_state = manager.get_current_state()
        print(f"当前任务: {initial_state['workflow_state']['current_mode']}")
        print(f"项目ID: {initial_state['project_context']['project_id']}")
        
        # 测试2: 更新状态
        print("\n2. 测试状态更新")
        manager.update_state({
            'current_task': '实现用户认证功能',
            'task_progress': 0.3,
            'stage_context': {
                'technology_stack': ['python', 'fastapi', 'jwt'],
                'current_stage': 'S2',
                'workflow_mode': 'standard'
            },
            'trigger': 'user_input',
            'reasoning': '用户开始实现认证功能'
        })
        
        updated_state = manager.get_current_state()
        print(f"更新后任务: {manager.current_state.current_task}")
        print(f"任务进度: {manager.current_state.task_progress * 100}%")
        print(f"技术栈: {updated_state['project_context']['technology_stack']}")
        
        # 测试3: 添加记忆
        print("\n3. 测试记忆管理")
        manager.add_memory(
            content="选择FastAPI作为Web框架，因为性能优秀且团队熟悉",
            category="decision",
            importance=0.9,
            tags=["框架选择", "技术决策"]
        )
        
        manager.add_memory(
            content="用户认证需要支持JWT和OAuth2",
            category="requirement",
            importance=0.8,
            tags=["认证", "需求"]
        )
        
        ai_memory = manager.get_current_state()['ai_memory']
        print(f"关键决策数量: {len(ai_memory['key_decisions'])}")
        print(f"上下文片段数量: {len(ai_memory['context_fragments'])}")
        
        # 测试4: 添加下一步建议
        print("\n4. 测试行动建议")
        manager.add_next_action(
            action_type="continue",
            description="实现JWT token生成和验证",
            command="aceflow implement jwt-auth",
            confidence=0.85
        )
        
        manager.add_next_action(
            action_type="parallel",
            description="并行设计用户数据模型",
            command="aceflow design user-model",
            confidence=0.75
        )
        
        state_declaration = manager.generate_state_declaration()
        print(f"下一步建议数量: {len(state_declaration['next_suggestions'])}")
        for suggestion in state_declaration['next_suggestions']:
            print(f"  - {suggestion['description']} (置信度: {suggestion['confidence']})")
        
        # 测试5: 状态声明
        print("\n5. 测试状态声明生成")
        declaration = manager.generate_state_declaration()
        print(f"当前任务: {declaration['current_task']}")
        print(f"进度: {declaration['progress'] * 100}%")
        print(f"记忆片段数量: {len(declaration['memory_fragments'])}")
        print(f"元认知信息: {declaration['meta_cognition']['current_understanding']}")
        
        # 测试6: 状态快照
        print("\n6. 测试状态快照")
        snapshot_name = manager.create_state_snapshot("test_snapshot")
        print(f"创建快照: {snapshot_name}")
        
        # 修改状态
        manager.update_state({
            'current_task': '测试用户认证功能',
            'task_progress': 0.6,
            'trigger': 'progress_update'
        })
        print(f"修改后任务: {manager.current_state.current_task}")
        
        # 从快照恢复
        success = manager.restore_from_snapshot(snapshot_name)
        print(f"快照恢复成功: {success}")
        print(f"恢复后任务: {manager.current_state.current_task}")
        
        # 测试7: 状态回滚
        print("\n7. 测试状态回滚")
        # 再次修改状态
        manager.update_state({
            'current_task': '部署认证服务',
            'task_progress': 0.8,
            'trigger': 'deployment'
        })
        print(f"修改前任务: {manager.current_state.current_task}")
        
        # 回滚
        rollback_success = manager.rollback_to_previous_state()
        print(f"回滚成功: {rollback_success}")
        print(f"回滚后任务: {manager.current_state.current_task}")
        
        # 测试8: 状态验证
        print("\n8. 测试状态完整性验证")
        validation = manager.validate_state_integrity()
        print(f"状态有效: {validation['valid']}")
        print(f"错误数量: {len(validation['errors'])}")
        print(f"警告数量: {len(validation['warnings'])}")
        print(f"记忆数量: {validation['memory_count']}")
        print(f"转换数量: {validation['transition_count']}")
        
        if validation['errors']:
            print("错误列表:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        if validation['warnings']:
            print("警告列表:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        print("\n=== 所有测试完成 ===")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == "__main__":
    success = test_state_tracking()
    sys.exit(0 if success else 1)