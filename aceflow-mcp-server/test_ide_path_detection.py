#!/usr/bin/env python3
"""
测试IDE安装目录检测和修复逻辑
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, '.')

from aceflow_mcp_server.tools import AceFlowTools

def test_ide_path_detection():
    """测试IDE安装路径检测和规避逻辑"""
    
    print("=== 测试IDE安装路径检测和修复 ===\n")
    
    tools = AceFlowTools()
    
    # 1. 测试IDE路径检测功能
    print("1. 测试IDE路径检测:")
    ide_paths = [
        "D:\\Program Files\\Microsoft VS Code",
        "D:\\Program Files\\CodeBuddy",
        "C:\\Program Files\\Visual Studio Code",
        "C:\\Program Files (x86)\\Microsoft VS Code",
        "/Applications/Visual Studio Code.app",
        "/opt/visual-studio-code",
        "/snap/code",
        "/usr/share/code"
    ]
    
    for path in ide_paths:
        is_ide = tools._is_ide_installation_path(path)
        print(f"   {path}: {'IDE路径' if is_ide else '非IDE路径'}")
    
    print()
    
    # 2. 测试环境变量优先级
    print("2. 测试环境变量优先级:")
    
    # 模拟当前目录是IDE安装目录的情况
    original_cwd = os.getcwd()
    
    # 创建测试项目目录
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()
        
        # 设置IDE环境变量
        os.environ['VSCODE_CWD'] = str(project_dir)
        
        try:
            # 模拟切换到"IDE安装目录"（实际是临时目录模拟）
            ide_sim_dir = Path(temp_dir) / "Program Files" / "Microsoft VS Code"
            ide_sim_dir.mkdir(parents=True)
            os.chdir(str(ide_sim_dir))
            
            # 测试动态检测
            detected_dir = tools._get_dynamic_working_directory()
            
            print(f"   当前目录: {os.getcwd()}")
            print(f"   VSCODE_CWD: {os.environ.get('VSCODE_CWD')}")
            print(f"   检测结果: {detected_dir}")
            print(f"   使用环境变量: {detected_dir == str(project_dir)}")
            
        except Exception as e:
            print(f"   检测过程出错: {e}")
        finally:
            os.environ.pop('VSCODE_CWD', None)
            os.chdir(original_cwd)
    
    print()
    
    # 3. 测试无可用目录时的错误提示
    print("3. 测试无可用目录时的处理:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建模拟IDE目录
        ide_sim_dir = Path(temp_dir) / "Program Files" / "CodeBuddy"
        ide_sim_dir.mkdir(parents=True)
        os.chdir(str(ide_sim_dir))
        
        try:
            # 应该抛出清晰的错误信息
            detected_dir = tools._get_dynamic_working_directory()
            print(f"   错误：应该抛出异常但没有，返回了: {detected_dir}")
        except ValueError as e:
            print(f"   正确：检测到IDE路径并要求用户指定目录")
            print(f"   错误信息预览: {str(e)[:150]}...")
        finally:
            os.chdir(original_cwd)
    
    print()
    
    # 4. 测试明确指定目录时的处理
    print("4. 测试明确指定目录:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "user_project"
        project_dir.mkdir()
        
        # 即使当前在IDE目录，明确指定也应该工作
        ide_sim_dir = Path(temp_dir) / "Program Files" / "VS Code"
        ide_sim_dir.mkdir(parents=True)
        os.chdir(str(ide_sim_dir))
        
        try:
            # 明确指定项目目录
            detected_dir = tools._get_dynamic_working_directory(str(project_dir))
            print(f"   当前目录: {os.getcwd()}")
            print(f"   指定目录: {project_dir}")
            print(f"   检测结果: {detected_dir}")
            print(f"   正确处理: {detected_dir == str(project_dir)}")
        finally:
            os.chdir(original_cwd)
    
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    test_ide_path_detection()