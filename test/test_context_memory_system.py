"""
ContextMemorySystem 单元测试
测试上下文记忆系统的核心功能
"""

import unittest
import tempfile
import shutil
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 pateoas 模块路径
sys.path.insert(0, str(Path(__file__).parent))

from pateoas.memory_system import ContextMemorySystem
from pateoas.models import MemoryCategory


class TestContextMemorySystem(unittest.TestCase):
    """ContextMemorySystem 单元测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_project_id = "test_memory_project"
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建临时工作目录
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 初始化记忆系统
        self.memory_system = ContextMemorySystem(project_id=self.test_project_id)
    
    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.memory_system.project_id, self.test_project_id)
        self.assertIsInstance(self.memory_system.memory_categories, dict)
        
        # 验证初始状态
        stats = self.memory_system.get_memory_stats()
        self.assertIn('total_memories', stats)
        self.assertEqual(stats['total_memories'], 0)
    
    def test_add_memory_basic(self):
        """测试基础记忆添加"""
        content = "实现用户登录功能"
        category = "context"
        importance = 0.8
        tags = ["登录", "用户认证"]
        
        # 添加记忆
        self.memory_system.add_memory(content, category, importance, tags)
        
        # 验证记忆添加
        stats = self.memory_system.get_memory_stats()
        self.assertEqual(stats['total_memories'], 1)
        
        # 搜索验证
        memories = self.memory_system.search_memories("用户登录", limit=1)
        self.assertEqual(len(memories), 1)
        
        memory = memories[0]
        self.assertEqual(memory['content'], content)
        self.assertEqual(memory['category'], category)
        self.assertEqual(memory['importance'], importance)
        self.assertEqual(memory['tags'], tags)
    
    def test_add_memory_different_categories(self):
        """测试不同类别的记忆添加"""
        test_memories = [
            ("需求分析完成", "context", 0.9, ["需求", "分析"]),
            ("选择FastAPI框架", "decision", 0.8, ["框架", "技术选型"]),
            ("API设计模式", "pattern", 0.7, ["设计", "模式"]),
            ("数据库连接失败", "issue", 0.6, ["数据库", "问题"]),
            ("学会了新的测试方法", "learning", 0.5, ["测试", "学习"])
        ]
        
        # 添加不同类别的记忆
        for content, category, importance, tags in test_memories:
            self.memory_system.add_memory(content, category, importance, tags)
        
        # 验证总数
        stats = self.memory_system.get_memory_stats()
        self.assertEqual(stats['total_memories'], 5)
        
        # 验证分类统计
        if 'categories' in stats:
            category_counts = {cat: data['count'] for cat, data in stats['categories'].items()}
            expected_categories = {'context', 'decision', 'pattern', 'issue', 'learning'}
            for category in expected_categories:
                self.assertIn(category, category_counts)
                self.assertEqual(category_counts[category], 1)
    
    def test_search_memories_basic(self):
        """测试基础记忆搜索"""
        # 添加测试记忆
        test_memories = [
            "实现用户登录API",
            "设计数据库表结构", 
            "编写单元测试",
            "用户界面设计",
            "API文档编写"
        ]
        
        for i, content in enumerate(test_memories):
            self.memory_system.add_memory(
                content, 
                "context", 
                0.5 + i * 0.1, 
                [f"tag_{i}"]
            )
        
        # 搜索测试
        results = self.memory_system.search_memories("用户", limit=3)
        self.assertGreater(len(results), 0)
        
        # 验证搜索结果包含相关内容
        found_user_content = any("用户" in result['content'] for result in results)
        self.assertTrue(found_user_content)
    
    def test_search_memories_by_category(self):
        """测试按类别搜索记忆"""
        # 添加不同类别的记忆
        self.memory_system.add_memory("技术决策：选择React", "decision", 0.8, ["React", "决策"])
        self.memory_system.add_memory("学习新框架", "learning", 0.6, ["学习", "框架"])
        self.memory_system.add_memory("API接口设计", "context", 0.7, ["API", "设计"])
        
        # 按类别搜索
        decision_memories = self.memory_system.search_memories("React", category="decision", limit=10)
        learning_memories = self.memory_system.search_memories("框架", category="learning", limit=10)
        
        # 验证搜索结果
        self.assertEqual(len(decision_memories), 1)
        self.assertEqual(len(learning_memories), 1)
        self.assertEqual(decision_memories[0]['category'], "decision")
        self.assertEqual(learning_memories[0]['category'], "learning")
    
    def test_recall_relevant_context(self):
        """测试相关上下文召回"""
        # 添加相关记忆
        self.memory_system.add_memory(
            "用户认证系统需要支持多种登录方式", 
            "context", 
            0.9, 
            ["认证", "登录", "需求"]
        )
        self.memory_system.add_memory(
            "选择JWT作为认证token格式", 
            "decision", 
            0.8, 
            ["JWT", "token", "认证"]
        )
        self.memory_system.add_memory(
            "实现OAuth2集成", 
            "context", 
            0.7, 
            ["OAuth2", "集成"]
        )
        
        # 测试上下文召回
        current_input = "开发用户登录功能"
        current_state = {"current_task": "用户认证", "stage": "development"}
        
        relevant_memories = self.memory_system.recall_relevant_context(
            current_input, current_state, limit=5
        )
        
        # 验证召回结果
        self.assertGreater(len(relevant_memories), 0)
        
        # 验证相关性排序（第一个应该最相关）
        if len(relevant_memories) > 1:
            first_relevance = relevant_memories[0].get('relevance_score', 0)
            second_relevance = relevant_memories[1].get('relevance_score', 0)
            self.assertGreaterEqual(first_relevance, second_relevance)
    
    def test_intelligent_recall(self):
        """测试智能召回功能"""
        # 添加复杂的记忆场景
        memories_data = [
            ("项目采用微服务架构", "decision", 0.9, ["微服务", "架构"]),
            ("用户服务负责认证和用户管理", "context", 0.8, ["用户服务", "认证"]),
            ("API网关处理路由和负载均衡", "context", 0.7, ["API网关", "路由"]),
            ("数据库分库分表策略", "pattern", 0.8, ["数据库", "分库分表"]),
            ("Redis用于缓存和会话存储", "decision", 0.7, ["Redis", "缓存"])
        ]
        
        for content, category, importance, tags in memories_data:
            self.memory_system.add_memory(content, category, importance, tags)
        
        # 测试智能召回
        query_context = {
            "current_task": "设计用户认证服务",
            "technology_focus": "微服务",
            "complexity_level": "high"
        }
        
        intelligent_results = self.memory_system.intelligent_recall(
            query="用户认证服务设计",
            current_state=query_context,
            min_relevance=0.6,
            limit=3
        )
        
        # 验证智能召回结果
        self.assertIn('results', intelligent_results)
        self.assertGreater(len(intelligent_results['results']), 0)
        
        # 验证返回的记忆都与查询相关
        for memory in intelligent_results['results']:
            self.assertIn('content', memory)
            self.assertIn('relevance_score', memory)
            self.assertGreaterEqual(memory['relevance_score'], 0.0)
    
    def test_store_interaction(self):
        """测试交互存储"""
        user_input = "如何实现用户权限管理？"
        ai_response = {
            "recommendation": "使用RBAC模型",
            "reasoning": "基于角色的访问控制更灵活",
            "confidence": 0.9
        }
        
        # 存储交互
        self.memory_system.store_interaction(user_input, ai_response)
        
        # 验证交互存储
        stats = self.memory_system.get_memory_stats()
        self.assertGreater(stats['total_memories'], 0)
        
        # 搜索相关记忆
        memories = self.memory_system.search_memories("权限管理", limit=5)
        self.assertGreater(len(memories), 0)
        
        # 验证存储的内容
        found_relevant = False
        for memory in memories:
            if "权限管理" in memory['content'] or "RBAC" in memory['content']:
                found_relevant = True
                break
        self.assertTrue(found_relevant)
    
    def test_memory_cleanup(self):
        """测试记忆清理功能"""
        # 添加一些旧记忆（模拟）
        old_memories = [
            "旧的需求分析",
            "过时的技术决策", 
            "历史问题记录"
        ]
        
        for content in old_memories:
            self.memory_system.add_memory(content, "context", 0.5, ["旧"])
        
        # 添加一些新记忆
        new_memories = [
            "最新的需求更新",
            "当前技术选择"
        ]
        
        for content in new_memories:
            self.memory_system.add_memory(content, "context", 0.8, ["新"])
        
        initial_count = self.memory_system.get_memory_stats()['total_memories']
        
        # 执行清理（清理1天前的记忆）
        cleaned_count = self.memory_system.cleanup_old_memories(days=1)
        
        # 由于是刚添加的记忆，实际清理数量可能为0
        # 主要验证方法不会出错
        self.assertGreaterEqual(cleaned_count, 0)
        
        final_count = self.memory_system.get_memory_stats()['total_memories']
        self.assertLessEqual(final_count, initial_count)
    
    def test_memory_optimization(self):
        """测试记忆优化"""
        # 添加一些相似的记忆
        similar_memories = [
            "用户登录功能实现",
            "用户登录功能开发", 
            "实现用户登录",
            "开发登录功能"
        ]
        
        for content in similar_memories:
            self.memory_system.add_memory(content, "context", 0.7, ["登录"])
        
        initial_count = self.memory_system.get_memory_stats()['total_memories']
        
        # 执行优化
        self.memory_system.optimize_memory_storage()
        
        # 验证优化后的状态
        optimized_count = self.memory_system.get_memory_stats()['total_memories']
        
        # 优化可能合并了相似的记忆
        self.assertLessEqual(optimized_count, initial_count)
    
    def test_memory_stats(self):
        """测试记忆统计功能"""
        # 添加多种类型的记忆
        test_data = [
            ("需求1", "context", 0.9),
            ("需求2", "context", 0.8),
            ("决策1", "decision", 0.7),
            ("模式1", "pattern", 0.6),
            ("问题1", "issue", 0.5)
        ]
        
        for content, category, importance in test_data:
            self.memory_system.add_memory(content, category, importance, [category])
        
        # 获取统计信息
        stats = self.memory_system.get_memory_stats()
        
        # 验证基础统计
        self.assertEqual(stats['total_memories'], 5)
        
        # 验证分类统计
        if 'categories' in stats:
            breakdown = {cat: data['count'] for cat, data in stats['categories'].items()}
            self.assertEqual(breakdown.get('context', 0), 2)
            self.assertEqual(breakdown.get('decision', 0), 1)
            self.assertEqual(breakdown.get('pattern', 0), 1)
            self.assertEqual(breakdown.get('issue', 0), 1)
        
        # 验证其他统计信息
        expected_fields = ['total_memories', 'avg_importance', 'memory_by_day']
        for field in expected_fields:
            if field in stats:
                self.assertIsNotNone(stats[field])


class TestMemorySystemPerformance(unittest.TestCase):
    """记忆系统性能测试"""
    
    def setUp(self):
        """性能测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.memory_system = ContextMemorySystem(project_id="perf_test")
    
    def tearDown(self):
        """性能测试清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_memory_storage_performance(self):
        """测试大量记忆存储性能"""
        import time
        
        start_time = time.time()
        
        # 添加1000条记忆
        for i in range(1000):
            content = f"测试记忆内容 {i} - " + "详细描述 " * 10
            category = ["context", "decision", "pattern", "issue", "learning"][i % 5]
            importance = 0.1 + (i % 10) * 0.1
            tags = [f"tag_{i%5}", f"category_{category}"]
            
            self.memory_system.add_memory(content, category, importance, tags)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：1000条记忆应在合理时间内完成
        self.assertLess(duration, 10.0, f"1000条记忆存储耗时过长: {duration:.2f}秒")
        
        # 验证数据完整性
        stats = self.memory_system.get_memory_stats()
        self.assertEqual(stats['total_memories'], 1000)
    
    def test_memory_search_performance(self):
        """测试记忆搜索性能"""
        import time
        
        # 先添加一些记忆
        for i in range(100):
            content = f"项目功能 {i} 的实现和测试"
            self.memory_system.add_memory(
                content, 
                "context", 
                0.5 + (i % 5) * 0.1, 
                [f"功能_{i}", "实现", "测试"]
            )
        
        # 测试搜索性能
        start_time = time.time()
        
        search_queries = [
            "项目功能",
            "实现和测试", 
            "功能实现",
            "测试相关",
            "项目开发"
        ]
        
        for query in search_queries:
            for _ in range(20):  # 每个查询搜索20次
                results = self.memory_system.search_memories(query, limit=10)
                self.assertIsInstance(results, list)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：100次搜索应在合理时间内完成
        self.assertLess(duration, 5.0, f"100次记忆搜索耗时过长: {duration:.2f}秒")
    
    def test_intelligent_recall_performance(self):
        """测试智能召回性能"""
        import time
        
        # 添加复杂的记忆数据
        for i in range(200):
            content = f"复杂项目场景 {i} - " + " ".join([
                f"技术栈{j}" for j in range(5)
            ]) + f" 解决方案和最佳实践"
            
            category = ["context", "decision", "pattern"][i % 3]
            importance = 0.3 + (i % 7) * 0.1
            tags = [f"技术{i%10}", f"场景{i%5}", "解决方案"]
            
            self.memory_system.add_memory(content, category, importance, tags)
        
        # 测试智能召回性能
        start_time = time.time()
        
        for i in range(50):
            query = f"技术解决方案 {i%10}"
            context = {
                "current_task": f"任务 {i}",
                "complexity": "medium",
                "technology_focus": f"技术{i%5}"
            }
            
            results = self.memory_system.intelligent_recall(
                query=query,
                current_state=context,
                limit=5
            )
            # 验证results字典结构
            self.assertIsInstance(results, dict)
            self.assertIn('results', results)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：50次智能召回应在合理时间内完成
        self.assertLess(duration, 8.0, f"50次智能召回耗时过长: {duration:.2f}秒")


if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加基础功能测试
    suite.addTests(loader.loadTestsFromTestCase(TestContextMemorySystem))
    
    # 添加性能测试
    suite.addTests(loader.loadTestsFromTestCase(TestMemorySystemPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print(f"\n🧪 ContextMemorySystem 测试完成:")
    print(f"✅ 测试通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 测试失败: {len(result.failures)}")
    print(f"💥 测试错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")