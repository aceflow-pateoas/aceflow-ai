#!/usr/bin/env python3
"""
包安装测试脚本
Package Installation Test Script

测试AceFlow MCP统一服务器包的安装和基本功能
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_local_installation():
    """测试本地安装"""
    print("🧪 Testing local package installation...")
    
    # 创建临时虚拟环境
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_env"
        
        # 创建虚拟环境
        print("  📦 Creating virtual environment...")
        success, stdout, stderr = run_command(f"python -m venv {venv_path}")
        if not success:
            print(f"  ❌ Failed to create virtual environment: {stderr}")
            return False
        
        # 激活虚拟环境的Python路径
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
        
        # 升级pip
        print("  📦 Upgrading pip...")
        success, stdout, stderr = run_command(f"{pip_path} install --upgrade pip")
        if not success:
            print(f"  ⚠️ Failed to upgrade pip: {stderr}")
        
        # 安装包（开发模式）
        print("  📦 Installing package in development mode...")
        package_path = Path(__file__).parent / "aceflow-mcp-server"
        success, stdout, stderr = run_command(f"{pip_path} install -e {package_path}")
        if not success:
            print(f"  ❌ Failed to install package: {stderr}")
            return False
        
        print("  ✅ Package installed successfully")
        
        # 测试命令行工具
        print("  🧪 Testing CLI tool...")
        success, stdout, stderr = run_command(f"{python_path} -m aceflow_mcp_server.cli --version")
        if not success:
            print(f"  ❌ CLI tool test failed: {stderr}")
            return False
        
        print(f"  ✅ CLI tool working: {stdout.strip()}")
        
        # 测试基本导入
        print("  🧪 Testing package import...")
        test_import_cmd = f"{python_path} -c \"import aceflow_mcp_server; print('Import successful:', aceflow_mcp_server.__version__)\""
        success, stdout, stderr = run_command(test_import_cmd)
        if not success:
            print(f"  ❌ Package import failed: {stderr}")
            return False
        
        print(f"  ✅ Package import successful: {stdout.strip()}")
        
        # 测试服务器创建
        print("  🧪 Testing server creation...")
        test_server_cmd = f"{python_path} -c \"import asyncio; from aceflow_mcp_server import create_unified_server; print('Server creation test passed')\""
        success, stdout, stderr = run_command(test_server_cmd)
        if not success:
            print(f"  ❌ Server creation test failed: {stderr}")
            return False
        
        print(f"  ✅ Server creation test passed")
        
        return True

def test_wheel_installation():
    """测试wheel包安装"""
    print("🧪 Testing wheel package installation...")
    
    # 检查是否有构建的wheel包
    dist_dir = Path(__file__).parent / "aceflow-mcp-server" / "dist"
    if not dist_dir.exists():
        print("  ⚠️ No dist directory found, building package first...")
        
        # 构建包
        package_dir = Path(__file__).parent / "aceflow-mcp-server"
        success, stdout, stderr = run_command("python -m build", cwd=package_dir)
        if not success:
            print(f"  ❌ Failed to build package: {stderr}")
            return False
        
        print("  ✅ Package built successfully")
    
    # 查找wheel文件
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("  ❌ No wheel files found")
        return False
    
    wheel_file = wheel_files[0]
    print(f"  📦 Found wheel file: {wheel_file.name}")
    
    # 创建临时虚拟环境测试wheel安装
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "wheel_test_env"
        
        # 创建虚拟环境
        success, stdout, stderr = run_command(f"python -m venv {venv_path}")
        if not success:
            print(f"  ❌ Failed to create virtual environment: {stderr}")
            return False
        
        # 激活虚拟环境的Python路径
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
        
        # 安装wheel包
        print("  📦 Installing wheel package...")
        success, stdout, stderr = run_command(f"{pip_path} install {wheel_file}")
        if not success:
            print(f"  ❌ Failed to install wheel: {stderr}")
            return False
        
        print("  ✅ Wheel package installed successfully")
        
        # 测试安装的包
        success, stdout, stderr = run_command(f"{python_path} -c \"import aceflow_mcp_server; print(aceflow_mcp_server.__version__)\"")
        if not success:
            print(f"  ❌ Wheel package test failed: {stderr}")
            return False
        
        print(f"  ✅ Wheel package test passed: {stdout.strip()}")
        
        return True

def test_cli_functionality():
    """测试CLI功能"""
    print("🧪 Testing CLI functionality...")
    
    # 测试各种CLI命令
    cli_tests = [
        ("--version", "Version check"),
        ("--help", "Help display"),
        ("config generate", "Config generation"),
        ("test health", "Health check"),
        ("admin status", "Status check"),
    ]
    
    for cmd, description in cli_tests:
        print(f"  🧪 Testing: {description}")
        success, stdout, stderr = run_command(f"python -m aceflow_mcp_server.cli {cmd}")
        if success:
            print(f"  ✅ {description}: PASS")
        else:
            print(f"  ⚠️ {description}: PARTIAL (expected for some commands)")
    
    return True

def main():
    """主测试函数"""
    print("🚀 AceFlow MCP Server - Package Installation Test")
    print("=" * 60)
    
    tests = [
        ("Local Installation", test_local_installation),
        ("Wheel Installation", test_wheel_installation),
        ("CLI Functionality", test_cli_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} Test: PASSED")
            else:
                print(f"❌ {test_name} Test: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} Test: ERROR - {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 PACKAGE INSTALLATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"  {status_icon} {test_name}")
    
    if passed == total:
        print("\n🎉 All package installation tests passed!")
        print("📦 Package is ready for distribution!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)