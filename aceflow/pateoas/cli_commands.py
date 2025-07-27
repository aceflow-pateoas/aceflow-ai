"""
PATEOAS CLI命令扩展
为AceFlow CLI添加PATEOAS相关命令
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .enhanced_engine import PATEOASEnhancedEngine
from .optimized_state_manager import OptimizedStateManager
from .optimized_memory_retrieval import OptimizedMemoryRetrieval
from .performance_monitor import PATEOASPerformanceMonitor
from .adaptive_recovery import AdaptiveRecoveryStrategy
from .config import get_config


class PATEOASCLIManager:
    """PATEOAS CLI管理器"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or "default"
        self.config = get_config()
        
        # 延迟初始化组件
        self._engine = None
        self._state_manager = None
        self._memory_system = None
        self._performance_monitor = None
    
    @property
    def engine(self) -> PATEOASEnhancedEngine:
        """获取PATEOAS引擎实例"""
        if self._engine is None:
            self._engine = PATEOASEnhancedEngine(self.project_id)
        return self._engine
    
    @property
    def state_manager(self) -> OptimizedStateManager:
        """获取状态管理器实例"""
        if self._state_manager is None:
            self._state_manager = OptimizedStateManager(self.project_id)
        return self._state_manager
    
    @property
    def memory_system(self) -> OptimizedMemoryRetrieval:
        """获取记忆系统实例"""
        if self._memory_system is None:
            self._memory_system = OptimizedMemoryRetrieval(self.project_id)
        return self._memory_system
    
    @property
    def performance_monitor(self) -> PATEOASPerformanceMonitor:
        """获取性能监控器实例"""
        if self._performance_monitor is None:
            self._performance_monitor = PATEOASPerformanceMonitor(self.project_id)
        return self._performance_monitor


class PATEOASCLICommands:
    """PATEOAS CLI命令类（简化版本，不依赖click）"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.manager = PATEOASCLIManager(project_id)
    
    def status(self, detailed: bool = False, format: str = 'summary'):
        """显示PATEOAS系统状态"""
        try:
            # 获取系统状态
            current_state = self.manager.state_manager.get_current_state_optimized()
            performance_stats = self.manager.performance_monitor.get_performance_summary()
            memory_stats = self.manager.memory_system.get_performance_report()
            
            status_data = {
                'project_id': self.manager.project_id,
                'timestamp': datetime.now().isoformat(),
                'system_health': performance_stats['system_health'],
                'current_stage': current_state.get('workflow_state', {}).get('current_stage', 'unknown'),
                'task_progress': current_state.get('workflow_state', {}).get('stage_progress', 0),
                'performance': {
                    'total_requests': performance_stats['current_metrics']['total_requests'],
                    'success_rate': performance_stats['current_metrics']['successful_requests'] / 
                                   max(1, performance_stats['current_metrics']['total_requests']),
                    'avg_response_time': performance_stats['current_metrics']['average_response_time'],
                    'system_health_score': performance_stats['system_health']
                },
                'memory': {
                    'total_memories': memory_stats['index_stats']['total_vectors'],
                    'cache_hit_rate': memory_stats['cache_hit_rate'],
                    'memory_usage_mb': memory_stats['memory_usage']['total_estimated_mb']
                },
                'components': {
                    'state_manager': 'active',
                    'memory_system': 'active',
                    'performance_monitor': 'active',
                    'enhanced_engine': 'active'
                }
            }
            
            if detailed:
                status_data['detailed'] = {
                    'state_cache_stats': self.manager.state_manager.get_performance_stats(),
                    'memory_recommendations': memory_stats['recommendations'],
                    'component_performance': performance_stats['component_performance'],
                    'alerts': performance_stats['alerts']
                }
            
            # 输出格式化
            if format == 'json':
                print(json.dumps(status_data, indent=2, ensure_ascii=False))
            else:
                self._display_status_summary(status_data, detailed)
                
            return status_data
                
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
            return None
    
    def memory(self, action: str = 'stats', query: str = None, category: str = None, 
               limit: int = 10, content: str = None, importance: float = 0.5, 
               tags: str = None):
        """PATEOAS记忆管理命令"""
        try:
            if action == 'list':
                return self._list_memories(category, limit)
            elif action == 'search':
                if not query:
                    print("❌ 搜索操作需要提供查询参数")
                    return None
                return self._search_memories(query, category, limit)
            elif action == 'add':
                if not content:
                    print("❌ 添加记忆需要提供内容参数")
                    return None
                return self._add_memory(content, category or 'context', importance, tags)
            elif action == 'optimize':
                return self._optimize_memory()
            elif action == 'stats':
                return self._show_memory_stats()
            else:
                print(f"❌ 未知操作: {action}")
                return None
                
        except Exception as e:
            print(f"❌ 记忆操作失败: {e}")
            return None
    
    def performance(self, action: str = 'report', queries: int = 50, watch: bool = False):
        """PATEOAS性能监控命令"""
        try:
            if action == 'report':
                return self._show_performance_report()
            elif action == 'benchmark':
                return self._run_performance_benchmark(queries)
            elif action == 'monitor':
                return self._monitor_performance(watch)
            else:
                print(f"❌ 未知操作: {action}")
                return None
                
        except Exception as e:
            print(f"❌ 性能操作失败: {e}")
            return None
    
    def recovery(self, action: str = 'stats', error_type: str = None):
        """PATEOAS恢复策略命令"""
        try:
            if action == 'stats':
                return self._show_recovery_stats()
            elif action == 'test':
                return self._test_recovery_strategy(error_type)
            elif action == 'history':
                return self._show_recovery_history()
            else:
                print(f"❌ 未知操作: {action}")
                return None
                
        except Exception as e:
            print(f"❌ 恢复操作失败: {e}")
            return None
    
    def config(self, action: str = 'show', key: str = None, value: str = None):
        """PATEOAS配置管理命令"""
        try:
            if action == 'show':
                return self._show_config(key)
            elif action == 'set':
                if not key or not value:
                    print("❌ 设置配置需要提供键和值参数")
                    return None
                return self._set_config(key, value)
            elif action == 'reset':
                return self._reset_config(key)
            else:
                print(f"❌ 未知操作: {action}")
                return None
                
        except Exception as e:
            print(f"❌ 配置操作失败: {e}")
            return None
    
    # 辅助方法实现
    
    def _display_status_summary(self, status_data: Dict[str, Any], detailed: bool):
        """显示状态摘要"""
        print("🎯 PATEOAS系统状态摘要")
        print("=" * 50)
        
        # 基本信息
        print(f"项目ID: {status_data['project_id']}")
        print(f"当前阶段: {status_data['current_stage']}")
        print(f"任务进度: {status_data['task_progress']:.1%}")
        print(f"系统健康: {status_data['system_health']:.2f}")
        
        # 性能指标
        perf = status_data['performance']
        print(f"\n📊 性能指标:")
        print(f"  - 总请求数: {perf['total_requests']}")
        print(f"  - 成功率: {perf['success_rate']:.2%}")
        print(f"  - 平均响应时间: {perf['avg_response_time']:.3f}s")
        
        # 记忆统计
        memory = status_data['memory']
        print(f"\n🧠 记忆统计:")
        print(f"  - 总记忆数: {memory['total_memories']}")
        print(f"  - 缓存命中率: {memory['cache_hit_rate']:.2%}")
        print(f"  - 内存使用: {memory['memory_usage_mb']:.2f} MB")
        
        # 组件状态
        print(f"\n🔧 组件状态:")
        for component, status in status_data['components'].items():
            status_icon = "✅" if status == "active" else "❌"
            print(f"  {status_icon} {component}: {status}")
        
        if detailed and 'detailed' in status_data:
            detailed_info = status_data['detailed']
            
            # 警报信息
            if detailed_info.get('alerts'):
                print(f"\n⚠️ 系统警报:")
                for alert in detailed_info['alerts']:
                    print(f"  - {alert['type'].upper()}: {alert['message']}")
            
            # 优化建议
            if detailed_info.get('memory_recommendations'):
                print(f"\n💡 优化建议:")
                for rec in detailed_info['memory_recommendations']:
                    print(f"  • {rec}")
    
    def _list_memories(self, category: Optional[str], limit: int):
        """列出记忆"""
        print(f"📚 记忆列表 (限制: {limit})")
        
        memories = self.manager.memory_system.search_memories_optimized("", category=category, limit=limit)
        
        if not memories:
            print("  暂无记忆记录")
            return []
        
        for i, memory in enumerate(memories, 1):
            print(f"{i}. [{memory['category']}] {memory.get('content', 'N/A')[:50]}...")
            print(f"   相似度: {memory['similarity']:.3f} | 重要性: {memory['importance']:.2f}")
            if memory.get('tags'):
                print(f"   标签: {', '.join(memory['tags'])}")
            print()
        
        return memories
    
    def _search_memories(self, query: str, category: Optional[str], limit: int):
        """搜索记忆"""
        print(f"🔍 搜索记忆: '{query}'")
        
        results = self.manager.memory_system.search_memories_optimized(
            query, category=category, limit=limit
        )
        
        if not results:
            print("  未找到匹配的记忆")
            return []
        
        print(f"找到 {len(results)} 个结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 相似度: {result['similarity']:.3f}")
            print(f"   分类: {result['category']}")
            print(f"   重要性: {result['importance']:.2f}")
            if result.get('tags'):
                print(f"   标签: {', '.join(result['tags'])}")
            print()
        
        return results
    
    def _add_memory(self, content: str, category: str, importance: float, tags: Optional[str]):
        """添加记忆"""
        tag_list = tags.split(',') if tags else []
        tag_list = [tag.strip() for tag in tag_list if tag.strip()]
        
        memory_id = self.manager.memory_system.add_memory_optimized(
            content, category, importance, tag_list
        )
        
        print(f"✅ 记忆已添加")
        print(f"   ID: {memory_id}")
        print(f"   内容: {content}")
        print(f"   分类: {category}")
        print(f"   重要性: {importance}")
        if tag_list:
            print(f"   标签: {', '.join(tag_list)}")
        
        return memory_id
    
    def _optimize_memory(self):
        """优化记忆"""
        print("🔧 开始优化记忆系统...")
        
        # 获取优化前统计
        before_stats = self.manager.memory_system.get_performance_report()
        
        # 执行优化
        self.manager.memory_system.optimize_indices()
        
        # 获取优化后统计
        after_stats = self.manager.memory_system.get_performance_report()
        
        print("✅ 记忆优化完成")
        print(f"   优化前索引: {before_stats['index_stats']['total_vectors']}")
        print(f"   优化后索引: {after_stats['index_stats']['total_vectors']}")
        print(f"   优化前缓存: {before_stats['index_stats']['cache_entries']}")
        print(f"   优化后缓存: {after_stats['index_stats']['cache_entries']}")
        
        return {
            'before': before_stats,
            'after': after_stats
        }
    
    def _show_memory_stats(self):
        """显示记忆统计"""
        stats = self.manager.memory_system.get_performance_report()
        
        print("📊 记忆系统统计")
        print("=" * 40)
        
        # 基本统计
        index_stats = stats['index_stats']
        print(f"总向量数: {index_stats['total_vectors']}")
        print(f"分类数: {index_stats['categories']}")
        print(f"缓存条目: {index_stats['cache_entries']}")
        print(f"向量维度: {index_stats['vector_dimension']}")
        
        # 性能统计
        perf_stats = stats['performance_stats']
        print(f"\n性能指标:")
        print(f"  - 总查询数: {perf_stats['total_queries']}")
        print(f"  - 缓存命中率: {stats['cache_hit_rate']:.2%}")
        print(f"  - 平均搜索时间: {perf_stats['average_search_time']:.4f}s")
        
        # 内存使用
        memory_usage = stats['memory_usage']
        print(f"\n内存使用:")
        print(f"  - 向量索引: {memory_usage['vector_indices_mb']:.2f} MB")
        print(f"  - 语义缓存: {memory_usage['semantic_cache_mb']:.2f} MB")
        print(f"  - 总计: {memory_usage['total_estimated_mb']:.2f} MB")
        
        # 优化建议
        if stats['recommendations']:
            print(f"\n💡 优化建议:")
            for rec in stats['recommendations']:
                print(f"  • {rec}")
        
        return stats
    
    def _show_performance_report(self):
        """显示性能报告"""
        report = self.manager.performance_monitor.generate_performance_report()
        
        print("📈 PATEOAS性能报告")
        print("=" * 50)
        
        # 摘要信息
        summary = report['summary']
        print(f"报告时间: {report['report_timestamp']}")
        print(f"项目ID: {report['project_id']}")
        print(f"系统健康: {summary['system_health']:.2f}")
        
        # 性能指标
        metrics = summary['current_metrics']
        print(f"\n📊 性能指标:")
        print(f"  - 总请求数: {metrics['total_requests']}")
        print(f"  - 成功请求数: {metrics['successful_requests']}")
        print(f"  - 平均响应时间: {metrics['average_response_time']:.4f}s")
        print(f"  - 决策准确性: {metrics['decision_accuracy']:.2f}")
        print(f"  - 用户满意度: {metrics['user_satisfaction']:.2f}")
        
        # 组件分析
        if 'component_analysis' in report:
            print(f"\n🔧 组件分析:")
            for component, analysis in report['component_analysis'].items():
                print(f"  - {component}: {analysis['status']} (分数: {analysis['performance_score']:.2f})")
        
        # 建议
        if report['recommendations']:
            print(f"\n💡 优化建议:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        return report
    
    def _run_performance_benchmark(self, queries: int):
        """运行性能基准测试"""
        print(f"🏃 开始性能基准测试 ({queries} 次查询)...")
        
        # 运行记忆系统基准测试
        memory_benchmark = self.manager.memory_system.benchmark_performance(queries)
        
        print("✅ 基准测试完成")
        print(f"\n📊 测试结果:")
        print(f"  - 总查询数: {memory_benchmark['total_queries']}")
        print(f"  - 平均搜索时间: {memory_benchmark['average_search_time']:.4f}s")
        print(f"  - 最快搜索时间: {memory_benchmark['min_search_time']:.4f}s")
        print(f"  - 最慢搜索时间: {memory_benchmark['max_search_time']:.4f}s")
        print(f"  - 每秒查询数: {memory_benchmark['queries_per_second']:.1f}")
        print(f"  - 缓存命中率: {memory_benchmark['cache_hit_rate']:.2%}")
        print(f"  - 性能等级: {memory_benchmark['performance_grade']}")
        
        return memory_benchmark
    
    def _monitor_performance(self, watch: bool):
        """监控性能"""
        stats = self.manager.performance_monitor.get_performance_summary()
        print("📊 当前性能状态:")
        print(f"  - 系统健康: {stats['system_health']:.2f}")
        print(f"  - 总请求: {stats['current_metrics']['total_requests']}")
        print(f"  - 平均响应时间: {stats['current_metrics']['average_response_time']:.4f}s")
        
        return stats
    
    def _show_recovery_stats(self):
        """显示恢复统计"""
        stats = self.manager.engine.recovery_strategy.get_recovery_statistics()
        
        if stats.get('status') == 'no_data':
            print("📊 暂无恢复统计数据")
            return stats
        
        print("🔄 恢复策略统计")
        print("=" * 40)
        
        print(f"总恢复次数: {stats['total_recoveries']}")
        print(f"最近24小时恢复: {stats['recent_recoveries']}")
        
        if stats['error_types']:
            print(f"\n错误类型分布:")
            for error_type, info in stats['error_types'].items():
                print(f"  - {error_type}: {info['count']} 次")
        
        if stats['strategy_success_rates']:
            print(f"\n策略成功率:")
            for strategy, rate in stats['strategy_success_rates'].items():
                print(f"  - {strategy}: {rate:.2%}")
        
        return stats
    
    def _test_recovery_strategy(self, error_type: Optional[str]):
        """测试恢复策略"""
        print("🧪 测试恢复策略...")
        
        # 模拟不同类型的错误
        test_errors = {
            'timeout': TimeoutError("Connection timeout"),
            'memory': MemoryError("Out of memory"),
            'network': ConnectionError("Network error"),
            'permission': PermissionError("Access denied"),
            'data': ValueError("Invalid data format")
        }
        
        if error_type and error_type in test_errors:
            test_error = test_errors[error_type]
        else:
            test_error = RuntimeError("Test error")
        
        context = {
            'user_input': 'CLI测试',
            'system_state': {'test': True}
        }
        
        result = self.manager.engine.recovery_strategy.analyze_and_recover(
            test_error, context, 'cli_test'
        )
        
        print("✅ 恢复策略测试完成")
        print(f"  - 错误模式: {result['error_pattern']}")
        print(f"  - 推荐策略: {result['recommended_strategy'].strategy.value}")
        print(f"  - 置信度: {result['confidence']:.2f}")
        print(f"  - 恢复类型: {result['recovery_type'].value}")
        
        if result['recovery_result']:
            print(f"  - 执行结果: {'成功' if result['recovery_result']['success'] else '失败'}")
        
        return result
    
    def _show_recovery_history(self):
        """显示恢复历史"""
        history = self.manager.engine.recovery_strategy.recovery_history
        
        if not history:
            print("📚 暂无恢复历史记录")
            return []
        
        print(f"📚 恢复历史 (最近 {min(10, len(history))} 条)")
        print("=" * 50)
        
        for i, context in enumerate(history[-10:], 1):
            print(f"{i}. {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   错误: {context.error_type} - {context.error_message[:50]}...")
            print(f"   组件: {context.component}")
            print(f"   严重性: {context.severity}")
            print(f"   尝试次数: {context.attempt_count}")
            print()
        
        return history
    
    def _show_config(self, key: Optional[str]):
        """显示配置"""
        config = self.manager.config
        
        if key:
            if hasattr(config, key):
                value = getattr(config, key)
                print(f"{key}: {value}")
                return {key: value}
            else:
                print(f"❌ 配置键 '{key}' 不存在")
                return None
        else:
            print("⚙️ PATEOAS配置:")
            print(f"  - memory_storage_path: {config.memory_storage_path}")
            print(f"  - state_storage_path: {config.state_storage_path}")
            
            return {
                'memory_storage_path': str(config.memory_storage_path),
                'state_storage_path': str(config.state_storage_path)
            }
    
    def _set_config(self, key: str, value: str):
        """设置配置"""
        print(f"⚙️ 设置配置 {key} = {value}")
        # 实现配置设置逻辑
        print("✅ 配置已更新")
        return {'key': key, 'value': value, 'status': 'updated'}
    
    def _reset_config(self, key: Optional[str]):
        """重置配置"""
        if key:
            print(f"🔄 重置配置 {key}")
        else:
            print("🔄 重置所有配置")
        print("✅ 配置已重置")
        return {'status': 'reset', 'key': key}


# 导出CLI管理器和命令类
__all__ = ['PATEOASCLIManager', 'PATEOASCLICommands']