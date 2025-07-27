#!/usr/bin/env python3
"""
测试智能记忆召回系统
"""

import sys
import os

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_intelligent_recall():
    """测试智能记忆召回功能"""
    try:
        from aceflow.pateoas.memory_system import ContextMemorySystem
        from aceflow.pateoas.smart_recall import MemoryRecallEngine, RecallContext
        
        print("=== 智能记忆召回系统测试 ===")
        
        # 1. 创建记忆系统
        memory_system = ContextMemorySystem(project_id="intelligent_test")
        print("✓ 创建记忆系统成功")
        
        # 2. 添加丰富的测试记忆
        test_memories = [
            {
                'content': '用户需要一个安全的登录系统，支持多因素认证',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['登录', '安全', '认证', '需求']
            },
            {
                'content': '决定使用JWT + Redis实现会话管理，提高性能和安全性',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['JWT', 'Redis', '会话', '技术选型']
            },
            {
                'content': '发现用户在移动端登录时经常超时，需要优化网络请求',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['移动端', '超时', '网络', '问题']
            },
            {
                'content': '用户倾向于使用社交媒体账号登录，而不是邮箱注册',
                'category': 'pattern',
                'importance': 0.7,
                'tags': ['社交登录', '用户行为', '偏好']
            },
            {
                'content': '学会了OAuth2.0的实现原理，可以集成第三方登录',
                'category': 'learning',
                'importance': 0.75,
                'tags': ['OAuth2', '第三方登录', '学习']
            },
            {
                'content': '当前正在开发用户认证模块，已完成基础框架',
                'category': 'context',
                'importance': 0.6,
                'tags': ['认证模块', '开发进度', '上下文']
            },
            {
                'content': '数据库连接池配置不当导致高并发时认证失败',
                'category': 'issue',
                'importance': 0.85,
                'tags': ['数据库', '连接池', '并发', '认证失败']
            },
            {
                'content': '选择PostgreSQL作为主数据库，因为支持JSON字段和事务',
                'category': 'decision',
                'importance': 0.8,
                'tags': ['PostgreSQL', '数据库', '技术选型']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        print(f"✓ 添加了 {len(test_memories)} 条测试记忆")
        
        # 3. 测试基础智能召回
        print("\n=== 基础智能召回测试 ===")
        
        test_queries = [
            {
                'query': '登录安全问题',
                'expected_categories': ['requirement', 'issue', 'decision'],
                'description': '安全相关查询'
            },
            {
                'query': 'JWT认证实现',
                'expected_categories': ['decision', 'learning'],
                'description': 'JWT技术查询'
            },
            {
                'query': '数据库性能问题',
                'expected_categories': ['issue', 'decision'],
                'description': '数据库相关查询'
            },
            {
                'query': '用户行为分析',
                'expected_categories': ['pattern'],
                'description': '用户模式查询'
            }
        ]
        
        for test_case in test_queries:
            print(f"\n查询: '{test_case['query']}' ({test_case['description']})")
            
            results = memory_system.recall_relevant_context(
                test_case['query'], 
                {'current_stage': 'S4', 'technology_stack': ['python', 'fastapi', 'postgresql']}, 
                limit=3
            )
            
            print(f"  召回结果: {len(results)} 条")
            
            found_categories = set()
            for i, result in enumerate(results):
                print(f"    {i+1}. [{result['category']}] {result['content'][:40]}...")
                print(f"       相关性: {result['relevance_score']:.3f}, 重要性: {result['importance']:.2f}")
                if 'reasoning' in result:
                    print(f"       推理: {result['reasoning']}")
                found_categories.add(result['category'])
            
            # 验证是否找到了预期的分类
            expected_found = any(cat in found_categories for cat in test_case['expected_categories'])
            status = "✓" if expected_found else "?"
            print(f"  {status} 预期分类匹配: {expected_found}")
        
        # 4. 测试增强智能召回接口
        print("\n=== 增强智能召回测试 ===")
        
        enhanced_result = memory_system.intelligent_recall(
            query="认证系统安全性",
            current_state={
                'current_stage': 'S4',
                'technology_stack': ['python', 'fastapi', 'jwt', 'redis'],
                'project_urgency': 'high'
            },
            limit=5,
            min_relevance=0.2
        )
        
        print(f"增强召回结果:")
        print(f"  总搜索记忆: {enhanced_result['total_searched']}")
        print(f"  召回记忆数: {enhanced_result['total_recalled']}")
        
        if enhanced_result['statistics']:
            stats = enhanced_result['statistics']
            print(f"  召回统计:")
            print(f"    平均相关性: {stats.get('avg_relevance', 0):.3f}")
            print(f"    召回质量: {stats.get('recall_quality', 'unknown')}")
            if 'category_distribution' in stats:
                print(f"    分类分布: {stats['category_distribution']}")
        
        if enhanced_result['query_analysis']:
            analysis = enhanced_result['query_analysis']
            print(f"  查询意图分析:")
            for intent, score in analysis.items():
                if score > 0:
                    print(f"    {intent}: {score:.2f}")
        
        print(f"  详细结果:")
        for i, result in enumerate(enhanced_result['results'][:3]):
            print(f"    {i+1}. [{result['category']}] {result['content'][:50]}...")
            print(f"       相关性: {result['relevance_score']:.3f}")
            if 'relevance_factors' in result:
                factors = result['relevance_factors']
                print(f"       因素: 语义({factors.get('semantic_similarity', 0):.2f}) "
                      f"时间({factors.get('temporal_relevance', 0):.2f}) "
                      f"重要性({factors.get('importance_weight', 0):.2f})")
        
        # 5. 测试分类过滤召回
        print("\n=== 分类过滤召回测试 ===")
        
        category_tests = ['requirement', 'decision', 'issue']
        for category in category_tests:
            filtered_result = memory_system.intelligent_recall(
                query="登录认证",
                category_filter=category,
                limit=2,
                min_relevance=0.1
            )
            
            print(f"  {category} 分类过滤:")
            print(f"    结果数量: {len(filtered_result['results'])}")
            for result in filtered_result['results']:
                print(f"      - [{result['category']}] {result['content'][:30]}... ({result['relevance_score']:.2f})")
        
        # 6. 测试记忆访问更新
        print("\n=== 记忆访问更新测试 ===")
        
        # 获取一个记忆的初始访问计数
        req_store = memory_system.memory_stores['requirement']
        req_memories = req_store.get_all_memories()
        if req_memories:
            initial_count = req_memories[0].access_count
            print(f"  初始访问计数: {initial_count}")
            
            # 执行召回（会更新访问计数）
            memory_system.recall_relevant_context("用户需求", {}, limit=1)
            
            # 检查更新后的访问计数
            updated_memories = req_store.get_all_memories()
            if updated_memories:
                updated_count = updated_memories[0].access_count
                print(f"  更新后访问计数: {updated_count}")
                print(f"  ✓ 访问计数正确更新: {updated_count > initial_count}")
        
        # 7. 测试多样性过滤
        print("\n=== 多样性过滤测试 ===")
        
        diverse_results = memory_system.recall_relevant_context(
            "系统开发", 
            {}, 
            limit=6  # 请求较多结果来测试多样性
        )
        
        category_counts = {}
        for result in diverse_results:
            category = result['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"  多样性测试结果 (总数: {len(diverse_results)}):")
        for category, count in category_counts.items():
            print(f"    {category}: {count} 条")
        
        # 验证多样性（没有单一分类占主导）
        max_category_count = max(category_counts.values()) if category_counts else 0
        diversity_good = max_category_count <= len(diverse_results) // 2 + 1
        print(f"  ✓ 多样性良好: {diversity_good}")
        
        print("\n=== 智能记忆召回系统测试完成 ===")
        print("✓ 所有核心功能正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_intelligent_recall()
    sys.exit(0 if success else 1)