"""
PATEOAS CLI 扩展
为 AceFlow CLI 添加 PATEOAS 功能
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .config import get_config, set_config, PATEOASConfig
from .utils import generate_id


class PATEOASCLI:
    """PATEOAS CLI 处理器"""
    
    def __init__(self):
        self.config = get_config()
    
    def handle_pateoas_status(self, args):
        """处理 pateoas-status 命令"""
        try:
            # 尝试导入增强引擎
            from .enhanced_engine import PATEOASEnhancedEngine
            
            project_id = args.project_id or "default"
            engine = PATEOASEnhancedEngine(project_id=project_id)
            status = engine.get_pateoas_status()
            
            if args.format == 'json':
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                self._print_status_text(status)
                
        except Exception as e:
            print(f"❌ 获取 PATEOAS 状态失败: {e}")
            return False
        
        return True
    
    def handle_pateoas_memory(self, args):
        """处理 pateoas-memory 命令"""
        try:
            from .memory_system import ContextMemorySystem
            
            project_id = args.project_id or "default"
            memory_system = ContextMemorySystem(project_id)
            
            if args.action == 'stats':
                stats = memory_system.get_memory_stats()
                print(f"📊 记忆统计 (项目: {project_id})")
                print(f"总记忆数量: {stats['total_memories']}")
                for category, info in stats['categories'].items():
                    print(f"  {category}: {info['count']} 条 (平均重要性: {info['avg_importance']:.2f})")
            
            elif args.action == 'search':
                if not args.query:
                    print("❌ 搜索需要提供查询词")
                    return False
                
                results = memory_system.search_memories(args.query, limit=args.limit or 10)
                print(f"🔍 搜索结果 (查询: '{args.query}')")
                for i, result in enumerate(results, 1):
                    print(f"{i}. [{result['category']}] {result['content'][:100]}...")
                    print(f"   相似度: {result['similarity']:.2f}, 重要性: {result['importance']:.2f}")
            
            elif args.action == 'add':
                if not args.content:
                    print("❌ 添加记忆需要提供内容")
                    return False
                
                memory_system.add_memory(
                    content=args.content,
                    category=args.category or 'context',
                    importance=args.importance or 0.5,
                    tags=args.tags.split(',') if args.tags else []
                )
                print(f"✅ 记忆已添加: {args.content[:50]}...")
            
            elif args.action == 'cleanup':
                cleaned = memory_system.cleanup_old_memories(args.days or 90)
                print(f"🧹 清理完成，删除了 {cleaned} 条旧记忆")
            
            else:
                print(f"❌ 未知的记忆操作: {args.action}")
                return False
                
        except Exception as e:
            print(f"❌ 记忆操作失败: {e}")
            return False
        
        return True
    
    def handle_pateoas_config(self, args):
        """处理 pateoas-config 命令"""
        try:
            if args.action == 'show':
                config_dict = self.config.to_dict()
                if args.format == 'json':
                    print(json.dumps(config_dict, indent=2, ensure_ascii=False))
                else:
                    self._print_config_text(config_dict)
            
            elif args.action == 'set':
                if not args.key or args.value is None:
                    print("❌ 设置配置需要提供 key 和 value")
                    return False
                
                # 简单的配置设置（实际实现会更复杂）
                if args.key == 'memory_enabled':
                    self.config.memory_enabled = args.value.lower() == 'true'
                elif args.key == 'adaptive_flow_enabled':
                    self.config.adaptive_flow_enabled = args.value.lower() == 'true'
                elif args.key == 'debug_mode':
                    self.config.debug_mode = args.value.lower() == 'true'
                else:
                    print(f"❌ 未知的配置项: {args.key}")
                    return False
                
                self.config.save_to_file()
                print(f"✅ 配置已更新: {args.key} = {args.value}")
            
            elif args.action == 'reset':
                default_config = PATEOASConfig()
                set_config(default_config)
                default_config.save_to_file()
                print("✅ 配置已重置为默认值")
            
            else:
                print(f"❌ 未知的配置操作: {args.action}")
                return False
                
        except Exception as e:
            print(f"❌ 配置操作失败: {e}")
            return False
        
        return True
    
    def handle_pateoas_analyze(self, args):
        """处理 pateoas-analyze 命令"""
        try:
            from .enhanced_engine import PATEOASEnhancedEngine
            
            if not args.task:
                print("❌ 分析需要提供任务描述")
                return False
            
            project_id = args.project_id or "default"
            engine = PATEOASEnhancedEngine(project_id=project_id)
            
            project_context = {
                'team_size': args.team_size or 5,
                'urgency': args.urgency or 'normal',
                'project_type': args.project_type or 'unknown'
            }
            
            result = engine.analyze_and_recommend(args.task, project_context)
            
            print(f"🧠 任务分析结果")
            print(f"任务: {args.task}")
            print(f"推荐模式: {result['mode_recommendation']['recommended_mode']}")
            print(f"置信度: {result['mode_recommendation']['confidence']:.2f}")
            print(f"推理: {result['mode_recommendation']['reasoning']}")
            
            if result['optimization_suggestions'].get('parallel_execution'):
                print(f"\n⚡ 并行执行机会:")
                for opp in result['optimization_suggestions']['parallel_execution']:
                    print(f"  - {opp['type']}: 可节省 {opp['time_saving']} 时间")
            
        except Exception as e:
            print(f"❌ 任务分析失败: {e}")
            return False
        
        return True
    
    def _print_status_text(self, status):
        """打印文本格式的状态"""
        print("📊 PATEOAS 系统状态")
        print("=" * 40)
        
        sys_info = status['system_info']
        print(f"项目ID: {sys_info['project_id']}")
        print(f"引擎版本: {sys_info['engine_version']}")
        print(f"运行时间: {sys_info['uptime']}")
        print(f"状态: {sys_info['status']}")
        
        state_info = status['state_info']
        print(f"\n当前任务: {state_info['current_task']}")
        print(f"整体进度: {state_info['overall_progress']}%")
        print(f"状态转换次数: {state_info['state_transitions']}")
        
        memory_info = status['memory_info']
        print(f"\n记忆统计:")
        print(f"总记忆数量: {memory_info['total_memories']}")
        for category, info in memory_info['categories'].items():
            print(f"  {category}: {info['count']} 条")
        
        perf_info = status['performance_metrics']
        print(f"\n性能指标:")
        print(f"总交互次数: {perf_info['total_interactions']}")
        print(f"成功决策数: {perf_info['successful_decisions']}")
        print(f"成功率: {perf_info['success_rate']:.2%}")
    
    def _print_config_text(self, config_dict):
        """打印文本格式的配置"""
        print("⚙️  PATEOAS 配置")
        print("=" * 40)
        
        for section, settings in config_dict.items():
            print(f"\n[{section}]")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {settings}")


def add_pateoas_commands(parser):
    """为 AceFlow CLI 添加 PATEOAS 命令"""
    pateoas_parser = parser.add_parser('pateoas', help='PATEOAS 相关命令')
    pateoas_subparsers = pateoas_parser.add_subparsers(dest='pateoas_command', help='PATEOAS 子命令')
    
    # pateoas status 命令
    status_parser = pateoas_subparsers.add_parser('status', help='查看 PATEOAS 状态')
    status_parser.add_argument('--project-id', help='项目ID')
    status_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    # pateoas memory 命令
    memory_parser = pateoas_subparsers.add_parser('memory', help='记忆管理')
    memory_parser.add_argument('action', choices=['stats', 'search', 'add', 'cleanup'], help='操作类型')
    memory_parser.add_argument('--project-id', help='项目ID')
    memory_parser.add_argument('--query', help='搜索查询词')
    memory_parser.add_argument('--content', help='记忆内容')
    memory_parser.add_argument('--category', help='记忆分类')
    memory_parser.add_argument('--importance', type=float, help='重要性 (0.0-1.0)')
    memory_parser.add_argument('--tags', help='标签 (逗号分隔)')
    memory_parser.add_argument('--limit', type=int, help='搜索结果限制')
    memory_parser.add_argument('--days', type=int, help='清理天数')
    
    # pateoas config 命令
    config_parser = pateoas_subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('action', choices=['show', 'set', 'reset'], help='操作类型')
    config_parser.add_argument('--key', help='配置键')
    config_parser.add_argument('--value', help='配置值')
    config_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    # pateoas analyze 命令
    analyze_parser = pateoas_subparsers.add_parser('analyze', help='任务分析')
    analyze_parser.add_argument('task', help='任务描述')
    analyze_parser.add_argument('--project-id', help='项目ID')
    analyze_parser.add_argument('--team-size', type=int, help='团队规模')
    analyze_parser.add_argument('--urgency', choices=['low', 'normal', 'high', 'emergency'], help='紧急程度')
    analyze_parser.add_argument('--project-type', help='项目类型')


def handle_pateoas_command(args):
    """处理 PATEOAS 命令"""
    cli = PATEOASCLI()
    
    if args.pateoas_command == 'status':
        return cli.handle_pateoas_status(args)
    elif args.pateoas_command == 'memory':
        return cli.handle_pateoas_memory(args)
    elif args.pateoas_command == 'config':
        return cli.handle_pateoas_config(args)
    elif args.pateoas_command == 'analyze':
        return cli.handle_pateoas_analyze(args)
    else:
        print("❌ 未知的 PATEOAS 命令")
        return False


if __name__ == "__main__":
    # 独立运行时的测试
    parser = argparse.ArgumentParser(description='PATEOAS CLI 测试')
    subparsers = parser.add_subparsers(dest='command')
    
    add_pateoas_commands(subparsers)
    
    args = parser.parse_args()
    
    if args.command == 'pateoas':
        success = handle_pateoas_command(args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()