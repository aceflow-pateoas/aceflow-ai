#!/usr/bin/env python3
"""
AceFlow v3.0 增强版 CLI 工具
集成 PATEOAS 功能，提供智能化项目管理
"""

import json
import os
import sys
import argparse
import time
import yaml
from datetime import datetime
from pathlib import Path

# 添加 pateoas 模块路径
sys.path.insert(0, str(Path(__file__).parent))

class EnhancedAceFlowCLI:
    def __init__(self):
        self.project_root = Path.cwd()
        self.aceflow_dir = self.project_root / ".aceflow"
        self.state_file = self.aceflow_dir / "state" / "project_state.json"
        self.config_file = self.aceflow_dir / "config" / "project.yaml"
        
        # 初始化 PATEOAS 引擎
        self.pateoas_engine = None
        self._init_pateoas_engine()
    
    def _init_pateoas_engine(self):
        """初始化 PATEOAS 引擎"""
        try:
            from pateoas.enhanced_engine import PATEOASEnhancedEngine
            project_id = self._get_project_id()
            self.pateoas_engine = PATEOASEnhancedEngine(project_id=project_id)
            print("🧠 PATEOAS 智能引擎已激活")
        except Exception as e:
            print(f"⚠️  PATEOAS 引擎初始化失败: {e}")
            print("📝 将使用基础模式运行")
    
    def _get_project_id(self):
        """获取项目ID"""
        state = self.load_state()
        return state.get('project_id', f"aceflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    def load_state(self):
        """加载项目状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_state(self, state):
        """保存项目状态"""
        state['last_updated'] = datetime.now().isoformat()
        
        # 确保目录存在
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """加载项目配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def init_project(self, mode='smart', enable_pateoas=True):
        """初始化 AceFlow 项目"""
        print(f"🚀 初始化 AceFlow v3.0 项目 (PATEOAS增强版)...")
        
        # 创建目录结构
        dirs = [
            '.aceflow/config',
            '.aceflow/state',
            '.aceflow/scripts',
            '.aceflow/templates',
            '.aceflow/memory',
            '.aceflow/pateoas/state',
            '.aceflow/pateoas/memory',
            'aceflow_result'
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        # 生成项目ID
        project_id = f"aceflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 初始化状态
        state = {
            "project_id": project_id,
            "flow_mode": mode,
            "selected_mode": None,
            "current_stage": None,
            "overall_progress": 0,
            "created_at": datetime.now().isoformat(),
            "version": "3.0.0",
            "pateoas_enabled": enable_pateoas
        }
        
        self.save_state(state)
        
        # 初始化 PATEOAS 配置
        if enable_pateoas:
            self._init_pateoas_config()
        
        print(f"✅ AceFlow 项目初始化完成！")
        print(f"   项目ID: {project_id}")
        print(f"   流程模式: {mode}")
        print(f"   PATEOAS增强: {'启用' if enable_pateoas else '禁用'}")
        
        return state
    
    def _init_pateoas_config(self):
        """初始化 PATEOAS 配置"""
        try:
            from pateoas.config import PATEOASConfig
            config = PATEOASConfig()
            config.save_to_file()
            print("⚙️  PATEOAS 配置已初始化")
        except Exception as e:
            print(f"⚠️  PATEOAS 配置初始化失败: {e}")
    
    def status(self, format_type='text', verbose=False, pateoas=False):
        """查看项目状态"""
        if not self.aceflow_dir.exists():
            print("❌ 未检测到 AceFlow 项目，请先运行 'aceflow init'")
            return
        
        state = self.load_state()
        config = self.load_config()
        
        if format_type == 'json':
            if pateoas and self.pateoas_engine:
                # 获取 PATEOAS 增强状态
                pateoas_status = self.pateoas_engine.get_pateoas_status()
                combined_status = {
                    'aceflow_state': state,
                    'pateoas_status': pateoas_status
                }
                print(json.dumps(combined_status, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            self._print_status_text(state, config, verbose, pateoas)
    
    def _print_status_text(self, state, config, verbose, pateoas):
        """打印文本格式的状态"""
        print("\n📊 AceFlow 项目状态 (PATEOAS增强版)")
        print("=" * 50)
        print(f"项目ID: {state.get('project_id', 'N/A')}")
        print(f"流程模式: {state.get('flow_mode', 'N/A')}")
        print(f"当前阶段: {state.get('current_stage', '未开始')}")
        print(f"整体进度: {state.get('overall_progress', 0)}%")
        print(f"PATEOAS增强: {'✅ 启用' if state.get('pateoas_enabled', False) else '❌ 禁用'}")
        print(f"最后更新: {state.get('last_updated', 'N/A')}")
        
        if verbose:
            print(f"\n📋 详细信息:")
            print(f"版本: {state.get('version', 'N/A')}")
            print(f"创建时间: {state.get('created_at', 'N/A')}")
            print(f"配置文件: {self.config_file}")
            print(f"状态文件: {self.state_file}")
        
        # 显示 PATEOAS 状态
        if pateoas and self.pateoas_engine:
            try:
                pateoas_status = self.pateoas_engine.get_pateoas_status()
                print(f"\n🧠 PATEOAS 智能状态:")
                print(f"系统状态: {pateoas_status['system_info']['status']}")
                print(f"总交互次数: {pateoas_status['performance_metrics']['total_interactions']}")
                print(f"成功率: {pateoas_status['performance_metrics']['success_rate']:.1%}")
                print(f"记忆总数: {pateoas_status['memory_info']['total_memories']}")
                
                # 显示下一步建议
                current_state = self.pateoas_engine.state_continuity.get_current_state()
                if current_state.get('workflow_state', {}).get('current_stage'):
                    print(f"\n💡 智能建议:")
                    declaration = self.pateoas_engine.state_continuity.generate_state_declaration()
                    for suggestion in declaration.get('next_suggestions', [])[:3]:
                        print(f"  • {suggestion.get('description', 'N/A')}")
                        
            except Exception as e:
                print(f"⚠️  获取 PATEOAS 状态失败: {e}")
    
    def analyze(self, task_description, team_size=None, urgency=None, project_type=None):
        """AI 任务分析 (PATEOAS增强版)"""
        print(f"🧠 正在分析任务: {task_description}")
        
        # 如果有 PATEOAS 引擎，使用智能分析
        if self.pateoas_engine:
            try:
                project_context = {
                    'team_size': team_size or 5,
                    'urgency': urgency or 'normal',
                    'project_type': project_type or 'unknown'
                }
                
                result = self.pateoas_engine.analyze_and_recommend(task_description, project_context)
                
                print(f"📊 智能分析结果:")
                mode_rec = result['mode_recommendation']
                print(f"  任务类型: {mode_rec['factors']['task_complexity']}")
                print(f"  推荐模式: {mode_rec['recommended_mode']}")
                print(f"  置信度: {mode_rec['confidence']:.1%}")
                print(f"  推理: {mode_rec['reasoning']}")
                
                # 显示优化建议
                if result['optimization_suggestions'].get('parallel_execution'):
                    print(f"\n⚡ 并行执行机会:")
                    for opp in result['optimization_suggestions']['parallel_execution']:
                        print(f"  • {opp['type']}: 可节省 {opp['time_saving']} 时间")
                
                return result
                
            except Exception as e:
                print(f"⚠️  智能分析失败，使用基础分析: {e}")
        
        # 基础分析逻辑（原有逻辑）
        return self._basic_analyze(task_description)
    
    def _basic_analyze(self, task_description):
        """基础任务分析"""
        keywords = {
            'bug': ['修复', 'fix', 'bug', '问题', '错误'],
            'feature': ['新功能', '开发', '实现', '添加', '功能'],
            'refactor': ['重构', '优化', '改进', '重写'],
            'project': ['项目', '系统', '平台', '架构']
        }
        
        task_type = 'unknown'
        for category, kw_list in keywords.items():
            if any(kw in task_description.lower() for kw in kw_list):
                task_type = category
                break
        
        mode_mapping = {
            'bug': 'minimal',
            'feature': 'standard',
            'refactor': 'standard',
            'project': 'complete',
            'unknown': 'smart'
        }
        
        recommended_mode = mode_mapping.get(task_type, 'smart')
        
        result = {
            'task_description': task_description,
            'task_type': task_type,
            'recommended_mode': recommended_mode,
            'confidence': 0.85,
            'analysis_time': datetime.now().isoformat()
        }
        
        print(f"📊 基础分析结果:")
        print(f"  任务类型: {task_type}")
        print(f"  推荐模式: {recommended_mode}")
        print(f"  置信度: 85%")
        
        return result
    
    def start(self, description=None, mode=None, auto_analyze=True):
        """开始新的工作流 (PATEOAS增强版)"""
        state = self.load_state()
        
        if not description:
            description = input("请描述您要开始的任务: ")
        
        # 使用 PATEOAS 智能分析
        if auto_analyze and self.pateoas_engine:
            try:
                print("🧠 启动智能分析...")
                analysis = self.pateoas_engine.analyze_and_recommend(description)
                if not mode:
                    mode = analysis['mode_recommendation']['recommended_mode']
                    print(f"💡 智能推荐模式: {mode}")
            except Exception as e:
                print(f"⚠️  智能分析失败，使用基础分析: {e}")
                if not mode:
                    analysis = self._basic_analyze(description)
                    mode = analysis['recommended_mode']
        elif not mode:
            analysis = self._basic_analyze(description)
            mode = analysis['recommended_mode']
        
        # 生成迭代ID
        iteration_id = f"iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 更新状态
        state.update({
            'selected_mode': mode,
            'current_stage': self._get_first_stage(mode),
            'iteration_id': iteration_id,
            'task_description': description,
            'overall_progress': 0,
            'stage_progress': 0
        })
        
        self.save_state(state)
        
        # 更新 PATEOAS 状态
        if self.pateoas_engine:
            try:
                self.pateoas_engine.state_continuity.update_state({
                    'current_task': description,
                    'task_progress': 0.0,
                    'stage_context': {
                        'workflow_mode': mode,
                        'current_stage': state['current_stage'],
                        'iteration_id': iteration_id
                    },
                    'trigger': 'workflow_start',
                    'reasoning': f'开始新的工作流: {description}'
                })
                
                # 添加项目记忆
                self.pateoas_engine.context_memory.add_memory(
                    content=f"开始新项目: {description}，使用 {mode} 模式",
                    category="context",
                    importance=0.8,
                    tags=["项目开始", mode, "工作流"]
                )
                
            except Exception as e:
                print(f"⚠️  PATEOAS 状态更新失败: {e}")
        
        # 创建结果目录
        result_dir = Path(f"aceflow_result/{iteration_id}")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🚀 AceFlow 工作流已启动")
        print(f"  任务描述: {description}")
        print(f"  选择模式: {mode}")
        print(f"  迭代ID: {iteration_id}")
        print(f"  当前阶段: {state['current_stage']}")
        print(f"  结果目录: {result_dir}")
        
        # 显示下一步建议
        if self.pateoas_engine:
            try:
                declaration = self.pateoas_engine.state_continuity.generate_state_declaration()
                if declaration.get('next_suggestions'):
                    print(f"\n💡 智能建议:")
                    for suggestion in declaration['next_suggestions'][:2]:
                        print(f"  • {suggestion.get('description', 'N/A')}")
                        print(f"    命令: {suggestion.get('command', 'N/A')}")
            except:
                pass
        
        return state
    
    def _get_first_stage(self, mode):
        """获取模式的第一个阶段"""
        stage_mapping = {
            'minimal': 'P',
            'standard': 'P1',
            'complete': 'S1',
            'smart': 'S1'
        }
        return stage_mapping.get(mode, 'S1')
    
    def progress(self, stage, percentage):
        """更新进度 (PATEOAS增强版)"""
        state = self.load_state()
        
        if stage == 'current':
            stage = state.get('current_stage')
        
        if not stage:
            print("❌ 未找到当前阶段")
            return
        
        state['stage_progress'] = percentage
        state['overall_progress'] = min(percentage, 100)
        
        self.save_state(state)
        
        # 更新 PATEOAS 状态
        if self.pateoas_engine:
            try:
                self.pateoas_engine.state_continuity.update_state({
                    'task_progress': percentage / 100.0,
                    'stage_context': {
                        'current_stage': stage,
                        'stage_progress': percentage
                    },
                    'trigger': 'progress_update',
                    'reasoning': f'阶段 {stage} 进度更新到 {percentage}%'
                })
            except Exception as e:
                print(f"⚠️  PATEOAS 进度更新失败: {e}")
        
        print(f"📈 进度更新: {stage} -> {percentage}%")
        
        # 显示智能建议
        if self.pateoas_engine and percentage < 100:
            try:
                declaration = self.pateoas_engine.state_continuity.generate_state_declaration()
                if declaration.get('next_suggestions'):
                    print(f"💡 继续建议: {declaration['next_suggestions'][0].get('description', 'N/A')}")
            except:
                pass
        
        return state
    
    def complete(self, stage=None):
        """完成阶段 (PATEOAS增强版)"""
        state = self.load_state()
        
        if not stage:
            stage = state.get('current_stage')
        
        if not stage:
            print("❌ 未找到当前阶段")
            return
        
        print(f"✅ 完成阶段: {stage}")
        
        # 更新状态
        state['stage_progress'] = 100
        
        # 移动到下一阶段
        next_stage = self._get_next_stage(stage, state.get('selected_mode'))
        if next_stage:
            state['current_stage'] = next_stage
            state['stage_progress'] = 0
            print(f"➡️  进入下一阶段: {next_stage}")
        else:
            print("🎉 所有阶段完成！")
            state['current_stage'] = None
            state['overall_progress'] = 100
        
        self.save_state(state)
        
        # 更新 PATEOAS 状态
        if self.pateoas_engine:
            try:
                self.pateoas_engine.state_continuity.update_state({
                    'task_progress': 1.0 if not next_stage else 0.0,
                    'stage_context': {
                        'current_stage': next_stage or 'completed',
                        'completed_stages': state.get('completed_stages', []) + [stage]
                    },
                    'trigger': 'stage_completion',
                    'reasoning': f'完成阶段 {stage}' + (f'，进入 {next_stage}' if next_stage else '，项目完成')
                })
                
                # 添加完成记忆
                self.pateoas_engine.context_memory.add_memory(
                    content=f"完成阶段 {stage}",
                    category="learning",
                    importance=0.7,
                    tags=["阶段完成", stage]
                )
                
            except Exception as e:
                print(f"⚠️  PATEOAS 状态更新失败: {e}")
        
        return state
    
    def _get_next_stage(self, current_stage, mode):
        """获取下一个阶段"""
        stage_flows = {
            'minimal': ['P', 'D', 'R'],
            'standard': ['P1', 'P2', 'D1', 'D2', 'R1'],
            'complete': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'],
            'smart': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
        }
        
        flow = stage_flows.get(mode, [])
        if current_stage in flow:
            current_index = flow.index(current_stage)
            if current_index + 1 < len(flow):
                return flow[current_index + 1]
        
        return None
    
    def smart_assist(self, user_input):
        """智能助手模式"""
        if not self.pateoas_engine:
            print("❌ PATEOAS 引擎未启用，无法使用智能助手")
            return
        
        try:
            print("🧠 智能助手正在分析...")
            result = self.pateoas_engine.process_with_state_awareness(user_input)
            
            # 显示增强结果
            enhancement = result.get('pateoas_enhancement', {})
            
            print(f"\n💡 智能分析结果:")
            print(f"当前理解: {enhancement.get('meta_cognition', {}).get('current_understanding', 'N/A')}")
            
            if enhancement.get('recommended_action'):
                action = enhancement['recommended_action']
                print(f"\n🎯 推荐行动:")
                print(f"  描述: {action.get('description', 'N/A')}")
                print(f"  命令: {action.get('command', 'N/A')}")
                print(f"  置信度: {action.get('confidence', 0):.1%}")
            
            if enhancement.get('relevant_memory'):
                print(f"\n🧠 相关记忆:")
                for memory in enhancement['relevant_memory'][:2]:
                    print(f"  • {memory.get('content', 'N/A')[:80]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ 智能助手处理失败: {e}")
            return None
    
    def handle_pateoas_command(self, args):
        """处理PATEOAS专用命令"""
        if not self.pateoas_engine:
            print("❌ PATEOAS 引擎未启用，请使用 'init --mode smart' 初始化项目")
            return
        
        pateoas_command = args.pateoas_command
        
        if pateoas_command == 'status':
            self.pateoas_status(args.format, args.performance, args.memory_stats)
        elif pateoas_command == 'memory':
            self.pateoas_memory(args)
        elif pateoas_command == 'analyze':
            self.pateoas_analyze(args)
        elif pateoas_command == 'gates':
            self.pateoas_gates(args)
        elif pateoas_command == 'optimize':
            self.pateoas_optimize(args)
        elif pateoas_command == 'test':
            self.pateoas_test(args)
        elif pateoas_command == 'diagnose':
            self.pateoas_diagnose(args)
        elif pateoas_command == 'config':
            self.pateoas_config(args)
        else:
            print("❌ 未知的PATEOAS命令，使用 'pateoas -h' 查看帮助")
    
    def pateoas_status(self, format_type='text', include_performance=False, include_memory_stats=False):
        """显示PATEOAS详细状态"""
        try:
            if format_type == 'json':
                status = self.pateoas_engine.get_pateoas_status()
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                self._print_pateoas_status_text(include_performance, include_memory_stats)
        except Exception as e:
            print(f"❌ 获取PATEOAS状态失败: {e}")
    
    def _print_pateoas_status_text(self, include_performance, include_memory_stats):
        """打印文本格式的PATEOAS状态"""
        try:
            status = self.pateoas_engine.get_pateoas_status()
            
            print("\n🧠 PATEOAS 增强状态")
            print("=" * 50)
            
            # 系统信息
            system_info = status['system_info']
            print(f"系统状态: {system_info['status']}")
            print(f"项目ID: {system_info['project_id']}")
            print(f"启动时间: {system_info['start_time']}")
            print(f"运行时长: {system_info['uptime']}")
            
            # 性能指标
            if include_performance:
                print(f"\n📈 性能指标:")
                perf = status['performance_metrics']
                print(f"  总交互次数: {perf['total_interactions']}")
                print(f"  成功率: {perf['success_rate']:.1%}")
                print(f"  平均响应时间: {perf.get('avg_response_time', 'N/A')}")
                print(f"  错误次数: {perf.get('error_count', 0)}")
            
            # 记忆统计
            if include_memory_stats:
                print(f"\n🧠 记忆统计:")
                memory_info = status['memory_info']
                print(f"  总记忆数: {memory_info['total_memories']}")
                
                if 'category_breakdown' in memory_info:
                    print("  分类统计:")
                    for category, count in memory_info['category_breakdown'].items():
                        print(f"    {category}: {count}")
            
            # 当前状态和建议
            if 'current_state' in status:
                current = status['current_state']
                if current.get('task_progress'):
                    print(f"\n📊 当前任务:")
                    print(f"  进度: {current['task_progress']:.1%}")
                    print(f"  阶段: {current.get('current_stage', 'N/A')}")
            
            # 智能建议
            try:
                declaration = self.pateoas_engine.state_manager.generate_state_declaration()
                if declaration.get('next_suggestions'):
                    print(f"\n💡 智能建议:")
                    for i, suggestion in enumerate(declaration['next_suggestions'][:3], 1):
                        print(f"  {i}. {suggestion.get('description', 'N/A')}")
                        if suggestion.get('command'):
                            print(f"     命令: {suggestion['command']}")
            except:
                pass
                
        except Exception as e:
            print(f"❌ 显示状态时发生错误: {e}")
    
    def pateoas_memory(self, args):
        """处理记忆管理命令 (优化版本，消除参数冲突)"""
        memory_action = args.memory_action
        
        if memory_action == 'list':
            self._memory_list(args.category, args.limit, args.recent, getattr(args, 'tags', None))
        elif memory_action == 'add':
            self._memory_add(args.content, args.category, args.tags, args.importance)
        elif memory_action == 'find':
            self._memory_find(args.query, args.limit, getattr(args, 'category', None))
        elif memory_action == 'recall':
            self._memory_recall(args.query, args.limit, args.context, getattr(args, 'min_relevance', 0.3))
        elif memory_action == 'smart-recall':
            self._memory_smart_recall(args.query, args.context, args.limit, 
                                    args.include_patterns, args.priority_recent, 
                                    getattr(args, 'detailed', False))
        elif memory_action == 'clean':
            self._memory_clean(args.days, args.category, args.confirm, getattr(args, 'dry_run', False))
        # 向后兼容性支持
        elif memory_action == 'search':
            print("⚠️ 'search' 命令已废弃，请使用 'find' 命令")
            self._memory_find(args.query if hasattr(args, 'query') else '', 
                            getattr(args, 'limit', 5), None)
        elif memory_action == 'intelligent-recall':
            print("⚠️ 'intelligent-recall' 命令已重命名为 'smart-recall'")
            query = getattr(args, 'query', '')
            self._memory_smart_recall(query, getattr(args, 'context', None), 
                                    getattr(args, 'limit', 10), 
                                    getattr(args, 'include_patterns', False), 
                                    getattr(args, 'priority_recent', False), False)
        else:
            print("❌ 未知的记忆操作，使用 'pateoas memory -h' 查看帮助")
            print("💡 可用命令: list, add, find, recall, smart-recall, clean")
    
    def _memory_list(self, category=None, limit=10, recent=False, tags=None):
        """列出记忆 (支持标签过滤)"""
        try:
            print(f"📚 记忆列表 (最多{limit}条)")
            if category:
                print(f"   📂 类别过滤: {category}")
            if tags:
                print(f"   🏷️ 标签过滤: {tags}")
            if recent:
                print(f"   ⏰ 仅显示最近记忆")
            print()
            
            # 使用记忆系统的搜索功能来获取记忆列表
            memories = self.pateoas_engine.memory_system.search_memories(
                query="", category=category, limit=limit*2 if recent else limit
            )
            
            # 标签过滤
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                filtered_memories = []
                for memory in memories:
                    memory_tags = memory.get('tags', [])
                    if any(tag in memory_tags for tag in tag_list):
                        filtered_memories.append(memory)
                memories = filtered_memories
            
            # 最近记忆过滤
            if recent:
                memories = sorted(memories, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
            
            if not memories:
                print("📭 未找到符合条件的记忆")
                return
            
            print(f"找到 {len(memories)} 条记忆:")
            print("=" * 60)
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'N/A')
                category_name = memory.get('category', 'unknown')
                created_at = memory.get('created_at', 'N/A')
                importance = memory.get('importance', 0)
                memory_tags = memory.get('tags', [])
                
                print(f"{i}. [{category_name}] {content[:60]}{'...' if len(content) > 60 else ''}")
                print(f"   ⭐ 重要性: {importance:.2f}")
                print(f"   🕒 创建: {created_at}")
                if memory_tags:
                    print(f"   🏷️ 标签: {', '.join(memory_tags)}")
                print()
                
        except Exception as e:
            print(f"❌ 列出记忆失败: {e}")
    
    def _memory_add(self, content, category='context', tags=None, importance=0.5):
        """添加记忆到系统 (支持位置参数)"""
        try:
            print(f"💾 添加记忆到{category}类别...")
            
            # 解析标签
            tag_list = []
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
            
            # 存储记忆
            memory_id = self.pateoas_engine.memory_system.add_memory(
                content=content,
                category=category,
                tags=tag_list,
                importance=importance
            )
            
            print(f"✅ 记忆已添加")
            print(f"   ID: {memory_id}")
            print(f"   类别: {category}")
            print(f"   重要性: {importance}")
            if tag_list:
                print(f"   标签: {', '.join(tag_list)}")
            print(f"   内容: {content[:100]}{'...' if len(content) > 100 else ''}")
            
        except Exception as e:
            print(f"❌ 添加记忆失败: {e}")
    
    def _memory_find(self, query, limit=5, category=None):
        """基础记忆搜索 (替代search命令)"""
        try:
            print(f"🔍 基础搜索: '{query}'")
            if category:
                print(f"   📂 限制类别: {category}")
            print()
            
            # 使用记忆系统的搜索功能
            memories = self.pateoas_engine.memory_system.search_memories(
                query, limit=limit, category=category
            )
            
            if not memories:
                print("📭 未找到相关记忆")
                print("💡 尝试:")
                print("  • 使用更通用的关键词")
                print("  • 使用 'recall' 命令进行智能召回")
                return
            
            print(f"🔍 找到 {len(memories)} 条匹配记忆:")
            print("=" * 50)
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'N/A')
                mem_category = memory.get('category', 'unknown')
                created_at = memory.get('created_at', 'N/A')
                tags = memory.get('tags', [])
                
                print(f"{i}. [{mem_category}] {content[:70]}{'...' if len(content) > 70 else ''}")
                print(f"   📅 {created_at}")
                if tags:
                    print(f"   🏷️ {', '.join(tags)}")
                print()
                
        except Exception as e:
            print(f"❌ 基础搜索失败: {e}")
    
    def _memory_recall(self, query, limit=10, context=None, min_relevance=0.3):
        """智能记忆召回 (中级功能，支持相关性过滤)"""
        try:
            print(f"🧠 智能召回: '{query}'")
            if context:
                print(f"   📋 上下文: {context}")
            print(f"   🎯 最低相关性: {min_relevance}")
            print()
            
            # 使用智能召回系统
            current_state = {'query_context': context} if context else {}
            
            recall_result = self.pateoas_engine.memory_system.intelligent_recall(
                query=query,
                current_state=current_state,
                limit=limit,
                min_relevance=min_relevance
            )
            
            memories = recall_result.get('results', []) if isinstance(recall_result, dict) else recall_result
            
            # 过滤低相关性记忆
            filtered_memories = [m for m in memories if m.get('relevance_score', 0) >= min_relevance]
            
            if not filtered_memories:
                print(f"🧠 未找到相关性≥{min_relevance}的记忆")
                print("💡 尝试:")
                print("  • 降低相关性阈值")
                print("  • 使用更通用的查询词")
                print("  • 尝试 'smart-recall' 获得更深入分析")
                return
            
            print(f"🧠 智能召回结果: '{query}' (共{len(filtered_memories)}条)")
            print("=" * 60)
            
            for i, memory in enumerate(filtered_memories, 1):
                content = memory.get('content', 'N/A')
                category_name = memory.get('category', 'unknown')
                created_at = memory.get('created_at', 'N/A')
                tags = memory.get('tags', [])
                relevance = memory.get('relevance_score', 0)
                
                print(f"{i}. [{category_name}] {content}")
                print(f"   🎯 相关性: {relevance:.2f}")
                print(f"   📅 创建: {created_at}")
                if tags:
                    print(f"   🏷️ 标签: {', '.join(tags)}")
                print()
                
            # 显示召回洞察
            if isinstance(recall_result, dict) and 'insights' in recall_result:
                print(f"\n💡 智能洞察:")
                for insight in recall_result['insights']:
                    print(f"  • {insight}")
                    
        except Exception as e:
            print(f"❌ 智能召回失败: {e}")
    
    def _memory_search(self, query, limit=5):
        """搜索记忆"""
        try:
            # 使用记忆系统的搜索功能
            memories = self.pateoas_engine.memory_system.search_memories(
                query=query, limit=limit
            )
            
            if not memories:
                print(f"🔍 未找到与 '{query}' 相关的记忆")
                return
            
            print(f"\n🔍 搜索结果: '{query}' (共{len(memories)}条)")
            print("=" * 60)
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'N/A')
                category_name = memory.get('category', 'unknown')
                created_at = memory.get('created_at', 'N/A')
                tags = memory.get('tags', [])
                relevance = memory.get('relevance_score', memory.get('importance', 0))
                
                print(f"{i}. [{category_name}] {content}")
                print(f"   相关性: {relevance:.2f}")
                print(f"   创建时间: {created_at}")
                if tags:
                    print(f"   标签: {', '.join(tags)}")
                print()
                
        except Exception as e:
            print(f"❌ 搜索记忆失败: {e}")
    
    def _memory_smart_recall(self, query, context=None, limit=10, include_patterns=False, priority_recent=False, detailed=False):
        """高级智能记忆召回 (最高级功能，替换intelligent-recall)"""
        try:
            print(f"🧠 PATEOAS高级智能召回: '{query}'")
            if context:
                print(f"📋 上下文: {context}")
            if include_patterns:
                print("🔍 包含模式分析")
            if priority_recent:
                print("⏰ 优先最近记忆")
            if detailed:
                print("📊 显示详细分析")
            print()
            
            # 构建智能召回参数
            current_state = {
                'context': context,
                'analysis_mode': 'detailed' if detailed else 'standard',
                'pattern_analysis': include_patterns,
                'priority_recent': priority_recent
            }
            
            # 使用增强的智能召回功能
            if hasattr(self.pateoas_engine.memory_system, 'intelligent_recall'):
                results = self.pateoas_engine.memory_system.intelligent_recall(
                    query=query,
                    current_state=current_state,
                    limit=limit
                )
                
                # 提取结果
                if isinstance(results, dict) and 'results' in results:
                    memories = results['results']
                    analysis_data = results
                else:
                    memories = results
                    analysis_data = {}
            else:
                # 降级到普通搜索
                memories = self.pateoas_engine.memory_system.search_memories(query, limit)
                analysis_data = {}
            
            if not memories:
                print("📭 未找到相关记忆")
                print("💡 建议:")
                print("  • 尝试使用更通用的关键词")
                print("  • 使用 'memory add' 命令添加相关记忆")
                print("  • 检查是否有拼写错误")
                return
            
            print(f"🧠 找到 {len(memories)} 条高度相关记忆:")
            print("=" * 70)
            
            for i, memory in enumerate(memories, 1):
                relevance = memory.get('relevance_score', 0.0)
                content = memory.get('content', '无内容')
                category = memory.get('category', 'unknown')
                created_at = memory.get('created_at', '未知')
                tags = memory.get('tags', [])
                reasoning = memory.get('reasoning', '')
                
                print(f"{i}. 📝 {content[:80]}{'...' if len(content) > 80 else ''}")
                print(f"   ┣━ 🎯 相关度: {relevance:.3f}")
                print(f"   ┣━ 📂 类别: {category}")
                print(f"   ┣━ 📅 创建: {created_at}")
                if tags:
                    print(f"   ┣━ 🏷️ 标签: {', '.join(tags)}")
                if detailed and reasoning:
                    print(f"   ┣━ 💭 推理: {reasoning}")
                print(f"   ┗━ {'=' * 50}")
                print()
            
            # 显示模式分析(如果启用)
            if include_patterns:
                print("🔍 智能模式分析:")
                patterns = self._analyze_memory_patterns(memories)
                for pattern in patterns:
                    print(f"  • {pattern}")
                print()
            
            # 显示上下文洞察
            print("💡 基于记忆的深度洞察:")
            insights = self._generate_memory_insights(memories, query, context)
            for insight in insights:
                print(f"  • {insight}")
            
            # 显示高级分析数据
            if detailed and analysis_data:
                if 'statistics' in analysis_data:
                    stats = analysis_data['statistics']
                    print(f"\n📊 详细统计:")
                    print(f"  • 总搜索时间: {stats.get('search_time', 'N/A')}")
                    print(f"  • 平均相关性: {stats.get('avg_relevance', 'N/A')}")
                    print(f"  • 覆盖类别: {len(set(m.get('category', '') for m in memories))}")
                
                if 'query_analysis' in analysis_data:
                    query_info = analysis_data['query_analysis']
                    print(f"\n🔍 查询分析:")
                    print(f"  • 查询类型: {query_info.get('intent', 'N/A')}")
                    print(f"  • 关键概念: {', '.join(query_info.get('key_concepts', []))}")
                
        except Exception as e:
            print(f"❌ 高级智能召回失败: {e}")
    
    def _memory_clean(self, days=30, category=None, confirm=False, dry_run=False):
        """清理记忆 (支持预览模式)"""
        try:
            print(f"🧹 记忆清理操作")
            print(f"   📅 清理范围: {days}天前的记忆")
            if category:
                print(f"   📂 限制类别: {category}")
            if dry_run:
                print(f"   👁️ 预览模式: 仅显示将被清理的记忆")
            print()
            
            if dry_run:
                print("🔍 预览将被清理的记忆...")
                # 这里应该调用记忆系统的预览清理功能
                # 暂时用搜索来模拟
                print("💡 dry-run 功能需要记忆系统支持，当前仅显示提示")
                return
            
            if not confirm:
                response = input(f"⚠️  确定要清理{days}天前的记忆吗？(y/N): ")
                if response.lower() != 'y':
                    print("❌ 取消清理操作")
                    return
            
            # 调用记忆系统的清理功能
            cleaned_count = self.pateoas_engine.memory_system.cleanup_old_memories(days=days)
            
            print(f"✅ 已清理 {cleaned_count} 条记忆")
            
        except Exception as e:
            print(f"❌ 清理记忆失败: {e}")
    
    def _analyze_memory_patterns(self, memories):
        """分析记忆模式"""
        patterns = []
        
        # 类别分布分析
        categories = {}
        for memory in memories:
            cat = memory.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            main_category = max(categories, key=categories.get)
            patterns.append(f"主要类别: {main_category} ({categories[main_category]}条)")
        
        # 时间分布分析
        created_ats = [m.get('created_at', '') for m in memories if m.get('created_at')]
        if created_ats:
            # 简单的时间分析，检查是否大部分是最近的
            import datetime
            try:
                recent_count = 0
                now = datetime.datetime.now()
                for created_at in created_ats:
                    if created_at and '2025-07-27' in created_at:  # 简单的最近检查
                        recent_count += 1
                if recent_count > len(created_ats) * 0.5:
                    patterns.append("大部分记忆来自最近时期")
            except:
                pass
        
        # 标签频率分析
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.get('tags', []))
        
        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            common_tags = tag_counts.most_common(3)
            patterns.append(f"常见标签: {', '.join([tag for tag, count in common_tags])}")
        
        return patterns
    
    def _generate_memory_insights(self, memories, query, context):
        """生成基于记忆的洞察"""
        insights = []
        
        if not memories:
            return ["暂无相关记忆可供分析"]
        
        # 基于记忆数量的洞察
        if len(memories) == 1:
            insights.append("这是一个相对独特的查询，系统中记忆较少")
        elif len(memories) > 5:
            insights.append("这是一个常见主题，系统中有丰富的相关经验")
        
        # 基于记忆质量的洞察
        avg_relevance = sum(m.get('relevance_score', 0) for m in memories) / len(memories)
        if avg_relevance > 0.8:
            insights.append("找到高度相关的记忆，建议重点参考")
        elif avg_relevance < 0.5:
            insights.append("记忆相关度一般，可能需要更精确的查询词")
        
        # 基于上下文的洞察
        if context:
            insights.append(f"结合当前上下文'{context}'，这些记忆特别有价值")
        
        # 建议后续行动
        categories = set(m.get('category', 'unknown') for m in memories)
        if 'decision' in categories:
            insights.append("包含决策相关记忆，建议参考历史决策模式")
        if 'pattern' in categories:
            insights.append("包含模式记忆，建议应用已识别的最佳实践")
        if 'issue' in categories:
            insights.append("包含问题处理记忆，建议注意潜在风险点")
        
        return insights
    
    
    def pateoas_analyze(self, args):
        """增强任务分析"""
        try:
            project_context = {
                'team_size': args.team_size,
                'urgency': args.urgency,
                'project_type': args.project_type
            }
            
            print(f"🧠 PATEOAS增强分析: {args.task}")
            print("=" * 50)
            
            result = self.pateoas_engine.analyze_and_recommend(args.task, project_context)
            
            # 显示分析结果
            self._display_analysis_result(result, args.detailed)
            
            # 保存分析结果
            if args.save_analysis:
                self._save_analysis_result(result, args.task)
            
        except Exception as e:
            print(f"❌ 增强分析失败: {e}")
    
    def _display_analysis_result(self, result, detailed=False):
        """显示分析结果"""
        # 基本分析结果
        task_analysis = result['task_analysis']
        mode_rec = result['mode_recommendation']
        
        print(f"\n📊 任务分析:")
        print(f"  复杂度: {task_analysis['complexity_factors']['primary_level']}")
        print(f"  预估工作量: {task_analysis['estimated_effort']}")
        print(f"  关键挑战: {len(task_analysis['key_challenges'])}个")
        
        print(f"\n🎯 模式推荐:")
        print(f"  推荐模式: {mode_rec['recommended_mode']}")
        print(f"  置信度: {mode_rec['confidence']:.1%}")
        print(f"  推理: {mode_rec['reasoning']}")
        
        # 优化建议
        opt_suggestions = result['optimization_suggestions']
        parallel_ops = opt_suggestions.get('parallel_execution', [])
        if parallel_ops:
            print(f"\n⚡ 并行执行机会:")
            for opp in parallel_ops[:3]:
                print(f"  • {opp['description']}")
                print(f"    预计节省时间: {opp.get('time_saving', 'N/A')}")
        
        # 详细信息
        if detailed:
            print(f"\n📋 详细分析:")
            
            # 复杂度因素
            complexity = task_analysis['complexity_factors']
            print(f"  技术深度: {complexity.get('technical_depth', 'N/A')}")
            print(f"  集成复杂度: {complexity.get('integration_complexity', 'N/A')}")
            
            # 风险评估
            risks = result.get('risk_assessment', {})
            for risk_type, risk_list in risks.items():
                if risk_list:
                    print(f"  {risk_type}: {len(risk_list)}个")
            
            # 历史相似项目
            similar_projects = result['contextual_insights'].get('similar_projects', [])
            if similar_projects:
                print(f"  相似项目: {len(similar_projects)}个")
        
        # 分析元数据
        metadata = result['analysis_metadata']
        print(f"\n📈 分析元数据:")
        print(f"  处理时间: {metadata['processing_duration']:.3f}秒")
        print(f"  使用历史记忆: {metadata['data_sources']['historical_memories']}条")
        print(f"  置信度: {metadata['confidence_score']:.1%}")
    
    def _save_analysis_result(self, result, task_description):
        """保存分析结果到文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"aceflow_analysis_{timestamp}.json"
            
            analysis_data = {
                'task_description': task_description,
                'analysis_result': result,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 分析结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存分析结果失败: {e}")
    
    def pateoas_gates(self, args):
        """处理决策门命令"""
        gates_action = args.gates_action
        
        if gates_action == 'evaluate':
            self._gates_evaluate(args.gate_id, args.verbose)
        elif gates_action == 'list':
            self._gates_list()
        elif gates_action == 'history':
            self._gates_history(args.gate_id, args.limit)
        else:
            print("❌ 未知的决策门操作，使用 'pateoas gates -h' 查看帮助")
    
    def _gates_evaluate(self, gate_id=None, verbose=False):
        """评估决策门"""
        try:
            print("🚦 开始决策门评估...")
            
            # 获取当前状态和记忆
            current_state = self.pateoas_engine.state_manager.get_current_state()
            memories = []
            
            # 获取最近的记忆片段用于评估
            memory_search = self.pateoas_engine.memory_system.search_memories("", limit=20)
            for mem in memory_search:
                from pateoas.models import MemoryFragment, MemoryCategory
                memory_obj = MemoryFragment(
                    content=mem['content'],
                    category=MemoryCategory(mem['category']),
                    importance=mem['importance'],
                    tags=mem['tags'],
                    created_at=datetime.fromisoformat(mem['created_at'])
                )
                memories.append(memory_obj)
            
            # 执行决策门评估
            if gate_id:
                # 评估特定决策门
                evaluation = self.pateoas_engine.decision_gate_manager.evaluate_gate(
                    gate_id, current_state, memories, {}
                )
                print(f"\n🚦 {gate_id} 决策门评估结果:")
                print(f"  结果: {evaluation.result.value}")
                print(f"  置信度: {evaluation.confidence:.2f}")
                print(f"  总分: {evaluation.score:.2f}")
                
                if verbose:
                    print(f"\n📊 详细评估:")
                    for criteria, score in evaluation.criteria_scores.items():
                        print(f"  {criteria}: {score:.2f}")
                    
                    if evaluation.recommendations:
                        print(f"\n💡 建议:")
                        for rec in evaluation.recommendations:
                            print(f"  • {rec}")
                    
                    if evaluation.risk_factors:
                        print(f"\n⚠️ 风险因素:")
                        for risk in evaluation.risk_factors:
                            print(f"  • {risk}")
            else:
                # 评估所有决策门
                evaluations = self.pateoas_engine.decision_gate_manager.evaluate_all_gates(
                    current_state, memories, {}
                )
                
                if evaluations:
                    print(f"\n🚦 所有决策门评估结果:")
                    print("=" * 50)
                    for gate_id, evaluation in evaluations.items():
                        print(f"\n{gate_id}: {evaluation.result.value}")
                        print(f"  置信度: {evaluation.confidence:.2f}")
                        print(f"  总分: {evaluation.score:.2f}")
                        
                        if verbose and evaluation.recommendations:
                            print(f"  建议: {evaluation.recommendations[0]}")
                else:
                    print("📋 当前没有可评估的决策门")
                    
        except Exception as e:
            print(f"❌ 决策门评估失败: {e}")
    
    def _gates_list(self):
        """列出可用决策门"""
        try:
            from pateoas.decision_gates import DecisionGateFactory
            
            available_gates = DecisionGateFactory.get_available_gates()
            
            print(f"\n🚦 可用决策门 (共{len(available_gates)}个):")
            print("=" * 40)
            
            for gate_id in available_gates:
                gate = DecisionGateFactory.create_decision_gate(gate_id)
                print(f"{gate_id}: {gate.name}")
                print(f"  描述: {gate.description}")
                print()
                
        except Exception as e:
            print(f"❌ 获取决策门列表失败: {e}")
    
    def _gates_history(self, gate_id=None, limit=10):
        """查看决策门评估历史"""
        try:
            history = self.pateoas_engine.decision_gate_manager.get_evaluation_history(gate_id)
            
            if not history:
                print("📋 暂无决策门评估历史")
                return
            
            # 限制显示数量
            history = history[-limit:]
            
            title = f"决策门 {gate_id} 评估历史" if gate_id else "所有决策门评估历史"
            print(f"\n📊 {title} (最近{len(history)}条):")
            print("=" * 60)
            
            for i, record in enumerate(history, 1):
                timestamp = record.get('timestamp', 'N/A')
                gate = record.get('gate_id', 'N/A')
                result = record.get('result', 'N/A')
                confidence = record.get('confidence', 0)
                score = record.get('score', 0)
                
                print(f"{i}. [{gate}] {result}")
                print(f"   时间: {timestamp}")
                print(f"   置信度: {confidence:.2f} | 分数: {score:.2f}")
                print()
                
        except Exception as e:
            print(f"❌ 获取评估历史失败: {e}")
    
    def pateoas_optimize(self, args):
        """处理工作流优化命令"""
        try:
            print("⚡ 开始工作流优化分析...")
            
            # 获取当前状态
            current_state = self.pateoas_engine.state_manager.get_current_state()
            project_context = current_state.get('project_context', {})
            
            # 使用流程控制器进行优化分析
            optimizations = self.pateoas_engine.flow_controller.optimize_workflow(
                current_state, project_context
            )
            
            print(f"\n⚡ 工作流优化分析结果:")
            print("=" * 50)
            
            # 显示瓶颈分析
            if 'bottlenecks' in optimizations:
                bottlenecks = optimizations['bottlenecks']
                if bottlenecks:
                    print(f"\n🔍 识别到的瓶颈 ({len(bottlenecks)}个):")
                    for i, bottleneck in enumerate(bottlenecks, 1):
                        print(f"  {i}. {bottleneck}")
            
            # 显示并行执行机会
            if 'parallel_execution' in optimizations:
                parallel_ops = optimizations['parallel_execution']
                if parallel_ops:
                    print(f"\n⚡ 并行执行机会 ({len(parallel_ops)}个):")
                    for i, op in enumerate(parallel_ops, 1):
                        print(f"  {i}. {op.get('type', 'N/A')}")
                        print(f"     阶段: {op.get('stages', [])}")
                        print(f"     节省时间: {op.get('time_saving', 'N/A')}")
                        print(f"     风险级别: {op.get('risk_level', 'N/A')}")
                        print()
            
            # 显示其他优化建议
            if args.suggest_improvements:
                print(f"\n💡 改进建议:")
                
                if 'stage_reordering' in optimizations:
                    reordering = optimizations['stage_reordering']
                    if reordering:
                        print(f"  • 阶段重排序机会: {len(reordering)}个")
                
                if 'stage_skipping' in optimizations:
                    skipping = optimizations['stage_skipping']
                    if skipping:
                        print(f"  • 可跳过阶段: {len(skipping)}个")
                
                if 'resource_allocation' in optimizations:
                    allocation = optimizations['resource_allocation']
                    if allocation:
                        print(f"  • 资源分配优化: 已识别")
            
        except Exception as e:
            print(f"❌ 工作流优化分析失败: {e}")
    
    def pateoas_test(self, args):
        """处理系统测试命令"""
        try:
            print("🧪 开始PATEOAS系统测试...")
            
            if args.all_components:
                self._test_all_components()
            elif args.component:
                self._test_component(args.component)
            elif args.quick:
                self._test_quick()
            else:
                self._test_basic()
                
        except Exception as e:
            print(f"❌ 系统测试失败: {e}")
    
    def _test_all_components(self):
        """测试所有组件"""
        components = ['memory', 'gates', 'flow', 'engine']
        results = {}
        
        for component in components:
            print(f"\n🔍 测试组件: {component}")
            results[component] = self._test_component(component, quiet=True)
        
        print(f"\n📊 组件测试总结:")
        print("=" * 30)
        for component, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{component}: {status}")
    
    def _test_component(self, component, quiet=False):
        """测试特定组件"""
        try:
            if component == 'memory':
                # 测试记忆系统
                memories = self.pateoas_engine.memory_system.search_memories("test", limit=1)
                if not quiet:
                    print("✅ 记忆系统运行正常")
                return True
                
            elif component == 'gates':
                # 测试决策门
                available_gates = self.pateoas_engine.decision_gate_manager.gates
                if not quiet:
                    print(f"✅ 决策门系统运行正常 ({len(available_gates)}个门)")
                return True
                
            elif component == 'flow':
                # 测试流程控制器
                decision = self.pateoas_engine.flow_controller.decide_next_action("test", {}, [])
                if not quiet:
                    print("✅ 流程控制器运行正常")
                return True
                
            elif component == 'engine':
                # 测试增强引擎
                status = self.pateoas_engine.get_pateoas_status()
                if not quiet:
                    print("✅ PATEOAS增强引擎运行正常")
                return True
                
            return False
            
        except Exception as e:
            if not quiet:
                print(f"❌ 组件 {component} 测试失败: {e}")
            return False
    
    def _test_quick(self):
        """快速测试"""
        print("⚡ 执行快速测试...")
        try:
            # 测试基本功能
            status = self.pateoas_engine.get_pateoas_status()
            print("✅ 基本功能正常")
            
            # 测试状态管理
            current_state = self.pateoas_engine.state_manager.get_current_state()
            print("✅ 状态管理正常")
            
            print("\n🎉 快速测试通过！")
            
        except Exception as e:
            print(f"❌ 快速测试失败: {e}")
    
    def _test_basic(self):
        """基础测试"""
        print("🔍 执行基础功能测试...")
        
        tests = [
            ("PATEOAS引擎初始化", lambda: self.pateoas_engine is not None),
            ("状态管理器", lambda: self.pateoas_engine.state_manager.get_current_state()),
            ("记忆系统", lambda: self.pateoas_engine.memory_system.get_memory_stats()),
            ("流程控制器", lambda: hasattr(self.pateoas_engine, 'flow_controller')),
            ("决策门", lambda: len(self.pateoas_engine.decision_gate_manager.gates) >= 0)
        ]
        
        passed = 0
        for test_name, test_func in tests:
            try:
                test_func()
                print(f"✅ {test_name}")
                passed += 1
            except Exception as e:
                print(f"❌ {test_name}: {e}")
        
        print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    def pateoas_diagnose(self, args):
        """处理系统诊断命令"""
        try:
            print("🔍 开始PATEOAS系统诊断...")
            
            diagnosis = {
                'timestamp': datetime.now().isoformat(),
                'system_status': {},
                'component_health': {},
                'performance_metrics': {},
                'recommendations': []
            }
            
            # 系统状态诊断
            try:
                status = self.pateoas_engine.get_pateoas_status()
                diagnosis['system_status'] = status.get('system_info', {})
                diagnosis['performance_metrics'] = status.get('performance_metrics', {})
                print("✅ 系统状态诊断完成")
            except Exception as e:
                print(f"⚠️ 系统状态诊断失败: {e}")
            
            # 组件健康检查
            components = ['memory_system', 'state_manager', 'flow_controller', 'decision_gates']
            for component in components:
                try:
                    if hasattr(self.pateoas_engine, component.replace('_', '')):
                        diagnosis['component_health'][component] = 'healthy'
                    else:
                        diagnosis['component_health'][component] = 'missing'
                except:
                    diagnosis['component_health'][component] = 'error'
            
            # 生成建议
            unhealthy = [comp for comp, health in diagnosis['component_health'].items() 
                        if health != 'healthy']
            
            if unhealthy:
                diagnosis['recommendations'].append(f"检查组件: {', '.join(unhealthy)}")
            
            if diagnosis['performance_metrics'].get('success_rate', 1.0) < 0.9:
                diagnosis['recommendations'].append("性能监控显示成功率较低，建议检查系统负载")
            
            # 显示诊断结果
            print(f"\n🔍 诊断结果:")
            print("=" * 40)
            print(f"系统状态: {diagnosis['system_status'].get('status', 'unknown')}")
            
            print(f"\n🏥 组件健康状态:")
            for component, health in diagnosis['component_health'].items():
                status_emoji = "✅" if health == 'healthy' else "❌"
                print(f"  {status_emoji} {component}: {health}")
            
            if diagnosis['recommendations']:
                print(f"\n💡 诊断建议:")
                for i, rec in enumerate(diagnosis['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            # 保存诊断报告
            if args.generate_report:
                filename = f"pateoas_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(diagnosis, f, indent=2, ensure_ascii=False)
                print(f"\n📄 诊断报告已保存: {filename}")
            
        except Exception as e:
            print(f"❌ 系统诊断失败: {e}")
    
    def pateoas_config(self, args):
        """处理PATEOAS配置命令"""
        config_action = args.config_action
        
        if config_action == 'show':
            self._config_show(args.key)
        elif config_action == 'set':
            self._config_set(args.key, args.value)
        elif config_action == 'reset':
            self._config_reset(args.confirm)
        else:
            print("❌ 未知的配置操作，使用 'pateoas config -h' 查看帮助")
    
    def _config_show(self, key=None):
        """显示配置"""
        try:
            config = self.pateoas_engine.config
            
            if key:
                if hasattr(config, key):
                    value = getattr(config, key)
                    print(f"{key}: {value}")
                else:
                    print(f"❌ 配置项 '{key}' 不存在")
            else:
                print("\n⚙️  PATEOAS 配置:")
                print("=" * 30)
                
                # 显示主要配置项
                config_items = [
                    ('memory_retention_days', '记忆保留天数'),
                    ('performance_monitoring', '性能监控'),
                    ('auto_optimization', '自动优化'),
                    ('decision_confidence_threshold', '决策置信度阈值'),
                    ('memory_search_limit', '记忆搜索限制')
                ]
                
                for key, desc in config_items:
                    if hasattr(config, key):
                        value = getattr(config, key)
                        print(f"{desc}: {value}")
                
        except Exception as e:
            print(f"❌ 显示配置失败: {e}")
    
    def _config_set(self, key, value):
        """设置配置项"""
        try:
            # 类型转换
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
            
            # 设置配置
            if hasattr(self.pateoas_engine.config, key):
                setattr(self.pateoas_engine.config, key, value)
                print(f"✅ 配置项 '{key}' 已设置为: {value}")
            else:
                print(f"❌ 配置项 '{key}' 不存在")
                
        except Exception as e:
            print(f"❌ 设置配置失败: {e}")
    
    def _config_reset(self, confirm=False):
        """重置配置"""
        try:
            if not confirm:
                response = input("⚠️  确定要重置所有PATEOAS配置吗？(y/N): ")
                if response.lower() != 'y':
                    print("取消重置操作")
                    return
            
            # 重置配置
            self.pateoas_engine.config.reset_to_defaults()
            print("✅ PATEOAS配置已重置为默认值")
            
        except Exception as e:
            print(f"❌ 重置配置失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='AceFlow v3.0 增强版 CLI 工具 (集成PATEOAS)')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化项目')
    init_parser.add_argument('--mode', choices=['smart', 'minimal', 'standard', 'complete'], 
                           default='smart', help='流程模式')
    init_parser.add_argument('--no-pateoas', action='store_true', help='禁用PATEOAS增强')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='查看状态')
    status_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    status_parser.add_argument('--verbose', action='store_true', help='详细输出')
    status_parser.add_argument('--pateoas', action='store_true', help='显示PATEOAS状态')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析任务')
    analyze_parser.add_argument('task', help='任务描述')
    analyze_parser.add_argument('--team-size', type=int, help='团队规模')
    analyze_parser.add_argument('--urgency', choices=['low', 'normal', 'high', 'emergency'], help='紧急程度')
    analyze_parser.add_argument('--project-type', help='项目类型')
    
    # start 命令
    start_parser = subparsers.add_parser('start', help='开始工作流')
    start_parser.add_argument('--description', help='任务描述')
    start_parser.add_argument('--mode', choices=['smart', 'minimal', 'standard', 'complete'], 
                            help='流程模式')
    start_parser.add_argument('--no-analyze', action='store_true', help='跳过智能分析')
    
    # progress 命令
    progress_parser = subparsers.add_parser('progress', help='更新进度')
    progress_parser.add_argument('stage', help='阶段名称')
    progress_parser.add_argument('percentage', type=int, help='进度百分比')
    
    # complete 命令
    complete_parser = subparsers.add_parser('complete', help='完成阶段')
    complete_parser.add_argument('stage', nargs='?', default='current', help='阶段名称')
    
    # assist 命令 (新增)
    assist_parser = subparsers.add_parser('assist', help='智能助手')
    assist_parser.add_argument('input', help='您的问题或需求')
    
    # PATEOAS专用命令组
    pateoas_subparsers = subparsers.add_parser('pateoas', help='PATEOAS增强功能').add_subparsers(dest='pateoas_command', help='PATEOAS子命令')
    
    # pateoas status 命令
    pateoas_status_parser = pateoas_subparsers.add_parser('status', help='显示PATEOAS详细状态')
    pateoas_status_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    pateoas_status_parser.add_argument('--performance', action='store_true', help='包含性能指标')
    pateoas_status_parser.add_argument('--memory-stats', action='store_true', help='显示记忆统计')
    
    # pateoas memory 命令 (重新设计，消除参数冲突)
    pateoas_memory_parser = pateoas_subparsers.add_parser('memory', help='记忆管理功能')
    pateoas_memory_subparsers = pateoas_memory_parser.add_subparsers(dest='memory_action', help='记忆操作')
    
    # memory list 子命令 - 列出记忆
    memory_list_parser = pateoas_memory_subparsers.add_parser('list', help='列出记忆')
    memory_list_parser.add_argument('--category', choices=['context', 'decision', 'pattern', 'issue', 'learning'], help='过滤记忆类别')
    memory_list_parser.add_argument('--limit', type=int, default=10, help='显示数量限制')
    memory_list_parser.add_argument('--recent', action='store_true', help='仅显示最近的记忆')
    memory_list_parser.add_argument('--tags', help='按标签过滤(逗号分隔)')

    # memory add 子命令 - 添加记忆
    memory_add_parser = pateoas_memory_subparsers.add_parser('add', help='添加记忆到系统')
    memory_add_parser.add_argument('content', help='记忆内容(必需)')
    memory_add_parser.add_argument('--category', choices=['context', 'decision', 'pattern', 'issue', 'learning'], default='context', help='记忆类别')
    memory_add_parser.add_argument('--tags', help='记忆标签(逗号分隔)')
    memory_add_parser.add_argument('--importance', type=float, default=0.5, help='重要性评分(0-1)')

    # memory find 子命令 - 基础搜索 (统一search和recall的简单版本)
    memory_find_parser = pateoas_memory_subparsers.add_parser('find', help='基础记忆搜索')
    memory_find_parser.add_argument('query', help='搜索关键词')
    memory_find_parser.add_argument('--limit', type=int, default=5, help='结果数量限制')
    memory_find_parser.add_argument('--category', choices=['context', 'decision', 'pattern', 'issue', 'learning'], help='限制搜索类别')
    
    # memory recall 子命令 - 智能召回 (中级功能)
    memory_recall_parser = pateoas_memory_subparsers.add_parser('recall', help='智能记忆召回')
    memory_recall_parser.add_argument('query', help='召回查询')
    memory_recall_parser.add_argument('--context', help='当前上下文信息')
    memory_recall_parser.add_argument('--limit', type=int, default=10, help='最大返回数量')
    memory_recall_parser.add_argument('--min-relevance', type=float, default=0.3, help='最低相关性阈值')
    
    # memory smart-recall 子命令 - 高级智能召回 (高级功能，替换intelligent-recall)
    memory_smart_recall_parser = pateoas_memory_subparsers.add_parser('smart-recall', help='高级智能记忆召回')
    memory_smart_recall_parser.add_argument('query', help='智能召回查询')
    memory_smart_recall_parser.add_argument('--context', help='当前上下文信息')
    memory_smart_recall_parser.add_argument('--limit', type=int, default=10, help='最大返回数量')
    memory_smart_recall_parser.add_argument('--include-patterns', action='store_true', help='包含模式分析')
    memory_smart_recall_parser.add_argument('--priority-recent', action='store_true', help='优先显示最近记忆')
    memory_smart_recall_parser.add_argument('--detailed', action='store_true', help='显示详细分析结果')

    # memory clean 子命令 - 清理记忆
    memory_clean_parser = pateoas_memory_subparsers.add_parser('clean', help='清理记忆')
    memory_clean_parser.add_argument('--days', type=int, default=30, help='清理N天前的记忆')
    memory_clean_parser.add_argument('--category', choices=['context', 'decision', 'pattern', 'issue', 'learning'], help='仅清理指定类别')
    memory_clean_parser.add_argument('--confirm', action='store_true', help='跳过确认提示')
    memory_clean_parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际删除')
    
    # pateoas analyze 命令 (增强版)
    pateoas_analyze_parser = pateoas_subparsers.add_parser('analyze', help='增强任务分析')
    pateoas_analyze_parser.add_argument('task', help='任务描述')
    pateoas_analyze_parser.add_argument('--team-size', type=int, default=5, help='团队规模')
    pateoas_analyze_parser.add_argument('--urgency', choices=['low', 'normal', 'high', 'emergency'], default='normal', help='紧急程度')
    pateoas_analyze_parser.add_argument('--project-type', help='项目类型')
    pateoas_analyze_parser.add_argument('--detailed', action='store_true', help='显示详细分析结果')
    pateoas_analyze_parser.add_argument('--save-analysis', action='store_true', help='保存分析结果到文件')
    
    # pateoas gates 命令
    pateoas_gates_parser = pateoas_subparsers.add_parser('gates', help='智能决策门管理')
    pateoas_gates_subparsers = pateoas_gates_parser.add_subparsers(dest='gates_action', help='决策门操作')
    
    # gates evaluate 子命令
    gates_evaluate_parser = pateoas_gates_subparsers.add_parser('evaluate', help='评估决策门')
    gates_evaluate_parser.add_argument('--gate-id', help='特定决策门ID (DG1, DG2)')
    gates_evaluate_parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    # gates list 子命令
    gates_list_parser = pateoas_gates_subparsers.add_parser('list', help='列出可用决策门')
    
    # gates history 子命令
    gates_history_parser = pateoas_gates_subparsers.add_parser('history', help='查看评估历史')
    gates_history_parser.add_argument('--gate-id', help='特定决策门的历史')
    gates_history_parser.add_argument('--limit', type=int, default=10, help='历史记录数量')
    
    # pateoas optimize 命令
    pateoas_optimize_parser = pateoas_subparsers.add_parser('optimize', help='工作流优化建议')
    pateoas_optimize_parser.add_argument('--analyze-workflow', action='store_true', help='分析当前工作流')
    pateoas_optimize_parser.add_argument('--suggest-improvements', action='store_true', help='建议改进措施')
    pateoas_optimize_parser.add_argument('--performance-focus', action='store_true', help='专注性能优化')
    
    # pateoas test 命令
    pateoas_test_parser = pateoas_subparsers.add_parser('test', help='系统测试和诊断')
    pateoas_test_parser.add_argument('--all-components', action='store_true', help='测试所有组件')
    pateoas_test_parser.add_argument('--component', choices=['memory', 'gates', 'flow', 'engine'], help='测试特定组件')
    pateoas_test_parser.add_argument('--quick', action='store_true', help='快速测试')
    
    # pateoas diagnose 命令
    pateoas_diagnose_parser = pateoas_subparsers.add_parser('diagnose', help='系统诊断')
    pateoas_diagnose_parser.add_argument('--generate-report', action='store_true', help='生成诊断报告')
    pateoas_diagnose_parser.add_argument('--auto-fix', action='store_true', help='自动修复问题')
    
    # pateoas config 命令
    pateoas_config_parser = pateoas_subparsers.add_parser('config', help='PATEOAS配置管理')
    pateoas_config_subparsers = pateoas_config_parser.add_subparsers(dest='config_action', help='配置操作')
    
    # config show 子命令
    config_show_parser = pateoas_config_subparsers.add_parser('show', help='显示当前配置')
    config_show_parser.add_argument('--key', help='显示特定配置项')
    
    # config set 子命令
    config_set_parser = pateoas_config_subparsers.add_parser('set', help='设置配置项')
    config_set_parser.add_argument('key', help='配置键')
    config_set_parser.add_argument('value', help='配置值')
    
    # config reset 子命令
    config_reset_parser = pateoas_config_subparsers.add_parser('reset', help='重置配置')
    config_reset_parser.add_argument('--confirm', action='store_true', help='跳过确认提示')
    
    args = parser.parse_args()
    
    cli = EnhancedAceFlowCLI()
    
    if args.command == 'init':
        cli.init_project(args.mode, not args.no_pateoas)
    elif args.command == 'status':
        cli.status(args.format, args.verbose, args.pateoas)
    elif args.command == 'analyze':
        cli.analyze(args.task, args.team_size, args.urgency, args.project_type)
    elif args.command == 'start':
        cli.start(args.description, args.mode, not args.no_analyze)
    elif args.command == 'progress':
        cli.progress(args.stage, args.percentage)
    elif args.command == 'complete':
        cli.complete(args.stage)
    elif args.command == 'assist':
        cli.smart_assist(args.input)
    elif args.command == 'pateoas':
        cli.handle_pateoas_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()