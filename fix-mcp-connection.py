#!/usr/bin/env python3
"""
修复MCP连接问题
Fix MCP Connection Issues
"""

import os
import sys
import json
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


def fix_mcp_config():
    """修复MCP配置"""
    print("🔧 修复MCP配置...")
    
    try:
        config_path = get_cursor_config_path()
        print(f"   配置文件路径: {config_path}")
        
        if not config_path.exists():
            print("❌ MCP配置文件不存在，请先运行 install-for-cursor.py")
            return False
        
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 修复aceflow-enhanced配置
        if "mcpServers" in config and "aceflow-enhanced" in config["mcpServers"]:
            aceflow_config = config["mcpServers"]["aceflow-enhanced"]
            
            # 移除host和port参数
            if "args" in aceflow_config:
                new_args = []
                skip_next = False
                for i, arg in enumerate(aceflow_config["args"]):
                    if skip_next:
                        skip_next = False
                        continue
                    if arg in ["--host", "--port"]:
                        skip_next = True
                        continue
                    new_args.append(arg)
                
                # 确保有log-level参数
                if "--log-level" not in new_args:
                    new_args.extend(["--log-level", "INFO"])
                
                aceflow_config["args"] = new_args
            else:
                aceflow_config["args"] = ["--log-level", "INFO"]
            
            # 保存修复后的配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ MCP配置已修复")
            return True
        else:
            print("❌ 未找到aceflow-enhanced配置")
            return False
            
    except Exception as e:
        print(f"❌ 修复配置时出错: {e}")
        return False


def reinstall_server():
    """重新安装服务器"""
    print("🔄 重新安装AceFlow MCP服务器...")
    
    try:
        # 卸载现有版本
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "aceflow-mcp-server", "-y"
        ], capture_output=True)
        
        # 重新安装
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "aceflow-mcp-server/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 服务器重新安装成功")
            return True
        else:
            print(f"❌ 重新安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重新安装过程中出错: {e}")
        return False


def test_server_command():
    """测试服务器命令"""
    print("🧪 测试服务器命令...")
    
    try:
        result = subprocess.run([
            "aceflow-enhanced-server", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 服务器命令正常")
            return True
        else:
            print(f"❌ 服务器命令失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 服务器命令超时")
        return False
    except FileNotFoundError:
        print("❌ aceflow-enhanced-server 命令未找到")
        return False
    except Exception as e:
        print(f"❌ 测试命令时出错: {e}")
        return False


def create_minimal_test():
    """创建最小化测试"""
    print("📝 创建MCP连接测试...")
    
    test_script = """#!/usr/bin/env python3
import subprocess
import sys
import time

def test_mcp_stdio():
    try:
        # 启动MCP服务器
        process = subprocess.Popen(
            ["aceflow-enhanced-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 发送初始化消息
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        import json
        message = json.dumps(init_message) + "\\n"
        
        process.stdin.write(message)
        process.stdin.flush()
        
        # 等待响应
        time.sleep(2)
        
        # 检查进程状态
        if process.poll() is None:
            print("✅ MCP服务器启动成功，正在运行")
            process.terminate()
            return True
        else:
            stderr = process.stderr.read()
            print(f"❌ MCP服务器启动失败: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ MCP测试失败: {e}")
        return False

if __name__ == "__main__":
    test_mcp_stdio()
"""
    
    with open("test_mcp_stdio.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 测试脚本已创建: test_mcp_stdio.py")
    
    # 运行测试
    try:
        result = subprocess.run([sys.executable, "test_mcp_stdio.py"], 
                              capture_output=True, text=True, timeout=15)
        print(f"📊 测试结果: {result.stdout}")
        if result.stderr:
            print(f"⚠️ 测试警告: {result.stderr}")
        return "✅" in result.stdout
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


def show_troubleshooting_guide():
    """显示故障排除指南"""
    print("\n🆘 MCP连接故障排除指南:")
    print("=" * 50)
    
    print("1. 🔄 重启Cursor")
    print("   - 完全关闭Cursor")
    print("   - 重新启动Cursor")
    print("   - 等待MCP服务器自动连接")
    
    print("\n2. 🔍 检查MCP配置")
    config_path = get_cursor_config_path()
    print(f"   - 配置文件位置: {config_path}")
    print("   - 确保JSON格式正确")
    print("   - 确保没有host和port参数")
    
    print("\n3. 🧪 手动测试服务器")
    print("   - 运行: aceflow-enhanced-server --help")
    print("   - 运行: python test_mcp_stdio.py")
    
    print("\n4. 📋 检查Cursor MCP日志")
    print("   - 在Cursor中打开MCP日志面板")
    print("   - 查看具体的错误信息")
    
    print("\n5. 🔄 完全重置")
    print("   - 删除MCP配置文件")
    print("   - 重新运行: python install-for-cursor.py")
    print("   - 重启Cursor")
    
    print("\n📞 如果问题仍然存在:")
    print("   - 检查Python环境是否正确")
    print("   - 确保pip install成功")
    print("   - 查看详细错误日志")


def main():
    """主修复函数"""
    print("🔧 AceFlow MCP连接问题修复工具")
    print("=" * 50)
    
    success_count = 0
    total_steps = 4
    
    # 步骤1: 修复MCP配置
    if fix_mcp_config():
        success_count += 1
    
    # 步骤2: 重新安装服务器
    if reinstall_server():
        success_count += 1
    
    # 步骤3: 测试服务器命令
    if test_server_command():
        success_count += 1
    
    # 步骤4: 创建并运行MCP测试
    if create_minimal_test():
        success_count += 1
    
    print(f"\n📊 修复结果: {success_count}/{total_steps} 步骤成功")
    
    if success_count == total_steps:
        print("🎉 MCP连接问题已修复！")
        print("\n✅ 下一步:")
        print("1. 重启Cursor")
        print("2. 等待MCP服务器自动连接")
        print("3. 尝试使用 @aceflow-enhanced 命令")
        
    elif success_count >= 2:
        print("⚠️ 部分修复成功，请按照故障排除指南继续")
        show_troubleshooting_guide()
        
    else:
        print("❌ 修复失败，请查看故障排除指南")
        show_troubleshooting_guide()
    
    return success_count >= 2


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 修复被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 修复过程中出现未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)