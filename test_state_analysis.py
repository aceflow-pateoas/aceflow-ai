#!/usr/bin/env python3
"""
测试状态连续性管理器的高级分析功能
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


def test_advanced_state_analysis():
    """测试高级状态分析功能"""
    print("=== 测试状态分析功能 ===")
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp()
    print(f"使用临时目录: {temp_dir}")
    
    try:
        # 初始化状态管理器
        manager = StateContinuityManager(project_id="analysis_test")
        
        # 模拟一系列状态变化
        print("\n1. 模拟项目开发过程")
        
        # 阶段1: 需求分析
        manager.update_state({
            'current_task': '需求分析',
            'task_progress': 0.2,
            'stage_context': {
                'current_stage': 'S1',
                'workflow_mode': 'standard'
            },
            'trigger': 'stage_start',
            'reasoning': '开始需求分析阶段'
        })
        
        manager.add_memory(
            content="客户需要一个电商系统，支持用户注册、商品浏览、购物车和支付",
            category="requirement",
            importance=0.9,
            tags=["电商", "核心需求"]
        )
        
        # 阶段2: 技术选型
        manager.update_state({
            'current_task': '技术架构设计',
            'task_progress': 0.4,
            'stage_context': {
                'current_stage': 'S2',
                'technology_stack': ['python', 'fastapi', 'postgresql', 'redis']
            },
            'trigger': 'progress_update',
            'reasoning': '完成需求分析，开始技术设计'
        })
        
        manager.add_memory(
            content="选择FastAPI作为后端框架，PostgreSQL作为主数据库，Redis用于缓存",
            category="decision",
            importance=0.8,
            tags=["技术选型", "架构"]
        )
        
        # 阶段3: 开发实现
        manager.update_state({
            'current_task': '用户认证模块开发',
            'task_progress': 0.6,
            'stage_context': {
                'current_stage': 'S4',
                'pending_tasks': ['用户注册', 'JWT认证', '权限管理']
            },
            'trigger': 'implementation_start',
            'reasoning': '开始核心模块开发'
        })
        
        manager.add_memory(
            content="实现JWT认证时遇到token过期处理问题，需要添加刷新token机制",
            category="issue",
            importance=0.7,
            tags=["认证", "技术问题"]
        )
        
        # 阶段4: 测试优化
        manager.update_state({
            'current_task': '系统测试和优化',
            'task_progress': 0.8,
            'stage_context': {
                'current_stage': 'S5',
                'completed_stages': ['S1', 'S2', 'S3', 'S4']
            },
            'trigger': 'testing_phase',
            'reasoning': '进入测试优化阶段'
        })
        
        manager.add_memory(
            content="发现用户在高并发情况下登录响应较慢，需要优化数据库查询",
            category="pattern",
            importance=0.6,
            tags=["性能", "优化"]
        )
        
        # 测试状态模式分析
        print("\n2. 测试状态模式分析")
        patterns = manager.analyze_state_patterns()
        
        print(f"识别的模式: {patterns['patterns']}")
        print(f"发展趋势: {patterns['trends']}")
        print(f"洞察建议: {patterns['insights']}")
        print(f"统计信息:")
        for key, value in patterns['statistics'].items():
            print(f"  - {key}: {value}")
        
        # 测试状态时间线
        print("\n3. 测试状态时间线")
        timeline = manager.get_state_timeline(limit=10)
        
        print(f"时间线事件数量: {len(timeline)}")
        for i, event in enumerate(timeline[-3:]):  # 显示最近3个事件
            print(f"事件 {i+1}:")
            print(f"  时间: {event['timestamp']}")
            print(f"  触发: {event['trigger']}")
            print(f"  原因: {event['reasoning']}")
            if event['changes']:
                print(f"  变化: {event['changes']}")
        
        # 测试状态摘要导出
        print("\n4. 测试状态摘要导出")
        summary = manager.export_state_summary()
        
        print("项目信息:")
        for key, value in summary['project_info'].items():
            print(f"  - {key}: {value}")
        
        print("记忆摘要:")
        for key, value in summary['memory_summary'].items():
            print(f"  - {key}: {value}")
        
        print("活动摘要:")
        for key, value in summary['activity_summary'].items():
            print(f"  - {key}: {value}")
        
        print("AI状态:")
        for key, value in summary['ai_status'].items():
            print(f"  - {key}: {value}")
        
        # 测试状态完整性验证（增强版）
        print("\n5. 测试状态完整性验证")
        validation = manager.validate_state_integrity()
        
        print(f"状态有效性: {validation['valid']}")
        print(f"记忆数量: {validation['memory_count']}")
        print(f"转换数量: {validation['transition_count']}")
        
        if validation['errors']:
            print("发现错误:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        if validation['warnings']:
            print("警告信息:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        # 测试状态清理功能
        print("\n6. 测试状态清理功能")
        print(f"清理前转换记录数: {len(manager.current_state.transition_history)}")
        
        # 添加更多转换记录来测试清理
        for i in range(5):
            manager.update_state({
                'task_progress': 0.8 + i * 0.01,
                'trigger': f'minor_update_{i}',
                'reasoning': f'小幅更新 {i}'
            })
        
        print(f"添加记录后转换数: {len(manager.current_state.transition_history)}")
        
        # 清理旧记录
        manager.cleanup_old_transitions(keep_count=5)
        print(f"清理后转换记录数: {len(manager.current_state.transition_history)}")
        
        # 测试记忆分类统计
        print("\n7. 测试记忆分类统计")
        memory_stats = manager._get_memory_category_stats()
        avg_importance = manager._get_average_memory_importance()
        
        print("记忆分类统计:")
        for category, count in memory_stats.items():
            print(f"  - {category}: {count}")
        print(f"平均重要性: {avg_importance:.2f}")
        
        # 测试状态变化分析
        print("\n8. 测试状态变化分析")
        if len(manager.current_state.transition_history) >= 2:
            last_transition = manager.current_state.transition_history[-1]
            changes = manager._analyze_state_changes(
                last_transition.from_state, 
                last_transition.to_state
            )
            print(f"最近状态变化: {changes}")
        
        print("\n=== 高级状态分析测试完成 ===")
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
    success = test_advanced_state_analysis()
    sys.exit(0 if success else 1)