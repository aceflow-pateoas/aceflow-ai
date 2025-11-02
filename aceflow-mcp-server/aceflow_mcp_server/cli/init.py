"""
CLI command: aceflow init

Initialize aceflow configuration for a project.
"""

import os
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from ..contract.config import ContractConfig


console = Console()


@click.command()
@click.option('--project-name', help='Project name')
@click.option('--openapi-url', help='OpenAPI URL (e.g., http://localhost:8080/v3/api-docs)')
@click.option('--contract-repo', help='Contract repository URL')
@click.option('--smtp-host', help='SMTP server host')
@click.option('--smtp-port', type=int, help='SMTP server port')
@click.option('--smtp-user', help='SMTP username')
@click.option('--smtp-from', help='From email address')
@click.option('--non-interactive', is_flag=True, help='Non-interactive mode (use with options)')
def init(
    project_name: Optional[str],
    openapi_url: Optional[str],
    contract_repo: Optional[str],
    smtp_host: Optional[str],
    smtp_port: Optional[int],
    smtp_user: Optional[str],
    smtp_from: Optional[str],
    non_interactive: bool
):
    """
    Initialize AceFlow configuration for contract management.

    This command creates a .aceflow/config.yaml file with project settings.
    """
    console.print("\n[bold cyan]🚀 AceFlow 契约管理初始化[/bold cyan]\n")

    config_path = Path.cwd() / ".aceflow" / "config.yaml"

    # Check if config already exists
    if config_path.exists():
        if not non_interactive:
            overwrite = Confirm.ask(
                f"配置文件已存在: {config_path}\n是否覆盖？",
                default=False
            )
            if not overwrite:
                console.print("[yellow]初始化已取消[/yellow]")
                return
        else:
            console.print(f"[yellow]⚠️  配置文件已存在: {config_path}[/yellow]")
            return

    # Interactive mode
    if not non_interactive:
        console.print("[bold]请输入项目配置:[/bold]\n")

        project_name = Prompt.ask(
            "📦 项目名称",
            default=Path.cwd().name
        )

        openapi_url = Prompt.ask(
            "🔗 OpenAPI 地址",
            default="http://localhost:8080/v3/api-docs"
        )

        contract_repo = Prompt.ask(
            "📁 契约仓库地址 (Git URL)",
            default=""
        )

        # SMTP configuration
        console.print("\n[bold]邮件通知配置 (可选，按 Enter 跳过):[/bold]\n")

        smtp_host = Prompt.ask(
            "📧 SMTP 服务器地址",
            default=""
        )

        if smtp_host:
            smtp_port = int(Prompt.ask(
                "📧 SMTP 端口",
                default="587"
            ))

            smtp_user = Prompt.ask(
                "📧 SMTP 用户名",
                default=""
            )

            smtp_password = Prompt.ask(
                "📧 SMTP 密码",
                password=True,
                default=""
            )

            smtp_from = Prompt.ask(
                "📧 发件人邮箱",
                default=smtp_user
            )
        else:
            smtp_password = ""

    # Create configuration
    config = ContractConfig(config_path)

    # Set basic configuration
    config.project_name = project_name
    config.openapi_url = openapi_url

    if contract_repo:
        config.contract_repo_url = contract_repo

    # Set SMTP configuration if provided
    if smtp_host and smtp_user:
        config.set_smtp_config(
            host=smtp_host,
            port=smtp_port or 587,
            user=smtp_user,
            password=smtp_password or "",
            from_email=smtp_from or smtp_user
        )

    # Initialize smart completion rules (default)
    if 'aceflow' not in config._config:
        config._config['aceflow'] = {}

    config._config['aceflow']['smart_completion'] = {
        'enabled': True,
        'rules': [
            {'pattern': '.*[Dd]ate$', 'example': '2025-01-01'},
            {'pattern': '.*[Uu]uid$', 'example': '550e8400-e29b-41d4-a716-446655440000'},
            {'pattern': '.*[Ii]d$', 'example': 12345},
            {'pattern': '.*[Ee]mail$', 'example': 'user@example.com'},
            {'pattern': '.*[Pp]hone$', 'example': '13800138000'},
        ]
    }

    # Save configuration
    config.save()

    # Success message
    console.print("\n[bold green]✅ 初始化成功！[/bold green]\n")
    console.print(f"📄 配置文件已创建: [cyan]{config_path}[/cyan]\n")

    console.print("[bold]配置摘要:[/bold]")
    console.print(f"  项目名称: {project_name}")
    console.print(f"  OpenAPI: {openapi_url}")
    if contract_repo:
        console.print(f"  契约仓库: {contract_repo}")
    if smtp_host:
        console.print(f"  SMTP: {smtp_host}:{smtp_port}")

    console.print("\n[bold]下一步:[/bold]")
    console.print("  添加需求配置: [cyan]aceflow feature add[/cyan]")
    console.print("  生成契约: [cyan]aceflow contract generate --feature <name>[/cyan]\n")


if __name__ == '__main__':
    init()
