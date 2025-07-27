#!/usr/bin/env python3
"""
简化的记忆系统测试
"""

import sys
import os

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

try:
    from aceflow.pateoas.memory_system import ContextMemorySystem
    print("✓ 成功导入 ContextMemorySystem")
    
    # 创建记忆系统实例
    memory_system = ContextMemorySystem(project_id="simple_test")
    print("✓ 成功创建记忆系统实例")
    
    # 添加一些测试记忆
    test_memories = [
        {
            'content': '用户需要登录功能',
            'category': 'requirement',
            'importance': 0.9,
            'tags': ['登录', '需求']
        },
        {
            'content': '选择JWT认证方案',
            'category': 'decision',
            'importance': 0.8,
            'tags': ['JWT', '认证']
        }
    ]
    
    for memory_data in test_memories:
        memory_system.add_memory(**memory_data)
        print(f"✓ 添加记忆: {memory_data['content'][:20]}...")
    
    # 获取统计信息
    stats = memory_system.get_memory_stats()
    print(f"✓ 总记忆数量: {stats['total_memories']}")
    
    # 测试搜索
    results = memory_system.recall_relevant_context("登录", {}, limit=2)
    print(f"✓ 搜索结果数量: {len(results)}")
    
    for result in results:
        print(f"  - [{result['category']}] {result['content'][:30]}...")
    
    print("\n=== 简化记忆系统测试成功 ===")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)