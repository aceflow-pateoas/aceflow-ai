"""
Document Exporter - 文档导出器

提供完整的文档导出功能
"""

import json
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import ExportFormat, ExportOptions, ExportResult
from ..state import StateManager
from ..memory import MemoryManager
from ..models import Iteration


class DocumentExporter:
    """文档导出器"""

    def __init__(self, state_manager: Optional[StateManager] = None,
                 memory_manager: Optional[MemoryManager] = None):
        """
        初始化导出器

        Args:
            state_manager: 状态管理器 (可选)
            memory_manager: 记忆管理器 (可选)
        """
        self.state_manager = state_manager or StateManager()
        self.memory_manager = memory_manager or MemoryManager()

    def export_iteration(self, iteration_id: str,
                        options: Optional[ExportOptions] = None) -> ExportResult:
        """
        导出单个迭代

        Args:
            iteration_id: 迭代ID
            options: 导出选项

        Returns:
            导出结果
        """
        if options is None:
            options = ExportOptions()

        # 获���迭代数据
        iteration = self.state_manager.get_iteration(iteration_id)
        if not iteration:
            return ExportResult(
                success=False,
                error=f"未找到迭代: {iteration_id}"
            )

        # 根据格式选择导出方法
        try:
            if options.format == ExportFormat.MARKDOWN:
                return self._export_markdown(iteration, options)
            elif options.format == ExportFormat.HTML:
                return self._export_html(iteration, options)
            elif options.format == ExportFormat.JSON:
                return self._export_json(iteration, options)
            elif options.format == ExportFormat.ARCHIVE:
                return self._export_archive(iteration, options)
            else:
                return ExportResult(
                    success=False,
                    error=f"不支持的导出格式: {options.format}"
                )

        except Exception as e:
            return ExportResult(
                success=False,
                error=f"导出失败: {str(e)}"
            )

    def export_all_iterations(self, options: Optional[ExportOptions] = None) -> ExportResult:
        """
        导出所有迭代

        Args:
            options: 导出选项

        Returns:
            导出结果
        """
        if options is None:
            options = ExportOptions()

        iterations = self.state_manager.list_iterations()

        if not iterations:
            return ExportResult(
                success=False,
                error="没有可导出的迭代"
            )

        # 确定输出目录
        output_dir = options.output_dir or Path.cwd() / "aceflow_exports"
        output_dir.mkdir(parents=True, exist_ok=True)

        all_files = []
        errors = []

        # 导出每个迭代
        for iteration in iterations:
            iter_options = ExportOptions(
                format=options.format,
                output_dir=output_dir / iteration.iteration_id,
                **{k: v for k, v in options.__dict__.items()
                   if k not in ['format', 'output_dir']}
            )

            result = self.export_iteration(iteration.iteration_id, iter_options)

            if result.success:
                all_files.extend(result.files_created)
            else:
                errors.append(f"{iteration.iteration_id}: {result.error}")

        # 创建总索引
        if options.create_index:
            index_file = self._create_index(iterations, output_dir, options.format)
            all_files.append(index_file)

        return ExportResult(
            success=len(errors) == 0,
            output_path=output_dir,
            files_created=all_files,
            error="; ".join(errors) if errors else None,
            metadata={
                'total_iterations': len(iterations),
                'successful_exports': len(iterations) - len(errors),
                'failed_exports': len(errors)
            }
        )

    # === Markdown 导出 ===

    def _export_markdown(self, iteration: Iteration, options: ExportOptions) -> ExportResult:
        """导出为 Markdown 格式"""
        output_dir = options.output_dir or Path.cwd() / "aceflow_exports" / iteration.iteration_id
        output_dir.mkdir(parents=True, exist_ok=True)

        files_created = []

        if options.single_file:
            # 单文件模式
            output_file = output_dir / f"{iteration.iteration_id}.md"
            content = self._generate_markdown_single(iteration, options)
            output_file.write_text(content, encoding='utf-8')
            files_created.append(output_file)

        else:
            # 多文件模式
            # 1. 主文档
            main_file = output_dir / "README.md"
            main_content = self._generate_markdown_main(iteration, options)
            main_file.write_text(main_content, encoding='utf-8')
            files_created.append(main_file)

            # 2. 各阶段文档
            stages_dir = output_dir / "stages"
            stages_dir.mkdir(exist_ok=True)

            for stage in iteration.stages:
                stage_file = stages_dir / f"{stage.stage_id}_{stage.name.split('(')[0].strip()}.md"
                stage_content = self._generate_markdown_stage(stage, iteration, options)
                stage_file.write_text(stage_content, encoding='utf-8')
                files_created.append(stage_file)

            # 3. 记忆文档 (如果需要)
            if options.include_memories:
                memories_file = output_dir / "memories.md"
                memories_content = self._generate_markdown_memories(iteration.iteration_id, options)
                memories_file.write_text(memories_content, encoding='utf-8')
                files_created.append(memories_file)

        return ExportResult(
            success=True,
            output_path=output_dir,
            files_created=files_created,
            metadata={'format': 'markdown'}
        )

    def _generate_markdown_single(self, iteration: Iteration, options: ExportOptions) -> str:
        """生成单文件 Markdown"""
        lines = []

        # 标题
        lines.append(f"# {iteration.iteration_id} - 迭代文档\n")

        # 元数据
        if options.include_metadata:
            lines.append("## 📋 元数据\n")
            lines.append(f"- **迭代ID**: {iteration.iteration_id}")
            lines.append(f"- **工作流模式**: {iteration.mode.value}")
            lines.append(f"- **状态**: {iteration.status.value}")
            lines.append(f"- **当前阶段**: {iteration.current_stage.stage_id if iteration.current_stage else 'N/A'}")
            lines.append(f"- **创建时间**: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **最后更新**: {iteration.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

            if iteration.metadata:
                lines.append("### 自定义元数据\n")
                for key, value in iteration.metadata.items():
                    lines.append(f"- **{key}**: {value}")
                lines.append("")

        # 目录
        if options.add_toc:
            lines.append("## 📑 目录\n")
            for i, stage in enumerate(iteration.stages, 1):
                lines.append(f"{i}. [{stage.name}](#{stage.stage_id.lower()})")
            lines.append("")

        # 各阶段内容
        lines.append("## 📊 阶段详情\n")
        for stage in iteration.stages:
            stage_md = self._generate_markdown_stage(stage, iteration, options)
            lines.append(stage_md)
            lines.append("\n---\n")

        # 统计信息
        if options.add_statistics:
            lines.append("## 📈 统计信息\n")
            completed = sum(1 for s in iteration.stages if s.status.value == 'completed')
            lines.append(f"- **总阶段数**: {len(iteration.stages)}")
            lines.append(f"- **已完成**: {completed}")
            lines.append(f"- **进度**: {completed}/{len(iteration.stages)} ({completed*100//len(iteration.stages)}%)")
            lines.append("")

        return "\n".join(lines)

    def _generate_markdown_main(self, iteration: Iteration, options: ExportOptions) -> str:
        """生成主 README"""
        lines = []

        lines.append(f"# {iteration.iteration_id} - 迭代文档\n")
        lines.append(f"> 工作流模式: **{iteration.mode.value}**\n")

        # 概览
        lines.append("## 📊 概览\n")
        lines.append(f"- **状态**: {iteration.status.value}")
        lines.append(f"- **当前阶段**: {iteration.current_stage.name if iteration.current_stage else 'N/A'}")
        lines.append(f"- **创建时间**: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **最后更新**: {iteration.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 阶段列表
        lines.append("## 🔄 阶段\n")
        for stage in iteration.stages:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'skipped': '⏭️',
                'failed': '❌'
            }.get(stage.status.value, '❓')

            lines.append(f"### {status_emoji} [{stage.name}](stages/{stage.stage_id}_{stage.name.split('(')[0].strip()}.md)")
            lines.append(f"- **状态**: {stage.status.value}")
            if stage.description:
                lines.append(f"- **描述**: {stage.description}")
            lines.append("")

        # 相关文档
        lines.append("## 📚 相关文档\n")
        if options.include_memories:
            lines.append("- [记忆和上下文](memories.md)")
        lines.append("")

        return "\n".join(lines)

    def _generate_markdown_stage(self, stage, iteration: Iteration, options: ExportOptions) -> str:
        """生成阶段 Markdown"""
        lines = []

        lines.append(f"## {stage.stage_id}: {stage.name}\n")

        # 状态
        status_emoji = {
            'pending': '⏳ 待处理',
            'in_progress': '🔄 进行中',
            'completed': '✅ 已完成',
            'skipped': '⏭️ 已跳过',
            'failed': '❌ 失败'
        }.get(stage.status.value, '❓ 未知')

        lines.append(f"**状态**: {status_emoji}\n")

        # 描述
        if stage.description:
            lines.append(f"**描述**: {stage.description}\n")

        # 任务列表
        if stage.tasks:
            lines.append("### ✅ 任务清单\n")
            for task in stage.tasks:
                lines.append(f"- {task}")
            lines.append("")

        # 交付物
        if stage.deliverables:
            lines.append("### 📦 交付物\n")
            for deliverable in stage.deliverables:
                lines.append(f"- {deliverable}")
            lines.append("")

        # 元数据
        if stage.metadata and options.include_metadata:
            lines.append("### 📋 元数据\n")
            for key, value in stage.metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def _generate_markdown_memories(self, iteration_id: str, options: ExportOptions) -> str:
        """生成记忆文档"""
        lines = []

        lines.append("# 记忆和上下文\n")

        # 获取迭代摘要
        summary = self.memory_manager.get_iteration_summary(iteration_id)

        lines.append("## 📊 摘要\n")
        lines.append(f"- **总记忆数**: {summary.get('total_memories', 0)}")
        lines.append(f"- **完成阶段**: {summary.get('stages_completed', 0)}")
        lines.append(f"- **决策数**: {summary.get('decisions_made', 0)}")
        lines.append(f"- **问题数**: {summary.get('issues_encountered', 0)}")
        lines.append(f"- **经验教训**: {summary.get('learnings_captured', 0)}\n")

        # 获取所有记忆
        memories = self.memory_manager.store.get_by_iteration(iteration_id)

        if memories:
            lines.append("## 📝 详细记忆\n")

            # 按类型分组
            by_type = {}
            for memory in memories:
                type_key = memory.type.value
                if type_key not in by_type:
                    by_type[type_key] = []
                by_type[type_key].append(memory)

            for type_key, mems in by_type.items():
                lines.append(f"### {type_key.upper()}\n")
                for mem in mems:
                    lines.append(f"**{mem.memory_id}**")
                    lines.append(f"- 内容: {mem.content[:200]}...")
                    lines.append(f"- 优先级: {mem.priority.value}")
                    lines.append(f"- 标签: {', '.join(mem.tags)}")
                    lines.append("")

        return "\n".join(lines)

    # === JSON 导出 ===

    def _export_json(self, iteration: Iteration, options: ExportOptions) -> ExportResult:
        """导出为 JSON 格式"""
        output_dir = options.output_dir or Path.cwd() / "aceflow_exports" / iteration.iteration_id
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{iteration.iteration_id}.json"

        # 构建导出数据
        data = iteration.to_dict()

        # 添加记忆
        if options.include_memories:
            memories = self.memory_manager.store.get_by_iteration(iteration.iteration_id)
            data['memories'] = [m.to_dict() for m in memories]

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return ExportResult(
            success=True,
            output_path=output_dir,
            files_created=[output_file],
            metadata={'format': 'json'}
        )

    # === HTML 导出 ===

    def _export_html(self, iteration: Iteration, options: ExportOptions) -> ExportResult:
        """导出为 HTML 格式"""
        # 先生成 Markdown
        md_result = self._export_markdown(iteration, options)

        if not md_result.success:
            return md_result

        # 简单的 Markdown to HTML 转换
        # 注: 生产环境建议使用 markdown 库
        output_dir = options.output_dir or Path.cwd() / "aceflow_exports" / iteration.iteration_id
        html_file = output_dir / f"{iteration.iteration_id}.html"

        # 读取 markdown
        if options.single_file:
            md_file = output_dir / f"{iteration.iteration_id}.md"
        else:
            md_file = output_dir / "README.md"

        md_content = md_file.read_text(encoding='utf-8')

        # 基本的 HTML 包装
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{iteration.iteration_id} - AceFlow 迭代文档</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
               max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 30px; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
<pre>{md_content}</pre>
</body>
</html>"""

        html_file.write_text(html_content, encoding='utf-8')

        return ExportResult(
            success=True,
            output_path=output_dir,
            files_created=[html_file],
            metadata={'format': 'html'}
        )

    # === Archive 导出 ===

    def _export_archive(self, iteration: Iteration, options: ExportOptions) -> ExportResult:
        """导出为完整文档包 (ZIP)"""
        # 先导出 Markdown
        md_options = ExportOptions(
            format=ExportFormat.MARKDOWN,
            output_dir=options.output_dir,
            single_file=False,
            **{k: v for k, v in options.__dict__.items()
               if k not in ['format', 'output_dir', 'single_file']}
        )

        md_result = self._export_markdown(iteration, md_options)

        if not md_result.success:
            return md_result

        # 创建 ZIP
        output_dir = options.output_dir or Path.cwd() / "aceflow_exports"
        output_dir.mkdir(parents=True, exist_ok=True)

        zip_file = output_dir / f"{iteration.iteration_id}.zip"

        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in md_result.files_created:
                arcname = file_path.relative_to(md_result.output_path.parent)
                zf.write(file_path, arcname)

        return ExportResult(
            success=True,
            output_path=zip_file,
            files_created=[zip_file],
            metadata={'format': 'archive', 'included_files': len(md_result.files_created)}
        )

    # === 工具方法 ===

    def _create_index(self, iterations: List[Iteration], output_dir: Path,
                     export_format: ExportFormat) -> Path:
        """创建总索引文件"""
        index_file = output_dir / "INDEX.md"

        lines = []
        lines.append("# AceFlow 导出索引\n")
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"总迭代数: {len(iterations)}\n")

        lines.append("## 迭代列表\n")

        for iteration in sorted(iterations, key=lambda x: x.created_at, reverse=True):
            lines.append(f"### [{iteration.iteration_id}]({iteration.iteration_id}/README.md)")
            lines.append(f"- **模式**: {iteration.mode.value}")
            lines.append(f"- **状态**: {iteration.status.value}")
            lines.append(f"- **创建时间**: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

        index_file.write_text("\n".join(lines), encoding='utf-8')
        return index_file
