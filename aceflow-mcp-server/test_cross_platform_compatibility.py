#!/usr/bin/env python3
"""
Windows和Linux平台兼容性测试脚本
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, '.')

from aceflow_mcp_server.tools import AceFlowTools

def test_cross_platform_compatibility():
    """测试跨平台兼容性"""
    
    print("=== 跨平台兼容性测试 ===\n")
    
    tools = AceFlowTools()
    
    print(f"当前平台: {os.name}")
    print(f"Python版本: {sys.version}")
    print(f"路径分隔符: {os.sep}")
    print(f"当前工作目录: {os.getcwd()}\n")
    
    # 1. 测试路径处理
    print("1. 测试路径处理兼容性:")
    test_paths = [
        ".",
        "./test",
        "../test", 
        "/tmp" if os.name != 'nt' else "C:\\temp",
        str(Path.home())
    ]
    
    for test_path in test_paths:
        try:
            if os.path.exists(test_path):
                abs_path = os.path.abspath(test_path)
                print(f"   {test_path} -> {abs_path}")
            else:
                print(f"   {test_path} -> 不存在")
        except Exception as e:
            print(f"   {test_path} -> 错误: {e}")
    
    # 2. 测试环境变量检测
    print(f"\n2. 测试环境变量检测:")
    
    # 通用环境变量
    common_vars = ['PWD', 'HOME', 'USER', 'PATH']
    if os.name == 'nt':
        # Windows特定环境变量
        platform_vars = ['USERPROFILE', 'USERNAME', 'APPDATA', 'CD']
    else:
        # Unix/Linux特定环境变量
        platform_vars = ['OLDPWD', 'SHELL', 'TERM']
    
    all_vars = common_vars + platform_vars
    
    for var in all_vars:
        value = os.environ.get(var)
        if value:
            # 截断长路径以便显示
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"   {var}: {display_value}")
        else:
            print(f"   {var}: 未设置")
    
    # 3. 测试动态工作目录在不同场景下的行为
    print(f"\n3. 测试动态工作目录检测:")
    
    # 场景1: 正常目录
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            detected_dir = tools._get_dynamic_working_directory()
            print(f"   临时目录检测: {detected_dir == temp_dir}")
            print(f"   路径: {detected_dir}")
        except Exception as e:
            print(f"   临时目录检测失败: {e}")
        finally:
            os.chdir(original_cwd)
    
    # 场景2: 带空格的路径（Windows常见）
    print(f"\n4. 测试特殊字符路径处理:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建带空格的子目录
        special_dir = Path(temp_dir) / "test with spaces"
        special_dir.mkdir()
        
        original_cwd = os.getcwd()
        os.chdir(str(special_dir))
        
        try:
            detected_dir = tools._get_dynamic_working_directory()
            print(f"   带空格路径检测: {detected_dir == str(special_dir)}")
            print(f"   路径: {detected_dir}")
        except Exception as e:
            print(f"   带空格路径检测失败: {e}")
        finally:
            os.chdir(original_cwd)
    
    # 5. 测试权限检查
    print(f"\n5. 测试目录权限检查:")
    
    test_dirs = [
        os.getcwd(),
        str(Path.home()),
        "/tmp" if os.name != 'nt' else "C:\\temp"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            is_valid = tools._is_valid_working_directory(test_dir)
            print(f"   {test_dir}: {'有效' if is_valid else '无效'}")
        else:
            print(f"   {test_dir}: 不存在")
    
    # 6. 模拟IDE环境变量
    print(f"\n6. 测试IDE环境变量模拟:")
    
    ide_vars = [
        ('VSCODE_CWD', str(Path.home())),
        ('CURSOR_CWD', str(Path.home())),
        ('PROJECT_DIR', str(Path.home())),
        ('MCP_PROJECT_DIR', str(Path.home()))
    ]
    
    for var, value in ide_vars:
        # 设置环境变量
        os.environ[var] = value
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    detected_dir = tools._get_dynamic_working_directory()
                    # 应该优先使用当前目录而不是环境变量
                    uses_current = detected_dir == temp_dir
                    print(f"   {var}: 优先当前目录 = {uses_current}")
                finally:
                    os.chdir(original_cwd)
        finally:
            # 清理环境变量
            os.environ.pop(var, None)
    
    print(f"\n=== 跨平台兼容性测试完成 ===")

if __name__ == "__main__":
    test_cross_platform_compatibility()