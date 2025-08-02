#!/usr/bin/env python3
"""
AceFlow v3.0 增强项目初始化脚本
AI Agent 增强层初始化工具 - 用户体验优化版

解决目录初始化和用户体验问题
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import tempfile

# 导入平台兼容性模块
try:
    from utils.platform_compatibility import (
        PlatformUtils, SafeFileOperations, EnhancedErrorHandler
    )
    COMPATIBILITY_AVAILABLE = True
except ImportError:
    COMPATIBILITY_AVAILABLE = False

# 脚本信息
SCRIPT_NAME = "aceflow-init.py"
VERSION = "3.0.1"
ACEFLOW_HOME = os.environ.get('ACEFLOW_HOME', 
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 颜色定义 (ANSI色彩代码)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

class EnhancedLogger:
    """增强日志工具类"""
    
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
    def important(message: str):
        print(f"{Colors.BOLD}{Colors.CYAN}[IMPORTANT]{Colors.NC} {message}")
    
    @staticmethod
    def step(step_num: int, total_steps: int, message: str):
        print(f"{Colors.PURPLE}[Step {step_num}/{total_steps}]{Colors.NC} {message}")
    
    @staticmethod
    def header():
        print(f"""{Colors.PURPLE}
╔══════════════════════════════════════╗
║      AceFlow v3.0 Enhanced 初始化     ║
║       AI Agent 增强层配置工具        ║
╚══════════════════════════════════════╝{Colors.NC}""")

class DirectoryHandler:
    """目录处理器 - 解决用户目录混淆问题"""
    
    @staticmethod
    def get_target_directory(args_directory: str) -> Path:
        """智能确定目标目录"""
        current_dir = Path.cwd()
        
        if args_directory == ".":
            # 用户想在当前目录初始化
            target_dir = current_dir
        else:
            # 用户指定了目录
            target_dir = Path(args_directory)
            if not target_dir.is_absolute():
                # 相对路径，基于当前工作目录
                target_dir = current_dir / target_dir
        
        return target_dir.resolve()
    
    @staticmethod
    def validate_target_directory(target_dir: Path, force: bool = False) -> tuple[bool, str]:
        """验证目标目录的有效性"""
        
        # 检查是否为AceFlow源码目录
        if DirectoryHandler.is_aceflow_source_directory(target_dir):
            return False, f"⚠️ 检测到这是AceFlow源码目录，不建议在此初始化项目。\n   建议在其他目录初始化您的项目。"
        
        # 检查是否已经是AceFlow项目
        if (target_dir / ".clinerules").exists() and not force:
            return False, f"❌ 目录已包含AceFlow配置。\n   使用 --force 强制覆盖，或选择其他目录。"
        
        # 检查目录权限
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            # 测试写入权限
            test_file = target_dir / ".aceflow_test"
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            return False, f"❌ 目录权限不足: {target_dir}\n   请选择有写入权限的目录。"
        except Exception as e:
            return False, f"❌ 目录访问失败: {e}"
        
        return True, ""
    
    @staticmethod
    def is_aceflow_source_directory(path: Path) -> bool:
        """检查是否为AceFlow源码目录"""
        # 检查典型的AceFlow源码结构
        indicators = [
            "aceflow-spec.md",
            "scripts/aceflow-init.py",
            "pateoas/__init__.py",
            "templates/complete/template.yaml"
        ]
        
        for indicator in indicators:
            if (path / indicator).exists():
                return True
        
        return False
    
    @staticmethod
    def show_directory_info(target_dir: Path, current_dir: Path):
        """显示目录信息，帮助用户理解"""
        print(f"\n{Colors.CYAN}📁 目录信息:{Colors.NC}")
        print(f"   当前工作目录: {current_dir}")
        print(f"   初始化目录:   {target_dir}")
        
        if target_dir == current_dir:
            print(f"   {Colors.GREEN}✓{Colors.NC} 将在当前目录初始化AceFlow项目")
        else:
            print(f"   {Colors.BLUE}ℹ{Colors.NC} 将在指定目录初始化AceFlow项目")
        
        # 显示目录内容概况
        if target_dir.exists():
            try:
                contents = list(target_dir.iterdir())
                if contents:
                    print(f"   目录内容: {len(contents)} 个文件/文件夹")
                    if len(contents) <= 5:
                        for item in contents:
                            print(f"     - {item.name}")
                    else:
                        print(f"     - {contents[0].name}")
                        print(f"     - {contents[1].name}")
                        print(f"     - ... (还有 {len(contents)-2} 个项目)")
                else:
                    print(f"   {Colors.GREEN}✓{Colors.NC} 目录为空，适合初始化")
            except Exception:
                pass

class EnhancedAceFlowInit:
    """增强版AceFlow初始化器"""
    
    def __init__(self):
        self.logger = EnhancedLogger()
        self.step_counter = 0
        self.total_steps = 6
    
    def next_step(self, message: str):
        """显示进度步骤"""
        self.step_counter += 1
        self.logger.step(self.step_counter, self.total_steps, message)
    
    def check_environment(self) -> bool:
        """检查环境依赖"""
        self.next_step("检查环境依赖...")
        
        issues = []
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            issues.append(f"Python版本过低: {sys.version}. 需要Python 3.7+")
        
        # 检查必要的模块
        try:
            import json, shutil, pathlib
            self.logger.success("✓ Python标准库检查通过")
        except ImportError as e:
            issues.append(f"Python标准库模块缺失: {e}")
        
        # 检查AceFlow HOME
        aceflow_home_path = Path(ACEFLOW_HOME)
        if not aceflow_home_path.exists():
            issues.append(f"AceFlow安装目录不存在: {ACEFLOW_HOME}")
        else:
            self.logger.success(f"✓ AceFlow安装目录: {ACEFLOW_HOME}")
        
        # 检查模板目录
        templates_dir = aceflow_home_path / "templates"
        if not templates_dir.exists():
            issues.append(f"模板目录不存在: {templates_dir}")
        else:
            self.logger.success("✓ 模板目录可用")
        
        # 报告问题
        if issues:
            self.logger.error("环境检查失败:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        self.logger.success("环境检查完成")
        return True
    
    def get_user_inputs(self, args) -> tuple[str, str, Path]:
        """获取用户输入，支持交互式和智能模式"""
        self.next_step("收集项目信息...")
        
        # 确定目标目录
        target_dir = DirectoryHandler.get_target_directory(args.directory)
        current_dir = Path.cwd()
        
        # 显示目录信息
        DirectoryHandler.show_directory_info(target_dir, current_dir)
        
        # 验证目录
        valid, error_msg = DirectoryHandler.validate_target_directory(target_dir, args.force)
        if not valid:
            self.logger.error(error_msg)
            
            # 提供解决建议
            if "AceFlow源码目录" in error_msg:
                print(f"\n{Colors.CYAN}💡 建议:{Colors.NC}")
                print("   1. 创建新的项目目录: mkdir my-project && cd my-project")
                print("   2. 然后运行: aceflow-init.py")
                print("   3. 或指定目录: aceflow-init.py --directory /path/to/my-project")
            
            sys.exit(1)
        
        # 项目名称
        project_name = args.project
        if not project_name and (args.interactive or args.mode == 'smart'):
            while not project_name:
                project_name = input(f"\n{Colors.CYAN}请输入项目名称:{Colors.NC} ").strip()
                if not project_name:
                    print("项目名称不能为空，请重新输入。")
        
        if not project_name:
            project_name = f"AceFlow项目-{datetime.now().strftime('%Y%m%d_%H%M')}"
            self.logger.info(f"使用默认项目名称: {project_name}")
        
        # 模式选择
        mode = args.mode
        if not mode and (args.interactive or args.mode == 'smart'):
            mode = self.interactive_mode_selection()
        
        if not mode:
            mode = "standard"  # 默认模式
            self.logger.info(f"使用默认模式: {mode}")
            
        return mode, project_name, target_dir
    
    def interactive_mode_selection(self) -> str:
        """交互式模式选择"""
        print(f"\n{Colors.CYAN}请选择AceFlow工作模式:{Colors.NC}")
        print(f"  {Colors.GREEN}1) minimal{Colors.NC}  - 最简流程 (适合: 快速原型、个人项目)")
        print(f"  {Colors.BLUE}2) standard{Colors.NC} - 标准流程 (适合: 团队协作、中型项目)")
        print(f"  {Colors.PURPLE}3) complete{Colors.NC} - 完整流程 (适合: 企业级、大型项目)")
        print(f"  {Colors.YELLOW}4) smart{Colors.NC}    - 智能流程 (适合: 复杂需求、自适应)")
        
        mode_map = {"1": "minimal", "2": "standard", "3": "complete", "4": "smart"}
        
        while True:
            choice = input(f"\n请选择 (1-4) [默认: 2]: ").strip()
            if not choice:
                return "standard"
            if choice in mode_map:
                selected_mode = mode_map[choice]
                if selected_mode == "smart":
                    # Smart模式需要额外确认
                    print(f"\n{Colors.YELLOW}Smart模式说明:{Colors.NC}")
                    print("- AI将通过智能访谈分析您的项目需求")
                    print("- 根据复杂度自动选择最适合的流程")
                    print("- 提供个性化的开发建议")
                    confirm = input("确认使用Smart模式? (y/N): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return self.ai_interview()
                    else:
                        continue
                return selected_mode
            else:
                print("无效选择，请输入 1-4 之间的数字。")
    
    def ai_interview(self) -> str:
        """AI智能访谈模式"""
        self.logger.info("🤖 启动AI智能访谈...")
        
        questions = [
            ("项目规模", "预期的团队规模? (1=个人, 2=小团队2-5人, 3=中型团队6-15人, 4=大型团队15+人)"),
            ("项目复杂度", "项目复杂度? (1=简单, 2=中等, 3=复杂, 4=非常复杂)"),
            ("时间要求", "时间要求? (1=快速原型, 2=正常开发, 3=充分测试, 4=严格质控)"),
            ("质量要求", "质量要求? (1=基本可用, 2=生产就绪, 3=企业级, 4=关键任务)")
        ]
        
        scores = {"minimal": 0, "standard": 0, "complete": 0}
        
        print(f"\n{Colors.CYAN}🎯 AI智能访谈 - 为您推荐最适合的工作模式{Colors.NC}")
        
        for category, question in questions:
            while True:
                try:
                    answer = input(f"\n{question} [1-4]: ").strip()
                    score = int(answer)
                    if 1 <= score <= 4:
                        # 评分逻辑
                        if score == 1:
                            scores["minimal"] += 3
                            scores["standard"] += 1
                        elif score == 2:
                            scores["minimal"] += 1
                            scores["standard"] += 3
                            scores["complete"] += 1
                        elif score == 3:
                            scores["standard"] += 2
                            scores["complete"] += 3
                        else:  # score == 4
                            scores["complete"] += 4
                        break
                    else:
                        print("请输入 1-4 之间的数字。")
                except ValueError:
                    print("请输入有效的数字。")
        
        # 确定推荐模式
        recommended_mode = max(scores, key=scores.get)
        
        print(f"\n{Colors.PURPLE}🎯 AI分析结果:{Colors.NC}")
        print(f"   推荐模式: {Colors.BOLD}{recommended_mode.upper()}{Colors.NC}")
        
        # 显示推荐理由
        reasons = {
            "minimal": "适合快速原型和简单项目，流程轻量化",
            "standard": "适合标准团队协作，平衡效率与质量",
            "complete": "适合企业级项目，全面质量控制"
        }
        print(f"   推荐理由: {reasons[recommended_mode]}")
        
        # 用户最终确认
        confirm = input(f"\n接受AI推荐的 {recommended_mode} 模式? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            return recommended_mode
        else:
            return self.interactive_mode_selection()
    
    def initialize_project(self, mode: str, project_name: str, target_dir: Path) -> bool:
        """初始化项目"""
        try:
            # 切换到目标目录
            original_cwd = Path.cwd()
            os.chdir(target_dir)
            
            self.next_step(f"初始化 {mode} 模式项目配置...")
            
            # 创建基础结构
            self.create_project_structure(mode, project_name, target_dir)
            
            self.next_step("创建AI Agent集成配置...")
            self.create_ai_agent_config(mode, project_name)
            
            self.next_step("复制项目级工作脚本...")
            self.copy_project_scripts(target_dir)
            
            self.next_step("初始化项目状态管理...")
            self.create_project_state(mode, project_name, target_dir)
            
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
            return True
            
        except Exception as e:
            self.logger.error(f"项目初始化失败: {e}")
            if COMPATIBILITY_AVAILABLE:
                error_report = EnhancedErrorHandler.create_error_report(e, "项目初始化")
                suggestions = EnhancedErrorHandler.get_error_suggestions(e)
                if suggestions:
                    print(f"\n{Colors.CYAN}💡 解决建议:{Colors.NC}")
                    for suggestion in suggestions:
                        print(f"   - {suggestion}")
            return False
    
    def create_project_structure(self, mode: str, project_name: str, target_dir: Path):
        """创建项目基础结构"""
        # 创建必要目录
        directories = [
            "aceflow_result",
            ".aceflow",
        ]
        
        for dir_name in directories:
            dir_path = target_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            self.logger.success(f"✓ 创建目录: {dir_name}")
    
    def create_ai_agent_config(self, mode: str, project_name: str):
        """创建AI Agent配置"""
        # 创建.clinerules文件
        clinerules_content = f"""# AceFlow v3.0 - AI Agent 集成配置
# 项目: {project_name}
# 模式: {mode}
# 初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 工作模式配置
AceFlow模式: {mode}
输出目录: aceflow_result/
配置目录: .aceflow/
项目名称: {project_name}

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

## 工具集成命令
- python aceflow-validate.py: 验证项目状态和合规性
- python aceflow-stage.py: 管理项目阶段和进度
- python aceflow-templates.py: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
        
        if COMPATIBILITY_AVAILABLE:
            success, msg = SafeFileOperations.safe_write_text(Path(".clinerules"), clinerules_content)
            if success:
                self.logger.success("✓ AI Agent配置文件已创建")
            else:
                self.logger.warning(f"配置文件创建警告: {msg}")
        else:
            with open(".clinerules", 'w', encoding='utf-8') as f:
                f.write(clinerules_content)
            self.logger.success("✓ AI Agent配置文件已创建")
    
    def copy_project_scripts(self, target_dir: Path):
        """复制项目级脚本"""
        project_scripts = [
            "aceflow-stage.py",
            "aceflow-validate.py", 
            "aceflow-templates.py"
        ]
        
        script_source_dir = Path(ACEFLOW_HOME) / "scripts"
        copied_count = 0
        
        for script in project_scripts:
            source_path = script_source_dir / script
            target_path = target_dir / script
            
            if source_path.exists():
                if COMPATIBILITY_AVAILABLE:
                    success, msg = SafeFileOperations.safe_copy_file(source_path, target_path)
                    if success:
                        self.logger.success(f"✓ 已复制: {script}")
                        copied_count += 1
                    else:
                        self.logger.warning(f"复制脚本警告: {msg}")
                else:
                    shutil.copy2(source_path, target_path)
                    target_path.chmod(0o755)
                    self.logger.success(f"✓ 已复制: {script}")
                    copied_count += 1
            else:
                self.logger.warning(f"⚠️ 源脚本不存在: {source_path}")
        
        # 创建使用说明
        readme_content = """# AceFlow 项目工具脚本

本项目已配置为AceFlow项目，包含以下管理工具:

## 🛠️ 可用命令

### 📊 项目状态管理
```bash
python aceflow-stage.py status    # 查看当前项目状态
python aceflow-stage.py next      # 推进到下一阶段
python aceflow-stage.py list      # 列出所有阶段
```

### 🔍 项目验证
```bash
python aceflow-validate.py        # 快速验证
python aceflow-validate.py --mode complete --report  # 完整验证
```

### 🛠️ 模板管理
```bash
python aceflow-templates.py list  # 查看可用模板
python aceflow-templates.py info standard  # 查看模式详情
```

## 📁 项目结构

- `aceflow_result/` - 所有AI工作产出
- `.aceflow/` - 流程配置文件
- `.clinerules` - AI Agent工作规则

## 🚀 快速开始

1. 与AI开始对话，AI将自动按照配置的流程工作
2. 使用 `python aceflow-stage.py status` 随时查看进度
3. 所有工作成果将保存在 `aceflow_result/` 目录

享受高效的AI协作开发体验！
"""
        
        readme_path = target_dir / "README_ACEFLOW.md"
        if COMPATIBILITY_AVAILABLE:
            SafeFileOperations.safe_write_text(readme_path, readme_content)
        else:
            readme_path.write_text(readme_content, encoding='utf-8')
        
        self.logger.success(f"✓ 项目脚本安装完成 ({copied_count}/{len(project_scripts)})")
    
    def create_project_state(self, mode: str, project_name: str, target_dir: Path):
        """创建项目状态文件"""
        aceflow_result_dir = target_dir / "aceflow_result"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 主状态文件
        current_state = {
            "project": {
                "name": project_name,
                "mode": mode,
                "directory": str(target_dir),
                "created_at": timestamp,
                "last_updated": timestamp,
                "version": VERSION
            },
            "flow": {
                "current_stage": "initialized",
                "completed_stages": [],
                "next_stage": self._get_first_stage(mode),
                "progress_percentage": 0
            },
            "memory": {
                "enabled": True,
                "last_session": timestamp,
                "context_preserved": True
            },
            "quality": {
                "standards_applied": True,
                "compliance_checked": False,
                "last_validation": None
            }
        }
        
        state_file = aceflow_result_dir / "current_state.json"
        if COMPATIBILITY_AVAILABLE:
            SafeFileOperations.safe_write_text(
                state_file, 
                json.dumps(current_state, ensure_ascii=False, indent=2)
            )
        else:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
        
        self.logger.success("✓ 项目状态文件已创建")
    
    def _get_first_stage(self, mode: str) -> str:
        """获取首个阶段"""
        stage_map = {
            "minimal": "requirements",
            "standard": "user_stories", 
            "complete": "s1_user_story",
            "smart": "analysis"
        }
        return stage_map.get(mode, "analysis")
    
    def show_completion_summary(self, mode: str, project_name: str, target_dir: Path):
        """显示完成摘要"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 AceFlow项目初始化成功！{Colors.NC}")
        
        print(f"\n{Colors.CYAN}📋 项目信息:{Colors.NC}")
        print(f"   名称: {Colors.BOLD}{project_name}{Colors.NC}")
        print(f"   模式: {Colors.BOLD}{mode.upper()}{Colors.NC}")
        print(f"   位置: {Colors.BLUE}{target_dir}{Colors.NC}")
        
        print(f"\n{Colors.CYAN}📁 已创建的文件结构:{Colors.NC}")
        print(f"   📋 .clinerules          - AI Agent工作配置")
        print(f"   📊 aceflow_result/      - 项目输出目录")
        print(f"   ⚙️  .aceflow/           - 流程配置目录")
        print(f"   📖 README_ACEFLOW.md    - 项目使用指南")
        print(f"   🛠️  aceflow-*.py        - 项目管理脚本")
        
        print(f"\n{Colors.CYAN}🚀 下一步操作:{Colors.NC}")
        if target_dir != Path.cwd():
            print(f"   1. 切换到项目目录: {Colors.YELLOW}cd {target_dir}{Colors.NC}")
        print(f"   2. 查看项目状态: {Colors.YELLOW}python aceflow-stage.py status{Colors.NC}")
        print(f"   3. 开始与AI协作开发，AI将自动遵循AceFlow规范")
        
        print(f"\n{Colors.GREEN}✨ 现在您可以享受智能化的AI协作开发体验！{Colors.NC}")
    
    def run(self):
        """主运行函数"""
        parser = argparse.ArgumentParser(
            description="AceFlow v3.0 Enhanced 项目初始化工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  %(prog)s                                    # 在当前目录初始化
  %(prog)s --directory ./my-project          # 在指定目录初始化  
  %(prog)s --mode smart --interactive        # 智能交互模式
  %(prog)s --project "我的项目" --force       # 强制覆盖已有配置

模式说明:
  minimal   - 最简流程，适合快速原型
  standard  - 标准流程，适合团队协作  
  complete  - 完整流程，适合企业项目
  smart     - 智能流程，AI自动推荐
            """
        )
        
        parser.add_argument("-m", "--mode", 
                          choices=["minimal", "standard", "complete", "smart"],
                          help="指定工作流程模式")
        parser.add_argument("-p", "--project", 
                          help="指定项目名称")
        parser.add_argument("-d", "--directory", 
                          default=".",
                          help="指定项目目录 (默认: 当前目录)")
        parser.add_argument("-i", "--interactive", 
                          action="store_true",
                          help="启用交互式配置")
        parser.add_argument("-f", "--force", 
                          action="store_true",
                          help="强制覆盖已存在的配置")
        parser.add_argument("-v", "--version", 
                          action="version",
                          version=f"AceFlow Enhanced Init v{VERSION}")
        
        args = parser.parse_args()
        
        try:
            # 显示标题
            self.logger.header()
            
            # 环境检查
            if not self.check_environment():
                return 1
            
            # 获取用户输入
            mode, project_name, target_dir = self.get_user_inputs(args)
            
            # 初始化项目
            if self.initialize_project(mode, project_name, target_dir):
                # 显示完成摘要
                self.show_completion_summary(mode, project_name, target_dir)
                return 0
            else:
                self.logger.error("项目初始化失败")
                return 1
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}操作被用户中断{Colors.NC}")
            return 1
        except Exception as e:
            self.logger.error(f"发生未预期的错误: {e}")
            if COMPATIBILITY_AVAILABLE:
                suggestions = EnhancedErrorHandler.get_error_suggestions(e)
                if suggestions:
                    print(f"\n{Colors.CYAN}💡 建议:{Colors.NC}")
                    for suggestion in suggestions:
                        print(f"   - {suggestion}")
            return 1

def main():
    """主函数"""
    app = EnhancedAceFlowInit()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())