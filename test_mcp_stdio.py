#!/usr/bin/env python3
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
        message = json.dumps(init_message) + "\n"
        
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
