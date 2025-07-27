#!/usr/bin/env python3
"""
调试记忆搜索功能
"""

import sys
import os

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

try:
    from aceflow.pateoas.memory_system import ContextMemorySystem
    from aceflow.pateoas.utils import calculate_similarity
    
    print("=== 调试记忆搜索功能 ===")
    
    # 创建记忆系统实例
    memory_system = ContextMemorySystem(project_id="debug_test")
    
    # 添加测试记忆
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
        print(f"添加记忆: {memory_data['content']}")
    
    # 检查记忆是否正确存储
    print(f"\n记忆存储检查:")
    for category, store in memory_system.memory_stores.items():
        memories = store.get_all_memories()
        print(f"  {category}: {len(memories)} 条记忆")
        for memory in memories:
            print(f"    - {memory.content}")
    
    # 测试相似度计算
    print(f"\n相似度测试:")
    query = "登录"
    for category, store in memory_system.memory_stores.items():
        memories = store.get_all_memories()
        for memory in memories:
            similarity = calculate_similarity(query, memory.content)
            print(f"  '{query}' vs '{memory.content}': {similarity:.3f}")
    
    # 测试单个存储器的搜索
    print(f"\n单个存储器搜索测试:")
    req_store = memory_system.memory_stores['requirement']
    req_results = req_store.search_similar("登录", {}, limit=5)
    print(f"需求存储器搜索结果: {len(req_results)} 条")
    for result in req_results:
        print(f"  - {result.content}")
    
    # 测试完整搜索
    print(f"\n完整搜索测试:")
    results = memory_system.recall_relevant_context("登录", {}, limit=5)
    print(f"完整搜索结果: {len(results)} 条")
    for result in results:
        print(f"  - [{result['category']}] {result['content']}")
    
    print("\n=== 调试完成 ===")
    
except Exception as e:
    print(f"调试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)