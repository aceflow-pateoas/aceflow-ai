#!/usr/bin/env python3
"""
开发工作流脚本 - 简化常见的开发任务
"""

import subprocess
import sys
from pathlib import Path
import argparse


def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ 命令执行失败: {cmd}")
            print(f"错误输出: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def sync_templates():
    """同步模板文件"""
    print("🔄 同步模板文件...")
    script_dir = Path(__file__).parent
    sync_script = script_dir / "sync_templates.py"
    return run_command(f"python {sync_script} --sync", cwd=script_dir.parent)


def check_templates():
    """检查模板同步状态"""
    print("🔍 检查模板同步状态...")
    script_dir = Path(__file__).parent
    sync_script = script_dir / "sync_templates.py"
    return run_command(f"python {sync_script} --check", cwd=script_dir.parent)


def build_package():
    """构建包"""
    print("📦 构建包...")
    script_dir = Path(__file__).parent
    return run_command("python -m build", cwd=script_dir.parent)


def test_package():
    """测试包"""
    print("🧪 运行测试...")
    script_dir = Path(__file__).parent
    return run_command("python -m pytest", cwd=script_dir.parent)


def install_dev():
    """开发模式安装"""
    print("🔧 开发模式安装...")
    script_dir = Path(__file__).parent
    return run_command("pip install -e .", cwd=script_dir.parent)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AceFlow MCP Server 开发工作流")
    parser.add_argument("action", choices=[
        "sync", "check", "build", "test", "install", "all"
    ], help="要执行的操作")
    
    args = parser.parse_args()
    
    if args.action == "sync":
        return 0 if sync_templates() else 1
    elif args.action == "check":
        return 0 if check_templates() else 1
    elif args.action == "build":
        # 构建前先同步模板
        if not sync_templates():
            return 1
        return 0 if build_package() else 1
    elif args.action == "test":
        return 0 if test_package() else 1
    elif args.action == "install":
        return 0 if install_dev() else 1
    elif args.action == "all":
        # 完整的开发工作流
        steps = [
            ("同步模板", sync_templates),
            ("运行测试", test_package),
            ("构建包", build_package),
        ]
        
        for step_name, step_func in steps:
            print(f"\n🚀 执行: {step_name}")
            if not step_func():
                print(f"❌ {step_name} 失败")
                return 1
        
        print("\n✅ 所有步骤完成!")
        return 0


if __name__ == "__main__":
    exit(main())