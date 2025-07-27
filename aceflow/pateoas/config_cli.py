"""
PATEOAS配置管理CLI命令
提供配置管理的命令行接口
"""

import click
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .config_manager import (
    get_pateoas_config_manager, 
    FeatureFlag, 
    DeploymentStage,
    FeatureConfig
)


@click.group(name='config')
@click.pass_context
def config_cli(ctx):
    """PATEOAS配置管理命令"""
    if ctx.obj is None:
        ctx.obj = {}
    
    # 初始化配置管理器
    ctx.obj['config_manager'] = get_pateoas_config_manager()
    
    click.echo("🔧 PATEOAS配置管理")


@config_cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'yaml']), default='table', help='输出格式')
@click.option('--user-id', '-u', help='指定用户ID检查功能启用状态')
@click.pass_context
def show(ctx, format, user_id):
    """显示当前配置"""
    config_manager = ctx.obj['config_manager']
    
    if format == 'json':
        config_data = config_manager.export_config(include_user_config=True)
        click.echo(json.dumps(config_data, ensure_ascii=False, indent=2))
        return
    
    # 显示主配置
    main_config = config_manager.get_main_config()
    click.echo("\n📋 主配置:")
    click.echo(f"  - PATEOAS版本: {main_config.pateoas_version}")
    click.echo(f"  - 配置版本: {main_config.config_version}")
    click.echo(f"  - 部署阶段: {main_config.deployment_stage.value}")
    click.echo(f"  - 调试模式: {'启用' if main_config.debug_mode else '禁用'}")
    click.echo(f"  - 日志级别: {main_config.log_level}")
    
    click.echo(f"\n🔧 核心功能:")
    click.echo(f"  - 状态连续性: {'启用' if main_config.enable_state_continuity else '禁用'}")
    click.echo(f"  - 记忆系统: {'启用' if main_config.enable_memory_system else '禁用'}")
    click.echo(f"  - 自适应流程: {'启用' if main_config.enable_adaptive_flow else '禁用'}")
    click.echo(f"  - 决策门: {'启用' if main_config.enable_decision_gates else '禁用'}")
    click.echo(f"  - 性能监控: {'启用' if main_config.enable_performance_monitoring else '禁用'}")
    click.echo(f"  - 异常处理: {'启用' if main_config.enable_exception_handling else '禁用'}")
    
    click.echo(f"\n⚡ 性能配置:")
    click.echo(f"  - 状态缓存大小: {main_config.state_cache_size}")
    click.echo(f"  - 记忆缓存大小: {main_config.memory_cache_size}")
    click.echo(f"  - 向量维度: {main_config.vector_dimension}")
    click.echo(f"  - 最大记忆片段: {main_config.max_memory_fragments}")
    
    # 显示功能配置
    click.echo(f"\n🚀 功能开关状态:")
    rollout_status = config_manager.get_feature_rollout_status()
    
    for feature_name, status in rollout_status.items():
        enabled_icon = "✅" if status['enabled'] else "❌"
        available_icon = "🟢" if status['available_in_current_stage'] else "🔴"
        user_enabled_icon = "👤✅" if status['enabled_for_current_user'] else "👤❌"
        
        click.echo(f"  {enabled_icon} {feature_name}")
        click.echo(f"    状态: {status['flag']}")
        click.echo(f"    部署百分比: {status['rollout_percentage']:.1f}%")
        click.echo(f"    当前阶段可用: {available_icon}")
        if user_id:
            user_enabled = config_manager.is_feature_enabled(feature_name, user_id)
            click.echo(f"    用户启用: {'👤✅' if user_enabled else '👤❌'}")


@config_cli.command()
@click.argument('feature_name')
@click.option('--enabled/--disabled', default=None, help='启用或禁用功能')
@click.option('--flag', type=click.Choice(['enabled', 'disabled', 'experimental', 'deprecated']), help='设置功能标志')
@click.option('--rollout', type=float, help='设置部署百分比 (0-100)')
@click.option('--stages', help='设置部署阶段 (逗号分隔)')
@click.option('--description', help='设置功能描述')
@click.pass_context
def feature(ctx, feature_name, enabled, flag, rollout, stages, description):
    """管理功能开关"""
    config_manager = ctx.obj['config_manager']
    
    # 获取现有配置
    feature_config = config_manager.get_feature_config(feature_name)
    
    if not feature_config:
        click.echo(f"❌ 功能 '{feature_name}' 不存在")
        return
    
    # 更新配置
    updates = {}
    
    if enabled is not None:
        updates['enabled'] = enabled
    
    if flag:
        updates['flag'] = FeatureFlag(flag)
    
    if rollout is not None:
        if not (0 <= rollout <= 100):
            click.echo("❌ 部署百分比必须在0-100之间")
            return
        updates['rollout_percentage'] = rollout
    
    if stages:
        try:
            stage_list = [DeploymentStage(stage.strip()) for stage in stages.split(',')]
            updates['deployment_stages'] = stage_list
        except ValueError as e:
            click.echo(f"❌ 无效的部署阶段: {e}")
            return
    
    if description:
        updates['description'] = description
    
    if updates:
        success = config_manager.update_feature_config(feature_name, **updates)
        if success:
            click.echo(f"✅ 功能 '{feature_name}' 配置已更新")
            
            # 显示更新后的配置
            updated_config = config_manager.get_feature_config(feature_name)
            click.echo(f"  - 启用状态: {'启用' if updated_config.enabled else '禁用'}")
            click.echo(f"  - 功能标志: {updated_config.flag.value}")
            click.echo(f"  - 部署百分比: {updated_config.rollout_percentage:.1f}%")
            click.echo(f"  - 部署阶段: {', '.join([stage.value for stage in updated_config.deployment_stages])}")
            if updated_config.description:
                click.echo(f"  - 描述: {updated_config.description}")
        else:
            click.echo(f"❌ 更新功能 '{feature_name}' 配置失败")
    else:
        # 显示当前配置
        click.echo(f"📋 功能 '{feature_name}' 当前配置:")
        click.echo(f"  - 启用状态: {'启用' if feature_config.enabled else '禁用'}")
        click.echo(f"  - 功能标志: {feature_config.flag.value}")
        click.echo(f"  - 部署百分比: {feature_config.rollout_percentage:.1f}%")
        click.echo(f"  - 部署阶段: {', '.join([stage.value for stage in feature_config.deployment_stages])}")
        if feature_config.description:
            click.echo(f"  - 描述: {feature_config.description}")
        click.echo(f"  - 创建时间: {feature_config.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"  - 更新时间: {feature_config.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")


@config_cli.command()
@click.argument('stage', type=click.Choice(['development', 'testing', 'staging', 'production']))
@click.pass_context
def stage(ctx, stage):
    """设置部署阶段"""
    config_manager = ctx.obj['config_manager']
    
    deployment_stage = DeploymentStage(stage)
    config_manager.set_deployment_stage(deployment_stage)
    
    click.echo(f"✅ 部署阶段已设置为: {stage}")
    
    # 显示在新阶段下可用的功能
    enabled_features = config_manager.get_enabled_features()
    click.echo(f"\n🚀 在 {stage} 阶段启用的功能:")
    for feature_name in enabled_features:
        click.echo(f"  ✅ {feature_name}")


@config_cli.command()
@click.argument('key')
@click.argument('value', required=False)
@click.option('--type', 't', type=click.Choice(['str', 'int', 'float', 'bool']), default='str', help='值类型')
@click.pass_context
def set(ctx, key, value, type):
    """设置主配置项"""
    config_manager = ctx.obj['config_manager']
    
    if value is None:
        # 显示当前值
        main_config = config_manager.get_main_config()
        if hasattr(main_config, key):
            current_value = getattr(main_config, key)
            click.echo(f"📋 {key}: {current_value}")
        else:
            click.echo(f"❌ 配置项 '{key}' 不存在")
        return
    
    # 类型转换
    try:
        if type == 'int':
            converted_value = int(value)
        elif type == 'float':
            converted_value = float(value)
        elif type == 'bool':
            converted_value = value.lower() in ('true', '1', 'yes', 'on')
        else:
            converted_value = value
    except ValueError:
        click.echo(f"❌ 无法将 '{value}' 转换为 {type} 类型")
        return
    
    # 更新配置
    success = config_manager.update_main_config(**{key: converted_value})
    
    if success:
        click.echo(f"✅ 配置项 '{key}' 已设置为: {converted_value}")
    else:
        click.echo(f"❌ 配置项 '{key}' 不存在或设置失败")


@config_cli.command()
@click.pass_context
def validate(ctx):
    """验证配置"""
    config_manager = ctx.obj['config_manager']
    
    click.echo("🔍 验证PATEOAS配置...")
    
    validation_result = config_manager.validate_config()
    
    if validation_result['valid']:
        click.echo("✅ 配置验证通过")
    else:
        click.echo("❌ 配置验证失败")
    
    if validation_result['errors']:
        click.echo("\n🔴 错误:")
        for error in validation_result['errors']:
            click.echo(f"  - {error}")
    
    if validation_result['warnings']:
        click.echo("\n🟡 警告:")
        for warning in validation_result['warnings']:
            click.echo(f"  - {warning}")


@config_cli.command()
@click.argument('file_path')
@click.option('--include-user', is_flag=True, help='包含用户配置')
@click.pass_context
def export(ctx, file_path, include_user):
    """导出配置到文件"""
    config_manager = ctx.obj['config_manager']
    
    try:
        config_data = config_manager.export_config(include_user_config=include_user)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        click.echo(f"✅ 配置已导出到: {file_path}")
        click.echo(f"  - 主配置: 已包含")
        click.echo(f"  - 功能配置: 已包含 ({len(config_data['feature_configs'])} 个功能)")
        click.echo(f"  - 用户配置: {'已包含' if include_user else '未包含'}")
        
    except Exception as e:
        click.echo(f"❌ 导出配置失败: {e}")


@config_cli.command()
@click.argument('file_path')
@click.option('--merge/--replace', default=True, help='合并或替换现有配置')
@click.pass_context
def import_config(ctx, file_path, merge):
    """从文件导入配置"""
    config_manager = ctx.obj['config_manager']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        success = config_manager.import_config(config_data, merge=merge)
        
        if success:
            click.echo(f"✅ 配置已从 {file_path} 导入")
            click.echo(f"  - 导入模式: {'合并' if merge else '替换'}")
            
            if 'main_config' in config_data:
                click.echo("  - 主配置: 已导入")
            
            if 'feature_configs' in config_data:
                click.echo(f"  - 功能配置: 已导入 ({len(config_data['feature_configs'])} 个功能)")
            
            if 'user_config' in config_data:
                click.echo("  - 用户配置: 已导入")
        else:
            click.echo(f"❌ 导入配置失败")
            
    except FileNotFoundError:
        click.echo(f"❌ 文件不存在: {file_path}")
    except json.JSONDecodeError:
        click.echo(f"❌ 文件格式错误: {file_path}")
    except Exception as e:
        click.echo(f"❌ 导入配置失败: {e}")


@config_cli.command()
@click.confirmation_option(prompt='确定要重置所有配置为默认值吗？')
@click.pass_context
def reset(ctx):
    """重置配置为默认值"""
    config_manager = ctx.obj['config_manager']
    
    config_manager.reset_to_defaults()
    click.echo("✅ 配置已重置为默认值")


@config_cli.command()
@click.option('--user-id', '-u', help='指定用户ID')
@click.pass_context
def test(ctx, user_id):
    """测试功能启用状态"""
    config_manager = ctx.obj['config_manager']
    
    if user_id:
        config_manager.set_current_user(user_id)
        click.echo(f"👤 测试用户: {user_id}")
    
    click.echo(f"🏗️ 当前部署阶段: {config_manager.current_deployment_stage.value}")
    
    enabled_features = config_manager.get_enabled_features(user_id)
    
    click.echo(f"\n✅ 启用的功能 ({len(enabled_features)}):")
    for feature_name in enabled_features:
        feature_config = config_manager.get_feature_config(feature_name)
        click.echo(f"  - {feature_name} ({feature_config.flag.value}, {feature_config.rollout_percentage:.1f}%)")
    
    # 显示所有功能的详细状态
    click.echo(f"\n📊 所有功能状态:")
    rollout_status = config_manager.get_feature_rollout_status()
    
    for feature_name, status in rollout_status.items():
        enabled_for_user = config_manager.is_feature_enabled(feature_name, user_id)
        status_icon = "✅" if enabled_for_user else "❌"
        
        click.echo(f"  {status_icon} {feature_name}")
        click.echo(f"    - 全局启用: {'是' if status['enabled'] else '否'}")
        click.echo(f"    - 当前阶段可用: {'是' if status['available_in_current_stage'] else '否'}")
        click.echo(f"    - 部署百分比: {status['rollout_percentage']:.1f}%")
        click.echo(f"    - 用户启用: {'是' if enabled_for_user else '否'}")


# 注册配置命令到主CLI
def register_config_commands(main_cli):
    """将配置命令注册到主CLI"""
    main_cli.add_command(config_cli)