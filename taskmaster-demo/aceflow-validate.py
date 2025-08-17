#!/usr/bin/env python3
"""
AceFlow v3.0 项目验证脚本
AI Agent 增强层合规性检查工具
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class Colors:
    """ANSI颜色代码"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


class ValidationLogger:
    """验证日志记录器"""
    
    def __init__(self, silent_mode: bool = False):
        self.silent_mode = silent_mode
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
        self.warning_checks = 0
    
    def info(self, message: str):
        if not self.silent_mode:
            print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
    
    def success(self, message: str):
        if not self.silent_mode:
            print(f"{Colors.GREEN}[PASS]{Colors.NC} {message}")
        self.passed_checks += 1
        self.total_checks += 1
    
    def warning(self, message: str):
        if not self.silent_mode:
            print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")
        self.warning_checks += 1
        self.total_checks += 1
    
    def error(self, message: str):
        if not self.silent_mode:
            print(f"{Colors.RED}[FAIL]{Colors.NC} {message}")
        self.failed_checks += 1
        self.total_checks += 1
    
    def header(self):
        if not self.silent_mode:
            header_text = f"""{Colors.PURPLE}
╔══════════════════════════════════════╗
║       AceFlow v3.0 项目验证          ║
║      AI Agent 增强层合规检查         ║
╚══════════════════════════════════════╝{Colors.NC}"""
            print(header_text)


class AceFlowValidator:
    """AceFlow项目验证器"""
    
    VERSION = "3.0.0"
    
    def __init__(self, project_dir: str, check_mode: str = "standard", 
                 auto_fix: bool = False, silent_mode: bool = False):
        self.project_dir = Path(project_dir)
        self.check_mode = check_mode
        self.auto_fix = auto_fix
        self.logger = ValidationLogger(silent_mode)
        
        # 获取AceFlow根目录
        script_path = Path(__file__).resolve()
        self.aceflow_home = os.environ.get('ACEFLOW_HOME', str(script_path.parent.parent))
    
    def check_basic_structure(self) -> bool:
        """检查项目基础结构"""
        self.logger.info("检查项目基础结构...")
        
        structure_ok = True
        
        # 检查.clinerules文件
        clinerules_path = self.project_dir / ".clinerules"
        if clinerules_path.exists():
            self.logger.success("AI Agent配置文件 (.clinerules) 存在")
            
            # 检查内容完整性
            try:
                content = clinerules_path.read_text(encoding='utf-8')
                if "AceFlow" in content and "aceflow_result" in content:
                    self.logger.success(".clinerules 包含必要的AceFlow配置")
                else:
                    self.logger.error(".clinerules 缺少必要的AceFlow配置")
                    structure_ok = False
            except Exception as e:
                self.logger.error(f".clinerules 文件读取失败: {e}")
                structure_ok = False
        else:
            self.logger.error("AI Agent配置文件 (.clinerules) 不存在")
            structure_ok = False
        
        # 检查aceflow_result目录
        aceflow_result_path = self.project_dir / "aceflow_result"
        if aceflow_result_path.exists() and aceflow_result_path.is_dir():
            self.logger.success("项目输出目录 (aceflow_result/) 存在")
        else:
            self.logger.error("项目输出目录 (aceflow_result/) 不存在")
            structure_ok = False
        
        # 检查.aceflow配置目录
        aceflow_config_path = self.project_dir / ".aceflow"
        if aceflow_config_path.exists() and aceflow_config_path.is_dir():
            self.logger.success("配置目录 (.aceflow/) 存在")
            
            # 检查模板文件
            template_path = aceflow_config_path / "template.yaml"
            if template_path.exists():
                self.logger.success("流程模板文件存在")
            else:
                self.logger.warning("流程模板文件不存在")
        else:
            self.logger.warning("配置目录 (.aceflow/) 不存在")
        
        return structure_ok
    
    def check_state_files(self):
        """检查项目状态文件"""
        self.logger.info("检查项目状态文件...")
        
        # 检查主状态文件
        state_file_path = self.project_dir / "aceflow_result" / "current_state.json"
        if state_file_path.exists():
            self.logger.success("项目状态文件存在")
            
            # 验证JSON格式
            try:
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                self.logger.success("项目状态文件格式正确")
                
                # 检查必要字段
                required_fields = ["project", "flow", "memory", "quality"]
                for field in required_fields:
                    if field in state_data:
                        self.logger.success(f"状态文件包含字段: {field}")
                    else:
                        self.logger.error(f"状态文件缺少字段: {field}")
            except json.JSONDecodeError:
                self.logger.error("项目状态文件JSON格式错误")
            except Exception as e:
                self.logger.error(f"项目状态文件读取失败: {e}")
        else:
            self.logger.error("项目状态文件不存在")
        
        # 检查阶段进度文件
        progress_file_path = self.project_dir / "aceflow_result" / "stage_progress.json"
        if progress_file_path.exists():
            self.logger.success("阶段进度文件存在")
            
            try:
                with open(progress_file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.logger.success("阶段进度文件格式正确")
            except json.JSONDecodeError:
                self.logger.error("阶段进度文件JSON格式错误")
            except Exception as e:
                self.logger.error(f"阶段进度文件读取失败: {e}")
        else:
            self.logger.warning("阶段进度文件不存在")
    
    def check_mode_consistency(self) -> str:
        """检查流程模式一致性"""
        self.logger.info("检查流程模式一致性...")
        
        mode_from_state = ""
        mode_from_clinerules = ""
        mode_from_template = ""
        
        # 从状态文件获取模式
        state_file_path = self.project_dir / "aceflow_result" / "current_state.json"
        if state_file_path.exists():
            try:
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                mode_from_state = state_data.get('project', {}).get('mode', '')
            except Exception:
                pass
        
        # 从.clinerules获取模式
        clinerules_path = self.project_dir / ".clinerules"
        if clinerules_path.exists():
            try:
                content = clinerules_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if "AceFlow模式:" in line:
                        mode_from_clinerules = line.split(':')[1].strip()
                        break
            except Exception:
                pass
        
        # 从模板文件获取模式
        template_path = self.project_dir / ".aceflow" / "template.yaml"
        if template_path.exists():
            try:
                content = template_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.strip().startswith('mode:'):
                        mode_from_template = line.split(':')[1].strip().strip('"\'')
                        break
            except Exception:
                pass
        
        # 比较模式一致性
        if mode_from_state and mode_from_clinerules and mode_from_template:
            if mode_from_state == mode_from_clinerules == mode_from_template:
                self.logger.success(f"流程模式一致: {mode_from_state}")
                return mode_from_state
            else:
                self.logger.error(f"流程模式不一致: 状态({mode_from_state}) vs 配置({mode_from_clinerules}) vs 模板({mode_from_template})")
                return "inconsistent"
        else:
            self.logger.warning("无法确定流程模式一致性")
            return "unknown"
    
    def check_output_compliance(self, mode: str):
        """检查输出文件合规性"""
        self.logger.info(f"检查输出文件合规性 (模式: {mode})...")
        
        aceflow_result_path = self.project_dir / "aceflow_result"
        if not aceflow_result_path.exists():
            self.logger.error("输出目录不存在，跳过合规性检查")
            return
        
        # 检查基础文件结构
        expected_files = []
        if mode == "minimal":
            expected_files = ["current_state.json", "stage_progress.json"]
        elif mode == "standard":
            expected_files = ["current_state.json", "stage_progress.json", "user_stories.md", "tasks_planning.md"]
        elif mode == "complete":
            expected_files = ["current_state.json", "stage_progress.json", "s1_user_story.md", "s2_tasks_group.md"]
        elif mode == "smart":
            expected_files = ["current_state.json", "stage_progress.json", "project_analysis.json"]
        else:
            self.logger.warning("未知模式，跳过特定文件检查")
            return
        
        # 检查预期文件
        for filename in expected_files:
            file_path = aceflow_result_path / filename
            if file_path.exists():
                self.logger.success(f"预期文件存在: {filename}")
            else:
                self.logger.warning(f"预期文件不存在: {filename}")
        
        # 检查文件命名规范
        non_compliant_files = []
        try:
            for file_path in aceflow_result_path.rglob('*'):
                if file_path.is_file():
                    basename = file_path.name
                    # AceFlow命名规范: 只允许字母、数字、下划线、连字符和点
                    if not re.match(r'^[a-zA-Z0-9_.-]+$', basename):
                        non_compliant_files.append(basename)
        except Exception as e:
            self.logger.warning(f"文件命名检查失败: {e}")
        
        if not non_compliant_files:
            self.logger.success("所有文件命名符合规范")
        else:
            self.logger.warning(f"发现不符合命名规范的文件: {', '.join(non_compliant_files)}")
    
    def check_memory_system(self):
        """检查记忆系统状态"""
        self.logger.info("检查记忆系统状态...")
        
        # 检查记忆状态文件
        memory_state_path = self.project_dir / "aceflow_result" / "memory_state.json"
        if memory_state_path.exists():
            self.logger.success("记忆状态文件存在")
            
            try:
                with open(memory_state_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.logger.success("记忆状态文件格式正确")
            except json.JSONDecodeError:
                self.logger.error("记忆状态文件JSON格式错误")
            except Exception as e:
                self.logger.error(f"记忆状态文件读取失败: {e}")
        else:
            self.logger.warning("记忆状态文件不存在 (首次运行时正常)")
        
        # 检查记忆持久化配置
        state_file_path = self.project_dir / "aceflow_result" / "current_state.json"
        if state_file_path.exists():
            try:
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                memory_enabled = state_data.get('memory', {}).get('enabled', False)
                
                if memory_enabled:
                    self.logger.success("记忆系统已启用")
                else:
                    self.logger.warning("记忆系统未启用")
            except Exception:
                pass
        
        # 检查PATEOAS集成
        try:
            import aceflow.pateoas
            self.logger.success("PATEOAS记忆系统集成正常")
        except ImportError:
            self.logger.warning("PATEOAS记忆系统未正确集成")
    
    def check_quality_standards(self, mode: str):
        """检查质量标准"""
        self.logger.info(f"检查质量标准 (模式: {mode})...")
        
        # 获取质量配置
        template_path = self.project_dir / ".aceflow" / "template.yaml"
        if template_path.exists():
            try:
                content = template_path.read_text(encoding='utf-8')
                if "quality" in content:
                    self.logger.success("模板定义了质量标准")
                else:
                    self.logger.warning("模板未定义质量标准")
            except Exception:
                self.logger.warning("无法读取模板文件")
        
        # 根据模式检查特定质量要求
        if mode == "complete":
            # Complete模式需要严格的质量标准
            codereview_path = self.project_dir / "aceflow_result" / "s6_codereview.md"
            if codereview_path.exists():
                self.logger.success("Complete模式包含代码评审文档")
            else:
                self.logger.warning("Complete模式缺少代码评审文档")
        elif mode == "smart":
            # Smart模式需要质量指标跟踪
            analysis_path = self.project_dir / "aceflow_result" / "project_analysis.json"
            if analysis_path.exists():
                try:
                    with open(analysis_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    if 'quality' in str(analysis_data):
                        self.logger.success("Smart模式包含质量指标跟踪")
                    else:
                        self.logger.warning("Smart模式缺少质量指标跟踪")
                except Exception:
                    self.logger.warning("Smart模式质量指标检查失败")
    
    def generate_report(self, detected_mode: str) -> str:
        """生成验证报告"""
        self.logger.info("生成验证报告...")
        
        timestamp = datetime.now().isoformat()
        report_filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.project_dir / "aceflow_result" / report_filename
        
        # 收集系统信息
        git_status = "unknown"
        try:
            if (self.project_dir / ".git").exists():
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    changed_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                    git_status = f"{changed_files} files changed"
        except Exception:
            pass
        
        # 获取Python版本
        python_version = f"Python {sys.version.split()[0]}"
        
        # 计算成功率
        success_rate = 0.0
        if self.logger.total_checks > 0:
            success_rate = round((self.logger.passed_checks * 100) / self.logger.total_checks, 2)
        
        # 生成推荐建议
        recommendations = []
        if self.logger.failed_checks > 0:
            recommendations.append("修复失败的检查项以确保项目合规性")
        if self.logger.warning_checks > 0:
            recommendations.append("关注警告项以提高项目质量")
        if self.logger.failed_checks == 0 and self.logger.warning_checks == 0:
            recommendations.append("项目验证通过，可以正常使用AceFlow功能")
        elif not recommendations:
            recommendations.append("建议解决发现的问题后重新验证")
        
        # 生成报告内容
        report_data = {
            "validation": {
                "timestamp": timestamp,
                "script_version": self.VERSION,
                "project_directory": str(self.project_dir),
                "detected_mode": detected_mode
            },
            "results": {
                "total_checks": self.logger.total_checks,
                "passed_checks": self.logger.passed_checks,
                "failed_checks": self.logger.failed_checks,
                "warning_checks": self.logger.warning_checks,
                "success_rate": success_rate
            },
            "environment": {
                "aceflow_home": self.aceflow_home,
                "python_version": python_version,
                "git_status": git_status,
                "working_directory": str(Path.cwd())
            },
            "recommendations": recommendations
        }
        
        # 确保输出目录存在
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入报告文件
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            self.logger.success(f"验证报告已生成: {report_path}")
            return str(report_path)
        except Exception as e:
            self.logger.error(f"生成验证报告失败: {e}")
            return ""
    
    def auto_fix_issues(self):
        """自动修复功能"""
        self.logger.info("尝试自动修复发现的问题...")
        
        fixed_count = 0
        
        # 修复缺失的目录
        aceflow_result_path = self.project_dir / "aceflow_result"
        if not aceflow_result_path.exists():
            aceflow_result_path.mkdir(parents=True, exist_ok=True)
            self.logger.success("已创建 aceflow_result/ 目录")
            fixed_count += 1
        
        aceflow_config_path = self.project_dir / ".aceflow"
        if not aceflow_config_path.exists():
            aceflow_config_path.mkdir(parents=True, exist_ok=True)
            self.logger.success("已创建 .aceflow/ 配置目录")
            fixed_count += 1
        
        # 修复缺失的基础状态文件
        state_file_path = aceflow_result_path / "current_state.json"
        if not state_file_path.exists():
            current_time = datetime.now().isoformat()
            default_state = {
                "project": {
                    "name": "修复的项目",
                    "mode": "standard",
                    "created_at": current_time,
                    "last_updated": current_time,
                    "version": "3.0.0"
                },
                "flow": {
                    "current_stage": "initialized",
                    "completed_stages": [],
                    "progress_percentage": 0
                },
                "memory": {
                    "enabled": True,
                    "last_session": current_time,
                    "context_preserved": False
                },
                "quality": {
                    "standards_applied": False,
                    "compliance_checked": True,
                    "last_validation": current_time
                }
            }
            
            try:
                with open(state_file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_state, f, indent=2, ensure_ascii=False)
                self.logger.success("已创建基础项目状态文件")
                fixed_count += 1
            except Exception as e:
                self.logger.error(f"创建状态文件失败: {e}")
        
        # 修复缺失的.clinerules文件
        clinerules_path = self.project_dir / ".clinerules"
        if not clinerules_path.exists():
            default_clinerules = """# AceFlow v3.0 - AI Agent 集成配置
# 自动修复生成

## 工作模式配置
AceFlow模式: standard
输出目录: aceflow_result/
配置目录: .aceflow/

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
            
            try:
                clinerules_path.write_text(default_clinerules, encoding='utf-8')
                self.logger.success("已创建基础 .clinerules 配置文件")
                fixed_count += 1
            except Exception as e:
                self.logger.error(f"创建 .clinerules 文件失败: {e}")
        
        if fixed_count > 0:
            self.logger.success(f"自动修复完成，共修复 {fixed_count} 个问题")
        else:
            self.logger.info("没有发现可自动修复的问题")
    
    def show_summary(self, detected_mode: str):
        """显示验证结果摘要"""
        if self.logger.silent_mode:
            return
        
        print()
        print(f"{Colors.PURPLE}╔══════════════════════════════════════╗")
        print("║           验证结果摘要               ║")
        print(f"╚══════════════════════════════════════╝{Colors.NC}")
        print()
        
        # 结果统计
        print(f"{Colors.CYAN}检查统计:{Colors.NC}")
        print(f"  总检查项: {self.logger.total_checks}")
        print(f"  通过: {Colors.GREEN}{self.logger.passed_checks}{Colors.NC}")
        print(f"  失败: {Colors.RED}{self.logger.failed_checks}{Colors.NC}")
        print(f"  警告: {Colors.YELLOW}{self.logger.warning_checks}{Colors.NC}")
        
        # 成功率计算
        success_rate = 0.0
        if self.logger.total_checks > 0:
            success_rate = round((self.logger.passed_checks * 100) / self.logger.total_checks, 1)
        print(f"  成功率: {Colors.BLUE}{success_rate}%{Colors.NC}")
        print()
        
        # 总体评估
        if self.logger.failed_checks == 0:
            if self.logger.warning_checks == 0:
                print(f"{Colors.GREEN}✅ 项目验证完全通过！{Colors.NC}")
                print("您可以安全地使用AceFlow的所有功能。")
            else:
                print(f"{Colors.YELLOW}⚠️  项目验证基本通过，但有警告项{Colors.NC}")
                print("建议查看警告信息并考虑改进。")
        else:
            print(f"{Colors.RED}❌ 项目验证失败{Colors.NC}")
            print("请修复失败的检查项后重新验证。")
        
        print()
        print(f"{Colors.CYAN}模式信息:{Colors.NC} {detected_mode}")
        print(f"{Colors.CYAN}项目目录:{Colors.NC} {self.project_dir}")
    
    def validate(self) -> bool:
        """执行完整验证流程"""
        # 显示标题
        if not self.logger.silent_mode:
            self.logger.header()
            print(f"{Colors.CYAN}检查目录:{Colors.NC} {self.project_dir}")
            print(f"{Colors.CYAN}检查模式:{Colors.NC} {self.check_mode}")
            print()
        
        # 执行基础检查
        self.check_basic_structure()
        
        # 根据检查模式执行相应的验证
        detected_mode = "unknown"
        
        if self.check_mode == "quick":
            # 快速检查只验证基础结构
            pass
        elif self.check_mode in ["standard", "complete"]:
            self.check_state_files()
            detected_mode = self.check_mode_consistency()
            
            if detected_mode not in ["unknown", "inconsistent"]:
                self.check_output_compliance(detected_mode)
                self.check_quality_standards(detected_mode)
            
            if self.check_mode == "complete":
                self.check_memory_system()
        
        # 自动修复
        if self.auto_fix and self.logger.failed_checks > 0:
            self.auto_fix_issues()
        
        # 显示摘要
        if detected_mode == "unknown":
            detected_mode = self.check_mode_consistency()
        self.show_summary(detected_mode)
        
        # 返回验证结果
        return self.logger.failed_checks == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AceFlow v3.0 项目验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
检查模式:
  quick     - 快速检查 (基础文件结构)
  standard  - 标准检查 (文件结构 + 内容格式)
  complete  - 完整检查 (全面合规性验证)

示例:
  %(prog)s --mode=complete --report
  %(prog)s -d ./my-project --fix
  %(prog)s --silent
        """
    )
    
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="指定项目目录 (默认: 当前目录)"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["quick", "standard", "complete"],
        default="standard",
        help="指定检查模式 (默认: standard)"
    )
    parser.add_argument(
        "-f", "--fix",
        action="store_true",
        help="自动修复发现的问题"
    )
    parser.add_argument(
        "-r", "--report",
        action="store_true",
        help="生成详细验证报告"
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="静默模式，只显示结果"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"AceFlow Validator v{AceFlowValidator.VERSION}"
    )
    
    args = parser.parse_args()
    
    # 验证项目目录
    project_dir = Path(args.directory).resolve()
    if not project_dir.exists():
        print(f"{Colors.RED}[ERROR]{Colors.NC} 项目目录不存在: {project_dir}")
        sys.exit(1)
    
    # 创建验证器并执行验证
    validator = AceFlowValidator(
        project_dir=str(project_dir),
        check_mode=args.mode,
        auto_fix=args.fix,
        silent_mode=args.silent
    )
    
    try:
        # 切换到项目目录
        original_cwd = Path.cwd()
        os.chdir(project_dir)
        
        # 执行验证
        validation_passed = validator.validate()
        
        # 生成报告
        if args.report:
            detected_mode = validator.check_mode_consistency()
            validator.generate_report(detected_mode)
        
        # 恢复原始工作目录
        os.chdir(original_cwd)
        
        # 设置退出码
        sys.exit(0 if validation_passed else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN]{Colors.NC} 验证被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.NC} 验证过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()