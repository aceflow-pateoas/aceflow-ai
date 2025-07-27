#!/usr/bin/env python3
"""
测试记忆分类和存储系统
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加 aceflow 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

from aceflow.pateoas.memory_system import ContextMemorySystem
from aceflow.pateoas.memory_categories import (
    RequirementsMemory, DecisionMemory, PatternMemory, 
    IssueMemory, LearningMemory, ContextMemory
)
from aceflow.pateoas.models import MemoryFragment, MemoryCategory


def test_memory_categorization_and_storage():
    """测试记忆分类和存储功能"""
    print("=== 测试记忆分类和存储系统 ===")
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp()
    print(f"使用临时目录: {temp_dir}")
    
    try:
        # 初始化记忆系统
        memory_system = ContextMemorySystem(project_id="categorization_test")
        
        # 测试1: 基本记忆存储和分类
        print("\n1. 测试基本记忆存储和分类")
        
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
            },
            {
                'content': '当前正在开发用户认证模块，进度60%',
                'category': 'context',
                'importance': 0.5,
                'tags': ['认证', '进度', '上下文']
            }
        ]
        
        # 添加测试记忆
        for memory_data in test_memories:
            memory_system.add_memory(**memory_data)
        
        # 验证记忆分类存储
        stats = memory_system.get_memory_stats()
        print(f"总记忆数量: {stats['total_memories']}")
        print("分类统计:")
        for category, info in stats['categories'].items():
            print(f"  - {category}: {info['count']} 条 (平均重要性: {info['avg_importance']:.2f})")
        
        # 测试2: 专门存储器功能
        print("\n2. 测试专门存储器功能")
        
        # 测试需求记忆存储器
        req_store = memory_system.memory_stores['requirements']
        req_memories = req_store.get_all_memories()
        print(f"需求记忆数量: {len(req_memories)}")
        
        functional_reqs = req_store.get_functional_requirements()
        print(f"功能性需求: {len(functional_reqs)}")
        
        # 测试决策记忆存储器
        decision_store = memory_system.memory_stores['decisions']
        decision_memories = decision_store.get_all_memories()
        print(f"决策记忆数量: {len(decision_memories)}")
        
        tech_decisions = decision_store.get_technical_decisions()
        print(f"技术决策: {len(tech_decisions)}")
        
        # 测试问题记忆存储器
        issue_store = memory_system.memory_stores['issues']
        issue_memories = issue_store.get_all_memories()
        print(f"问题记忆数量: {len(issue_memories)}")
        
        resolved_issues = issue_store.get_resolved_issues()
        open_issues = issue_store.get_open_issues()
        print(f"已解决问题: {len(resolved_issues)}, 未解决问题: {len(open_issues)}")
        
        # 测试3: 智能搜索功能
        print("\n3. 测试智能搜索功能")
        
        search_queries = [
            "用户登录功能",
            "JWT认证方案",
            "数据库连接问题",
            "FastAPI学习经验"
        ]
        
        for query in search_queries:
            print(f"\n搜索: '{query}'")
            results = memory_system.recall_relevant_context(
                query, 
                {'project_id': 'categorization_test'}, 
                limit=3
            )
            
            for i, result in enumerate(results):
                print(f"  {i+1}. [{result['category']}] {result['content'][:50]}...")
                print(f"     相关性: {result['relevance_score']:.2f}, 重要性: {result['importance']:.2f}")
        
        # 测试4: 记忆相似性检测
        print("\n4. 测试记忆相似性检测")
        
        # 尝试添加相似的需求记忆
        similar_req = {
            'content': '用户需要登录功能，要支持邮箱登录',
            'category': 'requirement',
            'importance': 0.85,
            'tags': ['登录', '邮箱', '需求']
        }
        
        before_count = len(req_store.get_all_memories())
        memory_system.add_memory(**similar_req)
        after_count = len(req_store.get_all_memories())
        
        print(f"添加相似需求前: {before_count} 条")
        print(f"添加相似需求后: {after_count} 条")
        if after_count == before_count:
            print("✓ 相似记忆被合并，避免了重复")
        else:
            print("✗ 相似记忆未被检测")
        
        # 测试5: 记忆访问和更新
        print("\n5. 测试记忆访问和更新")
        
        # 搜索会更新访问记录
        search_results = memory_system.recall_relevant_context("JWT认证", {}, limit=1)
        if search_results:
            # 再次获取该记忆，检查访问计数
            jwt_memories = decision_store.search_similar("JWT", {}, limit=1)
            if jwt_memories:
                print(f"JWT记忆访问次数: {jwt_memories[0].access_count}")
                print(f"最后访问时间: {jwt_memories[0].last_accessed}")
        
        # 测试6: 专门记忆类型获取
        print("\n6. 测试专门记忆类型获取")
        
        specialized_types = [
            ('requirements', {'functional_only': True}),
            ('decisions', {'technical_only': True}),
            ('patterns', {'code_only': False}),
            ('issues', {'resolved_only': True}),
            ('learning', {'technical_only': True}),
            ('context', {'hours': 24})
        ]
        
        for memory_type, kwargs in specialized_types:
            specialized_memories = memory_system.get_specialized_memories(memory_type, **kwargs)
            print(f"{memory_type} ({kwargs}): {len(specialized_memories)} 条")
        
        # 测试7: 记忆模式分析
        print("\n7. 测试记忆模式分析")
        
        pattern_analysis = memory_system.analyze_memory_patterns()
        
        print("发现的模式:")
        for pattern in pattern_analysis['patterns']:
            print(f"  - {pattern}")
        
        print("洞察:")
        for insight in pattern_analysis['insights']:
            print(f"  - {insight}")
        
        if pattern_analysis['recommendations']:
            print("建议:")
            for rec in pattern_analysis['recommendations']:
                print(f"  - {rec}")
        
        # 测试8: 记忆索引构建
        print("\n8. 测试记忆索引构建")
        
        memory_index = memory_system.build_memory_index()
        
        print("索引统计:")
        print(f"  按分类索引: {len(memory_index['by_category'])} 个分类")
        print(f"  按标签索引: {len(memory_index['by_tags'])} 个标签")
        print(f"  按重要性索引: {len(memory_index['by_importance'])} 个等级")
        print(f"  按时间索引: {len(memory_index['by_recency'])} 个时间段")
        
        # 显示一些索引内容
        if memory_index['by_tags']:
            print("热门标签:")
            tag_stats = memory_index['statistics']['tag_statistics']
            sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1]['count'], reverse=True)
            for tag, stats in sorted_tags[:5]:
                print(f"  - {tag}: {stats['count']} 次使用, 平均重要性: {stats['avg_importance']:.2f}")
        
        # 测试9: 记忆清理和优化
        print("\n9. 测试记忆清理和优化")
        
        # 添加一些低质量记忆用于测试清理
        low_quality_memories = [
            {
                'content': '测试记忆1',
                'category': 'context',
                'importance': 0.1,
                'tags': ['测试']
            },
            {
                'content': '测试记忆2',
                'category': 'context',
                'importance': 0.2,
                'tags': ['测试']
            }
        ]
        
        for memory_data in low_quality_memories:
            memory_system.add_memory(**memory_data)
        
        before_optimization = memory_system.get_memory_stats()
        print(f"优化前总记忆: {before_optimization['total_memories']}")
        
        # 执行优化
        optimization_stats = memory_system.optimize_memory_storage()
        
        after_optimization = memory_system.get_memory_stats()
        print(f"优化后总记忆: {after_optimization['total_memories']}")
        print(f"优化统计:")
        print(f"  - 移除重复: {optimization_stats['duplicates_removed']}")
        print(f"  - 移除低重要性: {optimization_stats['low_importance_removed']}")
        print(f"  - 合并相似: {optimization_stats['merged_similar']}")
        
        # 测试10: 记忆持久化
        print("\n10. 测试记忆持久化")
        
        # 保存当前状态
        original_stats = memory_system.get_memory_stats()
        
        # 创建新的记忆系统实例（模拟重启）
        new_memory_system = ContextMemorySystem(project_id="categorization_test")
        restored_stats = new_memory_system.get_memory_stats()
        
        print(f"原始记忆总数: {original_stats['total_memories']}")
        print(f"恢复记忆总数: {restored_stats['total_memories']}")
        
        if original_stats['total_memories'] == restored_stats['total_memories']:
            print("✓ 记忆持久化成功")
        else:
            print("✗ 记忆持久化失败")
        
        print("\n=== 记忆分类和存储测试完成 ===")
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
    success = test_memory_categorization_and_storage()
    sys.exit(0 if success else 1)