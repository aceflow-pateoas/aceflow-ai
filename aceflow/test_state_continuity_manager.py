"""
StateContinuityManager 单元测试
测试状态连续性管理器的核心功能
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

from pateoas.state_manager import StateContinuityManager
from pateoas.models import PATEOASState, MemoryFragment, NextAction, ReasoningStep


class TestStateContinuityManager(unittest.TestCase):
    """StateContinuityManager 单元测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_project_id = "test_project_001"
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建临时工作目录
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 初始化状态管理器
        self.state_manager = StateContinuityManager(project_id=self.test_project_id)
    
    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.state_manager.project_id, self.test_project_id)
        self.assertIsInstance(self.state_manager.state_history, list)
        self.assertIsInstance(self.state_manager.state_transitions, list)
        
        # 验证初始状态
        current_state = self.state_manager.get_current_state()
        self.assertIn('project_id', current_state)
        self.assertEqual(current_state['project_id'], self.test_project_id)
    
    def test_get_current_state(self):
        """测试获取当前状态"""
        state = self.state_manager.get_current_state()
        
        # 验证必要字段
        required_fields = ['project_id', 'session_id', 'timestamp', 'workflow_state', 'interaction_count']
        for field in required_fields:
            self.assertIn(field, state)
        
        # 验证数据类型
        self.assertIsInstance(state['project_id'], str)
        self.assertIsInstance(state['workflow_state'], dict)
        self.assertIsInstance(state['interaction_count'], int)
    
    def test_update_state(self):
        """测试状态更新"""
        # 获取初始状态
        initial_state = self.state_manager.get_current_state()
        initial_count = initial_state['interaction_count']
        
        # 更新状态
        update_data = {
            'current_task': '开发用户登录功能',
            'task_progress': 0.3,
            'trigger': 'task_start',
            'reasoning': '开始新任务'
        }
        
        self.state_manager.update_state(update_data)
        
        # 验证状态更新
        updated_state = self.state_manager.get_current_state()
        self.assertEqual(updated_state['current_task'], '开发用户登录功能')
        self.assertEqual(updated_state['task_progress'], 0.3)
        self.assertEqual(updated_state['interaction_count'], initial_count + 1)
        
        # 验证状态转换记录
        self.assertEqual(len(self.state_manager.state_transitions), 1)
        transition = self.state_manager.state_transitions[0]
        self.assertEqual(transition['trigger'], 'task_start')
        self.assertEqual(transition['reasoning'], '开始新任务')
    
    def test_generate_state_declaration(self):
        """测试状态声明生成"""
        # 更新一些状态数据
        self.state_manager.update_state({
            'current_task': '开发API接口',
            'task_progress': 0.6,
            'stage_context': {'current_stage': 'S4', 'workflow_mode': 'standard'},
            'trigger': 'progress_update',
            'reasoning': '任务进展良好'
        })
        
        # 生成状态声明
        declaration = self.state_manager.generate_state_declaration()
        
        # 验证声明结构
        required_fields = ['current_understanding', 'next_suggestions', 'meta_cognition', 'context_summary']
        for field in required_fields:
            self.assertIn(field, declaration)
        
        # 验证建议列表
        self.assertIsInstance(declaration['next_suggestions'], list)
        if declaration['next_suggestions']:
            suggestion = declaration['next_suggestions'][0]
            self.assertIn('action_type', suggestion)
            self.assertIn('description', suggestion)
    
    def test_state_persistence(self):
        """测试状态持久化"""
        # 更新状态
        test_data = {
            'test_field': 'test_value',
            'timestamp': datetime.now().isoformat(),
            'trigger': 'test',
            'reasoning': '测试持久化'
        }
        
        self.state_manager.update_state(test_data)
        
        # 创建新的状态管理器实例
        new_manager = StateContinuityManager(project_id=self.test_project_id)
        
        # 验证状态是否持久化
        loaded_state = new_manager.get_current_state()
        self.assertEqual(loaded_state.get('test_field'), 'test_value')
    
    def test_state_rollback(self):
        """测试状态回滚"""
        # 记录初始状态
        initial_state = self.state_manager.get_current_state()
        
        # 进行多次状态更新
        for i in range(3):
            self.state_manager.update_state({
                'step': i,
                'task_progress': i * 0.3,
                'trigger': f'step_{i}',
                'reasoning': f'执行步骤 {i}'
            })
        
        # 验证状态历史
        self.assertEqual(len(self.state_manager.state_transitions), 3)
        
        # 测试回滚到之前的状态
        if hasattr(self.state_manager, 'rollback_to_transition'):
            # 回滚到第一个状态
            self.state_manager.rollback_to_transition(0)
            current_state = self.state_manager.get_current_state()
            self.assertEqual(current_state.get('step'), 0)
    
    def test_context_analysis(self):
        """测试上下文分析"""
        # 创建复杂的状态场景
        scenario_data = {
            'current_task': '开发用户认证系统',
            'task_progress': 0.8,
            'stage_context': {
                'current_stage': 'S4',
                'workflow_mode': 'standard',
                'completed_stages': ['S1', 'S2', 'S3']
            },
            'project_context': {
                'team_size': 5,
                'technology_stack': ['python', 'fastapi', 'postgresql'],
                'deadline': (datetime.now() + timedelta(days=7)).isoformat()
            },
            'trigger': 'context_test',
            'reasoning': '测试上下文分析功能'
        }
        
        self.state_manager.update_state(scenario_data)
        
        # 生成状态声明
        declaration = self.state_manager.generate_state_declaration()
        
        # 验证上下文理解
        context_summary = declaration.get('context_summary', {})
        self.assertIn('project_progress', context_summary)
        self.assertIn('current_focus', context_summary)
        
        # 验证元认知
        meta_cognition = declaration.get('meta_cognition', {})
        self.assertIn('confidence_level', meta_cognition)
        self.assertIn('known_limitations', meta_cognition)
    
    def test_next_suggestions_generation(self):
        """测试下一步建议生成"""
        # 设置处于中间阶段的状态
        self.state_manager.update_state({
            'current_task': '实现用户注册功能',
            'task_progress': 0.5,
            'stage_context': {
                'current_stage': 'S4',
                'workflow_mode': 'standard'
            },
            'recent_activities': ['完成数据库设计', '实现基础API'],
            'trigger': 'suggestions_test',
            'reasoning': '测试建议生成'
        })
        
        declaration = self.state_manager.generate_state_declaration()
        suggestions = declaration.get('next_suggestions', [])
        
        # 验证建议质量
        self.assertGreater(len(suggestions), 0)
        
        for suggestion in suggestions:
            # 验证必要字段
            self.assertIn('action_type', suggestion)
            self.assertIn('description', suggestion)
            self.assertIn('priority', suggestion)
            
            # 验证建议类型
            self.assertIn(suggestion['action_type'], [
                'continue', 'optimize', 'review', 'test', 'document'
            ])
    
    def test_state_validation(self):
        """测试状态验证"""
        # 测试有效状态更新
        valid_update = {
            'current_task': '有效任务',
            'task_progress': 0.5,
            'trigger': 'valid_update',
            'reasoning': '有效的状态更新'
        }
        
        try:
            self.state_manager.update_state(valid_update)
            state = self.state_manager.get_current_state()
            self.assertEqual(state['current_task'], '有效任务')
        except Exception as e:
            self.fail(f"有效状态更新失败: {e}")
        
        # 测试边界情况
        boundary_update = {
            'task_progress': 1.0,  # 边界值
            'trigger': 'boundary_test',
            'reasoning': '边界测试'
        }
        
        try:
            self.state_manager.update_state(boundary_update)
        except Exception as e:
            self.fail(f"边界值更新失败: {e}")
    
    def test_concurrent_state_updates(self):
        """测试并发状态更新处理"""
        import threading
        import time
        
        results = []
        errors = []
        
        def update_state(thread_id):
            try:
                for i in range(5):
                    self.state_manager.update_state({
                        'thread_id': thread_id,
                        'iteration': i,
                        'timestamp': datetime.now().isoformat(),
                        'trigger': f'thread_{thread_id}_update',
                        'reasoning': f'线程{thread_id}的第{i}次更新'
                    })
                    time.sleep(0.01)  # 短暂延迟
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # 创建多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_state, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(errors), 0, f"并发更新出现错误: {errors}")
        self.assertEqual(len(results), 3, "并非所有线程都成功完成")
        
        # 验证最终状态
        final_state = self.state_manager.get_current_state()
        self.assertGreaterEqual(final_state['interaction_count'], 15)  # 3线程 × 5次更新


class TestStateManagerPerformance(unittest.TestCase):
    """状态管理器性能测试"""
    
    def setUp(self):
        """性能测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.state_manager = StateContinuityManager(project_id="perf_test")
    
    def tearDown(self):
        """性能测试清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_state_updates_performance(self):
        """测试大量状态更新的性能"""
        import time
        
        start_time = time.time()
        
        # 执行100次状态更新
        for i in range(100):
            self.state_manager.update_state({
                'iteration': i,
                'data': f'data_{i}' * 10,  # 增加数据大小
                'timestamp': datetime.now().isoformat(),
                'trigger': 'performance_test',
                'reasoning': f'性能测试第{i}次更新'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：100次更新应在合理时间内完成
        self.assertLess(duration, 5.0, f"100次状态更新耗时过长: {duration:.2f}秒")
        
        # 验证状态数据完整性
        final_state = self.state_manager.get_current_state()
        self.assertEqual(final_state['iteration'], 99)
        self.assertEqual(len(self.state_manager.state_transitions), 100)
    
    def test_state_declaration_performance(self):
        """测试状态声明生成性能"""
        import time
        
        # 先创建复杂状态
        complex_state = {
            'current_task': '复杂任务',
            'task_progress': 0.7,
            'stage_context': {
                'current_stage': 'S5',
                'workflow_mode': 'complete',
                'completed_stages': ['S1', 'S2', 'S3', 'S4'],
                'stage_details': {f'stage_{i}': f'detail_{i}' * 20 for i in range(10)}
            },
            'project_context': {
                'team_members': [f'member_{i}' for i in range(10)],
                'technologies': [f'tech_{i}' for i in range(15)],
                'requirements': [f'req_{i}' * 5 for i in range(20)]
            },
            'trigger': 'performance_test',
            'reasoning': '性能测试复杂状态'
        }
        
        self.state_manager.update_state(complex_state)
        
        # 测试声明生成性能
        start_time = time.time()
        
        for _ in range(10):
            declaration = self.state_manager.generate_state_declaration()
            self.assertIsInstance(declaration, dict)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：10次声明生成应在合理时间内完成
        self.assertLess(duration, 2.0, f"10次状态声明生成耗时过长: {duration:.2f}秒")


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加基础功能测试
    suite.addTest(unittest.makeSuite(TestStateContinuityManager))
    
    # 添加性能测试
    suite.addTest(unittest.makeSuite(TestStateManagerPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print(f"\n🧪 StateContinuityManager 测试完成:")
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