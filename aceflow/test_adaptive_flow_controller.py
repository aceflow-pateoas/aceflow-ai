"""
AdaptiveFlowController 单元测试
测试自适应流程控制器的核心功能
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

from pateoas.flow_controller import AdaptiveFlowController, WorkflowMode, ParallelOpportunity
from pateoas.models import NextAction, ActionType, ReasoningStep, MemoryFragment, MemoryCategory


class TestAdaptiveFlowController(unittest.TestCase):
    """AdaptiveFlowController 单元测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建临时工作目录
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 初始化流程控制器
        self.flow_controller = AdaptiveFlowController()
    
    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.flow_controller.config)
        self.assertEqual(self.flow_controller.current_mode, "smart")
        self.assertIsInstance(self.flow_controller.adaptation_history, list)
        self.assertIsInstance(self.flow_controller.performance_metrics, dict)
        
        # 验证性能指标
        required_metrics = ['efficiency', 'quality', 'speed']
        for metric in required_metrics:
            self.assertIn(metric, self.flow_controller.performance_metrics)
            self.assertIsInstance(self.flow_controller.performance_metrics[metric], float)
    
    def test_decide_next_action_basic(self):
        """测试基础决策功能"""
        user_input = "继续当前工作"
        current_state = {
            'workflow_state': {
                'current_stage': 'S2',
                'stage_progress': 0.6
            },
            'task_progress': 0.3
        }
        memory_context = []
        
        # 执行决策
        decision = self.flow_controller.decide_next_action(user_input, current_state, memory_context)
        
        # 验证决策结果结构
        required_fields = ['recommended_action', 'alternative_actions', 'reasoning', 'confidence']
        for field in required_fields:
            self.assertIn(field, decision)
        
        # 验证推荐行动
        recommended_action = decision['recommended_action']
        self.assertIsInstance(recommended_action, NextAction)
        self.assertIsInstance(recommended_action.action_type, ActionType)
        self.assertIsInstance(recommended_action.description, str)
        self.assertIsInstance(recommended_action.confidence, float)
        
        # 验证置信度在合理范围
        self.assertGreaterEqual(decision['confidence'], 0.0)
        self.assertLessEqual(decision['confidence'], 1.0)
    
    def test_decide_next_action_different_intents(self):
        """测试不同意图的决策"""
        test_cases = [
            {
                'input': "开始新项目",
                'expected_intent': 'start_project'
            },
            {
                'input': "查看当前状态",
                'expected_intent': 'check_status'
            },
            {
                'input': "修复问题",
                'expected_intent': 'fix_issue'
            },
            {
                'input': "优化性能",
                'expected_intent': 'optimize'
            }
        ]
        
        current_state = {
            'workflow_state': {'current_stage': 'S3'},
            'task_progress': 0.5
        }
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                decision = self.flow_controller.decide_next_action(
                    case['input'], current_state, []
                )
                
                # 验证决策包含合理的行动
                self.assertIsInstance(decision['recommended_action'], NextAction)
                self.assertGreater(len(decision['recommended_action'].description), 0)
                self.assertGreater(decision['confidence'], 0.0)
    
    def test_select_optimal_workflow_mode(self):
        """测试工作流模式选择"""
        test_scenarios = [
            {
                'task_description': '简单的bug修复',
                'project_context': {'team_size': 2, 'project_type': 'maintenance'},
                'expected_mode_type': str  # 应该是字符串
            },
            {
                'task_description': '复杂的微服务架构设计',
                'project_context': {'team_size': 12, 'project_type': 'enterprise'},
                'expected_mode_type': str
            },
            {
                'task_description': '紧急生产问题处理',
                'project_context': {'team_size': 5, 'project_type': 'hotfix'},
                'expected_mode_type': str
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(task=scenario['task_description'][:20]):
                result = self.flow_controller.select_optimal_workflow_mode(
                    scenario['task_description'],
                    scenario['project_context']
                )
                
                # 验证结果结构
                required_fields = ['recommended_mode', 'confidence', 'reasoning', 'factors']
                for field in required_fields:
                    self.assertIn(field, result)
                
                # 验证模式选择
                self.assertIsInstance(result['recommended_mode'], scenario['expected_mode_type'])
                self.assertGreaterEqual(result['confidence'], 0.5)
                self.assertLessEqual(result['confidence'], 1.0)
                
                # 验证因素分析
                factors = result['factors']
                self.assertIn('task_complexity', factors)
                self.assertIn('team_size', factors)
                self.assertIn('urgency', factors)
    
    def test_optimize_workflow_basic(self):
        """测试工作流优化基础功能"""
        current_state = {
            'workflow_state': {
                'current_stage': 'S4',
                'stage_progress': 0.8,
                'completed_stages': ['S1', 'S2', 'S3']
            },
            'task_progress': 0.7,
            'recent_issues_count': 2,
            'team_performance': 0.8
        }
        
        project_context = {
            'team_size': 6,
            'project_type': 'web_application',
            'deadline': (datetime.now() + timedelta(days=14)).isoformat(),
            'technology_stack': ['python', 'react', 'postgresql']
        }
        
        # 执行优化
        optimizations = self.flow_controller.optimize_workflow(current_state, project_context)
        
        # 验证优化结果结构
        expected_optimization_types = [
            'bottlenecks', 
            'parallel_execution', 
            'stage_reordering', 
            'stage_skipping', 
            'resource_allocation'
        ]
        
        for opt_type in expected_optimization_types:
            self.assertIn(opt_type, optimizations)
        
        # 验证并行执行建议
        parallel_suggestions = optimizations['parallel_execution']
        self.assertIsInstance(parallel_suggestions, list)
        
        # 如果有并行建议，验证其结构
        if parallel_suggestions:
            for suggestion in parallel_suggestions:
                required_fields = ['type', 'stages', 'time_saving', 'risk_level', 'confidence']
                for field in required_fields:
                    self.assertIn(field, suggestion)
    
    def test_analyze_user_intent(self):
        """测试用户意图分析"""
        test_intents = [
            ('开始新项目', 'start_project'),
            ('继续当前工作', 'continue_work'),
            ('检查项目状态', 'check_status'),
            ('修复这个bug', 'fix_issue'),
            ('优化性能', 'optimize'),
            ('完成当前阶段', 'complete_stage'),
            ('随机输入文本', 'general_query')  # 应该归类为一般查询
        ]
        
        current_state = {'workflow_state': {'current_stage': 'S3'}}
        
        for user_input, expected_intent in test_intents:
            with self.subTest(input=user_input):
                # 使用反射调用私有方法进行测试
                intent_analysis = self.flow_controller._analyze_user_intent(user_input, current_state)
                
                # 验证意图分析结果
                self.assertIn('primary_intent', intent_analysis)
                self.assertIn('all_intents', intent_analysis)
                self.assertIn('confidence', intent_analysis)
                
                # 验证意图识别准确性
                if expected_intent != 'general_query':
                    self.assertEqual(intent_analysis['primary_intent'], expected_intent)
                else:
                    # 对于一般查询，意图可能是general_query或其他
                    self.assertIsInstance(intent_analysis['primary_intent'], str)
    
    def test_workflow_mode_enum(self):
        """测试工作流模式枚举"""
        # 验证所有预期的模式都存在
        expected_modes = ['SMART', 'MINIMAL', 'STANDARD', 'COMPLETE', 'EMERGENCY']
        
        for mode_name in expected_modes:
            self.assertTrue(hasattr(WorkflowMode, mode_name))
            mode = getattr(WorkflowMode, mode_name)
            self.assertIsInstance(mode.value, str)
    
    def test_parallel_opportunity_class(self):
        """测试并行机会类"""
        opportunity = ParallelOpportunity(
            opportunity_type="design_development",
            stages=["S2", "S3"],
            time_saving="25%",
            risk_level="medium"
        )
        
        # 验证属性
        self.assertEqual(opportunity.type, "design_development")
        self.assertEqual(opportunity.stages, ["S2", "S3"])
        self.assertEqual(opportunity.estimated_time_saving, "25%")
        self.assertEqual(opportunity.risk_level, "medium")
        self.assertEqual(opportunity.confidence, 0.8)  # 默认值
    
    def test_performance_metrics_updates(self):
        """测试性能指标更新"""
        # 获取初始指标
        initial_metrics = self.flow_controller.performance_metrics.copy()
        
        # 验证指标在合理范围内
        for metric_name, value in initial_metrics.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        
        # 测试指标是否可修改（模拟使用场景）
        self.flow_controller.performance_metrics['efficiency'] = 0.9
        self.assertEqual(self.flow_controller.performance_metrics['efficiency'], 0.9)
    
    def test_adaptation_history_tracking(self):
        """测试适应性历史跟踪"""
        # 验证初始历史为空
        self.assertEqual(len(self.flow_controller.adaptation_history), 0)
        
        # 模拟添加历史记录
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'adaptation_type': 'mode_change',
            'from_mode': 'standard',
            'to_mode': 'complete',
            'reason': 'complexity_increase'
        }
        
        self.flow_controller.adaptation_history.append(history_entry)
        
        # 验证历史记录添加
        self.assertEqual(len(self.flow_controller.adaptation_history), 1)
        self.assertEqual(self.flow_controller.adaptation_history[0], history_entry)
    
    def test_memory_context_integration(self):
        """测试记忆上下文集成"""
        # 创建模拟记忆上下文
        memory_context = [
            {
                'content': '之前的类似任务花费了3小时',
                'category': 'learning',
                'importance': 0.8,
                'tags': ['时间估计', '任务执行']
            },
            {
                'content': '团队在数据库设计方面经验不足',
                'category': 'issue',
                'importance': 0.9,
                'tags': ['团队能力', '数据库']
            }
        ]
        
        current_state = {
            'workflow_state': {'current_stage': 'S2'},
            'task_progress': 0.2
        }
        
        # 测试带记忆上下文的决策
        decision = self.flow_controller.decide_next_action(
            "继续设计数据库",
            current_state,
            memory_context
        )
        
        # 验证决策考虑了记忆上下文
        self.assertIsInstance(decision['recommended_action'], NextAction)
        self.assertGreater(len(decision['reasoning']), 0)
        
        # 推理应该是字符串或推理步骤列表
        reasoning = decision['reasoning']
        self.assertTrue(
            isinstance(reasoning, str) or 
            (isinstance(reasoning, list) and all(isinstance(r, (str, dict, ReasoningStep)) for r in reasoning))
        )


class TestAdaptiveFlowControllerPerformance(unittest.TestCase):
    """AdaptiveFlowController 性能测试"""
    
    def setUp(self):
        """性能测试准备"""
        self.flow_controller = AdaptiveFlowController()
    
    def test_decision_making_performance(self):
        """测试决策制定性能"""
        import time
        
        # 准备测试数据
        current_state = {
            'workflow_state': {'current_stage': 'S3', 'stage_progress': 0.5},
            'task_progress': 0.4,
            'recent_issues_count': 1
        }
        
        memory_context = [
            {'content': f'测试记忆 {i}', 'category': 'context', 'importance': 0.6}
            for i in range(20)
        ]
        
        # 测试决策性能
        start_time = time.time()
        
        for i in range(50):
            user_input = f"继续执行任务 {i}"
            decision = self.flow_controller.decide_next_action(
                user_input, current_state, memory_context
            )
            self.assertIsInstance(decision, dict)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：50次决策应在合理时间内完成
        self.assertLess(duration, 5.0, f"50次决策制定耗时过长: {duration:.2f}秒")
    
    def test_workflow_optimization_performance(self):
        """测试工作流优化性能"""
        import time
        
        # 准备复杂状态
        current_state = {
            'workflow_state': {
                'current_stage': 'S4',
                'stage_progress': 0.7,
                'completed_stages': ['S1', 'S2', 'S3'],
                'stage_details': {f'stage_{i}': f'detail_{i}' * 10 for i in range(5)}
            },
            'task_progress': 0.6,
            'team_metrics': {f'metric_{i}': 0.8 for i in range(10)},
            'project_history': [f'event_{i}' for i in range(100)]
        }
        
        project_context = {
            'team_size': 8,
            'project_type': 'complex_system',
            'technology_stack': [f'tech_{i}' for i in range(15)],
            'constraints': {f'constraint_{i}': f'value_{i}' for i in range(10)}
        }
        
        # 测试优化性能
        start_time = time.time()
        
        for _ in range(10):
            optimizations = self.flow_controller.optimize_workflow(current_state, project_context)
            self.assertIsInstance(optimizations, dict)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：10次优化应在合理时间内完成
        self.assertLess(duration, 3.0, f"10次工作流优化耗时过长: {duration:.2f}秒")
    
    def test_mode_selection_performance(self):
        """测试模式选择性能"""
        import time
        
        # 准备测试用例
        test_tasks = [
            f"复杂任务描述 {i} " + "详细需求 " * 20
            for i in range(100)
        ]
        
        project_contexts = [
            {
                'team_size': i % 10 + 1,
                'project_type': ['web', 'mobile', 'desktop', 'api'][i % 4],
                'complexity_factors': {f'factor_{j}': 0.5 + (j % 5) * 0.1 for j in range(5)}
            }
            for i in range(100)
        ]
        
        # 测试模式选择性能
        start_time = time.time()
        
        for task, context in zip(test_tasks, project_contexts):
            result = self.flow_controller.select_optimal_workflow_mode(task, context)
            self.assertIn('recommended_mode', result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能：100次模式选择应在合理时间内完成
        self.assertLess(duration, 2.0, f"100次模式选择耗时过长: {duration:.2f}秒")


if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加基础功能测试
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveFlowController))
    
    # 添加性能测试
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveFlowControllerPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print(f"\n🧪 AdaptiveFlowController 测试完成:")
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