#!/usr/bin/env python3
"""
测试动态工作目录检测逻辑（IDE集成）
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, '.')

from aceflow_mcp_server.tools import AceFlowTools

def test_dynamic_working_directory():
    """测试动态工作目录检测，包括IDE环境变量支持"""
    
    print("=== 测试动态工作目录检测（IDE集成） ===\n")
    
    # 创建测试工具实例
    tools = AceFlowTools()
    
    # 1. 测试基本动态检测
    print("1. 测试基本动态检测 (当前目录):")
    current_dir = tools._get_dynamic_working_directory()
    print(f"   检测到的工作目录: {current_dir}")
    print(f"   os.getcwd(): {os.getcwd()}")
    print(f"   匹配: {current_dir == os.getcwd()}\n")
    
    # 2. 测试明确指定目录
    print("2. 测试明确指定目录:")
    specified_dir = tools._get_dynamic_working_directory("/tmp")
    print(f"   指定目录: /tmp")
    print(f"   返回目录: {specified_dir}")
    print(f"   匹配: {specified_dir == os.path.abspath('/tmp')}\n")
    
    # 3. 测试相对路径解析
    print("3. 测试相对路径解析 (.):")
    relative_dir = tools._get_dynamic_working_directory(".")
    print(f"   指定路径: .")
    print(f"   解析结果: {relative_dir}")
    print(f"   匹配当前目录: {relative_dir == os.getcwd()}\n")
    
    # 4. 测试IDE环境变量（模拟）
    print("4. 测试IDE环境变量支持:")
    
    # 模拟VS Code环境变量
    test_vscode_dir = str(Path.home())
    os.environ['VSCODE_CWD'] = test_vscode_dir
    
    try:
        # 创建临时目录并切换到那里
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # 检测应该优先使用当前目录，即使有环境变量
            detected_dir = tools._get_dynamic_working_directory()
            print(f"   当前目录: {os.getcwd()}")
            print(f"   VSCODE_CWD: {test_vscode_dir}")
            print(f"   检测结果: {detected_dir}")
            print(f"   优先使用当前目录: {detected_dir == os.getcwd()}")
            
    finally:
        # 清理环境变量
        os.environ.pop('VSCODE_CWD', None)
        os.chdir('/home/chenjing/AI/aceflow-ai/aceflow-mcp-server')
    
    print("\n5. 测试跨平台兼容性:")
    print(f"   当前平台: {os.name}")
    print(f"   Windows特定变量测试: {'支持' if os.name == 'nt' else '跳过'}")
    
    # 6. 测试aceflow_init工具的动态检测
    print("\n6. 测试aceflow_init工具集成:")
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_dynamic_project"
        project_dir.mkdir()
        
        # 切换到项目目录
        original_cwd = os.getcwd()
        os.chdir(str(project_dir))
        
        try:
            # 调用aceflow_init，应该在当前目录创建文件
            result = tools.aceflow_init(
                mode="minimal",
                project_name="dynamic_test"
            )
            
            print(f"   项目目录: {project_dir}")
            print(f"   当前目录: {os.getcwd()}")
            print(f"   初始化成功: {result.get('success')}")
            print(f"   检测到的目录: {result.get('project_info', {}).get('directory')}")
            print(f"   目录匹配: {result.get('project_info', {}).get('directory') == str(project_dir)}")
            
        except Exception as e:
            print(f"   初始化测试出错: {e}")
        finally:
            os.chdir(original_cwd)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_dynamic_working_directory()