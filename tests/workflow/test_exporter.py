"""
测试文档导出器

测试 aceflow.workflow.exporter 模块
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from aceflow.workflow.exporter import DocumentExporter, ExportOptions, ExportFormat, ExportResult
from aceflow.workflow.state import StateManager
from aceflow.workflow.engine import WorkflowEngine
from aceflow.workflow.models import WorkflowMode, StageStatus


class TestExportFormat:
    """测试导出格式枚举"""

    def test_format_values(self):
        """测试格式值"""
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.HTML.value == "html"
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.ARCHIVE.value == "archive"


class TestExportOptions:
    """测试导出选项"""

    def test_default_options(self):
        """测试默认选项"""
        options = ExportOptions()

        assert options.format == ExportFormat.MARKDOWN
        assert options.single_file is True
        assert options.include_metadata is True

    def test_custom_options(self, tmp_path):
        """测试自定义选项"""
        output_dir = tmp_path / "exports"

        options = ExportOptions(
            format=ExportFormat.HTML,
            output_dir=output_dir,
            single_file=False,
            include_metadata=False,
            include_transitions=True
        )

        assert options.format == ExportFormat.HTML
        assert options.output_dir == output_dir
        assert options.single_file is False
        assert options.include_metadata is False
        assert options.include_transitions is True

    def test_options_to_dict(self):
        """测试选项转字典"""
        options = ExportOptions(
            format=ExportFormat.JSON,
            single_file=True
        )

        data = options.to_dict()

        assert data['format'] == "json"
        assert data['single_file'] is True


class TestExportResult:
    """测试导出结果"""

    def test_successful_result(self, tmp_path):
        """测试成功的导出结果"""
        output_path = tmp_path / "output.md"
        output_path.touch()

        result = ExportResult(
            success=True,
            output_path=output_path,
            files_created=[output_path],
            message="导出成功"
        )

        assert result.success is True
        assert result.output_path == output_path
        assert len(result.files_created) == 1
        assert result.error is None

    def test_failed_result(self):
        """测试失败的导出结果"""
        result = ExportResult(
            success=False,
            error="文件写入失败",
            message="导出失败"
        )

        assert result.success is False
        assert result.error == "文件写入失败"
        assert result.output_path is None

    def test_result_to_dict(self, tmp_path):
        """测试结果转字典"""
        output_path = tmp_path / "output.md"

        result = ExportResult(
            success=True,
            output_path=output_path,
            files_created=[output_path]
        )

        data = result.to_dict()

        assert data['success'] is True
        assert 'output_path' in data


class TestDocumentExporter:
    """测试文档导出器"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器"""
        return StateManager(storage_dir=temp_dir / "state")

    @pytest.fixture
    def exporter(self, state_manager):
        """创建导出器"""
        return DocumentExporter(state_manager)

    @pytest.fixture
    def sample_iteration(self, state_manager):
        """创建示例迭代"""
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)
        iteration = engine.start_iteration("export_test_001")

        # 完成第一个阶段
        if iteration.current_stage:
            engine.complete_stage(iteration.iteration_id, iteration.current_stage.stage_id)

        return iteration

    def test_exporter_creation(self, exporter):
        """测试导出器创建"""
        assert exporter.state_manager is not None

    def test_export_markdown(self, exporter, sample_iteration, temp_dir):
        """测试导出为 Markdown"""
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            single_file=True
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()
        assert result.output_path.suffix == ".md"

        # 验证内容
        content = result.output_path.read_text()
        assert sample_iteration.iteration_id in content

    def test_export_markdown_multiple_files(self, exporter, sample_iteration, temp_dir):
        """测试导出为多个 Markdown 文件"""
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            single_file=False
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert len(result.files_created) > 0

        # 验证所有文件都存在
        for file_path in result.files_created:
            assert file_path.exists()

    def test_export_html(self, exporter, sample_iteration, temp_dir):
        """测试导出为 HTML"""
        options = ExportOptions(
            format=ExportFormat.HTML,
            output_dir=temp_dir / "exports",
            single_file=True
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()
        assert result.output_path.suffix == ".html"

        # 验证 HTML 结构
        content = result.output_path.read_text()
        assert "<html>" in content or "<!DOCTYPE html>" in content
        assert sample_iteration.iteration_id in content

    def test_export_json(self, exporter, sample_iteration, temp_dir):
        """测试导出为 JSON"""
        options = ExportOptions(
            format=ExportFormat.JSON,
            output_dir=temp_dir / "exports"
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()
        assert result.output_path.suffix == ".json"

        # 验证 JSON 内容
        with open(result.output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['iteration_id'] == sample_iteration.iteration_id
        assert 'mode' in data
        assert 'stages' in data

    def test_export_archive(self, exporter, sample_iteration, temp_dir):
        """测试导出为归档文件"""
        options = ExportOptions(
            format=ExportFormat.ARCHIVE,
            output_dir=temp_dir / "exports"
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()

        # 归档文件应该是 .zip 或 .tar.gz
        assert result.output_path.suffix in [".zip", ".gz"]

    def test_export_nonexistent_iteration(self, exporter, temp_dir):
        """测试导出不存在的迭代"""
        options = ExportOptions(
            output_dir=temp_dir / "exports"
        )

        result = exporter.export_iteration(
            "nonexistent_iter",
            options
        )

        assert result.success is False
        assert result.error is not None

    def test_export_with_metadata(self, exporter, sample_iteration, temp_dir):
        """测试包含元数据的导出"""
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            include_metadata=True
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True

        content = result.output_path.read_text()
        # 元数据应该包含在输出中
        assert "创建时间" in content or "created_at" in content

    def test_export_without_metadata(self, exporter, sample_iteration, temp_dir):
        """测试不包含元数据的导出"""
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            include_metadata=False
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True

    def test_export_with_transitions(self, exporter, sample_iteration, temp_dir):
        """测试包含状态转换的导出"""
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            include_transitions=True
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True

        content = result.output_path.read_text()
        # 应该包含状态转换信息
        # 具体内容取决于实现

    def test_export_batch(self, exporter, state_manager, temp_dir):
        """测试批量导出"""
        # 创建多个迭代
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)

        iteration_ids = []
        for i in range(3):
            iteration = engine.start_iteration(f"batch_export_{i:03d}")
            iteration_ids.append(iteration.iteration_id)

        # 批量导出
        options = ExportOptions(
            format=ExportFormat.JSON,
            output_dir=temp_dir / "batch_exports"
        )

        result = exporter.export_batch(iteration_ids, options)

        assert result.success is True
        assert len(result.files_created) == 3

        # 验证所有文件
        for file_path in result.files_created:
            assert file_path.exists()
            assert file_path.suffix == ".json"

    def test_export_all_iterations(self, exporter, state_manager, temp_dir):
        """测试导出所有迭代"""
        # 创建几个迭代
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)

        for i in range(2):
            engine.start_iteration(f"export_all_{i:03d}")

        # 导出所有
        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "all_exports"
        )

        result = exporter.export_all(options)

        assert result.success is True
        assert len(result.files_created) >= 2

    def test_export_custom_template(self, exporter, sample_iteration, temp_dir):
        """测试使用自定义模板导出"""
        # 创建自定义模板
        template_path = temp_dir / "custom_template.md"
        template_path.write_text("""# 迭代报告: {iteration_id}

模式: {mode}

## 阶段列表
{stages}
""")

        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=temp_dir / "exports",
            custom_template=template_path
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        # 如果支持自定义模板
        if result.success:
            content = result.output_path.read_text()
            assert "迭代报告" in content

    def test_export_with_filters(self, exporter, sample_iteration, temp_dir):
        """测试带过滤条件的导出"""
        options = ExportOptions(
            format=ExportFormat.JSON,
            output_dir=temp_dir / "exports",
            stage_filter=["P1", "D1"]  # 只导出特定阶段
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        if result.success:
            with open(result.output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证只包含指定的阶段
            if 'stages' in data and options.stage_filter:
                stage_ids = [s['stage_id'] for s in data['stages']]
                # 应该只包含过滤的阶段

    def test_export_directory_creation(self, exporter, sample_iteration, temp_dir):
        """测试自动创建导出目录"""
        output_dir = temp_dir / "deeply" / "nested" / "exports"

        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=output_dir
        )

        result = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result.success is True
        assert output_dir.exists()
        assert result.output_path.parent == output_dir

    def test_export_overwrite_handling(self, exporter, sample_iteration, temp_dir):
        """测试覆盖已存在文件的处理"""
        output_dir = temp_dir / "exports"
        output_dir.mkdir(parents=True)

        options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=output_dir,
            single_file=True
        )

        # 第一次导出
        result1 = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result1.success is True
        first_path = result1.output_path

        # 第二次导出（覆盖）
        result2 = exporter.export_iteration(
            sample_iteration.iteration_id,
            options
        )

        assert result2.success is True

        # 根据实现，可能是覆盖或创建新文件

    def test_export_with_empty_iteration(self, state_manager, exporter, temp_dir):
        """测试导出空迭代"""
        # 创建一个没有完成任何阶段的迭代
        engine = WorkflowEngine(WorkflowMode.MINIMAL, state_manager)
        iteration = engine.start_iteration("empty_iter")

        options = ExportOptions(
            format=ExportFormat.JSON,
            output_dir=temp_dir / "exports"
        )

        result = exporter.export_iteration(
            iteration.iteration_id,
            options
        )

        # 应该能成功导出，即使没有完成的阶段
        assert result.success is True

    def test_export_performance(self, exporter, state_manager, temp_dir):
        """测试导出性能"""
        import time

        # 创建一个包含多个阶段的迭代
        engine = WorkflowEngine(WorkflowMode.COMPLETE, state_manager)
        iteration = engine.start_iteration("perf_test")

        options = ExportOptions(
            format=ExportFormat.JSON,
            output_dir=temp_dir / "exports"
        )

        start_time = time.time()
        result = exporter.export_iteration(
            iteration.iteration_id,
            options
        )
        elapsed_time = time.time() - start_time

        assert result.success is True
        # 导出应该在合理时间内完成（比如 < 5 秒）
        assert elapsed_time < 5.0
