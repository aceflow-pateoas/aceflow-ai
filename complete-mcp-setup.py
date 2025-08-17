#!/usr/bin/env python3
"""
完整的MCP设置和修复脚本
Complete MCP Setup and Fix Script
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
import platform
import shutil


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


def check_aceflow_installation():
    """检查AceFlow MCP服务器安装"""
    print("🔍 检查AceFlow MCP服务器安装...")
    
    try:
        # 检查Python包
        import aceflow_mcp_server
        print("✅ AceFlow MCP服务器Python包已安装")
        
        # 检查命令行工具
        result = subprocess.run(
            ["aceflow-enhanced-server", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ aceflow-enhanced-server命令可用")
            return True
        else:
            print(f"❌ aceflow-enhanced-server命令失败: {result.stderr}")
            return False
            
    except ImportError:
        print("❌ AceFlow MCP服务器Python包未安装")
        return False
    except FileNotFoundError:
        print("❌ aceflow-enhanced-server命令未找到")
        return False
    except Exception as e:
        print(f"❌ 检查过程出错: {e}")
        return False


def install_aceflow_server():
    """安装AceFlow MCP服务器"""
    print("📦 安装AceFlow MCP服务器...")
    
    try:
        # 检查是否在aceflow-mcp-server目录中
        if Path("aceflow-mcp-server").exists():
            print("   发现本地aceflow-mcp-server目录，使用本地安装...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "aceflow-mcp-server/"],
                capture_output=True,
                text=True
            )
        else:
            print("   从PyPI安装...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "aceflow-mcp-server"],
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            print("✅ AceFlow MCP服务器安装成功")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False


def create_cursor_config():
    """创建Cursor MCP配置"""
    print("🔧 创建Cursor MCP配置...")
    
    config_path = get_cursor_config_path()
    print(f"   配置文件路径: {config_path}")
    
    # 创建配置目录
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取现有配置或创建新配置
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("   读取现有配置")
        except:
            config = {"mcpServers": {}}
            print("   现有配置损坏，创建新配置")
    else:
        config = {"mcpServers": {}}
        print("   创建新配置")
    
    # 更新AceFlow配置
    config["mcpServers"]["aceflow-enhanced"] = {
        "command": "aceflow-enhanced-server",
        "args": [
            "--log-level",
            "INFO"
        ],
        "env": {
            "ACEFLOW_DEFAULT_MODE": "standard",
            "ACEFLOW_AUTO_ADVANCE": "false",
            "ACEFLOW_COLLABORATION_TIMEOUT": "600"
        },
        "disabled": False,
        "autoApprove": [
            "aceflow_stage_collaborative",
            "aceflow_task_execute",
            "aceflow_respond",
            "aceflow_collaboration_status",
            "aceflow_validate_quality"
        ]
    }
    
    try:
        # 备份现有配置
        if config_path.exists():
            backup_path = config_path.with_suffix('.json.backup')
            shutil.copy2(config_path, backup_path)
            print(f"   已备份现有配置到: {backup_path}")
        
        # 写入新配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Cursor MCP配置已创建")
        return True
        
    except Exception as e:
        print(f"❌ 创建配置失败: {e}")
        return False


def test_mcp_server():
    """测试MCP服务器"""
    print("🧪 测试MCP服务器...")
    
    try:
        # 测试服务器启动
        process = subprocess.Popen(
            ["aceflow-enhanced-server", "--log-level", "INFO"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程状态
        if process.poll() is None:
            print("✅ MCP服务器启动成功")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP服务器启动失败")
            print(f"   标准输出: {stdout}")
            print(f"   错误输出: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False


def create_test_script():
    """创建测试脚本"""
    print("📝 创建测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
"""
AceFlow MCP服务器测试脚本
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_aceflow_server():
    """测试AceFlow MCP服务器"""
    print("🧪 测试AceFlow MCP服务器...")
    
    try:
        # 创建服务器参数
        server_params = StdioServerParameters(
            command="aceflow-enhanced-server",
            args=["--log-level", "INFO"]
        )
        
        # 连接服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                
                # 列出工具
                tools = await session.list_tools()
                print(f"✅ 发现 {len(tools.tools)} 个工具:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # 列出资源
                resources = await session.list_resources()
                print(f"✅ 发现 {len(resources.resources)} 个资源:")
                for resource in resources.resources:
                    print(f"   - {resource.name}: {resource.description}")
                
                # 测试协作状态工具
                print("\\n🔧 测试协作状态工具...")
                result = await session.call_tool(
                    "aceflow_collaboration_status",
                    {}
                )
                print(f"✅ 协作状态工具响应: {result.content[0].text}")
                
                print("\\n🎉 所有测试通过！")
                return True
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_aceflow_server())
'''
    
    try:
        with open("test_aceflow_mcp.py", 'w', encoding='utf-8') as f:
            f.write(test_script)
        print("✅ 测试脚本已创建: test_aceflow_mcp.py")
        return True
    except Exception as e:
        print(f"❌ 创建测试脚本失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 AceFlow MCP完整设置和修复")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    # 1. 检查安装
    if check_aceflow_installation():
        success_count += 1
    else:
        # 尝试安装
        if install_aceflow_server():
            success_count += 1
            # 重新检查
            if check_aceflow_installation():
                print("✅ 安装后验证成功")
            else:
                print("❌ 安装后验证失败")
    
    # 2. 创建配置
    if create_cursor_config():
        success_count += 1
    
    # 3. 测试服务器
    if test_mcp_server():
        success_count += 1
    
    # 4. 创建测试脚本
    if create_test_script():
        success_count += 1
    
    # 5. 最终验证
    print("\\n🔍 最终验证...")
    config_path = get_cursor_config_path()
    if config_path.exists():
        print("✅ Cursor配置文件存在")
        success_count += 1
    else:
        print("❌ Cursor配置文件不存在")
    
    print(f"\\n📊 设置结果: {success_count}/{total_steps} 步骤成功")
    
    if success_count == total_steps:
        print("\\n🎉 设置完成！")
        print("\\n📋 下一步操作:")
        print("1. 重启Cursor")
        print("2. 在Cursor中测试: @aceflow-enhanced")
        print("3. 运行测试脚本: python test_aceflow_mcp.py")
        print("\\n💡 使用示例:")
        print("   @aceflow-enhanced 我想开发一个用户管理系统")
        print("   @aceflow-enhanced 查看项目状态")
        print("   @aceflow-enhanced 继续下一个阶段")
    else:
        print("\\n⚠️ 设置未完全成功，请检查上述错误信息")
        print("\\n🔧 手动解决步骤:")
        print("1. 确保Python环境正确")
        print("2. 手动安装: pip install -e aceflow-mcp-server/")
        print("3. 检查Cursor配置文件权限")
        print("4. 重启Cursor并重试")
    
    return success_count == total_steps


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️ 设置被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ 设置过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)