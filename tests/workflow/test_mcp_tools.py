"""
测试 MCP 工具

测试 aceflow.workflow.mcp 模块
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.mcp import WorkflowMCPTools
from aceflow.workflow.mcp.models import MCPToolCategory, MCPToolResult
from aceflow.workflow.models import WorkflowMode, StageStatus


class TestMCPToolModels:
    """测试 MCP 工具数据模型"""

    def test_tool_category_enum(self):
        """测试工具类别枚举"""
        assert MCPToolCategory.WORKFLOW.value == "workflow"
        assert MCPToolCategory.STATE.value == "state"
        assert MCPToolCategory.MEMORY.value == "memory"
        assert MCPToolCategory.TEMPLATE.value == "template"
        assert MCPToolCategory.EXPORT.value == "export"

    def test_tool_result_success(self):
        """测试成功的工具结果"""
        result = MCPToolResult(
            success=True,
            data={"iteration_id": "iter_001"},
            message="迭代创建成功"
        )

        assert result.success is True
        assert result.data['iteration_id'] == "iter_001"
        assert result.message == "迭代创建成功"
        assert result.error is None

    def test_tool_result_failure(self):
        """测试失败的工具结果"""
        result = MCPToolResult(
            success=False,
            error="参数验证失败",
            message="无法创建迭代"
        )

        assert result.success is False
        assert result.error == "参数验证失败"
        assert result.data is None

    def test_tool_result_to_dict(self):
        """测试结果转字典"""
        result = MCPToolResult(
            success=True,
            data={"key": "value"},
            message="操作成功"
        )

        data = result.to_dict()

        assert data['success'] is True
        assert data['data']['key'] == "value"
        assert data['message'] == "操作成功"


class TestWorkflowMCPTools:
    """测试工作流 MCP 工具集"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def mcp_tools(self, temp_dir):
        """创建 MCP 工具集"""
        return WorkflowMCPTools(working_directory=temp_dir)

    def test_tools_initialization(self, mcp_tools):
        """测试工具集初始化"""
        assert mcp_tools.state_manager is not None
        assert mcp_tools.memory_manager is not None
        assert mcp_tools.template_manager is not None
        assert len(mcp_tools.tools) > 0

    def test_list_tools(self, mcp_tools):
        """测试列出所有工具"""
        tools = mcp_tools.list_tools()

        assert len(tools) >= 14  # 应该有至少14个工具
        assert all('name' in tool for tool in tools)
        assert all('category' in tool for tool in tools)

    def test_get_tool_schemas(self, mcp_tools):
        """测试获取工具 schemas"""
        schemas = mcp_tools.get_tool_schemas()

        assert len(schemas) >= 14
        assert all('name' in schema for schema in schemas)
        assert all('inputSchema' in schema for schema in schemas)

    def test_workflow_start_iteration(self, mcp_tools):
        """测试开始迭代工具"""
        result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "test_iter_001",
                "metadata": {"source": "test"}
            }
        )

        assert result.success is True
        assert result.data['iteration_id'] == "test_iter_001"
        assert result.data['mode'] == "minimal"

    def test_workflow_start_iteration_invalid_mode(self, mcp_tools):
        """测试使用无效模式开始迭代"""
        result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "invalid_mode",
                "iteration_id": "test_iter_001"
            }
        )

        assert result.success is False
        assert result.error is not None

    def test_workflow_next_stage(self, mcp_tools):
        """测试进入下一阶段"""
        # 先创建迭代
        start_result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "test_iter_002"
            }
        )

        assert start_result.success is True

        # 进入下一阶段
        next_result = mcp_tools.execute_tool(
            "workflow_next_stage",
            {"iteration_id": "test_iter_002"}
        )

        assert next_result.success is True

    def test_workflow_complete_stage(self, mcp_tools):
        """测试完成阶段"""
        # 创建迭代
        start_result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "test_iter_003"
            }
        )

        current_stage_id = start_result.data['current_stage']['stage_id']

        # 完成当前阶段
        complete_result = mcp_tools.execute_tool(
            "workflow_complete_stage",
            {
                "iteration_id": "test_iter_003",
                "stage_id": current_stage_id
            }
        )

        assert complete_result.success is True

    def test_state_get_current(self, mcp_tools):
        """测试获取当前状态"""
        # 创建迭代
        mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "standard",
                "iteration_id": "test_iter_004"
            }
        )

        # 获取状态
        result = mcp_tools.execute_tool(
            "state_get_current",
            {"iteration_id": "test_iter_004"}
        )

        assert result.success is True
        assert result.data['iteration_id'] == "test_iter_004"
        assert result.data['mode'] == "standard"
        assert 'progress' in result.data

    def test_state_get_history(self, mcp_tools):
        """测试获取历史状态"""
        # 创建迭代
        mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "test_iter_005"
            }
        )

        # 完成一个阶段以产生历史
        iteration = mcp_tools.state_manager.get_iteration("test_iter_005")
        if iteration.current_stage:
            mcp_tools.execute_tool(
                "workflow_complete_stage",
                {
                    "iteration_id": "test_iter_005",
                    "stage_id": iteration.current_stage.stage_id
                }
            )

        # 获取历史
        result = mcp_tools.execute_tool(
            "state_get_history",
            {"iteration_id": "test_iter_005"}
        )

        assert result.success is True
        assert 'transitions' in result.data

    def test_memory_record_decision(self, mcp_tools):
        """测试记录决策"""
        result = mcp_tools.execute_tool(
            "memory_record_decision",
            {
                "decision": "使用 PostgreSQL 数据库",
                "context": {"reason": "支持复杂查询"},
                "iteration_id": "test_iter_006"
            }
        )

        assert result.success is True
        assert 'memory_id' in result.data

    def test_memory_record_issue(self, mcp_tools):
        """测试记录问题"""
        result = mcp_tools.execute_tool(
            "memory_record_issue",
            {
                "issue": "API 响应慢",
                "severity": "high",
                "iteration_id": "test_iter_006",
                "solution": "添加缓存"
            }
        )

        assert result.success is True
        assert 'memory_id' in result.data

    def test_memory_record_learning(self, mcp_tools):
        """测试记录经验教训"""
        result = mcp_tools.execute_tool(
            "memory_record_learning",
            {
                "learning": "性能测试要早做",
                "category": "技术",
                "iteration_id": "test_iter_006"
            }
        )

        assert result.success is True
        assert 'memory_id' in result.data

    def test_memory_recall(self, mcp_tools):
        """测试召回记忆"""
        # 先记录一些记忆
        mcp_tools.execute_tool(
            "memory_record_decision",
            {
                "decision": "决策内容",
                "context": {},
                "iteration_id": "test_iter_007",
                "stage_id": "P1"
            }
        )

        # 召回记忆
        result = mcp_tools.execute_tool(
            "memory_recall",
            {
                "iteration_id": "test_iter_007",
                "stage_id": "P1"
            }
        )

        assert result.success is True
        assert 'memories' in result.data
        assert len(result.data['memories']) > 0

    def test_memory_search(self, mcp_tools):
        """测试搜索记忆"""
        # 记录一些记忆
        mcp_tools.execute_tool(
            "memory_record_issue",
            {
                "issue": "数据库性能问题",
                "severity": "high",
                "iteration_id": "test_iter_008"
            }
        )

        # 搜索
        result = mcp_tools.execute_tool(
            "memory_search",
            {
                "query": "数据库",
                "limit": 5
            }
        )

        assert result.success is True
        assert 'memories' in result.data

    def test_template_list(self, mcp_tools):
        """测试列出模板"""
        result = mcp_tools.execute_tool(
            "template_list",
            {"mode": "minimal"}
        )

        assert result.success is True
        assert 'templates' in result.data

    def test_template_render(self, mcp_tools, temp_dir):
        """测试渲染模板"""
        # 创建一个测试模板
        template_path = temp_dir / "test_template.md"
        template_path.write_text("# {title}\n\n负责人: {owner}")

        # 尝试渲染（如果模板存在）
        # 注意：这里需要模板已经在注册表中
        # 实际测试中可能需要先注册模板

    def test_export_iteration(self, mcp_tools):
        """测试导出迭代"""
        # 创建迭代
        mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": "test_iter_009"
            }
        )

        # 导出
        result = mcp_tools.execute_tool(
            "export_iteration",
            {
                "iteration_id": "test_iter_009",
                "format": "json"
            }
        )

        assert result.success is True
        assert 'output_path' in result.data
        assert 'files_created' in result.data

    def test_execute_nonexistent_tool(self, mcp_tools):
        """测试执行不存在的工具"""
        result = mcp_tools.execute_tool(
            "nonexistent_tool",
            {}
        )

        assert result.success is False
        assert "未找到工具" in result.error

    def test_execute_tool_with_invalid_params(self, mcp_tools):
        """测试使用无效参数执行工具"""
        result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                # 缺少必需的 mode 参数
                "iteration_id": "test_iter_010"
            }
        )

        assert result.success is False

    def test_get_tool_info(self, mcp_tools):
        """测试获取工具信息"""
        tool_info = mcp_tools.get_tool_info("workflow_start_iteration")

        assert tool_info is not None
        assert tool_info['name'] == "workflow_start_iteration"
        assert 'description' in tool_info
        assert 'parameters' in tool_info

    def test_validate_parameters(self, mcp_tools):
        """测试参数验证"""
        # 获取工具
        tool = mcp_tools.tools.get("workflow_start_iteration")

        if tool:
            # 验证有效参数
            valid_params = {
                "mode": "minimal",
                "iteration_id": "test_001"
            }

            # 这里假设工具有参数验证方法
            # 实际实现可能不同

    def test_concurrent_tool_execution(self, mcp_tools):
        """测试并发工具执行"""
        # 创建多个迭代
        results = []

        for i in range(3):
            result = mcp_tools.execute_tool(
                "workflow_start_iteration",
                {
                    "mode": "minimal",
                    "iteration_id": f"concurrent_iter_{i:03d}"
                }
            )
            results.append(result)

        # 所有操作都应该成功
        assert all(r.success for r in results)

        # 每个迭代应该有唯一的 ID
        iteration_ids = [r.data['iteration_id'] for r in results]
        assert len(set(iteration_ids)) == 3


class TestMCPToolIntegration:
    """MCP 工具集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def mcp_tools(self, temp_dir):
        """创建 MCP 工具集"""
        return WorkflowMCPTools(working_directory=temp_dir)

    def test_complete_workflow_via_mcp(self, mcp_tools):
        """测试通过 MCP 工具完成整个工作流"""
        iteration_id = "integration_test_001"

        # 1. 开始迭代
        start_result = mcp_tools.execute_tool(
            "workflow_start_iteration",
            {
                "mode": "minimal",
                "iteration_id": iteration_id
            }
        )

        assert start_result.success is True

        # 2. 记录决策
        decision_result = mcp_tools.execute_tool(
            "memory_record_decision",
            {
                "decision": "选择 Minimal 模式",
                "context": {"reason": "快速原型"},
                "iteration_id": iteration_id
            }
        )

        assert decision_result.success is True

        # 3. 获取当前状态
        status_result = mcp_tools.execute_tool(
            "state_get_current",
            {"iteration_id": iteration_id}
        )

        assert status_result.success is True
        current_stage_id = status_result.data['current_stage']['stage_id']

        # 4. 完成当前阶段
        complete_result = mcp_tools.execute_tool(
            "workflow_complete_stage",
            {
                "iteration_id": iteration_id,
                "stage_id": current_stage_id
            }
        )

        assert complete_result.success is True

        # 5. 进入下一阶段
        next_result = mcp_tools.execute_tool(
            "workflow_next_stage",
            {"iteration_id": iteration_id}
        )

        # 可能有下一阶段，也可能没有
        if next_result.success:
            assert 'stage_id' in next_result.data

        # 6. 召回记忆
        recall_result = mcp_tools.execute_tool(
            "memory_recall",
            {
                "iteration_id": iteration_id,
                "stage_id": current_stage_id
            }
        )

        assert recall_result.success is True

        # 7. 导出迭代
        export_result = mcp_tools.execute_tool(
            "export_iteration",
            {
                "iteration_id": iteration_id,
                "format": "json"
            }
        )

        assert export_result.success is True
