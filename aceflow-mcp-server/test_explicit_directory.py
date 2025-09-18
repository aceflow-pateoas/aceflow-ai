#!/usr/bin/env python3
"""
测试动态工具参数方案 - 用户明确指定项目路径
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, '.')

from aceflow_mcp_server.tools import AceFlowTools

def test_explicit_directory_parameter():
    """测试用户明确指定项目目录的方案"""
    
    print("=== 测试动态工具参数方案 ===\n")
    
    tools = AceFlowTools()
    
    # 1. 测试明确指定正确的项目目录
    print("1. 测试明确指定项目目录（推荐方案）:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建用户项目目录
        user_project = Path(temp_dir) / "my-awesome-project"
        user_project.mkdir()
        
        # 模拟在IDE安装目录中运行（这是问题场景）
        ide_dir = Path(temp_dir) / "Program Files" / "VS Code"
        ide_dir.mkdir(parents=True)
        original_cwd = os.getcwd()
        os.chdir(str(ide_dir))
        
        try:
            # 用户明确指定项目目录（这是推荐方案）
            result = tools.aceflow_init(
                mode="minimal",
                project_name="my_project",
                directory=str(user_project)  # 👈 关键：用户明确指定
            )
            
            print(f"   ✅ 成功：{result['success']}")
            print(f"   📁 项目目录：{result['project_info']['directory']}")
            print(f"   🎯 正确位置：{result['project_info']['directory'] == str(user_project)}")
            
            # 验证文件确实创建在正确位置
            aceflow_dir = user_project / ".aceflow"
            print(f"   📄 文件创建：{aceflow_dir.exists()}")
            
        except Exception as e:
            print(f"   ❌ 错误：{e}")
        finally:
            os.chdir(original_cwd)
    
    print()
    
    # 2. 测试不指定目录时的友好错误提示
    print("2. 测试无目录参数时的错误提示:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 模拟在IDE目录中
        ide_dir = Path(temp_dir) / "Program Files" / "CodeBuddy" 
        ide_dir.mkdir(parents=True)
        original_cwd = os.getcwd()
        os.chdir(str(ide_dir))
        
        try:
            # 不指定目录参数
            result = tools.aceflow_init(
                mode="minimal",
                project_name="test_project"
                # 👈 注意：没有指定directory参数
            )
            print(f"   ❌ 错误：应该失败但成功了")
        except ValueError as e:
            print(f"   ✅ 正确：提供了友好的错误提示")
            print(f"   📝 错误信息预览：{str(e)[:200]}...")
        finally:
            os.chdir(original_cwd)
    
    print()
    
    # 3. 测试相对路径 "." 的处理
    print("3. 测试相对路径处理:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建项目目录并切换到其中
        project_dir = Path(temp_dir) / "actual-project"
        project_dir.mkdir()
        original_cwd = os.getcwd()
        os.chdir(str(project_dir))
        
        try:
            # 使用相对路径 "."
            result = tools.aceflow_init(
                mode="minimal", 
                project_name="test_project",
                directory="."  # 👈 用户确认当前目录正确
            )
            
            print(f"   ✅ 成功：{result['success']}")
            print(f"   📁 解析路径：{result['project_info']['directory']}")
            print(f"   🎯 正确解析：{result['project_info']['directory'] == str(project_dir)}")
            
        except Exception as e:
            print(f"   ❌ 错误：{e}")
        finally:
            os.chdir(original_cwd)
    
    print(f"\n=== 总结 ===")
    print("📋 推荐使用方式：")
    print("   1. 🎯 总是明确指定完整的项目路径")
    print("   2. 🤖 让AI助手提供当前项目的绝对路径")
    print("   3. ✅ 避免依赖自动检测，确保可靠性")

if __name__ == "__main__":
    test_explicit_directory_parameter()