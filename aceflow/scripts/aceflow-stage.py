#!/usr/bin/env python3
"""
AceFlow v3.0 阶段管理脚本 (Python版本)
AI Agent 工作流阶段控制工具

提供跨平台的项目阶段管理功能。
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

# 脚本信息
SCRIPT_NAME = "aceflow-stage.py"
VERSION = "3.0.0"

# 颜色定义 (ANSI色彩代码)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class Logger:
    """日志工具类"""
    
    @staticmethod
    def info(message: str):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
    
    @staticmethod
    def success(message: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    @staticmethod
    def header():
        print(f"""{Colors.PURPLE}
╔══════════════════════════════════════╗
║       AceFlow v3.0 阶段管理          ║
║      AI Agent 工作流控制工具         ║
╚══════════════════════════════════════╝{Colors.NC}""")

class AceFlowStage:
    """AceFlow 阶段管理类"""
    
    def __init__(self, project_dir: str = "."):
        self.logger = Logger()
        self.project_dir = Path(project_dir).resolve()
        self.aceflow_result_dir = self.project_dir / "aceflow_result"
        self.current_state_file = self.aceflow_result_dir / "current_state.json"
        self.stage_progress_file = self.aceflow_result_dir / "stage_progress.json"

    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
AceFlow v3.0 阶段管理脚本 (Python版本)

用法: {SCRIPT_NAME} <command> [选项]

命令:
  status                    显示当前阶段状态
  list                     列出所有可用阶段
  next                     推进到下一阶段
  prev                     回退到上一阶段
  goto STAGE               跳转到指定阶段
  reset STAGE              重置到指定阶段 (清除后续进度)
  complete STAGE           标记指定阶段为完成
  rollback STAGE           回滚到指定阶段 (保留记录)

选项:
  -d, --directory DIR      指定项目目录 (默认: 当前目录)
  -f, --force              强制执行操作，跳过确认
  -v, --verbose            显示详细信息
  -h, --help               显示此帮助信息
  --version                显示版本信息

示例:
  {SCRIPT_NAME} status
  {SCRIPT_NAME} next --verbose
  {SCRIPT_NAME} goto s3_testcases
  {SCRIPT_NAME} reset s2_tasks_group --force
"""
        print(help_text)

    def load_current_state(self) -> Optional[Dict]:
        """加载当前项目状态"""
        if not self.current_state_file.exists():
            self.logger.error(f"项目状态文件不存在: {self.current_state_file}")
            self.logger.info("请确保在AceFlow项目目录中运行此命令")
            return None
        
        try:
            with open(self.current_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"项目状态文件格式错误: {e}")
            return None

    def save_current_state(self, state: Dict):
        """保存当前项目状态"""
        state['project']['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        with open(self.current_state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_stage_progress(self) -> Optional[Dict]:
        """加载阶段进度信息"""
        if not self.stage_progress_file.exists():
            self.logger.error(f"阶段进度文件不存在: {self.stage_progress_file}")
            return None
        
        try:
            with open(self.stage_progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"阶段进度文件格式错误: {e}")
            return None

    def save_stage_progress(self, progress: Dict):
        """保存阶段进度信息"""
        with open(self.stage_progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def get_stage_order(self, mode: str) -> List[str]:
        """获取阶段顺序"""
        stage_orders = {
            "minimal": ["analysis", "planning", "implementation", "validation"],
            "standard": ["user_stories", "tasks_planning", "test_design", 
                        "implementation", "testing", "review"],
            "complete": ["s1_user_story", "s2_tasks_group", "s3_testcases", 
                        "s4_implementation", "s5_test_report", "s6_codereview", 
                        "s7_demo_script", "s8_summary_report"],
            "smart": ["analysis", "planning", "implementation", "validation"]
        }
        return stage_orders.get(mode, [])

    def get_stage_display_name(self, stage: str) -> str:
        """获取阶段显示名称"""
        display_names = {
            # Minimal/Smart 模式
            "analysis": "需求分析",
            "planning": "规划设计",
            "implementation": "功能实现",
            "validation": "验证测试",
            
            # Standard 模式
            "user_stories": "用户故事",
            "tasks_planning": "任务规划",
            "test_design": "测试设计",
            "testing": "测试执行",
            "review": "代码评审",
            
            # Complete 模式
            "s1_user_story": "S1-用户故事分析",
            "s2_tasks_group": "S2-任务分组规划",
            "s3_testcases": "S3-测试用例设计",
            "s4_implementation": "S4-功能实现",
            "s5_test_report": "S5-测试报告",
            "s6_codereview": "S6-代码评审",
            "s7_demo_script": "S7-演示脚本",
            "s8_summary_report": "S8-项目总结"
        }
        return display_names.get(stage, stage)

    def show_status(self, verbose: bool = False):
        """显示当前阶段状态"""
        state = self.load_current_state()
        if not state:
            return False
        
        progress = self.load_stage_progress()
        if not progress:
            return False
        
        project = state['project']
        flow = state['flow']
        
        self.logger.header()
        print(f"{Colors.CYAN}项目状态概览{Colors.NC}")
        print("─" * 40)
        print(f"📋 项目名称: {project['name']}")
        print(f"🔄 流程模式: {project['mode']}")
        print(f"📊 当前阶段: {Colors.BLUE}{self.get_stage_display_name(flow['current_stage'])}{Colors.NC}")
        print(f"📈 完成进度: {flow['progress_percentage']}%")
        
        if flow['next_stage']:
            print(f"➡️  下一阶段: {self.get_stage_display_name(flow['next_stage'])}")
        
        print(f"🕒 最后更新: {project['last_updated']}")
        
        if verbose:
            print(f"\n{Colors.CYAN}详细阶段信息{Colors.NC}")
            print("─" * 40)
            
            stage_order = self.get_stage_order(project['mode'])
            for stage in stage_order:
                if stage in progress['stages']:
                    stage_info = progress['stages'][stage]
                    status = stage_info['status']
                    stage_progress = stage_info.get('progress', 0)
                    
                    # 状态图标
                    status_icons = {
                        'pending': '⏸️',
                        'in_progress': '🔄',
                        'completed': '✅',
                        'failed': '❌'
                    }
                    icon = status_icons.get(status, '❓')
                    
                    # 状态颜色
                    status_colors = {
                        'pending': Colors.YELLOW,
                        'in_progress': Colors.BLUE,
                        'completed': Colors.GREEN,
                        'failed': Colors.RED
                    }
                    color = status_colors.get(status, Colors.NC)
                    
                    print(f"{icon} {self.get_stage_display_name(stage):<20} "
                          f"{color}{status}{Colors.NC} ({stage_progress}%)")
        
        print("")
        return True

    def list_stages(self):
        """列出所有可用阶段"""
        state = self.load_current_state()
        if not state:
            return False
        
        mode = state['project']['mode']
        stage_order = self.get_stage_order(mode)
        
        print(f"{Colors.CYAN}{mode.upper()} 模式阶段列表{Colors.NC}")
        print("─" * 40)
        
        for i, stage in enumerate(stage_order, 1):
            print(f"{i:2d}. {stage:<20} - {self.get_stage_display_name(stage)}")
        
        print("")
        return True

    def next_stage(self, force: bool = False, verbose: bool = False):
        """推进到下一阶段"""
        state = self.load_current_state()
        if not state:
            return False
        
        progress = self.load_stage_progress()
        if not progress:
            return False
        
        current_stage = state['flow']['current_stage']
        next_stage = state['flow']['next_stage']
        
        if not next_stage:
            self.logger.info("已经是最后一个阶段")
            return True
        
        if current_stage != "initialized":
            # 检查当前阶段是否完成
            if current_stage in progress['stages']:
                current_status = progress['stages'][current_stage]['status']
                if current_status != 'completed' and not force:
                    self.logger.warning(f"当前阶段 '{self.get_stage_display_name(current_stage)}' 未完成")
                    response = input("是否强制推进到下一阶段? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        self.logger.info("操作已取消")
                        return False
        
        # 更新状态
        old_stage = current_stage
        state['flow']['current_stage'] = next_stage
        
        # 计算下一个阶段
        mode = state['project']['mode']
        stage_order = self.get_stage_order(mode)
        
        try:
            current_index = stage_order.index(next_stage)
            if current_index + 1 < len(stage_order):
                state['flow']['next_stage'] = stage_order[current_index + 1]
            else:
                state['flow']['next_stage'] = None
        except ValueError:
            state['flow']['next_stage'] = None
        
        # 更新完成的阶段列表
        if old_stage != "initialized" and old_stage not in state['flow']['completed_stages']:
            state['flow']['completed_stages'].append(old_stage)
        
        # 计算进度百分比
        completed_count = len(state['flow']['completed_stages'])
        total_stages = len(stage_order)
        state['flow']['progress_percentage'] = int((completed_count / total_stages) * 100)
        
        # 更新阶段进度
        if next_stage in progress['stages']:
            progress['stages'][next_stage]['status'] = 'in_progress'
            progress['stages'][next_stage]['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # 保存状态
        self.save_current_state(state)
        self.save_stage_progress(progress)
        
        self.logger.success(f"已推进到阶段: {self.get_stage_display_name(next_stage)}")
        
        if verbose:
            self.show_status(verbose=True)
        
        return True

    def goto_stage(self, target_stage: str, force: bool = False):
        """跳转到指定阶段"""
        state = self.load_current_state()
        if not state:
            return False
        
        progress = self.load_stage_progress()
        if not progress:
            return False
        
        mode = state['project']['mode']
        stage_order = self.get_stage_order(mode)
        
        if target_stage not in stage_order:
            self.logger.error(f"无效的阶段名称: {target_stage}")
            self.logger.info(f"可用阶段: {', '.join(stage_order)}")
            return False
        
        current_stage = state['flow']['current_stage']
        
        if current_stage == target_stage:
            self.logger.info(f"已经在目标阶段: {self.get_stage_display_name(target_stage)}")
            return True
        
        if not force:
            response = input(f"确认跳转到阶段 '{self.get_stage_display_name(target_stage)}'? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                self.logger.info("操作已取消")
                return False
        
        # 更新状态
        state['flow']['current_stage'] = target_stage
        
        # 计算下一个阶段
        try:
            current_index = stage_order.index(target_stage)
            if current_index + 1 < len(stage_order):
                state['flow']['next_stage'] = stage_order[current_index + 1]
            else:
                state['flow']['next_stage'] = None
        except ValueError:
            state['flow']['next_stage'] = None
        
        # 更新阶段进度
        if target_stage in progress['stages']:
            progress['stages'][target_stage]['status'] = 'in_progress'
            progress['stages'][target_stage]['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # 保存状态
        self.save_current_state(state)
        self.save_stage_progress(progress)
        
        self.logger.success(f"已跳转到阶段: {self.get_stage_display_name(target_stage)}")
        return True

    def complete_stage(self, stage: str, force: bool = False):
        """标记指定阶段为完成"""
        state = self.load_current_state()
        if not state:
            return False
        
        progress = self.load_stage_progress()
        if not progress:
            return False
        
        if stage not in progress['stages']:
            self.logger.error(f"阶段不存在: {stage}")
            return False
        
        if not force:
            response = input(f"确认标记阶段 '{self.get_stage_display_name(stage)}' 为完成? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                self.logger.info("操作已取消")
                return False
        
        # 更新阶段状态
        progress['stages'][stage]['status'] = 'completed'
        progress['stages'][stage]['progress'] = 100
        progress['stages'][stage]['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # 更新完成阶段列表
        if stage not in state['flow']['completed_stages']:
            state['flow']['completed_stages'].append(stage)
        
        # 重新计算进度
        mode = state['project']['mode']
        stage_order = self.get_stage_order(mode)
        completed_count = len(state['flow']['completed_stages'])
        total_stages = len(stage_order)
        state['flow']['progress_percentage'] = int((completed_count / total_stages) * 100)
        
        # 保存状态
        self.save_current_state(state)
        self.save_stage_progress(progress)
        
        self.logger.success(f"阶段 '{self.get_stage_display_name(stage)}' 已标记为完成")
        return True

    def reset_stage(self, target_stage: str, force: bool = False):
        """重置到指定阶段 (清除后续进度)"""
        state = self.load_current_state()
        if not state:
            return False
        
        progress = self.load_stage_progress()
        if not progress:
            return False
        
        mode = state['project']['mode']
        stage_order = self.get_stage_order(mode)
        
        if target_stage not in stage_order:
            self.logger.error(f"无效的阶段名称: {target_stage}")
            return False
        
        if not force:
            self.logger.warning("重置操作将清除目标阶段之后的所有进度")
            response = input(f"确认重置到阶段 '{self.get_stage_display_name(target_stage)}'? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                self.logger.info("操作已取消")
                return False
        
        target_index = stage_order.index(target_stage)
        
        # 重置后续阶段状态
        for i in range(target_index + 1, len(stage_order)):
            stage = stage_order[i]
            if stage in progress['stages']:
                progress['stages'][stage]['status'] = 'pending'
                progress['stages'][stage]['progress'] = 0
                if 'last_updated' in progress['stages'][stage]:
                    del progress['stages'][stage]['last_updated']
        
        # 更新当前状态
        state['flow']['current_stage'] = target_stage
        state['flow']['next_stage'] = stage_order[target_index + 1] if target_index + 1 < len(stage_order) else None
        state['flow']['completed_stages'] = [s for s in state['flow']['completed_stages'] 
                                           if stage_order.index(s) < target_index]
        
        # 重新计算进度
        completed_count = len(state['flow']['completed_stages'])
        total_stages = len(stage_order)
        state['flow']['progress_percentage'] = int((completed_count / total_stages) * 100)
        
        # 保存状态
        self.save_current_state(state)
        self.save_stage_progress(progress)
        
        self.logger.success(f"已重置到阶段: {self.get_stage_display_name(target_stage)}")
        return True

    def run(self):
        """主运行函数"""
        parser = argparse.ArgumentParser(
            description="AceFlow v3.0 阶段管理脚本 (Python版本)",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument('command', nargs='?',
                          help='要执行的命令')
        parser.add_argument('stage', nargs='?',
                          help='目标阶段名称 (对于 goto, reset, complete 命令)')
        parser.add_argument('-d', '--directory', 
                          default='.',
                          help='指定项目目录 (默认: 当前目录)')
        parser.add_argument('-f', '--force', 
                          action='store_true',
                          help='强制执行操作，跳过确认')
        parser.add_argument('-v', '--verbose', 
                          action='store_true',
                          help='显示详细信息')
        parser.add_argument('--version', 
                          action='version',
                          version=f'AceFlow Stage Manager v{VERSION}')
        
        args = parser.parse_args()
        
        if not args.command:
            self.show_help()
            return 1
        
        # 设置项目目录
        self.__init__(args.directory)
        
        # 检查项目目录
        if not self.aceflow_result_dir.exists():
            self.logger.error("这不是一个有效的AceFlow项目目录")
            self.logger.info("请在包含 aceflow_result/ 目录的项目中运行此命令")
            return 1
        
        # 执行命令
        try:
            if args.command == 'status':
                return 0 if self.show_status(args.verbose) else 1
            
            elif args.command == 'list':
                return 0 if self.list_stages() else 1
            
            elif args.command == 'next':
                return 0 if self.next_stage(args.force, args.verbose) else 1
            
            elif args.command == 'goto':
                if not args.stage:
                    self.logger.error("goto 命令需要指定目标阶段")
                    return 1
                return 0 if self.goto_stage(args.stage, args.force) else 1
            
            elif args.command == 'complete':
                if not args.stage:
                    self.logger.error("complete 命令需要指定目标阶段")
                    return 1
                return 0 if self.complete_stage(args.stage, args.force) else 1
            
            elif args.command == 'reset':
                if not args.stage:
                    self.logger.error("reset 命令需要指定目标阶段")
                    return 1
                return 0 if self.reset_stage(args.stage, args.force) else 1
            
            else:
                self.logger.error(f"未知命令: {args.command}")
                self.show_help()
                return 1
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}操作被用户中断{Colors.NC}")
            return 1
        except Exception as e:
            self.logger.error(f"发生未预期的错误: {e}")
            return 1

def main():
    """主函数"""
    app = AceFlowStage()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())