#!/usr/bin/env python3
"""
测试增强的状态声明生成功能
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

from aceflow.pateoas.state_manager import StateContinuityManager
from aceflow.pateoas.models import MemoryCategory, ActionType


def test_enhanced_state_declaration():
    """测试增强的状态声明生成功能"""
    print("=== 测试增强状态声明生成 ===")
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp()
    print(f"使用临时目录: {temp_dir}")
    
    try:
        # 初始化状态管理器
        manager = StateContinuityManager(project_id="declaration_test")
        
        # 设置复杂的项目状态
        print("\n1. 设置复杂项目状态")
        manager.update_state({
            'current_task': '电商系统用户认证模块开发',
            'task_progress': 0.65,
            'stage_context': {
                'current_stage': 'S4',
                'workflow_mode': 'standard',
                'technology_stack': ['python', 'fastapi', 'postgresql', 'redis', 'jwt'],
                'complexity_level': 'high',
                'team_size': 3,
                'completed_stages': ['S1', 'S2', 'S3'],
                'pending_tasks': ['JWT实现', '权限管理', '密码加密', '用户注册API']
            },
            'active_context': {
                'current_module': 'authentication',
                'last_commit': 'feat: add user model',
                'environment': 'development'
            },
            'trigger': 'development_progress',
            'reasoning': '正在开发核心认证功能'
        })
        
        # 添加丰富的记忆
        print("2. 添加项目记忆")
        memories = [
            {
                'content': '客户要求支持JWT认证和OAuth2登录，需要高安全性',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['认证', '安全', '需求']
            },
            {
                'content': '选择FastAPI框架，因为性能优秀且支持异步处理',
                'category': 'decision',
                'importance': 0.8,
                'tags': ['框架', '技术选型']
            },
            {
                'content': '用户密码必须使用bcrypt加密存储',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['安全', '密码', '加密']
            },
            {
                'content': 'JWT token过期时间设置为24小时，refresh token为7天',
                'category': 'decision',
                'importance': 0.7,
                'tags': ['JWT', '配置']
            },
            {
                'content': '发现PostgreSQL连接池配置不当导致性能问题',
                'category': 'issue',
                'importance': 0.75,
                'tags': ['数据库', '性能', '问题']
            },
            {
                'content': '用户在高并发情况下登录响应时间超过2秒',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['性能', '并发', '登录']
            },
            {
                'content': '发现用户倾向于使用邮箱而非用户名登录',
                'category': 'pattern',
                'importance': 0.6,
                'tags': ['用户行为', '登录方式']
            },
            {
                'content': '学会了FastAPI的依赖注入机制，可以优化代码结构',
                'category': 'learning',
                'importance': 0.7,
                'tags': ['FastAPI', '依赖注入', '学习']
            }
        ]
        
        for memory_data in memories:
            manager.add_memory(**memory_data)
        
        # 添加一些行动建议
        print("3. 添加行动建议")
        manager.add_next_action(
            action_type="continue",
            description="完成JWT token生成和验证逻辑",
            command="aceflow implement jwt-auth --secure",
            confidence=0.85
        )
        
        manager.add_next_action(
            action_type="parallel",
            description="并行开发用户权限管理系统",
            command="aceflow implement permissions --parallel",
            confidence=0.75
        )
        
        # 生成增强状态声明
        print("\n4. 生成增强状态声明")
        declaration = manager.generate_state_declaration()
        
        # 详细展示状态声明内容
        print("\n=== 状态声明详细内容 ===")
        
        print(f"\n📋 基本信息:")
        print(f"  当前任务: {declaration['current_task']}")
        print(f"  进度: {declaration['progress'] * 100:.1f}%")
        print(f"  状态ID: {declaration['state_id']}")
        print(f"  时间戳: {declaration['timestamp']}")
        
        print(f"\n🏗️ 阶段信息:")
        stage_info = declaration['stage_info']
        print(f"  当前阶段: {stage_info['current_stage']}")
        print(f"  工作流模式: {stage_info['workflow_mode']}")
        print(f"  已完成阶段: {', '.join(stage_info['completed_stages'])}")
        print(f"  待办任务: {', '.join(stage_info['pending_tasks'][:3])}...")
        
        print(f"\n🧠 记忆片段 (前5个):")
        for i, memory in enumerate(declaration['memory_fragments'][:5]):
            print(f"  {i+1}. [{memory['category']}] {memory['content'][:50]}...")
            print(f"     重要性: {memory['importance']:.2f}, 相关性: {memory['relevance_score']:.2f}")
            print(f"     标签: {', '.join(memory['tags'])}")
        
        print(f"\n📊 上下文摘要:")
        context = declaration['context_summary']
        print(f"  项目类型: {context['project_type']}")
        print(f"  技术栈: {context['technology_summary']}")
        print(f"  当前焦点: {context['current_focus']}")
        print(f"  复杂度: {context['complexity_assessment']['level']} (分数: {context['complexity_assessment']['score']:.2f})")
        
        if context['risk_factors']:
            print(f"  风险因素:")
            for risk in context['risk_factors']:
                print(f"    - {risk}")
        
        if context['opportunities']:
            print(f"  机会点:")
            for opp in context['opportunities']:
                print(f"    - {opp}")
        
        print(f"\n🎯 智能建议 (前3个):")
        for i, suggestion in enumerate(declaration['next_suggestions'][:3]):
            print(f"  {i+1}. [{suggestion['action_type']}] {suggestion['description']}")
            print(f"     命令: {suggestion['command']}")
            print(f"     置信度: {suggestion['confidence']:.2f}, 预计时间: {suggestion['estimated_time']}")
            if suggestion.get('auto_generated'):
                print(f"     (AI自动生成)")
        
        print(f"\n🔄 替代路径:")
        for i, alt in enumerate(declaration['alternative_paths']):
            print(f"  {i+1}. [{alt['path_type']}] {alt['description']}")
            print(f"     理由: {alt['rationale']}")
            print(f"     时间节省: {alt['estimated_time_saving']}, 风险: {alt['risk_level']}")
        
        print(f"\n🤖 增强元认知:")
        meta = declaration['meta_cognition']
        print(f"  当前理解: {meta['current_understanding']}")
        print(f"  置信度: {meta['confidence_level']:.2f}")
        print(f"  记忆利用: {meta['memory_utilization']}")
        print(f"  上下文完整性: {meta['context_completeness']:.2f}")
        
        if meta['knowledge_gaps']:
            print(f"  知识缺口:")
            for gap in meta['knowledge_gaps']:
                print(f"    - {gap}")
        
        if meta['learning_opportunities']:
            print(f"  学习机会:")
            for opp in meta['learning_opportunities']:
                print(f"    - {opp}")
        
        print(f"\n💊 状态健康:")
        health = declaration['state_health']
        print(f"  总体健康: {health['overall_health']}")
        print(f"  健康分数: {health['health_score']:.2f}")
        print(f"  健康因素:")
        for factor, status in health['health_factors'].items():
            print(f"    - {factor}: {status}")
        
        if health['recommendations']:
            print(f"  建议:")
            for rec in health['recommendations']:
                print(f"    - {rec}")
        
        # 测试状态声明的JSON序列化
        print(f"\n5. 测试JSON序列化")
        try:
            json_str = json.dumps(declaration, ensure_ascii=False, indent=2)
            print(f"JSON序列化成功，长度: {len(json_str)} 字符")
            
            # 验证可以反序列化
            parsed = json.loads(json_str)
            print(f"JSON反序列化成功，包含 {len(parsed)} 个顶级字段")
            
        except Exception as e:
            print(f"JSON序列化失败: {e}")
        
        # 测试状态声明的完整性
        print(f"\n6. 验证状态声明完整性")
        required_fields = [
            'current_task', 'progress', 'stage_info', 'memory_fragments',
            'context_summary', 'next_suggestions', 'alternative_paths',
            'meta_cognition', 'state_health', 'timestamp', 'state_id'
        ]
        
        missing_fields = [field for field in required_fields if field not in declaration]
        if missing_fields:
            print(f"缺少字段: {missing_fields}")
        else:
            print("所有必需字段都存在 ✓")
        
        # 验证数据质量
        print(f"\n7. 验证数据质量")
        quality_checks = {
            '记忆片段数量': len(declaration['memory_fragments']) >= 5,
            '智能建议数量': len(declaration['next_suggestions']) >= 3,
            '上下文摘要完整': all(key in declaration['context_summary'] for key in ['project_type', 'current_focus']),
            '元认知信息完整': 'knowledge_gaps' in declaration['meta_cognition'],
            '健康评估完整': 'overall_health' in declaration['state_health']
        }
        
        for check, passed in quality_checks.items():
            status = "✓" if passed else "✗"
            print(f"  {check}: {status}")
        
        all_passed = all(quality_checks.values())
        print(f"\n数据质量检查: {'全部通过' if all_passed else '部分失败'}")
        
        print("\n=== 增强状态声明测试完成 ===")
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
    success = test_enhanced_state_declaration()
    sys.exit(0 if success else 1)