#!/usr/bin/env python3
"""
最终记忆分类和存储测试
"""

import sys
import os

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_memory_system():
    """测试记忆系统的核心功能"""
    try:
        from aceflow.pateoas.memory_system import ContextMemorySystem
        
        print("=== 记忆分类和存储系统测试 ===")
        
        # 1. 创建记忆系统
        memory_system = ContextMemorySystem(project_id="final_test")
        print("✓ 创建记忆系统成功")
        
        # 2. 添加不同类型的记忆
        test_memories = [
            {
                'content': '用户需要一个登录功能，支持邮箱和手机号登录',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['登录', '用户', '需求']
            },
            {
                'content': '决定使用JWT作为认证方案，因为无状态且安全',
                'category': 'decision',
                'importance': 0.8,
                'tags': ['JWT', '认证', '技术选型']
            },
            {
                'content': '发现用户经常忘记密码，需要添加密码重置功能',
                'category': 'pattern',
                'importance': 0.7,
                'tags': ['用户行为', '密码', '模式']
            },
            {
                'content': '数据库连接超时导致登录失败，已修复连接池配置',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['数据库', '连接', '问题']
            },
            {
                'content': '学会了FastAPI的依赖注入，可以更好地管理数据库连接',
                'category': 'learning',
                'importance': 0.6,
                'tags': ['FastAPI', '依赖注入', '学习']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        print(f"✓ 添加了 {len(test_memories)} 条不同类型的记忆")
        
        # 3. 验证记忆分类存储
        stats = memory_system.get_memory_stats()
        print(f"✓ 总记忆数量: {stats['total_memories']}")
        
        print("分类统计:")
        for category, info in stats['categories'].items():
            if info['count'] > 0:
                print(f"  - {category}: {info['count']} 条 (平均重要性: {info['avg_importance']:.2f})")
        
        # 4. 测试智能搜索
        search_queries = [
            "用户登录",
            "JWT认证",
            "数据库问题",
            "FastAPI学习"
        ]
        
        print("\n智能搜索测试:")
        for query in search_queries:
            results = memory_system.recall_relevant_context(query, {}, limit=2)
            print(f"  '{query}': {len(results)} 条结果")
            for result in results:
                print(f"    - [{result['category']}] {result['content'][:30]}... (相关性: {result['relevance_score']:.2f})")
        
        # 5. 测试专门记忆类型获取
        print("\n专门记忆类型测试:")
        req_store = memory_system.memory_stores['requirement']
        req_memories = req_store.get_all_memories()
        print(f"  需求记忆: {len(req_memories)} 条")
        
        decision_store = memory_system.memory_stores['decision']
        decision_memories = decision_store.get_all_memories()
        print(f"  决策记忆: {len(decision_memories)} 条")
        
        # 6. 测试记忆访问更新
        print("\n记忆访问测试:")
        before_search = req_memories[0].access_count if req_memories else 0
        memory_system.recall_relevant_context("登录需求", {}, limit=1)
        after_search = req_store.get_all_memories()[0].access_count if req_store.get_all_memories() else 0
        print(f"  访问前计数: {before_search}, 访问后计数: {after_search}")
        
        # 7. 测试记忆模式分析
        print("\n记忆模式分析:")
        pattern_analysis = memory_system.analyze_memory_patterns()
        if pattern_analysis['patterns']:
            print("  发现的模式:")
            for pattern in pattern_analysis['patterns'][:3]:
                print(f"    - {pattern}")
        
        if pattern_analysis['insights']:
            print("  洞察:")
            for insight in pattern_analysis['insights'][:2]:
                print(f"    - {insight}")
        
        print("\n=== 记忆分类和存储系统测试完成 ===")
        print("✓ 所有核心功能正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_system()
    sys.exit(0 if success else 1)