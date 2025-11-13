"""
Export CLI - 导出AceFlow规范和模板

一键导出功能:导出完整的规范文档+提示词+模板文件，用于纯提示词驱动的AI工作流
"""

import click
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime

console = Console()


@click.group(name='export')
def export_group():
    """导出AceFlow规范和模板"""
    pass


@export_group.command()
@click.option('--mode', type=click.Choice(['standard', 'complete', 'both']),
              default='both', help='导出模式 (standard/complete/both)')
@click.option('--output', '-o', type=click.Path(), default=None,
              help='输出目录 (默认: ./.aceflow/templates/)')
@click.option('--include-spec', is_flag=True, default=True,
              help='包含SPEC规范文档')
@click.option('--include-readme', is_flag=True, default=True,
              help='包含README使用说明')
def templates(mode, output, include_spec, include_readme):
    """
    一键导出AceFlow模板包到项目

    导出内容:
    - SPEC.md规范文档
    - README.md使用说明
    - complete/或standard/模板文件

    用途:
    - 集成到项目的 .aceflow/templates/ 目录
    - 纯提示词驱动的AI工作流
    - 自定义模板修改

    示例:
        aceflow export templates                    # 导出到 ./.aceflow/templates/
        aceflow export templates --mode complete    # 只导出complete模式
        aceflow export templates -o /custom/path/   # 自定义路径
    """
    try:
        # 确定输出目录
        if output is None:
            # 默认导出到当前项目的 .aceflow/templates/
            output_dir = Path.cwd() / ".aceflow" / "templates"
        else:
            output_dir = Path(output)

        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定模板源目录
        # 开发环境路径: aceflow-ai/aceflow-mcp-server/aceflow_mcp_server/cli/export.py
        # 模板路径: aceflow-ai/aceflow/templates/
        current_file = Path(__file__).resolve()

        # 先尝试相对路径（开发环境）
        # current_file.parent.parent.parent.parent -> aceflow-ai/
        project_root = current_file.parent.parent.parent.parent
        template_source = project_root / "aceflow" / "templates"

        # 如果不存在，尝试从当前工作目录查找
        if not template_source.exists():
            # 可能在安装后的环境，尝试从包数据查找
            cwd_templates = Path.cwd() / "aceflow" / "templates"
            if cwd_templates.exists():
                template_source = cwd_templates

        if not template_source.exists():
            console.print(f"[red]✗[/red] 模板目录不存在: {template_source}")
            console.print(f"[yellow]提示:[/yellow] 请确保在AceFlow项目根目录下运行")
            return

        console.print(f"[cyan]→[/cyan] 导出模板到: {output_dir}")
        console.print(f"[cyan]→[/cyan] 模板源: {template_source}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # 1. 导出SPEC文档
            if include_spec:
                task = progress.add_task("导出SPEC规范文档...", total=None)
                spec_file = template_source / "SPEC.md"
                if spec_file.exists():
                    shutil.copy2(spec_file, output_dir / "SPEC.md")
                    console.print(f"[green]✓[/green] SPEC.md ({spec_file.stat().st_size} bytes)")
                else:
                    console.print(f"[yellow]⚠[/yellow] SPEC.md不存在，跳过")
                progress.remove_task(task)

            # 2. 导出README
            if include_readme:
                task = progress.add_task("导出README说明...", total=None)
                readme_file = template_source / "README.md"
                if readme_file.exists():
                    shutil.copy2(readme_file, output_dir / "README.md")
                    console.print(f"[green]✓[/green] README.md ({readme_file.stat().st_size} bytes)")
                progress.remove_task(task)

            # 3. 导出模板文件
            modes_to_export = []
            if mode == 'both':
                modes_to_export = ['standard', 'complete']
            else:
                modes_to_export = [mode]

            for mode_name in modes_to_export:
                task = progress.add_task(f"导出 {mode_name} 模式模板...", total=None)

                mode_source = template_source / mode_name
                mode_dest = output_dir / mode_name

                if not mode_source.exists():
                    console.print(f"[yellow]⚠[/yellow] {mode_name} 模板目录不存在，跳过")
                    progress.remove_task(task)
                    continue

                # 复制整个目录
                shutil.copytree(mode_source, mode_dest, dirs_exist_ok=True)

                # 统计文件
                template_files = list(mode_dest.glob("*.md"))
                template_count = len([f for f in template_files if f.name != "README.md"])

                console.print(f"[green]✓[/green] {mode_name}/ ({template_count} 个模板文件)")

                progress.remove_task(task)

        # 4. 生成使用说明
        usage_file = output_dir / "USAGE.md"
        usage_content = _generate_usage_guide(modes_to_export)
        usage_file.write_text(usage_content, encoding='utf-8')
        console.print(f"[green]✓[/green] USAGE.md (使用指南)")

        # 5. 汇总
        console.print()
        console.print(f"[bold green]✓ 导出完成！[/bold green]")
        console.print(f"[cyan]→[/cyan] 输出目录: {output_dir.absolute()}")
        console.print()
        console.print("[bold]导出文件:[/bold]")
        for file in sorted(output_dir.rglob("*")):
            if file.is_file():
                rel_path = file.relative_to(output_dir)
                console.print(f"  • {rel_path}")

        console.print()
        console.print("[bold]下一步:[/bold]")
        console.print("  1. 查看 USAGE.md 了解如何使用")
        console.print("  2. 将模板文件提供给AI助手")
        console.print("  3. 基于SPEC.md开始工作流")

    except Exception as e:
        console.print(f"[red]✗ 导出失败: {str(e)}[/red]")
        raise


def _generate_usage_guide(modes: list) -> str:
    """生成使用指南"""
    return f"""# AceFlow 模板包使用指南

> 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 导出模式: {', '.join(modes)}

## 📁 项目目录结构

将AceFlow集成到你的项目后的推荐目录结构：

```
my-project/                              # 你的项目根目录
├── .aceflow/                            # AceFlow配置和模板
│   ├── config.yaml                      # 项目配置（aceflow init生成）
│   ├── current_state.json               # 工作流状态（MCP自动生成）
│   └── templates/                       # 模板库（本次导出的内容）
│       ├── SPEC.md                      # AceFlow v3.1 规范
│       ├── README.md                    # 模板说明
│       ├── USAGE.md                     # 本使用指南
{_format_mode_structure(modes)}
│
├── aceflow_result/                      # 工作流执行结果
│   └── iter_20250113_001/               # 迭代目录
│       └── {modes[0]}/                  # 使用的模式
│           ├── user_stories.md          # AI填充后的文档
│           ├── task_breakdown.md
│           └── ...
│
├── src/                                 # 项目源码
└── README.md                            # 项目文档
```

## 🚀 快速开始

### 步骤1: 初始化项目配置（可选）

如果需要使用MCP集成，先初始化配置：

```bash
cd my-project
aceflow init
```

### 步骤2: 导出模板到项目

```bash
# 导出到默认位置 .aceflow/templates/
aceflow export templates

# 或指定模式
aceflow export templates --mode standard
```

### 步骤3: 开始使用

**方式A - 纯提示词驱动（推荐新手）**:

1. 手动创建结果目录: `mkdir -p aceflow_result/iter_001/{modes[0]}`
2. 与AI对话时引用模板文件

示例对话:
```
User: 请根据 .aceflow/templates/{modes[0]}/user_stories.md 模板，
      为"用户登录"功能编写用户故事

AI: [基于模板生成内容]

User: 保存到 aceflow_result/iter_001/{modes[0]}/user_stories.md
```

**方式B - MCP集成（推荐熟练用户）**:

配置Claude Code或Cline后，AI会自动：
- 调用MCP工具管理工作流
- 基于 `.aceflow/templates/` 生成文档
- 保存到 `aceflow_result/` 目录
- 追踪工作流状态

## 📋 工作流模式

### Standard模式 (7阶段)
适用于大多数项目的日常开发，周期5-10天

阶段顺序:
1. user_stories - 用户故事
2. task_breakdown - 任务分解
3. test_design - 测试设计
4. implementation - 功能实现
5. unit_test - 单元测试
6. integration_test - 集成测试
7. code_review - 代码审查

### Complete模式 (10阶段)
适用于大型项目、关键系统，周期2-4周

阶段顺序:
1. requirement_analysis - 需求分析
2. architecture_design - 架构设计
3. user_stories - 用户故事
4. task_breakdown - 任务分解
5. test_design - 测试设计
6. implementation - 功能实现
7. unit_test - 单元测试
8. integration_test - 集成测试
9. performance_test - 性能测试
10. code_review - 代码审查

## 💡 使用提示

### 1. 版本控制建议

`.gitignore` 配置:
```
# AceFlow运行时状态（不提交）
.aceflow/current_state.json

# 保留模板和配置（提交到Git）
!.aceflow/config.yaml
!.aceflow/templates/

# 执行结果（可选：提交作为项目文档）
aceflow_result/
```

### 2. 团队协作

- 将 `.aceflow/templates/` 提交到Git，团队共享统一标准
- 可自定义编辑模板适应团队规范
- `aceflow_result/` 可作为项目文档提交

### 3. 模板自定义

模板文件位于 `.aceflow/templates/{modes[0]}/`，可以：
- 修改模板格式适应项目需求
- 添加团队特定的检查项
- 调整文档结构

### 4. 多迭代管理

每次新功能开发创建新的迭代目录：
```
aceflow_result/
├── iter_001/    # 第一次迭代
├── iter_002/    # 第二次迭代
└── iter_003/    # 第三次迭代
```

## 📖 AI提示词示例

### 开始新的工作流

```
我要开始一个新功能"用户认证"的开发，使用AceFlow的Standard模式。

请从第一个阶段开始，参考 .aceflow/templates/standard/user_stories.md 模板，
生成用户故事文档并保存到 aceflow_result/iter_001/standard/user_stories.md
```

### 推进到下一阶段

```
用户故事阶段已完成，现在进入任务分解阶段。

请参考 .aceflow/templates/standard/task_breakdown.md 模板，
基于已有的用户故事，分解开发任务。
```

## 🔗 相关资源

- **完整规范**: 查看 `.aceflow/templates/SPEC.md`
- **模板说明**: 查看 `.aceflow/templates/README.md`
- **MCP集成**: `pip install aceflow-mcp-server`
- **GitHub**: https://github.com/aceflow/aceflow-ai

---

**提示**: `.aceflow/` 是隐藏目录，保持项目根目录整洁。使用 `ls -la` 查看。
"""


def _format_mode_structure(modes: list) -> str:
    """格式化模式目录结构"""
    lines = []
    for mode in modes:
        if mode == 'standard':
            lines.append("│       ├── standard/                 # Standard模式(7阶段)")
            lines.append("│       │   ├── user_stories.md")
            lines.append("│       │   ├── task_breakdown.md")
            lines.append("│       │   └── ...（7个模板文件）")
        elif mode == 'complete':
            lines.append("│       ├── complete/                # Complete模式(10阶段)")
            lines.append("│       │   ├── requirement_analysis.md")
            lines.append("│       │   ├── architecture_design.md")
            lines.append("│       │   └── ...（10个模板文件）")
    return '\n'.join(lines)
