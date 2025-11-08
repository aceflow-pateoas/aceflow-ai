"""
集成测试 - 完整工作流

测试完整的工作流执行流程
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.engine import WorkflowEngine
from aceflow.workflow.state import StateManager
from aceflow.workflow.memory import MemoryManager
from aceflow.workflow.templates import TemplateManager
from aceflow.workflow.exporter import DocumentExporter, ExportOptions, ExportFormat
from aceflow.workflow.models import WorkflowMode, StageStatus


class TestWorkflowIntegration:
    """工作流集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器"""
        return StateManager(storage_dir=temp_dir)

    @pytest.fixture
    def memory_manager(self, temp_dir):
        """创建记忆管理器"""
        return MemoryManager(storage_path=temp_dir / "memory.json")

    def test_minimal_workflow_complete_cycle(self, state_manager, memory_manager):
        """测试 Minimal 模式的完整周期"""
        # 1. 创建引擎
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)

        # 2. 开始迭代
        iteration = engine.start_iteration("test_iter_001")
        assert iteration is not None
        assert iteration.mode == WorkflowMode.MINIMAL

        # 3. 记录初始状态
        memory_manager.record_decision(
            "选择 Minimal 模式",
            {"reason": "快速原型开发"},
            iteration_id=iteration.iteration_id
        )

        # 4. 遍历所有阶段
        stages_completed = 0
        max_iterations = 10  # 防止无限循环

        while stages_completed < max_iterations:
            current = state_manager.get_iteration(iteration.iteration_id)
            current_stage = current.current_stage

            if not current_stage or current_stage.status == StageStatus.COMPLETED:
                # 尝试进入下一阶段
                next_stage = engine.advance_to_next_stage(iteration.iteration_id)
                if not next_stage:
                    # 没有更多阶段了
                    break

                # 记录阶段输出
                memory_manager.record_stage_output(
                    iteration.iteration_id,
                    next_stage,
                    f"完成 {next_stage.name} 阶段",
                    WorkflowMode.MINIMAL.value
                )

            # 完成当前阶段
            current = state_manager.get_iteration(iteration.iteration_id)
            if current.current_stage:
                engine.complete_stage(iteration.iteration_id, current.current_stage.stage_id)
                stages_completed += 1

        # 5. 验证所有阶段都完成了
        final_iteration = state_manager.get_iteration(iteration.iteration_id)
        completed_stages = [s for s in final_iteration.stages if s.status == StageStatus.COMPLETED]
        assert len(completed_stages) == len(final_iteration.stages)

        # 6. 获取记忆摘要
        summary = memory_manager.get_iteration_summary(iteration.iteration_id)
        assert summary['iteration_id'] == iteration.iteration_id
        assert summary['total_memories'] > 0

    def test_standard_workflow_with_templates(self, state_manager, temp_dir):
        """测试 Standard 模式结合模板"""
        # 1. 创建引擎和模板管理器
        engine = WorkflowEngine(WorkflowMode.STANDARD, state_manager)
        template_manager = TemplateManager(output_root=temp_dir / "output")

        # 2. 开始迭代
        iteration = engine.start_iteration("test_iter_002")

        # 3. 为每个阶段生成模板
        for stage in iteration.stages:
            template = template_manager.get_template_for_stage(
                WorkflowMode.STANDARD.value,
                stage.stage_id
            )

            if template:
                # 渲染模板
                variables = {
                    'iteration_id': iteration.iteration_id,
                    'stage_id': stage.stage_id,
                    'stage_name': stage.name,
                    'owner': 'Test User'
                }

                rendered = template_manager.render_template(
                    template.template_id,
                    variables
                )

                assert rendered is not None
                assert iteration.iteration_id in rendered

        # 4. 验证模板系统
        templates = template_manager.get_templates_for_mode(WorkflowMode.STANDARD.value)
        assert len(templates) > 0

    def test_complete_workflow_with_gates(self, state_manager):
        """测试 Complete 模式结合质量门"""
        from aceflow.workflow.gates import GateManager

        # 1. 创建引擎和质量门管理器
        engine = WorkflowEngine(WorkflowMode.COMPLETE, state_manager)
        gate_manager = GateManager()

        # 2. 开始迭代
        iteration = engine.start_iteration("test_iter_003")

        # 3. 找到需要质量门的阶段
        gate_stages = [s for s in iteration.stages if s.metadata.get('quality_gate')]

        assert len(gate_stages) >= 3  # Complete 模式应该有3个质量门

        # 4. 模拟质量门评估
        for stage in gate_stages:
            gate_id = stage.metadata.get('quality_gate')

            if gate_id:
                # 准备评估上下文
                context = {
                    'user_stories': [
                        {'has_acceptance_criteria': True}
                    ],
                    'tasks': [
                        {'subtasks': ['sub1', 'sub2']}
                    ],
                    'test_cases': list(range(10)),
                    'dependencies_identified': True,
                    'technical_design_complete': True
                }

                # 评估质量门
                evaluation = gate_manager.evaluate_gate(gate_id, context)

                assert evaluation is not None
                assert evaluation.gate_id == gate_id
                assert evaluation.score >= 0.0
                assert evaluation.score <= 1.0

    def test_export_iteration(self, state_manager, temp_dir):
        """测试导出迭代文档"""
        # 1. 创建并完成一个迭代
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)
        iteration = engine.start_iteration("test_iter_004")

        # 完成第一个阶段
        engine.complete_stage(iteration.iteration_id, iteration.current_stage.stage_id)

        # 2. 导出为 Markdown
        exporter = DocumentExporter(state_manager)

        result = exporter.export_iteration(
            iteration.iteration_id,
            ExportOptions(
                format=ExportFormat.MARKDOWN,
                output_dir=temp_dir / "exports",
                single_file=True
            )
        )

        assert result.success
        assert result.output_path is not None
        assert len(result.files_created) > 0

        # 验证文件存在
        for file_path in result.files_created:
            assert file_path.exists()

        # 3. 导出为 JSON
        json_result = exporter.export_iteration(
            iteration.iteration_id,
            ExportOptions(
                format=ExportFormat.JSON,
                output_dir=temp_dir / "exports_json"
            )
        )

        assert json_result.success
        assert len(json_result.files_created) == 1

        # 验证 JSON 文件
        json_file = json_result.files_created[0]
        assert json_file.exists()
        assert json_file.suffix == '.json'

    def test_memory_recall_integration(self, state_manager, memory_manager):
        """测试记忆召回集成"""
        # 1. 创建迭代并记录记忆
        engine = WorkflowEngine(WorkflowMode.STANDARD, state_manager)
        iteration = engine.start_iteration("test_iter_005")

        # 2. 记录多种类型的记忆
        memory_manager.record_decision(
            "使用 Standard 模式",
            {"reason": "平衡开发速度和质量"},
            iteration_id=iteration.iteration_id
        )

        memory_manager.record_issue(
            "API 接口设计不明确",
            severity="medium",
            iteration_id=iteration.iteration_id,
            stage_id=iteration.current_stage.stage_id if iteration.current_stage else None,
            solution="补充接口文档"
        )

        memory_manager.record_learning(
            "API 设计需要提前明确",
            category="技术",
            iteration_id=iteration.iteration_id
        )

        # 3. 召回记忆
        if iteration.current_stage:
            memories = memory_manager.recall_for_stage(
                iteration.iteration_id,
                iteration.current_stage.stage_id
            )

            assert len(memories) > 0

        # 4. 搜索相似问题
        similar_issues = memory_manager.recall_similar_issues("API", limit=5)
        assert len(similar_issues) > 0

        # 5. 获取经验教训
        learnings = memory_manager.recall_learnings(category="技术")
        assert len(learnings) > 0


class TestMCPToolsIntegration:
    """MCP 工具集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    def test_mcp_tools_workflow(self, temp_dir):
        """测试通过 MCP 工具操作工作流"""
        from aceflow.workflow.mcp import WorkflowMCPTools

        # 1. 创建 MCP 工具集
        tools = WorkflowMCPTools(working_directory=temp_dir)

        # 2. 使用 MCP 工具开始迭代
        result = tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "mcp_test_001",
                "metadata": {"source": "mcp_test"}
            }
        )

        assert result.success
        assert result.data['iteration_id'] == "mcp_test_001"

        # 3. 获取当前状态
        status_result = tools.execute_tool(
            "state_get_current",
            {"iteration_id": "mcp_test_001"}
        )

        assert status_result.success
        assert status_result.data['iteration_id'] == "mcp_test_001"

        # 4. 进入下一阶段
        next_result = tools.execute_tool(
            "workflow_next_stage",
            {"iteration_id": "mcp_test_001"}
        )

        assert next_result.success

        # 5. 记录记忆
        memory_result = tools.execute_tool(
            "memory_record_issue",
            {
                "issue": "测试问题",
                "severity": "low",
                "iteration_id": "mcp_test_001"
            }
        )

        assert memory_result.success

        # 6. 列出所有工具
        all_tools = tools.list_tools()
        assert len(all_tools) >= 14  # 应该有至少14个工具

        # 7. 获取工具 schemas
        schemas = tools.get_tool_schemas()
        assert len(schemas) >= 14
        assert all('name' in s for s in schemas)
        assert all('inputSchema' in s for s in schemas)
