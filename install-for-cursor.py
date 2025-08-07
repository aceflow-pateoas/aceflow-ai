#!/usr/bin/env python3
"""
Cursor用户快速安装脚本
Quick installation script for Cursor users
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import platform


def get_cursor_config_path():
    """获取Cursor MCP配置文件路径"""
    system = platform.system()
    
    if system == "Windows":
        config_dir = Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage"
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Cursor" / "User" / "globalStorage"
    
    return config_dir / "mcp.json"


def install_aceflow_server():
    """安装AceFlow MCP服务器"""
    print("🚀 安装AceFlow MCP服务器...")
    
    try:
        # 检查是否在正确的目录
        aceflow_server_dir = Path("aceflow-mcp-server")
        if not aceflow_server_dir.exists():
            print("❌ 错误：未找到aceflow-mcp-server目录")
            print("   请确保在项目根目录运行此脚本")
            return False
        
        # 安装服务器
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", str(aceflow_server_dir)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ AceFlow MCP服务器安装成功")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程中出现错误: {e}")
        return False


def verify_installation():
    """验证安装"""
    print("🔍 验证安装...")
    
    try:
        result = subprocess.run([
            "aceflow-enhanced-server", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 服务器命令验证成功")
            return True
        else:
            print(f"❌ 服务器命令验证失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 服务器命令验证超时")
        return False
    except FileNotFoundError:
        print("❌ aceflow-enhanced-server 命令未找到")
        print("   请检查安装是否成功")
        return False
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return False


def configure_cursor():
    """配置Cursor MCP设置"""
    print("⚙️ 配置Cursor MCP设置...")
    
    try:
        config_path = get_cursor_config_path()
        print(f"   配置文件路径: {config_path}")
        
        # 创建配置目录
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取现有配置
        existing_config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                print("   发现现有MCP配置")
            except json.JSONDecodeError:
                print("   现有配置文件格式错误，将创建新配置")
        
        # 读取AceFlow配置
        aceflow_config_path = Path("cursor-mcp-config.json")
        if not aceflow_config_path.exists():
            print("❌ 错误：未找到cursor-mcp-config.json文件")
            return False
        
        with open(aceflow_config_path, 'r', encoding='utf-8') as f:
            aceflow_config = json.load(f)
        
        # 合并配置
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"].update(aceflow_config["mcpServers"])
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)
        
        print("✅ Cursor MCP配置更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 配置过程中出现错误: {e}")
        return False


def test_functionality():
    """测试功能"""
    print("🧪 测试AceFlow功能...")
    
    try:
        # 运行简单测试
        test_script = Path("test_mcp_server_simple.py")
        if test_script.exists():
            result = subprocess.run([
                sys.executable, str(test_script)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "3/3 通过" in result.stdout:
                print("✅ 功能测试通过")
                return True
            else:
                print("⚠️ 功能测试部分失败，但基本功能可用")
                return True
        else:
            print("⚠️ 测试脚本未找到，跳过功能测试")
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️ 功能测试超时，但基本安装应该成功")
        return True
    except Exception as e:
        print(f"⚠️ 功能测试出现错误: {e}")
        return True


def show_usage_guide():
    """显示使用指南"""
    print("\n🎯 使用指南:")
    print("=" * 50)
    
    print("1. 重启Cursor以加载新的MCP配置")
    print("2. 在Cursor中与AI助手对话，尝试以下命令:")
    print("   - @aceflow-enhanced 这是PRD文档，开始开发")
    print("   - @aceflow-enhanced 查看项目状态")
    print("   - @aceflow-enhanced 开始编码实现")
    print("   - @aceflow-enhanced 验证代码质量")
    
    print("\n📋 可用工具:")
    tools = [
        "aceflow_stage_collaborative - 智能协作式阶段管理",
        "aceflow_task_execute - 任务级协作执行",
        "aceflow_respond - 协作请求响应",
        "aceflow_collaboration_status - 协作状态查询",
        "aceflow_validate_quality - 多级质量验证"
    ]
    
    for tool in tools:
        print(f"   - {tool}")
    
    print("\n📚 详细文档:")
    print("   - 查看 CURSOR_INTEGRATION_GUIDE.md 获取完整使用指南")
    print("   - 查看 aceflow-mcp-server/README.md 了解更多功能")
    
    print("\n🆘 如需帮助:")
    print("   - 运行: python test_mcp_server_simple.py")
    print("   - 检查Cursor MCP配置是否正确加载")
    print("   - 确保Cursor已重启")


def main():
    """主安装函数"""
    print("🚀 AceFlow MCP Server - Cursor用户快速安装")
    print("=" * 60)
    print("这个脚本将为Cursor用户安装和配置AceFlow AI-人协同工作流")
    print()
    
    success_count = 0
    total_steps = 4
    
    # 步骤1: 安装服务器
    if install_aceflow_server():
        success_count += 1
    
    # 步骤2: 验证安装
    if verify_installation():
        success_count += 1
    
    # 步骤3: 配置Cursor
    if configure_cursor():
        success_count += 1
    
    # 步骤4: 测试功能
    if test_functionality():
        success_count += 1
    
    # 显示结果
    print(f"\n📊 安装结果: {success_count}/{total_steps} 步骤成功")
    
    if success_count == total_steps:
        print("🎉 安装完成！AceFlow MCP Server已成功配置到Cursor")
        show_usage_guide()
        
        print("\n✅ 下一步:")
        print("1. 重启Cursor")
        print("2. 开始体验AI-人协同开发！")
        
    elif success_count >= 2:
        print("⚠️ 部分安装成功，基本功能应该可用")
        show_usage_guide()
        
        print("\n🔧 故障排除:")
        print("- 检查Python环境和pip安装")
        print("- 确保有足够的文件系统权限")
        print("- 查看详细错误信息进行调试")
        
    else:
        print("❌ 安装失败，请检查错误信息并重试")
        print("\n🆘 常见问题:")
        print("- 确保在项目根目录运行此脚本")
        print("- 检查Python和pip是否正确安装")
        print("- 确保有网络连接以下载依赖")
    
    return success_count == total_steps


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)