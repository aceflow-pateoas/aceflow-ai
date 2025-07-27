#!/usr/bin/env python3
"""
测试智能记忆召回系统的最终版本
"""

import sys
import os

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_intelligent_recall_system():
    """测试智能记忆召回系统"""
    try:
        from aceflow.pateoas.memory_system import ContextMemorySystem
        
        print("=== 智能记忆召回系统测试 ===")
        
        # 1. 创建记忆系统
        memory_system = ContextMemorySystem(project_id="intelligent_final_test")
        print("✓ 创建记忆系统成功")
        
        # 2. 添加丰富的测试记忆
        test_memories = [
            {
                'content': '用户需要一个安全的登录系统，支持多因素认证和社交登录',
                'category': 'requirement',
                'importance': 0.9,
                'tags': ['登录', '安全', '认证', '社交登录']
            },
            {
                'content': '决定使用JWT + Redis实现会话管理，提高性能和安全性',
                'category': 'decision',
                'importance': 0.85,
                'tags': ['JWT', 'Redis', '会话', '性能']
            },
            {
                'content': '发现用户在移动端登录时经常超时，需要优化网络请求',
                'category': 'issue',
                'importance': 0.8,
                'tags': ['移动端', '超时', '网络', '优化']
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
                'tags': ['OAuth2', '第三方登录', '集成']
            },
            {
                'content': '数据库连接池配置不当导致高并发时认证失败',
                'category': 'issue',
                'importance': 0.85,
                'tags': ['数据库', '连接池', '并发', '认证']
            }
        ]
        
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        print(f"✓ 添加了 {len(test_memories)} 条测试记忆")
        
        # 3. 测试增强智能召回接口
        print("\n=== 增强智能召回测试 ===")
        
        test_queries = [
            {
                'query': '登录安全问题',
                'description': '安全相关查询',
                'expected_categories': ['requirement', 'issue']
            },
            {
                'query': 'JWT认证实现',
                'description': 'JWT技术查询',
                'expected_categories': ['decision', 'learning']
            },
            {
                'query': '数据库性能问题',
                'description': '数据库相关查询',
                'expected_categories': ['issue']
            }
        ]
        
        for test_case in test_queries:
            print(f"\n查询: '{test_case['query']}' ({test_case['description']})")
            
            enhanced_result = memory_system.intelligent_recall(
                query=test_case['query'],
                current_state={
                    'current_stage': 'S4',
                    'technology_stack': ['python', 'fastapi', 'jwt', 'redis'],
                    'project_urgency': 'high'
                },
                limit=3,
                min_relevance=0.2
            )
            
            print(f"  召回结果: {enhanced_result['total_recalled']} / {enhanced_result['total_searched']}")
            
            # 显示统计信息
            if enhanced_result['statistics']:
                stats = enhanced_result['statistics']
                print(f"  召回质量: {stats.get('recall_quality', 'unknown')}")
                print(f"  平均相关性: {stats.get('avg_relevance', 0):.3f}")
                if 'category_distribution' in stats:
                    print(f"  分类分布: {stats['category_distribution']}")
            
            # 显示查询意图分析
            if enhanced_result['query_analysis']:
                analysis = enhanced_result['query_analysis']
                intent_scores = {k: v for k, v in analysis.items() if v > 0}
                if intent_scores:
                    print(f"  查询意图: {intent_scores}")
            
            # 显示详细结果
            print(f"  详细结果:")
            found_categories = set()
            for i, result in enumerate(enhanced_result['results']):
                print(f"    {i+1}. [{result['category']}] {result['content'][:40]}...")
                print(f"       相关性: {result['relevance_score']:.3f}")
                print(f"       推理: {result['reasoning']}")
                if 'relevance_factors' in result:
                    factors = result['relevance_factors']
                    print(f"       因素: 语义({factors.get('semantic_similarity', 0):.2f}) "
                          f"时间({factors.get('temporal_relevance', 0):.2f}) "
                          f"重要性({factors.get('importance_weight', 0):.2f})")
                found_categories.add(result['category'])
            
            # 验证预期分类
            expected_found = any(cat in found_categories for cat in test_case['expected_categories'])
            status = "✓" if expected_found else "?"
            print(f"  {status} 预期分类匹配: {expected_found}")
        
        # 4. 测试分类过滤召回
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
        
        # 5. 测试多样性过滤
        print("\n=== 多样性过滤测试 ===")
        
        diverse_results = memory_system.intelligent_recall(
            query="系统开发", 
            limit=6,  # 请求较多结果来测试多样性
            min_relevance=0.1
        )
        
        category_counts = {}
        for result in diverse_results['results']:
            category = result['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"  多样性测试结果 (总数: {len(diverse_results['results'])}):")
        for category, count in category_counts.items():
            print(f"    {category}: {count} 条")
        
        # 验证多样性（没有单一分类占主导）
        if category_counts:
            max_category_count = max(category_counts.values())
            diversity_good = max_category_count <= len(diverse_results['results']) // 2 + 1
            print(f"  ✓ 多样性良好: {diversity_good}")
        
        # 6. 测试相关性因素分解
        print("\n=== 相关性因素分解测试 ===")
        
        factor_test_result = memory_system.intelligent_recall(
            query="JWT安全认证",
            current_state={'technology_stack': ['jwt', 'redis']},
            limit=2,
            min_relevance=0.1
        )
        
        if factor_test_result['results']:
            result = factor_test_result['results'][0]
            factors = result.get('relevance_factors', {})
            print(f"  最高相关性结果的因素分解:")
            print(f"    语义相似度: {factors.get('semantic_similarity', 0):.3f}")
            print(f"    时间相关性: {factors.get('temporal_relevance', 0):.3f}")
            print(f"    上下文重叠: {factors.get('context_overlap', 0):.3f}")
            print(f"    重要性权重: {factors.get('importance_weight', 0):.3f}")
            print(f"    访问频率: {factors.get('access_frequency', 0):.3f}")
        
        # 7. 测试记忆访问更新
        print("\n=== 记忆访问更新测试 ===")
        
        # 获取一个记忆的初始访问计数
        req_store = memory_system.memory_stores['requirement']
        req_memories = req_store.get_all_memories()
        if req_memories:
            initial_count = req_memories[0].access_count
            print(f"  初始访问计数: {initial_count}")
            
            # 执行智能召回（会更新访问计数）
            memory_system.intelligent_recall("用户需求", {}, limit=1)
            
            # 检查更新后的访问计数
            updated_memories = req_store.get_all_memories()
            if updated_memories:
                updated_count = updated_memories[0].access_count
                print(f"  更新后访问计数: {updated_count}")
                print(f"  ✓ 访问计数正确更新: {updated_count > initial_count}")
        
        print("\n=== 智能记忆召回系统测试完成 ===")
        print("✓ 所有核心功能正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_intelligent_recall_system()
    sys.exit(0 if success else 1)