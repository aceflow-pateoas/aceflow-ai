"""
CLI command: aceflow contract generate

Generate filtered OpenAPI contracts for features.
"""

import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional
import json

from ..contract.config import ContractConfig
from ..contract.generator import ContractGenerator
from ..contract.filter import ContractFilter
from ..contract.completion import SmartCompletion
from ..contract.repo import ContractRepo
from ..notification.email import EmailNotifier


console = Console()


@click.group(name='contract')
def contract_group():
    """
    Manage OpenAPI contracts for features.
    """
    pass


@contract_group.command(name='generate')
@click.option('--feature', required=True, help='Feature name to generate contract for')
@click.option('--output', help='Output file path (default: .aceflow/contracts/<feature>.json)')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Output format')
@click.option('--no-smart-completion', is_flag=True, help='Disable smart completion')
def generate_contract(
    feature: str,
    output: Optional[str],
    format: str,
    no_smart_completion: bool
):
    """
    Generate filtered OpenAPI contract for a feature.

    Example:
        aceflow contract generate --feature user-management
        aceflow contract generate --feature user-management --output contract.yaml --format yaml
    """
    console.print("\n[bold cyan]📝 生成契约文件[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)

    # Get feature configuration
    feature_config = config.get_feature(feature)
    if not feature_config:
        console.print(f"[red]❌ 错误: 需求 '{feature}' 不存在[/red]")
        console.print("[yellow]请先运行: aceflow feature add[/yellow]\n")
        return

    # Display feature info
    console.print(f"[bold]需求:[/bold] [cyan]{feature}[/cyan]")
    description = feature_config.get('description', '')
    if description:
        console.print(f"[bold]描述:[/bold] {description}")

    api_filter_config = feature_config.get('api_filter', {})
    filter_type = api_filter_config.get('type', 'prefix')
    pattern = api_filter_config.get('pattern', '')
    console.print(f"[bold]过滤规则:[/bold] [{filter_type}] {pattern}\n")

    # Get OpenAPI URL
    openapi_url = config.openapi_url
    if not openapi_url:
        console.print("[red]❌ 错误: 未配置 OpenAPI URL[/red]")
        console.print("[yellow]请在 .aceflow/config.yaml 中配置 openapi_url[/yellow]\n")
        return

    try:
        # Step 1: Fetch OpenAPI spec
        generator = ContractGenerator(openapi_url)
        openapi_spec = generator.fetch_openapi()

        # Step 2: Filter paths
        contract_filter = ContractFilter(api_filter_config)
        filtered_spec = contract_filter.filter_paths(openapi_spec)

        # Check if any paths matched
        if len(filtered_spec.get('paths', {})) == 0:
            console.print("[yellow]⚠️  没有匹配的接口，契约文件将为空[/yellow]")
            console.print("[yellow]请检查过滤规则是否正确[/yellow]\n")
            # Continue to save empty contract

        # Step 3: Apply smart completion
        if not no_smart_completion and config.smart_completion_enabled:
            completion_rules = config.get_completion_rules()
            smart_completion = SmartCompletion(completion_rules, enabled=True)
            filtered_spec = smart_completion.apply_to_openapi(filtered_spec)
        else:
            if no_smart_completion:
                console.print("[dim]智能补全已跳过（--no-smart-completion）[/dim]\n")
            else:
                console.print("[dim]智能补全已禁用（配置）[/dim]\n")

        # Step 4: Save to file
        if not output:
            # Default output path
            output_dir = Path.cwd() / ".aceflow" / "contracts"
            output_dir.mkdir(parents=True, exist_ok=True)
            extension = 'yaml' if format == 'yaml' else 'json'
            output = str(output_dir / f"{feature}.{extension}")

        generator.save_to_file(filtered_spec, output)

        # Display statistics
        stats = contract_filter.get_statistics(openapi_spec)
        console.print("[bold]生成统计:[/bold]")
        console.print(f"  匹配路径: [cyan]{stats['matched_paths']}[/cyan] / {stats['total_paths']}")
        console.print(f"  匹配操作: [cyan]{stats['matched_operations']}[/cyan] / {stats['total_operations']}")
        console.print(f"  输出文件: [cyan]{output}[/cyan]\n")

        console.print("[bold green]✅ 契约生成成功！[/bold green]\n")

        # Next steps
        console.print("[bold]下一步:[/bold]")
        console.print(f"  查看文件: [cyan]cat {output}[/cyan]")
        console.print(f"  提交到 Git: [cyan]aceflow contract push --feature {feature}[/cyan]\n")

    except Exception as e:
        console.print(f"[red]❌ 生成失败: {e}[/red]\n")
        import traceback
        if console.is_terminal:
            console.print("[dim]详细错误信息:[/dim]")
            console.print(f"[dim]{traceback.format_exc()}[/dim]\n")
        raise click.Abort()


@contract_group.command(name='list')
def list_contracts():
    """
    List all generated contracts.
    """
    console.print("\n[bold cyan]📋 契约文件列表[/bold cyan]\n")

    contracts_dir = Path.cwd() / ".aceflow" / "contracts"
    if not contracts_dir.exists():
        console.print("[yellow]暂无契约文件[/yellow]")
        console.print("\n[bold]生成契约:[/bold]")
        console.print("  [cyan]aceflow contract generate --feature <name>[/cyan]\n")
        return

    # Find all contract files
    contract_files = list(contracts_dir.glob("*.json")) + list(contracts_dir.glob("*.yaml")) + list(contracts_dir.glob("*.yml"))

    if not contract_files:
        console.print("[yellow]暂无契约文件[/yellow]\n")
        return

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("需求名称", style="cyan")
    table.add_column("文件名", style="green")
    table.add_column("格式", style="yellow")
    table.add_column("大小", style="magenta")

    for contract_file in sorted(contract_files):
        feature_name = contract_file.stem
        file_name = contract_file.name
        file_format = contract_file.suffix[1:].upper()
        file_size = contract_file.stat().st_size

        # Format size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        table.add_row(feature_name, file_name, file_format, size_str)

    console.print(table)
    console.print()


@contract_group.command(name='show')
@click.argument('feature')
def show_contract(feature: str):
    """
    Show contract file information.

    Example:
        aceflow contract show user-management
    """
    console.print(f"\n[bold cyan]📄 契约详情: {feature}[/bold cyan]\n")

    contracts_dir = Path.cwd() / ".aceflow" / "contracts"

    # Try to find contract file
    contract_file = None
    for ext in ['.json', '.yaml', '.yml']:
        potential_file = contracts_dir / f"{feature}{ext}"
        if potential_file.exists():
            contract_file = potential_file
            break

    if not contract_file:
        console.print(f"[red]❌ 契约文件不存在: {feature}[/red]")
        console.print(f"[yellow]请先生成: aceflow contract generate --feature {feature}[/yellow]\n")
        return

    # Load and display contract info
    try:
        if contract_file.suffix == '.json':
            with open(contract_file, 'r', encoding='utf-8') as f:
                contract_spec = json.load(f)
        else:
            import yaml
            with open(contract_file, 'r', encoding='utf-8') as f:
                contract_spec = yaml.safe_load(f)

        info = contract_spec.get('info', {})
        paths = contract_spec.get('paths', {})

        console.print(f"[bold]文件路径:[/bold] {contract_file}")
        console.print(f"[bold]文件大小:[/bold] {contract_file.stat().st_size} 字节")
        console.print(f"[bold]OpenAPI 版本:[/bold] {contract_spec.get('openapi', contract_spec.get('swagger', 'Unknown'))}")
        console.print(f"[bold]API 标题:[/bold] {info.get('title', 'Unknown')}")
        console.print(f"[bold]API 版本:[/bold] {info.get('version', 'Unknown')}")
        console.print(f"[bold]接口数量:[/bold] {len(paths)} 个\n")

        if paths:
            console.print("[bold]接口列表:[/bold]")
            for path in sorted(paths.keys()):
                console.print(f"  [cyan]{path}[/cyan]")
            console.print()

    except Exception as e:
        console.print(f"[red]❌ 读取失败: {e}[/red]\n")


@contract_group.command(name='push')
@click.option('--feature', required=True, help='Feature name to push contract for')
@click.option('--message', help='Custom commit message')
@click.option('--branch', default='main', help='Git branch (default: main)')
def push_contract(feature: str, message: Optional[str], branch: str):
    """
    Push contract to Git repository.

    Example:
        aceflow contract push --feature user-management
        aceflow contract push --feature user-management --message "Update user API contract"
    """
    console.print("\n[bold cyan]⬆️  推送契约到仓库[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)

    # Check if feature exists
    feature_config = config.get_feature(feature)
    if not feature_config:
        console.print(f"[red]❌ 错误: 需求 '{feature}' 不存在[/red]")
        console.print("[yellow]请先运行: aceflow feature add[/yellow]\n")
        return

    # Check if contract repo is configured
    repo_url = config.contract_repo_url
    if not repo_url:
        console.print("[red]❌ 错误: 未配置契约仓库 URL[/red]")
        console.print("[yellow]请在 .aceflow/config.yaml 中配置 contract_repo.url[/yellow]\n")
        return

    # Find contract file
    contracts_dir = Path.cwd() / ".aceflow" / "contracts"
    contract_file = None

    for ext in ['.json', '.yaml', '.yml']:
        potential_file = contracts_dir / f"{feature}{ext}"
        if potential_file.exists():
            contract_file = potential_file
            break

    if not contract_file:
        console.print(f"[red]❌ 错误: 契约文件不存在: {feature}[/red]")
        console.print(f"[yellow]请先生成: aceflow contract generate --feature {feature}[/yellow]\n")
        return

    # Display info
    console.print(f"[bold]需求:[/bold] [cyan]{feature}[/cyan]")
    console.print(f"[bold]契约文件:[/bold] {contract_file.name}")
    console.print(f"[bold]仓库:[/bold] {repo_url}")
    console.print(f"[bold]分支:[/bold] {branch}\n")

    # Push to repository
    try:
        repo = ContractRepo(repo_url)
        base_path = config.contract_repo_base_path

        success, result_message = repo.push_contract(
            contract_file=contract_file,
            feature_name=feature,
            base_path=base_path,
            branch=branch,
            commit_message=message
        )

        if success:
            console.print(f"[bold green]✅ {result_message}[/bold green]\n")

            # Send email notification
            smtp_config = config.smtp_config
            if smtp_config:
                try:
                    # Get dev team emails
                    dev_team = feature_config.get('dev_team', [])

                    # For MVP, assume dev_team contains email addresses
                    # In production, you might need to map usernames to emails
                    recipients = [member for member in dev_team if '@' in member]

                    if recipients:
                        notifier = EmailNotifier(smtp_config)

                        # Extract commit hash from result message if present
                        commit_hash = None
                        if '(' in result_message and ')' in result_message:
                            commit_hash = result_message.split('(')[-1].split(')')[0]

                        notifier.send_contract_update_notification(
                            feature_name=feature,
                            contract_url=repo_url,
                            recipients=recipients,
                            commit_hash=commit_hash,
                            dev_team=dev_team,
                            custom_message=message
                        )
                except Exception as e:
                    console.print(f"[yellow]⚠️  邮件通知失败: {e}[/yellow]")
                    console.print("[yellow]契约已推送成功，但邮件通知未发送[/yellow]\n")

            # Display next steps
            console.print("[bold]下一步:[/bold]")
            console.print("  前端开发者现在可以拉取契约进行开发")
            console.print(f"  启动 Mock Server: [cyan]aceflow mock start --feature {feature}[/cyan]\n")
        else:
            console.print(f"[bold red]❌ 推送失败: {result_message}[/bold red]\n")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]❌ 推送失败: {e}[/red]\n")
        import traceback
        if console.is_terminal:
            console.print("[dim]详细错误信息:[/dim]")
            console.print(f"[dim]{traceback.format_exc()}[/dim]\n")
        raise click.Abort()


if __name__ == '__main__':
    contract_group()
