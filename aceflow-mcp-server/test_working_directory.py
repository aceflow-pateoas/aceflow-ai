#!/usr/bin/env python3
"""
测试新的工作目录检测逻辑
"""

import os
import sys
from pathlib import Path
import tempfile
import shutil

# 添加当前目录到路径
sys.path.insert(0, '.')

from aceflow_mcp_server.tools import AceFlowTools

def test_working_directory_detection():
    """测试工作目录检测逻辑"""
    
    print("=== 测试工作目录检测逻辑 ===\n")
    
    # 1. 测试：明确指定目录
    print("1. 测试明确指定目录:")
    tools = AceFlowTools("/tmp")
    print(f"   指定目录: /tmp")
    print(f"   工作目录: {tools.working_directory}\n")
    
    # 2. 测试：指定当前目录
    print("2. 测试指定当前目录 (.):")
    tools2 = AceFlowTools(".")
    print(f"   指定目录: .")
    print(f"   工作目录: {tools2.working_directory}\n")
    
    # 3. 测试：创建临时项目目录
    print("3. 测试自动检测项目目录:")
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建项目文件
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test"}')
        (project_dir / "README.md").write_text("# Test Project")
        
        # 切换到项目目录
        original_cwd = os.getcwd()
        os.chdir(str(project_dir))
        
        try:
            tools3 = AceFlowTools()
            print(f"   当前目录: {os.getcwd()}")
            print(f"   工作目录: {tools3.working_directory}")
            print(f"   自动检测成功: {tools3.working_directory == str(project_dir)}\n")
        finally:
            os.chdir(original_cwd)
    
    # 4. 测试：非项目目录（应该要求用户输入）
    print("4. 测试非项目目录:")
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个空的子目录，确保它不在任何项目中
        empty_dir = Path(temp_dir) / "empty" / "nested" / "deep"
        empty_dir.mkdir(parents=True)
        
        original_cwd = os.getcwd()
        os.chdir(str(empty_dir))
        
        try:
            print(f"   测试目录: {os.getcwd()}")
            try:
                tools4 = AceFlowTools()
                print(f"   错误：应该抛出异常但没有，工作目录: {tools4.working_directory}")
            except ValueError as e:
                print(f"   正确：检测失败并要求用户输入")
                print(f"   错误信息: {str(e)[:100]}...")
        finally:
            os.chdir(original_cwd)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_working_directory_detection()