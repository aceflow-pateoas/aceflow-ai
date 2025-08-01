#!/usr/bin/env python3
"""
AceFlow v3.0 模板管理脚本
AI Agent 增强层模板系统工具
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI颜色代码"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    GRAY = '\033[0;37m'
    NC = '\033[0m'  # No Color


class TemplateLogger:
    """模板管理日志记录器"""
    
    def __init__(self):
        pass
    
    def info(self, message: str):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
    
    def success(self, message: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    def warning(self, message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    def error(self, message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    def header(self):
        header_text = f"""{Colors.PURPLE}
╔══════════════════════════════════════╗
║       AceFlow v3.0 模板管理          ║
║      AI Agent 增强层模板工具         ║
╚══════════════════════════════════════╝{Colors.NC}"""
        print(header_text)


class AceFlowTemplateManager:
    """AceFlow模板管理器"""
    
    VERSION = "3.0.0"
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.logger = TemplateLogger()
        
        # 获取AceFlow根目录
        script_path = Path(__file__).resolve()
        self.aceflow_home = Path(os.environ.get('ACEFLOW_HOME', script_path.parent.parent))
    
    def get_template_dir(self) -> Path:
        """获取模板目录"""
        return self.aceflow_home / "templates"
    
    def validate_mode(self, mode: str) -> bool:
        """验证模式是否存在"""
        template_dir = self.get_template_dir()
        mode_dir = template_dir / mode
        return mode_dir.exists() and mode_dir.is_dir()
    
    def get_current_mode(self) -> str:
        """获取当前项目模式"""
        state_file = self.project_dir / "aceflow_result" / "current_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('project', {}).get('mode', 'unknown')
            except Exception:
                return "unknown"
        return "unknown"
    
    def list_templates(self, verbose: bool = False) -> bool:
        """列出所有可用模板"""
        template_dir = self.get_template_dir()
        
        self.logger.info(f"扫描模板目录: {template_dir}")
        
        if not template_dir.exists():
            self.logger.error(f"模板目录不存在: {template_dir}")
            return False
        
        print()
        print(f"{Colors.CYAN}可用模板列表{Colors.NC}")
        print("─────────────────────────────")
        
        current_mode = self.get_current_mode()
        template_count = 0
        
        # 需要跳过的特殊目录
        skip_patterns = [
            "document_templates",
            "s1_", "s2_", "s3_", "s4_", "s5_", "s6_", "s7_", "s8_"
        ]
        
        for mode_dir in sorted(template_dir.iterdir()):
            if mode_dir.is_dir():
                mode = mode_dir.name
                
                # 跳过特殊目录
                if any(mode.startswith(pattern) for pattern in skip_patterns):
                    continue
                
                status = ""
                icon = "📋"
                
                if mode == current_mode:
                    status = f" {Colors.GREEN}(当前使用){Colors.NC}"
                    icon = "📌"
                
                print(f"  {icon} {Colors.BLUE}{mode}{Colors.NC}{status}")
                template_count += 1
                
                if verbose:
                    # 显示模板详细信息
                    template_file = mode_dir / "template.yaml"
                    readme_file = mode_dir / "README.md"
                    
                    if template_file.exists():
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            # 简单提取描述信息
                            description = "无描述"
                            for line in content.split('\n'):
                                if line.strip().startswith('description:'):
                                    description = line.split(':', 1)[1].strip().strip('"\'')
                                    break
                            print(f"    📝 描述: {description}")
                        except Exception:
                            print("    📝 描述: 读取失败")
                    
                    if readme_file.exists():
                        try:
                            with open(readme_file, 'r', encoding='utf-8') as f:
                                first_line = f.readline().strip()
                                if first_line.startswith('#'):
                                    first_line = first_line.lstrip('#').strip()
                                if first_line:
                                    print(f"    📖 说明: {first_line}")
                        except Exception:
                            pass
                    
                    # 显示文件统计
                    try:
                        file_count = len(list(mode_dir.rglob('*')))
                        print(f"    📁 文件数: {file_count}")
                    except Exception:
                        print("    📁 文件数: 未知")
                    print()
        
        if template_count == 0:
            self.logger.warning("未找到可用模板")
            return False
        
        print()
        print(f"{Colors.CYAN}模板统计{Colors.NC}")
        print("─────────────────────────────")
        print(f"可用模板数: {template_count}")
        print(f"当前模式: {current_mode}")
        
        return True
    
    def show_template_info(self, mode: str, verbose: bool = False) -> bool:
        """显示模板详细信息"""
        if not self.validate_mode(mode):
            self.logger.error(f"模板不存在: {mode}")
            return False
        
        template_dir = self.get_template_dir()
        mode_dir = template_dir / mode
        template_file = mode_dir / "template.yaml"
        readme_file = mode_dir / "README.md"
        
        print()
        print(f"{Colors.CYAN}模板信息: {mode}{Colors.NC}")
        print("═══════════════════════════════════")
        
        # 基础信息
        if template_file.exists():
            print(f"{Colors.YELLOW}📋 配置信息{Colors.NC}")
            print("─────────────────────────────")
            
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                # 提取关键信息
                project_info = template_data.get('project', {})
                description = project_info.get('description', '无描述')
                team_size = project_info.get('team_size', '未指定')
                duration = project_info.get('estimated_duration', '未指定')
                
                print(f"描述: {description}")
                print(f"团队规模: {team_size}")
                print(f"预估时长: {duration}")
                print()
                
            except Exception as e:
                print(f"配置文件读取失败: {e}")
                print()
        
        # README信息
        if readme_file.exists():
            print(f"{Colors.YELLOW}📖 使用说明{Colors.NC}")
            print("─────────────────────────────")
            
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if verbose:
                    # 显示完整README
                    print(''.join(lines))
                else:
                    # 显示前10行
                    display_lines = lines[:10]
                    print(''.join(display_lines))
                    
                    if len(lines) > 10:
                        print()
                        print(f"{Colors.GRAY}... (还有 {len(lines) - 10} 行，使用 --verbose 查看完整内容){Colors.NC}")
                print()
                
            except Exception as e:
                print(f"README读取失败: {e}")
                print()
        
        # 文件结构
        print(f"{Colors.YELLOW}📁 文件结构{Colors.NC}")
        print("─────────────────────────────")
        
        try:
            # 尝试使用tree命令
            result = subprocess.run(
                ["tree", str(mode_dir), "-I", "__pycache__|*.pyc"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                raise subprocess.CalledProcessError(result.returncode, "tree")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 使用简单的文件列表
            try:
                files = sorted([str(p.relative_to(mode_dir)) for p in mode_dir.rglob('*') if p.is_file()])
                for file_path in files:
                    print(f"  {file_path}")
            except Exception as e:
                print(f"无法列出文件: {e}")
        
        print()
        
        # 模板统计
        print(f"{Colors.YELLOW}📊 统计信息{Colors.NC}")
        print("─────────────────────────────")
        
        try:
            all_files = list(mode_dir.rglob('*'))
            file_count = len([f for f in all_files if f.is_file()])
            yaml_count = len([f for f in all_files if f.is_file() and f.suffix in ['.yaml', '.yml']])
            md_count = len([f for f in all_files if f.is_file() and f.suffix == '.md'])
            
            print(f"总文件数: {file_count}")
            print(f"YAML配置: {yaml_count}")
            print(f"Markdown文档: {md_count}")
            
            # 最后修改时间
            try:
                mtimes = [f.stat().st_mtime for f in all_files if f.is_file()]
                if mtimes:
                    last_modified = datetime.fromtimestamp(max(mtimes)).strftime("%Y-%m-%d %H:%M:%S")
                    print(f"最后修改: {last_modified}")
            except Exception:
                print("最后修改: 未知")
                
        except Exception as e:
            print(f"统计信息获取失败: {e}")
        
        return True
    
    def switch_mode(self, target_mode: str, force: bool = False, verbose: bool = False) -> bool:
        """切换项目模式"""
        if not self.validate_mode(target_mode):
            self.logger.error(f"模板不存在: {target_mode}")
            return False
        
        current_mode = self.get_current_mode()
        
        if target_mode == current_mode:
            self.logger.info(f"项目已经使用模式: {target_mode}")
            return True
        
        # 检查项目是否已初始化
        state_file = self.project_dir / "aceflow_result" / "current_state.json"
        if not state_file.exists():
            self.logger.error("项目未初始化，请先运行 aceflow-init.py")
            return False
        
        if not force:
            print(f"{Colors.YELLOW}即将从 '{current_mode}' 切换到 '{target_mode}' 模式{Colors.NC}")
            print(f"{Colors.RED}警告: 这将重置项目状态和进度{Colors.NC}")
            confirm = input("确认继续? (y/N): ").strip().lower()
            if confirm != 'y' and confirm != 'yes':
                self.logger.info("操作已取消")
                return True
        
        self.logger.info("备份当前配置...")
        self.backup_current_config()
        
        self.logger.info("应用新模板...")
        template_dir = self.get_template_dir()
        
        # 清理并重新创建配置目录
        aceflow_config_dir = self.project_dir / ".aceflow"
        if aceflow_config_dir.exists():
            shutil.rmtree(aceflow_config_dir)
        aceflow_config_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制新模板
        source_template_dir = template_dir / target_mode
        try:
            for item in source_template_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, aceflow_config_dir)
                elif item.is_dir():
                    shutil.copytree(item, aceflow_config_dir / item.name)
        except Exception as e:
            self.logger.error(f"复制模板失败: {e}")
            return False
        
        # 更新项目状态
        self.update_project_mode(target_mode)
        
        # 重新生成.clinerules
        self.generate_clinerules(target_mode)
        
        self.logger.success(f"已切换到模式: {target_mode}")
        
        if verbose:
            self.show_template_info(target_mode, False)
        
        return True
    
    def backup_current_config(self) -> bool:
        """备份当前配置"""
        backup_dir = self.project_dir / "aceflow_result" / "backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_backup_{timestamp}"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 备份配置目录
            aceflow_config_dir = self.project_dir / ".aceflow"
            if aceflow_config_dir.exists():
                backup_config_dir = backup_dir / backup_name
                shutil.copytree(aceflow_config_dir, backup_config_dir)
                self.logger.success(f"配置已备份到: {backup_config_dir}")
            
            # 备份状态文件
            state_file = self.project_dir / "aceflow_result" / "current_state.json"
            if state_file.exists():
                backup_state_file = backup_dir / f"{backup_name}_state.json"
                shutil.copy2(state_file, backup_state_file)
            
            # 备份.clinerules
            clinerules_file = self.project_dir / ".clinerules"
            if clinerules_file.exists():
                backup_clinerules_file = backup_dir / f"{backup_name}_clinerules"
                shutil.copy2(clinerules_file, backup_clinerules_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            return False
    
    def restore_from_backup(self, backup_name: str, force: bool = False) -> bool:
        """从备份恢复配置"""
        backup_dir = self.project_dir / "aceflow_result" / "backups"
        backup_path = backup_dir / backup_name
        
        if not backup_path.exists():
            self.logger.error(f"备份不存在: {backup_name}")
            self.logger.info("可用备份:")
            
            try:
                backups = [d.name for d in backup_dir.iterdir() 
                          if d.is_dir() and d.name.startswith("config_backup_")]
                if backups:
                    for backup in sorted(backups):
                        print(f"  {backup}")
                else:
                    print("  (无备份)")
            except Exception:
                print("  (无法列出备份)")
            
            return False
        
        if not force:
            print(f"{Colors.YELLOW}即将从备份恢复配置: {backup_name}{Colors.NC}")
            confirm = input("确认继续? (y/N): ").strip().lower()
            if confirm != 'y' and confirm != 'yes':
                self.logger.info("操作已取消")
                return True
        
        try:
            # 恢复配置目录
            aceflow_config_dir = self.project_dir / ".aceflow"
            if aceflow_config_dir.exists():
                shutil.rmtree(aceflow_config_dir)
            shutil.copytree(backup_path, aceflow_config_dir)
            
            # 恢复状态文件
            backup_state_file = backup_dir / f"{backup_name}_state.json"
            if backup_state_file.exists():
                state_file = self.project_dir / "aceflow_result" / "current_state.json"
                shutil.copy2(backup_state_file, state_file)
            
            # 恢复.clinerules
            backup_clinerules_file = backup_dir / f"{backup_name}_clinerules"
            if backup_clinerules_file.exists():
                clinerules_file = self.project_dir / ".clinerules"
                shutil.copy2(backup_clinerules_file, clinerules_file)
            
            self.logger.success(f"配置已从备份恢复: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复失败: {e}")
            return False
    
    def validate_template(self, mode: str) -> bool:
        """验证模板配置"""
        if not self.validate_mode(mode):
            self.logger.error(f"模板不存在: {mode}")
            return False
        
        template_dir = self.get_template_dir()
        mode_dir = template_dir / mode
        template_file = mode_dir / "template.yaml"
        readme_file = mode_dir / "README.md"
        
        validation_errors = 0
        
        print(f"{Colors.CYAN}验证模板: {mode}{Colors.NC}")
        print("─────────────────────────────")
        
        # 检查必需文件
        if template_file.exists():
            self.logger.success("模板配置文件存在")
            
            # 验证YAML格式
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                self.logger.success("YAML格式正确")
            except yaml.YAMLError:
                self.logger.error("YAML格式错误")
                validation_errors += 1
            except Exception as e:
                self.logger.error(f"YAML读取失败: {e}")
                validation_errors += 1
            
            # 检查必需字段
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                required_fields = ["project", "flow"]
                for field in required_fields:
                    if field in template_data:
                        self.logger.success(f"包含必需字段: {field}")
                    else:
                        self.logger.error(f"缺少必需字段: {field}")
                        validation_errors += 1
                        
            except Exception as e:
                self.logger.error(f"字段检查失败: {e}")
                validation_errors += 1
        else:
            self.logger.error("模板配置文件不存在: template.yaml")
            validation_errors += 1
        
        if readme_file.exists():
            self.logger.success("README文档存在")
        else:
            self.logger.warning("README文档不存在")
        
        # 验证模式特定要求
        if mode == "complete":
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                stage_files = ["s1_user_story", "s2_tasks_group", "s3_testcases", 
                              "s4_implementation", "s5_test_report", "s6_codereview", 
                              "s7_demo_script", "s8_summary_report"]
                
                for stage in stage_files:
                    if stage in content:
                        self.logger.success(f"包含完整模式阶段: {stage}")
                    else:
                        self.logger.warning(f"完整模式可能缺少阶段: {stage}")
                        
            except Exception:
                pass
                
        elif mode == "smart":
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "smart_features" in content:
                    self.logger.success("包含智能特性配置")
                else:
                    self.logger.error("智能模式缺少智能特性配置")
                    validation_errors += 1
                    
            except Exception:
                pass
        
        print()
        if validation_errors == 0:
            self.logger.success("模板验证通过")
            return True
        else:
            self.logger.error(f"模板验证失败，发现 {validation_errors} 个错误")
            return False
    
    def customize_template(self, mode: str) -> bool:
        """自定义模板配置"""
        if not self.validate_mode(mode):
            self.logger.error(f"模板不存在: {mode}")
            return False
        
        print(f"{Colors.CYAN}自定义模板配置: {mode}{Colors.NC}")
        print("─────────────────────────────")
        
        # 创建自定义配置目录
        custom_dir = self.project_dir / ".aceflow" / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制原始模板
        template_dir = self.get_template_dir()
        source_template_dir = template_dir / mode
        
        try:
            for item in source_template_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, custom_dir)
                elif item.is_dir():
                    shutil.copytree(item, custom_dir / item.name, dirs_exist_ok=True)
        except Exception as e:
            self.logger.error(f"复制模板失败: {e}")
            return False
        
        self.logger.info(f"模板已复制到自定义目录: {custom_dir}")
        print()
        
        # 提供自定义选项
        print("可自定义选项:")
        print("1. 修改项目信息 (项目名称、描述等)")
        print("2. 调整质量标准 (覆盖率、通过率等)")
        print("3. 自定义阶段配置 (添加或删除阶段)")
        print("4. 修改输出格式 (文档模板、命名规则等)")
        print("5. 集成工具配置 (CI/CD、测试工具等)")
        print()
        
        try:
            custom_choice = input("选择要自定义的选项 (1-5): ").strip()
            
            if custom_choice == "1":
                self.customize_project_info(custom_dir)
            elif custom_choice == "2":
                self.logger.info("质量标准自定义功能待实现")
            elif custom_choice == "3":
                self.logger.info("阶段配置自定义功能待实现")
            elif custom_choice == "4":
                self.logger.info("输出格式自定义功能待实现")
            elif custom_choice == "5":
                self.logger.info("工具集成自定义功能待实现")
            else:
                self.logger.info("无效选择，请使用文本编辑器手动自定义")
                template_file = custom_dir / "template.yaml"
                editor = os.environ.get('EDITOR', 'nano')
                try:
                    subprocess.run([editor, str(template_file)])
                except Exception as e:
                    self.logger.error(f"打开编辑器失败: {e}")
                    return False
            
        except KeyboardInterrupt:
            self.logger.info("自定义操作被取消")
            return False
        
        self.logger.success("自定义配置完成")
        print(f"自定义文件位置: {custom_dir}")
        print(f"使用 'aceflow-templates.py import {custom_dir}/template.yaml' 应用自定义配置")
        
        return True
    
    def customize_project_info(self, custom_dir: Path) -> bool:
        """自定义项目信息"""
        template_file = custom_dir / "template.yaml"
        
        print("自定义项目信息:")
        
        try:
            project_name = input("项目名称: ").strip()
            project_desc = input("项目描述: ").strip()
            team_size = input("团队规模: ").strip()
            duration = input("预估时长: ").strip()
            
            # 读取现有配置
            with open(template_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            if 'project' not in data:
                data['project'] = {}
            
            # 更新配置
            if project_name:
                data['project']['name'] = project_name
            if project_desc:
                data['project']['description'] = project_desc
            if team_size:
                data['project']['team_size'] = team_size
            if duration:
                data['project']['estimated_duration'] = duration
            
            # 写回文件
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            print("项目信息已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新项目信息失败: {e}")
            return False
    
    def export_template(self, mode: str, output_file: str) -> bool:
        """导出模板配置"""
        if not self.validate_mode(mode):
            self.logger.error(f"模板不存在: {mode}")
            return False
        
        template_dir = self.get_template_dir()
        template_file = template_dir / mode / "template.yaml"
        
        if not template_file.exists():
            self.logger.error("模板配置文件不存在")
            return False
        
        try:
            # 复制模板文件
            shutil.copy2(template_file, output_file)
            self.logger.success(f"模板已导出到: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"导出失败: {e}")
            return False
    
    def import_template(self, import_file: str, force: bool = False) -> bool:
        """导入模板配置"""
        import_path = Path(import_file)
        if not import_path.exists():
            self.logger.error(f"导入文件不存在: {import_file}")
            return False
        
        # 验证导入文件格式
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError:
            self.logger.error("导入文件格式错误")
            return False
        except Exception as e:
            self.logger.error(f"导入文件读取失败: {e}")
            return False
        
        if not force:
            print(f"{Colors.YELLOW}即将导入模板配置: {import_file}{Colors.NC}")
            confirm = input("确认继续? (y/N): ").strip().lower()
            if confirm != 'y' and confirm != 'yes':
                self.logger.info("操作已取消")
                return True
        
        # 备份当前配置
        self.backup_current_config()
        
        try:
            # 应用导入的配置
            aceflow_config_dir = self.project_dir / ".aceflow"
            aceflow_config_dir.mkdir(parents=True, exist_ok=True)
            
            template_target = aceflow_config_dir / "template.yaml"
            shutil.copy2(import_path, template_target)
            
            # 确定导入的模式
            with open(import_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            imported_mode = data.get('flow', {}).get('mode', 'standard')
            
            # 更新项目状态
            self.update_project_mode(imported_mode)
            self.generate_clinerules(imported_mode)
            
            self.logger.success("模板配置已导入")
            return True
            
        except Exception as e:
            self.logger.error(f"导入失败: {e}")
            return False
    
    def update_project_mode(self, new_mode: str) -> bool:
        """更新项目模式"""
        state_file = self.project_dir / "aceflow_result" / "current_state.json"
        
        if not state_file.exists():
            return False
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['project']['mode'] = new_mode
            data['project']['last_updated'] = datetime.now().isoformat()
            data['flow']['current_stage'] = 'initialized'
            data['flow']['completed_stages'] = []
            data['flow']['progress_percentage'] = 0
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新项目模式失败: {e}")
            return False
    
    def generate_clinerules(self, mode: str) -> bool:
        """生成.clinerules文件"""
        clinerules_content = f"""# AceFlow v3.0 - AI Agent 集成配置
# 模式: {mode}

## 工作模式配置
AceFlow模式: {mode}
输出目录: aceflow_result/
配置目录: .aceflow/
模板文件: .aceflow/template.yaml

## 核心工作原则
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 工具集成命令
- aceflow-validate.py: 验证项目状态和合规性
- aceflow-stage.py: 管理项目阶段和进度
- aceflow-templates.py: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
        
        try:
            clinerules_file = self.project_dir / ".clinerules"
            clinerules_file.write_text(clinerules_content, encoding='utf-8')
            return True
        except Exception as e:
            self.logger.error(f"生成.clinerules失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AceFlow v3.0 模板管理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令说明:
  list                     列出所有可用模板
  info MODE               显示指定模式的详细信息
  switch MODE             切换项目到指定模式
  backup                  备份当前模板配置
  restore BACKUP          从备份恢复模板配置
  validate MODE           验证模板配置
  customize MODE          自定义模板配置
  export MODE FILE        导出模板配置到文件
  import FILE             从文件导入模板配置

模式类型:
  minimal     - 最简流程模式
  standard    - 标准流程模式
  complete    - 完整流程模式
  smart       - 智能自适应模式

示例:
  %(prog)s list
  %(prog)s info smart --verbose
  %(prog)s switch complete --force
  %(prog)s export smart my-template.yaml
        """
    )
    
    parser.add_argument(
        "command",
        choices=["list", "info", "switch", "backup", "restore", "validate", "customize", "export", "import"],
        help="要执行的命令"
    )
    parser.add_argument(
        "mode_or_file",
        nargs="?",
        help="模式名称、备份名称或文件路径"
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        help="输出文件路径 (用于export命令)"
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="指定项目目录 (默认: 当前目录)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="强制执行操作，跳过确认"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    parser.add_argument(
        "-o", "--output",
        help="指定输出目录"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"AceFlow Template Manager v{AceFlowTemplateManager.VERSION}"
    )
    
    args = parser.parse_args()
    
    # 验证项目目录
    project_dir = Path(args.directory).resolve()
    if not project_dir.exists():
        print(f"{Colors.RED}[ERROR]{Colors.NC} 项目目录不存在: {project_dir}")
        sys.exit(1)
    
    # 创建模板管理器
    manager = AceFlowTemplateManager(str(project_dir))
    
    try:
        # 切换到项目目录
        original_cwd = Path.cwd()
        os.chdir(project_dir)
        
        # 显示标题
        manager.logger.header()
        
        success = True
        
        # 执行对应命令
        if args.command == "list":
            success = manager.list_templates(args.verbose)
            
        elif args.command == "info":
            if not args.mode_or_file:
                manager.logger.error("请指定模式名称")
                success = False
            else:
                success = manager.show_template_info(args.mode_or_file, args.verbose)
                
        elif args.command == "switch":
            if not args.mode_or_file:
                manager.logger.error("请指定目标模式")
                success = False
            else:
                success = manager.switch_mode(args.mode_or_file, args.force, args.verbose)
                
        elif args.command == "backup":
            success = manager.backup_current_config()
            
        elif args.command == "restore":
            if not args.mode_or_file:
                manager.logger.error("请指定备份名称")
                success = False
            else:
                success = manager.restore_from_backup(args.mode_or_file, args.force)
                
        elif args.command == "validate":
            if not args.mode_or_file:
                manager.logger.error("请指定模式名称")
                success = False
            else:
                success = manager.validate_template(args.mode_or_file)
                
        elif args.command == "customize":
            if not args.mode_or_file:
                manager.logger.error("请指定模式名称")
                success = False
            else:
                success = manager.customize_template(args.mode_or_file)
                
        elif args.command == "export":
            if not args.mode_or_file or not args.output_file:
                manager.logger.error("请指定模式名称和输出文件")
                success = False
            else:
                success = manager.export_template(args.mode_or_file, args.output_file)
                
        elif args.command == "import":
            if not args.mode_or_file:
                manager.logger.error("请指定导入文件")
                success = False
            else:
                success = manager.import_template(args.mode_or_file, args.force)
        
        # 恢复原始工作目录
        os.chdir(original_cwd)
        
        # 设置退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARNING]{Colors.NC} 操作被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.NC} 执行过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()